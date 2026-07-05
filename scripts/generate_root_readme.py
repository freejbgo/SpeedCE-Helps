#!/usr/bin/env python3
"""Generate root README.md with article index and clickable links."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "articles" / "index.json"
ART_DIR = ROOT / "articles"
README = ROOT / "README.md"

CATEGORY_ORDER = [
    "故障排查", "VPS线路", "CDN", "出海", "开发", "运维", "数据库", "安全",
    "云原生", "网络", "行业", "方法论", "对比", "进阶",
]


def extract_intro(md_path: Path, max_len: int = 120) -> str:
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


def main():
    articles = json.loads(INDEX.read_text(encoding="utf-8"))
    by_cat: dict[str, list] = {}
    for a in articles:
        by_cat.setdefault(a["category"], []).append(a)

    lines = [
        "# SpeedCE 技术文档库\n",
        "\n",
        "> [SpeedCE](https://www.speedce.com) — 多节点网站 / IP 测速工具  \n",
        "> 中文界面：https://speedce.com/?lang=zh-CN  \n",
        "> 联系：speedceads@gmail.com\n",
        "\n",
        "点击下方标题即可跳转到对应文章正文。\n",
        "\n",
        "## 统计\n",
        "\n",
        f"| 项目 | 数量 |\n|------|------|\n",
        f"| 仓库内长文 | {len(articles)} 篇 |\n",
        "| 每篇配图 | 封面 + 示意图（500/800px） |\n",
        "\n",
        "## 仓库文章目录\n",
    ]

    lines.append("\n> 说明：链接指向本仓库 `articles/` 下的 Markdown 原文。\n")

    for cat in CATEGORY_ORDER:
        items = sorted(by_cat.get(cat, []), key=lambda x: x["slug"])
        if not items:
            continue
        lines.append(f"\n### {cat}（{len(items)} 篇）\n\n")
        for a in items:
            slug = a["slug"]
            title = a["title"]
            link = f"articles/{slug}.md"
            intro = extract_intro(ART_DIR / f"{slug}.md")
            img_cover = f"articles/images/{slug}/cover-500.png"
            lines.append(f"- [**{title}**]({link})  \n")
            lines.append(f"  {intro}  \n")
            if Path(ROOT / img_cover).exists():
                lines.append(
                    f"  📷 配图：[封面]({img_cover}) · "
                    f"[示意图](articles/images/{slug}/diagram-500.png)\n\n"
                )
            else:
                lines.append("\n")

    lines.append("\n## 工具与脚本\n\n")
    lines.append("| 脚本 | 用途 |\n|------|------|\n")
    lines.append("| `scripts/diverse_article_generator.py` | 生成 500 篇差异化技术文章 |\n")
    lines.append("| `scripts/generate_article_images.py` | 生成封面与示意图 |\n")
    lines.append("| `scripts/generate_root_readme.py` | 更新本 README |\n")
    lines.append("| `scripts/generate_seo_index.py` | 生成 SEO / AI 收录索引与 GitHub Pages 页面 |\n")
    lines.append("\n## 搜索引擎与 AI 收录\n\n")
    lines.append(
        "本仓库已配置 **GitHub Pages + 爬虫友好索引**，"
        f"便于百度/Google 及 GPTBot、ClaudeBot 等 AI 爬虫收录全部 {len(articles)} 篇文章。\n\n"
    )
    lines.append("| 资源 | 地址 |\n|------|------|\n")
    lines.append("| 在线阅读（GitHub Pages） | https://freejbgo.github.io/SpeedCE-Tech/ |\n")
    lines.append("| Sitemap | https://freejbgo.github.io/SpeedCE-Tech/sitemap.xml |\n")
    lines.append("| robots.txt | https://freejbgo.github.io/SpeedCE-Tech/robots.txt |\n")
    lines.append("| llms.txt（AI 索引） | https://freejbgo.github.io/SpeedCE-Tech/llms.txt |\n")
    lines.append("| JSON 元数据 | https://freejbgo.github.io/SpeedCE-Tech/articles-index.json |\n")
    lines.append("\n重新生成索引：`python3 scripts/generate_seo_index.py`（文章增删后执行；每周一 CI 也会自动刷新）。\n")

    README.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {README} ({len(articles)} articles)")


if __name__ == "__main__":
    main()
