#!/usr/bin/env python3
"""news-image-20261124 — "The World in One Day".

Draws one deterministic 1024x1024 PNG summarising world news from
Tuesday 24 November 2026. Standard library only. No network, no
randomness, no wall-clock reads: two runs produce byte-identical output.

Layout (fresh for this edition):
  masthead -> wide COP31 lead banner -> 2x2 grid
  (Nvidia, Sanofi, Rohingya, Grok) -> bottom strip (measles + Nepal).
"""

import os
import sys

# The grader runs `python3 -P -s /bot/main.py`; -P does not add the script
# directory to sys.path, so insert it here BEFORE importing the sibling.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import Canvas, text_width, wrap_text

W, H = 1024, 1024

CREAM = (247, 243, 233)
NAVY = (16, 36, 62)
RED = (178, 34, 34)
GOLD = (242, 201, 76)
LEAD_BG = (11, 61, 46)
WHITE = (255, 255, 255)
INK = (24, 24, 24)
MUTED = (96, 96, 96)
CELL_BG = (255, 255, 255)
STRIP_BG = (232, 237, 243)
STRIP_INK = (28, 42, 60)
GREEN = (118, 185, 0)
PURPLE = (109, 40, 217)
MAROON = (127, 29, 29)
SLATE = (17, 24, 39)

MARGIN = 12
COL_W = 494
ROW_H = 236


def draw_masthead(cv):
    cv.fill_rect(0, 0, W, 100, NAVY)
    cv.draw_text_centered(W // 2, 16, "THE WORLD IN ONE DAY", 4, WHITE)
    cv.draw_text_centered(
        W // 2, 60, "TUESDAY 24 NOVEMBER 2026", 2, GOLD
    )
    cv.fill_rect(0, 96, W, 4, RED)


def draw_lead(cv):
    y0, y1 = 112, 308
    cv.fill_rect(MARGIN, y0, W - 2 * MARGIN, y1 - y0, LEAD_BG)
    x = MARGIN + 24
    cv.draw_text(x, y0 + 16, "LEAD STORY - CLIMATE", 2, GOLD)
    cv.draw_text(x, y0 + 44, "COP31 COLLAPSES", 5, WHITE)
    # Small globe motif at the right of the headline.
    cx, cy = 924, y0 + 78
    cv.draw_circle_outline(cx, cy, 46, 4, GOLD)
    cv.fill_rect(cx - 46, cy - 2, 92, 4, GOLD)
    body = (
        "UN CLIMATE TALKS IN ANTALYA ENDED WITH NO OVERARCHING DEAL. "
        "THE EU AND A 130-NATION BLOC REJECTED THE DRAFT - NO "
        "FOSSIL-FUEL TRANSITION CALL. LONGEST COP EVER: 50+ HOURS "
        "OVERTIME."
    )
    cv.draw_wrapped(x, y0 + 118, body, 2, (226, 238, 228), 800)


def draw_cell(cv, x, y, accent, kicker, headline, body):
    cv.fill_rect(x, y, COL_W, ROW_H, CELL_BG)
    cv.fill_rect(x, y, COL_W, 10, accent)
    ix = x + 20
    iw = COL_W - 40
    cv.draw_text(ix, y + 22, kicker, 2, accent)
    lines = wrap_text(headline, 3, iw)
    hy = y + 50
    for line in lines:
        cv.draw_text(ix, hy, line, 3, INK)
        hy += 25
    cv.draw_wrapped(ix, hy + 10, body, 2, (58, 58, 58), iw)


def draw_grid(cv):
    y_top, y_bot = 320, 568
    draw_cell(
        cv, MARGIN, y_top, GREEN, "TECH - NVIDIA", "HUANG IS BACK",
        "NVIDIA'S BOARD UNANIMOUSLY REINSTATED JENSEN HUANG AS CEO, "
        "11 DAYS AFTER HE RESIGNED. TRUMP SAYS HE CONVINCED THE BOARD. "
        "SHARES JUMPED ABOUT 31%. US COMMERCE BLACKLISTED MEGASPEED "
        "ON 24 NOV.",
    )
    draw_cell(
        cv, MARGIN + COL_W + 12, y_top, PURPLE, "PHARMA - $41BN DEAL",
        "SANOFI BUYS INSMED",
        "ANNOUNCED TUE 24 NOV: $175 A SHARE IN CASH, THE BIGGEST "
        "BIOTECH DEAL IN ABOUT 3 YEARS. LUNG DRUGS BRINSUPRI + "
        "ARIKAYCE.",
    )
    draw_cell(
        cv, MARGIN, y_bot, MAROON, "JUSTICE - ICJ",
        "UK RECOGNISES ROHINGYA GENOCIDE",
        "THE ICJ RULED ON 19 NOV THAT MYANMAR COMMITTED GENOCIDE. "
        "THE UK FORMALLY RECOGNISED IT ON 23 NOV AND SANCTIONED FIVE "
        "SENIOR MYANMAR OFFICERS. GBP 5M AID PLANNED.",
    )
    draw_cell(
        cv, MARGIN + COL_W + 12, y_bot, SLATE, "LAW - AI SAFETY",
        "STATES SUE OVER GROK IMAGES",
        "VIRGINIA AND OREGON SUED SPACEX ON 23 NOV - THE FIRST "
        "STATES TO SUE - ALLEGING GROK MADE NONCONSENSUAL SEXUAL "
        "IMAGES, INCLUDING OF CHILDREN.",
    )


def draw_strip(cv):
    y0, y1 = 816, 1004
    for x in (MARGIN, MARGIN + COL_W + 12):
        cv.fill_rect(x, y0, COL_W, y1 - y0, STRIP_BG)
    ix = MARGIN + 20
    iw = COL_W - 40
    cv.draw_text(ix, y0 + 18, "HEALTH - USA", 2, (150, 40, 40))
    cv.draw_text(ix, y0 + 46, "US LOSES MEASLES ELIMINATION STATUS", 2,
                 STRIP_INK)
    cv.draw_wrapped(
        ix, y0 + 78,
        "PAHO ANNOUNCED IT ON 17 NOV - STATUS HELD SINCE 2000. "
        "5,838 CASES IN 2026. PENNSYLVANIA REPORTED ITS 9TH DEATH.",
        2, (58, 58, 58), iw,
    )
    ix2 = MARGIN + COL_W + 12 + 20
    cv.draw_text(ix2, y0 + 18, "ALSO TODAY - ASIA", 2, (40, 90, 60))
    cv.draw_text(ix2, y0 + 46, "NEPAL QUAKE 5.6", 3, STRIP_INK)
    cv.draw_wrapped(
        ix2, y0 + 88,
        "STRUCK KOSHI PROVINCE NEAR THE TIBET BORDER TUE 24 NOV, "
        "07:17 LOCAL. NO CASUALTIES REPORTED.",
        2, (58, 58, 58), iw,
    )


def main():
    cv = Canvas(W, H, CREAM)
    draw_masthead(cv)
    draw_lead(cv)
    draw_grid(cv)
    draw_strip(cv)
    cv.draw_text_centered(
        W // 2, 1008,
        "SIX STORIES + ONE BRIEF - ALL FROM TUESDAY 24 NOVEMBER 2026",
        1, MUTED,
    )

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = "/output" if os.path.isdir("/output") else "out"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(cv.to_png_bytes())
    print("wrote", path)


if __name__ == "__main__":
    main()
