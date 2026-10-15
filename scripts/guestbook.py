"""Guestbook driven by the issue form in .github/ISSUE_TEMPLATE/guestbook.yml.

Entries are sanitised (HTML stripped, links removed, allow-listed characters only, 140 chars),
stored in data/guestbook.json and the last 5 are written into the README between markers.

    python scripts/guestbook.py            # reads ISSUE_* env vars
    python scripts/guestbook.py --render
"""
from __future__ import annotations
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import DATA, OWNER, REPO, Event, load_json, now_utc, rate_limited, respond, save_json, update_readme  # noqa: E402

STATE = DATA / "guestbook.json"
MAX_MESSAGE, MAX_NAME, SHOWN, KEPT = 140, 30, 5, 200
TLDS = "com|net|org|io|dev|me|in|co|xyz|app|ly|gg|ai|info|biz|us|uk|ru|cn|tk|ml|ga|cf|gq|link|site|online|shop|top|club"

_TAGS = re.compile(r"<[^>]*>?")                                  # anything tag-like, even unterminated
_URLS = re.compile(r"(?:https?|ftp|mailto|javascript|data):\S*|www\.\S+|\S+@\S+\.\S+", re.I)
_DOMAINS = re.compile(rf"\b[\w-]+(?:\.[\w-]+)*\.(?:{TLDS})\b(?:/\S*)?", re.I)
_MD_LINK = re.compile(r"\]\((?:[^()]|\([^)]*\))*\)?")                          # the (target) part of [text](target)
_PUNCT = frozenset(" .,!?'-:;()&+/=")
_SPACES = re.compile(r"\s+")


def sanitize(text: str, limit: int) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = _TAGS.sub(" ", text)
    text = _MD_LINK.sub(" ", text)
    text = _URLS.sub(" ", text)
    text = _DOMAINS.sub(" ", text)
    # allow-list: letters/digits of any script (+ combining marks so Indic text survives) and tame punctuation;
    # everything else (markdown, @, #, brackets, backticks, pipes, underscores, emoji) is dropped
    text = "".join(
        ch if (ch.isalnum() or unicodedata.category(ch).startswith("M") or ch in _PUNCT) else (" " if ch == "\n" else "")
        for ch in text)
    text = _SPACES.sub(" ", text).strip()
    return text[:limit].strip()


def parse_form(body: str) -> dict[str, str]:
    """Issue forms render as '### Label\\n\\nvalue'. Only the two known labels are read."""
    parts = re.split(r"^###\s+(.+?)\s*$", body or "", flags=re.M)
    fields = {parts[i].strip().lower(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
    return {"name": fields.get("name", ""), "message": fields.get("message", "")}


def add_entry(state: dict, name: str, message: str, user: str, date: str) -> tuple[bool, str]:
    name, message = sanitize(name, MAX_NAME), sanitize(message, MAX_MESSAGE)
    if not name or not message:
        return False, "Your name or message was empty after cleaning (no HTML, links or special characters are allowed). Please try again."
    state["entries"] = ([{"name": name, "message": message, "date": date, "user": user}] + state["entries"])[:KEPT]
    return True, f"Thanks for signing the guestbook, {name}!"


def block(state: dict) -> str:
    link = f"https://github.com/{OWNER}/{REPO}/issues/new?template=guestbook.yml"
    items = "\n".join(f"> **{e['name']}** &mdash; {e['message']} <sub>{e['date']}</sub>  " for e in state["entries"][:SHOWN])
    body = items or "> *No entries yet - be the first!*"
    return f"{body}\n\n<sub><a href=\"{link}\">&#9998; Sign the guestbook</a> &#183; max {MAX_MESSAGE} characters, no links &#183; shows up ~60 s after you submit</sub>"


def main(argv: list[str]) -> int:
    state = load_json(STATE, None) or {"entries": [], "rate": {}}
    state.setdefault("rate", {})
    if "--render" in argv:
        update_readme("guestbook", block(state))
        return 0
    ev = Event()
    if not ev.valid_user:
        respond(ev.number, "Sorry, bots can't sign the guestbook.")
        return 0
    if rate_limited(state["rate"], ev.user, now_utc()):
        respond(ev.number, "Easy there - one entry per minute. Try again shortly.")
        save_json(STATE, state)
        return 0
    form = parse_form(ev.body)
    ok, msg = add_entry(state, form["name"], form["message"], ev.user, now_utc().strftime("%Y-%m-%d"))
    save_json(STATE, state)
    if ok:
        update_readme("guestbook", block(state))
    respond(ev.number, msg + ("\n\nIt will show up in the README within about a minute." if ok else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
