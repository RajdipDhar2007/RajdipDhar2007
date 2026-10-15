import datetime as dt
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import game  # noqa: E402
from common import rate_limited, replace_block  # noqa: E402


def test_winner_detection():
    assert game.winner(["X", "X", "X", "", "", "", "", "", ""]) == "X"
    assert game.winner(["O", "", "", "", "O", "", "", "", "O"]) == "O"
    assert game.winner([""] * 9) is None


def test_bot_takes_winning_move_and_blocks():
    board = ["O", "O", "", "X", "X", "", "", "", ""]
    assert game.minimax(board, game.BOT)[1] == 2        # wins instead of blocking
    board = ["X", "X", "", "", "O", "", "", "", ""]
    assert game.minimax(board, game.BOT)[1] == 2        # must block


def test_perfect_bot_never_loses(monkeypatch):
    monkeypatch.setattr(game, "BLUNDER_RATE", 0.0)
    for seed in range(150):
        rng = random.Random(seed)
        state = game.fresh_state()
        while state["status"] == "playing":
            cell = rng.choice(game.moves(state["board"]))
            game.play(state, cell, "tester", "2026-01-01", rng)
        assert state["status"] in ("lost", "draw")


def test_blunder_rate_allows_human_to_win():
    class Always(random.Random):
        def random(self):
            return 0.0                                   # always blunder
        def choice(self, seq):
            return seq[0]
    state = game.fresh_state()
    for cell in (4, 5, 3):                               # bot answers 0,1,... -> human completes row 3-4-5
        ok, _ = game.play(state, cell, "alice", "2026-01-01", Always())
        assert ok
    assert state["status"] == "won"
    assert state["history"][0] == {"winner": "alice", "date": "2026-01-01"}
    assert state["totals"]["human"] == 1


def test_rejects_taken_cell_and_finished_game():
    state = game.fresh_state()
    state["board"][0] = "X"
    ok, msg = game.play(state, 0, "bob", "d")
    assert not ok and "taken" in msg
    state["status"] = "draw"
    ok, msg = game.play(state, 5, "bob", "d")
    assert not ok and "over" in msg


def test_history_keeps_last_five():
    state = game.fresh_state()
    for i in range(8):
        game.finish(state, "human", f"u{i}", "2026-01-01")
    assert len(state["history"]) == game.HISTORY
    assert state["history"][0]["winner"] == "u7"


@pytest.mark.parametrize("title,ok", [
    ("ttt|move|0", True), ("ttt|move|8", True), ("ttt|new|0", True),
    ("ttt|move|9", False), ("ttt|move|-1", False), ("ttt|move|1 ", False),
    ("ttt|move|1\nrm -rf /", False), ("ttt|move|1;ls", False), ("TTT|move|1", False), ("ttt|win|1", False),
])
def test_title_is_parsed_strictly(title, ok):
    assert bool(game.TITLE_RE.fullmatch(title)) is ok


def test_board_block_links_only_empty_cells():
    state = game.fresh_state()
    state["board"][4] = "X"
    html = game.board_block(state)
    assert html.count("<img src=\"assets/game/cell_") == 9
    assert html.count("<a href=") == 8
    assert "ttt%7Cmove%7C4" not in html and "ttt%7Cmove%7C0" in html
    assert "New game" not in html
    state["status"] = "won"
    html = game.board_block(state)
    assert "New game" in html and "ttt%7Cnew%7C0" in html and html.count("ttt%7Cmove") == 0


def test_rate_limit_one_action_per_minute():
    rate = {}
    t0 = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
    assert not rate_limited(rate, "Alice", t0)
    assert rate_limited(rate, "alice", t0 + dt.timedelta(seconds=30))
    assert not rate_limited(rate, "alice", t0 + dt.timedelta(seconds=61))
    assert not rate_limited(rate, "bob", t0)


def test_replace_block_roundtrip():
    text = "a\n<!--START_SECTION:x-->\nold\n<!--END_SECTION:x-->\nb"
    out = replace_block(text, "x", "new $1 \\g<0>")
    assert out == "a\n<!--START_SECTION:x-->\nnew $1 \\g<0>\n<!--END_SECTION:x-->\nb"
    with pytest.raises(ValueError):
        replace_block(text, "missing", "z")
