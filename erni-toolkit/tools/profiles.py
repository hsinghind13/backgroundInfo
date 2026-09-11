# profiles.py -- row and column optical-thickness profiles, side by side.
# %run -i profiles.py   (needs vol_sample, vol_open_lr, no_nan_divide in the namespace)
# Written with no line continuations and no indented blocks: paste-safe.

import numpy as np
import matplotlib.pyplot as plt

CHAN = slice(100, 300)   # short-wavelength band, where the counts are
COLS = slice(150, 400)   # column band inside the pellet -> used for the ROW profile
ROWS = slice(300, 390)   # row band inside the pellet    -> used for the COLUMN profile

num_r = vol_sample[CHAN, :, COLS].sum(axis=0)
den_r = vol_open_lr[CHAN, :, COLS].sum(axis=0)
T_r = no_nan_divide(num_r, den_r)
ot_rows = -np.log(np.where(T_r > 0, T_r, np.nan))
prof_row = np.nanmean(ot_rows, axis=1)

num_c = vol_sample[CHAN, ROWS, :].sum(axis=0)
den_c = vol_open_lr[CHAN, ROWS, :].sum(axis=0)
T_c = no_nan_divide(num_c, den_c)
ot_cols = -np.log(np.where(T_c > 0, T_c, np.nan))
prof_col = np.nanmean(ot_cols, axis=0)

fig, ax = plt.subplots(1, 2, figsize=(13, 4.5), sharey=True)

ax[0].plot(prof_row, lw=1.2, color="k")
ax[0].axvspan(ROWS.start, ROWS.stop, color="0.85", zorder=0, label="ROWS used for col profile")
ax[0].axvspan(300, 330, alpha=0.20, label="band A 300-330")
ax[0].axvspan(330, 360, alpha=0.20, label="band B 330-360")
ax[0].axvspan(360, 390, alpha=0.20, label="band C 360-390")
ax[0].set_xlabel("row  (vertical, across the diameter)")
ax[0].set_ylabel("optical thickness  -ln T")
ax[0].set_title("Row profile: chord varies, dome is geometry")
ax[0].grid(alpha=0.3)
ax[0].legend(fontsize=7, ncol=2)

ax[1].plot(prof_col, lw=1.2, color="k")
ax[1].axvspan(COLS.start, COLS.stop, color="0.85", zorder=0, label="COLS used for row profile")
ax[1].axvspan(150, 250, alpha=0.20, label="col A 150-250")
ax[1].axvspan(250, 350, alpha=0.20, label="col B 250-350")
ax[1].axvspan(350, 400, alpha=0.20, label="col C 350-400")
ax[1].set_xlabel("column  (along the cylinder axis)")
ax[1].set_title("Column profile: chord constant, structure is composition")
ax[1].grid(alpha=0.3)
ax[1].legend(fontsize=7, ncol=2)

plt.tight_layout()
plt.show()

flat = prof_col[COLS]
print("column profile inside", COLS.start, "-", COLS.stop)
print("  mean", round(float(np.nanmean(flat)), 4), " std", round(float(np.nanstd(flat)), 4), " rms%", round(100 * float(np.nanstd(flat)) / float(np.nanmean(flat)), 1))
print("row bands (expect spread: chord)")
print("  A 300-330 mean", round(float(np.nanmean(prof_row[300:330])), 4))
print("  B 330-360 mean", round(float(np.nanmean(prof_row[330:360])), 4))
print("  C 360-390 mean", round(float(np.nanmean(prof_row[360:390])), 4))
