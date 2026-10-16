"""Contribution city: an isometric, animated 3D bar chart of the last 36 weeks, built from live GitHub data.

    python scripts/city.py     # needs GITHUB_TOKEN / GH_TOKEN (or `gh auth login` locally)

Replaces the third-party chart service so the city refreshes on our own schedule (hourly in Actions).
"""
from __future__ import annotations
import datetime as dt
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from poster.common import PAL, MODES, OUT, doc, write, typo  # noqa: E402
from poster.hero import star4, _tw, _grad  # noqa: E402
from cards import gql, OWNER  # noqa: E402

WEEKS = 36
LEVELS = {
    "dark": ["#1E2B40", "#0E7490", "#22D3EE", "#A78BFA", "#F472B6"],
    "light": ["#DCE4F2", "#9EC5FE", "#4C9AFF", "#8250DF", "#D6336C"],
}


def fetch_grid(login: str) -> list[list[int]]:
    """Last WEEKS weeks as [week][weekday] contribution counts (Sunday first, newest week last)."""
    now = dt.datetime.now(dt.timezone.utc)
    start = now - dt.timedelta(weeks=WEEKS + 1)
    d = gql("query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){contributionsCollection(from:$f,to:$t)"
            "{contributionCalendar{weeks{contributionDays{contributionCount weekday}}}}}}",
            l=login, f=start.strftime("%Y-%m-%dT%H:%M:%SZ"), t=now.strftime("%Y-%m-%dT%H:%M:%SZ"))
    weeks = d["user"]["contributionsCollection"]["contributionCalendar"]["weeks"][-WEEKS:]
    grid = []
    for w in weeks:
        col = [0] * 7
        for day in w["contributionDays"]:
            col[day["weekday"]] = day["contributionCount"]
        grid.append(col)
    return grid


def _shade(hexcol: str, k: float) -> str:
    r, g, b = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(v * k))) for v in (r, g, b))


def city_svg(mode: str, grid: list[list[int]]) -> str:
    c = PAL[mode]
    W, H = 830, 350
    ux, uy, vx, vy = 19.0, 3.4, -9.0, 9.0      # screen vectors of one week (along the row) and one weekday (towards the viewer)
    x0, y0 = 40 + 6 * 9.0 + 6, 122
    mono = typo.font(typo.MONO_B)
    pal = LEVELS[mode]
    nw = len(grid)
    nz = sorted(v for col in grid for v in col if v)
    vmax = nz[int(len(nz) * .94)] if nz else 1       # robust cap: one huge day must not flatten everything else
    qs = [nz[int(len(nz) * q)] for q in (.25, .5, .75)] if nz else [1, 1, 1]
    total = sum(sum(col) for col in grid)

    def pt(i, j):
        return x0 + i * ux + j * vx, y0 + i * uy + j * vy

    def lvl(v):
        return 0 if v == 0 else 1 + sum(v > q for q in qs)

    def hgt(v):
        return 3 + 92 * math.sqrt(min(v, vmax) / vmax) if v else 2

    css = ("@keyframes up{0%{transform:scaleY(.04)}14%,86%{transform:scaleY(1)}100%{transform:scaleY(.04)}}.bar{transform-box:fill-box;transform-origin:50% 100%;animation:up 12s cubic-bezier(.3,.8,.2,1) infinite both}"
           "@keyframes gl{0%,100%{opacity:0}50%{opacity:.55}}.gl{animation:gl 3.2s ease-in-out infinite}"
           "@keyframes run{to{stroke-dashoffset:-1000}}.run{stroke-dasharray:140 860;animation:run 7s linear infinite}"
           "@keyframes tg{0%{r:4;opacity:.9}100%{r:16;opacity:0}}.tg{animation:tg 1.8s ease-out infinite}"
           "@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}.fl{animation:fl 3s ease-in-out infinite}" + _tw())
    # floor slab
    corners = [pt(-.4, -.4), pt(nw + .2, -.4), pt(nw + .2, 7.4), pt(-.4, 7.4)]
    floor = " ".join(f"{x:.1f},{y:.1f}" for x, y in corners)
    body = (f'<clipPath id="cc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="28"/></clipPath>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="28" fill="{c["card"]}" stroke="{c["line"]}"/>'
            f'<polygon points="{floor}" fill="{c["accent"]}" fill-opacity=".05" stroke="{c["line"]}" stroke-width="1.4"/>'
            f'<polygon class="run" points="{floor}" fill="none" stroke="url(#g1)" stroke-width="2.6" pathLength="1000" stroke-linejoin="round"/>')
    # grid lines on the floor
    for j in range(8):
        a, b = pt(-.4, j), pt(nw + .2, j)
        body += f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{c["line"]}" stroke-opacity=".6" stroke-dasharray="2 6"/>'
    # bars, back (far weekday) to front
    m = .09
    au, av = (ux * (1 - 2 * m), uy * (1 - 2 * m)), (vx * (1 - 2 * m), vy * (1 - 2 * m))
    last = max(((i, j) for i in range(nw) for j in range(7) if grid[i][j] > 0), default=(nw - 1, 0))
    for i, j in sorted(((i, j) for i in range(nw) for j in range(7)), key=lambda t: (t[1], t[0])):
        v = grid[i][j]
        h = hgt(v)
        px, py = pt(i, j)
        px, py = px + (ux + vx) * m, py + (uy + vy) * m
        p00, p10, p11, p01 = (px, py), (px + au[0], py + au[1]), (px + au[0] + av[0], py + au[1] + av[1]), (px + av[0], py + av[1])
        base = pal[lvl(v)]

        def poly(*ps):
            return " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)
        top = poly((p00[0], p00[1] - h), (p10[0], p10[1] - h), (p11[0], p11[1] - h), (p01[0], p01[1] - h))
        front = poly((p01[0], p01[1] - h), (p11[0], p11[1] - h), p11, p01)
        right = poly((p10[0], p10[1] - h), (p11[0], p11[1] - h), p11, p10)
        delay = i * .05 + j * .02
        glow = f'<polygon class="gl" points="{top}" fill="#fff" style="animation-delay:{(i * .09 + j * .05) % 3.2:.2f}s"/>' if lvl(v) >= 4 else ""
        body += (f'<g class="bar" style="animation-delay:{delay:.2f}s"><polygon points="{front}" fill="{_shade(base, .62)}"/><polygon points="{right}" fill="{_shade(base, .42)}"/>'
                 f'<polygon points="{top}" fill="{_shade(base, 1.1)}"/>{glow}</g>')
    # "today" beacon above the newest contribution day
    li, lj = last
    bx, by = pt(li + .5, lj + .5)
    bh = hgt(grid[li][lj])
    body += (f'<g class="fl"><ellipse class="tg" cx="{bx:.1f}" cy="{by - bh - 6:.1f}" rx="6" ry="2.4" fill="none" stroke="{c["pink"]}" stroke-width="2"/>'
             f'<path d="M{bx:.1f} {by - bh - 12:.1f} l-5 -9 h10z" fill="{c["pink"]}"/></g>')
    # legend + summary
    lg, x = f'<path d="{mono.path("LESS", 9, 36, H - 30, 2)[0]}" fill="{c["muted"]}"/>', 78
    for k, col in enumerate(pal):
        lg += f'<polygon points="{x},{H - 36} {x + 8},{H - 32} {x},{H - 28} {x - 8},{H - 32}" fill="{col}"/>'
        x += 20
    lg += f'<path d="{mono.path("MORE", 9, x + 4, H - 30, 2)[0]}" fill="{c["muted"]}"/>'
    sd, sw = mono.path(f"{total} CONTRIBUTIONS  ·  LAST {nw} WEEKS", 10, 0, 0, 2)
    body += lg + f'<path d="{sd}" transform="translate({W - 36 - sw:.1f} {H - 30})" fill="{c["accent"]}"/>'
    body += star4(W - 40, 36, 7, c["accent"], "tw") + star4(W - 70, 58, 4, c["pink"], "tw", 'style="animation-delay:-1s"')
    return doc(W, H, body, css, _grad(c, "g1"), f"3D contribution city: {total} contributions in the last {nw} weeks")


def main() -> None:
    grid = fetch_grid(os.environ.get("GITHUB_REPOSITORY_OWNER", OWNER))
    for m in MODES:
        write(OUT / "3d" / f"contribution-{m}.svg", city_svg(m, grid))


if __name__ == "__main__":
    main()
