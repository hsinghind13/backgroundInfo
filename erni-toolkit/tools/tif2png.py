#!/usr/bin/env python3
"""TIFF (2D radiograph or 3D TOF stack) -> PNG.

PNG is 8-bit. The data is 16/32-bit counts. Every mapping from counts to
0-255 is a *display* choice: it is lossy and it is not the measurement.
Use this to look at and to present data, never as an input to a fit.
The chosen scaling limits are printed so they can be quoted.
"""
import argparse
import struct
import zlib

import numpy as np

# --- readers/writers: degrade rather than fail on a locked-down machine ------
# tifffile and numpy are pinned in requirements.lock.txt. Pillow is NOT -- it
# only arrives as a matplotlib transitive dependency. So the PNG writer below
# is stdlib-only (zlib + struct) and Pillow is used only if it happens to be
# installed. Nothing here needs a pip install beyond the pinned stack.
try:
    import tifffile
except ImportError:
    tifffile = None
try:
    from PIL import Image
except ImportError:
    Image = None

if tifffile is None and Image is None:
    raise SystemExit("need tifffile (preferred) or Pillow to read TIFF: "
                     "python -m pip install tifffile")


def read_tiff(path):
    """Return the TIFF as an ndarray, (H,W) or (N,H,W)."""
    if tifffile is not None:
        return tifffile.imread(path)
    from PIL import ImageSequence          # Pillow fallback, multipage-safe
    with Image.open(path) as im:
        pages = [np.array(f) for f in ImageSequence.Iterator(im)]
    return pages[0] if len(pages) == 1 else np.stack(pages)


def write_png(path, arr, upscale=1):
    """Write a greyscale PNG. Uses Pillow if present, else stdlib zlib/struct.

    arr is uint8 or uint16, shape (H,W). Returns (width, height).
    """
    if upscale > 1:
        arr = np.repeat(np.repeat(arr, upscale, axis=0), upscale, axis=1)
    h, w = arr.shape
    if Image is not None:
        Image.fromarray(arr).save(path)
        return w, h
    depth = 16 if arr.dtype == np.uint16 else 8
    be = arr.astype('>u2' if depth == 16 else 'u1')
    stride = w * (2 if depth == 16 else 1)
    raw = bytearray()
    flat = be.tobytes()
    for y in range(h):                     # filter byte 0 (None) per scanline
        raw.append(0)
        raw += flat[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data
                + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))

    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, depth, 0, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return w, h


def load(path, slices):
    a = read_tiff(path)
    if a.ndim == 2:
        return a.astype(np.float64), "single frame"
    if a.ndim != 3:
        raise SystemExit(f"unexpected shape {a.shape}")
    n = a.shape[0]
    if slices is None:
        sel = slice(0, n)
    elif ":" in slices:
        lo, hi = slices.split(":")
        sel = slice(int(lo) if lo else 0, int(hi) if hi else n)
    else:
        sel = slice(int(slices), int(slices) + 1)
    sub = a[sel].astype(np.float64)
    return sub.sum(0), f"summed slices {sel.start}:{sel.stop} of {n}"


def scale(img, mode, lo_p, hi_p, vmin, vmax):
    finite = img[np.isfinite(img)]
    if mode == "abs":
        lo = vmin if vmin is not None else finite.min()
        hi = vmax if vmax is not None else finite.max()
        basis = "absolute limits given on the command line"
    else:
        nz = finite[finite > 0]
        pool = nz if nz.size else finite
        lo, hi = np.percentile(pool, [lo_p, hi_p])
        basis = f"{lo_p}-{hi_p} percentile of nonzero pixels"
    if hi <= lo:
        hi = lo + 1.0
    out = np.clip((img - lo) / (hi - lo), 0, 1)
    if mode == "log":
        out = np.log1p(out * 999.0) / np.log(1000.0)
        basis += ", then log1p compressed"
    return out, lo, hi, basis


def selftest():
    """Make a synthetic TOF stack, convert it, read it back. No data needed."""
    import os
    import tempfile
    d = tempfile.mkdtemp(prefix="tif2png-selftest-")
    tif, png = os.path.join(d, "s.tiff"), os.path.join(d, "s.png")

    # 64 TOF bins, 32x32, a bright square on a dim field -- uint32 like the
    # LumaCam stacks. Deterministic, so the checks below are exact.
    n, k = 64, 32
    stack = np.full((n, k, k), 2, dtype=np.uint32)
    stack[:, 8:24, 8:24] = 40
    stack[:8] = 0                                   # empty leading bins
    if tifffile is not None:
        tifffile.imwrite(tif, stack)
    else:
        from PIL import Image as _I
        _I.fromarray(stack[0].astype(np.uint16)).save(
            tif, save_all=True,
            append_images=[_I.fromarray(f.astype(np.uint16)) for f in stack[1:]])

    back = read_tiff(tif)
    assert back.shape == (n, k, k), f"read back {back.shape}, expected {(n, k, k)}"

    img, what = load(tif, None)
    assert img.max() == 40 * (n - 8), f"sum over bins wrong: {img.max()}"

    norm, lo, hi, _ = scale(img, "percentile", 1.0, 99.0, None, None)
    w, h = write_png(png, (norm * 255).astype(np.uint8), upscale=2)
    assert (w, h) == (k * 2, k * 2), f"upscale wrong: {(w, h)}"
    with open(png, "rb") as f:
        assert f.read(8) == b"\x89PNG\r\n\x1a\n", "not a valid PNG"

    print(f"reader  : {'tifffile' if tifffile is not None else 'Pillow'}")
    print(f"writer  : {'Pillow' if Image is not None else 'stdlib zlib'}")
    print(f"stack   : {back.shape} {back.dtype}  ({what})")
    print(f"scale   : {lo:.0f} -> {hi:.0f}")
    print(f"png     : {png}  {w}x{h}")
    print("\nSELFTEST PASS")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("tiff", nargs="?")
    p.add_argument("png", nargs="?")
    p.add_argument("--selftest", action="store_true",
                   help="verify the install on synthetic data; needs no TIFF")
    p.add_argument("--slices", help="'i' for one TOF bin, 'lo:hi' for a range; "
                                    "default sums the whole stack (white beam)")
    p.add_argument("--mode", choices=["percentile", "abs", "log"], default="percentile")
    p.add_argument("--lo", type=float, default=1.0, help="low percentile (default 1)")
    p.add_argument("--hi", type=float, default=99.0, help="high percentile (default 99)")
    p.add_argument("--vmin", type=float, help="absolute low count, with --mode abs")
    p.add_argument("--vmax", type=float, help="absolute high count, with --mode abs")
    p.add_argument("--invert", action="store_true", help="dark = high transmission")
    p.add_argument("--upscale", type=int, default=1, help="integer nearest-neighbour zoom")
    p.add_argument("--sixteen-bit", action="store_true",
                   help="write 16-bit PNG instead of 8-bit (keeps more levels)")
    a = p.parse_args()
    if a.selftest:
        return selftest()
    if not a.tiff or not a.png:
        p.error("need TIFF and PNG paths (or --selftest)")

    img, what = load(a.tiff, a.slices)
    norm, lo, hi, basis = scale(img, a.mode, a.lo, a.hi, a.vmin, a.vmax)
    if a.invert:
        norm = 1.0 - norm

    if a.sixteen_bit:
        arr = (norm * 65535).astype(np.uint16)
    else:
        arr = (norm * 255).astype(np.uint8)
    w, h = write_png(a.png, arr, a.upscale)

    print(f"in    : {a.tiff}  ({what})")
    print(f"counts: min {img.min():.0f}  max {img.max():.0f}  mean {img.mean():.1f}")
    print(f"scale : {lo:.1f} -> {hi:.1f}  ({basis})")
    print(f"out   : {a.png}  {w}x{h}  "
          f"{'16-bit' if a.sixteen_bit else '8-bit'}{'  inverted' if a.invert else ''}")
    print(f"deps  : reader={'tifffile' if tifffile is not None else 'Pillow'}  "
          f"writer={'Pillow' if Image is not None else 'stdlib zlib'}")
    print("note  : display only -- the 8-bit PNG is not the measurement.")


if __name__ == "__main__":
    main()
