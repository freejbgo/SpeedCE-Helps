#!/usr/bin/env python3
"""Generate 2 square images (800x800) per article."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "articles" / "index.json"
OUT_DIR = ROOT / "articles" / "images"
SIZE = 800

FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
if not Path(FONT_PATH).exists():
    FONT_PATH = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"

CATEGORY_STYLE = {
    "故障排查": {"bg1": (22, 48, 88), "bg2": (180, 55, 45), "accent": (255, 120, 90)},
    "VPS线路": {"bg1": (15, 42, 95), "bg2": (30, 110, 200), "accent": (100, 200, 255)},
    "CDN": {"bg1": (48, 22, 78), "bg2": (120, 60, 180), "accent": (200, 150, 255)},
    "出海": {"bg1": (10, 55, 70), "bg2": (20, 140, 130), "accent": (80, 230, 210)},
    "行业": {"bg1": (18, 58, 42), "bg2": (40, 130, 80), "accent": (130, 230, 160)},
    "方法论": {"bg1": (35, 35, 85), "bg2": (70, 80, 180), "accent": (160, 170, 255)},
    "对比": {"bg1": (75, 50, 15), "bg2": (180, 120, 40), "accent": (255, 210, 120)},
    "进阶": {"bg1": (15, 50, 65), "bg2": (30, 120, 150), "accent": (100, 220, 255)},
}

MAP_DOT_STATES = [
    ((72, 200, 120), "通畅"),
    ((220, 70, 70), "异常"),
    ((200, 170, 60), "检测中"),
    ((120, 130, 150), "等待"),
]


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def gradient_bg(draw: ImageDraw.ImageDraw, w: int, h: int, c1: tuple, c2: tuple) -> None:
    for y in range(h):
        t = y / max(h - 1, 1)
        col = tuple(lerp(c1[i], c2[i], t) for i in range(3))
        draw.line([(0, y), (w, y)], fill=col)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        test = current + ch
        if font.getlength(test) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines or [text[:20]]


def short_title(title: str, max_len: int = 42) -> str:
    t = title.split("：")[0].split("——")[0].strip()
    if len(t) > max_len:
        return t[: max_len - 1] + "…"
    return t


def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def make_cover(article: dict) -> Image.Image:
    cat = article["category"]
    style = CATEGORY_STYLE.get(cat, CATEGORY_STYLE["方法论"])
    img = Image.new("RGB", (SIZE, SIZE), style["bg1"])
    draw = ImageDraw.Draw(img)
    gradient_bg(draw, SIZE, SIZE, style["bg1"], style["bg2"])

    # decorative grid
    for i in range(0, SIZE, 40):
        draw.line([(i, 0), (i, SIZE)], fill=(255, 255, 255, 20), width=1)
        draw.line([(0, i), (SIZE, i)], fill=(255, 255, 255, 20), width=1)

    draw_rounded_rect(draw, (40, 40, 360, 100), 16, (*style["accent"],))
    font_badge = load_font(28)
    draw.text((56, 52), f"  {cat}  ", fill=(20, 20, 30), font=font_badge)

    font_brand = load_font(36)
    draw.text((40, 120), "SpeedCE", fill=(255, 255, 255), font=font_brand)
    draw.text((40, 162), "多节点测速 · 地图可视化", fill=(220, 230, 245), font=load_font(22))

    title = short_title(article["title"], 36)
    font_title = load_font(40)
    lines = wrap_text(title, font_title, SIZE - 80)
    y = 240
    for line in lines[:5]:
        draw.text((40, y), line, fill=(255, 255, 255), font=font_title)
        y += 52

    # bottom stats bar
    draw_rounded_rect(draw, (40, SIZE - 120, SIZE - 40, SIZE - 40), 20, (15, 22, 38))
    font_sm = load_font(22)
    draw.text((60, SIZE - 102), "HTTPS · 中国节点 · 三网分离", fill=(230, 240, 255), font=font_sm)
    draw.text((60, SIZE - 72), "speedce.com/?lang=zh-CN", fill=style["accent"], font=load_font(24))

    # accent circle
    draw.ellipse((SIZE - 180, SIZE - 200, SIZE - 60, SIZE - 80), outline=style["accent"], width=4)
    draw.text((SIZE - 155, SIZE - 175), "测速", fill=style["accent"], font=load_font(30))

    return img


def china_outline_points(scale: float = 1.0, ox: float = 0, oy: float = 0) -> list[tuple[float, float]]:
    """Simplified China map silhouette for illustration."""
    pts = [
        (0.72, 0.22), (0.78, 0.28), (0.82, 0.35), (0.85, 0.42), (0.88, 0.50),
        (0.86, 0.58), (0.82, 0.65), (0.78, 0.72), (0.72, 0.78), (0.65, 0.82),
        (0.55, 0.85), (0.45, 0.83), (0.38, 0.78), (0.32, 0.70), (0.28, 0.60),
        (0.25, 0.50), (0.26, 0.40), (0.30, 0.32), (0.38, 0.25), (0.48, 0.20),
        (0.58, 0.18), (0.65, 0.20),
    ]
    return [(ox + p[0] * 520 * scale, oy + p[1] * 520 * scale) for p in pts]


def make_diagram(article: dict, seed: int) -> Image.Image:
    cat = article["category"]
    style = CATEGORY_STYLE.get(cat, CATEGORY_STYLE["方法论"])
    img = Image.new("RGB", (SIZE, SIZE), (18, 24, 38))
    draw = ImageDraw.Draw(img)
    gradient_bg(draw, SIZE, SIZE, (18, 24, 38), (30, 40, 60))

    font = load_font(26)
    draw.text((40, 36), "SpeedCE 节点地图示意", fill=(255, 255, 255), font=font)
    draw.text((40, 72), short_title(article["title"], 28), fill=(180, 200, 230), font=load_font(20))

    # map panel
    draw_rounded_rect(draw, (50, 110, SIZE - 50, SIZE - 200), 24, (12, 18, 32))
    mx, my = 120, 150
    outline = china_outline_points(1.0, mx, my)
    draw.polygon(outline, outline=(60, 80, 110), fill=(25, 35, 55))

    rng = random.Random(seed)
    for _ in range(28):
        px = rng.randint(mx + 30, mx + 450)
        py = rng.randint(my + 30, my + 450)
        state = rng.choices(MAP_DOT_STATES, weights=[70, 12, 10, 8], k=1)[0]
        color = state[0]
        r = rng.randint(6, 11)
        draw.ellipse((px - r, py - r, px + r, py + r), fill=color)

    # legend
    ly = SIZE - 175
    for i, (color, label) in enumerate(MAP_DOT_STATES):
        x = 60 + i * 175
        draw.ellipse((x, ly, x + 18, ly + 18), fill=color)
        draw.text((x + 26, ly - 2), label, fill=(200, 210, 225), font=load_font(20))

    # steps
    steps = ["1.选 HTTPS", "2.中国节点", "3.开始测速", "4.看地图"]
    sx = 60
    for step in steps:
        draw_rounded_rect(draw, (sx, SIZE - 95, sx + 155, SIZE - 50), 12, style["bg2"])
        draw.text((sx + 12, SIZE - 82), step, fill=(255, 255, 255), font=load_font(20))
        sx += 175

    return img


def main():
    articles = json.loads(INDEX.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []

    for i, art in enumerate(articles):
        slug = art["slug"]
        slug_dir = OUT_DIR / slug
        slug_dir.mkdir(parents=True, exist_ok=True)

        cover_path = slug_dir / "cover-800.png"
        diagram_path = slug_dir / "diagram-800.png"
        cover_500 = slug_dir / "cover-500.png"
        diagram_500 = slug_dir / "diagram-500.png"

        cover = make_cover(art)
        cover.save(cover_path, "PNG", optimize=True)
        cover.resize((500, 500), Image.Resampling.LANCZOS).save(cover_500, "PNG", optimize=True)

        diagram = make_diagram(art, seed=hash(slug) % (2**31))
        diagram.save(diagram_path, "PNG", optimize=True)
        diagram.resize((500, 500), Image.Resampling.LANCZOS).save(diagram_500, "PNG", optimize=True)

        manifest.append({
            "slug": slug,
            "title": art["title"],
            "category": art["category"],
            "cover_800": str(cover_path.relative_to(ROOT)),
            "diagram_800": str(diagram_path.relative_to(ROOT)),
            "cover_500": str(cover_500.relative_to(ROOT)),
            "diagram_500": str(diagram_500.relative_to(ROOT)),
        })

        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(articles)} done")

    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Generated {len(articles) * 4} images (800+500) for {len(articles)} articles")
    print(f"Output: {OUT_DIR}")


if __name__ == "__main__":
    main()
