# How this profile is built

Everything on the README is generated, so it stays consistent in dark and light mode.

| Command | Regenerates |
|---|---|
| `python scripts/poster/build.py` | header, footer, hero, section titles, toolbox, project cards, contact pills, **README.md** (no network) |
| `python scripts/ascii/build_svg.py` | the animated ASCII portrait (SVG + GIF), see `scripts/ascii/README.md` |
| `python scripts/cards.py` | the stats dashboard (needs `GITHUB_TOKEN` or `gh auth login`) |
| `python scripts/greeting.py` | the live Kolkata greeting |

Text in every SVG is converted to outlines with `fontTools` (`scripts/typo.py`), because web fonts do not load
inside `<img>` SVGs. Fonts are in `scripts/fonts` (SIL Open Font License); brand icons come from
[simple-icons](https://simpleicons.org) (CC0). Dev aids: `snap.py` (deterministic SVG snapshots through Chrome),
`sheet.py` (contact sheet), `preview_readme.py` (README preview). Tests: `python -m pytest`.

Content lives in `scripts/poster/*.py` (toolbox tiles in `work.ROWS`, projects in `work.PROJECTS`, copy in `hero.py`).
