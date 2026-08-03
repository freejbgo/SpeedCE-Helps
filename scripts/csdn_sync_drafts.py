#!/usr/bin/env python3
"""将仓库 articles/ 中尚未出现在 CSDN 的中文文章，同步为 CSDN 草稿。

设计要点（按当前约定）：
- 只读取 articles/，不改动仓库正文结构
- 按标题去重：CSDN 已发布或草稿里已有同标题则跳过
- 未发布文章先复制到 /tmp/csdn-pending/，同步完可删除
- 默认只做预览（dry-run），加 --sync 才会真正写入草稿
- Cookie 读取顺序：
  1) 环境变量 CSDN_COOKIE（适合 GitHub Actions 浏览器一键运行）
  2) 本机文件（默认 ~/csdn_cookie.txt）
- 不要把 Cookie 提交到 Git

仅使用 Python 标准库。
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import html as html_lib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
BLOG = "https://blog.csdn.net"
BIZ = "https://bizapi.csdn.net"
# CSDN 编辑器前端内置的公开签名常量（非用户密钥）
CA_KEY = "203803574"
CA_SECRET = b"9znpamsyl2c7cdrr9sas0le9vbc3r6ba"

DEFAULT_TEMP_DIR = Path("/tmp/csdn-pending")
DEFAULT_COOKIE_FILE = Path.home() / "csdn_cookie.txt"
TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)


@dataclass
class LocalArticle:
    path: Path
    title: str
    content: str


def die(msg: str, code: int = 1) -> None:
    print(f"错误: {msg}", file=sys.stderr)
    sys.exit(code)


def info(msg: str) -> None:
    print(msg)


def normalize_title(title: str) -> str:
    """标题规范化：去首尾空白、压缩空白、统一常见空白字符。"""
    t = (title or "").replace("\u3000", " ").replace("\xa0", " ")
    t = re.sub(r"\s+", " ", t).strip()
    # 去掉末尾常见标点，降低“多一个句号”导致的误判
    t = t.rstrip("。．.！!？?；;：:")
    return t


def normalize_cookie_text(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return ""
    # 允许用户误把 "Cookie: xxx" 整行贴进来
    if raw.lower().startswith("cookie:"):
        raw = raw.split(":", 1)[1].strip()
    # GitHub Secrets / 文本框里有时会带首尾引号
    if (raw.startswith("'") and raw.endswith("'")) or (
        raw.startswith('"') and raw.endswith('"')
    ):
        raw = raw[1:-1].strip()
    return raw


def validate_cookie(raw: str) -> str:
    if not raw:
        die("Cookie 为空。")
    if "UserName=" not in raw and "UserToken=" not in raw:
        die(
            "Cookie 看起来不完整：应包含 UserName / UserToken 等登录字段。\n"
            "请重新登录 CSDN 后，从浏览器 Network 请求头里复制整段 Cookie。"
        )
    return raw


def load_cookie(cookie_file: Path) -> str:
    env_cookie = normalize_cookie_text(os.environ.get("CSDN_COOKIE", ""))
    if env_cookie:
        info("已从环境变量 CSDN_COOKIE 读取登录信息")
        return validate_cookie(env_cookie)

    if not cookie_file.is_file():
        die(
            f"找不到 Cookie。\n"
            f"- 浏览器一键运行：请在 GitHub 仓库 Secrets 里配置 CSDN_COOKIE\n"
            f"- 本地运行：请创建文件 {cookie_file}，并把整段 Cookie 粘贴进去"
        )
    raw = normalize_cookie_text(cookie_file.read_text(encoding="utf-8"))
    if not raw:
        die(f"Cookie 文件是空的: {cookie_file}")
    return validate_cookie(raw)


def cookie_get(cookie: str, name: str) -> str | None:
    for part in cookie.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        if k.strip() == name:
            return v.strip()
    return None


def sorted_query(params: dict) -> str:
    """CSDN/Aliyun 网关签名要求 query 按 key 排序。"""
    return urllib.parse.urlencode(sorted((str(k), str(v)) for k, v in params.items()))


def ca_sign(method: str, path_with_query: str, content_type: str = "") -> dict[str, str]:
    nonce = str(uuid.uuid4())
    # Aliyun API Gateway 风格：
    # Method\nAccept\nContent-MD5\nContent-Type\nDate\nx-ca-*\nPathAndQuery
    string_to_sign = (
        f"{method}\n*/*\n\n{content_type}\n\n"
        f"x-ca-key:{CA_KEY}\nx-ca-nonce:{nonce}\n{path_with_query}"
    )
    sig = base64.b64encode(
        hmac.new(CA_SECRET, string_to_sign.encode("utf-8"), hashlib.sha256).digest()
    ).decode()
    return {
        "x-ca-key": CA_KEY,
        "x-ca-nonce": nonce,
        "x-ca-signature": sig,
        "x-ca-signature-headers": "x-ca-key,x-ca-nonce",
        "Accept": "*/*",
    }


def _parse_json_response(text: str, status_code: int, *, soft: bool) -> dict:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        if soft:
            return {"_error": True, "_status": status_code, "_raw": text[:500]}
        die(f"接口返回不是 JSON: {text[:300]}")
    if soft and isinstance(parsed, dict):
        parsed.setdefault("_status", status_code)
    return parsed


def _http_json_once(
    method: str,
    url: str,
    cookie: str,
    *,
    referer: str,
    origin: str,
    body: dict | None,
    signed_path: str | None,
    content_type: str,
    soft: bool,
) -> dict:
    headers = {
        "User-Agent": UA,
        "Accept": "*/*" if signed_path is not None else "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": referer,
        "Origin": origin,
        "Cookie": cookie,
        "Connection": "close",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }
    data = None
    if body is not None:
        content_type = content_type or "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = content_type

    if signed_path is not None:
        headers.update(ca_sign(method, signed_path, content_type))

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            text = resp.read().decode("utf-8", "replace")
            status_code = resp.status
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "replace")
        status_code = e.code
        if soft:
            return {
                "_error": True,
                "_status": status_code,
                "_raw": text[:500],
                "message": text[:500],
            }
        if "HMAC signature does not match" in text:
            die(
                f"CSDN 接口签名校验失败 ({status_code})。\n"
                f"这通常是脚本签名算法/参数排序问题，不一定是 Cookie 过期。\n"
                f"响应片段: {text[:240]}"
            )
        if status_code in (401, 403) or "WAF" in text:
            die(
                f"CSDN 拒绝访问 ({status_code})。常见原因：Cookie 过期，或触发了安全校验。\n"
                f"请重新登录 CSDN，更新 GitHub Secret `CSDN_COOKIE` 后再试。\n"
                f"响应片段: {text[:240]}"
            )
        die(f"HTTP {status_code} from {url}: {text[:300]}")
    except urllib.error.URLError as e:
        raise ConnectionError(str(e.reason if hasattr(e, "reason") else e)) from e
    except TimeoutError as e:
        raise ConnectionError(str(e)) from e

    return _parse_json_response(text, status_code, soft=soft)


def _http_json_curl(
    method: str,
    url: str,
    cookie: str,
    *,
    referer: str,
    origin: str,
    body: dict | None,
    signed_path: str | None,
    content_type: str,
    soft: bool,
) -> dict:
    """GitHub Actions 上 urllib 偶发被 CSDN 重置时，用 curl 再试一次。"""
    headers = {
        "User-Agent": UA,
        "Accept": "*/*" if signed_path is not None else "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": referer,
        "Origin": origin,
        "Cookie": cookie,
    }
    if body is not None:
        content_type = content_type or "application/json"
        headers["Content-Type"] = content_type
    if signed_path is not None:
        headers.update(ca_sign(method, signed_path, content_type))

    cmd = [
        "curl",
        "-sS",
        "-L",
        "--http1.1",
        "--connect-timeout",
        "20",
        "--max-time",
        "60",
        "-X",
        method,
    ]
    for k, v in headers.items():
        cmd.extend(["-H", f"{k}: {v}"])
    if body is not None:
        cmd.extend(["--data-binary", json.dumps(body, ensure_ascii=False)])
    cmd.append(url)

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError as e:
        raise ConnectionError("curl 不可用") from e
    if proc.returncode != 0:
        raise ConnectionError(proc.stderr.strip() or f"curl exit {proc.returncode}")
    return _parse_json_response(proc.stdout, 200, soft=soft)


def http_json(
    method: str,
    url: str,
    cookie: str,
    *,
    referer: str,
    origin: str,
    body: dict | None = None,
    signed_path: str | None = None,
    content_type: str = "",
    soft: bool = False,
    retries: int = 5,
) -> dict:
    last_err: Exception | None = None
    attempts = max(retries, 1)
    for i in range(attempts):
        try:
            return _http_json_once(
                method,
                url,
                cookie,
                referer=referer,
                origin=origin,
                body=body,
                signed_path=signed_path,
                content_type=content_type,
                soft=soft,
            )
        except ConnectionError as e:
            last_err = e
            info(f"网络抖动，准备重试 ({i + 1}/{attempts}): {e}")
            time.sleep(min(2 ** i, 20) + random.uniform(0.2, 1.0))

    # urllib 连续失败后，改用 curl 再试几轮（Actions 环境更常见）
    for i in range(3):
        try:
            info(f"改用 curl 重试 ({i + 1}/3): {url}")
            return _http_json_curl(
                method,
                url,
                cookie,
                referer=referer,
                origin=origin,
                body=body,
                signed_path=signed_path,
                content_type=content_type,
                soft=soft,
            )
        except ConnectionError as e:
            last_err = e
            time.sleep(2 + i * 2)

    if soft:
        return {"_error": True, "_status": 0, "message": str(last_err)}
    die(
        f"网络错误（已重试）: {last_err}\n"
        f"这通常是 GitHub Actions 访问 CSDN 时被重置，不一定是 Cookie 问题。\n"
        f"请稍后在 Actions 里再点一次 Run workflow。"
    )


def extract_title(md_text: str, fallback: str) -> str:
    m = TITLE_RE.search(md_text)
    if m:
        return m.group(1).strip()
    return fallback


def load_local_articles(articles_dir: Path) -> list[LocalArticle]:
    if not articles_dir.is_dir():
        die(f"找不到文章目录: {articles_dir}")
    items: list[LocalArticle] = []
    for path in sorted(articles_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        title = extract_title(content, path.stem)
        if not normalize_title(title):
            continue
        items.append(LocalArticle(path=path, title=title, content=content))
    if not items:
        die(f"{articles_dir} 下没有可读的 .md 文章")
    return items


def _curl_text(url: str, cookie: str, referer: str = BLOG) -> str:
    proc = subprocess.run(
        [
            "curl",
            "-sS",
            "-L",
            "--http1.1",
            "--connect-timeout",
            "20",
            "--max-time",
            "60",
            "-H",
            f"User-Agent: {UA}",
            "-H",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "-H",
            f"Referer: {referer}",
            "-H",
            f"Cookie: {cookie}",
            url,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise ConnectionError(proc.stderr.strip() or f"curl exit {proc.returncode}")
    return proc.stdout


def fetch_published_titles_from_html(cookie: str, username: str) -> dict[str, dict]:
    """备用方案：从博主文章列表页 HTML 提取已发布标题。"""
    titles: dict[str, dict] = {}
    title_re = re.compile(
        r'href="https?://blog\.csdn\.net/%s/article/details/(\d+)"[^>]*>(.*?)</a>'
        % re.escape(username),
        re.I | re.S,
    )
    alt_re = re.compile(
        r'data-articleid="(\d+)"[\s\S]{0,400}?<a[^>]*>(.*?)</a>',
        re.I,
    )
    for page in range(1, 51):
        url = f"{BLOG}/{username}/article/list/{page}"
        html = ""
        for attempt in range(3):
            try:
                html = _curl_text(url, cookie, referer=f"{BLOG}/{username}")
                break
            except ConnectionError as e:
                info(f"HTML 列表第 {page} 页重试 {attempt + 1}/3: {e}")
                time.sleep(2 + attempt * 2)
        if not html:
            break

        found = 0
        seen_ids: set[str] = set()
        for m in list(title_re.finditer(html)) + list(alt_re.finditer(html)):
            aid, raw_title = m.group(1), m.group(2)
            if aid in seen_ids:
                continue
            seen_ids.add(aid)
            title = normalize_title(re.sub(r"<[^>]+>", "", html_lib.unescape(raw_title)))
            if not title or title in {"阅读全文", "查看更多"}:
                continue
            titles[title] = {
                "title": title,
                "id": aid,
                "source": "published-html",
                "url": f"{BLOG}/{username}/article/details/{aid}",
            }
            found += 1
        if found == 0:
            break
        time.sleep(0.5)
    return titles


def fetch_published_titles(cookie: str, username: str) -> dict[str, dict]:
    """公开主页接口：已发布文章标题。"""
    titles: dict[str, dict] = {}
    page = 1
    total = None
    api_failed = False
    while True:
        qs = urllib.parse.urlencode(
            {
                "page": page,
                "size": 100,
                "businessType": "blog",
                "username": username,
            }
        )
        url = f"{BLOG}/community/home-api/v1/get-business-list?{qs}"
        data = http_json(
            "GET",
            url,
            cookie,
            referer=f"{BLOG}/{username}?type=blog",
            origin=BLOG,
            soft=True,
            retries=5,
        )
        if data.get("_error"):
            api_failed = True
            info(f"提示: 已发布列表 API 失败，将尝试 HTML 备用方案。详情: {data.get('message') or data.get('_raw')}")
            break
        code = data.get("code")
        if code not in (200, "200", None) and "data" not in data:
            api_failed = True
            info(f"提示: 已发布列表 API 返回异常，将尝试 HTML 备用方案。详情: {data}")
            break
        payload = data.get("data") or {}
        rows = payload.get("list") or []
        if total is None:
            total = payload.get("total")
        if not rows:
            break
        for row in rows:
            title = normalize_title(str(row.get("title") or ""))
            if title:
                titles[title] = {
                    "title": row.get("title"),
                    "id": row.get("articleId"),
                    "source": "published",
                    "url": row.get("url"),
                }
        if total is not None and page * 100 >= int(total):
            break
        if len(rows) < 100:
            break
        page += 1
        time.sleep(0.5 + random.uniform(0, 0.5))

    if titles:
        return titles

    if api_failed or not titles:
        html_titles = fetch_published_titles_from_html(cookie, username)
        if html_titles:
            info(f"HTML 备用方案成功，拿到已发布标题 {len(html_titles)} 个")
            return html_titles

    if not titles:
        die(
            "无法从 CSDN 拉取已发布文章标题（API 与 HTML 备用都失败）。\n"
            "常见原因是 GitHub Actions 出口 IP 被 CSDN 重置。\n"
            "请稍后重试 Run workflow；若连续失败，把 Actions 日志发我。"
        )
    return titles


def _ingest_console_rows(titles: dict[str, dict], rows: list) -> None:
    for row in rows:
        title = normalize_title(str(row.get("title") or row.get("articleTitle") or ""))
        if not title:
            continue
        aid = row.get("articleId") or row.get("id") or row.get("article_id")
        status = row.get("status") or row.get("articleStatus") or row.get("pubStatus")
        titles[title] = {
            "title": row.get("title") or row.get("articleTitle"),
            "id": aid,
            "source": f"console:{status}",
            "url": row.get("url"),
        }


def fetch_console_titles(cookie: str) -> dict[str, dict]:
    """创作中心接口：尽量覆盖已发布 + 草稿。

    该接口依赖 HMAC 签名；若签名/接口变更失败，返回空字典，由调用方降级。
    """
    titles: dict[str, dict] = {}
    # 依次尝试不同 status；只要某一种能分页拉通就继续
    status_values = ("all_v3", "all", "draft", "enable")

    for status in status_values:
        page = 1
        got_any = False
        while page <= 100:
            params = {
                "page": page,
                "pageSize": 50,
                "status": status,
            }
            qs = sorted_query(params)
            path = f"/blog/phoenix/console/v1/article/list?{qs}"
            url = f"{BIZ}{path}"
            data = http_json(
                "GET",
                url,
                cookie,
                referer="https://mp.csdn.net/",
                origin="https://mp.csdn.net",
                signed_path=path,
                soft=True,
            )
            if data.get("_error") or data.get("code") not in (200, "200", 0, "0", None):
                # 当前 status 不可用，试下一个
                if page == 1:
                    msg = data.get("message") or data.get("msg") or data.get("_raw") or data
                    info(f"提示: 创作中心列表 status={status} 不可用，尝试其他参数。详情: {msg}")
                break

            payload = data.get("data") or {}
            rows = payload.get("list") or payload.get("articles") or []
            if not rows:
                break
            got_any = True
            _ingest_console_rows(titles, rows)
            total = payload.get("total") or payload.get("count")
            if total is not None and page * 50 >= int(total):
                break
            if len(rows) < 50:
                break
            page += 1
            time.sleep(0.35)

        if got_any:
            info(f"创作中心列表可用（status={status}）")
            break

    if not titles:
        info(
            "提示: 未能读取创作中心/草稿列表，将仅按「已发布标题」去重。\n"
            "      若草稿箱里已有同标题文章，仍可能再存一份草稿；建议先小批量 --limit 5 验证。"
        )
    return titles


def md_to_html(src: str) -> str:
    """轻量 Markdown→HTML，满足 CSDN content 字段需要 HTML 的要求。"""
    src = (src or "").replace("\r\n", "\n")
    parts: list[str] = []

    def inline(text: str) -> str:
        t = html_lib.escape(text)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
        t = re.sub(
            r"!\[([^\]]*)\]\(([^)\s]+)\)",
            r'<img alt="\1" src="\2" />',
            t,
        )
        t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
        return t

    # 先抽出围栏代码块
    chunks = re.split(r"(```[\s\S]*?```)", src)
    blocks: list[str] = []
    for chunk in chunks:
        if chunk.startswith("```") and chunk.endswith("```"):
            body = chunk[3:-3]
            if "\n" in body:
                _lang, code = body.split("\n", 1)
            else:
                code = body
            blocks.append(f"<pre><code>{html_lib.escape(code.rstrip())}</code></pre>")
            continue
        for para in re.split(r"\n\s*\n", chunk):
            p = para.strip("\n")
            if not p.strip():
                continue
            first = p.lstrip()
            hm = re.match(r"(#{1,6})\s+(.*)", first)
            if hm and "\n" not in p.strip():
                lvl = len(hm.group(1))
                blocks.append(f"<h{lvl}>{inline(hm.group(2).strip())}</h{lvl}>")
                continue
            if all(line.strip().startswith(">") for line in p.splitlines() if line.strip()):
                inner = " ".join(re.sub(r"^>\s?", "", line) for line in p.splitlines())
                blocks.append(f"<blockquote><p>{inline(inner)}</p></blockquote>")
                continue
            lines = [ln for ln in p.splitlines() if ln.strip()]
            if lines and all(re.match(r"^[-*+]\s+", ln.strip()) for ln in lines):
                items = "".join(
                    f"<li>{inline(re.sub(r'^[-*+]\s+', '', ln.strip()))}</li>" for ln in lines
                )
                blocks.append(f"<ul>{items}</ul>")
                continue
            if lines and all(re.match(r"^\d+\.\s+", ln.strip()) for ln in lines):
                items = "".join(
                    f"<li>{inline(re.sub(r'^\d+\.\s+', '', ln.strip()))}</li>" for ln in lines
                )
                blocks.append(f"<ol>{items}</ol>")
                continue
            if re.fullmatch(r"!\[([^\]]*)\]\(([^)\s]+)\)", first.strip()):
                blocks.append(inline(first.strip()))
                continue
            blocks.append(f"<p>{inline(' '.join(ln.strip() for ln in lines))}</p>")

    return "\n".join(blocks)


def make_description(md_text: str, limit: int = 180) -> str:
    text = TITLE_RE.sub("", md_text, count=1)
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"[>#*_`\-\[\]\(\)!]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def stage_pending(
    pending: Iterable[LocalArticle],
    temp_dir: Path,
) -> list[tuple[LocalArticle, Path]]:
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    staged: list[tuple[LocalArticle, Path]] = []
    for art in pending:
        dest = temp_dir / art.path.name
        dest.write_text(art.content, encoding="utf-8")
        meta = {
            "source": str(art.path),
            "title": art.title,
        }
        dest.with_suffix(dest.suffix + ".meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        staged.append((art, dest))
    return staged


def save_draft(cookie: str, title: str, markdown: str, tags: str) -> dict:
    path = "/blog-console-api/v3/mdeditor/saveArticle"
    url = f"{BIZ}{path}"
    body = {
        "title": title,
        "markdowncontent": markdown,
        "content": md_to_html(markdown),
        "readType": "public",
        "status": 2,
        "categories": "",
        "tags": tags,
        "type": "original",
        "original_link": "",
        "authorized_status": False,
        "Description": make_description(markdown),
        "not_auto_saved": "1",
        "source": "pc_mdeditor",
        "cover_images": [],
        "cover_type": 0,
        "is_new": 1,
        "vote_id": 0,
        "pubStatus": "draft",
    }
    data = http_json(
        "POST",
        url,
        cookie,
        referer="https://editor.csdn.net/",
        origin="https://editor.csdn.net",
        body=body,
        signed_path=path,
        content_type="application/json",
    )
    if data.get("code") != 200:
        raise RuntimeError(data.get("msg") or data.get("message") or str(data))
    return data.get("data") or {}


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    p = argparse.ArgumentParser(
        description="把 articles/ 里尚未出现在 CSDN 的文章，同步为 CSDN 草稿（按标题去重）"
    )
    p.add_argument(
        "--articles-dir",
        type=Path,
        default=repo_root / "articles",
        help="本地中文文章目录（默认仓库 articles/）",
    )
    p.add_argument(
        "--cookie-file",
        type=Path,
        default=DEFAULT_COOKIE_FILE,
        help=f"Cookie 文件路径（默认 {DEFAULT_COOKIE_FILE}）",
    )
    p.add_argument(
        "--temp-dir",
        type=Path,
        default=DEFAULT_TEMP_DIR,
        help=f"未发布文章临时目录（默认 {DEFAULT_TEMP_DIR}）",
    )
    p.add_argument(
        "--tags",
        default="SpeedCE,网络测速,运维",
        help="写入草稿时的标签（逗号分隔，最多 5 个）",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="最多同步多少篇（0 表示不限制；建议先用 --limit 5）",
    )
    p.add_argument(
        "--delay",
        type=float,
        default=1.2,
        help="每篇同步间隔秒数，降低风控概率",
    )
    p.add_argument(
        "--sync",
        action="store_true",
        help="真正写入 CSDN 草稿；不加此参数时只预览",
    )
    p.add_argument(
        "--keep-temp",
        action="store_true",
        help="同步后保留临时目录（默认同步成功后删除）",
    )
    p.add_argument(
        "--skip-console-list",
        action="store_true",
        help="跳过创作中心列表，只按主页已发布文章去重",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    cookie = load_cookie(args.cookie_file)
    username = cookie_get(cookie, "UserName") or cookie_get(cookie, "UN")
    if not username:
        die("Cookie 中找不到 UserName，请重新复制完整 Cookie。")
    nick = cookie_get(cookie, "UserNick")
    if nick:
        nick = urllib.parse.unquote(nick)
    info(f"CSDN 账号: {username}" + (f"（{nick}）" if nick else ""))

    articles = load_local_articles(args.articles_dir)
    info(f"本地文章: {len(articles)} 篇（目录: {args.articles_dir}）")

    info("正在拉取 CSDN 已有标题（已发布）...")
    existing = fetch_published_titles(cookie, username)
    info(f"已发布标题: {len(existing)} 个")

    if not args.skip_console_list:
        info("正在拉取 CSDN 创作中心标题（含草稿）...")
        console_titles = fetch_console_titles(cookie)
        info(f"创作中心标题: {len(console_titles)} 个")
        existing.update(console_titles)

    pending: list[LocalArticle] = []
    skipped = 0
    for art in articles:
        key = normalize_title(art.title)
        if key in existing:
            skipped += 1
        else:
            pending.append(art)

    if args.limit and args.limit > 0:
        pending = pending[: args.limit]

    info("")
    info("======== 对比结果 ========")
    info(f"将跳过（标题已存在）: {skipped} 篇")
    info(f"待同步到草稿: {len(pending)} 篇")
    if pending:
        info("待同步示例（最多显示 20 篇）:")
        for art in pending[:20]:
            info(f"  - {art.title}  <=  {art.path.name}")
        if len(pending) > 20:
            info(f"  ... 还有 {len(pending) - 20} 篇")

    if not pending:
        info("没有需要同步的文章。")
        return

    staged = stage_pending(pending, args.temp_dir)
    info(f"\n已复制到临时目录: {args.temp_dir} （{len(staged)} 个文件）")

    if not args.sync:
        info("")
        info("当前是预览模式，没有写入 CSDN。")
        info("确认名单无误后，再执行：")
        info(
            f"  python3 scripts/csdn_sync_drafts.py --sync"
            + (f" --limit {args.limit}" if args.limit else "")
        )
        info("临时目录已生成，可先打开查看；预览模式下默认保留。")
        return

    results = []
    ok = 0
    fail = 0
    info("\n开始写入 CSDN 草稿...")
    for idx, (art, staged_path) in enumerate(staged, 1):
        info(f"[{idx}/{len(staged)}] 存草稿: {art.title}")
        try:
            data = save_draft(cookie, art.title, art.content, args.tags)
            aid = data.get("id") or data.get("art_id") or data.get("articleId")
            edit_url = (
                f"https://editor.csdn.net/md/?articleId={aid}" if aid else ""
            )
            results.append(
                {
                    "file": art.path.name,
                    "title": art.title,
                    "ok": True,
                    "article_id": aid,
                    "edit_url": edit_url,
                }
            )
            ok += 1
            info(f"  成功 -> {edit_url or aid}")
        except Exception as e:  # noqa: BLE001 - 单篇失败不中断整批
            fail += 1
            results.append(
                {
                    "file": art.path.name,
                    "title": art.title,
                    "ok": False,
                    "error": str(e),
                }
            )
            info(f"  失败: {e}")
        if idx < len(staged):
            time.sleep(max(args.delay, 0))

    result_path = args.temp_dir / "sync_result.json"
    result_path.write_text(
        json.dumps(
            {
                "username": username,
                "ok": ok,
                "fail": fail,
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    # 额外在用户家目录留一份结果，即使临时目录被删也能查看
    home_result = Path.home() / "csdn_sync_result.json"
    shutil.copyfile(result_path, home_result)

    info("")
    info("======== 同步完成 ========")
    info(f"成功: {ok}  失败: {fail}")
    info(f"结果文件: {home_result}")
    info("请打开 CSDN 草稿箱检查：https://mp.csdn.net/")

    if fail == 0 and not args.keep_temp:
        shutil.rmtree(args.temp_dir, ignore_errors=True)
        info(f"已删除临时目录: {args.temp_dir}")
    else:
        info(f"临时目录保留: {args.temp_dir}")
        if fail:
            info("因为有失败项，临时目录先保留，方便你核对。")


if __name__ == "__main__":
    main()
