"""'What should I build next?' poll driven by issues titled `poll|vote|<n>`.

One vote per GitHub user (votes are stored by login in data/poll.json); the bar chart is
re-rendered to assets/cards/poll-{dark,light}.svg and the README block is rewritten.

    python scripts/poll.py            # reads ISSUE_* env vars
    python scripts/poll.py --render   # redraw chart + README from data/poll.json
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import DATA, ROOT, Event, issue_link, load_json, now_utc, rate_limited, respond, save_json, update_readme  # noqa: E402
from theme import MONO, PROMPT, THEMES  # noqa: E402
from svgkit import esc  # noqa: E402

STATE = DATA / "poll.json"
CARDS = ROOT / "assets" / "cards"
TITLE_RE = re.compile(r"poll\|vote\|([0-9])")
DEFAULT = {
    "question": "What should I build next?",
    "options": ["An AI / LLM app", "A developer tool or CLI", "A game or creative project"],
    "votes": {},   # login (lower-case) -> option index
    "rate": {},
}


def tally(state: dict) -> list[int]:
    counts = [0] * len(state["options"])
    for v in state["votes"].values():
        if 0 <= v < len(counts):
            counts[v] += 1
    return counts


def cast(state: dict, user: str, option: int) -> tuple[bool, str]:
    if not 0 <= option < len(state["options"]):
        return False, "That option does not exist."
    key = user.lower()
    if key in state["votes"]:
        return False, f"You already voted for \"{state['options'][state['votes'][key]]}\" - one vote per person."
    state["votes"][key] = option
    return True, f"Vote recorded for \"{state['options'][option]}\". Thanks, @{user}!"


def chart_svg(state: dict, mode: str) -> str:
    c = THEMES[mode]
    counts = tally(state)
    total = sum(counts) or 1
    W, bar_x, bar_w = 560, 20, 340
    H = 64 + 44 * len(counts)
    top = max(counts) if counts else 0
    rows = []
    for i, (label, n) in enumerate(zip(state["options"], counts)):
        y = 58 + 44 * i
        w = bar_w * n / total
        col = c["accent"] if n == top and n > 0 else c["second"]
        rows.append(
            f'<text x="{bar_x}" y="{y}" font-size="13" fill="{c["text"]}">{esc(label)}</text>'
            f'<rect x="{bar_x}" y="{y + 8}" width="{bar_w}" height="12" rx="6" fill="{c["line"]}"/>'
            f'<rect class="b" x="{bar_x}" y="{y + 8}" width="{max(w, 0):.1f}" height="12" rx="6" fill="{col}" style="animation-delay:{i * .12:.2f}s"/>'
            f'<text x="{bar_x + bar_w + 14}" y="{y + 19}" font-size="13" fill="{c["muted"]}">{n} ({100 * n // total if sum(counts) else 0}%)</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Poll results: '
            f'{esc(state["question"])}"><style>text{{font-family:{MONO}}}@keyframes g{{from{{transform:scaleX(0)}}}}'
            f'.b{{transform-box:fill-box;transform-origin:left;animation:g .8s ease-out both}}'
            f'@media (prefers-reduced-motion: reduce){{.b{{animation:none}}}}</style>'
            f'<rect width="{W}" height="{H}" rx="10" fill="{c["bg"]}"/>'
            f'<text x="{bar_x}" y="30" font-size="14" font-weight="700" fill="{c["accent"]}">{PROMPT} poll --results</text>'
            f'{"".join(rows)}</svg>')


def block(state: dict) -> str:
    links = " &#183; ".join(
        f'<a href="{issue_link(f"poll|vote|{i}", "Press Submit new issue to cast your vote (one per person).")}">{esc(o)}</a>'
        for i, o in enumerate(state["options"]))
    n = len(state["votes"])
    return (f'<div align="center">\n<b>{esc(state["question"])}</b><br>\n'
            f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/cards/poll-dark.svg">'
            f'<source media="(prefers-color-scheme: light)" srcset="assets/cards/poll-light.svg">'
            f'<img alt="Poll results" src="assets/cards/poll-light.svg" width="560"></picture><br>\n'
            f'<sub>vote: {links}</sub><br>\n<sub>{n} vote{"s" if n != 1 else ""} so far &#183; one vote per person &#183; the chart updates ~60 s after you vote</sub>\n</div>')


def write_outputs(state: dict) -> None:
    CARDS.mkdir(parents=True, exist_ok=True)
    for mode in ("dark", "light"):
        (CARDS / f"poll-{mode}.svg").write_text(chart_svg(state, mode), encoding="utf-8")
    update_readme("poll", block(state))


def main(argv: list[str]) -> int:
    state = load_json(STATE, None) or {**DEFAULT, "votes": {}, "rate": {}}
    if "--render" in argv:
        write_outputs(state)
        save_json(STATE, state)
        return 0
    ev = Event()
    m = TITLE_RE.fullmatch(ev.title)
    if not m or not ev.valid_user:
        respond(ev.number, "Sorry, I could not understand that request (or it came from a bot). Use the vote links in the README.")
        return 0
    if rate_limited(state["rate"], ev.user, now_utc()):
        respond(ev.number, "Easy there - one action per minute. Try again shortly.")
        save_json(STATE, state)
        return 0
    _, msg = cast(state, ev.user, int(m.group(1)))
    save_json(STATE, state)
    write_outputs(state)
    respond(ev.number, msg + "\n\nThe chart refreshes within about a minute.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
