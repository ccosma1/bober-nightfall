#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
from process_sprites import chroma_key, tight_crop

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\calle\.grok\sessions\C%3A%5CUsers%5Ccalle\01a09bc9-59eb-7a32-a982-1f24a4adaecf\images")
SPR = ROOT / "assets" / "sprites"
INTRO = ROOT / "assets" / "intro"

CHROMA = [
    ("22.jpg", "rime-runner.png"),
    ("25.jpg", "slush-brute.png"),
    ("26.jpg", "chill-bell.png"),
    ("23.jpg", "icicle-toss.png"),
    ("24.jpg", "keymoth.png"),
]
STILLS = [
    ("28.jpg", "n14.jpg"),
    ("27.jpg", "n15.jpg"),
    ("29.jpg", "n16.jpg"),
    ("30.jpg", "n17.jpg"),
    ("31.jpg", "n18.jpg"),
]


def main() -> None:
    SPR.mkdir(parents=True, exist_ok=True)
    INTRO.mkdir(parents=True, exist_ok=True)
    for src_name, dest_name in CHROMA:
        im = chroma_key(Image.open(SRC / src_name))
        im = tight_crop(im, 12)
        im.save(SPR / dest_name)
        print("sprite", dest_name, im.size)
    for src_name, dest_name in STILLS:
        Image.open(SRC / src_name).convert("RGB").save(INTRO / dest_name, quality=92)
        print("intro", dest_name)


if __name__ == "__main__":
    main()
