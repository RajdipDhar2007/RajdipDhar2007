"""Stats / languages / streak cards rendered in the Terminal Noir palette.

* `streak`  - used by .github/workflows/stats.yml (no maintained streak Action exists).
* `seed`    - stats + langs cards written once locally so the README renders before
              the first workflow run; the github-readme-stats Action overwrites them.

    python scripts/cards.py streak            # needs GITHUB_TOKEN (or `gh auth login`)
    python scripts/cards.py seed
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
from theme import THEMES, MONO, OWNER, PROMPT  # noqa: E402
from svgkit import esc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_LANGS = {"Jupyter Notebook"}  # notebook output dwarfs real code; mirrored by `hide=` in stats.yml
REDUCE = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def token() -> str:
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def gql(query: str, **variables) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json", "User-Agent": "profile-cards"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


# ---------------------------------------------------------------- streak maths
def compute_streaks(days: dict[str, int], today: dt.date) -> dict:
    """days: ISO date -> contribution count. Pure function (unit-tested)."""
    dates = sorted(days)
    total = sum(days.values())
    longest = run = 0
    longest_end = None
    prev = None
    for d in dates:
        cur = dt.date.fromisoformat(d)
        if days[d] > 0:
            run = run + 1 if prev and (cur - prev).days == 1 else 1
            prev = cur
            if run > longest:
                longest, longest_end = run, cur
        else:
            run, prev = 0, None
    # current streak: walk back from today (today may still be empty)
    cur_streak, d = 0, today
    if days.get(d.isoformat(), 0) == 0:
        d -= dt.timedelta(days=1)
    while days.get(d.isoformat(), 0) > 0:
        cur_streak += 1
        d -= dt.timedelta(days=1)
    return {"total": total, "current": cur_streak, "longest": longest, "longest_end": longest_end}


def fetch_days(login: str) -> dict[str, int]:
    created = gql("query($l:String!){user(login:$l){createdAt}}", l=login)["user"]["createdAt"][:4]
    days: dict[str, int] = {}
    now = dt.datetime.now(dt.timezone.utc)
    for year in range(int(created), now.year + 1):
        d = gql(
            "query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){contributionsCollection(from:$f,to:$t)"
            "{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}",
            l=login, f=f"{year}-01-01T00:00:00Z", t=f"{year}-12-31T23:59:59Z")
        for w in d["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for day in w["contributionDays"]:
                days[day["date"]] = day["contributionCount"]
    return days


# ------------------------------------------------------------------ rendering
def frame(c: dict, w: int, h: int, title: str, body: str, extra_css: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
            f'<style>text{{font-family:{MONO}}}.t{{fill:{c["accent"]};font-size:14px;font-weight:700}}'
            f'@keyframes in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}.in{{animation:in .8s ease-out both}}'
            f'{extra_css}{REDUCE}</style>'
            f'<rect width="{w}" height="{h}" rx="10" fill="{c["bg"]}"/>'
            f'<text class="t" x="20" y="30">{PROMPT} {esc(title)}</text>{body}</svg>')


def streak_svg(mode: str, s: dict) -> str:
    c = THEMES[mode]
    W, H = 495, 195
    cols = [(82, s["total"], "contributions", c["text"]), (247, s["current"], "current streak", c["accent"]),
            (412, s["longest"], "longest streak", c["second"])]
    out = []
    for i, (x, v, lab, col) in enumerate(cols):
        out.append(f'<g class="in" style="animation-delay:{i * .15:.2f}s"><text x="{x}" y="108" text-anchor="middle" font-size="30" font-weight="700" fill="{col}">{v}</text>'
                   f'<text x="{x}" y="168" text-anchor="middle" font-size="12" fill="{c["muted"]}">{lab}</text></g>')
    out.append(f'<circle cx="247" cy="98" r="40" fill="none" stroke="{c["line"]}" stroke-width="4"/>'
               f'<circle class="ring" cx="247" cy="98" r="40" fill="none" stroke="{c["accent"]}" stroke-width="4" stroke-linecap="round" '
               f'stroke-dasharray="251" stroke-dashoffset="{251 * (1 - min(s["current"], 7) / 7):.0f}" transform="rotate(-90 247 98)"/>')
    out.append(f'<line x1="165" y1="60" x2="165" y2="165" stroke="{c["line"]}"/><line x1="330" y1="60" x2="330" y2="165" stroke="{c["line"]}"/>')
    return frame(c, W, H, "git streak", "".join(out), ".ring{animation:r 1.4s ease-out both}@keyframes r{from{stroke-dashoffset:251}}")


def stats_svg(mode: str, d: dict) -> str:
    c = THEMES[mode]
    rows = [("Total commits (this year)", d["commits"]), ("Pull requests", d["prs"]), ("Stars earned", d["stars"]), ("Followers", d["followers"])]
    body = "".join(
        f'<g class="in" style="animation-delay:{i * .12:.2f}s"><text x="20" y="{70 + i * 30}" font-size="13" fill="{c["text"]}">{esc(k)}</text>'
        f'<text x="475" y="{70 + i * 30}" font-size="13" font-weight="700" text-anchor="end" fill="{c["accent"]}">{v}</text></g>'
        for i, (k, v) in enumerate(rows))
    return frame(c, 495, 195, f"git stats {OWNER}", body)


def langs_svg(mode: str, langs: list[tuple[str, int]]) -> str:
    c = THEMES[mode]
    total = sum(v for _, v in langs) or 1
    x, bar, leg = 20, [], []
    palette = [c["accent"], c["second"], c["green"], "#F59E0B", "#F472B6", "#94A3B8"]
    for i, (name, v) in enumerate(langs[:6]):
        w = 455 * v / total
        col = palette[i % len(palette)]
        bar.append(f'<rect x="{x:.1f}" y="52" width="{max(w, 2):.1f}" height="10" fill="{col}"/>')
        x += w
        lx, ly = 20 + (i % 2) * 230, 96 + (i // 2) * 28
        leg.append(f'<g class="in" style="animation-delay:{i * .1:.1f}s"><circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{col}"/>'
                   f'<text x="{lx + 18}" y="{ly}" font-size="13" fill="{c["text"]}">{esc(name)}</text>'
                   f'<text x="{lx + 200}" y="{ly}" font-size="13" text-anchor="end" fill="{c["muted"]}">{100 * v / total:.1f}%</text></g>')
    return frame(c, 495, 195, "git langs --top", f'<clipPath id="cp"><rect x="20" y="52" width="455" height="10" rx="5"/></clipPath><g clip-path="url(#cp)">{"".join(bar)}</g>{"".join(leg)}')


def fetch_overview(login: str):
    d = gql("""query($l:String!){user(login:$l){followers{totalCount} pullRequests{totalCount}
      contributionsCollection{totalCommitContributions}
      repositories(ownerAffiliations:OWNER,isFork:false,first:100,privacy:PUBLIC){nodes{stargazerCount
      languages(first:8,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}""", l=login)["user"]
    langs: dict[str, int] = {}
    for r in d["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            if e["node"]["name"] in EXCLUDE_LANGS:
                continue
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    return ({"commits": d["contributionsCollection"]["totalCommitContributions"], "prs": d["pullRequests"]["totalCount"],
             "stars": sum(r["stargazerCount"] for r in d["repositories"]["nodes"]), "followers": d["followers"]["totalCount"]},
            sorted(langs.items(), key=lambda kv: -kv[1]))


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main(argv=None):
    cmd = (argv or sys.argv[1:] or ["streak"])[0]
    login = os.environ.get("GITHUB_REPOSITORY_OWNER", OWNER)
    if cmd == "streak":
        s = compute_streaks(fetch_days(login), dt.datetime.now(dt.timezone.utc).date())
        for mode in ("dark", "light"):
            write(ROOT / "profile" / f"streak-{mode}.svg", streak_svg(mode, s))
        write(ROOT / "profile" / "streak.svg", streak_svg("light", s))
        print("streak", s)
    elif cmd == "seed":
        stats, langs = fetch_overview(login)
        for mode in ("dark", "light"):
            write(ROOT / "assets" / "cards" / f"stats-{mode}.svg", stats_svg(mode, stats))
            write(ROOT / "assets" / "cards" / f"langs-{mode}.svg", langs_svg(mode, langs))
        print("seeded", stats, langs[:6])
    else:
        sys.exit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
