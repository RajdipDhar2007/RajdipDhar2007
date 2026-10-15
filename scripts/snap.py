"""Deterministic SVG snapshots through headless Chrome/Chromium (Playwright).

    python scripts/snap.py assets/ascii/portrait-dark.svg 0.5 2 4 8 --out preview --scheme dark
"""
from __future__ import annotations
import argparse
from pathlib import Path


def launch(p):
    for kw in ({"channel": "chrome"}, {"channel": "msedge"}, {}):
        try:
            return p.chromium.launch(**kw)
        except Exception:  # noqa: BLE001
            continue
    raise RuntimeError("No Chromium/Chrome/Edge available for Playwright")


def snapshots(svg: Path, times, out_files, scheme="dark", scale=1.0, reduced_motion=False, size=None, bg=None):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = launch(p)
        ctx = browser.new_context(color_scheme=scheme, device_scale_factor=scale,
                                  reduced_motion="reduce" if reduced_motion else "no-preference")
        page = ctx.new_page()
        page.goto(svg.resolve().as_uri())
        if bg:
            page.evaluate("(c)=>{document.documentElement.style.background=c}", bg)
        dims = page.evaluate("(()=>{const s=document.documentElement;const b=s.getBoundingClientRect();"
                             "return [s.viewBox.baseVal.width||b.width, s.viewBox.baseVal.height||b.height]})()")
        w, h = size or (int(dims[0]), int(dims[1]))
        page.set_viewport_size({"width": w, "height": h})
        for t, out in zip(times, out_files):
            # pause first and wait for the pending pause to resolve, else it overwrites currentTime
            page.evaluate("""async (t)=>{const an=document.getAnimations();an.forEach(a=>a.pause());
                await Promise.all(an.map(a=>a.ready));an.forEach(a=>{a.currentTime=t*1000});
                await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));}""", t)
            page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": w, "height": h})
        browser.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("svg")
    ap.add_argument("times", nargs="+", type=float)
    ap.add_argument("--out", default="preview")
    ap.add_argument("--scheme", default="dark")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--reduced", action="store_true")
    ap.add_argument("--bg", default=None)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(a.svg).stem
    files = [out / f"{stem}-{t:g}s.png" for t in a.times]
    snapshots(Path(a.svg), a.times, files, a.scheme, a.scale, a.reduced, bg=a.bg)
    print("\n".join(map(str, files)))


if __name__ == "__main__":
    main()
