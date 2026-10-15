"""Write the live IST time-of-day greeting SVGs (assets/live/greeting-{dark,light}.svg)."""
from __future__ import annotations
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from poster.common import MODES, OUT, write  # noqa: E402
from poster.hero import greeting_svg  # noqa: E402

IST = dt.timezone(dt.timedelta(hours=5, minutes=30), "IST")  # India has no DST


def greeting(now: dt.datetime) -> tuple[str, bool]:
    """(text, is_night) for the given moment, in Indian Standard Time."""
    h = now.astimezone(IST).hour
    if 5 <= h < 12:
        return "Good morning from Kolkata. Rajdip is probably heading to lectures at HITK", False
    if 12 <= h < 17:
        return "Good afternoon from Kolkata. Rajdip is probably between lectures and side projects", False
    if 17 <= h < 22:
        return "Good evening from Kolkata. Rajdip is probably shipping something small", False
    return "Night in Kolkata. Rajdip is probably debugging", True


def stamp(now: dt.datetime) -> str:
    return "Last auto-updated: " + now.astimezone(IST).strftime("%Y-%m-%d %H:%M IST")


def main() -> None:
    now = dt.datetime.now(dt.timezone.utc)
    text, night = greeting(now)
    for m in MODES:
        write(OUT / "live" / f"greeting-{m}.svg", greeting_svg(m, text, stamp(now), night))


if __name__ == "__main__":
    main()
