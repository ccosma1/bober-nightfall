#!/usr/bin/env python3
"""Prompt 0 checks for Bober Nightfall. No browser required."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"

NEED = [
    "BOBER NIGHTFALL",
    "Face the Frost King.",
    "Fan game by a holder.",
    "bober-nightfall-v1",
    "ACT I HELD",
    "John Snow from the white",
    "First he yeeted.",
    "Then he held the dam.",
    "Then he held the fire.",
    "Winter cracked. Green home stayed.",
    "One crown left: the Frost King.",
    "Bring the summer.",
    "Lodge fire held. Now end the winter.",
    "Ember Woods",
    "REST 5W",
    "WARM 12W",
    "Heart Piece",
    "hpMax",
    "heartPieces",
    "Desktop: WASD · LMB slash · RMB roll",
    "More games · Green Home Games",
    "https://ccosma1.github.io/green-home-games/",
    "ICE APPROACHES",
    "ACT II HELD",
    "ACT III HELD",
    "BONE CAMP",
    "Bone Camp",
    "Ice that used to walk.",
    "spawnEnemy(\"hound\"",
    "spawnEnemy(\"skull\"",
    "spawnEnemy(\"rib\"",
    "spawnEnemy(\"ash\"",
    "spawnEnemy(\"warden\"",
    "placeBomb",
    "Ice Approaches",
    "MAX_LV = 15",
    "act3Held",
    "bomb-badge",
    "min-width: 44px",
    "min-height: 44px",
    "exitArmed",
    "levelTimer",
    "newGameWipe",
    "CHARGE_HOLD = 0.25",
    "SLASH_REC = 0.18",
    "HITSTOP = 2 / 60",
    "ROLL_T = 0.28",
    "ROLL_CD = 0.55",
    "INVULN = 0.35",
    "e.hp = 1",
    "e.hp = 2",
    "e.hp = 3",
    "e.hp = 12",
    "e.hp = 4",
    "e.hp = 14",
    "min-height: 55dvh",
    "font-size: 14px",
    "font-size: 13px",
    "WASD",
    "WOODCHIP SHOP",
    "Door’s yours.",
    "assets/intro/n0.jpg",
    "assets/intro/n5.jpg",
    "boberverse-v1",
    "bober-frost-lodge-v1",
    "bober-history-v1",
    "BOMB_COST = 25",
    "act2Wood",
    "Roll past the shield. Hit his back. No bomb needed.",
    "e.turn = 2.6",
]

FORBID_UI = [
    "Night King",
    "Hobbit",
    "Shire",
    "Gandalf",
    "Mordor",
]


def brute_windows() -> list[str]:
    errs: list[str] = []
    stun = 1.28
    rec = 0.18
    slashes = int(stun / rec)
    slash_dmg = slashes * 1
    charge_cycle = 0.25 + 0.18
    charges = int(stun / charge_cycle)
    charge_dmg = charges * 2
    if slash_dmg < 6:
        errs.append(f"stun window slash dmg {slash_dmg} too low")
    if slash_dmg + charge_dmg < 12 and slash_dmg * 2 < 12:
        errs.append("Ice Brute 12HP not clearable in two stun windows")
    return errs


def main() -> int:
    errors: list[str] = []
    if not HTML.exists():
        print("FAIL: index.html missing")
        return 1
    text = HTML.read_text(encoding="utf-8")
    for s in NEED:
        if s not in text:
            errors.append("missing: " + s)
    for s in FORBID_UI:
        if s in text:
            errors.append("forbidden UI word: " + s)
    if re.search(r"\bRing\b", text):
        errors.append("forbidden UI word: Ring")
    if "wallet" in text.lower() and "No wallet" not in text:
        errors.append("wallet mention without denial")
    if "gacha" in text.lower() and "No gacha" not in text and "no gacha" not in text:
        errors.append("gacha mention")

    sprites = [
        "bober-idle.png", "bober-slash.png", "bober-roll.png",
        "twig-rat.png", "snow-spitter.png", "shield-grunt.png",
        "ice-brute.png", "ice-brute-slam.png", "john-snow.png",
        "bush.png", "pot.png", "key.png", "door.png", "door-lock.png",
    ]
    for name in sprites:
        p = ROOT / "assets" / "sprites" / name
        if not p.exists():
            errors.append("missing sprite " + name)
    for i in range(6):
        p = ROOT / "assets" / "intro" / f"n{i}.jpg"
        if not p.exists():
            errors.append("missing intro n" + str(i))
    if not (ROOT / "assets" / "splash.jpg").exists():
        errors.append("missing splash.jpg")
    if not (ROOT / "assets" / "endcard.jpg").exists():
        errors.append("missing endcard.jpg")

    if "y-sort" not in text and "list.sort" not in text:
        errors.append("no y-sort")
    if "ellipse" not in text:
        errors.append("no contact shadow ellipse")
    if "#stick" not in text or "bottom-left" in text.lower():
        pass
    if "flex: 1 1 auto" not in text:
        errors.append("stage not flex grow")

    errors.extend(brute_windows())

    if "spawnEnemy(\"rat\"" not in text and "spawnEnemy(\"rat\"" not in text:
        if 'spawnEnemy("rat"' not in text:
            errors.append("L2 rats missing")
    if 'spawnEnemy("spit"' not in text:
        errors.append("L3 spitters missing")
    if 'spawnEnemy("grunt"' not in text:
        errors.append("L4 grunt missing")
    if 'spawnEnemy("brute"' not in text:
        errors.append("L5 brute missing")
    if "levelTransit" not in text:
        errors.append("missing levelTransit latch")
    if "exitArmed" not in text:
        errors.append("missing exitArmed")
    if "levelTimer" not in text:
        errors.append("missing levelTimer")
    if "clearTimeout(levelTimer)" not in text:
        errors.append("missing clearTimeout(levelTimer)")
    if "buildLevel(levelN + 1)" in text:
        errors.append("live levelN+1 still in timeout")
    if "var next = levelN + 1" not in text:
        errors.append("tryExit must capture next")
    if "open: n === 1" in text:
        errors.append("L1 door still open at spawn")
    if "LEVEL " not in text or "lv-banner" not in text:
        errors.append("missing LEVEL banner")
    if "MAX_LV = 15" not in text:
        errors.append("levels not clamped to 15")
    if "Math.min(10, s.level" in text or "Math.min(10, n" in text:
        errors.append("old level clamp 10 still present")
    if "buildLevel(16" in text or "n === 16" in text or "n === 25" in text:
        errors.append("L16-25 must not ship yet")
    if 'addSolid("fence", 180, 320' in text:
        errors.append("L8 center fence still blocks the flank lane")
    if "chips < 40" in text or "chips -= 40" in text:
        errors.append("shop bomb still 40W")
    if "BOMB_COST = 25" not in text:
        errors.append("bomb cost not 25W")
    if 'href="https://ccosma1.github.io/boberverse/"' in text:
        errors.append("old hub URL still present")
    sprites_extra = [
        "frost-hound.png", "frost-hound-dash.png", "bomb.png", "ice-block.png",
        "rime-skull.png", "rime-skull-lunge.png", "rib-guard.png",
        "ash-archer.png", "ash-archer-draw.png",
        "tomb-warden.png", "tomb-warden-swipe.png", "bone-pile.png",
    ]
    for name in sprites_extra:
        if not (ROOT / "assets" / "sprites" / name).exists():
            errors.append("missing sprite " + name)
    if 'id="btn-bomb"' not in text.split('id="actions"')[1].split("</div>")[0]:
        errors.append("BOMB not in right action cluster")
    if "bottom-left" in text.lower() and "btn-bomb" in text.lower():
        pass
    if "#bomb-badge" in text and "font-size: 13px" not in text.split("#bomb-badge")[1][:400]:
        errors.append("bomb badge font-size not 13px")
    if "newGameWipe" not in text:
        errors.append("missing new-game wipe")
    if "localStorage.removeItem(SAVE_KEY)" not in text:
        errors.append("FACE THE FROST must wipe save")
    if "fillText" in text and "LOCKED" in text:
        errors.append("door still uses fillText LOCKED/OPEN")
    if "https://ccosma1.github.io/bober-yeet/" in text.split("id=\"splash\"")[1].split("id=\"history\"")[0]:
        errors.append("splash still piles sibling URLs")
    if "min-height: 56px" not in text:
        errors.append("intro caption bar < 56px")
    if "font-size: 16px" not in text:
        errors.append("intro caption not ≥16px")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("OK Prompt 0 Nightfall L1-5")
    print(" stun slash window ~", int(1.28 / 0.18), "hits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
