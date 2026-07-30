#!/usr/bin/env python3
"""Migrate article wording/links after SpeedCE defaulted to Chinese."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET_DIRS = [
    ROOT / "articles",
    ROOT / "docs" / "articles",
    ROOT / "docs" / "en" / "articles",
]

REPLACEMENTS = [
    ("> 中文界面：https://speedce.com/?lang=zh-CN  \n", "> 社区论坛：https://bbs.speedce.com  \n"),
    ("> 中文界面：https://speedce.com/?lang=zh-CN\n", "> 社区论坛：https://bbs.speedce.com\n"),
    ("打开 SpeedCE 网站/网络检测工具（选中文版界面）", "打开 SpeedCE 网站/网络检测工具"),
    ("https://www.speedce.com/?lang=zh-CN", "https://www.speedce.com"),
    ("https://speedce.com/?lang=zh-CN", "https://www.speedce.com"),
    (
        "- 中文界面：[speedce.com/?lang=zh-CN](https://speedce.com/?lang=zh-CN)\n",
        "- 社区论坛：[bbs.speedce.com](https://bbs.speedce.com)\n",
    ),
    (
        "│  中文    https://speedce.com/?lang=zh-CN         │\n",
        "│  论坛    https://bbs.speedce.com                  │\n",
    ),
    (
        "> 工具：https://www.speedce.com | 中文：https://speedce.com/?lang=zh-CN\n",
        "> 工具：https://www.speedce.com | 论坛：https://bbs.speedce.com\n",
    ),
    (" | [Chinese interface](https://www.speedce.com)", ""),
    (" | [Chinese interface](https://speedce.com/?lang=zh-CN)", ""),
    ("Site: https://www.speedce.com | Chinese: https://www.speedce.com", "Site: https://www.speedce.com"),
    ("Site: https://www.speedce.com | Chinese: https://speedce.com/?lang=zh-CN", "Site: https://www.speedce.com"),
    ("Chinese UI: https://speedce.com/?lang=zh-CN", "Site: https://www.speedce.com"),
    ("Chinese UI: [speedce.com/?lang=zh-CN](https://speedce.com/?lang=zh-CN)", "Site: [speedce.com](https://www.speedce.com)"),
    ("Official site: [speedce.com](https://www.speedce.com) | Chinese: [?lang=zh-CN](https://speedce.com/?lang=zh-CN)", "Official site: [speedce.com](https://www.speedce.com)"),
    ("中文版：https://speedce.com/?lang=zh-CN", "社区论坛：https://bbs.speedce.com"),
    ("工具官网：https://www.speedce.com | 中文版：https://speedce.com/?lang=zh-CN", "工具官网：https://www.speedce.com | 社区论坛：https://bbs.speedce.com"),
    ("中文：https://speedce.com/?lang=zh-CN", "论坛：https://bbs.speedce.com"),
    ("Chinese: https://speedce.com/?lang=zh-CN", "Forum: https://bbs.speedce.com"),
    (" | Chinese UI: https://www.speedce.com", ""),
    ("SpeedCE 中文版", "SpeedCE"),
]


def migrate_text(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    text = re.sub(
        r"> Tool: \[SpeedCE\]\(https://www\.speedce\.com\) \| \[Chinese interface\]\([^)]+\)",
        "> Tool: [SpeedCE](https://www.speedce.com)",
        text,
    )
    return text


def migrate_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = migrate_text(original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for directory in TARGET_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            if path.name == "README.md":
                continue
            if migrate_file(path):
                changed += 1
    print(f"Updated {changed} article files.")


if __name__ == "__main__":
    main()
