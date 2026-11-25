"""render.py — tiny stdlib-only bitmap canvas + PNG writer.

Written fresh for the news-image-20261124 entry. No third-party code,
no network, no randomness, no wall-clock reads: output is deterministic.
"""

import struct
import zlib

# ---------------------------------------------------------------- font ----
# 5x7 pixel glyphs, hand-designed for this entry. Each glyph is 7 rows of
# 5 characters; '#' is ink, '.' is empty. Only the characters the layout
# actually uses are defined: A-Z, 0-9 and a small punctuation set. All
# layout text is uppercase, so no lowercase glyphs exist.

FONT = {
    "A": (" .###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
}

GLYPH_W = 5
GLYPH_H = 7
ADVANCE = 6  # glyph width + 1px tracking


def text_width(text, scale):
    """Pixel width of text at the given scale (no wrapping)."""
    if not text:
        return 0
    return (len(text) * ADVANCE - 1) * scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap. Returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    """RGB canvas with filled rectangles, text and a PNG writer."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background) * (width * height)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            span = (x1 - x0) * 3
            row = bytearray((r, g, b)) * (x1 - x0)
            self.pixels[base:base + span] = row

    def draw_glyph(self, x, y, char, scale, color):
        glyph = FONT.get(char)
        if glyph is None:
            return
        for gy in range(GLYPH_H):
            row = glyph[gy]
            for gx in range(GLYPH_W):
                if row[gx] == "#":
                    self.fill_rect(
                        x + gx * scale, y + gy * scale, scale, scale, color
                    )

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for char in text:
            self.draw_glyph(cx, y, char, scale, color)
            cx += ADVANCE * scale
        return cx

    def draw_text_centered(self, cx, y, text, scale, color):
        x = cx - text_width(text, scale) // 2
        self.draw_text(x, y, text, scale, color)

    def draw_wrapped(self, x, y, text, scale, color, max_width, line_gap=4):
        """Draw wrapped text; returns the y just below the last line."""
        line_h = GLYPH_H * scale + line_gap
        cy = y
        for line in wrap_text(text, scale, max_width):
            self.draw_text(x, cy, line, scale, color)
            cy += line_h
        return cy

    def draw_circle_outline(self, cx, cy, radius, thickness, color):
        """Rough circle outline, used as a small globe motif."""
        r2 = radius * radius
        inner = (radius - thickness) * (radius - thickness)
        for yy in range(cy - radius, cy + radius + 1):
            for xx in range(cx - radius, cx + radius + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if inner <= d2 <= r2:
                    if 0 <= xx < self.width and 0 <= yy < self.height:
                        base = (yy * self.width + xx) * 3
                        self.pixels[base:base + 3] = bytes(color)

    # ------------------------------------------------------------ PNG ----
    def to_png_bytes(self):
        raw = bytearray()
        stride = self.width * 3
        for yy in range(self.height):
            raw.append(0)  # filter: none
            start = yy * stride
            raw += self.pixels[start:start + stride]
        compressed = zlib.compress(bytes(raw), 9)

        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)
        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", ihdr)
        png += chunk(b"IDAT", compressed)
        png += chunk(b"IEND", b"")
        return png
