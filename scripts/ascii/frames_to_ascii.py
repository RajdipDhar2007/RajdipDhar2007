"""Stage 3: prepped portrait -> ASCII text grids (dark + light tone maps).

Grid is COLS x ROWS glyph cells (cell box 6 x 10 px, so the portrait stays square).
Tone ramp ` .`:-=+*cs#%@`, Sobel edge glyphs `/ \\ | _` on the silhouette and strong features.

Output (scripts/ascii/_work/ascii/): meta.json, base-dark.txt, base-light.txt
"""
from __future__ import annotations
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "scripts" / "ascii" / "_work"
COLS, ROWS = 96, 58
RAMP = " .`:-=+*cs#%@"
EDGE_THR = 0.6
SIL_THR = 0.45
DETAIL = 2.6


def load(path: Path):
    l, a = Image.open(path).convert("LA").split()
    return np.asarray(l, np.float32) / 255, np.asarray(a, np.float32) / 255


def cell_mean(arr: np.ndarray, cols=COLS, rows=ROWS) -> np.ndarray:
    return np.asarray(Image.fromarray(arr).resize((cols, rows), Image.Resampling.BOX))


def edge_field(tone: np.ndarray, mask: np.ndarray):
    """Per-cell (strength, glyph) from Sobel on tone + silhouette."""
    import cv2
    ft = cv2.GaussianBlur(tone * mask, (0, 0), 2.2)
    fs = cv2.GaussianBlur(mask, (0, 0), 3.0)
    gx, gy = (cv2.Sobel(ft, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(ft, cv2.CV_32F, 0, 1, ksize=3))
    sx, sy = (cv2.Sobel(fs, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(fs, cv2.CV_32F, 0, 1, ksize=3))
    cgx, cgy, csx, csy = cell_mean(gx), cell_mean(gy), cell_mean(sx), cell_mean(sy)
    mt = np.hypot(cgx, cgy)
    mt = mt / (np.percentile(mt, 99) + 1e-6)
    ms = np.hypot(csx, csy)
    ms = ms / (ms.max() + 1e-6)
    sil = ms > SIL_THR
    mag = np.where(sil, 2.0, mt)                      # silhouette edges always win
    cgx, cgy = np.where(sil, csx, cgx), np.where(sil, csy, cgy)
    phi = np.mod(np.arctan2(cgx, -cgy), math.pi)      # tangent angle (y down)
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
    return np.clip(mag, 0, 2.0), glyph


def to_glyphs(tone: np.ndarray, mask: np.ndarray, mode: str) -> np.ndarray:
    import cv2
    t, m = cell_mean(tone), cell_mean(mask)
    mag, eg = edge_field(tone, mask)
    # local contrast boost at glyph resolution so glasses / eyes / mouth survive the small grid
    w = np.clip(m, 0, 1)
    low = cv2.GaussianBlur(t * w, (0, 0), 2.4) / (cv2.GaussianBlur(w, (0, 0), 2.4) + 1e-4)
    t = np.clip(0.72 * t + 0.14 + DETAIL * (t - low), 0, 1)
    inside = m > 0.5
    if inside.sum() > 50:                             # equalise inside the subject so skin tones spread over the ramp
        vals = np.sort(t[inside])
        eq = np.searchsorted(vals, t) / len(vals)
        t = np.where(inside, 0.45 * t + 0.55 * np.clip(eq, 0, 1), t)
    n = len(RAMP) - 1
    d = 0.16 + 0.84 * np.clip(t, 0, 1) ** 0.85 if mode == "dark" else 0.04 + 0.96 * (1 - np.clip(t, 0, 1)) ** 1.1
    idx = np.clip(np.rint(d * n).astype(int), 1, n)
    out = np.full((ROWS, COLS), " ", dtype="<U1")
    for r in range(ROWS):
        for c in range(COLS):
            if not inside[r, c]:
                if m[r, c] > 0.12 and mag[r, c] > 1.5:
                    out[r, c] = eg[r, c]
                continue
            out[r, c] = eg[r, c] if (mag[r, c] > EDGE_THR and t[r, c] > 0.3) else RAMP[idx[r, c]]
    return out


def main():
    prepped = sorted((WORK / "prepped").glob("f*.png"))
    if not prepped:
        raise SystemExit("frames_to_ascii: run prep.py first")
    out = WORK / "ascii"
    out.mkdir(parents=True, exist_ok=True)
    tone, mask = load(prepped[0])
    for mode in ("dark", "light"):
        grid = to_glyphs(tone, mask, mode)
        (out / f"base-{mode}.txt").write_text("\n".join("".join(r) for r in grid), encoding="utf-8")
    (out / "meta.json").write_text(json.dumps({"cols": COLS, "rows": ROWS}), encoding="utf-8")
    print(f"frames_to_ascii: {COLS}x{ROWS} grid -> {out}")


if __name__ == "__main__":
    main()
