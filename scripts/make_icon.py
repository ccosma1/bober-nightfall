#!/usr/bin/env python3
"""Bober Nightfall — raid-mark painter (original, this game only).

Wooden stick-sword jammed into a frost-cracked ice shard; two beaver
ear-nubs peek behind the upper blade. Night raid into the ice-woods.

Workshop is a 1200px milles sheet with a facet-mesh ice crystal, a
centerline stick-sword, and a planted-origin crack burst. Not a face,
not a hut, not dam logs, not a sling-V, not a glow-circle badge.

Outputs under assets/icons/:
  bober-nightfall.ico, icon-192.png, icon-512.png, icon-maskable-512.png
"""

from __future__ import annotations

import math
import struct
import sys
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "assets" / "icons"

# Brand hexes from BRAND_MARK.md (RGB). Alpha applied at stamp time.
NIGHT = (0x3A, 0x2A, 0x6A)
SWORD = (0x5C, 0x3A, 0x1A)
ICE = (0xA8, 0xC4, 0xE8)
FUR = (0x8B, 0x5A, 0x2B)
CREAM = (0xF4, 0xE6, 0xC3)
GOLD = (0xF5, 0xC4, 0x00)

WORK = 1200
MILLES = 1000.0
ICO_FACES = (16, 24, 32, 48, 64, 128, 256)


def _need_pil():
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pillow"])
        from PIL import Image, ImageDraw
    return Image, ImageDraw


def _rgba(rgb, a: int = 255) -> tuple[int, int, int, int]:
    return (rgb[0], rgb[1], rgb[2], a)


def _blend(a, b, t: float) -> tuple[int, int, int]:
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


# Supporting mixes — still the shared 2026 family, no cyan/oxblood/navy.
INK = _blend(SWORD, NIGHT, 0.35)
SWORD_LIT = _blend(SWORD, FUR, 0.55)
SWORD_CORE = _blend(SWORD, CREAM, 0.18)
FUR_IN = _blend(FUR, SWORD, 0.45)
ICE_LIT = _blend(ICE, CREAM, 0.42)
ICE_DIM = _blend(ICE, NIGHT, 0.38)
ICE_RIDGE = _blend(ICE, CREAM, 0.62)
CRACK = _blend(ICE, NIGHT, 0.55)
BANK_DIM = _blend(CREAM, ICE, 0.35)
GLINT = _blend(ICE_LIT, CREAM, 0.55)


def _kink(i: int, amp: float) -> float:
    """Deterministic side-step for crack walks. Not random, not a sine drape."""
    x = (i * 1664525 + 1013904223) & 0x7FFFFFFF
    return ((x % 2001) / 1000.0 - 1.0) * amp


class RaidSheet:
    """Mille-mapped canvas (0..1000) with optional maskable inset."""

    def __init__(self, Image, ImageDraw, px: int, inset: float = 0.0):
        self.Image = Image
        self.px = px
        self.inset = inset
        self.im = Image.new("RGBA", (px, px), _rgba(NIGHT))
        self.pen = ImageDraw.Draw(self.im)
        self._glass = None
        self._gpen = None

    def xy(self, u: float, v: float) -> tuple[float, float]:
        lo = self.inset * self.px
        span = (1.0 - 2.0 * self.inset) * self.px
        return (lo + u * span / MILLES, lo + v * span / MILLES)

    def sc(self, n: float) -> float:
        return n * (1.0 - 2.0 * self.inset) * self.px / MILLES

    def pts(self, seq) -> list[tuple[float, float]]:
        return [self.xy(u, v) for u, v in seq]

    def poly(self, seq, rgb, a: int = 255) -> None:
        p = self.pts(seq)
        if len(p) >= 3:
            self.pen.polygon(p, fill=_rgba(rgb, a))

    def disk(self, u: float, v: float, r: float, rgb, a: int = 255) -> None:
        self.oval(u, v, r, r, rgb, a)

    def oval(self, u: float, v: float, ru: float, rv: float, rgb, a: int = 255) -> None:
        cx, cy = self.xy(u, v)
        rx, ry = self.sc(ru), self.sc(rv)
        self.pen.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=_rgba(rgb, a))

    def glass_layer(self, ImageDraw):
        if self._glass is None:
            self._glass = self.Image.new("RGBA", (self.px, self.px), (0, 0, 0, 0))
            self._gpen = ImageDraw.Draw(self._glass)
        return self._gpen

    def glass_poly(self, ImageDraw, seq, rgb, a: int) -> None:
        pen = self.glass_layer(ImageDraw)
        p = self.pts(seq)
        if len(p) >= 3:
            pen.polygon(p, fill=_rgba(rgb, a))

    def seal_glass(self) -> None:
        if self._glass is not None:
            self.im = self.Image.alpha_composite(self.im, self._glass)
            self._glass = None
            self._gpen = None


def _fat_walk(origin, heading, length, half, kinks: int) -> list[tuple[float, float]]:
    """Quad strip along a kinky ray. Used for frost cracks radiating from the plant."""
    ang = heading
    x, y = origin
    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []
    step = length / max(1, kinks)
    for i in range(kinks + 1):
        nx, ny = -math.sin(ang), math.cos(ang)
        left.append((x + nx * half, y + ny * half))
        right.append((x - nx * half, y - ny * half))
        if i == kinks:
            break
        ang += _kink(i + 7, 0.46)
        x += math.cos(ang) * step
        y += math.sin(ang) * step
    return left + list(reversed(right))


def _shard_outline() -> list[tuple[float, float]]:
    """Asymmetric point-up crystal. Chipped left, notched base — not a hut mound."""
    return [
        (500, 348),  # apex, high so the triangle owns the lower field
        (668, 520),  # right upper chip
        (838, 886),  # right base
        (548, 848),  # inner notch (breaks pyramid / mountain read)
        (168, 908),  # left base, sitting in the bank
        (286, 556),  # left chip
    ]


def _plant() -> tuple[float, float]:
    return (500.0, 548.0)


def _paint_bank(sheet: RaidSheet) -> None:
    """Tiny frost crust under the shard. Broken floes, not a snow-capped roof."""
    floes = (
        (
            BANK_DIM,
            [(178, 932), (300, 902), (430, 918), (410, 986), (190, 990)],
        ),
        (
            CREAM,
            [(410, 922), (530, 888), (690, 918), (668, 988), (430, 992)],
        ),
        (
            BANK_DIM,
            [(640, 926), (770, 900), (860, 934), (838, 988), (650, 992)],
        ),
    )
    for rgb, poly in floes:
        sheet.poly(poly, INK)
        inset = [(u + 5, v + 4) for u, v in poly[:-2]] + poly[-2:]
        sheet.poly(inset, rgb)
    sheet.poly(
        [(260, 918), (500, 892), (750, 916), (710, 934), (500, 912), (290, 936)],
        ICE,
    )


def _paint_shard(sheet: RaidSheet, ImageDraw, detail: bool) -> None:
    outline = _shard_outline()
    plant = _plant()
    # Dark under-copy so the crystal separates from night purple.
    sheet.poly([(u + 8, v + 12) for u, v in outline], INK)
    sheet.poly(outline, ICE_DIM)

    apex, r_chip, r_base, notch, l_base, l_chip = outline
    sheet.poly([apex, l_chip, plant], ICE_DIM)
    sheet.poly([l_chip, l_base, plant], _blend(ICE_DIM, NIGHT, 0.2))
    sheet.poly([apex, r_chip, plant], ICE_LIT)
    sheet.poly([r_chip, r_base, plant], ICE)
    sheet.poly([l_base, notch, r_base, plant], _blend(ICE, CREAM, 0.12))

    # Center ridge — crystal, not a doorway.
    sheet.poly([apex, (plant[0] + 10, plant[1]), (plant[0] - 18, plant[1] + 8)], ICE_RIDGE)

    if not detail:
        return

    for heading, length, half, kinks in (
        (0.95, 250, 5.5, 5),
        (1.35, 210, 4.5, 4),
        (2.15, 240, 5.0, 5),
        (2.72, 180, 4.0, 4),
        (0.42, 160, 3.5, 3),
    ):
        strip = _fat_walk(plant, heading, length, half, kinks)
        sheet.poly(strip, CRACK)

    # Plant collar — ice burst where the blade is jammed in.
    cx, cy = plant
    sheet.poly(
        [
            (cx - 70, cy - 8),
            (cx - 18, cy - 28),
            (cx + 22, cy - 16),
            (cx + 64, cy - 4),
            (cx + 36, cy + 18),
            (cx - 30, cy + 22),
        ],
        ICE_LIT,
    )


def _paint_ears(sheet: RaidSheet) -> None:
    """Rounded ear-bumps only. Behind the upper blade; no snout, no teeth, no square head."""
    for side in (-1.0, 1.0):
        cu = 500 + side * 96
        cv = 318
        sheet.oval(cu + 5, cv + 8, 54, 70, INK)
        sheet.oval(cu, cv, 50, 66, FUR)
        sheet.oval(cu + side * 6, cv - 6, 28, 38, FUR_IN)


def _paint_sword(sheet: RaidSheet, detail: bool) -> None:
    """Short wooden stick-sword: round pommel, thick blade, tiny gold tack."""
    # Short timber stop — wider than the blade, far short of Dam's full-width logs.
    sheet.poly([(412, 248), (588, 246), (594, 292), (406, 294)], INK)
    sheet.poly([(418, 252), (582, 250), (586, 286), (414, 288)], SWORD)
    sheet.poly([(430, 254), (570, 252), (568, 266), (432, 268)], SWORD_LIT)

    # Blade — thick trapezoid, point buried in the shard (not a rapier).
    blade = [(418, 278), (582, 276), (546, 812), (454, 816)]
    sheet.poly([(u + 10, v + 10) for u, v in blade], INK)
    sheet.poly(blade, SWORD)
    sheet.poly([(440, 292), (478, 290), (468, 788), (450, 790)], SWORD_LIT)
    if detail:
        sheet.poly([(456, 310), (466, 308), (458, 770), (450, 772)], INK)
        sheet.poly([(522, 308), (530, 306), (520, 762), (512, 764)], INK)

    # Grip, slimmer than the blade, sits between the ear-bumps.
    sheet.poly([(458, 128), (542, 126), (548, 256), (452, 258)], INK)
    sheet.poly([(464, 132), (536, 130), (540, 250), (460, 252)], SWORD_LIT)
    if detail:
        for y0, y1 in ((150, 162), (178, 190), (206, 218)):
            sheet.poly([(470, y0), (530, y0 - 2), (530, y1 - 2), (470, y1)], CREAM)

    # Round pommel.
    sheet.disk(500, 86, 74, INK)
    sheet.disk(500, 80, 68, SWORD)
    sheet.disk(478, 66, 26, SWORD_LIT)
    sheet.disk(500, 80, 20, SWORD_CORE)
    # Tiny brass tack — the only yellow, a pin not a sling-V.
    sheet.disk(500, 80, 10, GOLD)
    sheet.disk(496, 76, 4, CREAM)


def _paint_ice_over_blade(sheet: RaidSheet, ImageDraw, detail: bool) -> None:
    """Translucent shard covering the buried blade so the sword reads as planted."""
    outline = _shard_outline()
    plant = _plant()
    apex, r_chip, r_base, notch, l_base, l_chip = outline
    buried = [
        (l_chip[0] + 20, plant[1] - 6),
        (r_chip[0] - 16, plant[1] + 4),
        r_base,
        notch,
        l_base,
    ]
    sheet.glass_poly(ImageDraw, buried, ICE, 132 if detail else 96)
    sheet.glass_poly(
        ImageDraw,
        [
            (plant[0] - 40, plant[1] - 4),
            (plant[0] + 44, plant[1] + 2),
            (plant[0] + 28, 790),
            (plant[0] - 26, 794),
        ],
        ICE_LIT,
        100,
    )
    sheet.seal_glass()


def _paint_glint(sheet: RaidSheet) -> None:
    """Ice-blue plus-sparkle on the shard. Not a moon, not an Orion star."""
    cu, cv, arm, thick = 742, 590, 44, 9
    sheet.poly(
        [
            (cu, cv - arm),
            (cu + thick, cv - thick),
            (cu + arm, cv),
            (cu + thick, cv + thick),
            (cu, cv + arm),
            (cu - thick, cv + thick),
            (cu - arm, cv),
            (cu - thick, cv - thick),
        ],
        GLINT,
    )
    sheet.disk(cu, cv, 7, CREAM)


def paint_raid(Image, ImageDraw, px: int, inset: float = 0.0, detail: bool = True):
    sheet = RaidSheet(Image, ImageDraw, px, inset)
    _paint_bank(sheet)
    _paint_shard(sheet, ImageDraw, detail)
    _paint_ears(sheet)
    _paint_sword(sheet, detail)
    _paint_ice_over_blade(sheet, ImageDraw, detail)
    if detail:
        _paint_glint(sheet)
    return sheet.im


def _put(px, x: int, y: int, rgb, n: int) -> None:
    if 0 <= x < n and 0 <= y < n:
        px[x, y] = _rgba(rgb)


def stamp_tiny(Image, n: int):
    """Hand grid so 16/24 still read as vertical sword + ice triangle."""
    im = Image.new("RGBA", (n, n), _rgba(NIGHT))
    px = im.load()
    if n == 16:
        ice = [
            (7, 7), (8, 7),
            (6, 8), (7, 8), (8, 8), (9, 8),
            (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9),
            (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (11, 10),
            (3, 11), (4, 11), (5, 11), (6, 11), (7, 11), (8, 11), (9, 11), (10, 11), (11, 11), (12, 11),
            (3, 12), (4, 12), (5, 12), (6, 12), (7, 12), (8, 12), (9, 12), (10, 12), (11, 12), (12, 12),
        ]
        for x, y in ice:
            _put(px, x, y, ICE if x >= 7 else ICE_DIM, n)
        for x in range(2, 14):
            _put(px, x, 13, CREAM, n)
            _put(px, x, 14, BANK_DIM, n)
        for y in range(3, 12):
            for x in range(6, 10):
                _put(px, x, y, SWORD, n)
        for x, y in ((6, 1), (7, 1), (8, 1), (9, 1), (6, 2), (7, 2), (8, 2), (9, 2), (7, 0), (8, 0)):
            _put(px, x, y, SWORD, n)
        for x in range(4, 12):
            _put(px, x, 4, SWORD_LIT, n)
        for x, y in ((3, 4), (4, 4), (3, 5), (4, 5), (11, 4), (12, 4), (11, 5), (12, 5)):
            _put(px, x, y, FUR, n)
        _put(px, 7, 1, GOLD, n)
        return im

    # 24px: same silhouette, extra room for pommel + shard chips.
    ice_tri = []
    for y in range(10, 21):
        half = 1 + (y - 10)
        for x in range(12 - half, 12 + half + 1):
            ice_tri.append((x, y, ICE if x >= 12 else ICE_DIM))
    for x, y, c in ice_tri:
        _put(px, x, y, c, n)
    for y in (20, 21, 22):
        for x in range(3, 21):
            _put(px, x, y, CREAM if y == 20 else BANK_DIM, n)
    for y in range(4, 18):
        for x in range(9, 15):
            _put(px, x, y, SWORD, n)
    for y in range(1, 6):
        for x in range(9, 15):
            if (x - 11.5) ** 2 + (y - 3.2) ** 2 <= 3.6 ** 2:
                _put(px, x, y, SWORD, n)
    for x in range(6, 18):
        _put(px, x, 6, SWORD_LIT, n)
        _put(px, x, 7, SWORD, n)
    for x, y in (
        (5, 6), (6, 6), (5, 7), (6, 7), (5, 8), (6, 8),
        (17, 6), (18, 6), (17, 7), (18, 7), (17, 8), (18, 8),
    ):
        _put(px, x, y, FUR, n)
    _put(px, 11, 3, GOLD, n)
    _put(px, 12, 3, GOLD, n)
    return im


def stamp(Image, ImageDraw, size: int, inset: float = 0.0):
    if size <= 24 and inset == 0.0:
        return stamp_tiny(Image, size)
    detail = size >= 48 or inset > 0
    work = paint_raid(Image, ImageDraw, WORK, inset=inset, detail=detail or size >= 32)
    if size == WORK:
        return work
    return work.resize((size, size), Image.Resampling.LANCZOS)


def emit_png(Image, ImageDraw, path: Path, size: int, inset: float = 0.0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp(Image, ImageDraw, size, inset=inset).save(path, format="PNG", optimize=True)


def emit_ico(Image, ImageDraw, path: Path, faces: tuple[int, ...]) -> None:
    """PNG-in-ICO directory. New filename so Windows cannot keep a sibling picture."""
    blobs: list[bytes] = []
    for n in faces:
        buf = BytesIO()
        stamp(Image, ImageDraw, n).save(buf, format="PNG")
        blobs.append(buf.getvalue())
    offset = 6 + 16 * len(faces)
    directory = bytearray()
    for n, blob in zip(faces, blobs):
        w = 0 if n >= 256 else n
        directory += struct.pack("<BBBBHHII", w, w, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fp:
        fp.write(struct.pack("<HHH", 0, 1, len(faces)))
        fp.write(directory)
        for blob in blobs:
            fp.write(blob)


def main() -> None:
    Image, ImageDraw = _need_pil()
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    emit_png(Image, ImageDraw, ICON_DIR / "icon-192.png", 192)
    emit_png(Image, ImageDraw, ICON_DIR / "icon-512.png", 512)
    emit_png(Image, ImageDraw, ICON_DIR / "icon-maskable-512.png", 512, inset=0.12)
    emit_ico(Image, ImageDraw, ICON_DIR / "bober-nightfall.ico", ICO_FACES)
    print(f"wrote {ICON_DIR / 'icon-192.png'}")
    print(f"wrote {ICON_DIR / 'icon-512.png'}")
    print(f"wrote {ICON_DIR / 'icon-maskable-512.png'}")
    print(f"wrote {ICON_DIR / 'bober-nightfall.ico'}")


if __name__ == "__main__":
    main()
