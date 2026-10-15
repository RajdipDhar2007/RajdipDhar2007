"""Turn text into SVG outlines so stylish fonts survive inside <img> SVGs (which cannot load web fonts).

    f = Font("Poppins-ExtraBold")
    d, width = f.path("Rajdip", size=64, x=0, y=64)          # one <path d=...>
    glyphs = f.glyphs("Rajdip", size=64)                        # [(d, x, advance), ...] for per-letter animation

Fonts live in scripts/fonts (all SIL Open Font License, see the OFL-*.txt files there).
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_DIR = Path(__file__).parent / "fonts"


def _n(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


class Font:
    def __init__(self, name: str):
        self.tt = TTFont(FONT_DIR / f"{name}.ttf")
        self.gs = self.tt.getGlyphSet()
        self.cmap = self.tt.getBestCmap()
        self.upm = self.tt["head"].unitsPerEm
        self.hmtx = self.tt["hmtx"]
        os2 = self.tt["OS/2"]
        self.cap = getattr(os2, "sCapHeight", 0) or self.upm * 0.7
        self.xh = getattr(os2, "sxHeight", 0) or self.upm * 0.5

    def _gname(self, ch: str) -> str:
        return self.cmap.get(ord(ch)) or self.cmap.get(ord("?"), ".notdef")

    def advance(self, ch: str, size: float) -> float:
        return self.hmtx[self._gname(ch)][0] * size / self.upm

    def width(self, text: str, size: float, tracking: float = 0.0) -> float:
        return sum(self.advance(c, size) + tracking for c in text) - (tracking if text else 0)

    def glyph_d(self, ch: str, size: float, x: float, y: float) -> str:
        pen = SVGPathPen(self.gs, ntos=_n)
        s = size / self.upm
        self.gs[self._gname(ch)].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        return pen.getCommands()

    def glyphs(self, text: str, size: float, x: float = 0, y: float = 0, tracking: float = 0.0):
        out, cx = [], x
        for ch in text:
            adv = self.advance(ch, size)
            if ch != " ":
                out.append((self.glyph_d(ch, size, cx, y), cx, adv))
            cx += adv + tracking
        return out

    def path(self, text: str, size: float, x: float = 0, y: float = 0, tracking: float = 0.0):
        d = " ".join(g[0] for g in self.glyphs(text, size, x, y, tracking))
        return d, self.width(text, size, tracking)

    def wrap(self, text: str, size: float, max_w: float, tracking: float = 0.0) -> list[str]:
        lines, cur = [], ""
        for word in text.split():
            trial = f"{cur} {word}".strip()
            if cur and self.width(trial, size, tracking) > max_w:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        return lines + ([cur] if cur else [])


@lru_cache(maxsize=None)
def font(name: str) -> Font:
    return Font(name)


# Role -> font file
DISPLAY = "Poppins-ExtraBold"
HEAD = "Poppins-SemiBold"
BODY = "Poppins-Regular"
MEDIUM = "Poppins-Medium"
SCRIPT = "KaushanScript-Regular"
SCRIPT2 = "Pacifico-Regular"
MONO = "SpaceMono-Regular"
MONO_B = "SpaceMono-Bold"
