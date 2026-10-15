"""Generate header/footer wave banners and the typing-intro SVG (dark + light)."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from theme import THEMES, MONO, PROMPT, NAME  # noqa: E402
from svgkit import wave_path, pct, esc, EPS  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "assets" / "banners"
REDUCE = "@media (prefers-reduced-motion: reduce){*{animation:none!important}%s}"

TYPING_LINES = [
    "First-year CSE @ HITK",
    "Building with TypeScript, Kotlin, C & Python",
    "Exploring AI / LLM apps & automation",
    "Open to internships & collaborations",
]


def grad(name, c):
    return (f'<linearGradient id="{name}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["second"]}"/></linearGradient>')


def banner(kind: str, mode: str) -> str:
    c = THEMES[mode]
    W = 1000
    H = 240 if kind == "header" else 150
    ink = "#0D1117" if mode == "dark" else "#FFFFFF"
    footer = kind == "footer"
    fill_to = H if footer else 0

    def layer(base, amp, period, phase, dur, opacity, rev=False):
        d = wave_path(W * 2, base, amp, period, phase, close_to=fill_to)
        d_rev = " reverse" if rev else ""
        return f'<path d="{d}" fill="url(#g)" opacity="{opacity}" style="animation:w {dur}s linear infinite{d_rev}"/>'

    if footer:
        layers = [layer(44, 14, 1000, 0.0, 16, .30), layer(32, 11, 500, 1.2, 11, .5, True), layer(22, 8, 250, 2.4, 8, 1)]
        text = (f'<text x="{W/2}" y="{H/2 + 30}" text-anchor="middle" class="fi" font-size="24" fill="{ink}">'
                f'thanks for stopping by &#183; {PROMPT} exit</text>')
    else:
        layers = [layer(H - 44, 14, 1000, 0.0, 16, .30), layer(H - 32, 11, 500, 1.2, 11, .5, True), layer(H - 22, 8, 250, 2.4, 8, 1)]
        text = (f'<text x="{W/2}" y="{H/2 - 14}" text-anchor="middle" class="fi" font-size="64" font-weight="700" fill="{ink}">{esc(NAME)}</text>'
                f'<text x="{W/2}" y="{H/2 + 30}" text-anchor="middle" class="fi2" font-size="24" fill="{ink}" opacity=".9">CSE @ HITK &#183; Builder</text>')
    css = (f"text{{font-family:{MONO}}}"
           "@keyframes w{from{transform:translateX(0)}to{transform:translateX(-1000px)}}"
           "@keyframes f{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
           ".fi{animation:f 1.2s ease-out both}.fi2{animation:f 1.2s .5s ease-out both}" + REDUCE % "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(NAME)} banner">'
            f'<defs>{grad("g", c)}</defs><style>{css}</style>{"".join(layers)}{text}</svg>')


def typing(mode: str) -> str:
    c = THEMES[mode]
    W, H, FS = 760, 54, 22
    CW = FS * 0.6
    hold, typ, gap = 1.9, 1.5, 0.3
    seg = typ + hold + gap
    total = seg * len(TYPING_LINES)
    css = [f"text{{font-family:{MONO};font-size:{FS}px}}",
           REDUCE % ".ln{opacity:0}.ln0{opacity:1;clip-path:none}.cur{opacity:0}.cu0{opacity:1;transform:translateX(%.1fpx)}" % (len(TYPING_LINES[0]) * CW)]
    parts = []
    for i, line in enumerate(TYPING_LINES):
        n = len(line)
        t0 = i * seg
        tw = n * CW
        x = (W - tw) / 2 - 8
        a, b, e = t0, t0 + typ, t0 + typ + hold
        st = f"animation-timing-function:steps({n},end)"
        kf = (f"@keyframes l{i}{{0%{{opacity:0;clip-path:inset(0 100% 0 0)}}"
              f"{pct(max(a - EPS, 0), total)}{{opacity:0;clip-path:inset(0 100% 0 0)}}"
              f"{pct(a, total)}{{opacity:1;clip-path:inset(0 100% 0 0);{st}}}"
              f"{pct(b, total)}{{opacity:1;clip-path:inset(0 0 0 0)}}"
              f"{pct(e, total)}{{opacity:1;clip-path:inset(0 0 0 0)}}"
              f"{pct(e + EPS, total)}{{opacity:0}}100%{{opacity:0}}}}")
        css.append(kf + f".ln{i}{{animation:l{i} {total:.1f}s linear infinite}}")
        css.append(f"@keyframes c{i}{{0%{{opacity:0;transform:translateX(0)}}"
                   f"{pct(max(a - EPS, 0), total)}{{opacity:0;transform:translateX(0)}}"
                   f"{pct(a, total)}{{opacity:1;transform:translateX(0);{st}}}"
                   f"{pct(b, total)}{{opacity:1;transform:translateX({tw:.1f}px)}}"
                   f"{pct(e, total)}{{opacity:1;transform:translateX({tw:.1f}px)}}"
                   f"{pct(e + EPS, total)}{{opacity:0}}100%{{opacity:0}}}}.cu{i}{{animation:c{i} {total:.1f}s linear infinite}}")
        parts.append(f'<text class="ln ln{i}" x="{x:.1f}" y="35" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs" fill="{c["text"]}">{esc(line)}</text>')
        parts.append(f'<rect class="cur cu{i}" x="{x + 2:.1f}" y="14" width="10" height="26" rx="1" fill="{c["accent"]}"/>')
    prompt = f'<text x="8" y="35" fill="{c["accent"]}" font-weight="700">$</text>'
    label = esc(" / ".join(TYPING_LINES))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}">'
            f'<style>{"".join(css)}</style>{prompt}{"".join(parts)}</svg>')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for mode in ("dark", "light"):
        for kind in ("header", "footer"):
            (OUT / f"{kind}-{mode}.svg").write_text(banner(kind, mode), encoding="utf-8")
        (OUT / f"typing-{mode}.svg").write_text(typing(mode), encoding="utf-8")
    print("banners written ->", OUT)


if __name__ == "__main__":
    main()
