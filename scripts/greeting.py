"""Rewrite the IST time-of-day greeting line in the README."""
from __future__ import annotations
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import IST, update_readme  # noqa: E402


def greeting(now: dt.datetime) -> str:
    h = now.astimezone(IST).hour
    if 5 <= h < 12:
        return "&#127749; Morning in Kolkata &mdash; Rajdip is probably heading to lectures at HITK"
    if 12 <= h < 17:
        return "&#9728;&#65039; Afternoon in Kolkata &mdash; Rajdip is probably between lectures and side projects"
    if 17 <= h < 22:
        return "&#127750; Evening in Kolkata &mdash; Rajdip is probably shipping something small"
    return "&#127769; Night in Kolkata &mdash; Rajdip is probably debugging"


def main() -> None:
    update_readme("greeting", f"<sub>{greeting(dt.datetime.now(dt.timezone.utc))}</sub>")


if __name__ == "__main__":
    main()
