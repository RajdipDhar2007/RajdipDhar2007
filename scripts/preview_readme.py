"""Dev aid: render README.md the way GitHub roughly would (GitHub markdown API + a GitHub-like page) and screenshot it."""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from snap import launch
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
mode = sys.argv[1] if len(sys.argv) > 1 else "dark"
width = int(sys.argv[2]) if len(sys.argv) > 2 else 1012
html = subprocess.run(["gh", "api", "markdown", "-f", f"text={(ROOT / 'README.md').read_text(encoding='utf-8')}", "-f", "mode=gfm"],
                      capture_output=True, text=True, check=True).stdout
bg, fg = ("#0D1117", "#E6EDF3") if mode == "dark" else ("#FFFFFF", "#1F2328")
page = (f"<base href='file:///{ROOT.as_posix()}/'><style>body{{margin:0;background:{bg};color:{fg};font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.5}}"
        f"article{{max-width:888px;margin:0 auto;padding:32px 32px}}img{{max-width:100%}}details{{margin:16px 0}}table{{border-collapse:collapse;width:100%}}td{{padding:6px 13px}}a{{color:#4493f8}}</style><article>{html}</article>")
out = ROOT / "scripts" / "ascii" / "_work" / "readme.html"
out.write_text(page, encoding="utf-8")
with sync_playwright() as p:
    b = launch(p)
    ctx = b.new_context(color_scheme=mode, viewport={"width": width, "height": 900})
    pg = ctx.new_page()
    pg.goto(out.as_uri())
    pg.wait_for_timeout(1500)
    pg.screenshot(path=str(ROOT / "preview" / f"readme-{mode}-{width}.png"), full_page=True)
    print(pg.evaluate("document.body.scrollHeight"))
