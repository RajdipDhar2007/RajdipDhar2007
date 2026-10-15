"""Shared plumbing for the event-driven profile features (game, poll, guestbook, greeting, stamp)."""
from __future__ import annotations
import datetime as dt
import json
import os
import re
import subprocess
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
DATA = ROOT / "data"

OWNER = os.environ.get("GITHUB_REPOSITORY", "RajdipDhar2007/RajdipDhar2007").split("/")[0]
REPO = os.environ.get("GITHUB_REPOSITORY", "RajdipDhar2007/RajdipDhar2007").split("/")[-1]
IST = dt.timezone(dt.timedelta(hours=5, minutes=30), "IST")  # India has no DST
RATE_LIMIT_SECONDS = 60


# --------------------------------------------------------------------------- io
def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def replace_block(text: str, name: str, content: str) -> str:
    """Replace what sits between <!--START_SECTION:name--> and <!--END_SECTION:name-->."""
    start, end = f"<!--START_SECTION:{name}-->", f"<!--END_SECTION:{name}-->"
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pat.search(text):
        raise ValueError(f"markers for section '{name}' not found")
    return pat.sub(lambda _m: f"{start}\n{content.strip()}\n{end}", text, count=1)


def update_readme(name: str, content: str, path: Path = README) -> None:
    path.write_text(replace_block(path.read_text(encoding="utf-8"), name, content), encoding="utf-8")


def issue_link(title: str, body: str = "", repo: str = f"{OWNER}/{REPO}") -> str:
    q = {"title": title}
    if body:
        q["body"] = body
    return f"https://github.com/{repo}/issues/new?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote)


# ------------------------------------------------------------------ rate limit
def rate_limited(rate: dict, user: str, now: dt.datetime, seconds: int = RATE_LIMIT_SECONDS) -> bool:
    """True if `user` already acted less than `seconds` ago. Records the action otherwise."""
    key = user.lower()
    last = rate.get(key)
    if last is not None and (now - dt.datetime.fromisoformat(last)).total_seconds() < seconds:
        return True
    rate[key] = now.isoformat()
    for k in [k for k, v in rate.items() if (now - dt.datetime.fromisoformat(v)).total_seconds() > 3600]:
        del rate[k]  # keep the file small
    return False


# ------------------------------------------------------------------- github io
class Event:
    """The issue that triggered the workflow. Read from env only - never interpolated into a shell."""

    def __init__(self, env=os.environ):
        self.number = int(env.get("ISSUE_NUMBER", "0") or 0)
        self.title = (env.get("ISSUE_TITLE") or "").strip()
        self.body = env.get("ISSUE_BODY") or ""
        self.user = (env.get("ISSUE_USER") or "").strip()
        self.user_type = env.get("ISSUE_USER_TYPE") or "User"

    @property
    def valid_user(self) -> bool:
        return bool(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", self.user)) and self.user_type != "Bot" and not self.user.endswith("[bot]")


def gh(*args: str, stdin: str | None = None) -> None:
    """Run the GitHub CLI with an argument vector (no shell). Silent no-op when DRY_RUN is set."""
    if os.environ.get("DRY_RUN"):
        print("DRY_RUN gh", *args, "<<<", stdin)
        return
    subprocess.run(["gh", *args], input=stdin, text=True, check=False)


def respond(number: int, message: str, close: bool = True, lock: bool = True) -> None:
    if not number:
        return
    gh("issue", "comment", str(number), "--body-file", "-", stdin=message)
    if close:
        gh("issue", "close", str(number), "--reason", "completed")
    if lock:
        gh("issue", "lock", str(number), "--reason", "resolved")


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)
