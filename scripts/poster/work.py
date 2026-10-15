"""Toolbox tiles and featured-project cards."""
from __future__ import annotations
from .common import PAL, MODES, OUT, doc, kf, lin_grad, typo, write, icon, icon_hex
from .hero import star4, _tw, _grad


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
           "@keyframes pu{0%,100%{opacity:1}50%{opacity:.3}}.pu{animation:pu 1.6s ease-in-out infinite}" + _tw())
    body, y, k = "", 0, 0
    for label, items, learning in ROWS:
        d, w = mf.path(label, 13, 0, 0, 4)
        body += f'<path d="{d}" transform="translate({(W - w) / 2:.0f} {y + 18})" fill="{c["accent"] if not learning else c["pink"]}"/>'
        body += star4((W - w) / 2 - 20, y + 13, 6, c["second"], "tw") + star4((W + w) / 2 + 20, y + 13, 6, c["accent"], "tw", 'style="animation-delay:-1.2s"')
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
                     f'<circle cx="{x + TW / 2:.1f}" cy="{y + 52}" r="30" fill="{col}" opacity=".14"/>'
                     f'{icon(key, x + TW / 2 - 21, y + 31, 42, col)}'
                     f'<path d="{nd}" transform="translate({x + (TW - nw) / 2:.1f} {y + 107})" fill="{c["ink"]}"/>'
                     + (f'<circle class="pu" cx="{x + TW - 16}" cy="{y + 16}" r="4" fill="{c["pink"]}"/>' if learning else "") + '</g>')
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
         desc="Open-world voxel survival sandbox written from scratch in C and OpenGL: hand-built physics, real animal sounds, five realms and an epic story."),
    dict(key="loci", name="Loci", icon="typescript", chips=["TypeScript", "Canvas"],
         desc="Graph anything in one living 3D space: 2D, implicit, inequality, parametric and 3D surfaces."),
    dict(key="attendtrack", name="AttendTrack", icon="kotlin", chips=["Kotlin", "Jetpack Compose", "Gemini"],
         desc="Android attendance tracker with a bunk calculator, timetable, exams, study planner and an AI copilot."),
    dict(key="meridian", name="Meridian", icon="react", chips=["React", "TypeScript", "Vite"],
         desc="Instrument-panel weather app with a live GPS-driven sky. No API keys needed."),
]


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
    css = ("@keyframes run{to{stroke-dashoffset:-1000}}.run{stroke-dasharray:160 840;animation:run 7s linear infinite}"
           "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}.cb{animation:bob 6s ease-in-out infinite}"
           "@keyframes arr{0%,100%{transform:translate(0,0)}50%{transform:translate(4px,-4px)}}.arr{animation:arr 2s ease-in-out infinite}"
           "@keyframes spin{to{transform:rotate(360deg)}}.wm{transform-box:fill-box;transform-origin:center;animation:spin 40s linear infinite}" + _tw())
    arrow = (f'<g class="arr"><circle cx="{W - 44}" cy="{H - 41}" r="20" fill="url(#g1)"/>'
             f'<path d="M{W - 52} {H - 33} L{W - 36} {H - 49} M{W - 48} {H - 49} H{W - 36} V{H - 37}" fill="none" stroke="{"#0D1117" if mode == "dark" else "#fff"}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></g>')
    body = (f'<clipPath id="cc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26"/></clipPath>'
            f'<g class="cb" style="animation-delay:-{idx * 1.3:.1f}s"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26" fill="{c["card"]}" stroke="{c["line"]}" stroke-width="1.5"/>'
            f'<g clip-path="url(#cc)"><circle cx="{W - 30}" cy="40" r="120" fill="{col}" opacity=".10"/>'
            f'<g class="wm">{icon(p["icon"], W - 130, -10, 130, col, "opacity=\".13\"")}</g></g>'
            f'<rect class="run" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26" fill="none" stroke="url(#g1)" stroke-width="3" pathLength="1000" style="animation-delay:-{idx * 1.7:.1f}s"/>'
            f'<path d="{kd}" fill="{c["accent"]}"/><path d="{td}" fill="url(#g1)"/>{dd}{chips}{arrow}'
            f'{star4(W - 90, 150, 6, c["accent"], "tw")}{star4(W - 40, 120, 4, c["pink"], "tw", "style=" + chr(34) + "animation-delay:-1.3s" + chr(34))}</g>')
    return doc(W, H, body, css, _grad(c, "g1"), f"{p['name']}: {p['desc']}", pad_y=8)


def build():
    for m in MODES:
        write(OUT / "sections" / f"toolbox-{m}.svg", toolbox(m))
        for i, p in enumerate(PROJECTS):
            write(OUT / "projects" / f"{p['key']}-{m}.svg", project_card(p, m, i))
