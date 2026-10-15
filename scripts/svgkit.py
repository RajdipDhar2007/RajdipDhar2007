"""Tiny helpers for hand-built animated SVGs (CSS keyframes, no JS)."""
from __future__ import annotations
import math
from xml.sax.saxutils import escape

EPS = 0.002  # seconds; makes hard edges between keyframes (offsets must stay distinct)


def pct(t: float, total: float) -> str:
    v = max(0.0, min(100.0, t / total * 100))
    return f"{v:.4f}".rstrip("0").rstrip(".") + "%"


def window_keyframes(name: str, total: float, windows, prop="opacity", on="1", off="0") -> str:
    """Keyframes that are `on` inside each (start, end) window and `off` elsewhere."""
    pts = [(0.0, off)]
    for a, b in sorted(windows):
        if a <= 0:
            pts[0] = (0.0, on)
        else:
            pts += [(a - EPS, off), (a, on)]
        if b < total:
            pts += [(b - EPS, on), (b, off)]
    if pts[-1][0] < total:
        pts.append((total, pts[-1][1]))
    body = "".join(f"{pct(t, total)}{{{prop}:{v}}}" for t, v in pts)
    return f"@keyframes {name}{{{body}}}"


def wave_path(width: float, base: float, amp: float, period: float, phase: float = 0.0, close_to=None) -> str:
    """Sine path from x=0..width; close_to = y to fill towards (None = open line)."""
    n = max(8, int(width / period * 24))
    pts = []
    for i in range(n + 1):
        x = width * i / n
        y = base + amp * math.sin(2 * math.pi * x / period + phase)
        pts.append(f"{x:.1f},{y:.1f}")
    d = "M" + " L".join(pts)
    if close_to is not None:
        d += f" L{width:.0f},{close_to:.0f} L0,{close_to:.0f} Z"
    return d


def esc(s: str) -> str:
    return escape(s)
