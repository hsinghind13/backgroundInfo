# ============================================================================
#  Multi-region fit with diagnostics.
#  Requires vol_sample and vol_open_lr already in memory (cells 2 and 3).
# ============================================================================
import math
from math import prod
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import nbragg

# ---------------------------- configure ------------------------------------
REGIONS = {
    "rows 330-360": np.s_[330:360, 105:430],
    "rows 220-250": np.s_[220:250, 120:380],
    "rows 200-220": np.s_[200:220, 105:430],
    # add controlled bands here, e.g. all same columns, different heights:
    # "band 360-390": np.s_[360:390, 150:400],
}
COLORS   = ["#d62728", "#ff7f0e", "#1f77b4", "#2ca02c", "#9467bd"]
CHAN_IMG = slice(100, 300)     # channels used for the DISPLAY image only
CHAN_FIT = slice(0, 800)       # channels fed to the fit
TSTEP, L = 1e-5, 8.95
NORM_FIXED, T0_FIXED = 0.3187, 1e-7
AL_NCMAT  = "nbragg/ncmat/Al_sg225.ncmat"
ZRH_NCMAT = "nbragg/ncmat/ZrH1p6_bct.ncmat"
# ---------------------------------------------------------------------------

def box(ax, rgn, color, dx=0, dy=0, lw=2, label=None):
    y0, y1 = rgn[0].start, rgn[0].stop
    x0, x1 = rgn[1].start, rgn[1].stop
    ax.plot([x0-dx, x1-dx, x1-dx, x0-dx, x0-dx],
            [y0-dy, y0-dy, y1-dy, y1-dy, y0-dy],
            color=color, lw=lw, label=label)

# ---- optical-thickness image used for every panel -------------------------
_T  = no_nan_divide(vol_sample[CHAN_IMG].sum(axis=0),
                    vol_open_lr[CHAN_IMG].sum(axis=0))
OT  = -np.log(np.where(_T > 0, _T, np.nan))
lo, hi = np.nanpercentile(OT, [2, 98])

# ================= FIGURE 1 : overview, all boxes ==========================
fig, ax = plt.subplots(figsize=(6.5, 6.5))
im = ax.imshow(OT, cmap="viridis", vmin=lo, vmax=hi)
fig.colorbar(im, ax=ax, label="optical thickness  $\\Sigma z$", shrink=0.82)
for (name, rgn), c in zip(REGIONS.items(), COLORS):
    box(ax, rgn, c, label=name)
ax.set_title("regions on the pellet")
ax.set_xlabel("column"); ax.set_ylabel("row")
ax.legend(fontsize=8, loc="lower right")
plt.tight_layout()

# ================= FIGURE 2 : per region, zoom + spectrum ==================
n = len(REGIONS)
fig, axes = plt.subplots(n, 2, figsize=(12.5, 3.4 * n),
                         gridspec_kw={"width_ratios": [1, 1.7]})
axes = np.atleast_2d(axes)

results = {}
for i, ((name, rgn), c) in enumerate(zip(REGIONS.items(), COLORS)):
    y0, y1 = rgn[0].start, rgn[0].stop
    x0, x1 = rgn[1].start, rgn[1].stop

    # ---------- left: zoomed crop with the box ----------
    m = 60
    ys = slice(max(0, y0 - m), min(OT.shape[0], y1 + m))
    xs = slice(max(0, x0 - m), min(OT.shape[1], x1 + m))
    axL = axes[i, 0]
    axL.imshow(OT[ys, xs], cmap="viridis", vmin=lo, vmax=hi,
               extent=[xs.start, xs.stop, ys.stop, ys.start])
    box(axL, rgn, c, lw=2.2)
    axL.set_title(f"{name}   mean $\\Sigma z$ = {np.nanmean(OT[rgn]):.2f}",
                  fontsize=10, color=c)
    axL.set_xlabel("column"); axL.set_ylabel("row")

    # ---------- spectra ----------
    N = prod([r.stop - r.start for r in rgn])
    s = vol_sample[CHAN_FIT, rgn[0], rgn[1]].mean(axis=(1, 2))
    o = vol_open_lr[CHAN_FIT, rgn[0], rgn[1]].mean(axis=(1, 2))
    trans = no_nan_divide(s, o)
    sig   = np.abs(trans) * np.sqrt((np.sqrt(s / N) / s) ** 2 +
                                    (np.sqrt(o / N) / o) ** 2)
    wl = (np.arange(trans.size) + 1) * (3956e-5 / L)

    openbm = pd.DataFrame({"stack": np.arange(o.size)+1, "counts": o, "err": np.sqrt(o/N)})
    sample = pd.DataFrame({"stack": np.arange(s.size)+1, "counts": s, "err": np.sqrt(s/N)})
    data   = nbragg.Data.from_counts(sample, openbm, tstep=TSTEP, L=L)

    # rebuild the cross section each time -- nbragg mutates it while fitting
    xs_i = 0.2*nbragg.CrossSection(al=AL_NCMAT) + 0.8*nbragg.CrossSection(zrh=ZRH_NCMAT)
    mdl  = nbragg.TransmissionModel(xs_i, vary_background=True, vary_response=True,
                                    vary_weights=True, vary_tof=True)
    mdl.params["thickness"].set(value=1.2, min=0.5, max=4.0)
    mdl.params["norm"].set(value=NORM_FIXED, vary=False)
    mdl.params["t0"].set(value=T0_FIXED, vary=False)
    mdl.params["L0"].set(value=1.0, min=0.98, max=1.02)
    r = mdl.fit(data, wlmin=0.02, wlmax=3.5)

    # ---------- right: transmission vs wavelength ----------
    axR = axes[i, 1]
    axR.plot(wl, trans, lw=0.8, color=c, label="measured")
    axR.fill_between(wl, trans - sig, trans + sig, color=c, alpha=0.25, lw=0)
    bf = getattr(r, "best_fit", None)
    if bf is not None and len(bf) == len(data.table):
        axR.plot(data.table["wavelength"], bf, lw=1.4, color="k", ls="--", label="fit")
    axR.set_xlim(0, 3.5); axR.set_yscale("log")
    axR.set_xlabel("wavelength [A]"); axR.set_ylabel("transmission")
    axR.legend(fontsize=8)

    # ---------- ZrH path with correlated error ----------
    t, p = r.params["thickness"], r.params["p1"]
    a  = math.exp(p.value) / (1 + math.exp(p.value)); z = 1 - a
    st, sp = (t.stderr or 0.0), (p.stderr or 0.0)
    rho = (p.correl or {}).get("thickness", 0.0)
    dt, dp = z, t.value * (-a * z)
    var = (dt*st)**2 + (dp*sp)**2 + 2*dt*dp*rho*st*sp
    path, spath = t.value * z, math.sqrt(max(var, 0.0))
    results[name] = dict(path=path, err=spath, thickness=t.value, zrh=z,
                         redchi=r.redchi, otmean=float(np.nanmean(OT[rgn])))
    axR.set_title(f"ZrH path = {path:.3f} $\\pm$ {spath:.3f} cm    "
                  f"$\\chi^2_\\nu$ = {r.redchi:.2f}", fontsize=10)

plt.tight_layout()
plt.show()

# ================= summary ==================================================
print(f"{'region':<16}{'mean OT':>9}{'ZrH path [cm]':>18}{'thickness':>11}{'zrh':>8}{'redchi':>9}")
for k, v in results.items():
    print(f"{k:<16}{v['otmean']:9.2f}{v['path']:11.4f} +/-{v['err']:6.4f}"
          f"{v['thickness']:11.3f}{v['zrh']:8.3f}{v['redchi']:9.2f}")

pv = [v["path"] for v in results.values()]
ov = [v["otmean"] for v in results.values()]
print(f"\nZrH path spread : {max(pv)-min(pv):.4f} cm ({100*(max(pv)-min(pv))/np.mean(pv):.1f}%)")
print(f"mean OT spread  : {max(ov)-min(ov):.2f}    ({100*(max(ov)-min(ov))/np.mean(ov):.1f}%)")
print("\nIf these two percentages track each other, the spread is CHORD LENGTH,")
print("not hydrogen -- both scale with how much material the beam crosses.")
