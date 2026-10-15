"""Hero column, section titles, ticker, about cards, contact pills, live greeting."""
from __future__ import annotations
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
    c = PAL[mode]
    W, H, T = 830, 118, 9.0
    f = typo.font(typo.DISPLAY)
    size = 46
    tw = f.width(text, size, 1)
    x0 = (W - tw) / 2
    gl = f.glyphs(text, size, x0, 84, 1)
    css, letters = "", ""
    for i, (d, _, _) in enumerate(gl):
        t0 = 0.15 + i * 0.05
        css += kf(f"l{i}", T, [(0, "opacity:0;transform:translateY(26px)"), (t0, "opacity:0;transform:translateY(26px)"), (t0 + .5, "opacity:1;transform:translateY(0)"),
                               (T - .7, "opacity:1;transform:translateY(0)"), (T - .25, "opacity:0;transform:translateY(-10px)"), (T, "opacity:0")]) + f".l{i}{{animation:l{i} {T}s cubic-bezier(.2,.9,.25,1.1) infinite}}"
        letters += f'<path class="l{i}" d="{d}" fill="url(#g1)"/>'
    mf = typo.font(typo.MONO_B)
    kd, kw = mf.path(f"{num}  //  PORTFOLIO", 13, 0, 0, 3)
    css += kf("k", T, [(0, "opacity:0"), (.1, "opacity:0"), (.8, "opacity:1"), (T - .7, "opacity:1"), (T - .25, "opacity:0"), (T, "opacity:0")]) + f".k{{animation:k {T}s linear infinite}}"
    css += kf("ln", T, [(0, "transform:scaleX(0)"), (.5, "transform:scaleX(0)"), (1.6, "transform:scaleX(1)"), (T - .7, "transform:scaleX(1)"), (T - .25, "transform:scaleX(1);opacity:0"), (T, "transform:scaleX(0);opacity:0")]) + f".ln{{transform-box:fill-box;transform-origin:center;animation:ln {T}s cubic-bezier(.3,.8,.2,1) infinite}}"
    css += f"@keyframes dot{{0%{{transform:translateX(0)}}100%{{transform:translateX({tw - 6:.0f}px)}}}}.dot{{animation:dot 3.2s ease-in-out infinite alternate}}"
    css += _tw()
    body = (f'<path class="k" d="{kd}" transform="translate({(W - kw) / 2:.0f} 30)" fill="{c["accent"]}"/>'
            f'{star4((W - kw) / 2 - 22, 25, 7, c["accent"], "tw")}{star4((W + kw) / 2 + 22, 25, 7, c["second"], "tw", "style=\"animation-delay:-1.2s\"")}'
            f'{letters}<g class="ln"><rect x="{x0:.0f}" y="102" width="{tw:.0f}" height="3" rx="1.5" fill="url(#g1)" opacity=".85"/>'
            f'<circle class="dot" cx="{x0 + 3:.0f}" cy="103.5" r="5" fill="{c["ink"]}"/></g>')
    return doc(W, H, body, css, _grad(c, "g1", 0, 1), f"{text.title()} section title")


# ------------------------------------------------------------------ ticker
def ticker(mode: str) -> str:
    c = PAL[mode]
    W, H, DUR = 830, 56, 26
    f = typo.font(typo.HEAD)
    words = ["FULL-STACK", "ANDROID", "GAME DEV", "WEB3", "AI / LLM", "AUTOMATION"]
    x, parts = 0.0, ""
    for i, w in enumerate(words):
        d, wd = f.path(w, 19, x, 36, 3)
        parts += f'<path d="{d}" fill="{c["ink"] if i % 2 == 0 else c["muted"]}"/>'
        x += wd + 26
        parts += star4(x, 29, 8, [c["accent"], c["second"], c["pink"]][i % 3])
        x += 30
    seq = parts
    shift = x
    css = f"@keyframes tk{{from{{transform:translateX(0)}}to{{transform:translateX(-{shift:.0f}px)}}}}.tk{{animation:tk {DUR}s linear infinite}}"
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
    defs = (_grad(c, "g1") + f'<clipPath id="cl"><path d="{full}"/></clipPath>'
            + '<linearGradient id="sg"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    body = (f'<path class="hi" d="{hi}" fill="{c["accent"]}"/>{letters}'
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
    ix = 22 if icon_name else 0
    total = w + (28 if icon_name else 0)
    x0 = (W - total) / 2
    fg = "#0D1117" if (primary and mode == "dark") else ("#FFFFFF" if primary else c["ink"])
    fill = 'url(#g1)' if primary else c["card"]
    ic = icon(icon_name, x0, 15, 22, fg) if icon_name else ""
    css = (kf("sw", T, [(0, "transform:translateX(0)"), (1.6, "transform:translateX(0)"), (2.6, "transform:translateX(280px)"), (T, "transform:translateX(280px)")]) + f".sw{{animation:sw {T}s linear infinite}}"
           "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}.bb{animation:bob 3.2s ease-in-out infinite}")
    body = (f'<g class="bb"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26" fill="{fill}" stroke="url(#g1)" stroke-width="2"/>'
            f'<clipPath id="bc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26"/></clipPath><g clip-path="url(#bc)"><rect class="sw" x="-100" y="0" width="60" height="{H}" fill="#fff" opacity=".35" transform="skewX(-20)"/></g>'
            f'{ic}<path d="{d}" transform="translate({x0 + (28 if icon_name else 0):.1f} 32)" fill="{fg}"/></g>')
    return doc(W, H, body, css, _grad(c, "g1"), label, pad_y=8)


# ------------------------------------------------------------------ about cards
def about(mode: str) -> str:
    c = PAL[mode]
    W, H, T = 830, 300, 10.0
    cards = [("EDUCATION", "B.Tech CSE", "Heritage Institute of Technology, Kolkata · 2026–2030", c["accent"]),
             ("FOCUS", "Build things", "Full-stack · Android · Game dev · Web3", c["second"]),
             ("EXPLORING", "AI & automation", "LLM-powered apps and workflows that save time", c["pink"]),
             ("LOOKING FOR", "Internships", "…and people to build cool things with", c["green"])]
    tf, bf, mf = typo.font(typo.DISPLAY), typo.font(typo.BODY), typo.font(typo.MONO_B)
    body, css = "", ("@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}.cb{animation:bob 5s ease-in-out infinite}"
                     "@keyframes run{to{stroke-dashoffset:-400}}.run{stroke-dasharray:90 310;animation:run 6s linear infinite}")
    for i, (lab, title, desc, col) in enumerate(cards):
        x = i * 213
        ld, _ = mf.path(lab, 11.5, x + 20, 50, 2)
        td, _ = tf.path(title, 21, x + 20, 92)
        lines = bf.wrap(desc, 13.5, 150)
        dd = "".join(f'<path d="{bf.path(l, 13.5, x + 20, 122 + k * 21)[0]}" fill="{c["muted"]}"/>' for k, l in enumerate(lines))
        body += (f'<g class="cb" style="animation-delay:-{i * 1.1:.1f}s"><rect x="{x + .5}" y="14.5" width="190" height="178" rx="22" fill="{c["card"]}" stroke="{c["line"]}"/>'
                 f'<rect class="run" x="{x + .5}" y="14.5" width="190" height="178" rx="22" fill="none" stroke="{col}" stroke-width="2.4" pathLength="400" style="animation-delay:-{i * 1.5}s"/>'
                 f'<circle cx="{x + 168}" cy="40" r="5" fill="{col}" opacity=".9"/><path d="{ld}" fill="{col}"/><path d="{td}" fill="{c["ink"]}"/>{dd}</g>')
    ff = typo.font(typo.HEAD)
    fd, _ = ff.path("Fun fact:", 15, 0, 0)
    fact = "this README is generated code. The portrait is made of text and every banner is hand-built SVG."
    lines = bf.wrap(fact, 15, 650)
    fy = 250
    ftxt = "".join(f'<path d="{bf.path(l, 15, 112, fy + k * 22)[0]}" fill="{c["ink"]}"/>' for k, l in enumerate(lines))
    body += (f'<g class="cb" style="animation-delay:-2s"><rect x=".5" y="214.5" width="829" height="74" rx="20" fill="{c["card"]}" stroke="{c["line"]}"/>'
             f'<path d="{ff.path("Fun fact:", 15, 28, fy)[0]}" fill="{c["accent"]}"/>{ftxt}</g>')
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
           "@keyframes run{to{stroke-dashoffset:-300}}.run{stroke-dasharray:70 230;animation:run 3.5s linear infinite}")
    body = (f'<clipPath id="bc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22"/></clipPath><g class="bb">'
            f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="{c["card"]}" stroke="{c["line"]}" stroke-width="1.5"/>'
            f'<rect class="run" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="url(#g1)" stroke-width="2.6" pathLength="300"/>'
            f'<g clip-path="url(#bc)"><rect class="sw" x="-90" y="0" width="50" height="{H}" fill="{c["accent"]}" opacity=".18" transform="skewX(-20)"/></g>'
            f'<circle cx="34" cy="34" r="20" fill="url(#g1)" opacity=".18"/>{icon(icon_name, 22, 22, 24, c["accent"])}'
            f'<path d="{ld}" fill="{c["ink"]}"/><path d="{sd}" fill="{c["muted"]}"/></g>')
    return doc(W, H, body, css, _grad(c, "g1"), f"{label}: {sub}", pad_y=8)


# ------------------------------------------------------------------ live greeting
def greeting_svg(mode: str, text: str, stamp: str, night: bool) -> str:
    c = PAL[mode]
    W, H = 830, 84
    hf, bf = typo.font(typo.HEAD), typo.font(typo.MONO)
    d, w = hf.path(text, 19, 84, 38)
    sd, _ = bf.path(stamp, 12, 84, 62)
    if night:   # crescent + twinkles
        icon_svg = (f'<path d="M52 22 a20 20 0 1 0 12 36 a16 16 0 1 1 -12 -36z" fill="{c["second"]}"/>'
                    f'{star4(66, 26, 5, c["accent"], "tw")}{star4(30, 30, 4, c["pink"], "tw", "style=\"animation-delay:-1s\"")}')
    else:       # sun with rotating rays
        rays = "".join(f'<line x1="42" y1="10" x2="42" y2="18" stroke="{c["accent"]}" stroke-width="3" stroke-linecap="round" transform="rotate({a} 42 42)"/>' for a in range(0, 360, 45))
        icon_svg = f'<g class="spin">{rays}</g><circle cx="42" cy="42" r="12" fill="{c["pink"]}"/>'
    css = ("@keyframes spin{to{transform:rotate(360deg)}}.spin{transform-origin:42px 42px;animation:spin 14s linear infinite}"
           "@keyframes run{to{stroke-dashoffset:-400}}.run{stroke-dasharray:80 320;animation:run 6s linear infinite}" + _tw())
    body = (f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="26" fill="{c["card"]}" stroke="{c["line"]}"/>'
            f'<rect class="run" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="26" fill="none" stroke="url(#g1)" stroke-width="2.4" pathLength="400"/>'
            f'{icon_svg}<path d="{d}" fill="{c["ink"]}"/><path d="{sd}" fill="{c["muted"]}"/>')
    return doc(W, H, body, css, _grad(c, "g1"), text)


TITLES = [("01", "ABOUT ME", "about"), ("02", "TOOLBOX", "toolbox"), ("03", "FEATURED WORK", "work"), ("04", "BY THE NUMBERS", "stats"),
          ("05", "CONTRIBUTION CITY", "city"), ("06", "LIVE ACTIVITY", "activity"), ("07", "LET'S CONNECT", "connect")]


def build():
    for m in MODES:
        for num, text, slug in TITLES:
            write(OUT / "titles" / f"{slug}-{m}.svg", section_title(num, text, m))
        write(OUT / "hero" / f"hello-{m}.svg", hero_hello(m))
        write(OUT / "hero" / f"roles-{m}.svg", hero_roles(m))
        write(OUT / "hero" / f"chips-{m}.svg", hero_chips(m))
        write(OUT / "hero" / f"welcome-{m}.svg", hero_welcome(m))
        write(OUT / "hero" / f"btn-email-{m}.svg", button("Email me", "gmail", m, True))
        write(OUT / "hero" / f"btn-work-{m}.svg", button("My work", "github", m, False))
        write(OUT / "sections" / f"ticker-{m}.svg", ticker(m))
        write(OUT / "sections" / f"about-{m}.svg", about(m))
        write(OUT / "contact" / f"email-{m}.svg", contact_pill("Email", "rajdipdharofficial@gmail.com", "gmail", m))
        write(OUT / "contact" / f"github-{m}.svg", contact_pill("GitHub", "@RajdipDhar2007", "github", m))
