"""Hero column, section titles, ticker, about cards, contact pills, live greeting."""
from __future__ import annotations
A = chr(39)
from .common import PAL, MODES, OUT, doc, kf, lin_grad, typo, write, icon, esc

# ------------------------------------------------------------------ small pieces
def star4(cx, cy, r, fill, cls="", extra=""):
    k = r * 0.28
    d = f"M{cx} {cy - r} Q{cx + k} {cy - k} {cx + r} {cy} Q{cx + k} {cy + k} {cx} {cy + r} Q{cx - k} {cy + k} {cx - r} {cy} Q{cx - k} {cy - k} {cx} {cy - r}Z"
    return f'<path class="{cls}" d="{d}" fill="{fill}" {extra}/>'


def _tw(cls="tw"):
    return ("@keyframes tw{0%,100%{opacity:.25;transform:scale(.6) rotate(0)}50%{opacity:1;transform:scale(1.1) rotate(45deg)}}"
            f".{cls}{{transform-box:fill-box;transform-origin:center;animation:tw 2.4s ease-in-out infinite}}")


def _grad(c, gid="g1", x1=0, x2=1):
    return lin_grad(gid, [(0, c["accent"]), (.55, c["second"]), (1, c["pink"])], x1, 0, x2, 0)


# ------------------------------------------------------------------ section titles
def section_title(num: str, text: str, mode: str) -> str:
    """`num` is kept for call compatibility; titles no longer show numbers or a kicker."""
    c = PAL[mode]
    W, H, T = 830, 100, 9.0
    f = typo.font(typo.DISPLAY)
    size = 46
    tw = f.width(text, size, 1)
    x0 = (W - tw) / 2
    gl = f.glyphs(text, size, x0, 62, 1)
    css, letters = "", ""
    for i, (d, _, _) in enumerate(gl):
        t0 = 0.15 + i * 0.05
        css += kf(f"l{i}", T, [(0, "opacity:0;transform:translateY(26px)"), (t0, "opacity:0;transform:translateY(26px)"), (t0 + .5, "opacity:1;transform:translateY(0)"),
                               (T - .7, "opacity:1;transform:translateY(0)"), (T - .25, "opacity:0;transform:translateY(-10px)"), (T, "opacity:0")]) + f".l{i}{{animation:l{i} {T}s cubic-bezier(.2,.9,.25,1.1) infinite}}"
        letters += f'<g class="lw" style="animation-delay:-{i * .25:.2f}s"><path class="l{i}" d="{d}" fill="url(#g1)"/></g>'
    css += "@keyframes lw{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}.lw{animation:lw 2.8s ease-in-out infinite}"
    full = " ".join(g[0] for g in gl)
    css += kf("ln", T, [(0, "transform:scaleX(0)"), (.5, "transform:scaleX(0)"), (1.6, "transform:scaleX(1)"), (T - .7, "transform:scaleX(1)"), (T - .25, "transform:scaleX(1);opacity:0"), (T, "transform:scaleX(0);opacity:0")]) + f".ln{{transform-box:fill-box;transform-origin:center;animation:ln {T}s cubic-bezier(.3,.8,.2,1) infinite}}"
    css += f"@keyframes dot{{0%{{transform:translateX(0)}}100%{{transform:translateX({tw - 6:.0f}px)}}}}.dot{{animation:dot 3.2s ease-in-out infinite alternate}}"
    css += kf("shm", T, [(0, "transform:translateX(0)"), (2.2, "transform:translateX(0)"), (3.6, f"transform:translateX({tw + 240:.0f}px)"), (5.6, "transform:translateX(0)"), (7.0, f"transform:translateX({tw + 240:.0f}px)"), (T, f"transform:translateX({tw + 240:.0f}px)")]) + f".shm{{animation:shm {T}s linear infinite}}"
    css += kf("orb", T, [(0, "opacity:0"), (.2, "opacity:0"), (1.0, "opacity:1"), (T - .7, "opacity:1"), (T - .25, "opacity:0"), (T, "opacity:0")]) + f".orb{{animation:orb {T}s ease-out infinite}}"
    css += _tw() + "@keyframes bst{0%,15%{opacity:0;transform:translate(0,0)}18%{opacity:1}35%,100%{opacity:0;transform:translate(var(--dx),var(--dy))}}.bst{animation:bst 9s ease-out infinite}"
    import math as _m
    burst = "".join(f'<circle class="bst" cx="{x0 + tw / 2:.0f}" cy="81" r="2.6" fill="{[c["accent"], c["second"], c["pink"]][j % 3]}" style="--dx:{58 * _m.cos(j * _m.pi / 5.5 - _m.pi):.0f}px;--dy:{-42 * abs(_m.sin(j * _m.pi / 5.5)):.0f}px"/>' for j in range(12))
    defs = (_grad(c, "g1", 0, 1) + f'<clipPath id="tc"><path d="{full}"/></clipPath>'
            '<linearGradient id="sg"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    dly = lambda v: f'style="animation-delay:-{v}s"'  # noqa: E731
    gl_a = kf("ga", T, [(0, "opacity:0"), (3.9, "opacity:0"), (3.91, "opacity:.9"), (4.03, "opacity:.9"), (4.04, "opacity:0"), (6.5, "opacity:0"), (6.51, "opacity:.9"), (6.62, "opacity:.9"), (6.63, "opacity:0"), (T, "opacity:0")])
    gl_b = kf("gb", T, [(0, "opacity:0"), (3.93, "opacity:0"), (3.94, "opacity:.9"), (4.06, "opacity:.9"), (4.07, "opacity:0"), (6.53, "opacity:0"), (6.54, "opacity:.9"), (6.65, "opacity:.9"), (6.66, "opacity:0"), (T, "opacity:0")])
    css += gl_a + gl_b + f".ga{{animation:ga {T}s linear infinite;opacity:0}}.gb{{animation:gb {T}s linear infinite;opacity:0}}"
    glitch = (f'<path class="ga" d="{full}" fill="{c["accent"]}" transform="translate(-3 0)"/><path class="gb" d="{full}" fill="{c["pink"]}" transform="translate(3 1)"/>')
    body = (f'<g class="orb">{star4(x0 - 34, 46, 9, c["accent"], "tw")}{star4(x0 + tw + 34, 46, 9, c["second"], "tw", dly(1.2))}'
            f'{star4(x0 - 14, 20, 5, c["pink"], "tw", dly(.6))}{star4(x0 + tw + 14, 20, 5, c["accent"], "tw", dly(1.8))}</g>'
            f'{letters}{glitch}<g clip-path="url(#tc)"><rect class="shm" x="{x0 - 200:.0f}" y="10" width="110" height="70" fill="url(#sg)" opacity=".8" transform="skewX(-18)"/></g>'
            f'{burst}<g class="ln"><rect x="{x0:.0f}" y="80" width="{tw:.0f}" height="3" rx="1.5" fill="url(#g1)" opacity=".85"/>'
            f'<circle class="dot" cx="{x0 + 3:.0f}" cy="81.5" r="5" fill="{c["ink"]}"/></g>')
    return doc(W, H, body, css, defs, f"{text.title()} section title")


def divider(mode: str) -> str:
    """Thin animated separator: two comets run along a gradient line past a spinning diamond."""
    c = PAL[mode]
    W, H = 830, 40
    css = ("@keyframes cm{0%{transform:translateX(0);opacity:0}10%{opacity:1}90%{opacity:1}100%{transform:translateX(700px);opacity:0}}"
           ".cm{animation:cm 4.5s ease-in-out infinite}.cm2{animation:cm 4.5s ease-in-out infinite;animation-delay:-2.25s}"
           "@keyframes sp{to{transform:rotate(360deg)}}.sp{transform-box:fill-box;transform-origin:center;animation:sp 8s linear infinite}" + _tw())
    body = (f'<line x1="40" y1="20" x2="790" y2="20" stroke="url(#g1)" stroke-opacity=".35" stroke-width="2" stroke-linecap="round"/>'
            f'<g class="cm"><rect x="40" y="18.5" width="90" height="3" rx="1.5" fill="url(#cg)"/><circle cx="130" cy="20" r="4" fill="{c["accent"]}"/></g>'
            f'<g class="cm2"><rect x="40" y="18.5" width="90" height="3" rx="1.5" fill="url(#cg)"/><circle cx="130" cy="20" r="4" fill="{c["pink"]}"/></g>'
            f'<rect x="{W / 2 - 40}" y="6" width="80" height="28" fill="{c["page"]}"/>'
            f'<g class="sp"><rect x="{W / 2 - 8}" y="12" width="16" height="16" rx="3" fill="none" stroke="url(#g1)" stroke-width="2.4" transform="rotate(45 {W / 2} 20)"/></g>'
            f'{star4(W / 2 - 28, 20, 6, c["accent"], "tw")}{star4(W / 2 + 28, 20, 6, c["second"], "tw", "style=" + chr(34) + "animation-delay:-1.2s" + chr(34))}')
    defs = _grad(c, "g1") + f'<linearGradient id="cg"><stop offset="0" stop-color="{c["accent"]}" stop-opacity="0"/><stop offset="1" stop-color="{c["accent"]}"/></linearGradient>'
    return doc(W, H, body, css, defs, "divider")



def divider2(mode: str) -> str:
    """Heartbeat-style separator: an ECG line with a travelling pulse and a beating dot."""
    c = PAL[mode]
    W, H = 830, 40
    d = "M40 20 H300 l12 0 l8 -14 l10 28 l10 -22 l8 8 H500 l10 0 l7 -10 l8 20 l8 -14 l6 4 H790"
    css = ("@keyframes ecg{0%{stroke-dashoffset:100}100%{stroke-dashoffset:-100}}.ecg{stroke-dasharray:18 82;animation:ecg 3.2s linear infinite}"
           "@keyframes bt{0%,100%{transform:scale(1)}15%{transform:scale(1.5)}30%{transform:scale(1)}}.bt{transform-box:fill-box;transform-origin:center;animation:bt 1.4s ease-in-out infinite}" + _tw())
    body = (f'<path d="{d}" fill="none" stroke="url(#g1)" stroke-opacity=".3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path class="ecg" d="{d}" fill="none" stroke="url(#g1)" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" pathLength="100"/>'
            f'<circle class="bt" cx="{W / 2}" cy="20" r="5" fill="{c["pink"]}"/>{star4(60, 20, 6, c["accent"], "tw")}{star4(770, 20, 6, c["second"], "tw", "style=" + chr(34) + "animation-delay:-1.2s" + chr(34))}')
    return doc(W, H, body, css, _grad(c, "g1"), "divider")


# ------------------------------------------------------------------ ticker
def ticker(mode: str, words=None, reverse: bool = False) -> str:
    c = PAL[mode]
    W, H, DUR = 830, 56, 26
    f = typo.font(typo.HEAD)
    words = words or ["FULL-STACK", "ANDROID", "GAME DEV", "WEB3", "AI / LLM", "AUTOMATION"]
    x, parts = 0.0, ""
    for i, w in enumerate(words):
        d, wd = f.path(w, 19, x, 36, 3)
        parts += f'<path d="{d}" fill="{c["ink"] if i % 2 == 0 else c["muted"]}"/>'
        x += wd + 26
        parts += star4(x, 29, 8, [c["accent"], c["second"], c["pink"]][i % 3])
        x += 30
    seq = parts
    shift = x
    css = f"@keyframes tk{{from{{transform:translateX(0)}}to{{transform:translateX(-{shift:.0f}px)}}}}.tk{{animation:tk {DUR}s linear infinite{' reverse' if reverse else ''}}}"
    reps = int(W / shift) + 2
    track = "".join(f'<g transform="translate({k * shift:.0f} 0)">{seq}</g>' for k in range(reps + 1))
    defs = (lin_grad("fade", [(0, c["page"]), (.1, c["page"]), (.18, c["page"])], 0, 0, 1, 0)
            + f'<linearGradient id="eg" x1="0" x2="1"><stop offset="0" stop-color="{c["page"]}"/><stop offset=".12" stop-color="{c["page"]}" stop-opacity="0"/>'
              f'<stop offset=".88" stop-color="{c["page"]}" stop-opacity="0"/><stop offset="1" stop-color="{c["page"]}"/></linearGradient>'
            + _grad(c, "g1"))
    body = (f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="28" fill="{c["card"]}" stroke="url(#g1)" stroke-opacity=".6"/>'
            f'<g class="tk">{track}</g><rect width="{W}" height="{H}" rx="28" fill="url(#eg)"/>')
    return doc(W, H, body, css, defs, "Full-stack, Android, game dev, Web3, AI / LLM, automation")


# ------------------------------------------------------------------ hero column (width 400)
def hero_hello(mode: str) -> str:
    c = PAL[mode]
    W, H, T = 400, 168, 10.0
    sf, df = typo.font(typo.SCRIPT), typo.font(typo.DISPLAY)
    hi, hw = sf.path("Hi, I'm", 38, 8, 46)
    gl = df.glyphs("Rajdip", 96, 2, 134)
    css, letters = "", ""
    for i, (d, _, _) in enumerate(gl):
        t0 = 0.4 + i * 0.09
        css += kf(f"h{i}", T, [(0, "opacity:0;transform:translateY(36px) scale(.9)"), (t0, "opacity:0;transform:translateY(36px) scale(.9)"), (t0 + .55, "opacity:1;transform:none"),
                               (T - .8, "opacity:1;transform:none"), (T - .3, "opacity:0;transform:translateY(-10px)"), (T, "opacity:0")]) + f".h{i}{{animation:h{i} {T}s cubic-bezier(.2,.9,.25,1.15) infinite}}"
        letters += f'<path class="h{i}" d="{d}" fill="url(#g1)"/>'
    css += kf("hi", T, [(0, "opacity:0"), (.1, "opacity:0"), (.8, "opacity:1"), (T - .8, "opacity:1"), (T - .3, "opacity:0"), (T, "opacity:0")]) + f".hi{{animation:hi {T}s linear infinite}}"
    css += kf("shm", T, [(0, "transform:translateX(0)"), (3.5, "transform:translateX(0)"), (4.8, "transform:translateX(520px)"), (T, "transform:translateX(520px)")]) + f".shm{{animation:shm {T}s linear infinite}}"
    css += _tw()
    full = " ".join(g[0] for g in gl)
    defs = (_grad(c, "g1") + '<filter id="bl2" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="26"/></filter>' + f'<clipPath id="cl"><path d="{full}"/></clipPath>'
            + '<linearGradient id="sg"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    css += "@keyframes aura{0%,100%{opacity:.22;transform:scale(1)}50%{opacity:.5;transform:scale(1.2)}}.aura{transform-box:fill-box;transform-origin:center;animation:aura 4s ease-in-out infinite}"
    body = (f'<ellipse class="aura" cx="150" cy="100" rx="150" ry="52" fill="url(#g1)" filter="url(#bl2)"/><path class="hi" d="{hi}" fill="{c["accent"]}"/>{letters}'
            f'<g clip-path="url(#cl)"><rect class="shm" x="-140" y="40" width="90" height="110" fill="url(#sg)" opacity=".7" transform="skewX(-18)"/></g>'
            f'<path d="M6 152 q50 12 110 0 t110 0 t110 0" fill="none" stroke="url(#g1)" stroke-width="4" stroke-linecap="round" opacity=".9"/>'
            f'{star4(330, 40, 9, c["accent"], "tw")}{star4(362, 74, 6, c["second"], "tw", "style=\"animation-delay:-.9s\"")}{star4(300, 22, 5, c["pink"], "tw", "style=\"animation-delay:-1.7s\"")}')
    return doc(W, H, body, css, defs, "Hi, I'm Rajdip")


def hero_roles(mode: str) -> str:
    c = PAL[mode]
    W, H = 400, 54
    seg = 3.2
    phrases = ["full-stack web apps", "Android apps", "games from scratch", "Web3 experiments", "AI & automation"]
    T = seg * len(phrases)
    pf, bf = typo.font(typo.HEAD), typo.font(typo.BODY)
    d0, w0 = bf.path("I build", 22, 6, 34)
    x = 6 + w0 + 10
    css, items = "", ""
    for i, p in enumerate(phrases):
        d, w = pf.path(p, 24, x, 35)
        a = i * seg
        pts = [(0, "opacity:0;clip-path:inset(0 100% 0 0)")]
        if a > .02:
            pts.append((a - .01, "opacity:0;clip-path:inset(0 100% 0 0)"))
        pts += [(a, "opacity:1;clip-path:inset(0 100% 0 0)"), (a + .9, "opacity:1;clip-path:inset(0 0 0 0)"), (a + seg - .35, "opacity:1;clip-path:inset(0 0 0 0)"),
                (a + seg - .3, "opacity:0;clip-path:inset(0 0 0 0)"), (T, "opacity:0")]
        css += kf(f"p{i}", T, pts) + f".p{i}{{animation:p{i} {T}s linear infinite}}"
        cur = [(0, "opacity:0;transform:translateX(0)")]
        if a > .02:
            cur.append((a - .01, "opacity:0;transform:translateX(0)"))
        cur += [(a, "opacity:1;transform:translateX(0)"), (a + .9, f"opacity:1;transform:translateX({w:.0f}px)"), (a + seg - .35, f"opacity:1;transform:translateX({w:.0f}px)"), (a + seg - .3, "opacity:0"), (T, "opacity:0")]
        css += kf(f"q{i}", T, cur) + f".q{i}{{animation:q{i} {T}s linear infinite}}"
        items += f'<path class="p{i}" d="{d}" fill="url(#g1)"/><rect class="q{i}" x="{x:.1f}" y="13" width="3" height="28" rx="1.5" fill="{c["accent"]}"/>'
    css += ".p0{opacity:1}"
    body = f'<path d="{d0}" fill="{c["muted"]}"/>{items}'
    return doc(W, H, body, css, _grad(c, "g1"), "I build full-stack web apps, Android apps, games from scratch, Web3 experiments, AI and automation")


def _chip_icon(kind, x, y, col):
    if kind == "cap":
        return f'<path d="M{x} {y + 6} L{x + 9} {y + 1.5} L{x + 18} {y + 6} L{x + 9} {y + 10.5}Z M{x + 4} {y + 8.5} v4.5 q5 3 10 0 v-4.5" fill="none" stroke="{col}" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"/>'
    if kind == "pin":
        return f'<path d="M{x + 9} {y + 15} C{x + 1} {y + 8} {x + 3} {y} {x + 9} {y} C{x + 15} {y} {x + 17} {y + 8} {x + 9} {y + 15}Z" fill="none" stroke="{col}" stroke-width="1.7" stroke-linejoin="round"/><circle cx="{x + 9}" cy="{y + 6.5}" r="2.2" fill="{col}"/>'
    if kind == "cal":
        return f'<rect x="{x + 1}" y="{y + 2}" width="16" height="14" rx="3" fill="none" stroke="{col}" stroke-width="1.7"/><path d="M{x + 1} {y + 7} h16 M{x + 6} {y} v4 M{x + 12} {y} v4" stroke="{col}" stroke-width="1.7" stroke-linecap="round"/>'
    return f'<circle class="pu" cx="{x + 9}" cy="{y + 8}" r="4.5" fill="{col}"/><circle class="pr" cx="{x + 9}" cy="{y + 8}" r="4.5" fill="none" stroke="{col}" stroke-width="1.6"/>'


def hero_chips(mode: str) -> str:
    c = PAL[mode]
    W, H = 400, 112
    f = typo.font(typo.MEDIUM)
    chips = [("cap", "B.Tech CSE · HITK", c["accent"]), ("pin", "Kolkata · IST", c["second"]), ("cal", "Batch 2026–2030", c["pink"]), ("dot", "Open to internships", c["green"])]
    body, css = "", ("@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}.cb{animation:bob 4s ease-in-out infinite}"
                     "@keyframes run{to{stroke-dashoffset:-200}}.run{stroke-dasharray:46 154;animation:run 4s linear infinite}"
                     "@keyframes pu{0%,100%{opacity:1}50%{opacity:.45}}.pu{animation:pu 1.6s ease-in-out infinite}"
                     "@keyframes pr{0%{r:4.5;opacity:.9}100%{r:10;opacity:0}}.pr{animation:pr 1.6s ease-out infinite}")
    for i, (ic, label, col) in enumerate(chips):
        x, y = (i % 2) * 204, (i // 2) * 58 + 4
        d, w = f.path(label, 13.5, x + 40, y + 28)
        body += (f'<g class="cb" style="animation-delay:-{i * .9:.1f}s"><rect x="{x}" y="{y}" width="196" height="44" rx="22" fill="{c["card"]}" stroke="{c["line"]}"/>'
                 f'<rect class="run" x="{x}" y="{y}" width="196" height="44" rx="22" fill="none" stroke="{col}" stroke-width="2" pathLength="200" style="animation-delay:-{i}s"/>'
                 f'{_chip_icon(ic, x + 15, y + 13, col)}<path d="{d}" fill="{c["ink"]}"/></g>')
    return doc(W, H, body, css, "", "B.Tech CSE at HITK, Kolkata IST, batch 2026 to 2030, open to internships", pad_y=8)


def hero_welcome(mode: str) -> str:
    c = PAL[mode]
    W, H, T = 400, 78, 9.0
    sf = typo.font(typo.SCRIPT)
    txt = "welcome to my space"
    size = 40
    tw = sf.width(txt, size)
    gl = sf.glyphs(txt, size, 8, 48)
    css, draw, fill = "", "", ""
    for i, (d, _, _) in enumerate(gl):
        t0 = .2 + i * .09
        css += kf(f"d{i}", T, [(0, "stroke-dashoffset:1;opacity:1"), (t0, "stroke-dashoffset:1;opacity:1"), (t0 + .7, "stroke-dashoffset:0;opacity:1"), (T - .6, "stroke-dashoffset:0;opacity:1"), (T - .3, "opacity:0;stroke-dashoffset:0"), (T, "opacity:0;stroke-dashoffset:1")]) + f".d{i}{{animation:d{i} {T}s ease-in-out infinite}}"
        draw += f'<path class="d{i}" d="{d}" pathLength="1" fill="none" stroke="url(#g1)" stroke-width="1.6" stroke-dasharray="1" stroke-dashoffset="1"/>'
        fill += f'<path d="{d}"/>'
    css += kf("nf", T, [(0, "opacity:0"), (1.2, "opacity:0"), (2.2, "opacity:1"), (T - .6, "opacity:1"), (T - .3, "opacity:0"), (T, "opacity:0")]) + f".nf{{animation:nf {T}s linear infinite}}" + _tw()
    body = (f'<g class="nf" fill="url(#g1)">{fill}</g>{draw}'
            f'<path d="M10 66 q{tw / 4:.0f} -9 {tw / 2:.0f} 0 t{tw / 2:.0f} 0" fill="none" stroke="url(#g1)" stroke-width="3" stroke-linecap="round" opacity=".8"/>'
            f'{star4(tw + 34, 22, 9, c["accent"], "tw")}{star4(tw + 12, 12, 5, c["pink"], "tw", "style=\"animation-delay:-1s\"")}')
    return doc(W, H, body, css, _grad(c, "g1"), "Welcome to my space")


def button(label: str, icon_name: str | None, mode: str, primary: bool) -> str:
    c = PAL[mode]
    W, H, T = 190, 52, 5.0
    f = typo.font(typo.HEAD)
    d, w = f.path(label, 16, 0, 0)
    pad = 40 if icon_name == "follow" else 28
    total = w + (pad if icon_name else 0)
    x0 = (W - total) / 2
    fg = "#0D1117" if (primary and mode == "dark") else ("#FFFFFF" if primary else c["ink"])
    fill = 'url(#g1)' if primary else c["card"]
    if icon_name == "follow":
        ic = (f'<circle cx="{x0 + 8}" cy="21" r="5.5" fill="{fg}"/><path d="M{x0 - 2} 38 q0 -10 10 -10 t10 10z" fill="{fg}"/>'
              f'<g class="plus"><path d="M{x0 + 20} 18 h10 M{x0 + 25} 13 v10" stroke="{fg}" stroke-width="2.6" stroke-linecap="round"/></g>')
    else:
        ic = icon(icon_name, x0, 15, 22, fg) if icon_name else ""
    css = (kf("sw", T, [(0, "transform:translateX(0)"), (1.6, "transform:translateX(0)"), (2.6, "transform:translateX(280px)"), (T, "transform:translateX(280px)")]) + f".sw{{animation:sw {T}s linear infinite}}"
           "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}.bb{animation:bob 3.2s ease-in-out infinite}"
           "@keyframes plus{0%,100%{transform:scale(1) rotate(0)}50%{transform:scale(1.35) rotate(90deg)}}.plus{transform-box:fill-box;transform-origin:center;animation:plus 2s ease-in-out infinite}"
           "@keyframes bpl{0%{transform:scale(1);opacity:.7}100%{transform:scale(1.18,1.5);opacity:0}}.bpl{transform-box:fill-box;transform-origin:center;animation:bpl 2.2s ease-out infinite}")
    body = (f'<rect class="bpl" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26" fill="none" stroke="url(#g1)" stroke-width="2"/>'
            f'<g class="bb"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26" fill="{fill}" stroke="url(#g1)" stroke-width="2"/>'
            f'<clipPath id="bc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26"/></clipPath><g clip-path="url(#bc)"><rect class="sw" x="-100" y="0" width="60" height="{H}" fill="#fff" opacity=".35" transform="skewX(-20)"/></g>'
            f'{ic}<path d="{d}" transform="translate({x0 + (pad if icon_name else 0):.1f} 32)" fill="{fg}"/></g>')
    return doc(W, H, body, css, _grad(c, "g1"), label, pad_y=8)



def star_cta(mode: str) -> str:
    """Closing call-to-action: a big glowing star, a hand-lettered ask and a shimmering button."""
    import math
    c = PAL[mode]
    W, H, T = 830, 290, 10.0
    sf, bf, hf = typo.font(typo.SCRIPT), typo.font(typo.BODY), typo.font(typo.HEAD)
    # five-point star (outer r, inner r) centred at (150, 145)
    cx, cy, ro, ri = 150, 150, 74, 32
    pts = " ".join(f"{cx + (ro if i % 2 == 0 else ri) * math.cos(-math.pi / 2 + i * math.pi / 5):.1f},{cy + (ro if i % 2 == 0 else ri) * math.sin(-math.pi / 2 + i * math.pi / 5):.1f}" for i in range(10))
    # title with a draw-on look
    gl = sf.glyphs("Enjoyed the tour?", 52, 300, 108)
    full = "".join(g[0] for g in gl)
    css = ""
    draw = ""
    for i, (d, _, _) in enumerate(gl):
        t0 = .2 + i * .08
        css += kf(f"d{i}", T, [(0, "stroke-dashoffset:1;opacity:1"), (t0, "stroke-dashoffset:1;opacity:1"), (t0 + .7, "stroke-dashoffset:0;opacity:1"), (T - .7, "stroke-dashoffset:0;opacity:1"), (T - .3, "opacity:0;stroke-dashoffset:0"), (T, "opacity:0;stroke-dashoffset:1")]) + f".d{i}{{animation:d{i} {T}s ease-in-out infinite}}"
        draw += f'<path class="d{i}" d="{d}" pathLength="1" fill="none" stroke="url(#g1)" stroke-width="1.6" stroke-dasharray="1" stroke-dashoffset="1"/>'
    css += kf("tf", T, [(0, "opacity:0"), (1.4, "opacity:0"), (2.4, "opacity:1"), (T - .7, "opacity:1"), (T - .3, "opacity:0"), (T, "opacity:0")]) + f".tf{{animation:tf {T}s linear infinite}}"
    lines = bf.wrap("If this profile made you smile, drop a star on this repo. It tells me the work is worth sharing and keeps me building.", 15, 460)
    sub = "".join(f'<path d="{bf.path(l, 15, 300, 150 + k * 23)[0]}" fill="{c["muted"]}"/>' for k, l in enumerate(lines))
    css += kf("sb", T, [(0, "opacity:0;transform:translateY(8px)"), (2.0, "opacity:0;transform:translateY(8px)"), (2.8, "opacity:1;transform:none"), (T - .7, "opacity:1;transform:none"), (T - .3, "opacity:0"), (T, "opacity:0")]) + f".sb{{animation:sb {T}s ease-out infinite}}"
    # button
    bw, bh, bx, by = 236, 54, 300, 214
    lab, lw = hf.path("Star this repo", 18, 0, 0)
    bx_text = bx + 62
    bsx, bsy = bx + 38, by + bh / 2
    bpts = " ".join(f"{bsx + (11 if k % 2 == 0 else 4.6) * math.cos(-math.pi / 2 + k * math.pi / 5):.1f},{bsy + (11 if k % 2 == 0 else 4.6) * math.sin(-math.pi / 2 + k * math.pi / 5):.1f}" for k in range(10))
    # falling mini stars
    rr = __import__("random").Random(9)
    rain = ""
    for j in range(14):
        x = rr.randint(20, 810)
        r = rr.choice([4, 5, 6, 8])
        k = r * 0.28
        d = f"M{x} {-r} Q{x + k} {-k} {x + r} 0 Q{x + k} {k} {x} {r} Q{x - k} {k} {x - r} 0 Q{x - k} {-k} {x} {-r}Z"
        rain += f'<path class="fall" d="{d}" fill="{[c["accent"], c["second"], c["pink"]][j % 3]}" style="animation-delay:-{rr.uniform(0, 9):.1f}s;animation-duration:{rr.randint(6, 11)}s"/>'
    # orbiting sparkles around the big star
    orbit = f"M{cx - 100} {cy} a100 100 0 1 0 200 0 a100 100 0 1 0 -200 0"
    sparks = "".join(f'<path class="orb" d="M0 -7 Q2 -2 7 0 Q2 2 0 7 Q-2 2 -7 0 Q-2 -2 0 -7Z" fill="{col}" style="offset-path:path({A}{orbit}{A});animation-delay:-{k * 1.3:.1f}s"/>' for k, col in enumerate([c["accent"], c["pink"], c["second"], c["accent"]]))
    css += ("@keyframes fall{0%{transform:translateY(-10px) rotate(0);opacity:0}10%{opacity:.8}100%{transform:translateY(300px) rotate(180deg);opacity:0}}.fall{animation:fall 8s linear infinite}"
            "@keyframes orb{from{offset-distance:0%}to{offset-distance:100%}}.orb{animation:orb 6s linear infinite}"
            "@keyframes bst{0%,100%{transform:scale(1) rotate(0)}50%{transform:scale(1.12) rotate(8deg)}}.bst{transform-box:fill-box;transform-origin:center;animation:bst 2.6s ease-in-out infinite}"
            "@keyframes glow{0%,100%{opacity:.25;transform:scale(1)}50%{opacity:.6;transform:scale(1.2)}}.glow{transform-box:fill-box;transform-origin:center;animation:glow 2.6s ease-in-out infinite}"
            "@keyframes run{to{stroke-dashoffset:-1000}}.run{stroke-dasharray:180 820;animation:run 6s linear infinite}"
            "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}.bob{animation:bob 3s ease-in-out infinite}"
            "@keyframes shn{0%{transform:translateX(0)}45%,100%{transform:translateX(320px)}}.shn{animation:shn 3.4s ease-in-out infinite}"
            "@keyframes arr{0%,100%{transform:translateX(0)}50%{transform:translateX(5px)}}.arr{animation:arr 1.2s ease-in-out infinite}"
            "@keyframes ring{0%{r:44;opacity:.7}100%{r:112;opacity:0}}.ring{animation:ring 2.8s ease-out infinite}" + _tw())
    body = (f'<clipPath id="pc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="30"/></clipPath>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="30" fill="{c["card"]}" stroke="{c["line"]}"/>'
            f'<g clip-path="url(#pc)"><circle cx="{cx}" cy="{cy}" r="120" fill="url(#rg)" class="glow"/>{rain}</g>'
            f'<rect class="run" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="30" fill="none" stroke="url(#g1)" stroke-width="3" pathLength="1000"/>'
            f'<circle class="ring" cx="{cx}" cy="{cy}" r="44" fill="none" stroke="{c["accent"]}" stroke-width="2"/>'
            f'<circle class="ring" cx="{cx}" cy="{cy}" r="44" fill="none" stroke="{c["pink"]}" stroke-width="2" style="animation-delay:-1.4s"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="100" ry="100" fill="none" stroke="{c["line"]}" stroke-dasharray="3 6"/>{sparks}'
            f'<g class="bst"><polygon points="{pts}" fill="url(#g1)" stroke="url(#g1)" stroke-width="8" stroke-linejoin="round"/>'
            f'<polygon points="{pts}" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="2" stroke-linejoin="round" transform="translate({cx} {cy}) scale(.55) translate({-cx} {-cy})"/></g>'
            f'<g class="tf" fill="url(#g1)"><path d="{full}"/></g>{draw}<g class="sb">{sub}</g>'
            f'<g class="bob"><clipPath id="bcl"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="27"/></clipPath>'
            f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="27" fill="url(#g1)"/>'
            f'<g clip-path="url(#bcl)"><rect class="shn" x="{bx - 90}" y="{by}" width="50" height="{bh}" fill="#fff" opacity=".4" transform="skewX(-20)"/></g>'
            f'<polygon points="{bpts}" fill="{"#0D1117" if mode == "dark" else "#fff"}"/>'
            f'<path d="{hf.path("Star this repo", 18, bx_text, by + 34)[0]}" fill="{"#0D1117" if mode == "dark" else "#fff"}"/>'
            f'<g class="arr"><path d="M{bx + bw - 40} {by + 27} h18 m-7 -7 l7 7 l-7 7" fill="none" stroke="{"#0D1117" if mode == "dark" else "#fff"}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/></g></g>')
    defs = _grad(c, "g1") + f'<radialGradient id="rg"><stop offset="0" stop-color="{c["accent"]}" stop-opacity=".55"/><stop offset="1" stop-color="{c["accent"]}" stop-opacity="0"/></radialGradient>'
    return doc(W, H, body, css, defs, "Enjoyed the tour? Star this repo", pad_y=8)



GAME_URL = "https://rajdipdhar2007.github.io/RajdipDhar2007/"


def arcade_card(mode: str) -> str:
    """README teaser for the playable game: a looping mini playfield next to the pitch and a PLAY button."""
    import random
    c = PAL[mode]
    W, H = 830, 330
    sf, hf, bf, mf = typo.font(typo.SCRIPT), typo.font(typo.HEAD), typo.font(typo.BODY), typo.font(typo.MONO_B)
    rr = random.Random(12)
    fx, fy, fw, fh = 26, 26, 262, 278
    # ---- mini playfield
    stars = "".join(f'<circle class="st" cx="{fx + rr.randint(4, fw - 4)}" cy="{fy + rr.randint(0, fh)}" r="{rr.choice([.8, 1.1, 1.5])}" fill="{c["ink"]}" style="animation-duration:{rr.randint(3, 7)}s;animation-delay:-{rr.uniform(0, 6):.1f}s"/>' for _ in range(34))

    def bug(x, col, dur, delay, amp):
        return (f'<g class="bf" style="animation-duration:{dur}s;animation-delay:-{delay}s"><g class="sw" style="animation-duration:{dur / 2}s;--a:{amp}px"><g transform="translate({x} {fy - 20})">'
                f'<ellipse cx="0" cy="2" rx="11" ry="13" fill="{c["card"]}" stroke="{col}" stroke-width="2"/>'
                f'<path d="M-11 -4 l-7 -3 M-11 3 l-8 1 M-11 9 l-7 5 M11 -4 l7 -3 M11 3 l8 1 M11 9 l7 5 M-3 -13 l-4 -7 M3 -13 l4 -7" stroke="{col}" stroke-width="2" stroke-linecap="round"/>'
                f'<circle cx="-4" cy="-4" r="2.4" fill="#fff"/><circle cx="4" cy="-4" r="2.4" fill="#fff"/></g></g></g>')
    bugs = bug(fx + 60, c["green"], 7, 0, 22) + bug(fx + 130, c["pink"], 6, 2.3, 30) + bug(fx + 200, c["second"], 8, 4.6, 18) + bug(fx + 95, c["green"], 9, 6.1, 26)
    bullets = "".join(f'<rect class="bl" x="{fx + fw / 2 - 2}" y="{fy + fh - 40}" width="4" height="14" rx="2" fill="{c["accent"]}" style="animation-delay:-{k * .22:.2f}s"/>' for k in range(5))
    booms = "".join(f'<circle class="bm" cx="{fx + x}" cy="{fy + y}" r="6" fill="none" stroke="{col}" stroke-width="3" style="animation-delay:-{d}s"/>' for x, y, col, d in [(70, 90, c["green"], 0), (170, 130, c["pink"], 1.7), (120, 60, c["accent"], 3.1)])
    ship = (f'<g transform="translate({fx + fw / 2} {fy + fh - 22})"><g class="sh"><path d="M0 -16 L11 12 L0 6 L-11 12Z" fill="url(#g1)"/>'
            f'<path class="fl" d="M-3 9 Q0 24 3 9Z" fill="{c["pink"]}"/></g></g>')
    hud = f'<path d="{mf.path("SCORE 004210", 10, fx + 12, fy + 20, 1)[0]}" fill="{c["accent"]}"/><path d="{mf.path("WAVE 3", 10, fx + fw - 62, fy + 20, 1)[0]}" fill="{c["muted"]}"/>'
    # ---- right side copy
    title, tw = sf.path("Bug Hunter", 64, 330, 98)
    sub, _ = mf.path("A  PLAYABLE  ARCADE  SHOOTER", 12, 332, 126, 3)
    pitch = bf.wrap("Squash bugs, dodge their fire and take on the SEGFAULT boss. Power-ups, combos and a rank for every score.", 15, 450)
    pd = "".join(f'<path d="{bf.path(l, 15, 332, 160 + k * 23)[0]}" fill="{c["muted"]}"/>' for k, l in enumerate(pitch))
    bx, by, bw, bh = 332, 244, 214, 52
    play, _ = hf.path("PLAY NOW", 17, bx + 66, by + 33, 1)
    tri = f"M{bx + 30} {by + 16} L{bx + 30} {by + 36} L{bx + 46} {by + 26}Z"
    dark = "#0D1117" if mode == "dark" else "#fff"
    # rotating motivational lines (one CSS cycle, each wipes in, glows, then fades up and out)
    qx, qw, slot = bx + bw + 24, 224, 3.6
    quotes = ["Debug today, ship tomorrow.", "Small steps still ship big things.", "Every bug is a lesson in disguise.", "Press start on your next idea.",
              "Code it. Break it. Fix it. Level up.", "Be the boss you are trying to beat.", "Progress beats perfect, every run.", "Stay curious. Keep shipping."]
    qparts = ""
    for k, qt in enumerate(quotes):
        ql = hf.wrap(qt, 14.5, qw)[:2]
        qd = "".join(f'<path d="{hf.path(l, 14.5, qx, by + 27 + j * 21)[0]}" fill="{c["ink"]}"/>' for j, l in enumerate(ql))
        qparts += f'<g class="q q{k}" style="animation-delay:{k * slot:.1f}s">{qd}</g>'
    qlab, _ = mf.path("POWER-UP", 9.5, qx + 14, by + 8, 3)
    quote = (f'<g class="qb"><path d="M{qx - 12} {by + 3} V{by + bh - 2}" stroke="url(#g1)" stroke-width="3" stroke-linecap="round"/></g>'
             f'<path class="qlab" d="{qlab}" fill="{c["accent"]}"/>{star4(qx + 4, by + 4, 4.5, c["pink"], "tw")}{qparts}')
    chips, x = "", 332
    for k, lab in enumerate(["BOSS FIGHTS", "POWER-UPS", "COMBOS", "MOBILE READY"]):
        cw = mf.width(lab, 10, 1) + 22
        chips += f'<rect x="{x}" y="200" width="{cw:.0f}" height="24" rx="12" fill="none" stroke="{[c["accent"], c["second"], c["pink"], c["green"]][k]}" stroke-width="1.6"/><path d="{mf.path(lab, 10, x + 11, 216, 1)[0]}" fill="{c["ink"]}"/>'
        x += cw + 8
    scan = "".join(f'<rect x="{fx}" y="{fy + k * 6}" width="{fw}" height="1" fill="#000" opacity=".16"/>' for k in range(fh // 6))
    pw = (f'<g class="pwr"><circle cx="{fx + 150}" cy="{fy - 12}" r="10" fill="{c["card"]}" stroke="{c["green"]}" stroke-width="2"/>'
          f'<path d="{mf.path("H", 11, fx + 145, fy - 8)[0]}" fill="{c["green"]}"/></g>'
          f'<path class="pop" d="{mf.path("+100", 11, fx + 60, fy + 120, 1)[0]}" fill="{c["gold"] if "gold" in c else c["pink"]}"/>')
    css = ("@keyframes pwr{from{transform:translate(0,0)}to{transform:translate(-40px,300px)}}.pwr{animation:pwr 9s linear infinite;animation-delay:-3s}"
           "@keyframes pop{0%,100%{opacity:0;transform:translateY(0)}10%{opacity:1}40%{opacity:0;transform:translateY(-22px)}}.pop{animation:pop 3.4s ease-out infinite}"
           "@keyframes qin{0%{opacity:0;transform:translateY(14px);clip-path:inset(0 100% 0 0)}2%{opacity:1}6%{opacity:1;transform:translateY(0);clip-path:inset(-4px 0 -4px 0)}11%{opacity:1;transform:translateY(0);clip-path:inset(-4px 0 -4px 0)}12.5%,100%{opacity:0;transform:translateY(-14px);clip-path:inset(-4px 0 -4px 0)}}"
           ".q{opacity:0;animation:qin 28.8s ease-out infinite both}.q0{opacity:1}"
           "@keyframes qlab{0%,100%{opacity:1}50%{opacity:.45}}.qlab{animation:qlab 1.4s ease-in-out infinite}"
           "@keyframes qbar{0%,100%{opacity:.5}50%{opacity:1}}.qb{animation:qbar 1.8s ease-in-out infinite}"
           "@keyframes crt{from{transform:translateY(0)}to{transform:translateY(6px)}}.crt{animation:crt .5s linear infinite}"
           "@keyframes bf{from{transform:translateY(0)}to{transform:translateY(330px)}}.bf{animation:bf 7s linear infinite}"
           "@keyframes sw{0%,100%{transform:translateX(calc(var(--a) * -1))}50%{transform:translateX(var(--a))}}.sw{animation:sw 3s ease-in-out infinite}"
           "@keyframes sh{0%,100%{transform:translateX(-70px)}50%{transform:translateX(70px)}}.sh{animation:sh 4.4s ease-in-out infinite}"
           "@keyframes bl{0%{transform:translateY(0);opacity:1}100%{transform:translateY(-230px);opacity:0}}.bl{animation:bl 1.1s linear infinite}"
           "@keyframes bm{0%{r:4;opacity:1}100%{r:26;opacity:0}}.bm{animation:bm 3.4s ease-out infinite}"
           "@keyframes st{0%{transform:translateY(0);opacity:.2}50%{opacity:1}100%{transform:translateY(40px);opacity:.2}}.st{animation:st 5s linear infinite}"
           "@keyframes fl{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.7)}}.fl{transform-box:fill-box;transform-origin:top;animation:fl .25s ease-in-out infinite}"
           "@keyframes run{to{stroke-dashoffset:-1000}}.run{stroke-dasharray:180 820;animation:run 6s linear infinite}"
           "@keyframes pl{0%{transform:scale(1);opacity:.7}100%{transform:scale(1.2,1.6);opacity:0}}.pl{transform-box:fill-box;transform-origin:center;animation:pl 1.8s ease-out infinite}"
           "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}.bob{animation:bob 2.6s ease-in-out infinite}"
           "@keyframes shn{0%{transform:translateX(0)}45%,100%{transform:translateX(300px)}}.shn{animation:shn 3.2s ease-in-out infinite}"
           "@keyframes tri{0%,100%{transform:translateX(0)}50%{transform:translateX(4px)}}.tri{animation:tri 1s ease-in-out infinite}" + _tw())
    body = (f'<clipPath id="pf"><rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="18"/></clipPath><clipPath id="pc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="30"/></clipPath>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="30" fill="{c["card"]}" stroke="{c["line"]}"/>'
            f'<rect class="run" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="30" fill="none" stroke="url(#g1)" stroke-width="3" pathLength="1000"/>'
            f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="18" fill="url(#pbg)" stroke="{c["accent"]}" stroke-opacity=".5"/>'
            f'<g clip-path="url(#pf)">{stars}{bugs}{booms}{bullets}{ship}{pw}<g class="crt">{scan}</g>{hud}</g>'
            f'<path d="{title}" fill="url(#g1)"/><path d="{sub}" fill="{c["accent"]}"/>{pd}{chips}'
            f'<rect class="pl" x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="26" fill="none" stroke="url(#g1)" stroke-width="2.5"/>'
            f'<g class="bob"><clipPath id="bcl"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="26"/></clipPath><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="26" fill="url(#g1)"/>'
            f'<g clip-path="url(#bcl)"><rect class="shn" x="{bx - 90}" y="{by}" width="46" height="{bh}" fill="#fff" opacity=".4" transform="skewX(-20)"/></g>'
            f'<path class="tri" d="{tri}" fill="{dark}"/><path d="{play}" fill="{dark}"/></g>'
            f'{quote}{star4(790, 40, 9, c["accent"], "tw")}{star4(760, 70, 5, c["pink"], "tw", "style=" + chr(34) + "animation-delay:-1s" + chr(34))}')
    defs = _grad(c, "g1") + f'<linearGradient id="pbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["base"]}"/><stop offset="1" stop-color="{c["base2"]}"/></linearGradient>'
    return doc(W, H, body, css, defs, "Bug Hunter, a playable arcade shooter. Click to play.", pad_y=8)

# ------------------------------------------------------------------ about cards
def _about_icon(i: int, x: float, y: float, col: str) -> str:
    """Tiny animated glyph per about card: cap bob, code brackets pulse, sparkle spin, radar ping."""
    if i == 0:
        return f'<g class="ic1"><path d="M{x} {y + 8} L{x + 11} {y + 2} L{x + 22} {y + 8} L{x + 11} {y + 14}Z M{x + 5} {y + 11} v6 q6 4 12 0 v-6" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></g>'
    if i == 1:
        return f'<g class="ic2"><path d="M{x + 7} {y + 2} L{x} {y + 10} L{x + 7} {y + 18} M{x + 15} {y + 2} L{x + 22} {y + 10} L{x + 15} {y + 18}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></g>'
    if i == 2:
        return f'<g class="ic3">{star4(x + 11, y + 10, 11, col)}</g>'
    return (f'<circle cx="{x + 11}" cy="{y + 10}" r="4" fill="{col}"/><circle class="ic4" cx="{x + 11}" cy="{y + 10}" r="4" fill="none" stroke="{col}" stroke-width="2"/>')


def about(mode: str) -> str:
    c = PAL[mode]
    W, H, T = 830, 300, 10.0
    cards = [("EDUCATION", "B.Tech CSE", "Heritage Institute of Technology, Kolkata · 2026–2030", c["accent"]),
             ("FOCUS", "Build things", "Full-stack · Android · Game dev · Web3", c["second"]),
             ("EXPLORING", "AI & automation", "LLM-powered apps and workflows that save time", c["pink"]),
             ("LOOKING FOR", "Internships", "…and people to build cool things with", c["green"])]
    tf, bf, mf = typo.font(typo.DISPLAY), typo.font(typo.BODY), typo.font(typo.MONO_B)
    body, css = "", ("@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}.cb{animation:bob 5s ease-in-out infinite}"
                     "@keyframes run{to{stroke-dashoffset:-400}}.run{stroke-dasharray:90 310;animation:run 6s linear infinite}"
                     "@keyframes shn{0%{transform:translateX(0)}45%,100%{transform:translateX(280px)}}.shn{animation:shn 6s ease-in-out infinite}"
                     "@keyframes ic1{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}.ic1{animation:ic1 2.2s ease-in-out infinite}"
                     "@keyframes ic2{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(1.12)}}.ic2{transform-box:fill-box;transform-origin:center;animation:ic2 1.8s ease-in-out infinite}"
                     "@keyframes ic3{to{transform:rotate(360deg)}}.ic3{transform-box:fill-box;transform-origin:center;animation:ic3 6s linear infinite}"
                     "@keyframes ic4{0%{r:4;opacity:.9}100%{r:13;opacity:0}}.ic4{animation:ic4 1.8s ease-out infinite}")
    for i, (lab, title, desc, col) in enumerate(cards):
        x = i * 213
        ld, _ = mf.path(lab, 11.5, x + 20, 50, 2)
        tsz = min(21.0, 21.0 * 152 / tf.width(title, 21))  # shrink long titles so they never leave the card
        td, _ = tf.path(title, tsz, x + 20, 92)
        lines = bf.wrap(desc, 13.5, 150)
        dd = "".join(f'<path d="{bf.path(l, 13.5, x + 20, 122 + k * 21)[0]}" fill="{c["muted"]}"/>' for k, l in enumerate(lines))
        body += (f'<g class="cb" style="animation-delay:-{i * 1.1:.1f}s"><rect x="{x + .5}" y="14.5" width="190" height="178" rx="22" fill="{c["card"]}" stroke="{c["line"]}"/>'
                 f'<rect class="run" x="{x + .5}" y="14.5" width="190" height="178" rx="22" fill="none" stroke="{col}" stroke-width="2.4" pathLength="400" style="animation-delay:-{i * 1.5}s"/>'
                 f'<clipPath id="ac{i}"><rect x="{x}" y="14" width="191" height="179" rx="22"/></clipPath><g clip-path="url(#ac{i})"><rect class="shn" x="{x - 60}" y="14" width="34" height="180" fill="{col}" opacity=".10" transform="skewX(-20)" style="animation-delay:-{i * 1.4:.1f}s"/></g>'
                 f'{_about_icon(i, x + 150, 28, col)}<path d="{ld}" fill="{col}"/><path d="{td}" fill="{c["ink"]}"/>{dd}</g>')
    ff = typo.font(typo.HEAD)
    fd, _ = ff.path("Fun fact:", 15, 0, 0)
    fact = "this README is generated code. The portrait is made of text and every banner is hand-built SVG."
    lines = bf.wrap(fact, 15, 650)
    fy = 250
    ftxt, tT, tcss, t0 = "", 11.0, "", 0.6
    for k, l in enumerate(lines):
        dur = max(len(l) * 0.045, .5)
        tcss += kf(f"ty{k}", tT, [(0, "opacity:0;clip-path:inset(0 100% 0 0)"), (t0 - .01, "opacity:0;clip-path:inset(0 100% 0 0)"), (t0, "opacity:1;clip-path:inset(0 100% 0 0)"),
                                  (t0 + dur, "opacity:1;clip-path:inset(0 0 0 0)"), (tT - .8, "opacity:1;clip-path:inset(0 0 0 0)"), (tT - .4, "opacity:0"), (tT, "opacity:0")]) + f".ty{k}{{animation:ty{k} {tT}s steps({max(len(l), 1)},end) infinite}}"
        ftxt += f'<g class="ty{k}"><path d="{bf.path(l, 15, 112, fy + k * 22)[0]}" fill="{c["ink"]}"/></g>'
        t0 += dur + .1
    tcss += "@keyframes cb{0%,49%{opacity:1}50%,100%{opacity:0}}.cb2{animation:cb 1s steps(1) infinite}"
    tcss += kf("cbw", tT, [(0, "opacity:0"), (t0, "opacity:0"), (t0 + .05, "opacity:1"), (tT - .8, "opacity:1"), (tT - .4, "opacity:0"), (tT, "opacity:0")]) + f".cbw{{animation:cbw {tT}s linear infinite}}"
    ftxt += f'<g class="cbw"><rect class="cb2" x="{112 + bf.width(lines[-1], 15) + 4:.0f}" y="{fy + (len(lines) - 1) * 22 - 14}" width="8" height="17" fill="{c["accent"]}"/></g>'
    abody_extra_css = tcss
    body += (f'<g class="cb" style="animation-delay:-2s"><rect x=".5" y="214.5" width="829" height="74" rx="20" fill="{c["card"]}" stroke="{c["line"]}"/>'
             f'<path d="{ff.path("Fun fact:", 15, 28, fy)[0]}" fill="{c["accent"]}"/>{ftxt}</g>')
    css += abody_extra_css
    return doc(W, H, body, css, "", "About: B.Tech CSE at HITK, full-stack, Android, game dev and Web3, exploring AI and automation, looking for internships", pad_y=8)


# ------------------------------------------------------------------ contact
def contact_pill(label: str, sub: str, icon_name: str, mode: str) -> str:
    c = PAL[mode]
    W, H, T = 250, 68, 6.0
    lf, sf = typo.font(typo.HEAD), typo.font(typo.BODY)
    ld, _ = lf.path(label, 17, 62, 30)
    sd, _ = sf.path(sub, 11.5, 62, 50)
    css = (kf("sw", T, [(0, "transform:translateX(0)"), (2, "transform:translateX(0)"), (3.2, "transform:translateX(340px)"), (T, "transform:translateX(340px)")]) + f".sw{{animation:sw {T}s linear infinite}}"
           "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}.bb{animation:bob 3.6s ease-in-out infinite}"
           "@keyframes run{to{stroke-dashoffset:-300}}.run{stroke-dasharray:70 230;animation:run 3.5s linear infinite}"
           "@keyframes png{0%{r:20;opacity:.8}100%{r:34;opacity:0}}.png{animation:png 2.2s ease-out infinite}")
    body = (f'<clipPath id="bc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22"/></clipPath><g class="bb">'
            f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="{c["card"]}" stroke="{c["line"]}" stroke-width="1.5"/>'
            f'<rect class="run" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="url(#g1)" stroke-width="2.6" pathLength="300"/>'
            f'<g clip-path="url(#bc)"><rect class="sw" x="-90" y="0" width="50" height="{H}" fill="{c["accent"]}" opacity=".18" transform="skewX(-20)"/></g>'
            f'<circle cx="34" cy="34" r="20" fill="url(#g1)" opacity=".18"/><circle class="png" cx="34" cy="34" r="20" fill="none" stroke="{c["accent"]}" stroke-width="2"/>{icon(icon_name, 22, 22, 24, c["accent"])}'
            f'<path d="{ld}" fill="{c["ink"]}"/><path d="{sd}" fill="{c["muted"]}"/></g>')
    return doc(W, H, body, css, _grad(c, "g1"), f"{label}: {sub}", pad_y=8)


# ------------------------------------------------------------------ live greeting
SLOTS = ("morning", "afternoon", "evening", "night")
SCENES = SLOTS + ("saturday", "sunday")


def greeting_svg(mode: str, text: str, stamp: str, scene="morning", slot=None) -> str:
    """scene: morning | afternoon | evening | night | saturday | sunday (a bool is accepted: True = night)."""
    import random as _r
    if isinstance(scene, bool):
        scene = "night" if scene else "morning"
    c = PAL[mode]
    warm = "#FB923C" if mode == "dark" else "#EA580C"
    W, H = 830, 88
    hf, bf = typo.font(typo.HEAD), typo.font(typo.MONO)
    d, w = hf.path(text, 18, 104, 38)
    sd, sw = bf.path(stamp, 11.5, 122, 60)
    rr = _r.Random(3)
    css = ("@keyframes spin{to{transform:rotate(360deg)}}.spin{transform-origin:42px 42px;animation:spin 14s linear infinite}"
           "@keyframes run{to{stroke-dashoffset:-400}}.run{stroke-dasharray:80 320;animation:run 6s linear infinite}"
           "@keyframes bobi{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}.bobi{animation:bobi 2.8s ease-in-out infinite}"
           "@keyframes tws{0%,100%{opacity:.15}50%{opacity:.9}}.tws{animation:tws 3s ease-in-out infinite}"
           "@keyframes gsl{0%{transform:translate(0,0);opacity:0}10%{opacity:1}35%,100%{transform:translate(220px,70px);opacity:0}}.gsl{animation:gsl 7s ease-in infinite}"
           "@keyframes cld{from{transform:translateX(0)}to{transform:translateX(300px)}}.cld{animation:cld 20s linear infinite}"
           "@keyframes hal{0%,100%{opacity:.25;transform:scale(1)}50%{opacity:.6;transform:scale(1.25)}}.hal{transform-box:fill-box;transform-origin:center;animation:hal 3.2s ease-in-out infinite}"
           "@keyframes bird{from{transform:translate(0,0)}to{transform:translate(340px,-22px)}}.bird{animation:bird 16s linear infinite}"
           "@keyframes flap{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.35)}}.flap{transform-box:fill-box;transform-origin:center;animation:flap .7s ease-in-out infinite}"
           "@keyframes fly{0%,100%{opacity:.1;transform:translate(0,0)}50%{opacity:1;transform:translate(8px,-10px)}}.fly{animation:fly 3.6s ease-in-out infinite}"
           "@keyframes conf{0%{transform:translateY(-12px) rotate(0);opacity:0}10%{opacity:1}100%{transform:translateY(100px) rotate(360deg);opacity:0}}.conf{animation:conf 4.5s linear infinite}"
           "@keyframes burst{0%{transform:scale(.1);opacity:1}70%{opacity:.9}100%{transform:scale(1);opacity:0}}.burst{transform-box:fill-box;transform-origin:center;animation:burst 3.4s ease-out infinite}"
           "@keyframes steam{0%{transform:translateY(0);opacity:0}30%{opacity:.8}100%{transform:translateY(-8px);opacity:0}}.steam{animation:steam 2.4s ease-in infinite}"
           "@keyframes leaf{0%{transform:translate(0,-10px) rotate(0);opacity:0}15%{opacity:.8}100%{transform:translate(-120px,100px) rotate(240deg);opacity:0}}.leaf{animation:leaf 9s linear infinite}"
           "@keyframes pad{0%,100%{transform:rotate(-8deg)}50%{transform:rotate(8deg)}}.pad{transform-box:fill-box;transform-origin:center;animation:pad 1.6s ease-in-out infinite}" + _tw())
    defs = _grad(c, "g1") + (f'<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset=".42" stop-color="#fff" stop-opacity="0"/><stop offset=".78" stop-color="#fff" stop-opacity="1"/></linearGradient>'
                             f'<mask id="sm" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>')
    scn = ""
    if scene == "night":      # crescent + twinkles
        icon_svg = (f'<path d="M52 22 a20 20 0 1 0 12 36 a16 16 0 1 1 -12 -36z" fill="{c["second"]}"/>'
                    f'{star4(66, 26, 5, c["accent"], "tw")}{star4(30, 30, 4, c["pink"], "tw", "style=" + chr(34) + "animation-delay:-1s" + chr(34))}')
        scn = "".join(f'<circle class="tws" cx="{rr.randint(520, 800)}" cy="{rr.randint(10, 72)}" r="{rr.choice([1, 1.4, 2])}" fill="{c["ink"]}" style="animation-delay:-{rr.uniform(0, 3):.1f}s"/>' for _ in range(26))
        scn += f'<line class="gsl" x1="560" y1="14" x2="500" y2="-6" stroke="{c["accent"]}" stroke-width="2" stroke-linecap="round"/>'
    elif scene == "evening":  # sun sinking into a glowing horizon, birds, fireflies
        defs += (f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["second"]}" stop-opacity="0"/>'
                 f'<stop offset=".6" stop-color="{c["pink"]}" stop-opacity=".16"/><stop offset="1" stop-color="{warm}" stop-opacity=".34"/></linearGradient>'
                 f'<clipPath id="hz"><rect x="14" y="14" width="56" height="42"/></clipPath>')
        icon_svg = (f'<circle class="hal" cx="42" cy="56" r="26" fill="{warm}" opacity=".3"/>'
                    f'<g clip-path="url(#hz)"><g class="bobi"><circle cx="42" cy="56" r="15" fill="{warm}"/><circle cx="42" cy="56" r="9" fill="{c["pink"]}" opacity=".55"/></g></g>'
                    f'<path d="M12 56 H72" stroke="{warm}" stroke-width="3" stroke-linecap="round"/><path d="M20 63 H64" stroke="{c["pink"]}" stroke-width="2" stroke-linecap="round" opacity=".6"/>'
                    f'{star4(66, 22, 4, c["accent"], "tw")}')
        scn = (f'<rect x="440" y="0" width="390" height="84" fill="url(#sky)"/>'
               + "".join(f'<g class="bird" style="animation-delay:-{k * 5.3:.1f}s;animation-duration:{14 + k * 3}s"><path class="flap" d="M470 {24 + k * 14} q6 -7 12 0 q6 -7 12 0" fill="none" stroke="{c["ink"]}" stroke-opacity=".45" stroke-width="1.8" stroke-linecap="round" style="animation-delay:-{k * .3:.1f}s"/></g>' for k in range(3))
               + "".join(f'<circle class="fly" cx="{rr.randint(560, 810)}" cy="{rr.randint(44, 76)}" r="{rr.choice([1.4, 1.9, 2.4])}" fill="{warm}" style="animation-delay:-{rr.uniform(0, 3.6):.1f}s"/>' for _ in range(14)))
    elif scene == "saturday":  # game pad + confetti and fireworks: weekend build mode
        icon_svg = (f'<g class="pad"><rect x="18" y="30" width="48" height="26" rx="13" fill="{c["card"]}" stroke="url(#g1)" stroke-width="3"/>'
                    f'<path d="M30 36 v14 M23 43 h14" stroke="{c["accent"]}" stroke-width="3" stroke-linecap="round"/>'
                    f'<circle cx="51" cy="40" r="3" fill="{c["pink"]}"/><circle cx="58" cy="46" r="3" fill="{c["green"]}"/></g>'
                    f'{star4(66, 22, 5, c["pink"], "tw")}{star4(20, 24, 4, c["accent"], "tw", "style=" + chr(34) + "animation-delay:-1.1s" + chr(34))}')
        cols = [c["accent"], c["pink"], c["second"], c["green"], warm]
        scn = "".join(f'<rect class="conf" x="{rr.randint(500, 810)}" y="{rr.randint(-4, 12)}" width="5" height="9" rx="1.5" fill="{cols[k % 5]}" style="animation-delay:-{rr.uniform(0, 4.5):.1f}s;animation-duration:{3.5 + rr.random() * 2:.1f}s"/>' for k in range(26))
        for k, (bx_, by_) in enumerate([(600, 30), (730, 48), (670, 62)]):
            ray = "".join(f'<line x1="{bx_}" y1="{by_ - 6}" x2="{bx_}" y2="{by_ - 17}" stroke="{cols[(k + a) % 5]}" stroke-width="2.2" stroke-linecap="round" transform="rotate({a * 45} {bx_} {by_})"/>' for a in range(8))
            scn += f'<g class="burst" style="animation-delay:-{k * 1.15:.2f}s">{ray}</g>'
    elif scene == "sunday":    # coffee with rising steam, drifting leaves: slow recharge day
        icon_svg = (f'<path d="M20 38 h36 v12 a12 12 0 0 1 -12 12 h-12 a12 12 0 0 1 -12 -12z" fill="{c["card"]}" stroke="url(#g1)" stroke-width="3" stroke-linejoin="round"/>'
                    f'<path d="M56 42 h4 a6 6 0 0 1 0 12 h-5" fill="none" stroke="url(#g1)" stroke-width="3" stroke-linecap="round"/>'
                    f'<path d="M24 38 h28 v4 h-28z" fill="{warm}" opacity=".7"/>'
                    + "".join(f'<path class="steam" d="M{x} 32 q-4 -5 0 -9 q4 -4 0 -9" fill="none" stroke="{c["muted"]}" stroke-width="2.2" stroke-linecap="round" style="animation-delay:-{k * .8:.1f}s"/>' for k, x in enumerate((28, 38, 48))))
        scn = "".join(f'<g class="cld" style="animation-delay:-{k * 6}s;animation-duration:{26 + k * 6}s"><ellipse cx="520" cy="{22 + k * 22}" rx="34" ry="9" fill="{c["second"]}" opacity=".16"/><ellipse cx="545" cy="{16 + k * 22}" rx="22" ry="8" fill="{c["second"]}" opacity=".16"/></g>' for k in range(3))
        scn += "".join(f'<g transform="translate({rr.randint(640, 830)} {rr.randint(0, 12)})"><path class="leaf" d="M0 0 q6 -8 12 0 q-6 8 -12 0z" fill="{[warm, c["green"], c["pink"]][k % 3]}" opacity=".7" style="animation-delay:-{rr.uniform(0, 9):.1f}s"/></g>' for k in range(9))
    else:                      # morning / afternoon: spinning sun, drifting clouds
        rays = "".join(f'<line x1="42" y1="10" x2="42" y2="18" stroke="{c["accent"]}" stroke-width="3" stroke-linecap="round" transform="rotate({a} 42 42)"/>' for a in range(0, 360, 45))
        icon_svg = f'<g class="spin">{rays}</g><circle cx="42" cy="42" r="12" fill="{c["pink"]}"/>'
        scn = "".join(f'<g class="cld" style="animation-delay:-{k * 5}s;animation-duration:{18 + k * 4}s"><ellipse cx="540" cy="{20 + k * 20}" rx="30" ry="9" fill="{c["accent"]}" opacity=".18"/><ellipse cx="560" cy="{14 + k * 20}" rx="20" ry="8" fill="{c["accent"]}" opacity=".18"/></g>' for k in range(3))
    chip = ""
    if scene in ("saturday", "sunday"):
        lab_t = "SATURDAY MODE" if scene == "saturday" else "SUNDAY MODE"
        cd, cw_ = bf.path(lab_t, 9.5, 0, 0, 1.6)
        cx0 = 122 + sw + 18
        chip = (f'<g class="bobi"><rect x="{cx0}" y="48" width="{cw_ + 34:.0f}" height="17" rx="8.5" fill="none" stroke="url(#g1)" stroke-width="1.6"/>'
                f'{star4(cx0 + 12, 56.5, 4, c["pink"], "tw")}<path d="{cd}" transform="translate({cx0 + 23:.0f} 60)" fill="{c["ink"]}"/></g>')
    css += ("@keyframes tlg{0%,30%{transform:translateX(0)}80%,100%{transform:translateX(190px)}}.tlg{animation:tlg 3.6s ease-in-out infinite}"
            "@keyframes tlp{0%{opacity:.8}100%{opacity:0}}.tlp{animation:tlp 1.8s ease-out infinite}"
            "@keyframes typ{0%{clip-path:inset(0 100% 0 0)}12%,100%{clip-path:inset(-6px 0 -6px 0)}}.typ{animation:typ 14s steps(40,end) infinite}"
            "@keyframes shm{0%,25%{transform:translateX(-120px)}60%,100%{transform:translateX(760px)}}.shm{animation:shm 6s ease-in-out infinite}"
            "@keyframes rsp{to{transform:rotate(360deg)}}.rsp{transform-box:fill-box;transform-origin:center;animation:rsp 24s linear infinite}"
            "@keyframes live{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(1.6)}}.live{transform-box:fill-box;transform-origin:center;animation:live 1.4s ease-in-out infinite}"
            "@keyframes brd{from{transform:rotate(0)}to{transform:rotate(360deg)}}")
    body = (f'<clipPath id="gc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="28"/></clipPath><g clip-path="url(#gc)"><g mask="url(#sm)"><g transform="scale(1 1.05)">{scn}</g></g></g>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" stroke="{c["line"]}"/>'
            f'<rect class="run" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" stroke="url(#g1)" stroke-width="2.6" pathLength="400"/>'
            f'<circle class="rsp" cx="52" cy="44" r="36" fill="none" stroke="url(#g1)" stroke-width="1.8" stroke-dasharray="4 8" stroke-linecap="round"/>'
            f'<g transform="translate(10 2)">{icon_svg}</g>'
            f'<clipPath id="tx"><path d="{d}"/></clipPath><g class="typ"><path d="{d}" fill="{c["ink"]}"/>'
            f'<g clip-path="url(#tx)"><rect class="shm" x="104" y="14" width="70" height="34" fill="url(#g1)" opacity=".9" transform="skewX(-20)"/></g></g>'
            f'<circle class="live" cx="108" cy="56" r="3.4" fill="{c["green"]}"/><path d="{sd}" fill="{c["muted"]}"/>{chip}')
    return doc(W, H, body, css, defs, text)


TITLES = [("01", "ABOUT ME", "about"), ("02", "TOOLBOX", "toolbox"), ("03", "FEATURED WORK", "work"), ("04", "BY THE NUMBERS", "stats"),
          ("05", "CONTRIBUTION CITY", "city"), ("08", "PLAY A GAME", "play"), ("06", "RIGHT NOW", "activity"), ("07", "LET'S CONNECT", "connect")]


def build():
    for m in MODES:
        for num, text, slug in TITLES:
            write(OUT / "titles" / f"{slug}-{m}.svg", section_title(num, text, m))
        write(OUT / "hero" / f"hello-{m}.svg", hero_hello(m))
        write(OUT / "hero" / f"roles-{m}.svg", hero_roles(m))
        write(OUT / "hero" / f"chips-{m}.svg", hero_chips(m))
        write(OUT / "hero" / f"welcome-{m}.svg", hero_welcome(m))
        write(OUT / "hero" / f"btn-follow-{m}.svg", button("Follow me", "follow", m, True))
        write(OUT / "sections" / f"star-{m}.svg", star_cta(m))
        write(OUT / "sections" / f"arcade-{m}.svg", arcade_card(m))
        write(OUT / "hero" / f"btn-work-{m}.svg", button("My work", "github", m, False))
        write(OUT / "sections" / f"ticker-{m}.svg", ticker(m))
        write(OUT / "sections" / f"divider-{m}.svg", divider(m))
        write(OUT / "sections" / f"divider2-{m}.svg", divider2(m))
        write(OUT / "sections" / f"ticker2-{m}.svg", ticker(m, ["BUILD", "SHIP", "LEARN", "REPEAT", "CREATE", "ITERATE"], True))
        write(OUT / "sections" / f"about-{m}.svg", about(m))
        write(OUT / "contact" / f"email-{m}.svg", contact_pill("Email", "rajdipdharofficial@gmail.com", "gmail", m))
        write(OUT / "contact" / f"github-{m}.svg", contact_pill("GitHub", "@RajdipDhar2007", "github", m))
