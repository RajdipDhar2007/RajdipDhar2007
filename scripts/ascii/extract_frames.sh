#!/usr/bin/env bash
# Extract the wave segment from input/wave.mp4 at 10 fps (-> ~6-8 frames for a 0.8 s wave cycle).
#
#   scripts/ascii/extract_frames.sh [input.mp4] [start_seconds] [duration_seconds]
#
# Defaults: input/wave.mp4, start 0, duration 0.8 s (one wave cycle at 10 fps = 8 frames).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IN="${1:-$ROOT/input/wave.mp4}"
START="${2:-0}"
DUR="${3:-0.8}"
OUT="$ROOT/scripts/ascii/_work/frames"

if [ ! -f "$IN" ]; then
  echo "extract_frames: $IN not found - skipping (build will use the still photo + synthetic wave)" >&2
  exit 0
fi
command -v ffmpeg >/dev/null || { echo "ffmpeg is required" >&2; exit 1; }

rm -rf "$OUT" && mkdir -p "$OUT"
ffmpeg -loglevel error -y -ss "$START" -t "$DUR" -i "$IN" -vf "fps=10" "$OUT/f%02d.png"
echo "extracted $(ls "$OUT" | wc -l) frames -> $OUT"
