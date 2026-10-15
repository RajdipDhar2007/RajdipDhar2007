import datetime as dt
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cards  # noqa: E402
import greeting  # noqa: E402
import guestbook as gb  # noqa: E402
import poll  # noqa: E402
import stamp  # noqa: E402
from common import Event  # noqa: E402


@pytest.mark.parametrize("raw,expected", [
    ("Hello <b>world</b>", "Hello world"),
    ("<script>alert(1)</script>hi", "alert(1) hi"),
    ("<img src=x onerror=alert(1)", ""),                        # unterminated tag removed entirely
    ("visit https://evil.example/x now", "visit now"),
    ("see www.evil.com please", "see please"),
    ("my site is evil.com/path ok", "my site is ok"),
    ("mail me a@b.co", "mail me"),
    ("ping @octocat and #1", "ping octocat and 1"),
    ("[click](javascript:alert(1))", "click"),
    ("**bold** `code` _em_ ~~x~~", "bold code em x"),
    ("line1\nline2", "line1 line2"),
    ("namaste नमस्ते", "namaste नमस्ते"),
    ("Great work.Thanks!", "Great work.Thanks!"),
])
def test_sanitize(raw, expected):
    assert gb.sanitize(raw, 140) == expected


def test_sanitize_limits_length():
    assert len(gb.sanitize("a" * 500, gb.MAX_MESSAGE)) == 140


def test_parse_issue_form_body():
    body = "### Name\n\nAda\n\n### Message\n\nLove it!\n\n### Name\n\nignored"
    assert gb.parse_form(body)["message"] == "Love it!"
    assert gb.parse_form("no headings")["name"] == ""


def test_add_entry_and_block():
    state = {"entries": [], "rate": {}}
    for i in range(7):
        ok, _ = gb.add_entry(state, f"User{i}", f"msg {i}", "u", "2026-01-01")
        assert ok
    html = gb.block(state)
    assert html.count("&mdash;") == gb.SHOWN
    assert "User6" in html and "User1" not in html          # newest first, only 5 shown


def test_empty_after_cleaning_is_rejected():
    state = {"entries": [], "rate": {}}
    ok, _ = gb.add_entry(state, "<b></b>", "https://spam.com", "u", "d")
    assert not ok and state["entries"] == []


def test_event_rejects_bots_and_odd_logins():
    assert Event({"ISSUE_USER": "alice", "ISSUE_USER_TYPE": "User"}).valid_user
    assert not Event({"ISSUE_USER": "dependabot[bot]", "ISSUE_USER_TYPE": "Bot"}).valid_user
    assert not Event({"ISSUE_USER": "a;rm -rf", "ISSUE_USER_TYPE": "User"}).valid_user


def test_poll_one_vote_per_user_and_chart_is_valid_xml():
    state = {**poll.DEFAULT, "votes": {}, "rate": {}}
    assert poll.cast(state, "Alice", 1)[0]
    assert not poll.cast(state, "alice", 2)[0]
    assert not poll.cast(state, "bob", 7)[0]
    assert poll.cast(state, "bob", 1)[0]
    assert poll.tally(state) == [0, 2, 0]
    for mode in ("dark", "light"):
        ET.fromstring(poll.chart_svg(state, mode))


def test_streak_math():
    day = dt.date(2026, 10, 16)
    days = {(day - dt.timedelta(days=i)).isoformat(): c for i, c in enumerate([0, 2, 1, 1, 0, 3, 4, 1])}
    s = cards.compute_streaks(days, day)               # today empty -> streak counts back from yesterday
    assert s["current"] == 3 and s["longest"] == 3 and s["total"] == 12
    days[day.isoformat()] = 1
    assert cards.compute_streaks(days, day)["current"] == 4


def test_cards_are_valid_xml():
    s = {"total": 5, "current": 2, "longest": 3, "longest_end": None}
    ET.fromstring(cards.streak_svg("dark", s))
    ET.fromstring(cards.stats_svg("light", {"commits": 1, "prs": 2, "stars": 3, "followers": 4}))
    ET.fromstring(cards.langs_svg("dark", [("C", 10), ("Python", 5)]))


@pytest.mark.parametrize("utc_hour", [0, 6, 12, 18, 23])
def test_greeting_uses_ist(utc_hour):
    # 00:00 UTC = 05:30 IST (morning) ; 06:00 UTC = 11:30 IST (still morning) ; 12:00 UTC = 17:30 IST (evening)
    now = dt.datetime(2026, 1, 1, utc_hour, 0, tzinfo=dt.timezone.utc)
    expected = {0: "Morning", 6: "Morning", 12: "Evening", 18: "Night", 23: "Night"}[utc_hour]
    assert expected in greeting.greeting(now)


def test_stamp_is_ist():
    assert stamp.stamp(dt.datetime(2026, 1, 1, 0, 0, tzinfo=dt.timezone.utc)) == "Last auto-updated: 2026-01-01 05:30 IST"
