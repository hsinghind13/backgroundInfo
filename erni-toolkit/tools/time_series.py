# time_series.py -- optical thickness vs time/temperature, per region.
#
#   %run -i time_series.py
#
# One TIFF stack per time point. Same ROIs, same wavelength band, same open
# beam for every frame, so anything that moves is the sample or the beam.
#
# FILL IN FRAMES BEFORE RUNNING. Nothing here is measured; it is all Thor's
# to supply -- run numbers, setpoints, elapsed time, exposure.

import numpy as np
import matplotlib.pyplot as plt
import tifffile

CHAN = slice(100, 300)         # wavelength band, same for every frame

# path, label, T setpoint [K], elapsed [min], proton charge [arb]
# T = None  -> unknown.  CHARGE = None -> not normalised, see WARNING below.
FRAMES = [
    ("runs/xxxxxx.tif", "RT before", 293.0, 0.0, None),
    ("runs/xxxxxx.tif", "ramp 1", 473.0, 30.0, None),
    ("runs/xxxxxx.tif", "hold", 673.0, 60.0, None),
    ("runs/xxxxxx.tif", "ramp down", 473.0, 90.0, None),
    ("runs/xxxxxx.tif", "RT after", 293.0, 120.0, None),
]
OPEN = "runs/111711.tif"

# ROIs -- axial ENDS, not dome edges. At the axial ends the chord is still
# full; at the top/bottom of the dome it goes to zero and the chord correction
# is worst exactly where you want the answer.
ROIS = {
    "end L":  np.s_[380:420, 200:240],
    "centre": np.s_[380:420, 255:295],
    "end R":  np.s_[380:420, 310:350],
    "can":    np.s_[380:420,  60:130],   # composition cannot change -> drift monitor
    "open":   np.s_[ 20: 60,  20: 60],   # unobstructed corner -> flux monitor
}
PELLET = np.s_[300:500, 200:350]         # whole projection, for the integral

# ---------------------------------------------------------------------------
def load_ot(path, den):
    with tifffile.TiffFile(path) as tf:
        arr = tf.series[0].asarray(out="memmap")
        num = np.asarray(arr[CHAN], dtype=np.float64).sum(axis=0)
    T = no_nan_divide(num, den)
    T = np.where(T > 0, T, np.nan)
    return -np.log(T)

with tifffile.TiffFile(OPEN) as tf:
    arr = tf.series[0].asarray(out="memmap")
    den = np.asarray(arr[CHAN], dtype=np.float64).sum(axis=0)

names = list(ROIS.keys())
series = {}
for n in names:
    series[n] = []
integral = []
times = []
temps = []
labels = []

for path, lab, T, t, q in FRAMES:
    OT = load_ot(path, den)
    if q is not None:
        OT = OT + np.log(q / FRAMES[0][4])   # exposure ratio -> additive in -ln T
    for n in names:
        series[n].append(float(np.nanmean(OT[ROIS[n]])))
    integral.append(float(np.nansum(OT[PELLET])))
    times.append(t)
    temps.append(T)
    labels.append(lab)

times = np.array(times)
integral = np.array(integral)

# ---------------------------------------------------------------------------
print("frame            T[K]   t[min]   end L   centre   end R    can    open")
for i, lab in enumerate(labels):
    print(lab.ljust(15),
          str(temps[i]).rjust(6), str(times[i]).rjust(7),
          round(series["end L"][i], 4), round(series["centre"][i], 4),
          round(series["end R"][i], 4), round(series["can"][i], 4),
          round(series["open"][i], 4))

can = np.array(series["can"])
opn = np.array(series["open"])
print()
print("DRIFT CONTROL")
print("  can drift over the run  :", round(float(can.max() - can.min()), 4))
print("  open drift over the run :", round(float(opn.max() - opn.min()), 4))
print("  -> any sample change smaller than these is instrumental")

print()
print("MASS-CONSERVING OBSERVABLE  (sum of Sigma*z over the whole projection)")
print("  first frame :", round(float(integral[0]), 1))
print("  last frame  :", round(float(integral[-1]), 1))
print("  change      :", round(float(100 * (integral[-1] - integral[0]) / integral[0]), 2), "%")
print("  -> thermal expansion redistributes but conserves this; only material")
print("     actually leaving the beam path changes it")

print()
print("HYSTERESIS ANCHOR  (compare frames at the SAME temperature)")
print("  expansion is reversible, hydrogen loss is not")
print("  RT before :", round(series["centre"][0], 4))
print("  RT after  :", round(series["centre"][-1], 4))
d = series["centre"][-1] - series["centre"][0]
print("  difference:", round(float(d), 4), " = ",
      round(float(100 * d / series["centre"][0]), 2), "%")
print("  -> dH/H approx", round(float(1.4 * 100 * d / series["centre"][0]), 2), "%")

# ---------------------------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))

a0 = ax[0]
a0.plot(times, series["end L"], marker="o", label="end L")
a0.plot(times, series["centre"], marker="o", label="centre")
a0.plot(times, series["end R"], marker="o", label="end R")
a0.plot(times, series["can"], marker="s", ls="--", color="0.5", label="can (control)")
a0.set_xlabel("elapsed time [min]")
a0.set_ylabel("optical thickness -ln T")
a0.set_title("Sigma*z vs time")
a0.grid(alpha=0.3)
a0.legend(fontsize=8)

a1 = ax[1]
a1.plot(temps, series["centre"], marker="o", label="centre")
a1.plot(temps, series["end L"], marker="o", label="end L")
a1.set_xlabel("temperature [K]")
a1.set_ylabel("optical thickness -ln T")
a1.set_title("heat-up vs cool-down: gap = irreversible loss")
a1.grid(alpha=0.3)
a1.legend(fontsize=8)

edge = 0.5 * np.array(series["end L"]) + 0.5 * np.array(series["end R"])
ctr = np.array(series["centre"])
a2 = ax[2]
a2.plot(times, edge / ctr, marker="o", color="k")
a2.axhline(1.0, color="r", lw=0.8, ls="--")
a2.set_xlabel("elapsed time [min]")
a2.set_ylabel("edge / centre")
a2.set_title("diffusion signature: ends deplete first")
a2.grid(alpha=0.3)

plt.tight_layout()
plt.show()
