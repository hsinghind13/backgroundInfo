#!/usr/bin/env bash
# tif2png.sh FILE.tiff [VMIN VMAX]
#   Converts a radiograph / TOF stack to PNG and opens it in Preview.
#   With no VMIN/VMAX it stretches to the image's own min/max -- fine for a
#   quick look, WRONG for comparing two images. Pass limits to compare.
set -euo pipefail

[ $# -ge 1 ] || { echo "usage: $(basename "$0") FILE.tiff [VMIN VMAX]" >&2; exit 1; }
SRC="$1"
[ -f "$SRC" ] || { echo "no such file: $SRC" >&2; exit 1; }
OUT="${SRC%.*}.png"

python3 - "$SRC" "$OUT" "${2:-}" "${3:-}" <<'PY'
import sys
import numpy as np, tifffile
from PIL import Image

src, out, vmin, vmax = sys.argv[1:5]
a = tifffile.imread(src)
img = (a.sum(0) if a.ndim == 3 else a).astype(float)

if vmin and vmax:
    lo, hi, how = float(vmin), float(vmax), "fixed limits"
else:
    lo, hi, how = img.min(), img.max(), "this image's own min/max"

Image.fromarray((np.clip((img - lo) / (hi - lo), 0, 1) * 255).astype('uint8')).save(out)
print(f"{a.shape} {a.dtype}  counts {img.min():.0f}..{img.max():.0f}")
print(f"scaled {lo:.0f}..{hi:.0f}  ({how})")
PY

echo "wrote $OUT"
open "$OUT"
