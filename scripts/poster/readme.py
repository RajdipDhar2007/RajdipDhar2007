"""Generate README.md (keeps the content of the workflow-managed marker sections).

    python scripts/poster/readme.py
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
REPO = "RajdipDhar2007/RajdipDhar2007"


def pic(path: str, alt: str, width: str = "100%", extra: str = "", dark: bool = True) -> str:
    """<picture> with dark/light sources; `path` contains {m} for the mode."""
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{path.format(m="dark")}">'
            f'<source media="(prefers-color-scheme: light)" srcset="{path.format(m="light")}">'
            f'<img alt="{alt}" src="{path.format(m="light")}" width="{width}" {extra}></picture>')


def title(slug: str, alt: str) -> str:
    return (f'<p align="center">{pic("assets/sections/divider-{m}.svg", "")}</p>\n'
            f'<p align="center">{pic("assets/titles/" + slug + "-{m}.svg", alt)}</p>\n')


def card(key: str, name: str, extra: str) -> str:
    return (f'<td width="50%" align="center" valign="top">\n'
            f'<a href="https://github.com/{REPO.split("/")[0]}/{name}">{pic("assets/projects/" + key + "-{m}.svg", name + " project card", "100%")}</a>\n'
            f'{extra}\n</td>')


def main() -> None:
    owner = REPO.split("/")[0]
    out = f'''<div align="center">
{pic("assets/banners/header-{m}.svg", "Rajdip Dhar: hand-drawn signature, animated aurora banner")}
</div>

<a href="scripts/ascii/">{pic("assets/ascii/portrait-{m}.svg", "Animated ASCII portrait of Rajdip Dhar", "420", 'align="left" hspace="10"').replace('src="assets/ascii/portrait-light.svg"', 'src="assets/ascii/portrait.gif"')}</a>

{pic("assets/hero/hello-{m}.svg", "Hi, I'm Rajdip", "360")}<br>
{pic("assets/hero/roles-{m}.svg", "I build full-stack web apps, Android apps, games from scratch, Web3 experiments, AI and automation", "360")}<br>
{pic("assets/hero/chips-{m}.svg", "B.Tech CSE at HITK, Kolkata IST, batch 2026 to 2030, open to internships", "360")}

{pic("assets/hero/welcome-{m}.svg", "Welcome to my space", "360")}<br>
<a href="mailto:rajdipdharofficial@gmail.com">{pic("assets/hero/btn-email-{m}.svg", "Email me", "172")}</a><a href="https://github.com/{owner}?tab=repositories">{pic("assets/hero/btn-work-{m}.svg", "See my work", "172")}</a>

<br clear="left">

<p align="center">{pic("assets/sections/ticker-{m}.svg", "Full-stack, Android, game dev, Web3, AI / LLM, automation")}</p>

{title("about", "About me")}
<p align="center">{pic("assets/sections/about-{m}.svg", "B.Tech CSE at HITK, full-stack, Android, game dev and Web3, exploring AI and automation, looking for internships")}</p>
<!-- TODO_RAJDIP: clubs, hackathons and achievements can become a new card or a short list here. -->

{title("toolbox", "Toolbox")}
<p align="center">{pic("assets/sections/toolbox-{m}.svg", "Toolbox: Python, TypeScript, JavaScript, Kotlin, C, HTML, React, Vite, Android Studio, OpenGL, Git, GitHub; learning Django, Solidity, Jupyter, ML, data science, LLM apps and automation")}</p>
<!-- TODO_RAJDIP: review the toolbox tiles (poster.work.ROWS); they only list what the public repos show. -->

<p align="center">{pic("assets/sections/ticker2-{m}.svg", "Build, ship, learn, repeat")}</p>

{title("work", "Featured work")}
<table>
<tr>
{card("ultimatecraft", "UltimateCraft", f'<sub><a href="https://github.com/{owner}/UltimateCraft/releases/latest">Download latest build</a></sub><!-- TODO_RAJDIP: write-up link, demo GIF -->')}
{card("loci", "Loci", "<!-- TODO_RAJDIP: live link, write-up, demo GIF -->")}
</tr>
<tr>
{card("attendtrack", "AttendTrack", "<!-- TODO_RAJDIP: live link, write-up, demo GIF -->")}
{card("meridian", "Meridian", "<!-- TODO_RAJDIP: live link, write-up, demo GIF -->")}
</tr>
</table>

<p align="center"><sub>More on my <a href="https://github.com/{owner}?tab=repositories">repositories</a> page: TaskFlow, MathForge, Rack Up (Web3 game on Base Sepolia), Periodic Table and more.</sub></p>

{title("stats", "By the numbers")}
<p align="center">{pic("assets/stats/dashboard-{m}.svg", "GitHub stats: commits, pull requests, stars, followers, top languages and contribution streak")}</p>

{title("city", "Contribution city")}
<p align="center">{pic("assets/3d/contribution-{m}.svg", "3D contribution chart for the last 36 weeks", "100%")}</p>

{title("activity", "Live activity")}
<p align="center">{pic("assets/live/greeting-{m}.svg", "Time-of-day greeting")}</p>

{title("connect", "Let's connect")}
<p align="center">
<a href="mailto:rajdipdharofficial@gmail.com">{pic("assets/contact/email-{m}.svg", "Email Rajdip", "250")}</a>
<a href="https://github.com/{owner}">{pic("assets/contact/github-{m}.svg", "Rajdip on GitHub", "250")}</a>
<!-- TODO_RAJDIP: add LinkedIn, portfolio, LeetCode / Codeforces and X pills (see contact_pill() in scripts/poster/hero.py) -->
</p>
<p align="center"><sub>Fastest reply: email &middot; open to internships and collaborations</sub></p>

<div align="center">
{pic("assets/banners/footer-{m}.svg", "Thanks for stopping by")}
</div>
'''
    README.write_text(out, encoding="utf-8")
    print("README.md written")


if __name__ == "__main__":
    main()
