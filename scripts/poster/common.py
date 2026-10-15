"""Design system + SVG helpers shared by every poster asset."""
from __future__ import annotations
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import typo  # noqa: E402,F401
from svgkit import esc  # noqa: E402,F401

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets"

PAL = {
    "dark": dict(page="#0D1117", base="#0B1220", base2="#111B33", card="#131B2B", line="#263247", ink="#E6EDF3", muted="#8B98AD",
                 accent="#22D3EE", second="#A78BFA", pink="#F472B6", green="#39D353", glow=0.55, blend="screen"),
    "light": dict(page="#FFFFFF", base="#F4F7FC", base2="#E8EEFB", card="#FFFFFF", line="#D5DCEA", ink="#1F2328", muted="#59636E",
                  accent="#0969DA", second="#8250DF", pink="#D6336C", green="#1A7F37", glow=0.35, blend="multiply"),
}
MODES = ("dark", "light")
REDUCE = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
EPS = 0.01


def pct(t: float, total: float) -> str:
    v = max(0.0, min(100.0, t / total * 100))
    return (f"{v:.3f}".rstrip("0").rstrip(".") or "0") + "%"


def kf(name: str, total: float, points: list[tuple[float, str]]) -> str:
    """@keyframes from [(seconds, 'css props'), ...]; duplicate offsets are nudged apart."""
    out, last = [], -1.0
    for t, props in points:
        p = max(t, last + EPS * 0.05) if t <= last else t
        out.append(f"{pct(p, total)}{{{props}}}")
        last = p
    return f"@keyframes {name}{{{''.join(out)}}}"


def window_pts(a: float, b: float, total: float, on: str, off: str, fade: float = 0.0):
    """Points for 'off until a, on in [a,b], off after b' (fade>0 -> soft edges)."""
    pts = [(0, off)]
    if a > fade:
        pts += [(a - fade, off)]
    pts += [(a, on), (b, on)]
    if b + fade < total:
        pts += [(b + fade, off)]
    pts += [(total, off)]
    return pts


def doc(w: int, h: int, body: str, css: str = "", defs: str = "", label: str = "", pad_y: int = 0) -> str:
    """pad_y adds breathing room top and bottom so bobbing elements are never clipped by the viewBox."""
    if pad_y:
        body, h = f'<g transform="translate(0 {pad_y})">{body}</g>', h + 2 * pad_y
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(label)}">'
            f'<title>{esc(label)}</title><defs>{defs}</defs><style>{css}{REDUCE}</style>{body}</svg>')


def lin_grad(gid: str, stops: list[tuple[float, str]], x1=0, y1=0, x2=1, y2=0, extra="") -> str:
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {extra}>{s}</linearGradient>'


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    kb = len(text.encode()) / 1024
    print(f"  {path.relative_to(ROOT)}  {kb:.0f} KB")


def rng(seed: int) -> random.Random:
    return random.Random(seed)


def icon(name: str, x: float, y: float, size: float, fill: str, extra: str = "") -> str:
    """simple-icons glyph (24x24 box) placed at x,y with the given size."""
    import json
    data = json.loads((Path(__file__).resolve().parents[1] / "icons.json").read_text(encoding="utf-8"))
    s = size / 24
    return f'<path d="{data[name]["path"]}" transform="translate({x:.1f} {y:.1f}) scale({s:.4f})" fill="{fill}" {extra}/>'


def icon_hex(name: str) -> str:
    import json
    data = json.loads((Path(__file__).resolve().parents[1] / "icons.json").read_text(encoding="utf-8"))
    return "#" + data[name]["hex"]
