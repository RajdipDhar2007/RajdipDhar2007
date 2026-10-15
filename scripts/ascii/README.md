# ASCII portrait pipeline

Builds the animated terminal portrait in the profile README:
`assets/ascii/portrait-dark.svg`, `portrait-light.svg` and the `portrait.gif` fallback.

```bash
pip install -r scripts/requirements.txt
python -m playwright install chromium     # only if Chrome/Edge is not installed
python scripts/ascii/build_svg.py         # the whole pipeline, one command
```

## Inputs (all optional)

| File | What | Fallback when missing |
|---|---|---|
| `input/photo.jpg` (or `.png`) | head-and-shoulders photo, plain background is fine | `assets/source/profile-vector.svg`, then a generated silhouette |
| `input/wave.mp4` | 3-5 s of you waving, camera still | a synthetic, accent-coloured waving hand (placeholder) |

`input/` is gitignored, so your raw photo and video are never committed.

## Stages

1. `extract_frames.sh` - ffmpeg the wave at 10 fps (8 frames = one 0.8 s wave cycle).
2. `prep.py` - background removal (existing alpha -> `rembg` if installed -> GrabCut), CLAHE contrast,
   head-anchored fixed crop and one fixed exposure for every frame, so the head never jitters.
3. `frames_to_ascii.py` - 96x58 glyph grid, ramp `` .`:-=+*cs#%@``, Sobel edge glyphs `/ \ | _`.
   Only the arm/hand region may differ between frames; everything else is copied from the base frame.
4. `build_svg.py` - one SVG per theme (static rows once, per-frame groups for the arm region), GIF
   via Pillow (+ `gifsicle -O3 --lossy=20` when installed) and PNG snapshots in `preview/`.

## Timeline (12 s loop)

| Time | Phase |
|---|---|
| 0.0-0.8 s | boot: types the command, progress bar fills |
| 0.8-2.6 s | scan line sweeps down; each row resolves from 3 scrambled versions |
| 2.6-3.0 s | cyan/violet glitch copies flash twice, then sharp; `identity verified` |
| 3.0-5.4 s | the hand waves 3x (frame swap on the arm region only); greeting is typed |
| 5.4-12 s | idle: blinking cursor, ~40 shimmering glyphs, faint scan every 4 s |
| 11.6-12 s | glitch-out, loop |

`prefers-reduced-motion: reduce` freezes the final composed frame (hand raised, text typed).

## Budgets

SVG < 500 KB (the build fails otherwise), GIF < 2 MB. Knobs: `COLS, ROWS` in `frames_to_ascii.py`,
`SCRAMBLE`, shimmer count and timeline constants in `build_svg.py`.
