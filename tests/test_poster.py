import datetime as dt
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import cards  # noqa: E402
import greeting  # noqa: E402
from poster import art, hero, work  # noqa: E402

SVG_BUDGET_KB = 500
TOTAL_BUDGET_MB = 3


def _ok(svg: str):
    ET.fromstring(svg)                                   # well-formed XML
    assert "prefers-reduced-motion" in svg               # every animated SVG respects reduced motion
    assert "<script" not in svg and "javascript:" not in svg.lower()
    assert "@import" not in svg and "http://fonts" not in svg and "https://fonts" not in svg   # no external fonts in <img> SVGs


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_generated_svgs_are_valid(mode):
    _ok(art.header(mode))
    _ok(art.footer(mode))
    _ok(hero.hero_hello(mode))
    _ok(hero.hero_roles(mode))
    _ok(hero.hero_chips(mode))
    _ok(hero.hero_welcome(mode))
    _ok(hero.ticker(mode))
    _ok(hero.about(mode))
    _ok(hero.section_title("01", "ABOUT ME", mode))
    _ok(hero.contact_pill("Email", "x@y.z", "gmail", mode))
    _ok(hero.button("Follow me", "follow", mode, True))
    _ok(hero.star_cta(mode))
    _ok(work.toolbox(mode))
    for i, p in enumerate(work.PROJECTS):
        _ok(work.project_card(p, mode, i))
    _ok(cards.dashboard_svg(mode, {"commits": 1, "prs": 2, "stars": 3, "followers": 4}, [("C", 10), ("Python", 5)], {"total": 9, "current": 2, "longest": 3}))
    _ok(greeting_svg(mode, True))
    _ok(greeting_svg(mode, False))


def greeting_svg(mode, night):
    return hero.greeting_svg(mode, "Night in Kolkata", "Last auto-updated: now", night)


def test_text_is_outlined_not_font_dependent():
    svg = art.header("dark")
    assert "<text" not in svg                             # stylish fonts are converted to paths


def test_committed_assets_fit_the_budget():
    files = [p for p in (ROOT / "assets").rglob("*") if p.is_file() and "source" not in p.parts]
    assert files, "run: python scripts/poster/build.py"
    for p in (f for f in files if f.suffix == ".svg"):
        assert p.stat().st_size / 1024 < SVG_BUDGET_KB, f"{p} is over {SVG_BUDGET_KB} KB"
    for other in ("light", "dark"):                      # a visitor loads one theme, never both
        loaded = sum(p.stat().st_size for p in files if f"-{other}." not in p.name and f"-{other}-" not in p.name)
        assert loaded / 1e6 < TOTAL_BUDGET_MB, f"theme payload is {loaded / 1e6:.1f} MB"
    assert (ROOT / "assets" / "ascii" / "portrait.gif").stat().st_size < 2e6   # GitHub camo limit is 5 MB; keep it < 2 MB


def test_readme_references_existing_files():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for ref in re.findall(r'(?:src|srcset|href)="(?!https?:|mailto:|#)([^"]+)"', text):
        assert (ROOT / ref).exists(), f"README references missing file {ref}"
    assert text.count("<picture>") >= 20


def test_readme_has_no_code_poster_leftovers():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "```" not in text and "ls projects" not in text and "./play" not in text


def test_streak_math():
    day = dt.date(2026, 10, 16)
    days = {(day - dt.timedelta(days=i)).isoformat(): c for i, c in enumerate([0, 2, 1, 1, 0, 3, 4, 1])}
    s = cards.compute_streaks(days, day)               # today empty -> streak counts back from yesterday
    assert s["current"] == 3 and s["longest"] == 3 and s["total"] == 12
    days[day.isoformat()] = 1
    assert cards.compute_streaks(days, day)["current"] == 4


@pytest.mark.parametrize("utc_hour,word", [(0, "morning"), (6, "morning"), (12, "evening"), (18, "Night"), (23, "Night")])
def test_greeting_uses_ist(utc_hour, word):
    # 00:00 UTC = 05:30 IST ; 06:00 UTC = 11:30 IST ; 12:00 UTC = 17:30 IST ; 18:00 UTC = 23:30 IST
    text, night = greeting.greeting(dt.datetime(2026, 1, 1, utc_hour, tzinfo=dt.timezone.utc))
    assert word in text and night == (word == "Night")


def test_stamp_is_ist():
    assert greeting.stamp(dt.datetime(2026, 1, 1, 0, 0, tzinfo=dt.timezone.utc)) == "Last auto-updated: 2026-01-01 05:30 IST"
