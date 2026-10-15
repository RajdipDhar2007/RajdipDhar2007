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

`input/` is gitignored, so your raw photo is never committed.

## Stages

1. `prep.py` - background removal (existing alpha, then `rembg` if installed, then GrabCut), CLAHE contrast,
   head-anchored square crop and fixed exposure.
2. `frames_to_ascii.py` - 96x58 glyph grid, ramp `` .`:-=+*cs#%@``, Sobel edge glyphs `/ \ | _`, separate dark and light tone maps.
3. `build_svg.py` - one SVG per theme, plus `portrait.gif` (Pillow, + `gifsicle -O3 --lossy=20` when installed)
   and PNG snapshots in `preview/`.

## Timeline (12 s loop)

| Time | Phase |
|---|---|
| 0.0-0.8 s | boot: the command is typed, progress bar fills |
| 0.8-2.6 s | scan line sweeps down; each row resolves from 3 scrambled versions |
| 2.6-3.0 s | cyan/violet glitch copies flash twice, then sharp; `identity verified` |
| 3.0-11.6 s | idle: light sweeps across the glyphs, glitch bands, hex rain, ~48 shimmering glyphs, blinking cursor, faint scans |
| 11.6-12 s | glitch-out, loop |

`prefers-reduced-motion: reduce` freezes the final frame. SVG budget: < 500 KB (the build fails otherwise).
