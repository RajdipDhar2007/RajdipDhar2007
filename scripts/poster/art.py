"""Animated header and footer banners (aurora, perspective grid, particles, hand-drawn signature)."""
from __future__ import annotations
from .common import PAL, MODES, OUT, doc, kf, lin_grad, pct, rng, typo, write, esc

W = 1000
ROLES = ["Full-stack developer", "Android developer", "Game developer from scratch", "Web3 explorer", "AI & automation tinkerer"]
TOKENS = ["{ }", "</>", "0x", "=>", "[ ]", "01", "#", "::", "fn()", "&&", "//", "++"]


def _aurora(c, h, t):
    """Three blurred colour blobs drifting slowly. Returns (defs, body, css)."""
    defs = '<filter id="bl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>'
    blobs = [("a1", 230, 110, 300, 120, c["accent"], 17, 60, 30), ("a2", 780, 90, 280, 110, c["second"], 21, -70, 25),
             ("a3", 520, h * .62, 220, 80, c["pink"], 25, 50, -25)]
    body, css = "", ""
    for name, cx, cy, rx, ry, col, dur, dx, dy in blobs:
        body += f'<ellipse class="{name}" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{col}" opacity="{c["glow"]}" filter="url(#bl)"/>'
        css += (f"@keyframes {name}{{0%,100%{{transform:translate(0,0) scale(1)}}50%{{transform:translate({dx}px,{dy}px) scale(1.18)}}}}"
                f".{name}{{animation:{name} {dur}s ease-in-out infinite}}")
    return defs, body, css


def _particles(c, r, n, h, y0=0):
    body, css = "", "@keyframes rise{0%{transform:translateY(0);opacity:0}15%{opacity:.9}100%{transform:translateY(-120px);opacity:0}}.pt{animation:rise var(--d) linear infinite}"
    for i in range(n):
        x, y = r.uniform(10, 990), r.uniform(y0 + 40, h - 20)
        rad = r.choice([1, 1.2, 1.6, 2.2])
        col = r.choice([c["accent"], c["second"], c["ink"], c["pink"]])
        body += f'<circle class="pt" cx="{x:.0f}" cy="{y:.0f}" r="{rad}" fill="{col}" style="--d:{r.uniform(5, 11):.1f}s;animation-delay:-{r.uniform(0, 11):.1f}s"/>'
    return body, css


def _tokens(c, r, h, count=11):
    f = typo.font(typo.MONO_B)
    body, css = "", "@keyframes fl{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-14px) rotate(4deg)}}.tk{animation:fl var(--d) ease-in-out infinite}"
    for i in range(count):
        tok = TOKENS[i % len(TOKENS)]
        x, y = r.choice([r.uniform(20, 300), r.uniform(700, 960)]), r.uniform(40, h - 90)
        d, _ = f.path(tok, r.choice([18, 22, 26]), x, y)
        col = r.choice([c["accent"], c["second"], c["muted"]])
        body += f'<path class="tk" d="{d}" fill="{col}" opacity=".30" style="--d:{r.uniform(5, 9):.1f}s;animation-delay:-{r.uniform(0, 8):.1f}s"/>'
    return body, css


def _waves(page, base, top: bool, h, span=(0, 1)):
    from svgkit import wave_path
    out, css = "", "@keyframes wv{from{transform:translateX(0)}to{transform:translateX(-1000px)}}.wv{animation:wv var(--d) linear infinite}"
    layers = [(h - 36 if not top else 40, 14, 1000, 0, 18, .35), (h - 26 if not top else 28, 11, 500, 1.2, 12, .6), (h - 14 if not top else 16, 8, 250, 2.4, 9, 1)]
    for b, a, p, ph, dur, op in layers:
        d = wave_path(2000, b, a, p, ph, close_to=(0 if top else h) if False else (0 if top else h))
        out += f'<path class="wv" d="{d}" fill="{page}" opacity="{op}" style="--d:{dur}s"/>'
    return out, css


def header(mode: str) -> str:
    c = PAL[mode]
    H, T = 380, 14.0
    r = rng(11)
    adefs, abody, acss = _aurora(c, H, T)
    pbody, pcss = _particles(c, r, 42, H)
    tbody, tcss = _tokens(c, r, H)
    wbody, wcss = _waves(c["page"], c["base"], False, 60 if False else 380)

    # perspective grid (vanishing point at 500, horizon y=292)
    hz = 306
    vlines = "".join(f'<line x1="{500 + i * 26}" y1="{hz}" x2="{500 + i * 150}" y2="{H}" stroke="{c["accent"]}" stroke-opacity=".28"/>' for i in range(-14, 15))
    hlines = "".join(f'<line class="fy" x1="0" x2="1000" y1="{hz}" y2="{hz}" stroke="{c["accent"]}" stroke-width="1.4" style="animation-delay:-{k * .6:.1f}s"/>' for k in range(6))
    gcss = ("@keyframes fy{0%{transform:translateY(0);opacity:0}20%{opacity:.55}100%{transform:translateY(90px);opacity:.9}}"
            ".fy{animation:fy 3.6s cubic-bezier(.55,0,.95,.6) infinite}")

    # hand-drawn signature
    sf = typo.font(typo.SCRIPT)
    size = 136
    name = "Rajdip Dhar"
    nw = sf.width(name, size)
    x0, base_y = (1000 - nw) / 2, 212
    gl = sf.glyphs(name, size, x0, base_y)
    full_d = " ".join(g[0] for g in gl)
    css_name, draw, fill = "", "", ""
    for i, (d, _, _) in enumerate(gl):
        t0 = 0.35 + i * 0.16
        css_name += kf(f"d{i}", T, [(0, "stroke-dashoffset:1;opacity:1"), (t0, "stroke-dashoffset:1;opacity:1"), (t0 + 0.9, "stroke-dashoffset:0;opacity:1"),
                                    (T - 0.7, "stroke-dashoffset:0;opacity:1"), (T - 0.4, "stroke-dashoffset:0;opacity:0"), (T, "stroke-dashoffset:1;opacity:0")])
        css_name += f".d{i}{{animation:d{i} {T}s ease-in-out infinite}}"
        draw += f'<path class="d{i}" d="{d}" pathLength="1" fill="none" stroke="url(#gn)" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="1" stroke-dashoffset="1"/>'
        fill += f'<path d="{d}"/>'
    css_name += kf("nf", T, [(0, "opacity:0"), (1.7, "opacity:0"), (2.7, "opacity:1"), (T - 0.7, "opacity:1"), (T - 0.4, "opacity:0"), (T, "opacity:0")]) + f".nf{{animation:nf {T}s ease-in-out infinite}}"
    css_name += "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}.bob{animation:bob 6s ease-in-out infinite}"
    css_name += kf("shm", T, [(0, "transform:translateX(0)"), (4.0, "transform:translateX(0)"), (5.4, "transform:translateX(1240px)"), (9.0, "transform:translateX(0)"), (10.4, "transform:translateX(1240px)"), (T, "transform:translateX(1240px)")]) + f".shm{{animation:shm {T}s linear infinite}}"
    # brush underline
    ul = f"M{x0 + 40:.0f} {base_y + 26} C {x0 + 200:.0f} {base_y + 38}, {x0 + nw - 220:.0f} {base_y + 14}, {x0 + nw - 30:.0f} {base_y + 28}"
    css_name += kf("ul", T, [(0, "stroke-dashoffset:1"), (2.4, "stroke-dashoffset:1"), (3.4, "stroke-dashoffset:0"), (T - 0.7, "stroke-dashoffset:0;opacity:1"), (T - 0.4, "opacity:0"), (T, "stroke-dashoffset:1;opacity:0")]) + f".ul{{animation:ul {T}s ease-in-out infinite}}"

    # rotating roles
    rf = typo.font(typo.HEAD)
    seg = 3.0
    rtotal = seg * len(ROLES)
    roles, rcss = "", ""
    for i, role in enumerate(ROLES):
        d, w = rf.path(role, 27, 500 - rf.width(role, 27) / 2, 288)
        a = i * seg
        rcss += kf(f"r{i}", rtotal, [(0, "opacity:0;transform:translateY(14px)")] +
                   ([(a - 0.01, "opacity:0;transform:translateY(14px)")] if a > 0.02 else []) +
                   [(a + .45, "opacity:1;transform:translateY(0)"), (a + seg - .55, "opacity:1;transform:translateY(0)"),
                    (a + seg - .1, "opacity:0;transform:translateY(-12px)"), (rtotal, "opacity:0;transform:translateY(-12px)")])
        rcss += f".r{i}{{animation:r{i} {rtotal}s cubic-bezier(.2,.7,.2,1) infinite}}"
        roles += f'<path class="r{i}" d="{d}" fill="url(#gr)"/>'
    rcss += ".r0{opacity:1}"
    # kicker + status chips
    mf = typo.font(typo.MONO_B)
    kd, kw = mf.path("B.TECH CSE  /  HERITAGE INSTITUTE OF TECHNOLOGY", 13, 0, 0, 2)
    kicker = f'<path class="kick" d="{kd}" transform="translate({500 - kw / 2:.0f} 74)" fill="{c["muted"]}"/>'
    kcss = kf("kick", T, [(0, "opacity:0"), (0.2, "opacity:0"), (1.2, "opacity:1"), (T - .7, "opacity:1"), (T - .4, "opacity:0"), (T, "opacity:0")]) + f".kick{{animation:kick {T}s linear infinite}}"
    hello_d, hw = mf.path("> hello, world", 13, 28, 36)
    hello = (f'<path d="{hello_d}" fill="{c["accent"]}"/><rect class="cur" x="{28 + hw + 5}" y="25" width="8" height="14" fill="{c["accent"]}"/>'
             "<style>@keyframes cu{0%,49%{opacity:1}50%,100%{opacity:0}}.cur{animation:cu 1s steps(1) infinite}</style>")
    st_d, sw = mf.path("BUILDING IN PUBLIC", 13, 0, 0, 2)
    status = (f'<g transform="translate({1000 - 28 - sw - 20:.0f} 36)"><circle class="pulse" cx="0" cy="-5" r="4" fill="{c["green"]}"/>'
              f'<path d="{st_d}" transform="translate(14 0)" fill="{c["muted"]}"/></g>'
              "<style>@keyframes pl{0%,100%{opacity:1;r:4}50%{opacity:.35;r:6}}.pulse{animation:pl 1.8s ease-in-out infinite}</style>")

    defs = (adefs + lin_grad("gn", [(0, c["accent"]), (.55, c["second"]), (1, c["pink"])], 0, 0, 1, 0, 'gradientUnits="userSpaceOnUse" x1="%d" x2="%d"' % (x0, x0 + nw)).replace('x1="0" y1="0" x2="1" y2="0" ', "")
            + lin_grad("gr", [(0, c["accent"]), (1, c["second"])]) + lin_grad("shg", [(0, "#fff"), (.5, "#fff"), (1, "#fff")]).replace('<stop offset="0" stop-color="#fff"/>', '<stop offset="0" stop-color="#fff" stop-opacity="0"/>').replace('<stop offset="1" stop-color="#fff"/>', '<stop offset="1" stop-color="#fff" stop-opacity="0"/>')
            + f'<clipPath id="nm"><path d="{full_d}"/></clipPath>')
    bg = (f'<defs><linearGradient id="bgg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["base"]}"/><stop offset="1" stop-color="{c["base2"]}"/></linearGradient></defs>'
          f'<rect width="1000" height="{H}" fill="url(#bgg)"/>')
    body = (bg + abody + f'<g clip-path="inset(0)">{vlines}{hlines}</g>'.replace('<g clip-path="inset(0)">', f'<g>') + pbody + tbody + hello + status + kicker
            + f'<g class="bob"><g class="nf"><path d="{full_d}" fill="url(#gn)"/></g>{draw}'
              f'<g clip-path="url(#nm)"><rect class="shm" x="-260" y="60" width="200" height="190" fill="url(#shg)" opacity=".75" transform="skewX(-18)"/></g>'
              f'<path class="ul" d="{ul}" fill="none" stroke="url(#gn)" stroke-width="4" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="0"/></g>'
            + roles + wbody)
    css = acss + pcss + tcss + gcss + wcss + css_name + rcss + kcss
    return doc(W, H, body, css, defs, "Rajdip Dhar: hand-drawn signature, rotating roles, animated aurora banner")


def footer(mode: str) -> str:
    c = PAL[mode]
    H, T = 300, 12.0
    r = rng(5)
    adefs, abody, acss = _aurora(c, H, T)
    pbody, pcss = _particles(c, r, 36, H, 20)
    from svgkit import wave_path
    wv, wcss = "", "@keyframes wv{from{transform:translateX(0)}to{transform:translateX(-1000px)}}.wv{animation:wv var(--d) linear infinite}"
    for b, a, p, ph, dur, op in [(44, 14, 1000, 0, 18, .35), (32, 11, 500, 1.2, 12, .6), (22, 8, 250, 2.4, 9, 1)]:
        wv += f'<path class="wv" d="{wave_path(2000, b, a, p, ph, close_to=0)}" fill="{c["page"]}" opacity="{op}" style="--d:{dur}s"/>'
    # shooting stars
    stars = "".join(f'<g class="ss" style="animation-delay:-{k * 2.7:.1f}s"><line x1="0" y1="0" x2="-70" y2="-24" stroke="url(#st)" stroke-width="2" stroke-linecap="round"/></g>'.replace('<g class="ss"', f'<g class="ss" transform="translate({150 + k * 260} {40 + (k % 2) * 40})"') for k in range(4))
    scss = "@keyframes ssh{0%{transform:translate(0,0);opacity:0}8%{opacity:1}35%,100%{transform:translate(220px,76px);opacity:0}}.ss line{animation:ssh 5.4s ease-in infinite;animation-delay:inherit}"
    stars = "".join(f'<g transform="translate({120 + k * 250} {58 + (k % 2) * 46})"><line class="sl" x1="0" y1="0" x2="-80" y2="-27" stroke="url(#st)" stroke-width="2.2" stroke-linecap="round" style="animation-delay:-{k * 1.6:.1f}s"/></g>' for k in range(4))
    scss = "@keyframes ssh{0%{transform:translate(0,0);opacity:0}6%{opacity:1}30%,100%{transform:translate(230px,78px);opacity:0}}.sl{animation:ssh 6.4s ease-in infinite}"
    sf = typo.font(typo.SCRIPT)
    msg = "Thanks for stopping by"
    size = 62
    mw = sf.width(msg, size)
    x0 = (1000 - mw) / 2
    gl = sf.glyphs(msg, size, x0, 150)
    letters, lcss = "", ""
    for i, (d, _, _) in enumerate(gl):
        t0 = 0.2 + i * 0.07
        lcss += kf(f"f{i}", T, [(0, "opacity:0;transform:translateY(18px)"), (t0, "opacity:0;transform:translateY(18px)"), (t0 + .55, "opacity:1;transform:translateY(0)"),
                                (T - .8, "opacity:1;transform:translateY(0)"), (T - .3, "opacity:0;transform:translateY(-8px)"), (T, "opacity:0")]) + f".f{i}{{animation:f{i} {T}s cubic-bezier(.2,.8,.2,1) infinite}}"
        letters += f'<path class="f{i}" d="{d}" fill="url(#gf)"/>'
    mf = typo.font(typo.MONO_B)
    sub = "LET'S BUILD SOMETHING TOGETHER"
    sd, sw = mf.path(sub, 14, 0, 0, 3)
    lcss += kf("sb", T, [(0, "opacity:0"), (1.6, "opacity:0"), (2.4, "opacity:1"), (T - .8, "opacity:1"), (T - .3, "opacity:0"), (T, "opacity:0")]) + f".sb{{animation:sb {T}s linear infinite}}"
    sub_el = f'<path class="sb" d="{sd}" transform="translate({500 - sw / 2:.0f} 196)" fill="{c["muted"]}"/>'
    hd, hwid = mf.path("MADE WITH PYTHON, SVG & CURIOSITY", 11, 0, 0, 2)
    made = f'<path d="{hd}" transform="translate({500 - hwid / 2:.0f} 262)" fill="{c["muted"]}" opacity=".8"/>'
    heart = (f'<path class="hb" d="M500 232 c-6-8 -18-3 -12 7 l12 12 l12-12 c6-10 -6-15 -12-7z" fill="{c["pink"]}" transform="translate(0 -4)"/>'
             "<style>@keyframes hb{0%,100%{transform:scale(1)}15%{transform:scale(1.25)}30%{transform:scale(1)}45%{transform:scale(1.18)}}.hb{transform-box:fill-box;transform-origin:center;animation:hb 1.6s ease-in-out infinite}</style>")
    defs = adefs + lin_grad("gf", [(0, c["accent"]), (.5, c["second"]), (1, c["pink"])], 0, 0, 1, 0) + lin_grad("st", [(0, "#fff"), (1, "#fff")], 0, 0, 1, 0).replace('stop-color="#fff"/><stop offset="1" stop-color="#fff"', f'stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["accent"]}" stop-opacity="0"')
    bg = (f'<linearGradient id="bgf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["base2"]}"/><stop offset="1" stop-color="{c["base"]}"/></linearGradient>'
          f'<rect width="1000" height="{H}" fill="url(#bgf)"/>')
    body = bg + abody + pbody + stars + letters + sub_el + heart.replace('translate(0 -4)', 'translate(0 8)') + made + wv
    return doc(1000, H, body, acss + pcss + scss + lcss + wcss, defs, "Thanks for stopping by: animated footer")


def build():
    for m in MODES:
        write(OUT / "banners" / f"header-{m}.svg", header(m))
        write(OUT / "banners" / f"footer-{m}.svg", footer(m))
