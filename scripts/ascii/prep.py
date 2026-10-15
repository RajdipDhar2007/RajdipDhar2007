"""Stage 2: background removal, contrast, aligned fixed crop.

Sources, in order of preference
  1. scripts/ascii/_work/frames/*.png   (from extract_frames.sh, input/wave.mp4)
  2. input/photo.jpg | .jpeg | .png
  3. assets/source/profile-vector.svg   (rasterised with headless Chrome, has alpha)
  4. a generated placeholder silhouette

Output: scripts/ascii/_work/prepped/fNN.png - "LA" images (L = tone, A = subject mask),
all with the SAME crop and the SAME exposure so only moving pixels differ between frames.
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "scripts" / "ascii" / "_work"
SIZE = 640  # working resolution of the square crop


def rasterise_svg(svg: Path, size: int = 1254) -> Image.Image:
    sys.path.insert(0, str(ROOT / "scripts"))
    from snap import launch
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = launch(p)
        page = b.new_page(viewport={"width": size, "height": size})
        page.goto(svg.resolve().as_uri())
        tmp = WORK / "_svg.png"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(tmp), omit_background=True)
        b.close()
    return Image.open(tmp).convert("RGBA")


def placeholder() -> Image.Image:
    im = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((280, 120, 520, 400), fill=(214, 160, 110, 255))          # head
    d.rectangle((360, 380, 440, 470), fill=(200, 145, 100, 255))        # neck
    d.pieslice((120, 430, 680, 1050), 180, 360, fill=(40, 42, 54, 255))  # shoulders
    d.pieslice((270, 100, 530, 330), 180, 360, fill=(30, 28, 40, 255))   # hair
    return im


def remove_bg(im: Image.Image) -> Image.Image:
    """Return RGBA with a usable alpha. Uses existing alpha, rembg if installed, else GrabCut."""
    a = np.asarray(im.convert("RGBA"))[..., 3]
    if a.min() < 250:
        return im.convert("RGBA")
    try:
        from rembg import remove  # type: ignore
        return remove(im.convert("RGB")).convert("RGBA")
    except Exception:  # noqa: BLE001
        pass
    import cv2
    rgb = np.asarray(im.convert("RGB"))
    h, w = rgb.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    rect = (int(w * .08), int(h * .05), int(w * .84), int(h * .93))
    bg = np.zeros((1, 65), np.float64)
    fg = np.zeros((1, 65), np.float64)
    cv2.grabCut(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), mask, rect, bg, fg, 4, cv2.GC_INIT_WITH_RECT)
    alpha = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    out = im.convert("RGBA")
    out.putalpha(Image.fromarray(alpha))
    return out


def head_anchor(im: Image.Image) -> tuple[float, float]:
    """Stable anchor: detected face centre, else centroid of the top 35% of the subject mask."""
    import cv2
    rgba = np.asarray(im)
    gray = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2GRAY)
    cascade_cls = getattr(cv2, "CascadeClassifier", None)  # absent in some OpenCV 5 builds
    data = getattr(cv2, "data", None)
    for name in ("haarcascade_frontalface_default.xml", "haarcascade_profileface.xml"):
        if cascade_cls is None or data is None:
            break
        faces = cascade_cls(data.haarcascades + name).detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
        if len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            return x + w / 2, y + h / 2
    ys, xs = np.nonzero(rgba[..., 3] > 128)
    if len(ys) == 0:
        return im.width / 2, im.height / 2
    top = ys < ys.min() + 0.35 * (ys.max() - ys.min())
    return float(xs[top].mean()), float(ys[top].mean())


def square_crop_box(im: Image.Image) -> tuple[float, float, float]:
    ys, xs = np.nonzero(np.asarray(im)[..., 3] > 128)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    side = max(x1 - x0, y1 - y0) * 1.06
    return (x0 + x1) / 2, (y0 + y1) / 2, side


def tone(gray: np.ndarray, mask: np.ndarray, lo_hi=None):
    import cv2
    g8 = gray.astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(6, 6))
    g = clahe.apply(g8).astype(np.float32)
    if lo_hi is None:  # fixed exposure: measured once on the reference frame
        vals = g[mask > 0.5]
        lo_hi = (np.percentile(vals, 2), np.percentile(vals, 98))
    g = np.clip((g - lo_hi[0]) / max(lo_hi[1] - lo_hi[0], 1), 0, 1)
    return g, lo_hi


def load_sources() -> list[Image.Image]:
    frames = sorted((WORK / "frames").glob("*.png"))
    if frames:
        return [remove_bg(Image.open(f)) for f in frames]
    for ext in ("jpg", "jpeg", "png"):
        p = ROOT / "input" / f"photo.{ext}"
        if p.exists():
            return [remove_bg(Image.open(p))]
    svg = ROOT / "assets" / "source" / "profile-vector.svg"
    if svg.exists():
        print("prep: using assets/source/profile-vector.svg (no input/photo.jpg found)")
        return [rasterise_svg(svg)]
    print("prep: no photo found - using generated placeholder silhouette")
    return [placeholder()]


def main():
    out = WORK / "prepped"
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.png"):
        f.unlink()
    srcs = load_sources()
    ref = srcs[0]
    ax0, ay0 = head_anchor(ref)
    cx, cy, side = square_crop_box(ref)
    lo_hi = None
    for i, im in enumerate(srcs):
        ax, ay = head_anchor(im) if i else (ax0, ay0)
        # translate so the head anchor sits on the reference anchor -> the head never jitters
        box = (cx - side / 2 + (ax - ax0), cy - side / 2 + (ay - ay0), cx + side / 2 + (ax - ax0), cy + side / 2 + (ay - ay0))
        crop = im.crop(tuple(int(round(v)) for v in box)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        rgba = np.asarray(crop)
        mask = rgba[..., 3].astype(np.float32) / 255
        white = rgba[..., :3].astype(np.float32) * mask[..., None] + 255 * (1 - mask[..., None])
        gray = np.dot(white, [0.299, 0.587, 0.114])
        g, lo_hi = tone(gray, mask, lo_hi)
        la = np.dstack([(g * 255).astype(np.uint8), (mask * 255).astype(np.uint8)])
        Image.fromarray(la, "LA").save(out / f"f{i:02d}.png")
    print(f"prep: {len(srcs)} frame(s) -> {out}")


if __name__ == "__main__":
    main()
