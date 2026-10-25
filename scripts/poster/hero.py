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
            f'<circle class="bt" cx="{W / 2}" cy="20" r="5" fill="{c["pink"]}"/>{star4(40, 20, 7, c["accent"], "tw")}{star4(790, 20, 7, c["second"], "tw", "style=" + chr(34) + "animation-delay:-1.2s" + chr(34))}')
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



def _mixhex(a: str, b: str, f: float) -> str:
    x = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    y = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(int(p + (q - p) * f) for p, q in zip(x, y))


def star3d(cx: float, cy: float, ro: float, ri: float, depth: int = 10, cls: str = "") -> str:
    """Faceted golden five-point star with an extruded body (layers fan out via --k when .ex is animated)."""
    import math
    LIGHT, MID, DARK = "#FFF1A6", "#FFC93C", "#B9740A"
    pts = [(cx + (ro if i % 2 == 0 else ri) * math.cos(-math.pi / 2 + i * math.pi / 5), cy + (ro if i % 2 == 0 else ri) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
    outline = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    layers = "".join(f'<g class="ex" style="--k:{n}"><polygon points="{outline}" fill="{_mixhex("#C98A0B", "#6B4300", n / depth)}" stroke="{_mixhex("#C98A0B", "#6B4300", n / depth)}" stroke-width="2" stroke-linejoin="round" transform="translate({n * .5:.1f} {n * 1.1:.1f})"/></g>' for n in range(depth, 0, -1))
    facets = ""
    for k in range(5):                     # outer tip k is point 2k; inner points sit at 2k+1 (right) and 2k-1 (left)
        o, ir, il = pts[2 * k], pts[(2 * k + 1) % 10], pts[(2 * k - 1) % 10]
        for a, b, side in ((il, o, 0), (o, ir, 1)):
            mx, my = (a[0] + b[0]) / 2 - cx, (a[1] + b[1]) / 2 - cy
            ang = math.atan2(my, mx) + (0.55 if side else -0.55)            # face tilt so the two halves of each tip differ
            lit = .5 + .5 * math.cos(ang - math.radians(-130))               # light from the top left
            col = _mixhex(DARK, LIGHT, lit) if lit < .6 else _mixhex(MID, LIGHT, (lit - .6) / .4)
            facets += f'<polygon points="{cx:.1f},{cy:.1f} {a[0]:.1f},{a[1]:.1f} {b[0]:.1f},{b[1]:.1f}" fill="{col}" stroke="{col}" stroke-width=".8" stroke-linejoin="round"/>'
    return (f'<g class="{cls}">{layers}<g class="fr">{facets}<polygon points="{outline}" fill="none" stroke="#FFF8D6" stroke-opacity=".85" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<clipPath id="sc{int(cx)}{int(cy)}"><polygon points="{outline}"/></clipPath><g clip-path="url(#sc{int(cx)}{int(cy)})"><rect class="ssh" x="{cx - ro - 60:.0f}" y="{cy - ro:.0f}" width="26" height="{ro * 2:.0f}" fill="#fff" opacity=".75" transform="skewX(-20)"/></g></g></g>')


def star_cta(mode: str) -> str:
    """Closing call-to-action: a faceted 3D golden star, a hand-lettered ask and a pressable glossy 3D button."""
    import math
    c = PAL[mode]
    W, H, T = 830, 300, 10.0
    sf, bf, hf = typo.font(typo.SCRIPT), typo.font(typo.BODY), typo.font(typo.HEAD)
    cx, cy = 150, 142
    gl = sf.glyphs("Enjoyed the tour?", 52, 300, 104)
    full = "".join(g[0] for g in gl)
    css, draw = "", ""
    for i, (d, _, _) in enumerate(gl):
        t0 = .2 + i * .08
        css += kf(f"d{i}", T, [(0, "stroke-dashoffset:1;opacity:1"), (t0, "stroke-dashoffset:1;opacity:1"), (t0 + .7, "stroke-dashoffset:0;opacity:1"), (T - .7, "stroke-dashoffset:0;opacity:1"), (T - .3, "opacity:0;stroke-dashoffset:0"), (T, "opacity:0")]) + f".d{i}{{animation:d{i} {T}s linear infinite}}"
        draw += f'<path class="d{i}" d="{d}" pathLength="1" fill="none" stroke="url(#g1)" stroke-width="1.6" stroke-dasharray="1" stroke-dashoffset="1"/>'
    css += kf("tf", T, [(0, "opacity:0"), (1.4, "opacity:0"), (2.4, "opacity:1"), (T - .7, "opacity:1"), (T - .3, "opacity:0"), (T, "opacity:0")]) + f".tf{{animation:tf {T}s linear infinite}}"
    lines = bf.wrap("If this profile made you smile, drop a star on this repo. It tells me the work is worth sharing and keeps me building.", 15, 460)
    sub = "".join(f'<path d="{bf.path(l, 15, 300, 146 + k * 23)[0]}" fill="{c["muted"]}"/>' for k, l in enumerate(lines))
    css += kf("sb", T, [(0, "opacity:0;transform:translateY(8px)"), (2.0, "opacity:0;transform:translateY(8px)"), (2.8, "opacity:1;transform:none"), (T - .7, "opacity:1;transform:none"), (T - .3, "opacity:0"), (T, "opacity:0")]) + f".sb{{animation:sb {T}s linear infinite}}"
    # ---- 3D button
    bw, bh, bx, by, dp = 300, 58, 300, 206, 7
    dark = "#0D1117" if mode == "dark" else "#fff"
    lab, lw = sf.path("Star this repo", 25, 0, 0)
    face = f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="29" fill="url(#g1)"/>'
    plate = f'<rect x="{bx}" y="{by + dp}" width="{bw}" height="{bh}" rx="29" fill="url(#g1d)"/>'
    gloss = f'<path d="M{bx + 18} {by + 4} H{bx + bw - 18} A25 25 0 0 1 {bx + bw - 24} {by + 25} H{bx + 24} A25 25 0 0 1 {bx + 18} {by + 4}Z" fill="#fff" opacity=".28"/>'
    mini = star3d(bx + 40, by + bh / 2 + 1, 15, 6.6, 5, "mini")
    chev = "".join(f'<path class="chv" d="M{bx + bw - 54 + k * 12} {by + 19} l8 10 l-8 10" fill="none" stroke="{dark}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" style="animation-delay:{k * .2:.1f}s"/>' for k in range(3))
    button = (f'<ellipse class="clk" cx="{bx + bw / 2}" cy="{by + bh / 2}" rx="{bw / 2}" ry="{bh / 2}" fill="none" stroke="url(#g1)" stroke-width="3"/>'
              f'{plate}<g class="press"><clipPath id="bcl"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="29"/></clipPath>{face}{gloss}'
              f'<g clip-path="url(#bcl)"><rect class="shn" x="{bx - 90}" y="{by}" width="50" height="{bh}" fill="#fff" opacity=".45" transform="skewX(-20)"/></g>'
              f'{mini}<path d="{lab}" transform="translate({bx + 72 + 1} {by + 38.5})" fill="#fff" opacity=".4"/><path d="{lab}" transform="translate({bx + 72} {by + 37})" fill="{dark}"/>{chev}</g>')
    note, nw = sf.path("go on, tap it", 19, 0, 0)
    # hand-drawn arrow: a curve that ends right at the button, with its head turned along the curve's end tangent
    ax1, ay1 = bx + bw + 92, by + 20                      # start: above the note
    ax2, ay2 = bx + bw + 14, by + 22                      # end: touching the button's right edge
    c1, c2 = (ax1 + 6, ay1 - 30), (ax2 + 38, ay2 - 34)
    tdx, tdy = ax2 - c2[0], ay2 - c2[1]
    tn = math.hypot(tdx, tdy)
    ux, uy = tdx / tn, tdy / tn
    head = " ".join(f"{ax2 - 11 * (ux * math.cos(a_) - uy * math.sin(a_)) * 1:.1f} {ay2 - 11 * (ux * math.sin(a_) + uy * math.cos(a_)):.1f}" for a_ in (0.5, -0.5))
    h1, h2 = head.split(" ", 2)[:2], head.split(" ")[2:]
    doodle = (f'<path class="dd" d="M{ax1} {ay1} C{c1[0]} {c1[1]} {c2[0]} {c2[1]} {ax2} {ay2}" fill="none" stroke="{c["pink"]}" stroke-width="2.6" stroke-linecap="round" pathLength="100"/>'
              f'<path class="dd" d="M{h1[0]} {h1[1]} L{ax2} {ay2} L{h2[0]} {h2[1]}" fill="none" stroke="{c["pink"]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" pathLength="100"/>'
              f'<path d="{note}" transform="translate({bx + bw + 44} {by + 50})" fill="{c["muted"]}" class="nt"/>')
    # ---- falling mini stars, orbiting sparkles
    rr = __import__("random").Random(9)
    rain = ""
    for j in range(14):
        x = rr.randint(20, 810)
        r = rr.choice([4, 5, 6, 8])
        k = r * 0.28
        d = f"M{x} {-r} Q{x + k} {-k} {x + r} 0 Q{x + k} {k} {x} {r} Q{x - k} {k} {x - r} 0 Q{x - k} {-k} {x} {-r}Z"
        rain += f'<path class="fall" d="{d}" fill="{[c["accent"], c["second"], c["pink"]][j % 3]}" style="animation-delay:-{rr.uniform(0, 9):.1f}s;animation-duration:{rr.randint(6, 11)}s"/>'
    orbit = f"M{cx - 104} {cy} a104 104 0 1 0 208 0 a104 104 0 1 0 -208 0"
    sparks = "".join(f'<path class="orb" d="M0 -7 Q2 -2 7 0 Q2 2 0 7 Q-2 2 -7 0 Q-2 -2 0 -7Z" fill="{col}" style="offset-path:path({A}{orbit}{A});animation-delay:-{k * 1.5:.1f}s"/>' for k, col in enumerate(["#FFD54A", c["pink"], c["accent"], "#FFF1A6"]))
    css += ("@keyframes fall{0%{transform:translateY(-10px) rotate(0);opacity:0}10%{opacity:.8}100%{transform:translateY(300px) rotate(180deg);opacity:0}}.fall{animation:fall 8s linear infinite}"
            "@keyframes orb{from{offset-distance:0%}to{offset-distance:100%}}.orb{animation:orb 6s linear infinite}"
            "@keyframes sway{0%,100%{transform:rotate(-6deg) scaleX(.93)}50%{transform:rotate(6deg) scaleX(1)}}.sway{transform-box:fill-box;transform-origin:50% 90%;animation:sway 4s ease-in-out infinite}"
            "@keyframes ex{0%,100%{transform:translate(calc(var(--k) * -.55px),0)}50%{transform:translate(calc(var(--k) * .55px),0)}}.ex{animation:ex 4s ease-in-out infinite}"
            "@keyframes ssh{0%,40%{transform:translateX(0)}80%,100%{transform:translateX(230px)}}.ssh{animation:ssh 3.4s ease-in-out infinite}"
            "@keyframes mn{0%,100%{transform:scaleX(1) rotate(-8deg)}50%{transform:scaleX(.8) rotate(8deg)}}.mini{transform-box:fill-box;transform-origin:center;animation:mn 2.4s ease-in-out infinite}"
            "@keyframes glow{0%,100%{opacity:.3;transform:scale(1)}50%{opacity:.7;transform:scale(1.2)}}.glow{transform-box:fill-box;transform-origin:center;animation:glow 2.6s ease-in-out infinite}"
            "@keyframes shd{0%,100%{transform:scale(1);opacity:.35}50%{transform:scale(.8);opacity:.2}}.shd{transform-box:fill-box;transform-origin:center;animation:shd 4s ease-in-out infinite}"
            "@keyframes run{to{stroke-dashoffset:-1000}}.run{stroke-dasharray:180 820;animation:run 6s linear infinite}"
            "@keyframes press{0%,78%,100%{transform:translateY(0)}86%{transform:translateY(" + str(dp - 1) + "px)}93%{transform:translateY(0)}}.press{animation:press 3.2s ease-in-out infinite}"
            "@keyframes clk{0%,84%{transform:scale(1);opacity:0}86%{opacity:.9}100%{transform:scale(1.35,1.9);opacity:0}}.clk{transform-box:fill-box;transform-origin:center;animation:clk 3.2s ease-out infinite}"
            "@keyframes shn{0%{transform:translateX(0)}45%,100%{transform:translateX(420px)}}.shn{animation:shn 3.4s ease-in-out infinite}"
            "@keyframes chv{0%,100%{opacity:.25}35%{opacity:1}}.chv{animation:chv 1.2s ease-in-out infinite}"
            "@keyframes ring{0%{r:50;opacity:.7}100%{r:118;opacity:0}}.ring{animation:ring 2.8s ease-out infinite}"
            "@keyframes dd{0%{stroke-dashoffset:100}40%,85%{stroke-dashoffset:0}100%{stroke-dashoffset:-100}}.dd{stroke-dasharray:100;animation:dd 5s ease-in-out infinite}"
            "@keyframes nt{0%,30%{opacity:0}50%,85%{opacity:1}100%{opacity:0}}.nt{animation:nt 5s ease-in-out infinite}" + _tw())
    body = (f'<clipPath id="pc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="30"/></clipPath>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="30" fill="{c["card"]}" stroke="{c["line"]}"/>'
            f'<g clip-path="url(#pc)"><circle cx="{cx}" cy="{cy}" r="124" fill="url(#rg)" class="glow"/>{rain}</g>'
            f'<rect class="run" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="30" fill="none" stroke="url(#g1)" stroke-width="3" pathLength="1000"/>'
            f'<circle class="ring" cx="{cx}" cy="{cy}" r="50" fill="none" stroke="#FFD54A" stroke-width="2"/>'
            f'<circle class="ring" cx="{cx}" cy="{cy}" r="50" fill="none" stroke="{c["pink"]}" stroke-width="2" style="animation-delay:-1.4s"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="104" ry="104" fill="none" stroke="{c["line"]}" stroke-dasharray="3 6"/>{sparks}'
            f'<ellipse class="shd" cx="{cx}" cy="{cy + 98}" rx="62" ry="9" fill="#000"/>'
            f'<g class="sway">{star3d(cx, cy, 78, 34)}</g>'
            f'<g class="tf" fill="url(#g1)"><path d="{full}"/></g>{draw}<g class="sb">{sub}</g>{button}{doodle}'
            f'{star4(bx - 14, by - 10, 6, c["accent"], "tw")}{star4(bx + bw + 6, by + bh + 2, 5, c["pink"], "tw", "style=" + chr(34) + "animation-delay:-1.3s" + chr(34))}')
    dk = lambda col: _mixhex(col, "#000000", .45)
    defs = (_grad(c, "g1") + lin_grad("g1d", [(0, dk(c["accent"])), (.55, dk(c["second"])), (1, dk(c["pink"]))], 0, 0, 1, 0)
            + f'<radialGradient id="rg"><stop offset="0" stop-color="#FFC93C" stop-opacity=".5"/><stop offset="1" stop-color="#FFC93C" stop-opacity="0"/></radialGradient>')
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

    # ---- a scripted fight that follows the real game's rules: bullets kill bugs, kills drop pickups (H shield, R rapid fire),
    #      the rocket catches them and the effect shows on the rocket (shield ring, doubled fire rate, HUD chips, combo, score)
    import math as _m
    T, SHIP_T, VB, V = 13.2, 4.4, 209.0, 48.0                 # loop, ship sweep, bullet speed, bug speed (px/s)
    cxf, Y0, YTOP = fx + fw / 2, fy + fh - 52, fy - 14
    SHIP_Y = fy + fh - 22

    def shipx(t):
        return cxf - 70 * _m.cos(2 * _m.pi * t / SHIP_T)

    def P(t):
        return f"{max(0.0, min(100.0, t / T * 100)):.3f}%"
    plan = [(5, 80, c["green"]), (14, 125, c["pink"]), (24, 95, c["second"]), (33, 140, c["green"]), (43, 85, c["pink"]), (52, 118, c["second"])]
    DROPS = {1: "H", 3: "R"}                                  # which kills drop a pickup

    def fight_for(fires):
        out = []
        for n, yh, col in plan:
            bxp = shipx(n * .22)
            s0 = n * .22 + (Y0 - (yh + 10)) / VB - (yh - YTOP) / V
            best = None
            for m_, tf in enumerate(fires):                   # the first bullet that really meets this bug
                if abs(shipx(tf) - bxp) > 13:
                    continue
                t = (Y0 - YTOP - 10 + VB * tf + V * s0) / (VB + V)
                if t >= max(tf, s0) and t < T and (best is None or t < best[0]):
                    best = (t, m_)
            tc, m_ = best
            out.append(dict(x=bxp, s=s0, tc=tc, yc=YTOP + V * (tc - s0), m=m_, col=col))
        return out

    def arrival(xb, tc, yc):
        """First time after the drop starts falling when the ship is under x = xb (pickups fall at 55 to 110 px/s)."""
        u = max(-1.0, min(1.0, -(xb - cxf) / 70))
        base = _m.acos(u) * SHIP_T / (2 * _m.pi)
        need = (SHIP_Y - 6 - yc) / 110
        for t in sorted(t for k in range(0, 5) for t in (base + SHIP_T * k, -base + SHIP_T * k)):
            if t >= tc + need:
                return t

    fires = [n * .22 for n in range(60)]
    fight = fight_for(fires)
    arr = {i: arrival(fight[i]["x"], fight[i]["tc"], fight[i]["yc"]) for i in DROPS}
    t_rapid = arr[[i for i, k in DROPS.items() if k == "R"][0]]
    fires = sorted(fires + [n * .22 + .11 for n in range(60) if n * .22 + .11 >= t_rapid and n * .22 + .11 < T - .3])   # rapid fire = twice the shots
    fight = fight_for(fires)
    arr = {i: arrival(fight[i]["x"], fight[i]["tc"], fight[i]["yc"]) for i in DROPS}
    WIN = {"H": 4.4, "R": 3.4}
    fcss, bugs, booms, pickups, ship_fx, hud_fx = "", "", "", "", "", ""
    for i, f_ in enumerate(fight):
        x_, y_, s0, tc, col = f_["x"], f_["yc"], f_["s"], f_["tc"], f_["col"]
        fcss += (f"@keyframes bg{i}{{0%,{P(s0)}{{opacity:0;transform:translate({x_:.1f}px,{YTOP}px)}}{P(s0 + .03)}{{opacity:1;transform:translate({x_:.1f}px,{YTOP}px)}}"
                 f"{P(tc)}{{opacity:1;transform:translate({x_:.1f}px,{y_:.1f}px)}}{P(tc + .03)},100%{{opacity:0;transform:translate({x_:.1f}px,{y_:.1f}px)}}}}.bg{i}{{opacity:0;animation:bg{i} {T}s linear infinite}}")
        fcss += (f"@keyframes bm{i}{{0%,{P(tc)}{{r:3;opacity:0}}{P(tc + .03)}{{r:3;opacity:1}}{P(tc + .55)},100%{{r:30;opacity:0}}}}.bm{i}{{opacity:0;animation:bm{i} {T}s ease-out infinite}}"
                 f"@keyframes sd{i}{{0%,{P(tc)}{{opacity:0;transform:translate(0,0)}}{P(tc + .03)}{{opacity:1;transform:translate(0,0)}}{P(tc + .5)},100%{{opacity:0;transform:translate(var(--dx),var(--dy))}}}}.sd{i}{{opacity:0;animation:sd{i} {T}s ease-out infinite}}"
                 f"@keyframes pt{i}{{0%,{P(tc)}{{opacity:0;transform:translateY(0)}}{P(tc + .05)}{{opacity:1;transform:translateY(0)}}{P(tc + .9)},100%{{opacity:0;transform:translateY(-26px)}}}}.pt{i}{{opacity:0;animation:pt{i} {T}s ease-out infinite}}")
        bugs += (f'<g class="bg{i}"><g class="wob" style="animation-delay:-{i * .13:.2f}s"><ellipse cx="0" cy="2" rx="11" ry="13" fill="{c["card"]}" stroke="{col}" stroke-width="2"/>'
                 f'<path d="M-11 -4 l-7 -3 M-11 3 l-8 1 M-11 9 l-7 5 M11 -4 l7 -3 M11 3 l8 1 M11 9 l7 5 M-3 -13 l-4 -7 M3 -13 l4 -7" stroke="{col}" stroke-width="2" stroke-linecap="round"/>'
                 f'<circle cx="-4" cy="-4" r="2.4" fill="#fff"/><circle cx="4" cy="-4" r="2.4" fill="#fff"/></g></g>')
        shards = "".join(f'<circle class="sd{i}" cx="{x_:.1f}" cy="{y_:.1f}" r="2.4" fill="{[col, c["accent"], "#fff"][k % 3]}" style="--dx:{22 * _m.cos(k * _m.pi / 3):.0f}px;--dy:{22 * _m.sin(k * _m.pi / 3):.0f}px"/>' for k in range(6))
        booms += (f'<circle class="bm{i}" cx="{x_:.1f}" cy="{y_:.1f}" r="3" fill="none" stroke="{col}" stroke-width="3"/>{shards}'
                  f'<path class="pt{i}" d="{mf.path("+100", 11, x_ - 14, y_ - 10, 1)[0]}" fill="{c["pink"]}"/>')
        if i in DROPS:                                                # the kill drops a pickup that the rocket catches
            kind, ta = DROPS[i], arr[i]
            pc = c["green"] if kind == "H" else c["accent"]
            fcss += (f"@keyframes pk{i}{{0%,{P(tc + .05)}{{opacity:0;transform:translate({x_:.1f}px,{y_:.1f}px)}}{P(tc + .12)}{{opacity:1;transform:translate({x_:.1f}px,{y_:.1f}px)}}"
                     f"{P(ta)}{{opacity:1;transform:translate({x_:.1f}px,{SHIP_Y - 6}px)}}{P(ta + .03)},100%{{opacity:0;transform:translate({x_:.1f}px,{SHIP_Y - 6}px)}}}}.pk{i}{{opacity:0;animation:pk{i} {T}s linear infinite}}")
            pickups += (f'<g class="pk{i}"><circle class="pwh" r="14" fill="{pc}"/><circle class="pwsp" r="13" fill="none" stroke="{pc}" stroke-width="2" stroke-dasharray="4 5" stroke-linecap="round"/>'
                        f'<circle r="10" fill="{c["card"]}" stroke="{pc}" stroke-width="2"/><path d="{mf.path(kind, 11, -3.6, 4)[0]}" fill="{pc}"/></g>')
            word = "SHIELD" if kind == "H" else "RAPID FIRE"
            wd, ww = mf.path(word, 9, 0, 0, 1)
            tx = max(fx + 8, min(fx + fw - 8 - ww, x_ - ww / 2))
            fcss += (f"@keyframes ft{i}{{0%,{P(ta)}{{opacity:0;transform:translateY(0)}}{P(ta + .05)}{{opacity:1;transform:translateY(0)}}{P(ta + 1.1)},100%{{opacity:0;transform:translateY(-30px)}}}}.ft{i}{{opacity:0;animation:ft{i} {T}s ease-out infinite}}"
                     f"@keyframes cb{i}{{0%,{P(ta)}{{r:6;opacity:0}}{P(ta + .03)}{{r:6;opacity:1}}{P(ta + .5)},100%{{r:38;opacity:0}}}}.cb{i}{{opacity:0;animation:cb{i} {T}s ease-out infinite}}"
                     f"@keyframes fx{kind}{{0%,{P(ta)}{{opacity:0}}{P(ta + .08)}{{opacity:1}}{P(min(ta + WIN[kind], T - .05) - .15)}{{opacity:1}}{P(min(ta + WIN[kind], T - .05))},100%{{opacity:0}}}}.fx{kind}{{opacity:0;animation:fx{kind} {T}s linear infinite}}"
                     f"@keyframes tm{kind}{{0%,{P(ta)}{{opacity:0;transform:scaleX(1)}}{P(ta + .05)}{{opacity:1;transform:scaleX(1)}}{P(min(ta + WIN[kind], T - .05))}{{opacity:1;transform:scaleX(0)}}{P(min(ta + WIN[kind], T - .05) + .01)},100%{{opacity:0;transform:scaleX(0)}}}}.tm{kind}{{opacity:0;transform-box:fill-box;transform-origin:left;animation:tm{kind} {T}s linear infinite}}")
            booms += f'<g class="ft{i}"><path d="{wd}" transform="translate({tx:.1f} {SHIP_Y - 26})" fill="{pc}"/></g>'
            ship_fx += f'<circle class="cb{i}" cx="0" cy="0" r="6" fill="none" stroke="{pc}" stroke-width="3"/>'
            if kind == "H":
                ship_fx += f'<g class="fxH"><circle class="shr" r="27" fill="{c["green"]}" fill-opacity=".12" stroke="{c["green"]}" stroke-width="2.4"/></g>'
            else:
                ship_fx += (f'<g class="fxR"><circle class="pwsp" r="21" fill="none" stroke="{c["accent"]}" stroke-width="2" stroke-dasharray="3 5" stroke-linecap="round"/>'
                            f'<path class="fl" d="M-6 9 Q-9 30 -3 9Z M6 9 Q9 30 3 9Z" fill="{c["accent"]}"/></g>')
            cxh = fx + 12 + (0 if kind == "H" else 40)
            hud_fx += (f'<g class="fx{kind}"><rect x="{cxh}" y="{fy + 30}" width="34" height="16" rx="8" fill="none" stroke="{pc}" stroke-width="1.6"/>'
                       f'<path d="{mf.path(kind, 9, cxh + 5, fy + 42, 0)[0]}" fill="{pc}"/><rect class="tm{kind}" x="{cxh + 16}" y="{fy + 36}" width="14" height="4" rx="2" fill="{pc}"/></g>')
    bullets = ""
    hit = {f_["m"]: f_["tc"] for f_ in fight}
    for m_, tf in enumerate(fires):
        if m_ in hit:
            dt_ = hit[m_] - tf
            fcss += (f"@keyframes bh{m_}{{0%{{opacity:0;transform:translateY(0)}}.01%{{opacity:1;transform:translateY(0)}}{P(dt_)}{{opacity:1;transform:translateY({-VB * dt_:.1f}px)}}{P(dt_ + .02)},100%{{opacity:0;transform:translateY({-VB * dt_:.1f}px)}}}}"
                     f".bh{m_}{{opacity:0;animation:bh{m_} {T}s linear infinite both}}")
            cls = f"bh{m_}"
        else:
            cls = "bl"
        bullets += f'<rect class="{cls}" x="{shipx(tf) - 2:.1f}" y="{Y0}" width="4" height="14" rx="2" fill="{c["accent"]}" style="animation-delay:{tf:.2f}s"/>'
    fcss += (f"@keyframes bl{{0%{{opacity:0;transform:translateY(0)}}.01%{{opacity:1;transform:translateY(0)}}{P(1.06)}{{opacity:.25;transform:translateY(-222px)}}{P(1.08)},100%{{opacity:0;transform:translateY(-222px)}}}}"
             f".bl{{opacity:0;animation:bl {T}s linear infinite both}}"
             "@keyframes shr{0%,100%{opacity:.7;transform:scale(1)}50%{opacity:1;transform:scale(1.07)}}.shr{animation:shr .5s ease-in-out infinite}")
    # score counts up with every kill; combo shows when kills come quickly (as in the game)
    order = sorted(f_["tc"] for f_ in fight)
    marks = [0.0] + order + [T]
    hud = ""
    for k in range(len(marks) - 1):
        t0, t1 = marks[k], marks[k + 1]
        fcss += (f"@keyframes sc{k}{{0%,{P(t0)}{{opacity:{1 if k == 0 else 0}}}{P(t0 + .001)}{{opacity:1}}{P(t1)}{{opacity:1}}{P(t1 + .001)},100%{{opacity:0}}}}"
                 f".sc{k}{{opacity:{1 if k == 0 else 0};animation:sc{k} {T}s linear infinite}}")
        hud += f'<path class="sc{k}" d="{mf.path(f"SCORE {4200 + 100 * k:06d}", 10, fx + 12, fy + 20, 1)[0]}" fill="{c["accent"]}"/>'
    combo = 0
    for k, tk in enumerate(order):
        combo = combo + 1 if k and tk - order[k - 1] < 1.7 else 1
        if combo >= 2:
            end = order[k + 1] if k + 1 < len(order) and order[k + 1] - tk < 1.7 else tk + 1.7
            fcss += (f"@keyframes cm{k}{{0%,{P(tk)}{{opacity:0}}{P(tk + .001)}{{opacity:1}}{P(end)}{{opacity:1}}{P(end + .001)},100%{{opacity:0}}}}.cm{k}{{opacity:0;animation:cm{k} {T}s linear infinite}}")
            hud += f'<path class="cm{k}" d="{mf.path(f"COMBO x{combo}", 10, fx + fw - 12 - mf.width(f"COMBO x{combo}", 10, 1), fy + 38, 1)[0]}" fill="{c["gold"] if "gold" in c else "#FBBF24"}"/>'
    hud += f'<path d="{mf.path("WAVE 3", 10, fx + fw - 62, fy + 20, 1)[0]}" fill="{c["muted"]}"/>'
    hud += "".join(f'<path d="M{fx + fw - 18 - i * 14} {fy + 54} l4 -10 l4 10 l-4 -3z" fill="{c["pink"]}"/>' for i in range(3)) + hud_fx
    ship = (f'<g transform="translate({cxf} {SHIP_Y})"><g class="sh">{ship_fx}<path d="M0 -16 L11 12 L0 6 L-11 12Z" fill="url(#g1)"/>'
            f'<path class="fl" d="M-3 9 Q0 24 3 9Z" fill="{c["pink"]}"/></g></g>')
    # ---- right side copy
    title, tw = sf.path("Bug Hunter", 64, 330, 98)
    sub, _ = mf.path("A  PLAYABLE  ARCADE  SHOOTER", 12, 332, 126, 3)
    pitch = bf.wrap("Squash bugs, dodge their fire and take on the SEGFAULT boss. Combos, bonus drops and a rank for every score.", 15, 450)
    pd = "".join(f'<path d="{bf.path(l, 15, 332, 160 + k * 23)[0]}" fill="{c["muted"]}"/>' for k, l in enumerate(pitch))
    bx, by, bw, bh = 332, 244, 214, 52
    play, _ = hf.path("PLAY NOW", 17, bx + 66, by + 33, 1)
    tri = f"M{bx + 30} {by + 16} L{bx + 30} {by + 36} L{bx + 46} {by + 26}Z"
    dark = "#0D1117" if mode == "dark" else "#fff"
    # rotating motivational lines in a charging "power-up" card
    qx, qy, qw_, qh_ = bx + bw + 20, by - 8, 236, 64
    slot = 3.6
    quotes = ["Debug today, ship tomorrow.", "Small steps still ship big things.", "Every bug is a lesson in disguise.", "Press start on your next idea.",
              "Code it. Break it. Fix it. Level up.", "Be the boss you are trying to beat.", "Progress beats perfect, every run.", "Stay curious. Keep shipping."]
    qparts = ""
    for k, qt in enumerate(quotes):
        size = 15.0
        while True:
            ql = sf.wrap(qt, size, 178)
            if len(ql) <= 2 or size <= 11:
                break
            size -= 1
        qd = "".join(f'<path d="{sf.path(l, size, qx + 52, qy + 36 + j * 18 - (9 if len(ql) == 2 else 0))[0]}" fill="url(#g1)"/>' for j, l in enumerate(ql[:2]))
        qparts += f'<g class="q q{k}" style="animation-delay:{k * slot:.1f}s">{qd}</g>'
    bolt = "M4 -13 L-6 2 H-1 L-4 13 L7 -3 H1Z"
    quote = (f'<rect x="{qx}" y="{qy}" width="{qw_}" height="{qh_}" rx="18" fill="{c["card"]}" fill-opacity=".6" stroke="{c["line"]}"/>'
             f'<rect class="qrun" x="{qx}" y="{qy}" width="{qw_}" height="{qh_}" rx="18" fill="none" stroke="url(#g1)" stroke-width="2" pathLength="400"/>'
             f'<circle class="qrip" cx="{qx + 28}" cy="{qy + qh_ / 2}" r="14" fill="none" stroke="{c["accent"]}" stroke-width="2"/>'
             f'<circle class="qrip" cx="{qx + 28}" cy="{qy + qh_ / 2}" r="14" fill="none" stroke="{c["pink"]}" stroke-width="2" style="animation-delay:-.9s"/>'
             f'<circle cx="{qx + 28}" cy="{qy + qh_ / 2}" r="17" fill="{c["card"]}" stroke="url(#g1)" stroke-width="2"/>'
             f'<g transform="translate({qx + 28} {qy + qh_ / 2})"><g class="qbolt"><path d="{bolt}" fill="url(#g1)" stroke="url(#g1)" stroke-width="1.4" stroke-linejoin="round"/></g></g>'
             f'{qparts}'
             f'<rect x="{qx + 52}" y="{qy + qh_ - 11}" width="170" height="3" rx="1.5" fill="{c["line"]}"/>'
             f'<rect class="qchg" x="{qx + 52}" y="{qy + qh_ - 11}" width="170" height="3" rx="1.5" fill="url(#g1)"/>'
             f'{star4(qx + qw_ - 14, qy + 12, 5, c["pink"], "tw")}')
    chips, x = "", 332
    for k, lab in enumerate(["BOSS FIGHTS", "HIGH SCORES", "COMBOS", "MOBILE READY"]):
        cw = mf.width(lab, 10, 1) + 22
        chips += f'<rect x="{x}" y="200" width="{cw:.0f}" height="24" rx="12" fill="none" stroke="{[c["accent"], c["second"], c["pink"], c["green"]][k]}" stroke-width="1.6"/><path d="{mf.path(lab, 10, x + 11, 216, 1)[0]}" fill="{c["ink"]}"/>'
        x += cw + 8
    scan = "".join(f'<rect x="{fx}" y="{fy + k * 6}" width="{fw}" height="1" fill="#000" opacity=".16"/>' for k in range(fh // 6))
    pw = pickups
    css = fcss + ("@keyframes wob{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(7deg)}}.wob{transform-box:fill-box;transform-origin:center;animation:wob .5s ease-in-out infinite}"
           "@keyframes pwr{from{transform:translate(0,0)}to{transform:translate(-40px,300px)}}.pwr{animation:pwr 9s linear infinite;animation-delay:-3s}"
           "@keyframes pop{0%,100%{opacity:0;transform:translateY(0)}10%{opacity:1}40%{opacity:0;transform:translateY(-22px)}}.pop{animation:pop 3.4s ease-out infinite}"
           "@keyframes qin{0%{opacity:0;transform:translateY(14px);clip-path:inset(0 100% 0 0)}2%{opacity:1}6%{opacity:1;transform:translateY(0);clip-path:inset(-4px 0 -4px 0)}11%{opacity:1;transform:translateY(0);clip-path:inset(-4px 0 -4px 0)}12.5%,100%{opacity:0;transform:translateY(-14px);clip-path:inset(-4px 0 -4px 0)}}"
           ".q{opacity:0;animation:qin 28.8s ease-out infinite both}.q0{opacity:1}"
           "@keyframes qlab{0%,100%{opacity:1}50%{opacity:.45}}.qlab{animation:qlab 1.4s ease-in-out infinite}"
           "@keyframes qrun{to{stroke-dashoffset:-400}}.qrun{stroke-dasharray:70 330;animation:qrun 4s linear infinite}"
           "@keyframes qrip{0%{r:17;opacity:.8}100%{r:30;opacity:0}}.qrip{animation:qrip 1.8s ease-out infinite}"
           "@keyframes qbolt{0%,100%{transform:scale(1) rotate(0)}50%{transform:scale(1.25) rotate(-8deg)}}.qbolt{animation:qbolt 1.1s ease-in-out infinite}"
           "@keyframes qchg{0%{transform:scaleX(0)}90%,100%{transform:scaleX(1)}}.qchg{transform-box:fill-box;transform-origin:left;animation:qchg 3.6s linear infinite}"
           "@keyframes pwh{0%,100%{opacity:.3;transform:scale(1)}50%{opacity:.8;transform:scale(1.5)}}.pwh{transform-box:fill-box;transform-origin:center;animation:pwh 1s ease-in-out infinite}"
           "@keyframes pwsp{to{transform:rotate(360deg)}}.pwsp{transform-box:fill-box;transform-origin:center;animation:pwsp 2.4s linear infinite}"
           "@keyframes qbar{0%,100%{opacity:.5}50%{opacity:1}}.qb{animation:qbar 1.8s ease-in-out infinite}"
           "@keyframes crt{from{transform:translateY(0)}to{transform:translateY(6px)}}.crt{animation:crt .5s linear infinite}"
           "@keyframes sh{" + "".join(f"{k * 2.5:g}%{{transform:translateX({-70 * _m.cos(2 * _m.pi * k / 40):.1f}px)}}" for k in range(41)) + "}.sh{animation:sh 4.4s linear infinite}"
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
            f'<g clip-path="url(#pf)">{stars}{bugs}{booms}{bullets}{pw}{ship}<g class="crt">{scan}</g>{hud}</g>'
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
        icon_svg = (f'<mask id="mm"><rect x="0" y="0" width="84" height="84" fill="#fff"/><circle cx="53" cy="35" r="17" fill="#000"/></mask>'
                    f'<g class="bobi"><circle cx="40" cy="44" r="20" fill="{c["second"]}" mask="url(#mm)"/></g>'
                    f'{star4(62, 54, 5, c["accent"], "tw")}{star4(58, 22, 4, c["pink"], "tw", "style=" + chr(34) + "animation-delay:-1s" + chr(34))}')
        scn = "".join(f'<circle class="tws" cx="{rr.randint(520, 800)}" cy="{rr.randint(10, 72)}" r="{rr.choice([1, 1.4, 2])}" fill="{c["ink"]}" style="animation-delay:-{rr.uniform(0, 3):.1f}s"/>' for _ in range(26))
        scn += f'<line class="gsl" x1="560" y1="14" x2="500" y2="-6" stroke="{c["accent"]}" stroke-width="2" stroke-linecap="round"/>'
    elif scene == "evening":  # a dusk porthole (sun sinking into the sea, all clipped to the disc), soft sunset glow, birds, fireflies
        defs += (f'<linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["second"]}"/><stop offset=".55" stop-color="{c["pink"]}"/><stop offset="1" stop-color="{warm}"/></linearGradient>'
                 f'<radialGradient id="sunh"><stop offset="0" stop-color="{warm}" stop-opacity=".9"/><stop offset="1" stop-color="{warm}" stop-opacity="0"/></radialGradient>'
                 f'<radialGradient id="skyg"><stop offset="0" stop-color="{warm}" stop-opacity=".34"/><stop offset=".55" stop-color="{c["pink"]}" stop-opacity=".12"/><stop offset="1" stop-color="{c["pink"]}" stop-opacity="0"/></radialGradient>'
                 f'<clipPath id="orb"><circle cx="42" cy="42" r="31"/></clipPath>')
        sea = "#1B1035" if mode == "dark" else "#5B2A86"
        icon_svg = (f'<g clip-path="url(#orb)"><rect x="8" y="8" width="68" height="68" fill="url(#dusk)"/>'
                    f'{star4(26, 22, 3.5, "#fff", "tw")}{star4(58, 18, 3, "#fff", "tw", "style=" + chr(34) + "animation-delay:-1.1s" + chr(34))}'
                    f'<g class="bobi"><circle class="hal" cx="42" cy="50" r="24" fill="url(#sunh)"/><circle cx="42" cy="50" r="12" fill="#FFE9B8"/><circle cx="42" cy="50" r="12" fill="{warm}" opacity=".35"/></g>'
                    f'<path d="M8 54 Q16 51 24 54 T40 54 T56 54 T76 54 V80 H8Z" fill="{sea}" opacity=".92"/>'
                    f'<g class="bobi"><path d="M31 59 h22 M35 64 h14 M38 69 h8" stroke="{warm}" stroke-width="2.4" stroke-linecap="round" opacity=".8"/></g></g>'
                    f'<circle cx="42" cy="42" r="31" fill="none" stroke="url(#g1)" stroke-width="2"/>')
        scn = (f'<ellipse cx="770" cy="104" rx="360" ry="86" fill="url(#skyg)"/><ellipse cx="610" cy="108" rx="230" ry="60" fill="url(#skyg)" opacity=".8"/>'
               + "".join(f'<g class="bird" style="animation-delay:-{k * 5.3:.1f}s;animation-duration:{14 + k * 3}s"><path class="flap" d="M470 {24 + k * 14} q6 -7 12 0 q6 -7 12 0" fill="none" stroke="{c["ink"]}" stroke-opacity=".45" stroke-width="1.8" stroke-linecap="round" style="animation-delay:-{k * .3:.1f}s"/></g>' for k in range(3))
               + "".join(f'<circle class="fly" cx="{rr.randint(560, 810)}" cy="{rr.randint(40, 74)}" r="{rr.choice([1.4, 1.9, 2.4])}" fill="{warm}" style="animation-delay:-{rr.uniform(0, 3.6):.1f}s"/>' for _ in range(14)))
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
        write(OUT / "contact" / f"linkedin-{m}.svg", contact_pill("LinkedIn", "rajdip-dhar", "linkedin", m))
