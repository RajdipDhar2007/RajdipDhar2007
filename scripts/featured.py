"""Featured work + "more repositories", driven by what is pinned on the GitHub profile.

    python scripts/featured.py     # needs GITHUB_TOKEN / GH_TOKEN (or `gh auth login` locally)

Pin or unpin repositories on the profile and the next run (hourly in Actions) rebuilds the project
cards, their download / open buttons and the "more from my repositories" pills, and rewrites the
FEATURED and MORE blocks of README.md.
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from poster.common import MODES, OUT  # noqa: E402
from poster import work  # noqa: E402
from poster.common import write  # noqa: E402
from cards import gql, OWNER  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PROFILE_REPO = OWNER
ICONS = {"python": "python", "typescript": "typescript", "javascript": "javascript", "kotlin": "kotlin", "c": "c", "html": "html",
         "jupyter notebook": "jupyter", "solidity": "solidity", "css": "html", "vue": "vite"}
CURATED_ART = {"ultimatecraft": "ultimatecraft", "loci": "loci", "attendtrack": "attendtrack", "meridian": "meridian"}
ART_BY_LANG = {"c": "ultimatecraft", "c++": "ultimatecraft", "kotlin": "attendtrack", "java": "attendtrack", "swift": "attendtrack",
               "typescript": "loci", "solidity": "chain", "python": "terminal", "javascript": "terminal", "html": "terminal", "css": "terminal"}
GLYPHS = ["task", "sigma", "game", "atom"]

QUERY = """query($l:String!){user(login:$l){
  pinnedItems(first:6,types:REPOSITORY){nodes{... on Repository{...F}}}
  repositories(first:30,ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,orderBy:{field:PUSHED_AT,direction:DESC}){nodes{...F}}}}
fragment F on Repository{name description homepageUrl url isArchived
  primaryLanguage{name} languages(first:3,orderBy:{field:SIZE,direction:DESC}){nodes{name}}
  latestRelease{releaseAssets(first:20){nodes{name downloadUrl}}}}"""


def pretty(name: str) -> str:
    words = re.sub(r"[_-]+", " ", name).split()
    return " ".join(words[:2]) if len(" ".join(words)) > 16 else " ".join(words)


def pill_name(name: str) -> str:
    full = " ".join(re.sub(r"[_-]+", " ", name).split())
    return full if len(full) <= 26 else full[:25].rstrip() + "..."


def pick_asset(assets: list[dict]) -> tuple[str, str] | None:
    """Best installable release asset as (url, sub-label), or None."""
    def rank(a):
        n = a["name"].lower()
        order = [(n.endswith(".apk"), 0, "ANDROID  ·  APK INSTALLER"), (n.endswith(".msi"), 1, "WINDOWS  ·  INSTALLER"),
                 (n.endswith(".exe") and "setup" in n, 1, "WINDOWS  ·  INSTALLER"), (n.endswith(".exe"), 2, "WINDOWS  ·  EXE"),
                 (n.endswith(".zip") and ("win" in n), 3, "WINDOWS  ·  ZIP BUILD"), (n.endswith(".dmg"), 4, "MACOS  ·  DMG"),
                 (n.endswith(".zip"), 5, "ZIP  ·  BUILD"), (n.endswith(".appimage"), 6, "LINUX  ·  APPIMAGE"),
                 (n.endswith((".tar.gz", ".tgz")), 7, "LINUX  ·  TAR.GZ")]
        for ok, r, label in order:
            if ok:
                return r, label
        return 99, ""
    best = min(assets, key=lambda a: rank(a)[0], default=None)
    if not best or rank(best)[0] == 99:
        return None
    return best["downloadUrl"], rank(best)[1]


def project(node: dict, idx: int) -> dict:
    langs = [n["name"] for n in node["languages"]["nodes"]] or ([node["primaryLanguage"]["name"]] if node["primaryLanguage"] else [])
    prim = (langs[0] if langs else "").lower()
    key = re.sub(r"[^a-z0-9]+", "", node["name"].lower()) or f"repo{idx}"
    icon = ICONS.get(prim, "github")
    art = CURATED_ART.get(key) or ("chain" if "solidity" in [l.lower() for l in langs] else None) or ART_BY_LANG.get(prim) or ["terminal", "chain", "loci", "meridian"][idx % 4]
    desc = (node["description"] or "No description yet.").strip()
    desc = re.sub(r"\s+", " ", desc)
    if len(desc) > 150:
        desc = desc[:147].rsplit(" ", 1)[0] + "..."
    got = pick_asset((node.get("latestRelease") or {}).get("releaseAssets", {}).get("nodes", []))
    home = node.get("homepageUrl") or ""
    if got:
        band = dict(kind="download", sub=got[1], url=got[0])
    elif home and "/releases" not in home:
        band = dict(kind="live", sub="WEBSITE  ·  LIVE", url=home)
    else:
        band = dict(kind="repo", sub="SOURCE  ·  README  ·  STARS", url=node["url"])
    return dict(key=key, art=art, name=pretty(node["name"]), repo=node["name"], url=node["url"], icon=icon, chips=langs[:3] or ["Code"], desc=desc, band=band)


def build_featured(projects: list[dict]) -> str:
    sys.path.insert(0, str(Path(__file__).parent / "poster"))
    from poster.readme import card
    cells = [card(p["key"], p["name"], p["band"]["url"], p["url"]) for p in projects]
    rows = []
    for i in range(0, len(cells), 2):
        pair = cells[i:i + 2] + ['<td width="50%"></td>'] * (2 - len(cells[i:i + 2]))
        rows.append("<tr>\n" + "\n".join(pair) + "\n</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def build_more(others: list[dict]) -> str:
    from poster.readme import pic
    items = [(o["name"], o["url"]) for o in others] + [("and more repositories", f"https://github.com/{OWNER}?tab=repositories")]
    out = []
    for k, (alt, url) in enumerate(items):
        img = pic("assets/sections/more-" + str(k) + "-{m}.svg", alt, "", 'align="top"').replace(' width=""', "")
        out.append(f'<a href="{url}">{img}</a>')
    return "\n".join(out)


def replace_block(text: str, name: str, content: str) -> str:
    pat = re.compile(rf"(<!-- {name}:START -->\n).*?(\n<!-- {name}:END -->)", re.S)
    if not pat.search(text):
        raise SystemExit(f"README.md has no {name} block (run scripts/poster/readme.py once)")
    return pat.sub(lambda m: m.group(1) + content + m.group(2), text)


def main() -> None:
    login = os.environ.get("GITHUB_REPOSITORY_OWNER", OWNER)
    u = gql(QUERY, l=login)["user"]
    pinned = [n for n in u["pinnedItems"]["nodes"] if n]
    pinned_names = {n["name"] for n in pinned}
    projects = [project(n, i) for i, n in enumerate(pinned)]
    others = [n for n in u["repositories"]["nodes"] if n["name"] not in pinned_names and n["name"] != PROFILE_REPO and not n["isArchived"]][:4]
    print("pinned:", [p["repo"] for p in projects], "| more:", [o["name"] for o in others])

    keep = set()
    for i, p in enumerate(projects):
        for m in MODES:
            write(OUT / "projects" / f"{p['key']}-{m}.svg", work.project_card(p, m, i))
            write(OUT / "projects" / f"{p['key']}-band-{m}.svg", work.action_band(p, m, i))
            keep |= {f"{p['key']}-{m}.svg", f"{p['key']}-band-{m}.svg"}
    for f in (OUT / "projects").glob("*.svg"):
        if f.name not in keep:
            f.unlink()
    more = [dict(name=pill_name(o["name"]), url=o["url"], kind=GLYPHS[i % len(GLYPHS)]) for i, o in enumerate(others)]
    more.append(dict(name="and more", url=f"https://github.com/{login}?tab=repositories", kind="plus"))
    for k in range(8):                                             # drop stale pills
        for m in MODES:
            (OUT / "sections" / f"more-{k}-{m}.svg").unlink(missing_ok=True)
    for k, o in enumerate(more):
        for m in MODES:
            write(OUT / "sections" / f"more-{k}-{m}.svg", work.repo_pill(o["name"], o["kind"], k % 5, m))

    text = README.read_text(encoding="utf-8")
    text = replace_block(text, "FEATURED", build_featured(projects))
    text = replace_block(text, "MORE", build_more([dict(name=o["name"], url=o["url"]) for o in others]))
    README.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
