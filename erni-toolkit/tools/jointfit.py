# ============================================================================
#  Joint fit: nbragg band results -> P_peak, R, y0.
#  R comes from the dome CURVATURE; the pixel size comes from the known
#  diameter; H/Zr falls out of the peak amplitude.
#  Needs vol_sample, vol_open_lr, no_nan_divide.     %run -i jointfit.py
# ============================================================================
import math
from math import prod
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import nbragg

# ---------------------------- configure ------------------------------------
D_MM      = 10.0                # <-- known pellet diameter, mm
CHAN_IMG  = slice(100, 300)
CHAN_FIT  = slice(0, 800)
COL_BAND  = slice(150, 400)
BAND_W, BAND_STEP = 20, 20
SCAN_ROWS = (200, 500)
TSTEP, L  = 1e-5, 8.95
NORM_FIXED, T0_FIXED = 0.3187, 1e-7
AL_NCMAT  = "nbragg/ncmat/Al_sg225.ncmat"
ZRH_NCMAT = "nbragg/ncmat/ZrH1p6_bct.ncmat"
# ---------------------------------------------------------------------------

# ---------- 1. row profile, for starting values and Sigma_eff --------------
_T = no_nan_divide(vol_sample[CHAN_IMG, :, COL_BAND].sum(axis=0),
                   vol_open_lr[CHAN_IMG, :, COL_BAND].sum(axis=0))
OT_row = np.nanmean(-np.log(np.where(_T > 0, _T, np.nan)), axis=1)
rows = np.arange(OT_row.size)

def dome(y, S, R, y0, c):
    return S*2.0*np.sqrt(np.clip(R**2-(y-y0)**2, 0, None)) + c

m0 = np.isfinite(OT_row) & (rows > 200) & (rows < 510)
p0, _ = curve_fit(dome, rows[m0], OT_row[m0], p0=[0.011, 190., 380., 1.14], maxfev=40000)
S0, R0, y00, off0 = p0
SIG_EFF = (dome(y00, *p0) - off0) / (D_MM/10.0)      # 1/cm, for the bias term
print(f"seed dome fit: R0 = {R0:.1f} px  y0 = {y00:.1f}  offset = {off0:.3f}"
      f"   (-ln norm = {-math.log(NORM_FIXED):.3f})")
print(f"Sigma_eff used for the averaging-bias term: {SIG_EFF:.2f} /cm\n")

# ---------- 2. nbragg per band, dropping bands with no uncertainty ---------
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
    if t.stderr is None or q.stderr is None:        # <-- the bug from last time
        return ("nostderr", None, None)
    a = math.exp(q.value)/(1+math.exp(q.value)); z = 1-a
    rho = (q.correl or {}).get("thickness", 0.0)
    dt, dq = z, t.value*(-a*z)
    var = (dt*t.stderr)**2 + (dq*q.stderr)**2 + 2*dt*dq*rho*t.stderr*q.stderr
    return (t.value*z, math.sqrt(max(var, 0.0)), r.redchi)

bands, meas, merr = [], [], []
for lo in range(SCAN_ROWS[0], SCAN_ROWS[1]-BAND_W+1, BAND_STEP):
    hi = lo + BAND_W
    res = fit_band(lo, hi)
    if res is None:
        print(f"  rows {lo}-{hi}: skipped, bad counts");                  continue
    if res[0] == "nostderr":
        print(f"  rows {lo}-{hi}: DROPPED, no uncertainty from the fit"); continue
    path, err, rc = res
    bands.append((lo, hi)); meas.append(path); merr.append(err)
    print(f"  rows {lo}-{hi}: {path:.4f} +/- {err:.4f} cm   redchi {rc:.2f}")

meas, merr = np.array(meas), np.array(merr)
ctr = np.array([0.5*(a+b) for a, b in bands])
print(f"\nusing {len(meas)} bands\n")

# ---------- 3. joint fit: P_peak (cm), R (px), y0 (px) ---------------------
def band_model(idx, P_peak, R, y0):
    out = np.empty(len(idx))
    for j, i in enumerate(np.asarray(idx, dtype=int)):
        lo, hi = bands[i]
        y = np.arange(lo, hi)
        path = P_peak*np.sqrt(np.clip(1.0-((y-y0)/R)**2, 0, None))
        Tavg = np.mean(np.exp(-SIG_EFF*path))
        out[j] = -np.log(Tavg)/SIG_EFF if Tavg > 0 else 0.0
    return out

idx = np.arange(len(meas))
pj, cj = curve_fit(band_model, idx, meas, sigma=merr, absolute_sigma=True,
                   p0=[D_MM/10.0, R0, y00], maxfev=40000)
P_peak, R_px, y0_px = pj
eP, eR, ey = np.sqrt(np.diag(cj))

D_cm  = D_MM/10.0
px_mm = D_MM/(2*R_px)
HZr   = 2.0*P_peak/D_cm
eHZr  = 2.0*eP/D_cm

fit  = band_model(idx, *pj)
res  = meas - fit
chi2 = np.sum((res/merr)**2)/max(len(meas)-3, 1)

print("=" * 62)
print(f"  R        = {R_px:7.2f} +/- {eR:.2f} px      (from the dome curvature)")
print(f"  y0       = {y0_px:7.2f} +/- {ey:.2f} px")
print(f"  P_peak   = {P_peak:7.4f} +/- {eP:.4f} cm    (ZrH2-equivalent at centre line)")
print(f"  reduced chi2 = {chi2:.2f}")
print("-" * 62)
print(f"  pixel size = {D_MM} mm / (2 x {R_px:.1f} px) = {px_mm:.4f} mm/px")
print(f"     detector geometry gives 14.08/512 = {14.08/512:.4f} mm/px")
print("-" * 62)
print(f"  H/Zr = 2 x {P_peak:.4f} / {D_cm:.3f} = {HZr:.3f} +/- {eHZr:.3f}")
if HZr > 2.0:
    print("  !! above the fluorite ceiling of 2.0 -- check D_MM and the pixel size")
print("=" * 62)

# ---------- 4. plot ---------------------------------------------------------
fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 8), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1]})
yy = np.linspace(SCAN_ROWS[0], SCAN_ROWS[1], 400)
a1.plot(yy, P_peak*np.sqrt(np.clip(1-((yy-y0_px)/R_px)**2, 0, None)),
        lw=1.3, color="0.5", label="joint fit, chord")
a1.plot(ctr, fit, "s", ms=6, mfc="none", color="#8F6320", label="model incl. bias")
a1.errorbar(ctr, meas, yerr=merr, fmt="o", ms=5, color="#256C7D", capsize=3,
            label="nbragg per band")
a1.set_ylabel("ZrH$_2$-equivalent path [cm]")
a1.set_title(f"R = {R_px:.0f} px   px = {px_mm:.4f} mm   "
             f"H/Zr = {HZr:.2f} $\\pm$ {eHZr:.2f}   $\\chi^2_\\nu$ = {chi2:.2f}")
a1.legend(); a1.grid(alpha=0.25)

a2.axhline(0, color="0.6", lw=0.8)
a2.errorbar(ctr, res, yerr=merr, fmt="o", ms=4, color="#8E3E31", capsize=3)
a2.set_xlabel("row"); a2.set_ylabel("residual [cm]"); a2.grid(alpha=0.25)
plt.tight_layout(); plt.show()
