"""Stage 4 + orchestrator: ASCII frames -> animated terminal-portrait SVG (dark/light) + GIF.

    python scripts/ascii/build_svg.py            # whole pipeline, one command
    python scripts/ascii/build_svg.py --skip-pipeline   # only re-render the SVG/GIF from _work/ascii
    python scripts/ascii/build_svg.py --no-gif --no-preview

Timeline (12 s loop):
  0.0-0.8 boot | 0.8-2.6 scan reveal (scramble -> real) | 2.6-3.0 glitch lock-in
  3.0-5.4 wave (3 cycles, frame swap on the arm region only) | 5.4-12 idle | 11.6-12 glitch-out
All animation is CSS keyframes inside the SVG (no JS) and is disabled under prefers-reduced-motion,
which freezes the final composed frame.
"""
from __future__ import annotations
import argparse
import json
import math
import random
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from theme import THEMES, MONO, NAME, PROMPT  # noqa: E402
from svgkit import window_keyframes, pct, esc, EPS  # noqa: E402

WORK = HERE / "_work"
ASCII = WORK / "ascii"
OUT = ROOT / "assets" / "ascii"
PREVIEW = ROOT / "preview"

T = 12.0                  # loop length (s)
HIDE_AT = 11.85           # stage disappears just before the loop restarts
CW, LH, FS = 6.0, 10.0, 10
PX, Y0 = 20, 84           # portrait origin
SCRAMBLE = "#$%01{}<>"
RAMP = " .`:-=+*cs#%@"
FRAME_DT = 0.1            # 10 fps wave


class Css:
    """Collects @keyframes + classes; identical window lists share one class."""

    def __init__(self):
        self.rules: list[str] = []
        self.cache: dict = {}
        self.n = 0

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


def txt(x, y, s, cls="", extra="", length=None):
    tl = f' textLength="{length:.1f}" lengthAdjust="spacing"' if length else ""
    c = f' class="{cls}"' if cls else ""
    return f'<text{c} x="{x:.1f}" y="{y:.1f}"{tl}{extra}>{esc(s)}</text>'


def build(mode: str) -> str:
    c = THEMES[mode]
    card = c["bg"] if mode == "dark" else c["panel"]
    meta = json.loads((ASCII / "meta.json").read_text())
    cols, rows = meta["cols"], meta["rows"]
    c0, r0, _c1, r1 = meta["region"]
    nfr = meta["frames"]
    base = read_grid(ASCII / f"base-{mode}.txt")
    frames = [read_grid(ASCII / mode / f"frame_{i:02d}.txt") for i in range(nfr)]
    masks = [read_grid(ASCII / f"mask_{i:02d}.txt") for i in range(nfr)]
    rnd = random.Random(2007)
    css = Css()
    W = int(cols * CW + 2 * PX)
    portrait_h = rows * LH
    H = int(Y0 + portrait_h + 64)
    glyphs = sum(1 for r in base for ch in r if ch != " ")

    def row_y(i):
        return Y0 + (i + 1) * LH - 2

    def t_row(i):
        return 0.8 + 1.8 * i / rows

    # ------------------------------------------------------------- portrait rows
    rows_svg: list[str] = []
    for i in range(rows):
        t0 = t_row(i)
        y = row_y(i)
        # three pre-rendered scrambled versions, then the real row
        for k in range(3):
            s = "".join(rnd.choice(SCRAMBLE) if ch != " " else " " for ch in base[i])
            cls = "sc " + css.window([(t0 + .06 * k, t0 + .06 * (k + 1))])
            rows_svg.append(txt(PX, y, s, cls, length=cols * CW))
        real_cls = "rw " + css.window([(t0 + .18, HIDE_AT)])
        in_region = r0 <= i < r1
        left = base[i][:c0] if in_region else base[i]
        if left.strip():
            rows_svg.append(txt(PX, y, left, real_cls, length=len(left) * CW))
        if in_region and base[i][c0:].strip():  # arm region resting state (hand lowered)
            rest = css.window([(t0 + .18, 3.0), (5.4, HIDE_AT)])
            rows_svg.append(txt(PX + c0 * CW, y, base[i][c0:], f"rest {rest}", length=(cols - c0) * CW))

    # ------------------------------------------------------------- wave frames
    wave_start, wave_end = 3.0, 5.4
    cycle_t = nfr * FRAME_DT
    cycles = math.ceil((wave_end - wave_start) / cycle_t)
    frame_svg: list[str] = []
    for k in range(nfr):
        wins = []
        for cy in range(cycles):
            a = wave_start + cy * cycle_t + k * FRAME_DT
            if a < wave_end:
                wins.append((a, min(a + FRAME_DT, wave_end)))
        parts = []
        for i in range(r0, r1):
            row, mk = frames[k][i][c0:], masks[k][i][c0:]
            under = "".join(ch if m != "1" else " " for ch, m in zip(row, mk))
            hand = "".join(ch if m == "1" else " " for ch, m in zip(row, mk))
            if under.strip():
                parts.append(txt(PX + c0 * CW, row_y(i), under, length=(cols - c0) * CW))
            if hand.strip():
                parts.append(txt(PX + c0 * CW, row_y(i), hand, "hand", length=(cols - c0) * CW))
        frame_svg.append(f'<g class="fr fr{k} {css.window(wins)}">{"".join(parts)}</g>')

    # ------------------------------------------------------------- bubble
    bub_x = PX + (c0 + 3) * CW
    bubble = []
    for j, (line, a, b) in enumerate([("hi \U0001F44B", 3.0, 3.35), ("welcome to", 3.4, 3.85), ("my space", 3.9, 4.3)]):
        n = len(line)
        bubble.append(txt(bub_x, Y0 + (3 + 2 * j) * LH, line, f"bub {css.typed(a, b, n)}", ' font-size="11"'))

    # ------------------------------------------------------------- boot + status
    boot = []
    cmd = "./render --portrait"
    pr_cls = css.typed(0.0, 0.45, len(PROMPT) + 1 + len(cmd))
    boot.append(f'<text class="{pr_cls} boot" x="{PX}" y="52" font-size="13"><tspan class="acc">{PROMPT}</tspan> {esc(cmd)}</text>')
    css.raw(f"@keyframes bar{{0%{{clip-path:inset(0 100% 0 0)}}{pct(0.4, T)}{{clip-path:inset(0 100% 0 0);animation-timing-function:steps(10,end)}}"
            f"{pct(0.75, T)}{{clip-path:inset(0 0 0 0)}}100%{{clip-path:inset(0 0 0 0)}}}}")
    css.raw(f".bar{{animation:bar {T:g}s linear infinite}}")
    boot.append(f'<rect x="{PX}" y="61" width="104" height="11" rx="2" fill="none" class="line"/>'
                f'<g class="bar"><rect x="{PX + 2}" y="63" width="100" height="7" rx="1" class="accf"/></g>')
    boot.append(txt(PX + 116, 71, f"100% · decoding {glyphs} glyphs", f"muted {css.window([(0.75, HIDE_AT)])}", ' font-size="12"'))
    status_y = Y0 + portrait_h + 22
    status_txt = f"✓ identity verified: {NAME}"
    status = txt(PX, status_y, status_txt, f"acc {css.typed(3.0, 3.5, len(status_txt))}", ' font-size="13"')
    cursor_x = PX + (len(PROMPT) + 1) * 7.8
    prompt2 = (f'<g class="{css.window([(3.5, HIDE_AT)])} pr2"><text x="{PX}" y="{status_y + 22}" font-size="13" class="muted">{PROMPT}</text>'
               f'<rect class="cursor accf" x="{cursor_x:.1f}" y="{status_y + 11}" width="8" height="14"/></g>')

    # ------------------------------------------------------------- scan lines
    def scan(cls):
        return (f'<g class="{cls}"><rect x="{PX - 8}" y="{Y0 - 18}" width="{cols * CW + 16}" height="18" fill="url(#glow)"/>'
                f'<rect x="{PX - 8}" y="{Y0 - 1}" width="{cols * CW + 16}" height="2" class="accf"/></g>')

    ph = portrait_h
    css.raw(f"@keyframes sc1{{0%{{opacity:0;transform:translateY(0)}}{pct(0.8 - EPS, T)}{{opacity:0;transform:translateY(0)}}"
            f"{pct(0.8, T)}{{opacity:1;transform:translateY(0)}}{pct(2.6, T)}{{opacity:1;transform:translateY({ph:.0f}px)}}"
            f"{pct(2.6 + EPS, T)}{{opacity:0}}100%{{opacity:0}}}}.scan{{animation:sc1 {T:g}s linear infinite;opacity:0}}")
    idle = "".join(f"{pct(a - EPS, T)}{{opacity:0;transform:translateY(0)}}{pct(a, T)}{{opacity:.28;transform:translateY(0)}}"
                   f"{pct(a + 0.9, T)}{{opacity:.28;transform:translateY({ph:.0f}px)}}{pct(a + 0.9 + EPS, T)}{{opacity:0}}" for a in (6.0, 10.0))
    css.raw(f"@keyframes sc2{{0%{{opacity:0}}{idle}100%{{opacity:0}}}}.scan2{{animation:sc2 {T:g}s linear infinite;opacity:0}}")

    # ------------------------------------------------------------- glitch copies
    gl_a = css.window([(2.60, 2.68), (2.76, 2.84), (11.60, 11.68), (11.76, 11.84)])
    gl_b = css.window([(2.62, 2.70), (2.78, 2.86), (11.62, 11.70), (11.78, 11.86)])
    glitch = (f'<use href="#fig" class="gl {gl_a}" transform="translate(-3.5 0)" fill="{c["accent"]}"/>'
              f'<use href="#fig" class="gl {gl_b}" transform="translate(3.5 1)" fill="{c["second"]}"/>')

    # ------------------------------------------------------------- shimmer
    cand = [(r, cc) for r in range(2, rows - 2) for cc in range(cols)
            if base[r][cc] not in " " and not (r0 <= r < r1 and cc >= c0)]
    rnd.shuffle(cand)
    shim = []
    for k, (r, cc) in enumerate(cand[:40]):
        ch = base[r][cc]
        idx = RAMP.find(ch)
        alt = RAMP[min(max(idx + rnd.choice([-2, -1, 1, 2]), 1), len(RAMP) - 1)] if idx > 0 else rnd.choice(".:+*")
        if alt == ch:
            alt = "*" if ch != "*" else "+"
        dur = rnd.choice([2, 3, 4, 6])
        delay = -rnd.uniform(0, dur)
        css.raw(f".s{k}{{animation:sh {dur}s linear infinite {delay:.2f}s}}")
        x = PX + cc * CW
        shim.append(f'<g class="s{k}"><rect x="{x:.1f}" y="{Y0 + r * LH:.1f}" width="{CW}" height="{LH}" fill="{card}"/>'
                    f'<text x="{x:.1f}" y="{row_y(r):.1f}" class="acc">{esc(alt)}</text></g>')
    css.raw("@keyframes sh{0%{opacity:0}49.9%{opacity:0}50%{opacity:1}99.9%{opacity:1}100%{opacity:0}}")
    shim_cls = css.window([(5.4, HIDE_AT)])

    # ------------------------------------------------------------- misc css
    css.raw(f"@keyframes blink{{0%,49.9%{{opacity:1}}50%,100%{{opacity:0}}}}.cursor{{animation:blink 1s steps(1) infinite}}")
    stage = css.window([(0, HIDE_AT)])
    reduced = ("@media (prefers-reduced-motion: reduce){*{animation:none!important}"
               ".sc,.scan,.scan2,.gl,.shw{display:none}.rest{opacity:0}.fr{opacity:0}.fr0{opacity:1}.rw,.boot,.bub{opacity:1}}")
    style = (f"text{{font-family:{MONO};font-size:{FS}px;white-space:pre}}"
             f".rw,.rest{{fill:{c['text']}}}.sc{{fill:{c['text']};opacity:0}}.fr{{opacity:0;fill:{c['text']}}}.hand{{fill:{c['accent']}}}"
             f".acc,.bub{{fill:{c['accent']}}}.accf{{fill:{c['accent']}}}.muted{{fill:{c['muted']}}}.line{{stroke:{c['line']};stroke-width:1}}"
             f".gl,.scan,.scan2{{opacity:0}}.boot{{fill:{c['text']}}}"
             + "".join(css.rules) + reduced)

    title = (f'<circle cx="18" cy="16" r="5" fill="{c["second"]}"/><circle cx="36" cy="16" r="5" fill="{c["accent"]}"/>'
             f'<circle cx="54" cy="16" r="5" fill="{c["green"]}"/>'
             f'<text x="{W / 2}" y="20" text-anchor="middle" class="muted" font-size="12">{PROMPT.split("$")[0]} ~/portrait</text>'
             f'<line x1="0" x2="{W}" y1="32" y2="32" class="line"/>')
    desc = f"Animated ASCII portrait of {NAME}: it renders, scans, glitches into focus, waves hello and idles."
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(desc)}">'
            f'<title>{esc(desc)}</title>'
            f'<defs><linearGradient id="glow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["accent"]}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{c["accent"]}" stop-opacity=".38"/></linearGradient></defs>'
            f'<style>{style}</style>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{card}" stroke="{c["line"]}"/>{title}'
            f'<g class="{stage}">'
            f'{"".join(boot)}'
            f'<g fill="{c["text"]}"><g id="fig">{"".join(rows_svg)}</g></g>'
            f'{"".join(frame_svg)}{"".join(bubble)}{glitch}{status}{prompt2}'
            f'<g class="shw {shim_cls}">{"".join(shim)}</g>'
            f'{scan("scan")}{scan("scan2")}'
            f'</g></svg>')


# ------------------------------------------------------------------ gif + previews
def make_gif(svg: Path, gif: Path, mode: str, fps=10, width=420):
    from PIL import Image
    from snap import snapshots
    tmp = WORK / "gif"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    n = int(T * fps)
    times = [i / fps for i in range(n)]
    files = [tmp / f"{i:03d}.png" for i in range(n)]
    snapshots(svg, times, files, scheme=mode, scale=width / 616)
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
        times = [0.5, 2.0, 4.0, 8.0]
        snapshots(svg, times, [PREVIEW / f"portrait-{mode}-{t:g}s.png" for t in times], scheme=mode)
        snapshots(svg, [8.0], [PREVIEW / f"portrait-{mode}-reduced.png"], scheme=mode, reduced_motion=True)
    print("previews ->", PREVIEW)


def run_pipeline():
    sh = shutil.which("bash")
    if sh and (ROOT / "input" / "wave.mp4").exists():
        subprocess.run([sh, str(HERE / "extract_frames.sh")], check=True)
    else:
        shutil.rmtree(WORK / "frames", ignore_errors=True)
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
