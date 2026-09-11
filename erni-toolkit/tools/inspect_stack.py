"""Step 0 for any new TOF stack: what is actually in this file?

Usage:  python3 inspect_stack.py <stack.tiff> [tstep_us] [L_m]
Reads slice-by-slice via memmap so a multi-GB stack does not blow up memory.
"""
import sys
import numpy as np
import tifffile

path  = sys.argv[1]
tstep = float(sys.argv[2]) * 1e-6 if len(sys.argv) > 2 else 10e-6   # seconds
L     = float(sys.argv[3])       if len(sys.argv) > 3 else 9.014    # metres

with tifffile.TiffFile(path) as tf:
    arr = tf.series[0].asarray(out='memmap')

    print("=" * 66)
    print("FILE      ", path)
    print("SHAPE     ", arr.shape, "  dtype:", arr.dtype)
    print("PAGES     ", len(tf.pages))
    if arr.ndim != 3:
        print("\n!! not a 3D stack -- cannot be a TOF series")
        sys.exit(1)

    nt, ny, nx = arr.shape
    print(f"READ AS   {nt} TOF bins of a {ny}x{nx} image")

    # ---- per-bin total counts: this IS the beam's TOF spectrum ----
    per_bin = np.empty(nt, dtype=np.float64)
    summed  = np.zeros((ny, nx), dtype=np.float64)
    for z in range(nt):
        sl = np.asarray(arr[z], dtype=np.float64)
        per_bin[z] = sl.sum()
        summed += sl

    print("\n" + "-" * 66)
    print("TOF SPECTRUM (summed over all pixels)")
    print(f"  total counts in stack : {per_bin.sum():,.0f}")
    print(f"  counts/bin  min / med / max : {per_bin.min():,.0f} / "
          f"{np.median(per_bin):,.0f} / {per_bin.max():,.0f}")
    print(f"  peak at bin {int(per_bin.argmax())}")

    dead = np.flatnonzero(per_bin == 0)
    weak = np.flatnonzero(per_bin < 0.01 * per_bin.max())
    print(f"  EMPTY bins            : {len(dead)}"
          + (f"  -> {dead[:8].tolist()}{' ...' if len(dead) > 8 else ''}" if len(dead) else ""))
    print(f"  <1% of peak (unusable): {len(weak)}")
    if len(weak):
        first_ok = int(np.flatnonzero(per_bin >= 0.01 * per_bin.max())[0])
        last_ok  = int(np.flatnonzero(per_bin >= 0.01 * per_bin.max())[-1])
        print(f"  usable bin range      : {first_ok} .. {last_ok}")

    # ---- bin index -> wavelength, the decisive check ----
    print("\n" + "-" * 66)
    print(f"WAVELENGTH COVERAGE   (tstep = {tstep*1e6:g} us, L = {L} m)")
    print("  lambda[A] = 3956 * (bin * tstep) / L")
    for b in (1, nt // 4, nt // 2, nt):
        print(f"    bin {b:>6}  ->  t = {b*tstep*1e3:8.3f} ms  ->  lambda = {3956*b*tstep/L:7.3f} A")
    lam_max = 3956 * nt * tstep / L
    print(f"\n  covers lambda up to {lam_max:.3f} A")
    for name, edge in (("delta-ZrH (111) 5.52 A", 5.52),
                       ("alpha-Zr        5.61 A", 5.61),
                       ("calib-free band 5.70 A", 5.70)):
        need = int(np.ceil(edge * L / 3956 / tstep))
        ok = "YES, near bin %d" % need if need <= nt else "NO  (would need %d bins)" % need
        print(f"    {name}  reachable? {ok}")

    # ---- where is the sample, where is the open beam ----
    print("\n" + "-" * 66)
    print("SUMMED IMAGE (for placing ROIs)")
    print(f"  per-pixel counts  min / med / max : {summed.min():,.0f} / "
          f"{np.median(summed):,.0f} / {summed.max():,.0f}")
    hi = summed > np.percentile(summed, 90)
    lo = summed < np.percentile(summed, 10)
    print(f"  brightest decile (open-beam candidate): {hi.sum()} px, "
          f"mean {summed[hi].mean():,.0f}")
    print(f"  darkest decile   (thickest sample)    : {lo.sum()} px, "
          f"mean {summed[lo].mean():,.0f}")
    print(f"  dynamic range bright/dark = {summed[hi].mean()/max(summed[lo].mean(),1):.1f}x")

    ys, xs = np.nonzero(lo)
    if len(ys):
        print(f"  dark region bbox  rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()}")

    # 12x12 ASCII preview so you can see the layout without a viewer
    print("\n  layout preview (dark = more attenuation):")
    k = 12
    blk = summed[:ny // k * k, :nx // k * k].reshape(k, -1, k, (nx // k * k) // k).mean((1, 3))
    ramp = " .:-=+*#%@"
    norm = (blk - blk.min()) / max(blk.ptp(), 1e-9)
    for row in norm:
        print("    " + "".join(ramp[min(int((1 - v) * (len(ramp) - 1)), len(ramp) - 1)] for v in row))
    print("=" * 66)
