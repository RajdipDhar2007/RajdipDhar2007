"""Stage 3: prepped frames -> ASCII text frames (dark + light tone maps).

Grid is COLS x ROWS glyph cells (cell box 6 x 10 px, so the portrait stays square).
Only the arm/hand region may differ between frames: everything outside it is copied
from the base frame, so the head can never shimmer by accident.

With a real wave video (>= 2 prepped frames) the region is detected from motion.
With a single photo the wave is a synthetic accent-coloured hand (placeholder you can
replace by dropping input/wave.mp4 next to input/photo.jpg and re-running the build).

Output (scripts/ascii/_work/ascii/):
    meta.json
    {dark,light}/frame_NN.txt   ROWS lines of COLS glyphs (base portrait + hand)
    mask_NN.txt                 '1' where the cell belongs to the waving hand
"""
from __future__ import annotations
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "scripts" / "ascii" / "_work"
COLS, ROWS = 96, 58
CW, LH = 6.0, 10.0
RAMP = " .`:-=+*cs#%@"
EDGE_THR = 0.6
SIL_THR = 0.45
DETAIL = 2.6
HS = 1.25  # synthetic hand scale (px per design unit)
# synthetic wave: swing angles (degrees) for the 8 frames of one 0.8 s cycle at 10 fps
SWING = [0, 9, 16, 9, 0, -9, -16, -9]
PIVOT = (80.0 * CW, 41.0 * LH)  # wrist/elbow pivot in px, near the right shoulder
REGION = (64, 8, COLS, 42)       # c0, r0, c1, r1 (end-exclusive) - arm/hand cells


def load(path: Path):
    im = Image.open(path).convert("LA")
    l, a = im.split()
    return np.asarray(l, np.float32) / 255, np.asarray(a, np.float32) / 255


def cell_mean(arr: np.ndarray, cols=COLS, rows=ROWS) -> np.ndarray:
    return np.asarray(Image.fromarray(arr).resize((cols, rows), Image.Resampling.BOX))


def edge_field(tone: np.ndarray, mask: np.ndarray):
    """Per-cell (strength 0..1, glyph) from Sobel on tone + silhouette."""
    import cv2
    ft = cv2.GaussianBlur(tone * mask, (0, 0), 2.2)
    fs = cv2.GaussianBlur(mask, (0, 0), 3.0)
    gx = cv2.Sobel(ft, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(ft, cv2.CV_32F, 0, 1, ksize=3)
    sx = cv2.Sobel(fs, cv2.CV_32F, 1, 0, ksize=3)
    sy = cv2.Sobel(fs, cv2.CV_32F, 0, 1, ksize=3)
    cgx, cgy, csx, csy = cell_mean(gx), cell_mean(gy), cell_mean(sx), cell_mean(sy)
    mt = np.hypot(cgx, cgy)
    mt = mt / (np.percentile(mt, 99) + 1e-6)
    ms = np.hypot(csx, csy)
    ms = ms / (ms.max() + 1e-6)
    mag = np.where(ms > SIL_THR, 2.0, mt)  # silhouette edges always win
    cgx = np.where(ms > SIL_THR, csx, cgx)
    cgy = np.where(ms > SIL_THR, csy, cgy)
    phi = np.mod(np.arctan2(cgx, -cgy), math.pi)  # tangent angle (y down)
    glyph = np.empty(mag.shape, dtype="<U1")
    for r in range(mag.shape[0]):
        for c in range(mag.shape[1]):
            p = phi[r, c]
            if p < math.pi / 8 or p >= 7 * math.pi / 8:
                glyph[r, c] = "-" if cgy[r, c] > 0 else "_"
            elif p < 3 * math.pi / 8:
                glyph[r, c] = "\\"
            elif p < 5 * math.pi / 8:
                glyph[r, c] = "|"
            else:
                glyph[r, c] = "/"
    return np.clip(mag, 0, 1.5), glyph


def to_glyphs(tone: np.ndarray, mask: np.ndarray, mode: str):
    import cv2
    t = cell_mean(tone)
    m = cell_mean(mask)
    # local contrast boost at glyph resolution so glasses / eyes / mouth survive the tiny grid
    w = np.clip(m, 0, 1)
    low = cv2.GaussianBlur(t * w, (0, 0), 2.4) / (cv2.GaussianBlur(w, (0, 0), 2.4) + 1e-4)
    t = np.clip(0.72 * t + 0.14 + DETAIL * (t - low), 0, 1)
    inside = m > 0.5
    if inside.sum() > 50:  # histogram-equalise inside the subject so skin tones spread over the ramp
        vals = np.sort(t[inside])
        eq = np.searchsorted(vals, t) / len(vals)
        t = np.where(inside, 0.45 * t + 0.55 * np.clip(eq, 0, 1), t)
    mag, eg = edge_field(tone, mask)
    n = len(RAMP) - 1
    if mode == "dark":     # bright pixel -> dense glyph; hair stays faintly present
        d = 0.16 + 0.84 * np.clip(t, 0, 1) ** 0.85
    else:                  # dark pixel -> dense glyph (ink on paper)
        d = 0.04 + 0.96 * (1 - np.clip(t, 0, 1)) ** 1.1
    idx = np.clip(np.rint(d * n).astype(int), 1, n)
    out = np.full((ROWS, COLS), " ", dtype="<U1")
    subject = m > 0.5
    for r in range(ROWS):
        for c in range(COLS):
            if not subject[r, c]:
                # partial coverage on the silhouette -> outline glyph
                if m[r, c] > 0.12 and mag[r, c] > 1.5:
                    out[r, c] = eg[r, c]
                continue
            g = RAMP[idx[r, c]]
            if mag[r, c] > EDGE_THR and t[r, c] > 0.3:
                g = eg[r, c]
            out[r, c] = g
    return out, t


# ---------------------------------------------------------------- synthetic hand
def _capsule(draw, p0, p1, w, fill=255):
    draw.line([p0, p1], fill=fill, width=int(w))
    for p in (p0, p1):
        draw.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=fill)


def hand_coverage(angle_deg: float, ss: int = 4) -> np.ndarray:
    """Coverage 0..1 per cell of an upright waving hand rotated about the pivot."""
    W, H = int(COLS * CW * ss), int(ROWS * LH * ss)
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    th = math.radians(angle_deg)
    px, py = PIVOT

    def tx(x, y):  # local (x right, y up from pivot) -> canvas
        x, y = x * HS, y * HS
        rx = x * math.cos(th) + y * math.sin(th)
        ry = -x * math.sin(th) + y * math.cos(th)
        return ((px + rx) * ss, (py - ry) * ss)

    # forearm / sleeve, palm, fingers, thumb (all in px, y measured upward)
    d.polygon([tx(-14, 0), tx(14, 0), tx(12, 118), tx(-12, 118)], fill=255)
    d.polygon([tx(-20, 112), tx(20, 112), tx(23, 150), tx(-23, 150)], fill=255)
    for x0, ang, ln in [(-16, -15, 34), (-5.5, -5, 44), (5.5, 5, 46), (16, 15, 36)]:
        a = math.radians(ang)
        base = (x0, 148)
        tip = (x0 + ln * math.sin(a), 148 + ln * math.cos(a))
        _capsule(d, tx(*base), tx(*tip), 6.5 * HS * ss)
    _capsule(d, tx(-20, 126), tx(-44, 146), 8.5 * HS * ss)  # thumb
    arr = np.asarray(img.resize((COLS, ROWS), Image.Resampling.BOX), np.float32) / 255
    return arr


def hand_glyphs(cov: np.ndarray) -> np.ndarray:
    out = np.full(cov.shape, " ", dtype="<U1")
    n = len(RAMP) - 1
    for r, c in zip(*np.nonzero(cov > 0.16)):
        out[r, c] = RAMP[int(np.clip(round(3 + float(cov[r, c]) * (n - 3)), 3, n))]
    return out


# --------------------------------------------------------------------------- main
def main():
    prepped = sorted((WORK / "prepped").glob("f*.png"))
    if not prepped:
        raise SystemExit("frames_to_ascii: run prep.py first")
    out = WORK / "ascii"
    for sub in ("dark", "light"):
        (out / sub).mkdir(parents=True, exist_ok=True)
        for f in (out / sub).glob("*.txt"):
            f.unlink()
    for f in out.glob("mask_*.txt"):
        f.unlink()

    loaded = [load(p) for p in prepped]
    mask = np.median([m for _, m in loaded], axis=0)
    tone_med = np.median([t for t, _ in loaded], axis=0)
    base = {m: to_glyphs(tone_med, mask, m)[0] for m in ("dark", "light")}
    frames: dict[str, list[np.ndarray]] = {"dark": [], "light": []}
    masks: list[np.ndarray] = []
    c0, r0, c1, r1 = REGION

    if len(loaded) >= 2:  # real wave: motion decides the region and the hand cells
        tcells = [cell_mean(t) for t, _ in loaded]
        tmed = np.median(tcells, axis=0)
        diffs = [np.abs(t - tmed) > 0.12 for t in tcells]
        union = np.any(diffs, axis=0)
        ys, xs = np.nonzero(union)
        if len(ys):
            c0, c1, r0, r1 = max(xs.min() - 1, 0), min(xs.max() + 2, COLS), max(ys.min() - 1, 0), min(ys.max() + 2, ROWS)
        for (t, m), dm in zip(loaded, diffs):
            for mode in ("dark", "light"):
                g, _ = to_glyphs(t, m, mode)
                frame = base[mode].copy()
                frame[r0:r1, c0:c1] = g[r0:r1, c0:c1]
                frames[mode].append(frame)
            mk = np.zeros((ROWS, COLS), bool)
            mk[r0:r1, c0:c1] = dm[r0:r1, c0:c1]
            masks.append(mk)
        synthetic = False
    else:                 # one photo: synthetic wave, region cells blanked under the hand
        for ang in SWING:
            cov = hand_coverage(ang)
            hg = hand_glyphs(cov)
            mk = hg != " "
            for mode in ("dark", "light"):
                frame = base[mode].copy()
                frame[mk] = hg[mk]
                frames[mode].append(frame)
            masks.append(mk)
        synthetic = True

    # hard guarantee: outside the region every frame is identical to the base
    for mode in ("dark", "light"):
        for fr in frames[mode]:
            keep = np.ones((ROWS, COLS), bool)
            keep[r0:r1, c0:c1] = False
            fr[keep] = base[mode][keep]
        for i, fr in enumerate(frames[mode]):
            (out / mode / f"frame_{i:02d}.txt").write_text("\n".join("".join(r) for r in fr), encoding="utf-8")
    for i, mk in enumerate(masks):
        (out / f"mask_{i:02d}.txt").write_text("\n".join("".join("1" if v else "0" for v in r) for r in mk), encoding="utf-8")
    for mode in ("dark", "light"):
        (out / f"base-{mode}.txt").write_text("\n".join("".join(r) for r in base[mode]), encoding="utf-8")
    meta = {"cols": COLS, "rows": ROWS, "region": [int(c0), int(r0), int(c1), int(r1)], "frames": len(masks), "synthetic": synthetic}
    (out / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    print("frames_to_ascii:", meta)


def preview(mode="dark", idx=2, path=None):
    """Quick PNG of a frame (dev aid) using PIL's default monospace."""
    from PIL import ImageFont
    out = WORK / "ascii"
    txt = (out / mode / f"frame_{idx:02d}.txt").read_text(encoding="utf-8").split("\n")
    mk = (out / f"mask_{idx:02d}.txt").read_text(encoding="utf-8").split("\n")
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 10)
    bg, fg, acc = ((13, 17, 23), (230, 237, 243), (34, 211, 238)) if mode == "dark" else ((255, 255, 255), (31, 35, 40), (9, 105, 218))
    im = Image.new("RGB", (int(COLS * CW) + 10, int(ROWS * LH) + 10), bg)
    d = ImageDraw.Draw(im)
    for r, line in enumerate(txt):
        for c, ch in enumerate(line):
            if ch != " ":
                d.text((5 + c * CW, 5 + r * LH), ch, font=font, fill=acc if mk[r][c] == "1" else fg)
    im.save(path or WORK / f"preview-{mode}.png")


if __name__ == "__main__":
    main()
