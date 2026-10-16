"""Generate README.md (keeps the content of the workflow-managed marker sections).

    python scripts/poster/readme.py
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
REPO = "RajdipDhar2007/RajdipDhar2007"


def pic(path: str, alt: str, width: str = "100%", extra: str = "", dark: bool = True) -> str:
    """<picture> with dark/light sources; `path` contains {m} for the mode."""
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{path.format(m="dark")}">'
            f'<source media="(prefers-color-scheme: light)" srcset="{path.format(m="light")}">'
            f'<img alt="{alt}" src="{path.format(m="light")}" width="{width}" {extra}></picture>')


_n = [0]


def title(slug: str, alt: str) -> str:
    _n[0] += 1
    div = "divider" if _n[0] % 2 else "divider2"
    return (f'<p align="center">{pic("assets/sections/" + div + "-{m}.svg", "")}</p>\n'
            f'<p align="center">{pic("assets/titles/" + slug + "-{m}.svg", alt)}</p>\n')


def card(key: str, name: str, band_url: str) -> str:
    """Project card (links to the repo) with an attached action band (download, or open the repo)."""
    owner = REPO.split("/")[0]
    top = pic("assets/projects/" + key + "-{m}.svg", name + " project card", "100%", 'align="top"')
    band = pic("assets/projects/" + key + "-band-{m}.svg", "Action button for " + name, "100%", 'align="top"')
    return (f'<td width="50%" align="center" valign="top">\n'
            f'<a href="https://github.com/{owner}/{name}">{top}</a><br>\n'
            f'<a href="{band_url}">{band}</a>\n</td>')


def more_pills(owner: str) -> str:
    """One linked pill per repository; the last one ("and more") opens the repositories page."""
    pills = [("TaskFlow", "TaskFlow"), ("MathForge", "MathForge"), ("Rack Up, a Web3 game on Base Sepolia", "Rack_Up-Onchain_Hi-Lo"),
             ("Periodic Table", "Periodic-Table"), ("and more repositories", None)]
    out = []
    for k, (alt, repo) in enumerate(pills):
        url = f"https://github.com/{owner}/{repo}" if repo else f"https://github.com/{owner}?tab=repositories"
        img = pic("assets/sections/more-" + str(k) + "-{m}.svg", alt, "", 'align="top"').replace(' width=""', "")
        out.append(f'<a href="{url}">{img}</a>')
    return "\n".join(out)


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
<a href="https://github.com/{owner}">{pic("assets/hero/btn-follow-{m}.svg", "Follow me on GitHub", "172")}</a><a href="https://github.com/{owner}?tab=repositories">{pic("assets/hero/btn-work-{m}.svg", "See my work", "172")}</a>

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
{card("ultimatecraft", "UltimateCraft", f"https://github.com/{owner}/UltimateCraft/releases/download/v5.1.0/UltimateCraft-5.1.0-windows.zip")}
{card("loci", "Loci", f"https://github.com/{owner}/Loci")}
</tr>
<tr>
{card("attendtrack", "AttendTrack", f"https://github.com/{owner}/AttendTrack/releases/latest/download/AttendTrack.apk")}
{card("meridian", "Meridian", f"https://github.com/{owner}/Meridian")}
</tr>
</table>

<p align="center"><a href="https://github.com/{owner}?tab=repositories">{pic("assets/sections/more-{m}.svg", "More from my repositories: open the repositories page")}</a></p>
<p align="center">
{more_pills(owner)}
</p>

{title("stats", "By the numbers")}
<p align="center">{pic("assets/stats/dashboard-{m}.svg", "GitHub stats: commits, pull requests, stars, followers, top languages and contribution streak")}</p>

{title("city", "Contribution city")}
<p align="center">{pic("assets/3d/contribution-{m}.svg", "3D contribution chart for the last 36 weeks", "100%")}</p>

{title("activity", "Live activity")}
<p align="center">{pic("assets/live/greeting-{m}.svg", "Time-of-day greeting")}</p>

{title("play", "Play a game")}
<p align="center"><a href="https://rajdipdhar2007.github.io/RajdipDhar2007/">{pic("assets/sections/arcade-{m}.svg", "Bug Hunter, a playable arcade shooter. Click to play.")}</a></p>

{title("connect", "Let's connect")}
<p align="center">
<a href="mailto:rajdipdharofficial@gmail.com">{pic("assets/contact/email-{m}.svg", "Email Rajdip", "250")}</a>
<a href="https://github.com/{owner}">{pic("assets/contact/github-{m}.svg", "Rajdip on GitHub", "250")}</a>
<!-- TODO_RAJDIP: add LinkedIn, portfolio, LeetCode / Codeforces and X pills (see contact_pill() in scripts/poster/hero.py) -->
</p>

<p align="center"><a href="https://github.com/{REPO}">{pic("assets/sections/star-{m}.svg", "Enjoyed the tour? Star this repo")}</a></p>

<div align="center">
{pic("assets/banners/footer-{m}.svg", "Thanks for stopping by")}
</div>
'''
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from bust import carry
    old = README.read_text(encoding="utf-8") if README.exists() else ""
    README.write_text(carry(old, out), encoding="utf-8")
    print("README.md written")


if __name__ == "__main__":
    main()
