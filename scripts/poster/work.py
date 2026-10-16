"""Toolbox tiles and featured-project cards."""
from __future__ import annotations
from .common import PAL, MODES, OUT, doc, kf, lin_grad, typo, write, icon, icon_hex
from .hero import star4, _tw, _grad

Q = chr(34)
A = chr(39)


def _lum(hexcol: str) -> float:
    r, g, b = (int(hexcol[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _brand(name: str, c: dict, mode: str) -> str:
    col = icon_hex(name)
    if mode == "dark" and _lum(col) < 0.28:
        return c["ink"]
    if mode == "light" and _lum(col) > 0.82:
        return c["ink"]
    return col


# ------------------------------------------------------------------ toolbox
ROWS = [
    ("LANGUAGES", [("python", "Python"), ("typescript", "TypeScript"), ("javascript", "JavaScript"), ("kotlin", "Kotlin"), ("c", "C"), ("html", "HTML")], False),
    ("BUILD & TOOLS", [("react", "React"), ("vite", "Vite"), ("android", "Android Studio"), ("opengl", "OpenGL"), ("git", "Git"), ("github", "GitHub")], False),
    ("LEARNING NOW", [("django", "Django"), ("solidity", "Solidity"), ("jupyter", "Jupyter")], True),
]
PILLS = ["Machine Learning", "Data Science", "LLM apps", "Automation"]


def toolbox(mode: str) -> str:
    c = PAL[mode]
    W, TW, TH, GAP = 830, 112, 124, 16
    mf, nf, pf = typo.font(typo.MONO_B), typo.font(typo.MEDIUM), typo.font(typo.HEAD)
    css = ("@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}.tl{animation:bob 4.6s ease-in-out infinite}"
           "@keyframes run{to{stroke-dashoffset:-400}}.run{stroke-dasharray:90 310;animation:run 5s linear infinite}"
           "@keyframes pu{0%,100%{opacity:1}50%{opacity:.3}}.pu{animation:pu 1.6s ease-in-out infinite}"
           "@keyframes flow{0%{stroke-dashoffset:100}100%{stroke-dashoffset:-100}}.flow{stroke-dasharray:22 78;animation:flow 1.6s linear infinite}"
           "@keyframes shn{0%{transform:translateX(0)}40%,100%{transform:translateX(220px)}}.shn{animation:shn 5s ease-in-out infinite}"
           "@keyframes orb{from{offset-distance:0%}to{offset-distance:100%}}.orb{animation:orb 4s linear infinite;filter:drop-shadow(0 0 3px currentColor)}"
           "@keyframes gw{0%,100%{opacity:.12;transform:scale(1)}50%{opacity:.3;transform:scale(1.18)}}.gw{transform-box:fill-box;transform-origin:center;animation:gw 3s ease-in-out infinite}" + _tw())
    body, y, k = "", 0, 0
    for label, items, learning in ROWS:
        d, w = mf.path(label, 13, 0, 0, 4)
        body += f'<path d="{d}" transform="translate({(W - w) / 2:.0f} {y + 18})" fill="{c["accent"] if not learning else c["pink"]}"/>'
        body += star4((W - w) / 2 - 20, y + 13, 6, c["second"], "tw") + star4((W + w) / 2 + 20, y + 13, 6, c["accent"], "tw", 'style="animation-delay:-1.2s"')
        if y > 0:  # flowing energy line linking the rows
            body += (f'<line x1="{W / 2}" y1="{y - 26}" x2="{W / 2}" y2="{y - 2}" stroke="url(#g1)" stroke-opacity=".3" stroke-width="2" stroke-linecap="round"/>'
                     f'<line class="flow" x1="{W / 2}" y1="{y - 26}" x2="{W / 2}" y2="{y - 2}" stroke="url(#g1)" stroke-width="3.2" stroke-linecap="round" pathLength="100"/>')
        y += 34
        total = len(items) * TW + (len(items) - 1) * GAP
        x0 = (W - total) / 2
        for i, (key, name) in enumerate(items):
            x = x0 + i * (TW + GAP)
            col = _brand(key, c, mode)
            nd, nw = nf.path(name, 13, 0, 0)
            dash = ' stroke-dasharray="6 6"' if learning else ""
            body += (f'<g class="tl" style="animation-delay:-{(k * .7) % 4.6:.1f}s">'
                     f'<rect x="{x + .5:.1f}" y="{y + .5}" width="{TW - 1}" height="{TH - 1}" rx="22" fill="{c["card"]}" stroke="{c["line"] if not learning else c["pink"]}" stroke-opacity="{1 if not learning else .8}"{dash}/>'
                     f'<rect class="run" x="{x + .5:.1f}" y="{y + .5}" width="{TW - 1}" height="{TH - 1}" rx="22" fill="none" stroke="{col}" stroke-width="2.2" pathLength="400" style="animation-delay:-{(k * 1.3) % 5:.1f}s"/>'
                     f'<clipPath id="tc{k}"><rect x="{x:.1f}" y="{y}" width="{TW}" height="{TH}" rx="22"/></clipPath>'
                     f'<g clip-path="url(#tc{k})"><rect class="shn" x="{x - 70:.1f}" y="{y}" width="40" height="{TH}" fill="#fff" opacity=".09" transform="skewX(-20)" style="animation-delay:-{(k * .45) % 5:.2f}s"/></g>'
                     f'<circle class="gw" cx="{x + TW / 2:.1f}" cy="{y + 52}" r="30" fill="{col}" opacity=".14" style="animation-delay:-{(k * .5) % 3:.1f}s"/>'
                     f'{icon(key, x + TW / 2 - 21, y + 31, 42, col)}'
                     f'<path d="{nd}" transform="translate({x + (TW - nw) / 2:.1f} {y + 107})" fill="{c["ink"]}"/>'
                     + ((f'<circle class="pu" cx="{x + TW - 16}" cy="{y + 16}" r="4" fill="{c["pink"]}"/>'
                         f'<circle class="orb" r="3.2" fill="{c["pink"]}" style="offset-path:path({A}M{x + 22:.1f} {y:.1f} H{x + TW - 22:.1f} A22 22 0 0 1 {x + TW:.1f} {y + 22:.1f} V{y + TH - 22:.1f} A22 22 0 0 1 {x + TW - 22:.1f} {y + TH:.1f} H{x + 22:.1f} A22 22 0 0 1 {x:.1f} {y + TH - 22:.1f} V{y + 22:.1f} A22 22 0 0 1 {x + 22:.1f} {y:.1f}Z{A});animation-delay:-{k * .9:.1f}s"/>') if learning else "") + '</g>')
            k += 1
        y += TH + 30
    # skill pills (badges)
    pills, tot = [], 0
    for p in PILLS:
        pw = pf.width(p, 15) + 62
        pills.append((p, pw))
        tot += pw + 12
    x = (W - tot + 12) / 2
    for i, (p, pw) in enumerate(pills):
        pd, _ = pf.path(p, 15, x + 38, y + 29)
        body += (f'<g class="tl" style="animation-delay:-{i * .8:.1f}s"><rect x="{x:.1f}" y="{y}" width="{pw:.1f}" height="44" rx="22" fill="{c["card"]}" stroke="url(#g1)" stroke-width="1.6"/>'
                 f'{star4(x + 22, y + 22, 8, [c["accent"], c["second"], c["pink"], c["green"]][i], "tw", f"style=" + chr(34) + f"animation-delay:-{i * .6:.1f}s" + chr(34))}'
                 f'<path d="{pd}" fill="{c["ink"]}"/></g>')
        x += pw + 12
    H = y + 56
    return doc(W, int(H), body, css, _grad(c, "g1"), "Toolbox: Python, TypeScript, JavaScript, Kotlin, C, HTML, React, Vite, Android Studio, OpenGL, Git, GitHub. Learning Django, Solidity, Jupyter, machine learning, data science, LLM apps, automation", pad_y=8)


# ------------------------------------------------------------------ projects
PROJECTS = [
    dict(key="ultimatecraft", name="UltimateCraft", icon="c", chips=["C", "OpenGL"],
         desc="Open-world voxel survival sandbox written from scratch in C and OpenGL: hand-built physics, real animal sounds, five realms and an epic story.",
         band=dict(kind="download", sub="WINDOWS  ·  ZIP BUILD", url="https://github.com/RajdipDhar2007/UltimateCraft/releases/download/v5.1.0/UltimateCraft-5.1.0-windows.zip")),
    dict(key="loci", name="Loci", icon="typescript", chips=["TypeScript", "Canvas"],
         desc="Graph anything in one living 3D space: 2D, implicit, inequality, parametric and 3D surfaces.",
         band=dict(kind="repo", sub="SOURCE  ·  README  ·  STARS", url="https://github.com/RajdipDhar2007/Loci")),
    dict(key="attendtrack", name="AttendTrack", icon="kotlin", chips=["Kotlin", "Jetpack Compose", "Gemini"],
         desc="Android attendance tracker with a bunk calculator, timetable, exams, study planner and an AI copilot.",
         band=dict(kind="download", sub="ANDROID  ·  APK INSTALLER", url="https://github.com/RajdipDhar2007/AttendTrack/releases/latest/download/AttendTrack.apk")),
    dict(key="meridian", name="Meridian", icon="react", chips=["React", "TypeScript", "Vite"],
         desc="Instrument-panel weather app with a live GPS-driven sky. No API keys needed.",
         band=dict(kind="repo", sub="SOURCE  ·  README  ·  STARS", url="https://github.com/RajdipDhar2007/Meridian")),
]


def _cube(cx, cy, sz, col, op=1.0):
    h = sz / 2
    return (f'<g opacity="{op}"><path d="M{cx} {cy - sz} L{cx + sz} {cy - h} L{cx} {cy} L{cx - sz} {cy - h}Z" fill="{col}"/>'
            f'<path d="M{cx - sz} {cy - h} L{cx} {cy} V{cy + sz} L{cx - sz} {cy + h}Z" fill="{col}" opacity=".55"/>'
            f'<path d="M{cx + sz} {cy - h} L{cx} {cy} V{cy + sz} L{cx + sz} {cy + h}Z" fill="{col}" opacity=".30"/></g>')


def art_voxels(x, y, col, c):
    return (f'<g class="vx1">{_cube(x + 30, y + 52, 18, col)}</g><g class="vx2">{_cube(x + 66, y + 52, 18, col)}</g>'
            f'<g class="vx3">{_cube(x + 48, y + 28, 18, col)}</g>')


def art_graph(x, y, col, c):
    pts = " ".join(f"{x + i * 2.2:.1f},{y + 40 - 24 * __import__('math').sin(i / 6.5):.1f}" for i in range(0, 51))
    pts2 = " ".join(f"{x + i * 2.2:.1f},{y + 40 - 16 * __import__('math').cos(i / 5):.1f}" for i in range(0, 51))
    return (f'<path d="M{x} {y + 40} H{x + 110} M{x} {y + 8} V{y + 72}" stroke="{col}" stroke-opacity=".35" stroke-width="1.5" fill="none"/>'
            f'<polyline points="{pts2}" fill="none" stroke="{c["second"]}" stroke-width="2" pathLength="100" stroke-linecap="round" style="stroke-dasharray:100;animation:gdraw 4s ease-in-out infinite;animation-delay:-1s"/>'
            f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.6" pathLength="100" stroke-linecap="round" style="stroke-dasharray:100;animation:gdraw 4s ease-in-out infinite"/>')


def art_ring(x, y, col, c):
    cx, cy, r = x + 55, y + 40, 30
    circ = 2 * 3.14159 * r
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-opacity=".25" stroke-width="7"/>'
            f'<circle class="rgp" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="7" stroke-linecap="round" transform="rotate(-90 {cx} {cy})" style="--c:{circ:.0f}"/>'
            f'<path class="chk" d="M{cx - 11} {cy + 1} L{cx - 3} {cy + 10} L{cx + 12} {cy - 9}" fill="none" stroke="{c["ink"]}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" pathLength="100"/>')


def art_sky(x, y, col, c):
    cx, cy = x + 55, y + 62
    ticks = "".join(f'<line x1="{cx}" y1="{cy - 50}" x2="{cx}" y2="{cy - 55}" stroke="{col}" stroke-opacity=".5" stroke-width="2" transform="rotate({a} {cx} {cy})"/>' for a in range(-80, 81, 20))
    return (f'<path d="M{cx - 50} {cy} A50 50 0 0 1 {cx + 50} {cy}" fill="none" stroke="{col}" stroke-opacity=".3" stroke-width="2" stroke-dasharray="3 5"/>'
            f'<line x1="{cx - 58}" y1="{cy}" x2="{cx + 58}" y2="{cy}" stroke="{col}" stroke-opacity=".5" stroke-width="2"/>{ticks}'
            f'<g transform="translate({cx} {cy})"><g class="sun"><circle cx="0" cy="-50" r="9" fill="{c["pink"]}"/><circle class="sunr" cx="0" cy="-50" r="9" fill="none" stroke="{c["pink"]}" stroke-width="2"/></g></g>')


ART = {"ultimatecraft": art_voxels, "loci": art_graph, "attendtrack": art_ring, "meridian": art_sky}
ART_CSS = ("@keyframes vx{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}.vx1{animation:vx 2.4s ease-in-out infinite}.vx2{animation:vx 2.4s ease-in-out infinite;animation-delay:-.8s}.vx3{animation:vx 2.4s ease-in-out infinite;animation-delay:-1.6s}"
           "@keyframes gdraw{0%{stroke-dashoffset:100}50%,80%{stroke-dashoffset:0}100%{stroke-dashoffset:-100}}"
           "@keyframes rgp{0%{stroke-dashoffset:var(--c)}45%,85%{stroke-dashoffset:calc(var(--c) * .22)}100%{stroke-dashoffset:var(--c)}}.rgp{stroke-dasharray:var(--c);animation:rgp 5s ease-in-out infinite}"
           "@keyframes chk{0%,30%{stroke-dasharray:0 100}55%,85%{stroke-dasharray:100 0}100%{stroke-dasharray:0 100}}.chk{animation:chk 5s ease-in-out infinite}"
           "@keyframes sun{0%{transform:rotate(-75deg)}100%{transform:rotate(75deg)}}.sun{animation:sun 6s ease-in-out infinite alternate}"
           "@keyframes sunr{0%{r:9;opacity:.8}100%{r:20;opacity:0}}.sunr{animation:sunr 1.8s ease-out infinite}")


def project_card(p: dict, mode: str, idx: int) -> str:
    c = PAL[mode]
    W, H = 400, 250
    tf, bf, mf, cf = typo.font(typo.DISPLAY), typo.font(typo.BODY), typo.font(typo.MONO_B), typo.font(typo.MEDIUM)
    col = _brand(p["icon"], c, mode)
    td, _ = tf.path(p["name"], 30, 28, 92)
    lines = bf.wrap(p["desc"], 13.5, 330)[:4]
    dd = "".join(f'<path d="{bf.path(l, 13.5, 28, 124 + k * 21)[0]}" fill="{c["muted"]}"/>' for k, l in enumerate(lines))
    chips, x = "", 28
    for ch in p["chips"]:
        cw = cf.width(ch, 11.5) + 26
        cd, _ = cf.path(ch, 11.5, x + 13, 218)
        chips += f'<rect x="{x}" y="200" width="{cw:.0f}" height="26" rx="13" fill="{col}" opacity=".16"/><path d="{cd}" fill="{c["ink"]}"/>'
        x += cw + 8
    kd, _ = mf.path(f"PROJECT 0{idx + 1}", 11, 28, 48, 3)
    css = (ART_CSS + "@keyframes run{to{stroke-dashoffset:-1000}}.run{stroke-dasharray:160 840;animation:run 7s linear infinite}"
           "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}.cb{animation:bob 6s ease-in-out infinite}"
           "@keyframes arr{0%,100%{transform:translate(0,0)}50%{transform:translate(4px,-4px)}}.arr{animation:arr 2s ease-in-out infinite}"
           "@keyframes ptl{0%{transform:translateY(0);opacity:0}15%{opacity:.8}100%{transform:translateY(-150px);opacity:0}}.ptl{animation:ptl 5s linear infinite}"
           "@keyframes sheen{0%{transform:translateX(0)}45%,100%{transform:translateX(620px)}}.sheen{animation:sheen 6s ease-in-out infinite}"
           "@keyframes spin{to{transform:rotate(360deg)}}.wm{transform-box:fill-box;transform-origin:center;animation:spin 40s linear infinite}" + _tw())
    arrow = (f'<g class="arr"><circle cx="{W - 44}" cy="{H - 41}" r="20" fill="url(#g1)"/>'
             f'<path d="M{W - 52} {H - 33} L{W - 36} {H - 49} M{W - 48} {H - 49} H{W - 36} V{H - 37}" fill="none" stroke="{"#0D1117" if mode == "dark" else "#fff"}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></g>')
    body = (f'<clipPath id="cc"><rect x="1" y="1" width="{W - 2}" height="{H + 38}" rx="26"/></clipPath>'
            f'<g><rect x="1" y="1" width="{W - 2}" height="{H + 38}" rx="26" fill="{c["card"]}" stroke="{c["line"]}" stroke-width="1.5"/>'
            f'<g clip-path="url(#cc)"><circle cx="{W - 30}" cy="40" r="120" fill="{col}" opacity=".10"/>'
            f'<g class="wm">{icon(p["icon"], W - 130, -10, 130, col, "opacity=\".07\"")}</g></g>'
            f'{ART[p["key"]](W - 150, 26, col, c)}'
            f'<rect class="run" x="1" y="1" width="{W - 2}" height="{H + 38}" rx="26" fill="none" stroke="url(#g1)" stroke-width="3" pathLength="1000" style="animation-delay:-{idx * 1.7:.1f}s"/>'
            f'<g clip-path="url(#cc)">{"".join(f"<circle class=" + chr(34) + "ptl" + chr(34) + f" cx=" + chr(34) + f"{40 + j * 58}" + chr(34) + f" cy=" + chr(34) + f"{H - 10}" + chr(34) + f" r=" + chr(34) + f"{1.6 + (j % 3) * .6}" + chr(34) + f" fill=" + chr(34) + f"{col}" + chr(34) + " style=" + chr(34) + f"animation-delay:-{(j * 1.1 + idx) % 6:.1f}s;animation-duration:{4 + j % 3}s" + chr(34) + "/>" for j in range(6))}</g>'
            f'<g clip-path="url(#cc)"><rect class="sheen" x="-120" y="0" width="70" height="{H}" fill="#fff" opacity=".10" transform="skewX(-20)" style="animation-delay:-{idx * 1.6:.1f}s"/></g>'
            f'<path d="{kd}" fill="{c["accent"]}"/><path d="{td}" fill="url(#g1)"/>{dd}{chips}{arrow}'
            f'{star4(W - 90, 150, 6, c["accent"], "tw")}{star4(W - 40, 120, 4, c["pink"], "tw", "style=" + chr(34) + "animation-delay:-1.3s" + chr(34))}</g>')
    return doc(W, H, body, css, _grad(c, "g1"), f"{p['name']}: {p['desc']}")


def action_band(p: dict, mode: str, idx: int) -> str:
    """Bottom strip of a project card: a big animated button (download the build, or open the repo)."""
    c = PAL[mode]
    W, H = 400, 70
    hf, mf = typo.font(typo.HEAD), typo.font(typo.MONO_B)
    dl = p["band"]["kind"] == "download"
    dark = "#0D1117" if mode == "dark" else "#fff"
    fg = dark if dl else c["ink"]
    px, py, pw, ph = 20, 10, W - 40, 50
    label = "DOWNLOAD" if dl else "OPEN REPOSITORY"
    ld, _ = hf.path(label, 17, 88, py + 25, 2)
    sd, _ = mf.path(p["band"]["sub"], 9.5, 88, py + 40, 2)
    if dl:   # arrow into a tray
        glyph = (f'<g class="bnc"><path d="M0 -9 V5 M-7 -2 L0 5 L7 -2" fill="none" stroke="{fg}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g>'
                 f'<path d="M-9 10 H9" stroke="{fg}" stroke-width="3" stroke-linecap="round"/>')
    else:    # arrow out of the card
        glyph = f'<g class="nudge"><path d="M-6 6 L6 -6 M-3 -6 H6 V3" fill="none" stroke="{fg}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g>'
    chev = "".join(f'<path class="chv" d="M{px + pw - 62 + k * 14} {py + 16} l8 9 l-8 9" fill="none" stroke="{fg}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="animation-delay:{k * .22:.2f}s"/>' for k in range(3))
    fill = 'fill="url(#g1)"' if dl else f'fill="{c["accent"]}" fill-opacity=".07" stroke="url(#g1)" stroke-width="2"'
    disc = (f'fill="{dark}" fill-opacity=".22"' if dl else f'fill="{c["card"]}" stroke="url(#g1)" stroke-width="2"')
    prog = f'<rect class="prog" x="{px}" y="{py + ph - 4}" width="{pw}" height="4" fill="{dark}" opacity=".3"/>' if dl else ""
    css = ("@keyframes bnc{0%,100%{transform:translateY(-2px)}50%{transform:translateY(3px)}}.bnc{animation:bnc 1s ease-in-out infinite}"
           "@keyframes nudge{0%,100%{transform:translate(0,0)}50%{transform:translate(3px,-3px)}}.nudge{animation:nudge 1.4s ease-in-out infinite}"
           "@keyframes chv{0%,100%{opacity:.2}35%{opacity:1}}.chv{animation:chv 1.3s ease-in-out infinite}"
           "@keyframes rip{0%{r:19;opacity:.8}100%{r:34;opacity:0}}.rip{animation:rip 1.8s ease-out infinite}"
           "@keyframes shn{0%{transform:translateX(0)}45%,100%{transform:translateX(460px)}}.shn{animation:shn 3.2s ease-in-out infinite}"
           "@keyframes prog{0%{transform:scaleX(0)}70%,100%{transform:scaleX(1)}}.prog{transform-box:fill-box;transform-origin:left;animation:prog 2.6s ease-in-out infinite}"
           "@keyframes pl{0%{opacity:.75;transform:scale(1)}100%{opacity:0;transform:scale(1.05,1.25)}}.pl{transform-box:fill-box;transform-origin:center;animation:pl 2s ease-out infinite}"
           "@keyframes run{to{stroke-dashoffset:-1000}}.run{stroke-dasharray:160 840;animation:run 6s linear infinite}"
           "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}.bob{animation:bob 2.4s ease-in-out infinite}" + _tw())
    body = (f'<rect x="1" y="-40" width="{W - 2}" height="{H + 39}" rx="26" fill="{c["card"]}" stroke="{c["line"]}" stroke-width="1.5"/>'
            f'<rect class="run" x="1" y="-40" width="{W - 2}" height="{H + 39}" rx="26" fill="none" stroke="url(#g1)" stroke-width="3" pathLength="1000" style="animation-delay:-{idx * 1.7 + 3:.1f}s"/>'
            f'<line x1="26" y1="1" x2="{W - 26}" y2="1" stroke="{c["line"]}" stroke-dasharray="2 6" stroke-linecap="round"/>'
            f'<clipPath id="bp"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="25"/></clipPath>'
            f'<rect class="pl" x="{px}" y="{py}" width="{pw}" height="{ph}" rx="25" fill="none" stroke="url(#g1)" stroke-width="2.5"/>'
            f'<g class="bob"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="25" {fill}/>'
            f'<g clip-path="url(#bp)"><rect class="shn" x="{px - 90}" y="{py}" width="46" height="{ph}" fill="#fff" opacity="{.38 if dl else .14}" transform="skewX(-20)"/>{prog}</g>'
            f'<circle class="rip" cx="{px + 30}" cy="{py + 25}" r="19" fill="none" stroke="{fg if dl else c["accent"]}" stroke-width="2"/>'
            f'<circle cx="{px + 30}" cy="{py + 25}" r="19" {disc}/>'
            f'<g transform="translate({px + 30} {py + 25})">{glyph}</g>'
            f'<path d="{ld}" fill="{fg}"/><path d="{sd}" fill="{fg}" fill-opacity=".72"/>{chev}'
            f'{star4(px + pw - 14, py + 9, 4.5, fg if dl else c["pink"], "tw")}</g>')
    verb = "Download" if dl else "Open"
    return doc(W, H, body, css, _grad(c, "g1"), f"{verb} {p['name']}: " + " ".join(p["band"]["sub"].split()))


def build():
    for m in MODES:
        write(OUT / "sections" / f"toolbox-{m}.svg", toolbox(m))
        for i, p in enumerate(PROJECTS):
            write(OUT / "projects" / f"{p['key']}-{m}.svg", project_card(p, m, i))
            write(OUT / "projects" / f"{p['key']}-band-{m}.svg", action_band(p, m, i))
