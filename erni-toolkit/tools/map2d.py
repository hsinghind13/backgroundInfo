# ============================================================================
#  2D optical-thickness map with row and column marginals, plus a chord fit.
#  Needs vol_sample, vol_open_lr, no_nan_divide already in memory.
#  Run with:  %run -i map2d.py
# ============================================================================
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ---------------------------- configure ------------------------------------
CHAN     = slice(100, 300)   # wavelength band (the one that worked)
COL_BAND = slice(150, 400)   # columns averaged for the ROW profile
ROW_BAND = slice(380, 420)   # rows averaged for the COLUMN profile (near dome peak)
FIT_ROWS = (250, 500)        # clean part of the dome for the chord fit
NORM, BG = 0.3187, 0.0035    # from the nbragg fit; set NORM=1, BG=0 for raw
# ---------------------------------------------------------------------------

# ---- optical thickness over the whole frame -------------------------------
num = vol_sample[CHAN].sum(axis=0)
den = vol_open_lr[CHAN].sum(axis=0)
T   = no_nan_divide(num, den)
T   = (T - BG) / NORM                       # undo background and exposure ratio
OT  = -np.log(np.where(T > 0, T, np.nan))

rows = np.arange(OT.shape[0])
cols = np.arange(OT.shape[1])
row_prof = np.nanmean(OT[:, COL_BAND], axis=1)      # vs row  -> geometry
col_prof = np.nanmean(OT[ROW_BAND, :], axis=0)      # vs col  -> hydrogen

# ---- fit the chord model to the dome --------------------------------------
def chord(y, S, R, y0, c):
    return S * 2.0 * np.sqrt(np.clip(R**2 - (y - y0)**2, 0, None)) + c

m = np.isfinite(row_prof) & (rows > FIT_ROWS[0]) & (rows < FIT_ROWS[1])
p, cov = curve_fit(chord, rows[m], row_prof[m],
                   p0=[0.02, 150.0, 0.5*(FIT_ROWS[0]+FIT_ROWS[1]), 0.0], maxfev=20000)
S_fit, R_fit, y0_fit, c_fit = p
err = np.sqrt(np.diag(cov))
print(f"chord fit:  R = {R_fit:.1f} +/- {err[1]:.1f} px    "
      f"centre row = {y0_fit:.1f} +/- {err[2]:.1f}    "
      f"Sigma = {S_fit:.4f} /px    offset = {c_fit:.3f}")
print(f"            diameter = {2*R_fit:.1f} px = {2*R_fit*0.026:.2f} mm  (at 0.026 mm/px)")
print(f"            peak chord Sigma*z = {chord(y0_fit,*p):.3f}")

def panel(field, rprof, cprof, title, cmap="viridis", overlay_fit=False):
    lo, hi = np.nanpercentile(field, [2, 98])
    fig = plt.figure(figsize=(9.5, 8.5))
    gs  = fig.add_gridspec(2, 2, width_ratios=[3, 1], height_ratios=[3, 1],
                           wspace=0.05, hspace=0.05)
    axM = fig.add_subplot(gs[0, 0])
    axR = fig.add_subplot(gs[0, 1], sharey=axM)
    axB = fig.add_subplot(gs[1, 0], sharex=axM)

    im = axM.imshow(field, cmap=cmap, vmin=lo, vmax=hi, aspect="auto")
    axM.axhspan(ROW_BAND.start, ROW_BAND.stop, color="w", alpha=0.22)
    axM.axvspan(COL_BAND.start, COL_BAND.stop, color="w", alpha=0.12)
    axM.axhline(y0_fit, color="w", lw=0.8, ls="--")
    axM.set_ylabel("row"); axM.set_title(title)
    plt.setp(axM.get_xticklabels(), visible=False)

    axR.plot(rprof, rows, lw=1.0, color="#256C7D")
    if overlay_fit:
        axR.plot(chord(rows[m], *p), rows[m], lw=1.4, color="k", ls="--")
    axR.axhspan(ROW_BAND.start, ROW_BAND.stop, color="k", alpha=0.10)
    axR.set_xlabel("row profile"); axR.grid(alpha=0.25)
    plt.setp(axR.get_yticklabels(), visible=False)

    axB.plot(cols, cprof, lw=1.0, color="#8F6320")
    axB.axvspan(COL_BAND.start, COL_BAND.stop, color="k", alpha=0.10)
    axB.set_xlabel("column"); axB.set_ylabel("col profile"); axB.grid(alpha=0.25)

    fig.colorbar(im, ax=axB, orientation="horizontal", fraction=0.35, pad=0.45)
    return fig

panel(OT, row_prof, col_prof,
      "optical thickness  $\\Sigma z$   (GEOMETRY + hydrogen)", overlay_fit=True)

# ---- chord-corrected map: divide out the geometry -------------------------
shape = chord(rows, S_fit, R_fit, y0_fit, 0.0)
shape = np.where(shape > 0.25 * shape.max(), shape, np.nan)   # drop the thin rim
SIGMA = OT / shape[:, None] * shape[int(round(y0_fit))]        # scaled to the centre line

sig_row = np.nanmean(SIGMA[:, COL_BAND], axis=1)
sig_col = np.nanmean(SIGMA[ROW_BAND, :], axis=0)

panel(SIGMA, sig_row, sig_col,
      "chord-corrected   (HYDROGEN, geometry removed)", cmap="magma")
plt.show()

# ---- what the corrected map says ------------------------------------------
inner = SIGMA[ROW_BAND, COL_BAND]
print(f"\ncorrected map, inner region: mean {np.nanmean(inner):.3f}  "
      f"std {np.nanstd(inner):.3f}  ({100*np.nanstd(inner)/np.nanmean(inner):.1f}%)")
good = np.isfinite(sig_col) & (cols > COL_BAND.start) & (cols < COL_BAND.stop)
if good.sum() > 10:
    sl = np.polyfit(cols[good], sig_col[good], 1)[0]
    span = sl * (COL_BAND.stop - COL_BAND.start)
    print(f"column profile slope across the band: {span:+.3f} in Sigma*z "
          f"({100*span/np.nanmean(sig_col[good]):+.1f}%)")
    print(f"  -> Delta(H/Zr) approx {span/np.nanmean(sig_col[good])/0.045*0.1:+.3f} along the axis")
