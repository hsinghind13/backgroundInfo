# ============================================================================
#  Row-band scan: nbragg fit per band vs the chord model.
#  Needs vol_sample, vol_open_lr, no_nan_divide in memory.   %run -i rowscan.py
# ============================================================================
import math
from math import prod
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import nbragg

# ---------------------------- configure ------------------------------------
CHAN_IMG = slice(100, 300)      # band for the row profile / chord fit
CHAN_FIT = slice(0, 800)        # channels fed to nbragg
COL_BAND = slice(150, 400)      # columns used everywhere
BAND_W, BAND_STEP = 20, 20      # row-band width and spacing
SCAN_ROWS = (200, 500)          # scan this row range
FIT_ROWS  = (200, 510)          # rows used for the chord fit
PX_CM     = 0.0026              # 0.026 mm/px
TSTEP, L  = 1e-5, 8.95
NORM_FIXED, T0_FIXED = 0.3187, 1e-7
AL_NCMAT  = "nbragg/ncmat/Al_sg225.ncmat"
ZRH_NCMAT = "nbragg/ncmat/ZrH1p6_bct.ncmat"
# ---------------------------------------------------------------------------

# ---------- 1. row profile and chord fit -----------------------------------
_T = no_nan_divide(vol_sample[CHAN_IMG, :, COL_BAND].sum(axis=0),
                   vol_open_lr[CHAN_IMG, :, COL_BAND].sum(axis=0))
OT_row = np.nanmean(-np.log(np.where(_T > 0, _T, np.nan)), axis=1)
rows   = np.arange(OT_row.size)

def chord_px(y, R, y0):
    return 2.0*np.sqrt(np.clip(R**2 - (y-y0)**2, 0, None))

def dome(y, S, R, y0, c):
    return S*chord_px(y, R, y0) + c

m = np.isfinite(OT_row) & (rows > FIT_ROWS[0]) & (rows < FIT_ROWS[1])
p, cov = curve_fit(dome, rows[m], OT_row[m], p0=[0.011, 200., 390., 1.14], maxfev=40000)
S_px, R_px, y0, offs = p
perr = np.sqrt(np.diag(cov))
Sig_pellet = S_px/PX_CM
print(f"chord fit  R = {R_px:.1f} +/- {perr[1]:.1f} px    y0 = {y0:.1f} +/- {perr[2]:.1f}")
print(f"           diameter = {2*R_px*PX_CM:.3f} cm     Sigma_pellet = {Sig_pellet:.2f} /cm")
print(f"           constant offset = {offs:.3f}   (-ln(norm) = {-math.log(NORM_FIXED):.3f})")

# ---------- 2. nbragg fit per row band -------------------------------------
def fit_band(lo, hi):
    rgn = np.s_[lo:hi, COL_BAND]
    N = prod([r.stop - r.start for r in rgn])
    s = vol_sample[CHAN_FIT, rgn[0], rgn[1]].mean(axis=(1, 2))
    o = vol_open_lr[CHAN_FIT, rgn[0], rgn[1]].mean(axis=(1, 2))
    if not np.all(np.isfinite(s)) or s.min() <= 0:
        return None
    ob = pd.DataFrame({"stack": np.arange(o.size)+1, "counts": o, "err": np.sqrt(o/N)})
    sm = pd.DataFrame({"stack": np.arange(s.size)+1, "counts": s, "err": np.sqrt(s/N)})
    data = nbragg.Data.from_counts(sm, ob, tstep=TSTEP, L=L)
    xs = 0.2*nbragg.CrossSection(al=AL_NCMAT) + 0.8*nbragg.CrossSection(zrh=ZRH_NCMAT)
    mdl = nbragg.TransmissionModel(xs, vary_background=True, vary_response=True,
                                   vary_weights=True, vary_tof=True)
    mdl.params["thickness"].set(value=1.0, min=0.05, max=4.0)
    mdl.params["norm"].set(value=NORM_FIXED, vary=False)
    mdl.params["t0"].set(value=T0_FIXED, vary=False)
    mdl.params["L0"].set(value=1.0, min=0.98, max=1.02)
    r = mdl.fit(data, wlmin=0.02, wlmax=3.5)
    t, q = r.params["thickness"], r.params["p1"]
    a = math.exp(q.value)/(1+math.exp(q.value)); z = 1-a
    st, sq = (t.stderr or 0.0), (q.stderr or 0.0)
    rho = (q.correl or {}).get("thickness", 0.0)
    dt, dq = z, t.value*(-a*z)
    var = (dt*st)**2 + (dq*sq)**2 + 2*dt*dq*rho*st*sq
    return t.value*z, math.sqrt(max(var, 0.0)), r.redchi

centres, meas, merr, geo, geo_bias = [], [], [], [], []
for lo in range(SCAN_ROWS[0], SCAN_ROWS[1]-BAND_W+1, BAND_STEP):
    hi = lo + BAND_W
    res = fit_band(lo, hi)
    if res is None:
        print(f"  rows {lo}-{hi}: skipped (bad counts)")
        continue
    path, err, rc = res
    yy = np.arange(lo, hi)
    c_cm = chord_px(yy, R_px, y0)*PX_CM
    # what a single-thickness fit returns when the chord varies across the band
    Tavg = np.mean(np.exp(-Sig_pellet*c_cm))
    z_app = -math.log(Tavg)/Sig_pellet if Tavg > 0 else np.nan
    centres.append(0.5*(lo+hi)); meas.append(path); merr.append(err)
    geo.append(c_cm.mean()); geo_bias.append(z_app)
    print(f"  rows {lo}-{hi}: nbragg {path:.4f}+/-{err:.4f}   chord {c_cm.mean():.4f}"
          f"   biased {z_app:.4f}   redchi {rc:.2f}")

centres = np.array(centres); meas = np.array(meas); merr = np.array(merr)
geo = np.array(geo); geo_bias = np.array(geo_bias)

# ---------- 3. one global scale = H/Zr / 2 ---------------------------------
w  = 1.0/np.maximum(merr, 1e-6)**2
ok = np.isfinite(meas) & np.isfinite(geo_bias) & (geo_bias > 0.05)
k  = np.sum(w[ok]*meas[ok]*geo_bias[ok])/np.sum(w[ok]*geo_bias[ok]**2)
resid = meas - k*geo_bias
print(f"\nglobal scale k = {k:.4f}   ->  H/Zr = 2k = {2*k:.3f}")
print(f"residual scatter about the model: {np.nanstd(resid[ok]):.4f} cm "
      f"({100*np.nanstd(resid[ok])/np.nanmean(meas[ok]):.1f}%)")
print(f"mean quoted error:                {np.nanmean(merr[ok]):.4f} cm")

# ---------- 4. plot ---------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8), sharex=True,
                               gridspec_kw={"height_ratios": [3, 1]})
yy = np.linspace(SCAN_ROWS[0], SCAN_ROWS[1], 400)
ax1.plot(yy, k*chord_px(yy, R_px, y0)*PX_CM, lw=1.2, color="0.55",
         label="chord model x k")
ax1.plot(centres, k*geo_bias, lw=1.6, color="#8F6320", ls="--",
         label="chord + averaging bias  (expected)")
ax1.errorbar(centres, meas, yerr=merr, fmt="o", ms=5, color="#256C7D",
             capsize=3, label="nbragg per band")
ax1.set_ylabel("ZrH$_2$-equivalent path [cm]")
ax1.set_title(f"row scan   R = {R_px:.0f} px, y0 = {y0:.0f}, H/Zr = {2*k:.2f}")
ax1.legend(); ax1.grid(alpha=0.25)

ax2.axhline(0, color="0.6", lw=0.8)
ax2.errorbar(centres, resid, yerr=merr, fmt="o", ms=4, color="#8E3E31", capsize=3)
ax2.set_xlabel("row"); ax2.set_ylabel("residual [cm]"); ax2.grid(alpha=0.25)
plt.tight_layout(); plt.show()
