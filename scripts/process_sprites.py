#!/usr/bin/env python3
"""Chroma-key magenta sprites to transparent PNG and copy intro stills."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

SRC = Path(
    r"C:\Users\calle\.grok\sessions\C%3A%5CUsers%5Ccalle\01a091d5-de91-77a2-bb05-7da376f92591\images"
)
ROOT = Path(__file__).resolve().parents[1]
SPR = ROOT / "assets" / "sprites"
TIL = ROOT / "assets" / "tiles"
INTRO = ROOT / "assets" / "intro"

ACT4 = Path(
    r"C:\Users\calle\.grok\sessions\C%3A%5CUsers%5Ccalle\01a0946b-3765-7840-8c8e-ba4a080ce500\images"
)
ACT4_CHROMA = [
    ("3.jpg", "sleet-imp.png"),
    ("2.jpg", "keep-halberd.png"),
    ("5.jpg", "frost-captain.png"),
    ("6.jpg", "frost-captain-bash.png"),
    ("4.jpg", "torch.png"),
    ("1.jpg", "frost-web.png"),
]
ACT3 = Path(
    r"C:\Users\calle\.grok\sessions\C%3A%5CUsers%5Ccalle\01a0927e-bcf5-75d1-9dcc-85753c003059\images"
)
ACT3_CHROMA = [
    ("2.jpg", "rime-skull.png"),
    ("6.jpg", "rime-skull-lunge.png"),
    ("3.jpg", "rib-guard.png"),
    ("5.jpg", "ash-archer.png"),
    ("7.jpg", "ash-archer-draw.png"),
    ("4.jpg", "tomb-warden.png"),
    ("8.jpg", "tomb-warden-swipe.png"),
    ("1.jpg", "bone-pile.png"),
]

CHROMA = [
    ("1.jpg", "twig-rat.png"),
    ("12.jpg", "snow-spitter.png"),
    ("2.jpg", "snow-spitter-spit.png"),
    ("4.jpg", "shield-grunt.png"),
    ("3.jpg", "ice-brute.png"),
    ("13.jpg", "ice-brute-slam.png"),
    ("5.jpg", "john-snow.png"),
    ("14.jpg", "bober-idle.png"),
    ("22.jpg", "bober-slash.png"),
    ("20.jpg", "bober-roll.png"),
    ("7.jpg", "heart.png"),
    ("8.jpg", "woodchips.png"),
    ("9.jpg", "pot.png"),
    ("10.jpg", "key.png"),
    ("11.jpg", "bush.png"),
    ("15.jpg", "pine.png"),
    ("32.jpg", "pine-snow.png"),
    ("18.jpg", "door.png"),
    ("24.jpg", "door-lock.png"),
]

STILLS = [
    ("31.jpg", "n0.jpg"),
    ("23.jpg", "n1.jpg"),
    ("26.jpg", "n2.jpg"),
    ("27.jpg", "n3.jpg"),
    ("25.jpg", "n4.jpg"),
    ("29.jpg", "n5.jpg"),
]


def is_magenta(r: int, g: int, b: int) -> bool:
    return r > 145 and b > 120 and g < 145 and (r + b) > g * 2.1 and min(r, b) > g + 12


def chroma_key(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    out = Image.new("RGBA", (w, h))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, _ = px[x, y]
            if is_magenta(r, g, b):
                op[x, y] = (0, 0, 0, 0)
            else:
                op[x, y] = (r, g, b, 255)
    for _ in range(3):
        cur = out.copy()
        cp = cur.load()
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                r, g, b, a = cp[x, y]
                if a == 0:
                    continue
                trans = 0
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    if cp[x + dx, y + dy][3] == 0:
                        trans += 1
                if trans == 0:
                    continue
                pink = r > 90 and b > 70 and g < 150 and r + b > g * 1.55
                dark = r < 55 and g < 55 and b < 55
                if pink and not dark:
                    op[x, y] = (0, 0, 0, 0)
                elif dark:
                    op[x, y] = (12, 10, 14, 255)
    return out


def tight_crop(im: Image.Image, pad: int = 10) -> Image.Image:
    bbox = im.split()[-1].getbbox()
    if not bbox:
        return im
    l, t, r, b = bbox
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(im.width, r + pad)
    b = min(im.height, b + pad)
    return im.crop((l, t, r, b))


def composite_endcard(bober: Image.Image) -> None:
    bg_path = SRC / "16.jpg"
    if not bg_path.exists():
        return
    bg = Image.open(bg_path).convert("RGBA")
    w, h = bg.size
    # Cover the misdrawn beaver on the lower-right with a snow patch, then stamp graph Bober.
    cover = Image.new("RGBA", (int(w * 0.42), int(h * 0.48)), (0, 0, 0, 0))

    d = ImageDraw.Draw(cover)
    d.ellipse((0, int(cover.height * 0.2), cover.width, cover.height), fill=(232, 240, 248, 255))
    d.ellipse(
        (int(cover.width * 0.1), int(cover.height * 0.05), int(cover.width * 0.9), int(cover.height * 0.55)),
        fill=(220, 232, 244, 255),
    )
    bg.alpha_composite(cover, (int(w * 0.58), int(h * 0.52)))
    bw = int(w * 0.28)
    bh = int(bober.height * bw / bober.width)
    stamp = bober.resize((bw, bh), Image.Resampling.LANCZOS)
    bg.alpha_composite(stamp, (int(w * 0.66), int(h * 0.58)))
    out = bg.convert("RGB")
    out.save(ROOT / "assets" / "endcard.jpg", quality=92)


def main() -> None:
    SPR.mkdir(parents=True, exist_ok=True)
    TIL.mkdir(parents=True, exist_ok=True)
    INTRO.mkdir(parents=True, exist_ok=True)
    for src_name, dest_name in CHROMA:
        src = SRC / src_name
        if not src.exists():
            print("MISSING", src_name)
            continue
        im = chroma_key(Image.open(src))
        im = tight_crop(im, 12)
        dest = SPR / dest_name
        im.save(dest)
        print("sprite", dest_name, im.size)
    snow = SRC / "19.jpg"
    if snow.exists():
        Image.open(snow).convert("RGB").save(TIL / "snow.png")
        print("tile snow")
    for src_name, dest_name in STILLS:
        src = SRC / src_name
        if not src.exists():
            print("MISSING still", src_name)
            continue
        Image.open(src).convert("RGB").save(INTRO / dest_name, quality=92)
        print("intro", dest_name)
    splash_src = SRC / "29.jpg"
    if splash_src.exists():
        Image.open(splash_src).convert("RGB").save(ROOT / "assets" / "splash.jpg", quality=92)
        print("splash")
    end_src = SRC / "16.jpg"
    if end_src.exists():
        Image.open(end_src).convert("RGB").save(ROOT / "assets" / "endcard.jpg", quality=92)
        print("endcard")


if __name__ == "__main__":
    main()
