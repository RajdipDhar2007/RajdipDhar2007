"""GitHub stats dashboard (stats + languages + streak) as one animated SVG per theme.

Data comes from the GitHub GraphQL API (public data of the repo owner), so the default
GITHUB_TOKEN is enough in Actions; a PAT only adds private-repo numbers.

    python scripts/cards.py            # needs GITHUB_TOKEN / GH_TOKEN (or `gh auth login` locally)
"""
from __future__ import annotations
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from poster.common import PAL, MODES, OUT, doc, write, typo, icon  # noqa: E402
from poster.hero import star4, _tw, _grad  # noqa: E402

OWNER = "RajdipDhar2007"
EXCLUDE_LANGS = {"Jupyter Notebook"}  # notebook output dwarfs real code


def token() -> str:
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    return t or subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def gql(query: str, **variables) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json", "User-Agent": "profile-cards"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


# ---------------------------------------------------------------- streak maths
def compute_streaks(days: dict[str, int], today: dt.date) -> dict:
    """days: ISO date -> contribution count. Pure function (unit-tested)."""
    total = sum(days.values())
    longest = run = 0
    prev = None
    for d in sorted(days):
        cur = dt.date.fromisoformat(d)
        if days[d] > 0:
            run = run + 1 if prev and (cur - prev).days == 1 else 1
            prev = cur
            longest = max(longest, run)
        else:
            run, prev = 0, None
    cur_streak, d = 0, today
    if days.get(d.isoformat(), 0) == 0:   # today may still be empty
        d -= dt.timedelta(days=1)
    while days.get(d.isoformat(), 0) > 0:
        cur_streak += 1
        d -= dt.timedelta(days=1)
    return {"total": total, "current": cur_streak, "longest": longest}


def fetch_days(login: str) -> dict[str, int]:
    created = gql("query($l:String!){user(login:$l){createdAt}}", l=login)["user"]["createdAt"][:4]
    days: dict[str, int] = {}
    for year in range(int(created), dt.datetime.now(dt.timezone.utc).year + 1):
        d = gql("query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){contributionsCollection(from:$f,to:$t)"
                "{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}",
                l=login, f=f"{year}-01-01T00:00:00Z", t=f"{year}-12-31T23:59:59Z")
        for w in d["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for day in w["contributionDays"]:
                days[day["date"]] = day["contributionCount"]
    return days


def fetch_overview(login: str):
    d = gql("""query($l:String!){user(login:$l){followers{totalCount} pullRequests{totalCount}
      contributionsCollection{totalCommitContributions}
      repositories(ownerAffiliations:OWNER,isFork:false,first:100,privacy:PUBLIC){nodes{stargazerCount
      languages(first:8,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}""", l=login)["user"]
    langs: dict[str, int] = {}
    for r in d["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            if e["node"]["name"] not in EXCLUDE_LANGS:
                langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    stats = {"commits": d["contributionsCollection"]["totalCommitContributions"], "prs": d["pullRequests"]["totalCount"],
             "stars": sum(r["stargazerCount"] for r in d["repositories"]["nodes"]), "followers": d["followers"]["totalCount"]}
    return stats, sorted(langs.items(), key=lambda kv: -kv[1])


# ------------------------------------------------------------------- rendering
def _star5(cx, cy, r, fill):
    import math
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke-linejoin="round"/>'


def _people(cx, cy, fill):
    return f'<circle cx="{cx}" cy="{cy - 5}" r="5" fill="{fill}"/><path d="M{cx - 10} {cy + 11} q0 -11 10 -11 t10 11z" fill="{fill}"/>'



def _roll(num: str, x: float, y: float, size: float, font, name: str, delay: float, T: float = 10.0):
    """Odometer-style number: every digit scrolls up a 0-9 strip, lands, holds, then the loop restarts."""
    lh = size * 1.3
    out, css, cx = "", "", x
    for k, ch in enumerate(num):
        adv = font.advance(ch, size)
        if not ch.isdigit():
            out += f'<path d="{font.path(ch, size, cx, y)[0]}" fill="url(#g1)"/>'
            cx += adv
            continue
        d = int(ch)
        strip = "".join(f'<path d="{font.path(str(n), size, cx, y + n * lh)[0]}" fill="url(#g1)"/>' for n in range(10))
        t0, t1 = delay + k * 0.12, delay + k * 0.12 + 1.3
        css += (f"@keyframes {name}{k}{{0%,{t0 / T * 100:.2f}%{{transform:translateY(0)}}{t1 / T * 100:.2f}%,94%{{transform:translateY({-d * lh:.1f}px)}}100%{{transform:translateY(0)}}}}"
                f".{name}{k}{{animation:{name}{k} {T}s cubic-bezier(.2,.8,.2,1) infinite}}")
        out += (f'<clipPath id="{name}c{k}"><rect x="{cx - 1:.1f}" y="{y - size * .95:.1f}" width="{adv + 2:.1f}" height="{size * 1.15:.1f}"/></clipPath>'
                f'<g clip-path="url(#{name}c{k})"><g class="{name}{k}" style="transform:translateY({-d * lh:.1f}px)">{strip}</g></g>')
        cx += adv
    # reduced motion: show the final value (strip stops at the right digit via the base transform)
    return out, css


def _art_commits(x, y, col, c):
    """Branching commit graph with a pulse running along the branch."""
    return (f'<g class="a1"><path d="M{x} {y + 44} H{x + 20} C{x + 34} {y + 44} {x + 30} {y + 8} {x + 48} {y + 8} H{x + 66}" fill="none" stroke="{col}" stroke-opacity=".35" stroke-width="3" stroke-linecap="round"/>'
            f'<path class="run" d="M{x} {y + 44} H{x + 20} C{x + 34} {y + 44} {x + 30} {y + 8} {x + 48} {y + 8} H{x + 66}" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" pathLength="100" style="stroke-dasharray:22 78;animation:cmt 2.4s linear infinite"/>'
            f'<circle cx="{x}" cy="{y + 44}" r="5" fill="{col}"/><circle cx="{x + 20}" cy="{y + 44}" r="4" fill="{col}" opacity=".7"/>'
            f'<circle class="pu" cx="{x + 66}" cy="{y + 8}" r="5.5" fill="{col}"/></g>')


def _art_prs(x, y, col, c):
    """Two branches merging into one, with an arrow head."""
    return (f'<path d="M{x} {y + 8} C{x + 28} {y + 8} {x + 28} {y + 26} {x + 52} {y + 26}" fill="none" stroke="{col}" stroke-opacity=".4" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M{x} {y + 44} C{x + 28} {y + 44} {x + 28} {y + 26} {x + 52} {y + 26}" fill="none" stroke="{col}" stroke-opacity=".4" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M{x} {y + 8} C{x + 28} {y + 8} {x + 28} {y + 26} {x + 52} {y + 26}" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" pathLength="100" style="stroke-dasharray:18 82;animation:cmt 2.2s linear infinite"/>'
            f'<path d="M{x} {y + 44} C{x + 28} {y + 44} {x + 28} {y + 26} {x + 52} {y + 26}" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" pathLength="100" style="stroke-dasharray:18 82;animation:cmt 2.2s linear infinite;animation-delay:-1.1s"/>'
            f'<circle cx="{x}" cy="{y + 8}" r="4.5" fill="{col}"/><circle cx="{x}" cy="{y + 44}" r="4.5" fill="{col}"/>'
            f'<path class="a2" d="M{x + 52} {y + 17} L{x + 66} {y + 26} L{x + 52} {y + 35}Z" fill="{col}"/>')


def _art_stars(x, y, col, c):
    """Twinkling constellation."""
    pts = [(x + 12, y + 36, 9, 0), (x + 34, y + 14, 6, .6), (x + 54, y + 38, 7, 1.2), (x + 66, y + 12, 5, 1.8), (x + 30, y + 46, 4, 2.2)]
    out = f'<path d="M{pts[0][0]} {pts[0][1]} L{pts[1][0]} {pts[1][1]} L{pts[2][0]} {pts[2][1]} L{pts[3][0]} {pts[3][1]}" fill="none" stroke="{col}" stroke-opacity=".3" stroke-dasharray="3 4"/>'
    for sx, sy, r, d in pts:
        k = r * 0.28
        out += (f'<path class="tw" style="animation-delay:-{d}s" d="M{sx} {sy - r} Q{sx + k} {sy - k} {sx + r} {sy} Q{sx + k} {sy + k} {sx} {sy + r} Q{sx - k} {sy + k} {sx - r} {sy} Q{sx - k} {sy - k} {sx} {sy - r}Z" fill="{col}"/>')
    return out


def _art_followers(x, y, col, c):
    """Avatar with two orbiting friends."""
    cx, cy = x + 34, y + 26
    return (f'<circle cx="{cx}" cy="{cy}" r="22" fill="none" stroke="{col}" stroke-opacity=".3" stroke-dasharray="3 5"/>'
            f'<circle cx="{cx}" cy="{cy - 4}" r="6" fill="{col}"/><path d="M{cx - 11} {cy + 12} q0 -11 11 -11 t11 11z" fill="{col}"/>'
            f'<g transform="translate({cx} {cy})"><g class="orb1"><circle cx="22" cy="0" r="5" fill="{col}"/></g><g class="orb2"><circle cx="-22" cy="0" r="4" fill="{col}" opacity=".7"/></g></g>')


def dashboard_svg(mode: str, stats: dict, langs: list[tuple[str, int]], streak: dict) -> str:
    c = PAL[mode]
    W, H, T = 830, 470, 10.0
    big, lab, mono, body_f = typo.font(typo.DISPLAY), typo.font(typo.MEDIUM), typo.font(typo.MONO_B), typo.font(typo.BODY)
    css = (f"@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}.bb{{animation:bob 5s ease-in-out infinite}}"
           f"@keyframes grow{{0%{{transform:scaleX(0)}}12%,86%{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}}}.gr{{transform-box:fill-box;transform-origin:left;animation:grow {T}s cubic-bezier(.3,.8,.2,1) infinite}}"
           f"@keyframes ring{{0%{{stroke-dashoffset:var(--full)}}15%,86%{{stroke-dashoffset:var(--off)}}100%{{stroke-dashoffset:var(--full)}}}}.rg{{animation:ring {T}s cubic-bezier(.3,.8,.2,1) infinite}}"
           f"@keyframes cmt{{from{{stroke-dashoffset:100}}to{{stroke-dashoffset:0}}}}"
           f"@keyframes pu{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.45;transform:scale(1.35)}}}}.pu{{transform-box:fill-box;transform-origin:center;animation:pu 1.6s ease-in-out infinite}}"
           f"@keyframes a2{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(5px)}}}}.a2{{animation:a2 1.4s ease-in-out infinite}}"
           f"@keyframes orbit{{to{{transform:rotate(360deg)}}}}.orb1{{transform-origin:0 0;animation:orbit 4s linear infinite}}.orb2{{transform-origin:0 0;animation:orbit 6s linear infinite reverse}}"
           f"@keyframes shn{{0%{{transform:translateX(0)}}50%,100%{{transform:translateX(900px)}}}}.shn{{animation:shn 7s ease-in-out infinite}}"
           f"@keyframes run{{to{{stroke-dashoffset:-400}}}}.run{{stroke-dasharray:80 320;animation:run 6s linear infinite}}" + _tw())
    body = ""

    def panel(x, y, w, h, i):
        return (f'<clipPath id="pc{i}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24"/></clipPath>'
                f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="24" fill="{c["card"]}" stroke="{c["line"]}"/>'
                f'<g clip-path="url(#pc{i})"><rect class="shn" x="{x - 90}" y="{y}" width="60" height="{h}" fill="{c["accent"]}" opacity=".05" transform="skewX(-20)" style="animation-delay:-{i * 1.1:.1f}s"/></g>'
                f'<rect class="run" x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="24" fill="none" stroke="url(#g1)" stroke-width="2.2" pathLength="400" style="animation-delay:-{i * 1.4:.1f}s"/>')

    tiles = [("commits", "commits this year", c["accent"], lambda x, y: icon("git", x, y, 26, c["accent"]), _art_commits),
             ("prs", "pull requests", c["second"], lambda x, y: icon("github", x, y, 26, c["second"]), _art_prs),
             ("stars", "stars earned", c["pink"], lambda x, y: _star5(x + 13, y + 13, 14, c["pink"]), _art_stars),
             ("followers", "followers", c["green"], lambda x, y: _people(x + 13, y + 14, c["green"]), _art_followers)]
    for i, (key, label, col, ic, art) in enumerate(tiles):
        x = i * 213
        digits, dcss = _roll(str(stats[key]), x + 24, 96, 40, big, f"n{i}", 0.25 + i * 0.15)
        css += dcss
        body += (f'<g class="bb" style="animation-delay:-{i * .9:.1f}s">{panel(x, 8, 190, 120, i)}{art(x + 112, 22, col, c)}'
                 f'{ic(x + 24, 34)}{digits}<path d="{lab.path(label, 13, x + 24, 118)[0]}" fill="{c["muted"]}"/></g>')
    # languages panel
    top = langs[:5]
    total = sum(v for _, v in top) or 1
    pal = [c["accent"], c["second"], c["pink"], c["green"], "#F59E0B"]
    body += f'<g class="bb" style="animation-delay:-1s">{panel(0, 150, 405, 300, 4)}'
    body += f'<path d="{mono.path("TOP LANGUAGES", 12, 28, 190, 3)[0]}" fill="{c["accent"]}"/>'
    for i, (name, v) in enumerate(top):
        y = 218 + i * 44
        pctv = 100 * v / total
        nd, _ = lab.path(name, 14, 28, y)
        pd, pw = lab.path(f"{pctv:.1f}%", 13, 0, y)
        body += (f'<path d="{nd}" fill="{c["ink"]}"/><path d="{pd}" transform="translate({377 - pw:.0f} 0)" fill="{c["muted"]}"/>'
                 f'<rect x="28" y="{y + 9}" width="349" height="8" rx="4" fill="{c["line"]}"/>'
                 f'<rect class="gr" x="28" y="{y + 9}" width="{max(349 * v / total, 6):.1f}" height="8" rx="4" fill="{pal[i]}" style="animation-delay:{i * .12:.2f}s"/>')
    body += "</g>"
    # streak panel
    cx, cy, r = 425 + 112, 300, 62
    circ = 2 * 3.14159 * r
    frac = min(streak["current"], 30) / 30 if streak["current"] else 0.02
    cd, cw = big.path(str(streak["current"]), 46, 0, 0)
    body += f'<g class="bb" style="animation-delay:-2s">{panel(425, 150, 405, 300, 5)}'
    body += f'<path d="{mono.path("CONTRIBUTION STREAK", 12, 453, 190, 3)[0]}" fill="{c["pink"]}"/>'
    body += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c["line"]}" stroke-width="10"/>'
             f'<circle class="rg" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#g1)" stroke-width="10" stroke-linecap="round" stroke-dasharray="{circ:.0f}" '
             f'style="--full:{circ:.0f};--off:{circ * (1 - frac):.0f}" transform="rotate(-90 {cx} {cy})"/>'
             f'<path d="{big.path(str(streak["current"]), 46, cx - cw / 2, cy + 8)[0]}" fill="{c["ink"]}"/>'
             f'<path d="{lab.path("days", 13, cx - lab.width("days", 13) / 2, cy + 32)[0]}" fill="{c["muted"]}"/>')
    for i, (val, label, col) in enumerate([(streak["longest"], "longest streak", c["second"]), (streak["total"], "total contributions", c["accent"])]):
        y = 258 + i * 76
        vd, _ = big.path(str(val), 30, 0, 0)
        body += (f'<path d="{big.path(str(val), 30, 700, y)[0]}" fill="{col}"/>'
                 f'<path d="{lab.path(label, 12.5, 700, y + 24)[0]}" fill="{c["muted"]}"/>')
    body += star4(790, 190, 6, c["accent"], "tw") + "</g>"
    return doc(W, H, body, css, _grad(c, "g1"), "GitHub stats: commits, pull requests, stars, followers, top languages and contribution streak", pad_y=8)


def main() -> None:
    login = os.environ.get("GITHUB_REPOSITORY_OWNER", OWNER)
    stats, langs = fetch_overview(login)
    streak = compute_streaks(fetch_days(login), dt.datetime.now(dt.timezone.utc).date())
    print(stats, langs[:5], streak)
    for m in MODES:
        write(OUT / "stats" / f"dashboard-{m}.svg", dashboard_svg(m, stats, langs, streak))


if __name__ == "__main__":
    main()
