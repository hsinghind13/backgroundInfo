# model_locked.py -- nbragg model with the instrument bolted down.
#
# BASIS for every fixed value, per CLAUDE.md's standing rule:
#
#  alpha0, beta0 : moderator emission-time distribution, Vogel thesis eq 3.52.
#                  "as the emission spectrum is assumed to be constant,
#                   parameters should be gathered during a calibration run and
#                   remain constant afterwards"  -- thesis section 3.3.3.
#                  Same moderator + flight path for every region and frame.
#  alpha1        : set to zero. Thesis: "For alpha, it is sufficient to vary
#                  only alpha0 and set alpha1 to zero."
#  L0, t0        : flight-path geometry. Hirsh et al. 2025: L = 9.014 +/- 0.001 m,
#                  t0 = 0.10 +/- 0.01 us. NOTE the conflict with L = 8.95 used
#                  here -- 0.7% in wavelength. Resolve before trusting lattice
#                  parameters; harmless for a smooth-curve thickness fit.
#  bg0..bg2      : instrument background, ~2.5% on HIPPO/FP4 (gamma rejection).
#                  A property of the shielding, not of the region.
#  norm          : exposure ratio. MUST come from proton charge, not from a fit
#                  to this same data. The 0.3187 currently in use is
#                  self-referential -- see ERNI-RESUME.
#  al weight     : from the can-only columns via can_subtract.py. Measured in
#                  pixels that never see the pellet, so external to this fit.
#  thickness     : the sample. The only thing left free.

import numpy as np
import nbragg

# ---------------------------------------------------------------------------
# CALIBRATION BLOCK -- fill from a calibration run, then never touch per region
# ---------------------------------------------------------------------------
CAL = {
    "alpha0": 3.67,      # PLACEHOLDER: nbragg default. Replace with a calibrated
    "beta0":  3.06,      # PLACEHOLDER: value. See CALIBRATE below.
    "L0":     0.99745607,
    "t0":     1e-07,
    "bg0":    2.6250e-04,
    "bg1":   -7.6070e-04,
    "bg2":    3.48700e-03,
}
AL_FRAC = 0.177          # PLACEHOLDER: replace with the can-only measurement
NORM = 0.3187            # PLACEHOLDER: replace with proton-charge ratio
TEMP = 293.15            # per frame in a ramp series
WLMIN, WLMAX = 0.02, 3.5 # RAISE THIS if inspect_stack shows counts past 4.68 A

CALIBRATE = False        # True  -> free the instrument on a calibration region
                         # False -> lock it and fit the sample

# ---------------------------------------------------------------------------
al = nbragg.CrossSection(al="nbragg/ncmat/Al_sg225.ncmat")
zrh = nbragg.CrossSection(zrh="nbragg/ncmat/ZrH1p6_bct.ncmat")
xs = AL_FRAC * al + (1.0 - AL_FRAC) * zrh

model = nbragg.TransmissionModel(
    xs,
    vary_background=CALIBRATE,
    vary_response=CALIBRATE,
    vary_weights=False,       # fixed from can geometry, not fitted
    vary_tof=CALIBRATE,
)

p = model.params
p["thickness"].set(value=1.2, min=0.5, max=4.0)
p["temp"].set(value=TEMP, vary=False)
p["norm"].set(value=NORM, vary=False)

if not CALIBRATE:
    for k in ["L0", "t0", "bg0", "bg1", "bg2"]:
        if k in p:
            p[k].set(value=CAL[k], vary=False)
    for name, key in [("α0", "alpha0"), ("β0", "beta0")]:
        if name in p:
            p[name].set(value=CAL[key], vary=False)
    for name in ["α1", "β1"]:
        if name in p:
            p[name].set(value=0.0, vary=False)

result = model.fit(data, wlmin=WLMIN, wlmax=WLMAX)
print(result.fit_report_text())

# ---------------------------------------------------------------------------
# What the locked fit should show if the restructure is right:
#   - variables drop from 8 to 1
#   - thickness error bar GROWS (the old 8.55% was borrowed from free
#     background and response soaking up real signal)
#   - reduced chi-square RISES (fewer knobs, same data) -- that is honest,
#     not worse. A redchi that stays at 4.75 with 1 variable means the old
#     7 were doing nothing.
#   - the 0.9996 thickness/p1 correlation is gone because p1 no longer exists
# ---------------------------------------------------------------------------
free = [k for k in result.params if result.params[k].vary]
print()
print("free parameters :", free)
print("count           :", len(free))
