"""Animated header and footer banners (aurora, perspective grid, particles, hand-drawn signature)."""
from __future__ import annotations
from .common import PAL, MODES, OUT, doc, kf, lin_grad, pct, rng, typo, write, esc

W = 1000
A = chr(39)
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

    # slow rotating light rays behind the signature
    rays = "".join(f'<path d="M500 190 L{500 + 700 * __import__("math").cos(a):.0f} {190 + 700 * __import__("math").sin(a):.0f} L{500 + 700 * __import__("math").cos(a + .12):.0f} {190 + 700 * __import__("math").sin(a + .12):.0f}Z" fill="url(#ry)"/>' for a in [k * 0.7854 for k in range(8)])
    rays = f'<g class="rays" style="transform-origin:500px 190px">{rays}</g>'
    rcss0 = "@keyframes rays{to{transform:rotate(360deg)}}.rays{animation:rays 90s linear infinite;opacity:.55}"
    # drifting synthwave skyline sitting on the horizon (two copies = seamless loop)
    sr = rng(23)
    bx, blds, wins = 0, "", ""
    while bx < 1000:
        bw, bh = sr.randint(16, 40), sr.randint(6, 15)
        blds += f'<rect x="{bx}" y="{hz - bh}" width="{bw}" height="{bh}" fill="{c["base"] if mode == "dark" else c["base2"]}" stroke="{c["accent"]}" stroke-opacity=".35"/>'
        for _ in range(sr.randint(0, 3)):
            wx, wy = bx + sr.randint(3, max(4, bw - 6)), hz - sr.randint(5, max(6, bh - 3))
            wins += f'<rect class="wn" x="{wx}" y="{wy}" width="3" height="3" fill="{sr.choice([c["accent"], c["pink"], c["second"]])}" style="animation-delay:-{sr.uniform(0, 4):.1f}s"/>'
        bx += bw + sr.randint(0, 6)
    city = f'<g class="cty">{blds}{wins}<g transform="translate(1000 0)">{blds}{wins}</g></g>'
    ccss = ("@keyframes cty{from{transform:translateX(0)}to{transform:translateX(-1000px)}}.cty{animation:cty 70s linear infinite}"
            "@keyframes wn{0%,100%{opacity:.2}50%{opacity:1}}.wn{animation:wn 3s ease-in-out infinite}")

    # three glowing dots circling the signature on an elliptical orbit
    orb_path = "M60 190 a440 78 0 1 0 880 0 a440 78 0 1 0 -880 0"
    orbit = (f'<path d="{orb_path}" fill="none" stroke="{c["accent"]}" stroke-opacity=".22" stroke-dasharray="2 7"/>'
             + "".join(f'<circle class="odot" r="{r}" fill="{col}" style="offset-path:path({A}{orb_path}{A});animation-delay:-{k * 6:.1f}s"/>' for k, (r, col) in enumerate([(4, c["accent"]), (3, c["pink"]), (3.5, c["second"])])))
    ocss = "@keyframes odot{from{offset-distance:0%}to{offset-distance:100%}}.odot{animation:odot 18s linear infinite;filter:drop-shadow(0 0 4px currentColor)}"

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

    adefs += f'<radialGradient id="ry" cx="500" cy="190" r="700" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{c["accent"]}" stop-opacity=".30"/><stop offset="1" stop-color="{c["accent"]}" stop-opacity="0"/></radialGradient>'
    defs = (adefs + lin_grad("gn", [(0, c["accent"]), (.55, c["second"]), (1, c["pink"])], 0, 0, 1, 0, 'gradientUnits="userSpaceOnUse" x1="%d" x2="%d"' % (x0, x0 + nw)).replace('x1="0" y1="0" x2="1" y2="0" ', "")
            + lin_grad("gr", [(0, c["accent"]), (1, c["second"])]) + lin_grad("shg", [(0, "#fff"), (.5, "#fff"), (1, "#fff")]).replace('<stop offset="0" stop-color="#fff"/>', '<stop offset="0" stop-color="#fff" stop-opacity="0"/>').replace('<stop offset="1" stop-color="#fff"/>', '<stop offset="1" stop-color="#fff" stop-opacity="0"/>')
            + f'<clipPath id="nm"><path d="{full_d}"/></clipPath>')
    bg = (f'<defs><linearGradient id="bgg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["base"]}"/><stop offset="1" stop-color="{c["base2"]}"/></linearGradient></defs>'
          f'<rect width="1000" height="{H}" fill="url(#bgg)"/>')
    body = (bg + abody + f'<g clip-path="inset(0)">{vlines}{hlines}</g>'.replace('<g clip-path="inset(0)">', f'<g>') + rays + city + orbit + pbody + tbody + hello + status + kicker
            + f'<g class="bob"><g class="nf"><path d="{full_d}" fill="url(#gn)"/></g>{draw}'
              f'<g clip-path="url(#nm)"><rect class="shm" x="-260" y="60" width="200" height="190" fill="url(#shg)" opacity=".75" transform="skewX(-18)"/></g>'
              f'<path class="ul" d="{ul}" fill="none" stroke="url(#gn)" stroke-width="4" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="0"/></g>'
            + roles + wbody)
    shoot = "".join(f'<g transform="translate({90 + k * 330} {30 + (k % 2) * 36})"><line class="sl" x1="0" y1="0" x2="-80" y2="-27" stroke="url(#st)" stroke-width="2.2" stroke-linecap="round" style="animation-delay:-{k * 2.1:.1f}s"/></g>' for k in range(3))
    body = body.replace(wbody, shoot + wbody)
    defs += f'<linearGradient id="st" x1="0" x2="1"><stop offset="0" stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["accent"]}" stop-opacity="0"/></linearGradient>'
    css = acss + pcss + tcss + gcss + wcss + css_name + rcss + kcss + ccss + ocss + rcss0 + "@keyframes ssh{0%{transform:translate(0,0);opacity:0}6%{opacity:1}30%,100%{transform:translate(230px,78px);opacity:0}}.sl{animation:ssh 7.2s ease-in infinite}"
    return doc(W, H, body, css, defs, "Rajdip Dhar: hand-drawn signature, rotating roles, animated aurora banner")


def footer(mode: str) -> str:
    """Night-sky finale: parallax skyline with blinking windows, a ringed planet with a satellite, a rocket that keeps launching,
    drifting hearts, a wavy glowing 'Thanks' line, cycling messages and an equalizer along the bottom edge."""
    import math
    c = PAL[mode]
    W_, H = 1000, 330
    r = rng(5)
    adefs, abody, acss = _aurora(c, H, 12.0)
    pbody, pcss = _particles(c, r, 26, H, 20)
    sf, mf = typo.font(typo.SCRIPT), typo.font(typo.MONO_B)
    sky = c["ink"]
    css = ("@keyframes twk{0%,100%{opacity:.15}50%{opacity:1}}.twk{animation:twk var(--d) ease-in-out infinite}"
           "@keyframes ssh{0%{transform:translate(0,0);opacity:0}6%{opacity:1}30%,100%{transform:translate(230px,78px);opacity:0}}.sl{animation:ssh 6.4s ease-in infinite}"
           "@keyframes mv{from{transform:translateX(0)}to{transform:translateX(-1000px)}}.far{animation:mv 90s linear infinite}.near{animation:mv 48s linear infinite}"
           "@keyframes win{0%,100%{opacity:.15}50%{opacity:1}}.win{animation:win var(--d) steps(1) infinite}"
           "@keyframes orbr{to{transform:rotate(360deg)}}.ringp{transform-box:fill-box;transform-origin:center}"
           "@keyframes sat{from{offset-distance:0%}to{offset-distance:100%}}.sat{animation:sat 7s linear infinite}"
           "@keyframes fly{from{offset-distance:0%}to{offset-distance:100%}}.rk{animation:fly 9s cubic-bezier(.45,0,.55,1) infinite}"
           "@keyframes hrt{0%{transform:translate(0,0) scale(.6);opacity:0}12%{opacity:.9}50%{transform:translate(14px,-90px) scale(1)}100%{transform:translate(-10px,-190px) scale(.8);opacity:0}}.hrt{animation:hrt var(--d) ease-in-out infinite}"
           "@keyframes wave{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}.lt{animation:wave 2.6s ease-in-out infinite}"
           "@keyframes gl{0%,100%{opacity:.35}50%{opacity:.8}}.gl{animation:gl 3s ease-in-out infinite}"
           "@keyframes shm{0%,30%{transform:translateX(-160px)}80%,100%{transform:translateX(1120px)}}.shm{animation:shm 5s ease-in-out infinite}"
           "@keyframes msg{0%{opacity:0;transform:translateY(10px)}4%,22%{opacity:1;transform:translateY(0)}26%,100%{opacity:0;transform:translateY(-10px)}}.msg{opacity:0;animation:msg 16s ease-in-out infinite both}"
           "@keyframes eq{0%,100%{transform:scaleY(.25)}50%{transform:scaleY(1)}}.eq{transform-box:fill-box;transform-origin:50% 100%;animation:eq var(--d) ease-in-out infinite}"
           "@keyframes hb{0%,100%{transform:scale(1)}15%{transform:scale(1.3)}30%{transform:scale(1)}45%{transform:scale(1.2)}}.hb{transform-box:fill-box;transform-origin:center;animation:hb 1.4s ease-in-out infinite}"
           "@keyframes pls{0%{r:6;opacity:.8}100%{r:26;opacity:0}}.pls{animation:pls 2.4s ease-out infinite}"
           "@keyframes pulse{0%,100%{opacity:.5}50%{opacity:1}}.pulse{animation:pulse 1.2s ease-in-out infinite}")
    # ---- stars
    stars = "".join(f'<circle class="twk" cx="{r.randint(8, 992)}" cy="{r.randint(6, 210)}" r="{r.choice([.8, 1.1, 1.5, 2])}" fill="{sky}" style="--d:{r.uniform(2, 5):.1f}s;animation-delay:-{r.uniform(0, 5):.1f}s"/>' for _ in range(70))
    shoot = "".join(f'<g transform="translate({90 + k * 280} {30 + (k % 2) * 50})"><line class="sl" x1="0" y1="0" x2="-80" y2="-27" stroke="url(#st)" stroke-width="2.2" stroke-linecap="round" style="animation-delay:-{k * 2.1:.1f}s"/></g>' for k in range(4))
    # ---- ringed planet + satellite
    px, py, pr = 870, 96, 30
    orbit = f"M{px - 74} {py + 6} a74 22 -18 1 0 148 -12 a74 22 -18 1 0 -148 12"
    planet = (f'<circle cx="{px}" cy="{py}" r="{pr + 14}" fill="{c["second"]}" opacity=".18" class="gl"/>'
              f'<circle cx="{px}" cy="{py}" r="{pr}" fill="url(#pln)"/><circle cx="{px - 10}" cy="{py - 8}" r="5" fill="#fff" opacity=".14"/><circle cx="{px + 9}" cy="{py + 10}" r="7" fill="#000" opacity=".12"/>'
              f'<ellipse cx="{px}" cy="{py}" rx="58" ry="14" fill="none" stroke="{c["accent"]}" stroke-width="3" opacity=".75" transform="rotate(-18 {px} {py})"/>'
              f'<path d="M{px - 58} {py} A58 14 0 0 0 {px + 58} {py}" fill="none" stroke="{c["pink"]}" stroke-width="3" opacity=".9" transform="rotate(-18 {px} {py})"/>'
              f'<g class="sat" style="offset-path:path({A}{orbit}{A})"><rect x="-4" y="-2.5" width="8" height="5" rx="1" fill="{c["ink"]}"/><rect x="-10" y="-1" width="5" height="2" fill="{c["accent"]}"/><rect x="5" y="-1" width="5" height="2" fill="{c["accent"]}"/></g>')
    # ---- parallax skyline
    def skyline(seed, hmax, col, op, windows, cls):
        fr = rng(seed)
        x, shapes, wins = 0, "", ""
        while x < 1000:
            w, h = fr.randint(22, 52), fr.randint(int(hmax * .35), hmax)
            shapes += f'<rect x="{x}" y="{298 - h}" width="{w}" height="{h}" fill="{col}"/>'
            if fr.random() < .3:
                shapes += f'<rect x="{x + w / 2 - 1}" y="{298 - h - 12}" width="2" height="12" fill="{col}"/>'
            if windows:
                for wy in range(298 - h + 7, 292, 9):
                    for wx in range(x + 5, x + w - 6, 8):
                        if fr.random() < .3:
                            wins += f'<rect class="win" x="{wx}" y="{wy}" width="3.4" height="4.4" fill="{fr.choice([c["accent"], c["pink"], "#FBBF24"])}" style="--d:{fr.uniform(1.5, 6):.1f}s;animation-delay:-{fr.uniform(0, 6):.1f}s"/>'
            x += w + fr.randint(2, 8)
        grp = f'<g opacity="{op}">{shapes}</g>{wins}'
        return f'<g class="{cls}">{grp}<g transform="translate(1000 0)">{grp}</g></g>'
    city = skyline(31, 62, c["second"], .28, False, "far") + skyline(32, 50, c["page"] if mode == "dark" else c["ink"], .92 if mode == "dark" else .22, True, "near")
    # ---- rocket on a looping flight path, with a trail behind it
    flight = "M-40 310 C 220 90, 560 250, 1060 30"
    trail = "".join(f'<circle class="rk" r="{5 - k * .6:.1f}" fill="{[c["accent"], c["pink"], "#FBBF24"][k % 3]}" opacity="{.7 - k * .09:.2f}" style="offset-path:path({A}{flight}{A});animation-delay:{k * .07:.2f}s"/>' for k in range(1, 8))
    rocket = (f'<g class="rk" style="offset-path:path({A}{flight}{A});offset-rotate:auto"><g transform="translate(-4 0)"><path d="M16 0 C6 -9 -8 -9 -14 -6 L-14 6 C-8 9 6 9 16 0Z" fill="{c["ink"]}"/>'
              f'<circle cx="3" cy="0" r="3.6" fill="{c["accent"]}"/><path d="M-6 -7 L-14 -13 L-14 -5Z M-6 7 L-14 13 L-14 5Z" fill="{c["pink"]}"/><path d="M-14 -3 Q-30 0 -14 3Z" fill="#FBBF24"/></g></g>')
    # ---- hearts
    hearts = "".join(f'<g transform="translate({60 + k * 78 + (k % 3) * 11} 268)"><path class="hrt" d="M0 0 c-5 -7 -16 -2 -10 6 l10 10 l10 -10 c6 -8 -5 -13 -10 -6z" fill="{[c["pink"], c["accent"], c["second"]][k % 3]}" style="--d:{5 + (k * 7) % 5}s;animation-delay:-{k * 1.3:.1f}s"/></g>' for k in range(12))
    # ---- headline: wavy letters over a glowing copy, shimmer sweep
    msg, size = "Thanks for stopping by", 64
    x0 = (W_ - sf.width(msg, size)) / 2
    gl = sf.glyphs(msg, size, x0, 140)
    full = "".join(g[0] for g in gl)
    letters = "".join(f'<path class="lt" d="{d}" fill="url(#gf)" style="animation-delay:-{i * .13:.2f}s"/>' for i, (d, _, _) in enumerate(gl))
    head = (f'<g class="gl" filter="url(#glow)"><path d="{full}" fill="url(#gf)"/></g>{letters}'
            f'<clipPath id="hc"><path d="{full}"/></clipPath><g clip-path="url(#hc)"><rect class="shm" x="0" y="70" width="60" height="90" fill="#fff" opacity=".65" transform="skewX(-22)"/></g>')
    # ---- cycling subtitles
    subs = ["LET'S BUILD SOMETHING TOGETHER", "OPEN TO INTERNSHIPS & COLLABS", "SEE YOU ON GITHUB", "KEEP SHIPPING, KEEP LEARNING"]
    sub_el = ""
    for k, t in enumerate(subs):
        d, w = mf.path(t, 14, 0, 0, 3)
        sub_el += f'<g class="msg" style="animation-delay:{k * 4}s"><path d="{d}" transform="translate({500 - w / 2:.0f} 190)" fill="{c["ink"]}"/></g>'
    hd, hwid = mf.path("MADE WITH PYTHON, SVG & CURIOSITY", 11, 0, 0, 2)
    made = (f'<path d="{hd}" transform="translate({500 - hwid / 2 + 14:.0f} 222)" fill="{c["muted"]}" opacity=".9"/>'
            f'<circle class="pls" cx="{500 - hwid / 2 - 6:.0f}" cy="218" r="6" fill="none" stroke="{c["pink"]}" stroke-width="2"/>'
            f'<path class="hb" d="M{500 - hwid / 2 - 6:.0f} 222 c-3 -4 -9 -1 -6 4 l6 6 l6 -6 c3 -5 -3 -8 -6 -4z" fill="{c["pink"]}"/>')
    # ---- equalizer along the bottom edge
    eq = "".join(f'<rect class="eq" x="{k * 20 + 3}" y="{H - 30}" width="12" height="30" rx="4" fill="url(#gf)" opacity=".7" style="--d:{.7 + (math.sin(k * 1.7) + 1) * .5:.2f}s;animation-delay:-{(k * .37) % 2:.2f}s"/>' for k in range(50))
    defs = (adefs + lin_grad("gf", [(0, c["accent"]), (.5, c["second"]), (1, c["pink"])], 0, 0, 1, 0)
            + '<linearGradient id="st" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>'
            + f'<radialGradient id="pln" cx=".35" cy=".3" r=".85"><stop offset="0" stop-color="{c["pink"]}"/><stop offset=".6" stop-color="{c["second"]}"/><stop offset="1" stop-color="{c["base"] if mode == "dark" else c["second"]}"/></radialGradient>'
            + '<filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>'
            + f'<linearGradient id="bgf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["base2"]}"/><stop offset="1" stop-color="{c["base"]}"/></linearGradient>')
    body = (f'<rect width="{W_}" height="{H}" fill="url(#bgf)"/>{abody}{stars}{pbody}{shoot}{planet}{city}{hearts}{trail}{rocket}{head}{sub_el}{made}{eq}')
    return doc(W_, H, body, acss + pcss + css, defs, "Thanks for stopping by: animated night-sky footer")


def build():
    for m in MODES:
        write(OUT / "banners" / f"header-{m}.svg", header(m))
        write(OUT / "banners" / f"footer-{m}.svg", footer(m))
