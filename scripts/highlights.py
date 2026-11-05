"""Highlights tiles (live milestones from the contribution calendar).

    python scripts/highlights.py     # needs GITHUB_TOKEN / GH_TOKEN (or `gh auth login` locally)
"""
from __future__ import annotations
import datetime as dt
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cards import gql, OWNER, fetch_days, compute_streaks  # noqa: E402
from poster.honors import build_highlights  # noqa: E402


def summarize(days: dict[str, int], today: dt.date) -> dict:
    """Pure function: calendar -> numbers shown on the tiles."""
    st = compute_streaks(days, today)
    active = [v for v in days.values() if v > 0]
    best = max(days, key=lambda k: days[k]) if days else None
    last30 = [days.get((today - dt.timedelta(days=29 - k)).isoformat(), 0) for k in range(30)]
    return {"total": st["total"], "longest": st["longest"], "current": st["current"], "active_days": len(active),
            "busiest": days[best] if best else 0,
            "busiest_date": dt.date.fromisoformat(best).strftime("%d %b %Y") if best else "n/a",
            "per_active": (sum(active) / len(active)) if active else 0.0, "last30": last30}


def main() -> None:
    login = os.environ.get("GITHUB_REPOSITORY_OWNER", OWNER)
    d = summarize(fetch_days(login), dt.datetime.now(dt.timezone.utc).date())
    print({k: v for k, v in d.items() if k != "last30"})
    build_highlights(d)


if __name__ == "__main__":
    main()
