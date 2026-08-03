#!/usr/bin/env python3
"""将仓库 articles/ 中尚未出现在 CSDN 的中文文章，同步为 CSDN 草稿。

设计要点（按当前约定）：
- 只读取 articles/，不改动仓库正文结构
- 按标题去重：CSDN 已发布或草稿里已有同标题则跳过
- 未发布文章先复制到 /tmp/csdn-pending/，同步完可删除
- 默认只做预览（dry-run），加 --sync 才会真正写入草稿
- Cookie 从本机文件读取（默认 ~/csdn_cookie.txt），不要提交到 Git

仅使用 Python 标准库，Mac 一般自带 python3 即可运行。
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import html as html_lib
import json
import os
import re
import shutil
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


def load_cookie(cookie_file: Path) -> str:
    if not cookie_file.is_file():
        die(
            f"找不到 Cookie 文件: {cookie_file}\n"
            f"请先在 Mac 上创建该文件，并把整段 Cookie 粘贴进去（只有一行）。"
        )
    raw = cookie_file.read_text(encoding="utf-8").strip()
    if not raw:
        die(f"Cookie 文件是空的: {cookie_file}")
    # 允许用户误把 "Cookie: xxx" 整行贴进来
    if raw.lower().startswith("cookie:"):
        raw = raw.split(":", 1)[1].strip()
    if "UserName=" not in raw and "UserToken=" not in raw:
        die(
            "Cookie 看起来不完整：应包含 UserName / UserToken 等登录字段。\n"
            "请重新登录 CSDN 后，从浏览器 Network 请求头里复制整段 Cookie。"
        )
    return raw


def cookie_get(cookie: str, name: str) -> str | None:
    for part in cookie.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        if k.strip() == name:
            return v.strip()
    return None


def ca_sign(method: str, path_with_query: str, content_type: str = "") -> dict[str, str]:
    nonce = str(uuid.uuid4())
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
) -> dict:
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": referer,
        "Origin": origin,
        "Cookie": cookie,
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
        with urllib.request.urlopen(req, timeout=45) as resp:
            text = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "replace")
        if e.code in (401, 403) or "WAF" in text:
            die(
                f"CSDN 拒绝访问 ({e.code})。常见原因：Cookie 过期，或触发了安全校验。\n"
                f"请重新登录 CSDN，更新 ~/csdn_cookie.txt 后再试。\n"
                f"响应片段: {text[:240]}"
            )
        die(f"HTTP {e.code} from {url}: {text[:300]}")
    except urllib.error.URLError as e:
        die(f"网络错误: {e}")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        die(f"接口返回不是 JSON: {text[:300]}")


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


def fetch_published_titles(cookie: str, username: str) -> dict[str, dict]:
    """公开主页接口：已发布文章标题。"""
    titles: dict[str, dict] = {}
    page = 1
    total = None
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
        )
        code = data.get("code")
        if code not in (200, "200", None) and "data" not in data:
            die(f"拉取已发布列表失败: {data}")
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
        time.sleep(0.3)
    return titles


def fetch_console_titles(cookie: str) -> dict[str, dict]:
    """创作中心接口：尽量覆盖已发布 + 草稿。"""
    titles: dict[str, dict] = {}
    page = 1
    while True:
        qs = urllib.parse.urlencode(
            {
                "page": page,
                "status": "all_v3",
                "pageSize": 50,
            }
        )
        path = f"/blog/phoenix/console/v1/article/list?{qs}"
        url = f"{BIZ}{path}"
        data = http_json(
            "GET",
            url,
            cookie,
            referer="https://mp.csdn.net/",
            origin="https://mp.csdn.net",
            signed_path=path,
        )
        if data.get("code") not in (200, "200", 0, "0"):
            # 不直接失败：有的账号/地区可能列表接口变更，仍可用已发布列表去重
            info(f"提示: 创作中心列表接口返回异常，将主要依赖已发布列表去重。详情: {data.get('message') or data.get('msg') or data}")
            break
        payload = data.get("data") or {}
        rows = payload.get("list") or payload.get("articles") or []
        if not rows:
            break
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
        total = payload.get("total") or payload.get("count")
        if total is not None and page * 50 >= int(total):
            break
        if len(rows) < 50:
            break
        page += 1
        time.sleep(0.35)
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
