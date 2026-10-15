"""Seed placeholder SVGs for assets that only GitHub Actions can generate.

The README references profile-3d-contrib/*.svg; until the "3D contribution city" workflow has run once,
a calm placeholder is shown instead of a broken image. The workflow overwrites these files.
No contribution data is faked: the skyline is purely decorative.
"""
from __future__ import annotations
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from theme import MONO, PROMPT, THEMES  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "profile-3d-contrib"
NAMES = {"dark": "profile-neon-night.svg", "light": "profile-neon-day.svg"}


def city(mode: str) -> str:
    c = THEMES[mode]
    rnd = random.Random(7)
    W, H = 900, 260
    bars = []
    for i in range(36):
        h = rnd.randint(20, 120)
        x = 40 + i * 23
        bars.append(f'<rect class="b" x="{x}" y="{200 - h}" width="17" height="{h}" rx="2" fill="{c["line"]}" style="animation-delay:{i * .05:.2f}s"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="3D contribution city (pending first render)">'
            f'<style>text{{font-family:{MONO}}}@keyframes u{{from{{transform:scaleY(.2)}}}}.b{{transform-box:fill-box;transform-origin:bottom;animation:u 1s ease-out both}}'
            f'@media (prefers-reduced-motion: reduce){{.b{{animation:none}}}}</style>'
            f'<rect width="{W}" height="{H}" rx="12" fill="{c["bg"]}"/>{"".join(bars)}'
            f'<text x="{W / 2}" y="236" text-anchor="middle" font-size="13" fill="{c["muted"]}">{PROMPT} ./contrib --city   (rendered by Actions, runs daily)</text></svg>')


def main():
    OUT.mkdir(exist_ok=True)
    for mode, name in NAMES.items():
        p = OUT / name
        if p.exists() and "pending first render" not in p.read_text(encoding="utf-8")[:400]:
            continue  # a real render exists: never overwrite it
        p.write_text(city(mode), encoding="utf-8")
        print("placeholder ->", p)


if __name__ == "__main__":
    main()
