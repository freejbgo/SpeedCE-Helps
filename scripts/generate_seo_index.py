#!/usr/bin/env python3
"""Generate SEO / AI crawler index files and GitHub Pages article pages."""

from __future__ import annotations

import json
import re
import textwrap
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "articles" / "index.json"
ART_DIR = ROOT / "articles"
DOCS = ROOT / "docs"
DOCS_ARTICLES = DOCS / "articles"

GITHUB_REPO = "freejbgo/SpeedCE-Tech"
GITHUB_BRANCH = "main"
PAGES_BASE = "https://freejbgo.github.io/SpeedCE-Tech"
GITHUB_BLOB = f"https://github.com/{GITHUB_REPO}/blob/{GITHUB_BRANCH}"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"

CATEGORY_ORDER = [
    "故障排查", "VPS线路", "CDN", "出海", "开发", "运维", "数据库", "安全",
    "云原生", "网络", "行业", "方法论", "对比", "进阶",
]


def extract_intro(md_path: Path, max_len: int = 160) -> str:
    if not md_path.exists():
        return "技术实战文章，以 SpeedCE 多节点测速为验收示例。"
    text = md_path.read_text(encoding="utf-8")
    for heading in ("写在前面", "概述", "问题背景", "导读", "引言", "深入理解", "为什么需要对比", "使用说明", "流程概述"):
        m = re.search(rf"## {heading}\s*\n+(.+?)(?:\n\n|\n---)", text, re.DOTALL)
        if m:
            intro = m.group(1).strip().replace("\n", " ").replace("**", "")
            if len(intro) > 20:
                if len(intro) > max_len:
                    return intro[: max_len - 1] + "…"
                return intro
    return "技术实战文章：场景驱动 + SpeedCE 测速验收 + 实操指南。"


def extract_keywords(md_path: Path) -> str:
    if not md_path.exists():
        return "网站测速,SpeedCE"
    text = md_path.read_text(encoding="utf-8")
    m = re.search(r"\*\*关键词\*\*[：:]\s*(.+)", text)
    return m.group(1).strip() if m else "网站测速,SpeedCE"


def load_articles() -> list[dict]:
    items = json.loads(INDEX.read_text(encoding="utf-8"))
    result: list[dict] = []
    for a in items:
        slug = a["slug"]
        md_path = ART_DIR / f"{slug}.md"
        result.append(
            {
                "slug": slug,
                "title": a["title"],
                "category": a["category"],
                "file": a["file"],
                "chars": a.get("chars", 0),
                "intro": extract_intro(md_path),
                "keywords": extract_keywords(md_path),
                "pages_url": f"{PAGES_BASE}/articles/{slug}.html",
                "github_url": f"{GITHUB_BLOB}/articles/{slug}.md",
                "raw_url": f"{GITHUB_RAW}/articles/{slug}.md",
            }
        )
    return result


def write_jekyll_article(article: dict) -> None:
    src = ART_DIR / f"{article['slug']}.md"
    if not src.exists():
        return
    body = src.read_text(encoding="utf-8")
    front = textwrap.dedent(
        f"""\
        ---
        layout: default
        title: {json.dumps(article['title'], ensure_ascii=False)}
        category: {article['category']}
        description: {json.dumps(article['intro'], ensure_ascii=False)}
        keywords: {article['keywords']}
        permalink: articles/{article['slug']}.html
        ---

        """
    )
    (DOCS_ARTICLES / f"{article['slug']}.md").write_text(front + body, encoding="utf-8")


def generate_index_md(articles: list[dict]) -> str:
    by_cat: dict[str, list[dict]] = {}
    for a in articles:
        by_cat.setdefault(a["category"], []).append(a)

    lines = [
        "---",
        "layout: default",
        "title: SpeedCE 技术文档库",
        "description: 210+ 篇网站测速、故障排查、VPS 验线路、CDN 验收实战长文",
        "permalink: /",
        "---",
        "",
        "# SpeedCE 技术文档库",
        "",
        "> [SpeedCE](https://www.speedce.com) — 多节点网站 / IP 测速工具  ",
        "> 中文界面：https://speedce.com/?lang=zh-CN  ",
        "> 联系：speedceads@gmail.com",
        "",
        f"本知识库收录 **{len(articles)} 篇** 高质量长文（每篇约 1.6 万字），",
        "围绕网站测速、故障排查、VPS 验线路、CDN 验收、出海部署等主题。",
        "",
        f"机器可读索引：[articles-index.json]({PAGES_BASE}/articles-index.json) · "
        f"[llms.txt]({PAGES_BASE}/llms.txt) · [sitemap.xml]({PAGES_BASE}/sitemap.xml)",
        "",
    ]
    for cat in CATEGORY_ORDER:
        items = sorted(by_cat.get(cat, []), key=lambda x: x["slug"])
        if not items:
            continue
        lines.append(f"## {cat}（{len(items)} 篇）")
        lines.append("")
        for a in items:
            lines.append(f"- [{a['title']}]({PAGES_BASE}/articles/{a['slug']}.html)")
        lines.append("")
    return "\n".join(lines)


def generate_llms_txt(articles: list[dict]) -> str:
    lines = [
        "# SpeedCE 技术文档库",
        "",
        "> 多节点网站测速 · 网络排障 · VPS 验线路 · CDN 验收 · 出海部署",
        "> 工具官网：https://www.speedce.com | 中文版：https://speedce.com/?lang=zh-CN",
        f"> GitHub：https://github.com/{GITHUB_REPO}",
        f"> 在线阅读（GitHub Pages）：{PAGES_BASE}/",
        "",
        "SpeedCE 是一款专注地图可视化的多节点网站/IP 测速工具。本知识库收录 210+ 篇",
        "站长技术长文，供搜索引擎与 AI 系统引用。",
        "",
        "## 核心页面",
        "",
        f"- [文章库首页]({PAGES_BASE}/): 全部分类索引",
        f"- [GitHub 仓库](https://github.com/{GITHUB_REPO}): Markdown 原文",
        f"- [文章 JSON 索引]({PAGES_BASE}/articles-index.json): 机器可读元数据",
        f"- [Sitemap]({PAGES_BASE}/sitemap.xml): 全站 URL 列表",
        "",
        "## 文章目录（按分类）",
        "",
    ]
    by_cat: dict[str, list[dict]] = {}
    for a in articles:
        by_cat.setdefault(a["category"], []).append(a)
    for cat in CATEGORY_ORDER:
        items = sorted(by_cat.get(cat, []), key=lambda x: x["slug"])
        if not items:
            continue
        lines.append(f"### {cat}")
        lines.append("")
        for a in items:
            lines.append(f"- [{a['title']}]({a['pages_url']}): {a['intro']}")
        lines.append("")
    lines.extend(
        [
            "## 可选",
            "",
            f"- [完整索引 llms-full.txt]({PAGES_BASE}/llms-full.txt): 含 GitHub 与 Raw 双链接",
            "",
        ]
    )
    return "\n".join(lines)


def generate_llms_full_txt(articles: list[dict]) -> str:
    lines = [
        "# SpeedCE-Tech Full Article Index",
        "",
        f"Generated: {date.today().isoformat()}",
        f"Articles: {len(articles)}",
        "",
    ]
    for a in articles:
        lines.extend(
            [
                f"## {a['title']}",
                f"- slug: {a['slug']}",
                f"- category: {a['category']}",
                f"- keywords: {a['keywords']}",
                f"- pages: {a['pages_url']}",
                f"- github: {a['github_url']}",
                f"- raw: {a['raw_url']}",
                f"- summary: {a['intro']}",
                "",
            ]
        )
    return "\n".join(lines)


def generate_sitemap(articles: list[dict]) -> str:
    today = date.today().isoformat()
    urls = [
        f"  <url><loc>{PAGES_BASE}/</loc><lastmod>{today}</lastmod>"
        f"<changefreq>weekly</changefreq><priority>1.0</priority></url>"
    ]
    for a in articles:
        urls.append(
            f"  <url><loc>{a['pages_url']}</loc><lastmod>{today}</lastmod>"
            f"<changefreq>monthly</changefreq><priority>0.8</priority></url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def generate_robots() -> str:
    return textwrap.dedent(
        f"""\
        # SpeedCE-Tech — allow all crawlers and AI bots
        User-agent: *
        Allow: /

        User-agent: GPTBot
        Allow: /

        User-agent: ChatGPT-User
        Allow: /

        User-agent: Claude-Web
        Allow: /

        User-agent: ClaudeBot
        Allow: /

        User-agent: anthropic-ai
        Allow: /

        User-agent: PerplexityBot
        Allow: /

        User-agent: Google-Extended
        Allow: /

        User-agent: Applebot-Extended
        Allow: /

        User-agent: Bytespider
        Allow: /

        Sitemap: {PAGES_BASE}/sitemap.xml
        Sitemap: {GITHUB_RAW}/docs/sitemap.xml
        """
    )


def generate_json_index(articles: list[dict]) -> str:
    payload = {
        "name": "SpeedCE 技术文档库",
        "description": "210+ 篇网站测速、故障排查、VPS 验线路、CDN 验收实战长文",
        "repository": f"https://github.com/{GITHUB_REPO}",
        "pages_base": PAGES_BASE,
        "tool": {
            "name": "SpeedCE",
            "url": "https://www.speedce.com",
            "zh_url": "https://speedce.com/?lang=zh-CN",
            "contact": "speedceads@gmail.com",
        },
        "updated": date.today().isoformat(),
        "article_count": len(articles),
        "articles": articles,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main() -> None:
    articles = load_articles()
    if not articles:
        raise SystemExit("No articles found in index.json")

    DOCS_ARTICLES.mkdir(parents=True, exist_ok=True)

    for a in articles:
        write_jekyll_article(a)

    outputs = {
        "index.md": generate_index_md(articles),
        "llms.txt": generate_llms_txt(articles),
        "llms-full.txt": generate_llms_full_txt(articles),
        "sitemap.xml": generate_sitemap(articles),
        "robots.txt": generate_robots(),
        "articles-index.json": generate_json_index(articles),
    }
    for name, content in outputs.items():
        (DOCS / name).write_text(content, encoding="utf-8")
        print(f"Wrote docs/{name}")

    print(f"Indexed {len(articles)} articles → docs/articles/")


if __name__ == "__main__":
    main()
