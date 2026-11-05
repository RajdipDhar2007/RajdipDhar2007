"""Regenerate every static poster asset and the README (no network needed).

    python scripts/poster/build.py

Live pieces are separate: scripts/cards.py (GitHub API), scripts/greeting.py (clock),
scripts/ascii/build_svg.py (portrait), and the 3D chart (see .github/workflows/3d-chart.yml).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from poster import art, hero, work, readme  # noqa: E402


def main() -> None:
    art.build()
    hero.build()
    work.build()
    readme.main()


if __name__ == "__main__":
    main()
