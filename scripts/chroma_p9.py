#!/usr/bin/env python3
"""Chroma-key Prompt 9 sprites and copy intro stills."""
from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

from process_sprites import chroma_key, tight_crop

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\calle\.grok\sessions\C%3A%5CUsers%5Ccalle\01a09bc9-59eb-7a32-a982-1f24a4adaecf\images")
SPR = ROOT / "assets" / "sprites"
INTRO = ROOT / "assets" / "intro"
MUS = ROOT / "assets" / "museum"

CHROMA = [
    ("12.jpg", "lady-thaw.png"),
    ("9.jpg", "ice-warden.png"),
    ("10.jpg", "lockwight.png"),
    ("17.jpg", "pale-guest.png"),
    ("8.jpg", "chain-choir.png"),
]
STILLS = [
    ("14.jpg", "n6.jpg"),
    ("13.jpg", "n7.jpg"),
    ("18.jpg", "n8.jpg"),
    ("21.jpg", "n9.jpg"),
    ("16.jpg", "n10.jpg"),
    ("15.jpg", "n11.jpg"),
    ("20.jpg", "n12.jpg"),
    ("19.jpg", "n13.jpg"),
]


def main() -> None:
    SPR.mkdir(parents=True, exist_ok=True)
    INTRO.mkdir(parents=True, exist_ok=True)
    MUS.mkdir(parents=True, exist_ok=True)
    for src_name, dest_name in CHROMA:
        src = SRC / src_name
        im = chroma_key(Image.open(src))
        im = tight_crop(im, 12)
        im.save(SPR / dest_name)
        print("sprite", dest_name, im.size)
    for src_name, dest_name in STILLS:
        Image.open(SRC / src_name).convert("RGB").save(INTRO / dest_name, quality=92)
        print("intro", dest_name)
    Image.open(SRC / "19.jpg").convert("RGB").save(ROOT / "assets" / "endcard-thaw.jpg", quality=92)
    print("endcard-thaw")
    shutil.copyfile(SPR / "lady-thaw.png", MUS / "lady-thaw.png")
    print("museum lady-thaw")


if __name__ == "__main__":
    main()
