# can_subtract.py -- separate the can from the pellet, and test whether any
# axial gradient is real or instrumental.
#
#   %run -i can_subtract.py
#
# Needs vol_sample, vol_open_lr, no_nan_divide in the namespace.
# Low bracket nesting on purpose: one call per line.
#
# GEOMETRY ASSUMED (Thor to confirm): cylinder axis horizontal = column
# direction, beam across the diameter. Along a row you cross:
#   open beam | can wall x2 | can wall x2 + pellet chord | can wall x2 | open beam
# So the can-only columns give the wall term to subtract, AND a stretch of the
# frame where the answer is known to be constant.

import numpy as np
import matplotlib.pyplot as plt

CHAN = slice(100, 300)      # wavelength band
ROWS = slice(380, 420)      # dome peak, matches map2d.py

CAN_L = slice(60, 130)      # GUESS -- can wall only, left of the pellet
SAMP  = slice(200, 350)     # GUESS -- pellet
CAN_R = slice(420, 480)     # GUESS -- can wall only, right of the pellet

# ---- optical thickness, whole frame ---------------------------------------
num = vol_sample[CHAN].sum(axis=0)
den = vol_open_lr[CHAN].sum(axis=0)
T = no_nan_divide(num, den)
T = np.where(T > 0, T, np.nan)
OT = -np.log(T)

cols = np.arange(OT.shape[1])
rows = np.arange(OT.shape[0])
band = OT[ROWS, :]
col_prof = np.nanmean(band, axis=0)

# ---- levels ----------------------------------------------------------------
can_l = np.nanmean(col_prof[CAN_L])
can_r = np.nanmean(col_prof[CAN_R])
samp = np.nanmean(col_prof[SAMP])
can_mean = 0.5 * can_l + 0.5 * can_r

print("optical thickness at the dome-peak row band")
print("  can only, left  :", round(float(can_l), 4))
print("  can only, right :", round(float(can_r), 4))
print("  can + pellet    :", round(float(samp), 4))
print("  pellet alone    :", round(float(samp - can_mean), 4))
print("  can as % of raw :", round(float(100 * can_mean / samp), 1))

# ---- TEST 1: is the can level the same on both sides? ----------------------
# It must be. The wall is the same wall. A difference is an instrumental
# gradient -- beam profile, open-beam mismatch, detector gain -- and the SAME
# gradient sits under the pellet, faking a hydrogen loss signal.
can_tilt = can_r - can_l
print()
print("TEST 1  can left vs right :", round(float(can_tilt), 4))
print("        as % of pellet-only path :",
      round(float(100 * can_tilt / (samp - can_mean)), 1))
print("        -> this is the floor on any axial gradient you can claim")

# ---- TEST 2: is the can region actually pellet-free? -----------------------
# If it is, its row profile is flat. If it domes, those columns still see the
# pellet and CAN_L / CAN_R are wrong.
row_can = np.nanmean(OT[:, CAN_L], axis=1)
row_samp = np.nanmean(OT[:, SAMP], axis=1)
inner = slice(300, 500)
dome_can = np.nanmax(row_can[inner]) - np.nanmin(row_can[inner])
dome_samp = np.nanmax(row_samp[inner]) - np.nanmin(row_samp[inner])
print()
print("TEST 2  vertical swing, can columns    :", round(float(dome_can), 4))
print("        vertical swing, pellet columns :", round(float(dome_samp), 4))
print("        ratio :", round(float(dome_can / dome_samp), 3), " -- want << 1")

# ---- gradient across the pellet, with the can trend removed ----------------
anchor_x = [float(np.mean(cols[CAN_L])), float(np.mean(cols[CAN_R]))]
anchor_y = [float(can_l), float(can_r)]
trend = np.interp(cols, anchor_x, anchor_y)
pellet_prof = col_prof - trend

good = np.isfinite(pellet_prof[SAMP])
xs = cols[SAMP][good]
ys = pellet_prof[SAMP][good]
slope = np.polyfit(xs, ys, 1)[0]
span = slope * (SAMP.stop - SAMP.start)
level = float(np.nanmean(ys))
print()
print("pellet-only axial gradient across the sample :", round(float(span), 4))
print("  as % of the pellet path :", round(float(100 * span / level), 1))
print("  -> dH/H approx", round(float(1.4 * 100 * span / level), 1), "%  "
      "(1.4 = 1 / 0.72, from hydrogen_sensitivity.py -- RERUN IT, untested)")

# ---- plots -----------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))

a0 = ax[0]
a0.plot(cols, col_prof, lw=1.0, color="k")
a0.plot(cols, trend, lw=1.0, color="r", ls="--")
a0.axvspan(CAN_L.start, CAN_L.stop, alpha=0.2, color="C0")
a0.axvspan(SAMP.start, SAMP.stop, alpha=0.2, color="C1")
a0.axvspan(CAN_R.start, CAN_R.stop, alpha=0.2, color="C0")
a0.set_xlabel("column -- along the cylinder axis")
a0.set_ylabel("optical thickness -ln T")
a0.set_title("blue = can only, orange = can + pellet, red = can trend")
a0.grid(alpha=0.3)

a1 = ax[1]
a1.plot(rows, row_can, lw=1.0, color="C0", label="can columns")
a1.plot(rows, row_samp, lw=1.0, color="C1", label="pellet columns")
a1.set_xlabel("row -- vertical")
a1.set_ylabel("optical thickness -ln T")
a1.set_title("TEST 2: can columns should be flat")
a1.grid(alpha=0.3)
a1.legend(fontsize=8)

plt.tight_layout()
plt.show()
