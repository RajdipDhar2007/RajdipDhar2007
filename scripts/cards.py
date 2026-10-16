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
           f"@keyframes fl{{0%,100%{{transform:scale(1,1) rotate(-2deg)}}25%{{transform:scale(.92,1.1) rotate(2deg)}}50%{{transform:scale(1.05,.95) rotate(-1deg)}}75%{{transform:scale(.95,1.08) rotate(3deg)}}}}.flame{{transform-box:fill-box;transform-origin:bottom;animation:fl .9s ease-in-out infinite}}"
           f"@keyframes bshine{{0%,25%{{transform:translateX(0)}}70%,100%{{transform:translateX(420px)}}}}.bshine{{animation:bshine 4s ease-in-out infinite}}"
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
    # ---------------------------------------------------------------- languages: 3D test tubes
    import math
    top = langs[:5]
    vmax = max((v for _, v in top), default=1) or 1
    total = sum(v for _, v in top) or 1
    pal = [c["accent"], c["second"], c["pink"], c["green"], "#F59E0B"]
    css += ("@keyframes rise{0%{transform:translateY(var(--h))}20%,88%{transform:translateY(0)}100%{transform:translateY(var(--h))}}.rise{animation:rise 10s cubic-bezier(.3,.8,.2,1) infinite both}"
            "@keyframes dr{0%{transform:translateY(0) scale(.5);opacity:0}12%{opacity:1;transform:translateY(0) scale(1)}58%{transform:translateY(var(--dy));opacity:1}60%,100%{transform:translateY(var(--dy));opacity:0}}.dr{animation:dr 2.6s ease-in infinite}"
            "@keyframes rpl{0%,58%{transform:scale(.1);opacity:0}60%{opacity:.95}100%{transform:scale(1);opacity:0}}.rpl{transform-box:fill-box;transform-origin:center;animation:rpl 2.6s ease-out infinite}"
            "@keyframes bub{0%{transform:translateY(0) scale(.6);opacity:0}15%{opacity:.8}100%{transform:translateY(var(--by));opacity:0}}.bub{animation:bub 3.4s ease-in infinite}"
            "@keyframes sway{0%,100%{transform:rotate(-2.2deg)}50%{transform:rotate(2.2deg)}}.sway{animation:sway 5s ease-in-out infinite}"
            "@keyframes spk{0%,25%{transform:translateX(-30px)}65%,100%{transform:translateX(60px)}}.spk{animation:spk 4.2s ease-in-out infinite}"
            "@keyframes brth{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.72)}}.brth{transform-box:fill-box;transform-origin:center;animation:brth 2.2s ease-in-out infinite}"
            "@keyframes swl{to{stroke-dashoffset:-60}}.swl{stroke-dasharray:14 46;animation:swl 2.4s linear infinite}"
            "@keyframes fsh{0%,100%{opacity:.28;transform:scale(1)}50%{opacity:.5;transform:scale(1.12)}}.fsh{transform-box:fill-box;transform-origin:center;animation:fsh 5s ease-in-out infinite}"
            "@keyframes nz{0%,100%{transform:translateY(0)}50%{transform:translateY(2px)}}.nz{animation:nz 2.6s ease-in-out infinite}"
            "@keyframes ttl{0%,20%{transform:translateX(-140px)}60%,100%{transform:translateX(360px)}}.ttl{animation:ttl 5s ease-in-out infinite}"
            "@keyframes brush{0%{stroke-dashoffset:200}35%,85%{stroke-dashoffset:0}100%{stroke-dashoffset:-200}}.brush{stroke-dasharray:200;animation:brush 6s ease-in-out infinite}")
    script_f = typo.font(typo.SCRIPT)

    def fancy_title(text, x, y, col, tid):
        td, tw_ = script_f.path(text, 30, x, y)
        return (f'<clipPath id="{tid}"><path d="{td}"/></clipPath><path d="{td}" fill="url(#g1)"/>'
                f'<g clip-path="url(#{tid})"><rect class="ttl" x="{x}" y="{y - 34}" width="46" height="46" fill="#fff" opacity=".7" transform="skewX(-22)"/></g>'
                f'<path class="brush" d="M{x} {y + 10} q{tw_ * .25:.0f} -7 {tw_ * .5:.0f} -2 t{tw_ * .5:.0f} -3" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" pathLength="200"/>'
                f'{star4(x + tw_ + 14, y - 22, 6, col, "tw")}{star4(x + tw_ + 30, y - 6, 4, c["accent"], "tw", "style=" + chr(34) + "animation-delay:-1s" + chr(34))}')

    body += f'<g class="bb" style="animation-delay:-1s">{panel(0, 150, 405, 300, 4)}'
    body += fancy_title("Top Languages", 28, 196, c["accent"], "ttl1")
    TW, TOP, BOT, PITCH = 46, 242, 388, 70
    x_start = 28 + (349 - PITCH * len(top)) / 2 + (PITCH - TW) / 2
    for i, (name, v) in enumerate(top):
        col = pal[i]
        x = x_start + i * PITCH
        r = TW / 2
        cxm = x + r
        lvl = .16 + .78 * math.sqrt(v / vmax)
        ys = BOT - lvl * (BOT - TOP - 10)
        tube = f"M{x} {TOP} V{BOT - r} A{r} {r} 0 0 0 {x + TW} {BOT - r} V{TOP}"
        bubbles = "".join(f'<circle class="bub" cx="{x + 10 + (k * 13) % (TW - 18):.1f}" cy="{BOT - 8 - (k % 2) * 6}" r="{1.6 + k * .5:.1f}" fill="#fff" fill-opacity=".75" style="--by:{-(BOT - ys - 16):.0f}px;animation-delay:{i * .35 + k * 1.1:.2f}s"/>' for k in range(3))
        pctv = 100 * v / total
        nd, nw = lab.path(name, 13.5, 0, 0)
        pd, pw = mono.path(f"{pctv:.1f}%", 12, 0, 0, 1)
        ripples = "".join(f'<ellipse class="rpl" cx="{cxm}" cy="{ys:.1f}" rx="{r - 3}" ry="{(r - 3) * .3:.1f}" fill="none" stroke="#fff" stroke-width="1.5" style="animation-delay:{i * .5 + k * .12:.2f}s"/>' for k in range(2))
        body += (f'<clipPath id="tb{i}"><path d="{tube} Z"/></clipPath>'
                 f'<ellipse class="fsh" cx="{cxm}" cy="{BOT + 4}" rx="{r + 10}" ry="8" fill="{col}" style="animation-delay:-{i * .7:.1f}s"/>'
                 f'<ellipse cx="{cxm}" cy="{BOT + 3}" rx="{r + 3}" ry="5" fill="#000" opacity=".28"/>'
                 f'<g class="nz" style="animation-delay:-{i * .5:.1f}s"><ellipse cx="{cxm}" cy="203" rx="7" ry="8" fill="{col}"/><ellipse cx="{cxm}" cy="203" rx="7" ry="8" fill="url(#cyl)"/><ellipse cx="{cxm - 2.5}" cy="199.5" rx="1.8" ry="3" fill="#fff" opacity=".6"/>'
                 f'<rect x="{cxm - 6.5}" y="208" width="13" height="4" rx="2" fill="{c["muted"]}"/><rect x="{cxm - 6.5}" y="208" width="13" height="4" rx="2" fill="url(#cyl)"/>'
                 f'<path d="M{cxm - 4.5} 212 h9 v9 l-2.4 8 h-4.2 l-2.4 -8z" fill="{c["ink"]}" fill-opacity=".14" stroke="{c["ink"]}" stroke-opacity=".55" stroke-width="1.2" stroke-linejoin="round"/>'
                 f'<path d="M{cxm - 4.5} 212 h9 v9 l-2.4 8 h-4.2 l-2.4 -8z" fill="url(#cyl)" opacity=".8"/><path d="M{cxm - 2.2} 214 v8" stroke="#fff" stroke-opacity=".6" stroke-width="1.6" stroke-linecap="round"/></g>'
                 f'<g class="sway" style="transform-origin:{cxm}px {BOT}px;animation-delay:-{i * .9:.1f}s">'
                 # back of the opening, glass body
                 f'<ellipse cx="{cxm}" cy="{TOP}" rx="{r}" ry="6" fill="{c["page"]}" opacity=".5"/>'
                 f'<path d="{tube} Z" fill="url(#glass)"/>'
                 f'<g clip-path="url(#tb{i})"><g class="rise" style="--h:{BOT - ys + 12:.0f}px;animation-delay:{i * .14:.2f}s">'
                 f'<rect x="{x}" y="{ys:.1f}" width="{TW}" height="{BOT - ys + 4:.1f}" fill="{col}"/>'
                 f'<rect x="{x}" y="{ys:.1f}" width="{TW}" height="{BOT - ys + 4:.1f}" fill="url(#cyl)"/>'
                 # liquid surface seen in perspective
                 f'<ellipse cx="{cxm}" cy="{ys:.1f}" rx="{r - 1}" ry="6" fill="{col}"/><ellipse class="brth" cx="{cxm}" cy="{ys:.1f}" rx="{r - 1}" ry="6" fill="#fff" opacity=".35"/>'
                 f'<ellipse class="swl" cx="{cxm}" cy="{ys:.1f}" rx="{r - 6}" ry="3.2" fill="none" stroke="#fff" stroke-opacity=".8" stroke-width="1.8" stroke-linecap="round" pathLength="60"/>'
                 f'{ripples}{bubbles}</g>'
                 f'<rect class="spk" x="{x}" y="{TOP}" width="9" height="{BOT - TOP}" fill="#fff" opacity=".3" transform="skewX(-8)"/></g>'
                 f'<path d="{tube}" fill="none" stroke="{c["ink"]}" stroke-opacity=".5" stroke-width="2.2" stroke-linecap="round"/>'
                 f'<ellipse cx="{cxm}" cy="{TOP}" rx="{r + 2.5}" ry="6.5" fill="none" stroke="{c["ink"]}" stroke-opacity=".7" stroke-width="2.4"/>'
                 f'<path d="M{x + 6} {TOP + 14} V{BOT - 26}" stroke="#fff" stroke-opacity=".45" stroke-width="3" stroke-linecap="round"/></g>'
                 f'<g class="dr" style="--dy:{ys - 238:.0f}px;animation-delay:{i * .5:.1f}s"><path d="M{cxm} 229 q-4.5 6.5 -4.5 10 a4.5 4.5 0 0 0 9 0 q0 -3.5 -4.5 -10z" fill="{col}"/>'
                 f'<path d="M{cxm} 229 q-4.5 6.5 -4.5 10 a4.5 4.5 0 0 0 9 0 q0 -3.5 -4.5 -10z" fill="url(#dsh)"/><ellipse cx="{cxm - 1.7}" cy="238" rx="1.1" ry="1.9" fill="#fff" opacity=".85"/></g>'
                 f'<path d="{nd}" transform="translate({cxm - nw / 2:.1f} 416)" fill="{c["ink"]}"/>'
                 f'<path d="{pd}" transform="translate({cxm - pw / 2:.1f} 436)" fill="{col}"/>')
    body += "</g>"
    # ---------------------------------------------------------------- streak
    cur = streak["current"]
    marks = [7, 14, 30, 50, 100, 200, 300, 365, 500, 750, 1000, 2000]
    nxt = next((m for m in marks if m > cur), cur + 1)
    frac = max(cur / nxt, .02)
    cx, cy, r = 425 + 108, 296, 60
    circ = 2 * math.pi * r
    nt = 60
    lit = int(round(frac * nt))
    ticks = ""
    for k in range(nt):
        a = k / nt * 2 * math.pi - math.pi / 2
        x1, y1, x2, y2 = (cx + (r + 14) * math.cos(a), cy + (r + 14) * math.sin(a), cx + (r + (22 if k % 5 == 0 else 19)) * math.cos(a), cy + (r + (22 if k % 5 == 0 else 19)) * math.sin(a))
        if k < lit:
            ticks += f'<line class="tk" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{[c["accent"], c["second"], c["pink"]][k * 3 // nt]}" stroke-width="2.4" stroke-linecap="round" style="animation-delay:{k * .05:.2f}s"/>'
        else:
            ticks += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c["line"]}" stroke-width="2" stroke-linecap="round"/>'
    css += ("@keyframes tk{0%,100%{opacity:.35}40%{opacity:1}}.tk{animation:tk 3s ease-in-out infinite}"
            "@keyframes cmtr{to{stroke-dashoffset:-" + f"{circ:.0f}" + "}}.cmtr{animation:cmtr 3.2s linear infinite}"
            "@keyframes emb{0%{transform:translate(0,0) scale(1);opacity:0}15%{opacity:1}100%{transform:translate(var(--ex),-58px) scale(.2);opacity:0}}.emb{animation:emb 2.4s ease-out infinite}"
            "@keyframes aura{0%,100%{opacity:.18;transform:scale(1)}50%{opacity:.42;transform:scale(1.15)}}.aura{transform-box:fill-box;transform-origin:center;animation:aura 2.2s ease-in-out infinite}"
            "@keyframes wob{0%,100%{transform:rotate(-3deg)}50%{transform:rotate(3deg)}}.wob{transform-box:fill-box;transform-origin:bottom;animation:wob 2.2s ease-in-out infinite}"
            "@keyframes sweep{0%,20%{transform:translateX(0)}70%,100%{transform:translateX(220px)}}.sweep{animation:sweep 4.5s ease-in-out infinite}")
    script, scr_w = typo.font(typo.SCRIPT).path("day streak", 17, 0, 0)
    num = str(cur)
    nsize = 54
    nw_ = sum(big.advance(ch, nsize) for ch in num)
    digits, dcss = _roll(num, cx - nw_ / 2, cy + 24, nsize, big, "sk", 0.4)
    css += dcss
    embers = "".join(f'<circle class="emb" cx="{cx + (k - 2.5) * 6}" cy="{cy - 36}" r="{1.4 + (k % 3) * .5:.1f}" fill="{[c["pink"], c["accent"], "#F59E0B"][k % 3]}" style="--ex:{(k - 2.5) * 5:.0f}px;animation-delay:{k * .4:.1f}s"/>' for k in range(6))
    body += f'<g class="bb" style="animation-delay:-2s">{panel(425, 150, 405, 300, 5)}'
    body += fancy_title("Contribution Streak", 453, 196, c["pink"], "ttl2")
    body += (f'<circle class="aura" cx="{cx}" cy="{cy}" r="{r + 4}" fill="url(#aura)"/>{ticks}'
             f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c["line"]}" stroke-width="10"/>'
             f'<circle class="rg" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#g1)" stroke-width="10" stroke-linecap="round" stroke-dasharray="{circ:.0f}" '
             f'style="--full:{circ:.0f};--off:{circ * (1 - frac):.0f}" transform="rotate(-90 {cx} {cy})"/>'
             f'<circle class="cmtr" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#fff" stroke-opacity=".85" stroke-width="3" stroke-linecap="round" stroke-dasharray="14 {circ - 14:.0f}"/>'
             f'{embers}<g transform="translate({cx} {cy - 44}) scale(1.2)"><g class="flame"><path d="M0 -22 C10 -10 14 -2 8 8 C5 13 -5 13 -8 8 C-14 -2 -8 -10 0 -22Z" fill="url(#g1)"/>'
             f'<path d="M0 -6 C5 0 6 4 3 8 C1 10 -1 10 -3 8 C-6 4 -4 0 0 -6Z" fill="{c["page"]}" opacity=".55"/></g></g>'
             f'{digits}<path d="{script}" transform="translate({cx - scr_w / 2:.1f} {cy + 45})" fill="url(#g1)"/>')
    # milestone line
    msg = f"{nxt - cur} days to {nxt}" if cur < nxt else "keep it going"
    md, mw = mono.path(msg.upper(), 10, 0, 0, 2)
    body += (f'<path d="{md}" transform="translate({cx - mw / 2:.1f} 408)" fill="{c["muted"]}"/>'
             f'<rect x="{cx - 80}" y="418" width="160" height="6" rx="3" fill="{c["line"]}"/>'
             f'<clipPath id="mb"><rect x="{cx - 80}" y="418" width="{160 * frac:.0f}" height="6" rx="3"/></clipPath><rect x="{cx - 80}" y="418" width="{160 * frac:.0f}" height="6" rx="3" fill="url(#g1)"/>'
             f'<g clip-path="url(#mb)"><rect class="bshine" x="{cx - 100}" y="418" width="20" height="6" fill="#fff" opacity=".7" transform="skewX(-25)"/></g>')
    # side cards
    for i, (val, label, col, kind) in enumerate([(streak["longest"], "LONGEST STREAK", c["second"], "trophy"), (streak["total"], "CONTRIBUTIONS", c["accent"], "grid")]):
        y = 214 + i * 96
        px = 668
        sdig, scss = _roll(str(val), px + 18, y + 67, 28, big, f"sc{i}", 0.6 + i * .25)
        css += scss
        if kind == "trophy":
            glyph = (f'<path d="M{px + 18} {y + 18} h20 v10 a10 10 0 0 1 -20 0z M{px + 18} {y + 21} h-6 a6 6 0 0 0 6 10 M{px + 38} {y + 21} h6 a6 6 0 0 1 -6 10 M{px + 28} {y + 38} v6 M{px + 21} {y + 45} h14" '
                     f'fill="none" stroke="{col}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
        else:
            glyph = "".join(f'<rect class="tk" x="{px + 14 + gx * 11}" y="{y + 18 + gy * 11}" width="8" height="8" rx="2" fill="{col}" opacity="{.35 + .2 * ((gx + gy) % 3)}" style="animation-delay:{(gx + gy) * .25:.2f}s"/>' for gx in range(3) for gy in range(3))
        ld, _ = mono.path(label, 8.5, px + 58, y + 34, 1.4)
        body += (f'<rect x="{px + .5}" y="{y + .5}" width="147" height="75" rx="18" fill="{col}" fill-opacity=".07" stroke="{col}" stroke-opacity=".55"/>'
                 f'<clipPath id="sk{i}"><rect x="{px}" y="{y}" width="148" height="76" rx="18"/></clipPath><g clip-path="url(#sk{i})"><rect class="sweep" x="{px - 70}" y="{y}" width="24" height="76" fill="{col}" opacity=".16" transform="skewX(-20)" style="animation-delay:{i * 1.3:.1f}s"/></g>'
                 f'<g transform="translate(0 -8)">{glyph}</g><path d="{ld}" fill="{col}" transform="translate(0 -8)"/>{sdig}')
    body += star4(790, 190, 6, c["accent"], "tw") + "</g>"
    defs_extra = (f'<radialGradient id="dsh" cx=".35" cy=".65" r=".75"><stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".42"/></radialGradient>'
                  + f'<linearGradient id="cyl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".38"/><stop offset=".22" stop-color="#fff" stop-opacity=".22"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></linearGradient>'
                  f'<linearGradient id="glass" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["ink"]}" stop-opacity=".16"/><stop offset=".3" stop-color="{c["ink"]}" stop-opacity=".03"/><stop offset="1" stop-color="{c["ink"]}" stop-opacity=".12"/></linearGradient>'
                  + f'<linearGradient id="shade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".25"/><stop offset=".35" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".28"/></linearGradient>'
                  f'<radialGradient id="aura"><stop offset="0" stop-color="{c["pink"]}" stop-opacity=".5"/><stop offset="1" stop-color="{c["pink"]}" stop-opacity="0"/></radialGradient>')
    return doc(W, H, body, css, _grad(c, "g1") + defs_extra, "GitHub stats: commits, pull requests, stars, followers, top languages and contribution streak", pad_y=8)


def main() -> None:
    login = os.environ.get("GITHUB_REPOSITORY_OWNER", OWNER)
    stats, langs = fetch_overview(login)
    streak = compute_streaks(fetch_days(login), dt.datetime.now(dt.timezone.utc).date())
    print(stats, langs[:5], streak)
    for m in MODES:
        write(OUT / "stats" / f"dashboard-{m}.svg", dashboard_svg(m, stats, langs, streak))


if __name__ == "__main__":
    main()
