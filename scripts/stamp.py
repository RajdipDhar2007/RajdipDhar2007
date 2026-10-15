"""Write 'Last auto-updated: <IST timestamp>' into the README footer."""
from __future__ import annotations
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import IST, update_readme  # noqa: E402


def stamp(now: dt.datetime) -> str:
    return "Last auto-updated: " + now.astimezone(IST).strftime("%Y-%m-%d %H:%M IST")


def main() -> None:
    update_readme("stamp", f"<sub>{stamp(dt.datetime.now(dt.timezone.utc))}</sub>")


if __name__ == "__main__":
    main()
