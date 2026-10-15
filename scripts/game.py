"""Tic-tac-toe vs the bot, played through GitHub issues.

Trigger: an issue titled `ttt|move|<0-8>` (play X) or `ttt|new|0` (start a new game).
The human is always X and moves first; the bot is O and answers with minimax (with a small
blunder rate so that winning is possible and the leaderboard has meaning).

    python scripts/game.py            # reads ISSUE_* env vars, updates data/, assets/, README.md
    python scripts/game.py --assets   # (re)generate assets/game/*.svg
    python scripts/game.py --render   # re-render the README block from data/game.json
"""
from __future__ import annotations
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import (DATA, ROOT, Event, issue_link, load_json, now_utc, rate_limited, respond,  # noqa: E402
                    save_json, update_readme)
from theme import DARK, MONO  # noqa: E402

STATE = DATA / "game.json"
ASSETS = ROOT / "assets" / "game"
TITLE_RE = re.compile(r"ttt\|(move|new)\|([0-8])")
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
HUMAN, BOT = "X", "O"
BLUNDER_RATE = 0.15  # chance that the bot plays a random legal move instead of the best one
HISTORY = 5


def fresh_state(keep: dict | None = None) -> dict:
    keep = keep or {}
    return {
        "board": [""] * 9,
        "status": "playing",          # playing | won | lost | draw
        "player": None,               # who is playing the current game
        "history": keep.get("history", []),
        "totals": keep.get("totals", {"human": 0, "bot": 0, "draw": 0}),
        "rate": keep.get("rate", {}),
    }


def winner(board: list[str]) -> str | None:
    for a, b, c in LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None


def moves(board: list[str]) -> list[int]:
    return [i for i, v in enumerate(board) if not v]


def minimax(board: list[str], turn: str) -> tuple[int, int | None]:
    """Score from the bot's point of view: +1 bot wins, -1 human wins, 0 draw."""
    w = winner(board)
    if w:
        return (1 if w == BOT else -1), None
    free = moves(board)
    if not free:
        return 0, None
    best_score, best_move = (-2 if turn == BOT else 2), None
    for m in free:
        board[m] = turn
        score, _ = minimax(board, HUMAN if turn == BOT else BOT)
        board[m] = ""
        if (turn == BOT and score > best_score) or (turn == HUMAN and score < best_score):
            best_score, best_move = score, m
    return best_score, best_move


def bot_move(board: list[str], rng: random.Random | None = None) -> int:
    rng = rng or random.Random()
    free = moves(board)
    if len(free) > 1 and rng.random() < BLUNDER_RATE:
        return rng.choice(free)
    return minimax(list(board), BOT)[1]  # type: ignore[return-value]


def finish(state: dict, result: str, user: str, date: str) -> None:
    """result: human | bot | draw"""
    state["status"] = {"human": "won", "bot": "lost", "draw": "draw"}[result]
    state["totals"][result] += 1
    state["history"] = ([{"winner": user if result == "human" else ("bot" if result == "bot" else "draw"), "date": date}]
                        + state["history"])[:HISTORY]


def play(state: dict, cell: int, user: str, date: str, rng: random.Random | None = None) -> tuple[bool, str]:
    """Apply a human move + the bot reply. Returns (changed, message)."""
    if state["status"] != "playing":
        return False, "This game is over - use the **New game** link in the README to start another."
    if state["board"][cell]:
        return False, f"Cell {cell} is already taken. Pick an empty one."
    state["player"] = state.get("player") or user
    state["board"][cell] = HUMAN
    if winner(state["board"]) == HUMAN:
        finish(state, "human", user, date)
        return True, f"You beat the bot, @{user}! You are now on the leaderboard."
    if not moves(state["board"]):
        finish(state, "draw", user, date)
        return True, "It's a draw."
    reply = bot_move(state["board"], rng)
    state["board"][reply] = BOT
    if winner(state["board"]) == BOT:
        finish(state, "bot", user, date)
        return True, f"The bot played cell {reply} and won. Better luck next time!"
    if not moves(state["board"]):
        finish(state, "draw", user, date)
        return True, f"The bot played cell {reply}. It's a draw."
    return True, f"You played {cell}, the bot answered {reply}. Your move!"


# ----------------------------------------------------------------------- render
def board_block(state: dict) -> str:
    rel = "assets/game"
    banner = {"playing": "board-your-turn", "won": "board-you-won", "lost": "board-bot-won", "draw": "board-draw"}[state["status"]]
    alt = {"playing": "Your turn", "won": "You won", "lost": "Bot won", "draw": "Draw"}[state["status"]]
    rows = []
    for r in range(3):
        cells = []
        for c in range(3):
            i = r * 3 + c
            v = state["board"][i]
            if v:
                cells.append(f'<img src="{rel}/cell_{v.lower()}.svg" width="96" height="96" alt="{v}">')
            elif state["status"] == "playing":
                href = issue_link(f"ttt|move|{i}", "Just press **Submit new issue**. The bot replies in about a minute. Don't change the title.")
                cells.append(f'<a href="{href}"><img src="{rel}/cell_empty.svg" width="96" height="96" alt="Play cell {i}"></a>')
            else:
                cells.append(f'<img src="{rel}/cell_empty.svg" width="96" height="96" alt="empty">')
        rows.append("".join(cells))
    new = ""
    if state["status"] != "playing":
        new = f'\n<p><a href="{issue_link("ttt|new|0", "Press Submit new issue to start a fresh game.")}"><b>&#9654; New game</b></a></p>'
    t = state["totals"]
    hist = state["history"]
    if hist:
        board_hist = "\n".join(
            f"| {('&#129302; bot' if h['winner'] == 'bot' else ('&#129309; draw' if h['winner'] == 'draw' else '&#127942; [@' + h['winner'] + '](https://github.com/' + h['winner'] + ')'))} | {h['date']} |"
            for h in hist)
        table = f"\n<details><summary>&#127942; Last {HISTORY} results</summary>\n\n| Winner | Date |\n|---|---|\n{board_hist}\n\n</details>"
    else:
        table = "\n<sub>No finished games yet - be the first on the leaderboard.</sub>"
    return (f'<div align="center">\n<img src="{rel}/{banner}.svg" alt="{alt}" height="36"><br>\n'
            + "<br>\n".join(rows) + f"\n{new}\n<sub>humans {t['human']} &#183; bot {t['bot']} &#183; draws {t['draw']} &#183; "
            f"you are X, click a square &#183; the board updates ~60 s after you submit</sub>\n</div>{table}")


# ----------------------------------------------------------------------- assets
def _tile(inner: str, w=96, h=96, bg=DARK["panel"]) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect x="3" y="3" width="{w - 6}" height="{h - 6}" rx="10" fill="{bg}" stroke="{DARK["line"]}" stroke-width="2"/>{inner}</svg>')


def write_assets() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    a, s = DARK["accent"], DARK["second"]
    draw_css = "<style>@keyframes d{from{stroke-dashoffset:80}to{stroke-dashoffset:0}}.p{stroke-dasharray:80;animation:d .45s ease-out both}@media (prefers-reduced-motion: reduce){.p{animation:none}}</style>"
    (ASSETS / "cell_x.svg").write_text(_tile(
        f'{draw_css}<path class="p" d="M28 28L68 68M68 28L28 68" stroke="{a}" stroke-width="9" stroke-linecap="round" fill="none"/>'), encoding="utf-8")
    (ASSETS / "cell_o.svg").write_text(_tile(
        f'{draw_css}<circle class="p" cx="48" cy="48" r="22" stroke="{s}" stroke-width="9" fill="none" transform="rotate(-90 48 48)"/>'), encoding="utf-8")
    (ASSETS / "cell_empty.svg").write_text(_tile(
        f'<style>@keyframes b{{50%{{opacity:.25}}}}.h{{animation:b 2.4s ease-in-out infinite}}@media (prefers-reduced-motion: reduce){{.h{{animation:none}}}}</style>'
        f'<circle class="h" cx="48" cy="48" r="4" fill="{DARK["muted"]}"/>'), encoding="utf-8")
    banners = {"board-your-turn": ("&gt; your turn, you are X", a), "board-you-won": ("&#10003; you won", DARK["green"]),
               "board-bot-won": ("&#10007; the bot won", s), "board-draw": ("= draw", DARK["muted"])}
    for name, (label, col) in banners.items():
        w = 300
        (ASSETS / f"{name}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="36" viewBox="0 0 {w} 36"><rect width="{w}" height="36" rx="8" fill="{DARK["bg"]}" stroke="{DARK["line"]}"/>'
            f'<text x="{w / 2}" y="23" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{col}">{label}</text></svg>', encoding="utf-8")


# ------------------------------------------------------------------------- main
def render(state: dict) -> None:
    update_readme("game", board_block(state))


def main(argv: list[str]) -> int:
    if "--assets" in argv:
        write_assets()
        return 0
    state = load_json(STATE, None) or fresh_state()
    if "--render" in argv:
        render(state)
        return 0
    ev = Event()
    now = now_utc()
    m = TITLE_RE.fullmatch(ev.title)
    if not m or not ev.valid_user:
        respond(ev.number, "Sorry, I could not understand that request (or it came from a bot). Use the squares in the README.")
        return 0
    if rate_limited(state["rate"], ev.user, now):
        respond(ev.number, "Easy there - one action per minute per player. Try again shortly.")
        save_json(STATE, state)
        return 0
    kind, cell = m.group(1), int(m.group(2))
    date = now.strftime("%Y-%m-%d")
    if kind == "new":
        if state["status"] == "playing" and any(state["board"]):
            msg = "A game is still in progress - finish it first."
        else:
            state = fresh_state(state)
            msg = "New game started - you are X. Pick a square in the README."
    else:
        _, msg = play(state, cell, ev.user, date)
    save_json(STATE, state)
    write_assets()
    render(state)
    respond(ev.number, msg + "\n\nThe README refreshes within about a minute.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
