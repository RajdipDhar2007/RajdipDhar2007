"""Stage 4 + orchestrator: ASCII grid -> animated terminal-portrait SVG (dark/light) + GIF fallback.

    python scripts/ascii/build_svg.py                    # whole pipeline, one command
    python scripts/ascii/build_svg.py --skip-pipeline    # only re-render SVG/GIF from _work/ascii
    python scripts/ascii/build_svg.py --no-gif --no-preview

Timeline (12 s loop):
  0.0-0.8 boot | 0.8-2.6 scan reveal (scramble -> real rows) | 2.6-3.0 glitch lock-in
  3.0-11.6 idle: light sweeps across the glyphs, glitch bands, hex rain, shimmering characters,
           blinking cursor, faint scans | 11.6-12 glitch-out, loop
All animation is CSS keyframes inside the SVG (no JS); prefers-reduced-motion freezes the final frame.
"""
from __future__ import annotations
import argparse
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from theme import THEMES, MONO, NAME  # noqa: E402
from svgkit import window_keyframes, pct, esc, EPS  # noqa: E402
import typo  # noqa: E402

WORK = HERE / "_work"
ASCII = WORK / "ascii"
OUT = ROOT / "assets" / "ascii"
PREVIEW = ROOT / "preview"

T = 12.0
HIDE_AT = 11.85
CW, LH, FS = 6.0, 10.0, 10
PX, Y0 = 20, 92
SCRAMBLE = "#$%01{}<>"
RAMP = " .`:-=+*cs#%@"
HEX = "0123456789ABCDEF"
PROMPT = "rajdip@hitk:~$"


class Css:
    def __init__(self):
        self.rules, self.cache, self.n = [], {}, 0

    def window(self, windows) -> str:
        key = tuple((round(a, 4), round(b, 4)) for a, b in windows)
        if key not in self.cache:
            name = f"w{self.n}"
            self.n += 1
            self.rules.append(window_keyframes(name, T, list(key)))
            self.rules.append(f".{name}{{animation:{name} {T:g}s linear infinite}}")
            self.cache[key] = name
        return self.cache[key]

    def raw(self, rule: str):
        self.rules.append(rule)

    def typed(self, a: float, b: float, n: int, end: float = HIDE_AT) -> str:
        key = ("typed", round(a, 4), round(b, 4), n, end)
        if key not in self.cache:
            name = f"t{self.n}"
            self.n += 1
            st = f"animation-timing-function:steps({n},end)"
            self.rules.append(
                f"@keyframes {name}{{0%{{opacity:0;clip-path:inset(0 100% 0 0)}}"
                f"{pct(max(a - EPS, 0), T)}{{opacity:0;clip-path:inset(0 100% 0 0)}}"
                f"{pct(a, T)}{{opacity:1;clip-path:inset(0 100% 0 0);{st}}}"
                f"{pct(b, T)}{{opacity:1;clip-path:inset(0 0 0 0)}}"
                f"{pct(end, T)}{{opacity:1;clip-path:inset(0 0 0 0)}}"
                f"{pct(end + EPS, T)}{{opacity:0}}100%{{opacity:0}}}}"
                f".{name}{{animation:{name} {T:g}s linear infinite}}")
            self.cache[key] = name
        return self.cache[key]


def read_grid(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").split("\n")


def txt(x, y, s, cls="", length=None):
    tl = f' textLength="{length:.1f}" lengthAdjust="spacing"' if length else ""
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}"{tl}>{esc(s)}</text>'


def ptxt(s: str, x: float, y: float, size: float, fill: str = "", tracking: float = 0, font=typo.MONO_B) -> str:
    d, _ = typo.font(font).path(s, size, x, y, tracking)
    f = f' fill="{fill}"' if fill else ""
    return f'<path d="{d}"{f}/>'


def build(mode: str) -> str:
    c = THEMES[mode]
    card = c["bg"] if mode == "dark" else c["panel"]
    meta = json.loads((ASCII / "meta.json").read_text())
    cols, rows = meta["cols"], meta["rows"]
    base = read_grid(ASCII / f"base-{mode}.txt")
    rnd = random.Random(2007)
    css = Css()
    W = int(cols * CW + 2 * PX)
    ph = rows * LH
    H = int(Y0 + ph + 66)
    glyphs = sum(1 for r in base for ch in r if ch != " ")

    def row_y(i):
        return Y0 + (i + 1) * LH - 2

    def t_row(i):
        return 0.8 + 1.8 * i / rows

    # ------------------------------------------------------------ portrait rows
    rows_svg, static_rows = [], []
    for i in range(rows):
        t0 = t_row(i)
        for k in range(3):                            # three scrambled versions, then the real row
            s = "".join(rnd.choice(SCRAMBLE) if ch != " " else " " for ch in base[i])
            rows_svg.append(txt(PX, row_y(i), s, "sc " + css.window([(t0 + .06 * k, t0 + .06 * (k + 1))]), cols * CW))
        if base[i].strip():
            rows_svg.append(txt(PX, row_y(i), base[i], "rw " + css.window([(t0 + .18, HIDE_AT)]), cols * CW))
            static_rows.append(txt(PX, row_y(i), base[i], "", cols * CW))

    # ------------------------------------------------------------ boot + status (outlined mono font)
    cmd = "./render --portrait"
    adv = typo.font(typo.MONO_B).advance("x", 14)              # monospace advance of the 14 px prompt font
    boot = (f'<g class="{css.typed(0.0, 0.45, len(PROMPT) + 1 + len(cmd))} boot">'
            f'{ptxt(PROMPT, PX, 66, 14, fill=c["accent"])}{ptxt(cmd, PX + adv * (len(PROMPT) + 1), 66, 14, fill=c["text"])}</g>')
    css.raw(f"@keyframes bar{{0%{{clip-path:inset(0 100% 0 0)}}{pct(0.4, T)}{{clip-path:inset(0 100% 0 0);animation-timing-function:steps(12,end)}}"
            f"{pct(0.78, T)}{{clip-path:inset(0 0 0 0)}}100%{{clip-path:inset(0 0 0 0)}}}}.bar{{animation:bar {T:g}s linear infinite}}")
    boot += (f'<rect x="{PX}" y="76" width="124" height="10" rx="5" fill="none" stroke="{c["line"]}"/>'
             f'<g class="bar"><rect x="{PX + 2}" y="78" width="120" height="6" rx="3" fill="url(#bg)"/></g>'
             f'<g class="{css.window([(0.78, HIDE_AT)])}">{ptxt(f"100%  decoding {glyphs} glyphs", PX + 136, 85, 11, fill=c["muted"])}</g>')
    status_y = Y0 + ph + 26
    status_txt = f"> identity verified: {NAME}"
    status = f'<g class="{css.typed(3.0, 3.6, len(status_txt))}">{ptxt(status_txt, PX, status_y, 14, fill=c["accent"])}</g>'
    cur_x = PX + adv * (len(PROMPT) + 1)
    prompt2 = (f'<g class="{css.window([(3.6, HIDE_AT)])}">{ptxt(PROMPT, PX, status_y + 26, 14, fill=c["muted"])}'
               f'<rect class="cursor" x="{cur_x:.1f}" y="{status_y + 14}" width="8" height="15" fill="{c["accent"]}"/></g>')

    # ------------------------------------------------------------ scan lines
    def scan(cls):
        return (f'<g class="{cls}"><rect x="{PX - 8}" y="{Y0 - 20}" width="{cols * CW + 16}" height="20" fill="url(#glow)"/>'
                f'<rect x="{PX - 8}" y="{Y0 - 1}" width="{cols * CW + 16}" height="2" fill="{c["accent"]}"/></g>')
    css.raw(f"@keyframes sc1{{0%{{opacity:0;transform:translateY(0)}}{pct(0.8 - EPS, T)}{{opacity:0;transform:translateY(0)}}{pct(0.8, T)}{{opacity:1;transform:translateY(0)}}"
            f"{pct(2.6, T)}{{opacity:1;transform:translateY({ph:.0f}px)}}{pct(2.6 + EPS, T)}{{opacity:0}}100%{{opacity:0}}}}.scan{{animation:sc1 {T:g}s linear infinite;opacity:0}}")
    idle = "".join(f"{pct(a - EPS, T)}{{opacity:0;transform:translateY(0)}}{pct(a, T)}{{opacity:.28;transform:translateY(0)}}"
                   f"{pct(a + 0.9, T)}{{opacity:.28;transform:translateY({ph:.0f}px)}}{pct(a + 0.9 + EPS, T)}{{opacity:0}}" for a in (6.0, 10.0))
    css.raw(f"@keyframes sc2{{0%{{opacity:0}}{idle}100%{{opacity:0}}}}.scan2{{animation:sc2 {T:g}s linear infinite;opacity:0}}")

    # ------------------------------------------------------------ glitch + light-sweep copies of the figure
    gl_a = css.window([(2.60, 2.68), (2.76, 2.84), (11.60, 11.68), (11.76, 11.84)])
    gl_b = css.window([(2.62, 2.70), (2.78, 2.86), (11.62, 11.70), (11.78, 11.86)])
    bands = ""
    fx = (f'<use href="#fs" class="fx {gl_a}" transform="translate(-3.5 0)" fill="{c["accent"]}"/>'
          f'<use href="#fs" class="fx {gl_b}" transform="translate(3.5 1)" fill="{c["second"]}"/>')
    for n, (a, b) in enumerate([(3.4, 4.8), (7.6, 9.0)]):        # accent light sweeping left to right across the glyphs
        css.raw(f"@keyframes sw{n}{{0%{{opacity:0;clip-path:inset(0 88% 0 0)}}{pct(a - EPS, T)}{{opacity:0;clip-path:inset(0 88% 0 0)}}"
                f"{pct(a, T)}{{opacity:1;clip-path:inset(0 88% 0 0)}}{pct(b, T)}{{opacity:1;clip-path:inset(0 0 0 88%)}}{pct(b + EPS, T)}{{opacity:0}}100%{{opacity:0}}}}"
                f".sw{n}{{animation:sw{n} {T:g}s ease-in-out infinite}}")
        fx += f'<use href="#fs" class="fx sw{n}" fill="{c["accent"]}" stroke="{c["accent"]}" stroke-width=".8"/>'
        css.raw(f"@keyframes gl{n}{{0%{{opacity:0;transform:translateX(0)}}{pct(a - EPS, T)}{{opacity:0;transform:translateX(0)}}{pct(a, T)}{{opacity:1;transform:translateX(0)}}"
                f"{pct(b, T)}{{opacity:1;transform:translateX({cols * CW + 90:.0f}px)}}{pct(b + EPS, T)}{{opacity:0}}100%{{opacity:0}}}}"
                f".gl{n}{{animation:gl{n} {T:g}s ease-in-out infinite;opacity:0}}")
        bands += f'<rect class="gl{n}" x="{PX - 80}" y="{Y0}" width="80" height="{ph}" fill="url(#sg)"/>'
    for n, (a, top, bot, col) in enumerate([(5.5, 34, 52, c["accent"]), (9.8, 58, 28, c["second"])]):
        css.raw(f"@keyframes gb{n}{{0%{{opacity:0}}{pct(a - EPS, T)}{{opacity:0;transform:translateX(0)}}{pct(a, T)}{{opacity:1;transform:translateX(-7px)}}"
                f"{pct(a + .06, T)}{{opacity:1;transform:translateX(6px)}}{pct(a + .12, T)}{{opacity:1;transform:translateX(-3px)}}{pct(a + .16, T)}{{opacity:0}}100%{{opacity:0}}}}"
                f".gb{n}{{animation:gb{n} {T:g}s linear infinite;clip-path:inset({top}% 0 {bot}% 0)}}")
        fx += f'<use href="#fs" class="fx gb{n}" fill="{col}"/>'

    # ------------------------------------------------------------ hex rain on the empty margins
    rain = ""
    for k, x in enumerate((PX + 4, PX + 14, PX + (cols - 3) * CW + 2, PX + (cols - 2) * CW + 12)):
        chars = [rnd.choice(HEX) for _ in range(52)]
        lines = "".join(f'<tspan x="{x:.1f}" y="{Y0 + 8 + j * 11}">{ch}</tspan>' for j, ch in enumerate(chars + chars))
        css.raw(f".rn{k}{{animation:rain {5 + k}s linear infinite}}")
        rain += f'<text class="rn{k}" font-size="9" fill="{c["accent"]}" opacity=".30">{lines}</text>'
    css.raw(f"@keyframes rain{{from{{transform:translateY(0)}}to{{transform:translateY(-{52 * 11}px)}}}}")
    rain = (f'<clipPath id="rc"><rect x="{PX}" y="{Y0}" width="{cols * CW}" height="{26 * LH}"/></clipPath>'
            f'<g clip-path="url(#rc)" class="{css.window([(3.0, HIDE_AT)])} rainw">{rain}</g>')

    # ------------------------------------------------------------ shimmering glyphs
    cand = [(r, cc) for r in range(2, rows - 2) for cc in range(cols) if base[r][cc] != " "]
    rnd.shuffle(cand)
    shim = []
    for k, (r, cc) in enumerate(cand[:48]):
        ch = base[r][cc]
        idx = RAMP.find(ch)
        alt = RAMP[min(max(idx + rnd.choice([-2, -1, 1, 2]), 1), len(RAMP) - 1)] if idx > 0 else rnd.choice(".:+*")
        alt = alt if alt != ch else ("*" if ch != "*" else "+")
        dur = rnd.choice([2, 3, 4, 6])
        css.raw(f".s{k}{{animation:sh {dur}s linear infinite {-rnd.uniform(0, dur):.2f}s}}")
        x = PX + cc * CW
        shim.append(f'<g class="s{k}"><rect x="{x:.1f}" y="{Y0 + r * LH:.1f}" width="{CW}" height="{LH}" fill="{card}"/>'
                    f'<text x="{x:.1f}" y="{row_y(r):.1f}" class="acc">{esc(alt)}</text></g>')
    css.raw("@keyframes sh{0%{opacity:0}49.9%{opacity:0}50%{opacity:1}99.9%{opacity:1}100%{opacity:0}}")
    shim_cls = css.window([(3.2, HIDE_AT)])

    # ------------------------------------------------------------ HUD: corner brackets, live indicator
    x0, x1, y0, y1, L = PX - 8, PX + cols * CW + 8, Y0 - 6, Y0 + ph + 6, 22
    brackets = (f'<path class="hud" d="M{x0} {y0 + L} V{y0} H{x0 + L} M{x1 - L} {y0} H{x1} V{y0 + L} M{x1} {y1 - L} V{y1} H{x1 - L} M{x0 + L} {y1} H{x0} V{y1 - L}" '
                f'fill="none" stroke="{c["accent"]}" stroke-width="2" stroke-linecap="round"/>')
    css.raw("@keyframes hud{0%,100%{opacity:.35}50%{opacity:1}}.hud{animation:hud 2.4s ease-in-out infinite}"
            "@keyframes lv{0%,100%{opacity:1}50%{opacity:.25}}.lv{animation:lv 1.4s ease-in-out infinite}"
            "@keyframes blink{0%,49.9%{opacity:1}50%,100%{opacity:0}}.cursor{animation:blink 1s steps(1) infinite}")
    live = f'<circle class="lv" cx="{W - 128}" cy="17" r="4" fill="{c["green"]}"/>' + ptxt("ASCII  LIVE", W - 116, 21, 10.5, fill=c["muted"], tracking=1.5)
    title = (f'<circle cx="18" cy="17" r="5" fill="{c["second"]}"/><circle cx="36" cy="17" r="5" fill="{c["accent"]}"/><circle cx="54" cy="17" r="5" fill="{c["green"]}"/>'
             f'{ptxt("rajdip@hitk ~/portrait", W / 2 - 80, 21, 11.5, fill=c["muted"])}{live}<line x1="0" x2="{W}" y1="34" y2="34" stroke="{c["line"]}"/>')
    stage = css.window([(0, HIDE_AT)])
    reduced = ("@media (prefers-reduced-motion: reduce){*{animation:none!important}"
               ".sc,.fx,.scan,.scan2,.rainw,.shw,.gl0,.gl1{display:none}.rw,.boot{opacity:1}}")
    style = (f"text{{font-family:{MONO};font-size:{FS}px;white-space:pre}}.sc{{opacity:0}}.acc{{fill:{c['accent']}}}"
             f".fx,.scan,.scan2{{opacity:0}}" + "".join(css.rules) + reduced)
    desc = f"Animated ASCII portrait of {NAME}: it renders, scans, glitches into focus, then idles with sweeping light."
    defs = (f'<linearGradient id="glow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["accent"]}" stop-opacity="0"/><stop offset="1" stop-color="{c["accent"]}" stop-opacity=".4"/></linearGradient>'
            f'<linearGradient id="sg" x1="0" x2="1"><stop offset="0" stop-color="{c["accent"]}" stop-opacity="0"/><stop offset=".7" stop-color="{c["accent"]}" stop-opacity=".34"/><stop offset="1" stop-color="{c["accent"]}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="bg" x1="0" x2="1"><stop offset="0" stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["second"]}"/></linearGradient>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(desc)}">'
            f'<title>{esc(desc)}</title><defs>{defs}<g id="fs">{"".join(static_rows)}</g></defs><style>{style}</style>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{card}" stroke="{c["line"]}"/>{title}'
            f'<g class="{stage}">{boot}{brackets}{rain}{bands}<g fill="{c["text"]}"><g id="fig">{"".join(rows_svg)}</g></g>{fx}{status}{prompt2}'
            f'<g class="shw {shim_cls}">{"".join(shim)}</g>{scan("scan")}{scan("scan2")}</g></svg>')


# ------------------------------------------------------------------ gif + previews
def make_gif(svg: Path, gif: Path, mode: str, fps=10, width=420):
    from PIL import Image
    from snap import snapshots
    tmp = WORK / "gif"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    n = int(T * fps)
    files = [tmp / f"{i:03d}.png" for i in range(n)]
    snapshots(svg, [i / fps for i in range(n)], files, scheme=mode, scale=width / 616)
    imgs = [Image.open(f).convert("RGB") for f in files]
    pal_src = Image.new("RGB", (imgs[0].width, imgs[0].height * 4))
    for k, i in enumerate((0, n // 6, n // 3, n // 2)):
        pal_src.paste(imgs[i], (0, k * imgs[0].height))
    pal = pal_src.quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    frames = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in imgs]
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0, optimize=True, disposal=1)
    gs = shutil.which("gifsicle")
    if gs:
        subprocess.run([gs, "-O3", "--lossy=20", "-b", str(gif)], check=False)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"gif: {gif.name} {gif.stat().st_size / 1024:.0f} KB" + ("" if gs else " (gifsicle not found, Pillow-optimised only)"))


def previews(svgs: dict[str, Path]):
    from snap import snapshots
    PREVIEW.mkdir(exist_ok=True)
    for mode, svg in svgs.items():
        times = [0.5, 2.0, 2.65, 4.2, 8.0]
        snapshots(svg, times, [PREVIEW / f"portrait-{mode}-{t:g}s.png" for t in times], scheme=mode)
        snapshots(svg, [8.0], [PREVIEW / f"portrait-{mode}-reduced.png"], scheme=mode, reduced_motion=True)
    print("previews ->", PREVIEW)


def run_pipeline():
    for step in ("prep.py", "frames_to_ascii.py"):
        subprocess.run([sys.executable, str(HERE / step)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-pipeline", action="store_true")
    ap.add_argument("--no-gif", action="store_true")
    ap.add_argument("--no-preview", action="store_true")
    a = ap.parse_args()
    if not a.skip_pipeline:
        run_pipeline()
    OUT.mkdir(parents=True, exist_ok=True)
    svgs = {}
    for mode in ("dark", "light"):
        p = OUT / f"portrait-{mode}.svg"
        p.write_text(build(mode), encoding="utf-8")
        kb = p.stat().st_size / 1024
        print(f"svg: {p.name} {kb:.0f} KB")
        if kb > 500:
            raise SystemExit(f"{p.name} is {kb:.0f} KB (> 500 KB budget): reduce scramble variants or grid size")
        svgs[mode] = p
    if not a.no_preview:
        previews(svgs)
    if not a.no_gif:
        make_gif(svgs["dark"], OUT / "portrait.gif", "dark")


if __name__ == "__main__":
    main()
