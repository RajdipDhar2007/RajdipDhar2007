"""Cache-bust the auto-updated images in README.md.

GitHub's image proxy (camo) caches README images, so a regenerated SVG at the same URL can look
stale for hours. The live workflows call this after rewriting their assets: it bumps ?v=<timestamp>
on that group's image URLs, which makes the README bytes change and the proxy fetch a fresh copy.

    python scripts/bust.py live|stats|3d
"""
from __future__ import annotations
import re
import sys
import time
from pathlib import Path

README = Path(__file__).resolve().parents[1] / "README.md"
GROUPS = ("live", "stats", "3d")
_REF = re.compile(r"(assets/(?:live|stats|3d)/[\w.-]+?\.svg)(\?v=\d+)?")


def bump(text: str, group: str, version: int) -> str:
    return _REF.sub(lambda m: f"{m.group(1)}?v={version}" if m.group(1).startswith(f"assets/{group}/") else m.group(0), text)


def carry(old: str, new: str) -> str:
    """Keep the versions the workflows already stamped when the README is regenerated."""
    seen = {m.group(1): m.group(2) for m in _REF.finditer(old) if m.group(2)}
    return _REF.sub(lambda m: m.group(1) + seen.get(m.group(1), ""), new)


def main() -> None:
    group = sys.argv[1]
    if group not in GROUPS:
        sys.exit(f"group must be one of {GROUPS}")
    text = README.read_text(encoding="utf-8")
    README.write_text(bump(text, group, int(time.time())), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
