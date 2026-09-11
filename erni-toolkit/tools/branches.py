# branches.py -- split the ramp into heat-up and cool-down, pair frames at the
# same temperature, and read the gap as hydrogen that did not come back.
#
#   %run -i time_series.py      (defines series, temps, times, labels)
#   %run -i branches.py
#
# The gap at temperature T is a difference between two frames at the SAME
# temperature, so sigma(T), Debye-Waller and thermal expansion all cancel.
# Nothing here needs an NCrystal cross section.

import numpy as np
import matplotlib.pyplot as plt

REGION = "centre"        # or "end L" / "end R"
TOL = 15.0               # K -- how close two setpoints must be to pair
ONSET_LIT = 750.0        # K -- literature desorption onset, EXTERNAL to this data

y = np.array(series[REGION], dtype=float)
T = np.array(temps, dtype=float)
t = np.array(times, dtype=float)

peak = int(np.argmax(T))
up = np.arange(0, peak + 1)
dn = np.arange(peak, len(T))
print("heat-up frames :", [labels[i] for i in up])
print("cool-down      :", [labels[i] for i in dn])

# ---- pair frames at matching temperature ----------------------------------
pair_T = []
pair_up = []
pair_dn = []
for i in up:
    j_best = -1
    d_best = TOL
    for j in dn:
        d = abs(T[j] - T[i])
        if d < d_best:
            d_best = d
            j_best = j
    if j_best >= 0:
        pair_T.append(0.5 * T[i] + 0.5 * T[j_best])
        pair_up.append(y[i])
        pair_dn.append(y[j_best])

pair_T = np.array(pair_T)
pair_up = np.array(pair_up)
pair_dn = np.array(pair_dn)
gap = pair_up - pair_dn                    # positive = thickness lost
frac = 100.0 * gap / pair_up

print()
print("SAME-TEMPERATURE PAIRS  region =", REGION)
print("  T[K]     up      down      gap     gap%    dH/H%")
for k in range(len(pair_T)):
    print("  " + str(round(float(pair_T[k]), 1)).rjust(6),
          str(round(float(pair_up[k]), 4)).rjust(8),
          str(round(float(pair_dn[k]), 4)).rjust(8),
          str(round(float(gap[k]), 4)).rjust(8),
          str(round(float(frac[k]), 2)).rjust(7),
          str(round(float(1.4 * frac[k]), 2)).rjust(8))

# ---- onset: lowest paired T where the gap clears the drift floor ----------
can = np.array(series["can"], dtype=float)
floor = float(can.max() - can.min())
print()
print("drift floor from the can ROI :", round(floor, 4))
sig = np.flatnonzero(gap > floor)
if len(sig):
    print("gap clears the floor from T =", round(float(pair_T[sig[0]]), 1), "K")
    print("  literature desorption onset for comparison :", ONSET_LIT, "K")
else:
    print("no pair clears the drift floor -- no loss resolved at this precision")
    print("  upper limit on dH/H :", round(float(1.4 * 100 * floor / y[0]), 2), "%")

# ---- thermal-only baseline from the pre-onset heat-up ---------------------
# BASIS: below the desorption onset no hydrogen leaves, so all variation on the
# heat-up branch is sigma(T) + expansion. Fit it there, extrapolate, and excess
# above it is loss. SELF-REFERENTIAL unless ONSET_LIT is external -- it is
# (Zr hydride plateau pressures), so state which value you used and its source.
pre = up[T[up] < ONSET_LIT]
if len(pre) >= 2:
    c = np.polyfit(T[pre], y[pre], 1)
    base = np.polyval(c, T)
    excess = base - y
    print()
    print("thermal baseline fitted over", len(pre), "pre-onset frames, slope",
          round(float(c[0]), 6), "per K")
    print("  frame            T[K]   excess over baseline   dH/H%")
    for i in range(len(T)):
        print("  " + labels[i].ljust(15), str(T[i]).rjust(6),
              str(round(float(excess[i]), 4)).rjust(10),
              str(round(float(1.4 * 100 * excess[i] / y[0]), 2)).rjust(10))
else:
    base = None
    print()
    print("not enough pre-onset frames to fit a thermal baseline")

# ---- plots ----------------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))

a0 = ax[0]
a0.plot(T[up], y[up], marker="o", color="C3", label="heat-up")
a0.plot(T[dn], y[dn], marker="s", color="C0", label="cool-down")
if base is not None:
    a0.plot(T, base, lw=1.0, ls=":", color="k", label="thermal baseline")
a0.set_xlabel("temperature [K]")
a0.set_ylabel("optical thickness -ln T")
a0.set_title("hysteresis loop, region = " + REGION)
a0.grid(alpha=0.3)
a0.legend(fontsize=8)

a1 = ax[1]
a1.plot(pair_T, gap, marker="o", color="k")
a1.axhline(floor, color="r", lw=0.8, ls="--", label="can drift floor")
a1.axvline(ONSET_LIT, color="C2", lw=0.8, ls=":", label="lit. onset")
a1.set_xlabel("temperature [K]")
a1.set_ylabel("up - down  [-ln T]")
a1.set_title("irreversible gap vs temperature")
a1.grid(alpha=0.3)
a1.legend(fontsize=8)

a2 = ax[2]
for n in ["end L", "centre", "end R"]:
    a2.plot(t, np.array(series[n]) / series[n][0], marker="o", label=n)
a2.plot(t, can / can[0], marker="s", ls="--", color="0.5", label="can")
a2.set_xlabel("elapsed time [min]")
a2.set_ylabel("Sigma*z normalised to frame 0")
a2.set_title("ends should fall before the centre")
a2.grid(alpha=0.3)
a2.legend(fontsize=8)

plt.tight_layout()
plt.show()
