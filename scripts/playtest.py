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
    "The fire held. Now the woods.",
    "Twigs and spit. Chop a path.",
    "Ice wants a bomb. The hound waits.",
    "End the frost. Bring the summer.",
    "Bring the summer.",
    "id=\"btn-museum\"",
    "id=\"museum\"",
    "bober-nightfall-museum-v1",
    "MUSEUM",
    "Milestones",
    "Roster",
    "Frost King",
    "Twig Rat",
    "Sleet Imp",
    "calmT = 0.62",
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
    "MAX_LV = 40",
    "ACT VI HELD",
    "The Quiet Below",
    "Lady Thaw",
    "Ice Warden",
    "Lockwight",
    "Pale Guest",
    "Chain Choir",
    "spawnEnemy(\"iward\"",
    "startPlay(26, true)",
    "assets/intro/n13.jpg",
    "Frost King down. Not done.",
    "A short vow. A long road.",
    "Held under the keep. Worth the whole winter.",
    "id=\"diff-pick\"",
    "Lodge pace.",
    "Sharper frost.",
    "No mercy. Still fair.",
    "Rime Runner",
    "Slush Brute",
    "Chill Bell",
    "Icicle Toss",
    "Keymoth",
    "spawnEnemy(\"runr\"",
    "hpScale",
    "assets/intro/n18.jpg",
    "act3Held",
    "act4Held",
    "hasTorch",
    "keepSeen",
    "FROST KEEP",
    "ACT IV HELD",
    "Stone colder than the dead.",
    "spawnEnemy(\"imp\"",
    "spawnEnemy(\"halb\"",
    "spawnEnemy(\"captain\"",
    "TORCH_R = 72",
    "btn-torch",
    "KeyF",
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
    "showBuddyTip",
    "hideBuddyTip",
    "elon-tip",
    "elon-cameo",
    "assets/sprites/john-snow.png",
    "pointerenter",
    "pointerleave",
    "CONTINUE on Held",
    "Long Night — don’t freeze.",
    "Chop the trees blocking the door.",
    "Read the tip. Then START.",
    'id="lv-start"',
    'id="btn-lv-start"',
    "waitingStart",
    "showStartGate",
    "beginLevel",
    "chopHintDone",
    "dismissStartTips",
    "calmT",
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
    for i in range(19):
        p = ROOT / "assets" / "intro" / f"n{i}.jpg"
        if not p.exists():
            errors.append("missing intro n" + str(i))
    if not (ROOT / "assets" / "splash.jpg").exists():
        errors.append("missing splash.jpg")
    if not (ROOT / "assets" / "endcard.jpg").exists():
        errors.append("missing endcard.jpg")
    if not (ROOT / "assets" / "endcard-thaw.jpg").exists():
        errors.append("missing endcard-thaw.jpg")
    if not (ROOT / "assets" / "museum" / "frost-king.jpg").exists():
        errors.append("missing museum frost-king.jpg")

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
    if "MAX_LV = 40" not in text:
        errors.append("levels not clamped to 40")
    if "MAX_LV = 15" in text:
        errors.append("old MAX_LV = 15 still present")
    if "Math.min(10, s.level" in text or "Math.min(10, n" in text:
        errors.append("old level clamp 10 still present")
    if "n === 16" not in text:
        errors.append("L16 missing")
    if "john =" in text.split("n === 16")[1].split("function allBraziersLit")[0]:
        errors.append("John Snow spawned in Act IV")
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
        "sleet-imp.png", "keep-halberd.png", "frost-captain.png",
        "frost-captain-bash.png", "torch.png", "frost-web.png",
        "ice-warden.png", "lockwight.png", "pale-guest.png",
        "chain-choir.png", "lady-thaw.png",
        "rime-runner.png", "slush-brute.png", "chill-bell.png",
        "icicle-toss.png", "keymoth.png",
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
    if "https://ccosma1.github.io/green-home-games/" not in text:
        errors.append("hub URL missing")
    if 'addSolid("fence"' in text.split("n === 18")[1].split("n === 19")[0]:
        errors.append("L18 courtyard has a fence choke")
    if "kind === \"web\" && !fromTorch" not in text:
        errors.append("frost-web must only burn from torch")
    if "kind === \"ice\"" in text and "fromTorch" not in text:
        errors.append("torch ice rule missing")
    if "e.turn = e.kind === \"rib\" ? 2.05 : e.kind === \"halb\" ? 2.0 : 2.6" not in text:
        errors.append("Keep Halberd turn not ~2.0s")
    if "0.85" not in text:
        errors.append("Keep Halberd block arc missing")
    if 'spawnEnemy("imp"' not in text:
        errors.append("Sleet Imp missing")
    if "levelN === 20 ? 4" not in text and "showActEnd(4)" not in text:
        errors.append("Act IV endcard path missing")
    if "chip-lv" in text and "L 1/40" not in text:
        errors.append("HUD not L n/40")
    if "min-height: 55dvh" not in text:
        errors.append("stage min-height not 55dvh")
    if "var TIPS" not in text or text.count("Act II.") < 1:
        errors.append("missing TIPS array")
    if text.split("var TIPS = [")[1].split("];")[0].count('"') < 80:
        errors.append("need 40 buddy tips")
    if "tipT = 3.4" not in text:
        errors.append("buddy tip auto-dismiss not ~3.4s")
    if 'id="elon-tip"' not in text.split('id="stage"')[1].split('id="dock"')[0]:
        errors.append("elon-tip not in stage (HUD crush risk)")
    elon_css = text.split("#elon-tip {")[1].split("}")[0]
    if "top:" not in elon_css:
        errors.append("elon-tip not below HUD / upper-middle")
    if "bottom: 8px" in elon_css:
        errors.append("elon-tip bottom-docked (HUD crush)")
    cam_css = text.split("#elon-cameo {")[1].split("}")[0]
    if "bottom: 8px" in cam_css:
        errors.append("elon-cameo bottom-docked under stick")
    if "top:" not in cam_css:
        errors.append("elon-cameo not parked below HUD")
    stage = text.split('id="stage"')[1].split('id="dock"')[0]
    if "buddy.png" in stage:
        errors.append("elon tip/cameo still uses buddy.png")
    if stage.count("john-snow.png") < 2:
        errors.append("elon tip/cameo not using john-snow.png")
    if "bindTipHover" not in text or "fromHover" not in text:
        errors.append("cameo hover-to-hint missing")
    if "btn-end-ok" in text and 'startPlay(11, true)' not in text:
        errors.append("CONTINUE L10→L11 missing")
    if "btn-end-ok" in text and 'startPlay(16, true)' not in text:
        errors.append("CONTINUE L15→L16 missing")
    if "btn-end-ok" in text and 'startPlay(21, true)' not in text:
        errors.append("CONTINUE L20→L21 missing")
    if "wallet" in text.lower() and "No wallet" not in text:
        errors.append("wallet mention without denial")
    tips_block = text.split("var TIPS = [")[1].split("];")[0].lower()
    if "wallet" in tips_block or "crypto" in tips_block or "gacha" in tips_block:
        errors.append("buddy tips pitch wallet/crypto/gacha")

    if 'id="btn-lv-start"' not in text.split('id="stage"')[1].split('id="dock"')[0]:
        errors.append("START button not in stage")
    if "showStartGate()" not in text.split("function buildLevel")[1].split("function allBraziersLit")[0]:
        errors.append("buildLevel must show START gate")
    if "waitingStart" not in text.split("function frame")[1].split("function setStick")[0]:
        errors.append("frame must freeze until START")
    if ".chop = true" not in text:
        errors.append("L1 blocking trees not marked chop")
    if "function maybeClear" in text and 'kind === "bush" && props[i].alive' in text.split("function maybeClear")[1].split("function tryExit")[0]:
        errors.append("L1 still clears on bushes not trees")
    if "props[i].chop && props[i].alive" not in text:
        errors.append("L1 clear must count chop trees")
    if "exitDoor.needKey = false" not in text:
        errors.append("L1 door must lock without a key icon")
    if 'strokeText("CHOP"' not in text and 'fillText("CHOP"' not in text:
        errors.append("L1 missing CHOP ping on blocking trees")
    bl = text.split("function buildLevel")[1].split("function allBraziersLit")[0]
    if 'say("TIP"' in bl or 'say("JOHN SNOW"' in bl or 'say("CAMP"' in bl:
        errors.append("level start still fires say() plus buddy tip")
    if "showBuddyTip()" not in bl:
        errors.append("level start missing single buddy tip")
    if "dismissStartTips()" not in text.split("function beginLevel")[1].split("function addPop")[0]:
        errors.append("START must dismiss tip UI")
    if "calmT" not in text.split("function updateEnemy")[1][:400]:
        errors.append("post-START calm window missing on enemies")
    if "calmT = 1.25" in text:
        errors.append("post-START freeze still 1.25s (should be ~half)")
    if "calmT = 0.62" not in text:
        errors.append("post-START freeze not halved to ~0.62s")
    if "First he yeeted." in text or "Then he held the dam." in text:
        errors.append("old yeet/dam intro captions still present")
    if 'id="btn-museum"' not in text.split('id="splash"')[1].split('id="history"')[0]:
        errors.append("Museum button missing on splash")
    if 'id="btn-museum2"' not in text.split('id="paused"')[1].split('id="shop"')[0]:
        errors.append("Museum button missing on pause")
    if "var ROSTER" not in text or "var MILES" not in text:
        errors.append("museum roster/milestones missing")
    hist_line_css = text.split("#history .hist-line")[1].split("}")[0]
    if "-webkit-line-clamp: 2" in hist_line_css:
        errors.append("hist-line still two-line clamp")
    intro_block = text.split("var INTRO = [")[1].split("];")[0].lower()
    if "meadow" in intro_block or "yeeted" in intro_block:
        errors.append("intro copy not Nightfall story")
    if "if (s.act5Held) { applySaveMeta(s); showActEnd(5)" in text:
        errors.append("ACT V CONTINUE still camps Held instead of L26")
    if "function buildQuietBelow" not in text:
        errors.append("Act VI builder missing")
    if "function startNewRun" not in text or "diffId" not in text:
        errors.append("difficulty picker missing")
    if "width: 148px" not in text or "height: 148px" not in text:
        errors.append("phone stick not enlarged")
    if "min-width: 64px" not in text:
        errors.append("phone action buttons not enlarged")
    if "eatDockTouch" not in text:
        errors.append("dock touch preventDefault missing")
    dock_css = text.split("    #dock {")[1].split("    #stick {")[0]
    if "touch-action: none" not in dock_css:
        errors.append("dock missing touch-action none")
    if 'difficulty === "easy" ? 1' not in text and "hpScale" not in text:
        errors.append("easy must stay 1.0x")
    if "Lady Thaw" not in text or "The Quiet Below" not in text:
        errors.append("Act VI names missing")
    if 'id="mus-detail"' not in text:
        errors.append("museum card detail overlay missing")
    if "function openMusDetail" not in text or "function closeMusDetail" not in text:
        errors.append("museum detail open/close missing")
    if "data-id" not in text.split("function paintMuseum")[1].split("function findMusCard")[0]:
        errors.append("museum cards not tagged for tap")
    paint_js = text.split("function paintMuseum")[1].split("function findMusCard")[0]
    if "<button" not in paint_js or "mus-card" not in paint_js:
        errors.append("museum cards not buttons")
    if "Reach this act to unlock." not in text:
        errors.append("locked detail tease missing")

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
