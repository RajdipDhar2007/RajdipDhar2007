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


def dashboard_svg(mode: str, stats: dict, langs: list[tuple[str, int]], streak: dict) -> str:
    c = PAL[mode]
    W, H, T = 830, 470, 10.0
    big, lab, mono, body_f = typo.font(typo.DISPLAY), typo.font(typo.MEDIUM), typo.font(typo.MONO_B), typo.font(typo.BODY)
    css = (f"@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}.bb{{animation:bob 5s ease-in-out infinite}}"
           f"@keyframes grow{{0%{{transform:scaleX(0)}}12%,86%{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}}}.gr{{transform-box:fill-box;transform-origin:left;animation:grow {T}s cubic-bezier(.3,.8,.2,1) infinite}}"
           f"@keyframes ring{{0%{{stroke-dashoffset:var(--full)}}15%,86%{{stroke-dashoffset:var(--off)}}100%{{stroke-dashoffset:var(--full)}}}}.rg{{animation:ring {T}s cubic-bezier(.3,.8,.2,1) infinite}}"
           f"@keyframes run{{to{{stroke-dashoffset:-400}}}}.run{{stroke-dasharray:80 320;animation:run 6s linear infinite}}" + _tw())
    body = ""

    def panel(x, y, w, h, i):
        return (f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="24" fill="{c["card"]}" stroke="{c["line"]}"/>'
                f'<rect class="run" x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="24" fill="none" stroke="url(#g1)" stroke-width="2.2" pathLength="400" style="animation-delay:-{i * 1.4:.1f}s"/>')

    tiles = [("commits", "commits this year", c["accent"], lambda x, y: icon("git", x, y, 26, c["accent"])),
             ("prs", "pull requests", c["second"], lambda x, y: icon("github", x, y, 26, c["second"])),
             ("stars", "stars earned", c["pink"], lambda x, y: _star5(x + 13, y + 13, 14, c["pink"])),
             ("followers", "followers", c["green"], lambda x, y: _people(x + 13, y + 14, c["green"]))]
    for i, (key, label, col, ic) in enumerate(tiles):
        x = i * 213
        nd, nw = big.path(str(stats[key]), 44, 0, 0)
        ld, _ = lab.path(label, 13.5, x + 24, 108)
        body += (f'<g class="bb" style="animation-delay:-{i * .9:.1f}s">{panel(x, 8, 190, 120, i)}<circle cx="{x + 150}" cy="48" r="26" fill="{col}" opacity=".12"/>'
                 f'{ic(x + 24, 34)}<path d="{nd}" transform="translate({x + 24} 100)" fill="{col}" opacity="0"/>'
                 f'</g>')
        # number is placed below the icon; label under it
        nd2, _ = big.path(str(stats[key]), 40, x + 24, 96)
        body = body.replace(f'<path d="{nd}" transform="translate({x + 24} 100)" fill="{col}" opacity="0"/>', f'<path d="{nd2}" fill="url(#g1)"/>')
        body = body.replace('</g>', f'<path d="{lab.path(label, 13, x + 24, 118)[0]}" fill="{c["muted"]}"/></g>', 1) if False else body
        body += f'<path d="{lab.path(label, 13, x + 24, 118)[0]}" fill="{c["muted"]}"/>'
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
