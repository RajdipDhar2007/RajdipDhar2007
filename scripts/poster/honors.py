"""Achievements (GitHub profile badges) and Highlights (live milestone tiles) as animated SVGs.

Achievements are static (build.py).  Highlights need live data, see scripts/highlights.py.
"""
from __future__ import annotations
import math
from .common import PAL, MODES, OUT, doc, kf, typo, write
from .hero import star4, _tw, _grad

# Badges shown on github.com/RajdipDhar2007 (name, blurb, tint key)
ACHIEVEMENTS = [
    ("Pull Shark", "Opened pull requests that got merged", "accent", "merge"),
    ("Quickdraw", "Closed an issue or PR within 5 minutes", "pink", "bolt"),
    ("YOLO", "Merged a pull request without a review", "green", "rocket"),
    ("Pair Extraordinaire", "Co-authored commits on a merged PR", "second", "pair"),
    ("Galaxy Brain", "Had answers accepted in Discussions", "accent", "galaxy"),
]


def _glyph(kind: str, cx: float, cy: float, col) -> str:
    if kind == "merge":
        return (f'<g class="gl" fill="none" stroke="{col}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">'
                f'<circle cx="{cx - 9}" cy="{cy - 11}" r="3.6"/><circle cx="{cx - 9}" cy="{cy + 11}" r="3.6"/><circle cx="{cx + 10}" cy="{cy + 2}" r="3.6"/>'
                f'<path d="M{cx - 9} {cy - 7} V{cy + 7} M{cx - 9} {cy - 3} Q{cx - 9} {cy + 2} {cx + 6} {cy + 2}"/></g>')
    if kind == "bolt":
        return f'<g class="gl"><path d="M{cx + 3} {cy - 15} L{cx - 9} {cy + 3} H{cx - 1} L{cx - 4} {cy + 15} L{cx + 9} {cy - 4} H{cx + 1}Z" fill="{col}"/></g>'
    if kind == "rocket":
        return (f'<g class="gl"><path d="M{cx} {cy - 16} Q{cx + 10} {cy - 6} {cx + 6} {cy + 8} H{cx - 6} Q{cx - 10} {cy - 6} {cx} {cy - 16}Z" fill="{col}"/>'
                f'<circle cx="{cx}" cy="{cy - 5}" r="3" fill="#0B1220" opacity=".55"/>'
                f'<path class="fl" d="M{cx - 4} {cy + 10} Q{cx} {cy + 22} {cx + 4} {cy + 10}Z" fill="#F59E0B"/></g>')
    if kind == "pair":
        return (f'<g class="gl"><circle cx="{cx - 6}" cy="{cy}" r="10" fill="{col}" opacity=".85"/><circle cx="{cx + 6}" cy="{cy}" r="10" fill="none" stroke="{col}" stroke-width="3.2"/></g>')
    return f'<g class="gl spin">{star4(cx, cy, 15, col)}{star4(cx, cy, 8, "#fff", extra='opacity=".8"')}</g>'


def achievements(mode: str) -> str:
    c = PAL[mode]
    W, H, T = 830, 262, 10.0
    n, gap = len(ACHIEVEMENTS), 14
    cw = (W - gap * (n - 1)) / n
    nf, bf, mf = typo.font(typo.HEAD), typo.font(typo.BODY), typo.font(typo.MONO_B)
    css = ("@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}.bb{animation:bob 5s ease-in-out infinite}"
           "@keyframes run{to{stroke-dashoffset:-400}}.run{stroke-dasharray:80 320;animation:run 6s linear infinite}"
           "@keyframes ring{to{transform:rotate(360deg)}}.rg{transform-box:fill-box;transform-origin:center;animation:ring 14s linear infinite}"
           "@keyframes ringr{to{transform:rotate(-360deg)}}.rgr{transform-box:fill-box;transform-origin:center;animation:ringr 9s linear infinite}"
           "@keyframes gl{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}.gl{transform-box:fill-box;transform-origin:center;animation:gl 2.4s ease-in-out infinite}"
           "@keyframes spin{to{transform:rotate(360deg)}}.spin{animation:spin 7s linear infinite}"
           "@keyframes fl{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.5)}}.fl{transform-box:fill-box;transform-origin:top;animation:fl .4s ease-in-out infinite}"
           "@keyframes shn{0%{transform:translateX(0)}45%,100%{transform:translateX(220px)}}.shn{animation:shn 6s ease-in-out infinite}"
           "@keyframes halo{0%,100%{opacity:.25;transform:scale(.9)}50%{opacity:.7;transform:scale(1.15)}}.halo{transform-box:fill-box;transform-origin:center;animation:halo 3.4s ease-in-out infinite}"
           "@keyframes pop{0%,8%{transform:scale(.4);opacity:0}16%{transform:scale(1.18);opacity:1}22%,92%{transform:scale(1);opacity:1}100%{transform:scale(.4);opacity:0}}"
           ".pop{transform-box:fill-box;transform-origin:center;animation:pop 10s cubic-bezier(.2,.9,.25,1.1) infinite both}" + _tw())
    body = ""
    for i, (name, blurb, tint, kind) in enumerate(ACHIEVEMENTS):
        x = i * (cw + gap)
        col = c[tint]
        mx, my = x + cw / 2, 82
        sz = min(16.0, 16.0 * (cw - 28) / nf.width(name, 16))
        nd, _ = nf.path(name, sz, mx - nf.width(name, sz) / 2, 168)
        ed, _ = mf.path("UNLOCKED", 10.5, mx - mf.width("UNLOCKED", 10.5, 2) / 2, 204, 2)
        lines = bf.wrap(blurb, 11.5, cw - 26)
        dd = "".join(f'<path d="{bf.path(l, 11.5, mx - bf.width(l, 11.5) / 2, 188 + k * 15)[0]}" fill="{c["muted"]}"/>' for k, l in enumerate(lines))
        ed, _ = mf.path("UNLOCKED", 10.5, mx - mf.width("UNLOCKED", 10.5, 2) / 2, 236, 2)
        hexp = " ".join(f"{mx + 38 * math.cos(math.pi / 6 + k * math.pi / 3):.1f},{my + 38 * math.sin(math.pi / 6 + k * math.pi / 3):.1f}" for k in range(6))
        sparks = "".join(star4(mx + dx, my + dy, r, col, "tw", f'style="animation-delay:-{k * .7:.1f}s"')
                         for k, (dx, dy, r) in enumerate([(-46, -30, 4), (48, -22, 5), (44, 36, 3.5), (-42, 38, 4.5)]))
        body += (f'<g class="bb" style="animation-delay:-{i * .9:.1f}s">'
                 f'<rect x="{x + .5:.1f}" y="14.5" width="{cw - 1:.1f}" height="233" rx="22" fill="{c["card"]}" stroke="{c["line"]}"/>'
                 f'<clipPath id="ak{i}"><rect x="{x:.1f}" y="14" width="{cw:.1f}" height="234" rx="22"/></clipPath>'
                 f'<g clip-path="url(#ak{i})"><rect class="shn" x="{x - 70:.1f}" y="14" width="36" height="234" fill="{col}" opacity=".10" transform="skewX(-20)" style="animation-delay:-{i * 1.3:.1f}s"/></g>'
                 f'<rect class="run" x="{x + .5:.1f}" y="14.5" width="{cw - 1:.1f}" height="233" rx="22" fill="none" stroke="{col}" stroke-width="2.2" pathLength="400" style="animation-delay:-{i * 1.5}s"/>'
                 f'<g class="pop" style="animation-delay:{i * .35:.2f}s">'
                 f'<circle class="halo" cx="{mx:.1f}" cy="{my}" r="50" fill="{col}" opacity=".25"/>'
                 f'<circle class="rg" cx="{mx:.1f}" cy="{my}" r="47" fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="6 9" opacity=".8"/>'
                 f'<circle class="rgr" cx="{mx:.1f}" cy="{my}" r="43" fill="none" stroke="{col}" stroke-width="1.4" stroke-dasharray="2 12" opacity=".6"/>'
                 f'<polygon points="{hexp}" fill="{c["base2"]}" stroke="{col}" stroke-width="2.6" stroke-linejoin="round"/>'
                 f'{_glyph(kind, mx, my, col)}{sparks}</g>'
                 f'<path d="{nd}" fill="{c["ink"]}"/>{dd}<path d="{ed}" fill="{col}"/></g>')
    return doc(W, H, body, css, _grad(c, "g1"), "Achievements: " + ", ".join(a[0] for a in ACHIEVEMENTS), pad_y=8)


def _spark_bars(vals, x, y, w, h, col, c) -> str:
    """Last-N-days bars that grow from the baseline, one after another."""
    n = len(vals)
    vmax = max(vals) or 1
    bw = w / n
    out = ""
    for k, v in enumerate(vals):
        bh = max(3.0, h * v / vmax) if v else 3.0
        out += (f'<rect class="bar" x="{x + k * bw + 1:.1f}" y="{y + h - bh:.1f}" width="{bw - 2:.1f}" height="{bh:.1f}" rx="2" '
                f'fill="{col if v else c["line"]}" opacity="{.95 if v else .6}" style="animation-delay:{.6 + k * .045:.2f}s"/>')
    return out


def highlights(mode: str, d: dict) -> str:
    """d: total, longest, current, active_days, busiest (count), busiest_date, last30 (list[int]), per_active (float)."""
    from cards import _roll  # live module owns the odometer helper
    c = PAL[mode]
    W, H, T = 830, 400, 10.0
    big, lab, mono, bf = typo.font(typo.DISPLAY), typo.font(typo.MEDIUM), typo.font(typo.MONO_B), typo.font(typo.BODY)
    css = ("@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}.bb{animation:bob 5s ease-in-out infinite}"
           "@keyframes run{to{stroke-dashoffset:-400}}.run{stroke-dasharray:80 320;animation:run 6s linear infinite}"
           "@keyframes shn{0%{transform:translateX(0)}45%,100%{transform:translateX(300px)}}.shn{animation:shn 7s ease-in-out infinite}"
           "@keyframes bar{0%{transform:scaleY(0)}10%,88%{transform:scaleY(1)}100%{transform:scaleY(0)}}.bar{transform-box:fill-box;transform-origin:bottom;animation:bar 10s cubic-bezier(.3,.8,.2,1) infinite both}"
           "@keyframes pu{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.4)}}.pu{transform-box:fill-box;transform-origin:center;animation:pu 1.6s ease-in-out infinite}"
           "@keyframes flm{0%,100%{transform:scale(1,1) rotate(-2deg)}50%{transform:scale(.93,1.1) rotate(2deg)}}.flm{transform-box:fill-box;transform-origin:bottom;animation:flm 1.1s ease-in-out infinite}"
           "@keyframes ping{0%{r:3;opacity:.9}100%{r:13;opacity:0}}.ping{animation:ping 1.8s ease-out infinite}" + _tw())
    tiles = [
        (f"{d['total']:,}".replace(",", ""), "contributions, all time", c["accent"], "pulse"),
        (str(d["longest"]), "day longest streak", c["pink"], "flame"),
        (str(d["current"]), "day current streak", c["green"], "dot"),
        (str(d["active_days"]), "days I shipped something", c["second"], "star"),
        (str(d["busiest"]), "contributions on my best day", c["accent"], "bolt"),
        (f"{d['per_active']:.0f}", "average on an active day", c["pink"], "pulse"),
    ]
    body = ""
    cw, ch, gx, gy = 266, 116, 16, 16
    for i, (num, label, col, ic) in enumerate(tiles):
        x, y = (i % 3) * (cw + gx), 8 + (i // 3) * (ch + gy)
        digits, dcss = _roll(num, x + 24, y + 72, 40, big, f"h{i}", .25 + i * .15)
        css += dcss
        if ic == "flame":
            g = f'<g class="flm"><path d="M{x + 234} {y + 62} Q{x + 218} {y + 46} {x + 228} {y + 26} Q{x + 232} {y + 36} {x + 238} {y + 32} Q{x + 252} {y + 46} {x + 244} {y + 58} Q{x + 241} {y + 64} {x + 234} {y + 62}Z" fill="{col}"/></g>'
        elif ic == "dot":
            g = f'<circle cx="{x + 234}" cy="{y + 42}" r="6" fill="{col}" class="pu"/><circle class="ping" cx="{x + 234}" cy="{y + 42}" r="3" fill="none" stroke="{col}" stroke-width="2"/>'
        elif ic == "star":
            g = star4(x + 234, y + 42, 15, col, "tw")
        elif ic == "bolt":
            g = f'<path class="pu" d="M{x + 238} {y + 24} L{x + 226} {y + 44} H{x + 234} L{x + 230} {y + 60} L{x + 244} {y + 38} H{x + 236}Z" fill="{col}"/>'
        else:
            g = f'<path d="M{x + 214} {y + 44} h8 l5 -14 l8 28 l6 -14 h8" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="pu"/>'
        body += (f'<g class="bb" style="animation-delay:-{i * .8:.1f}s"><clipPath id="hc{i}"><rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="24"/></clipPath>'
                 f'<rect x="{x + .5}" y="{y + .5}" width="{cw - 1}" height="{ch - 1}" rx="24" fill="{c["card"]}" stroke="{c["line"]}"/>'
                 f'<g clip-path="url(#hc{i})"><rect class="shn" x="{x - 90}" y="{y}" width="50" height="{ch}" fill="{col}" opacity=".07" transform="skewX(-20)" style="animation-delay:-{i * 1.2:.1f}s"/></g>'
                 f'<rect class="run" x="{x + .5}" y="{y + .5}" width="{cw - 1}" height="{ch - 1}" rx="24" fill="none" stroke="{col}" stroke-width="2.2" pathLength="400" style="animation-delay:-{i * 1.4:.1f}s"/>'
                 f'{g}{digits}<path d="{lab.path(label, 13, x + 24, y + 98)[0]}" fill="{c["muted"]}"/></g>')
    # last 30 days strip
    sy = 8 + 2 * (ch + gy)
    body += (f'<g class="bb" style="animation-delay:-5s"><rect x=".5" y="{sy + .5}" width="829" height="{H - sy - 8}" rx="24" fill="{c["card"]}" stroke="{c["line"]}"/>'
             f'<path d="{mono.path("LAST 30 DAYS", 11.5, 28, sy + 30, 2)[0]}" fill="{c["accent"]}"/>'
             f'<path d="{bf.path("Busiest day: " + d["busiest_date"], 12.5, 640 - bf.width("Busiest day: " + d["busiest_date"], 12.5) + 160, sy + 30)[0]}" fill="{c["muted"]}"/>'
             f'{_spark_bars(d["last30"], 28, sy + 44, 774, 52, c["accent"], c)}</g>')
    return doc(W, H, body, css, _grad(c, "g1"), f"Highlights: {d['total']} contributions, {d['longest']} day longest streak, {d['active_days']} active days", pad_y=6)


def build_achievements():
    for m in MODES:
        write(OUT / "sections" / f"achievements-{m}.svg", achievements(m))


def build_highlights(d: dict):
    for m in MODES:
        write(OUT / "stats" / f"highlights-{m}.svg", highlights(m, d))
