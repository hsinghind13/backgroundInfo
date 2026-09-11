# YH₂ Campaign Handoff

**11 Sep 2026 — personal Mac → work machine.**
Run 111859 (ZrH₂ in Al) was the practice problem. The YH₂ in-situ heating campaign is the
real one, and it is far better suited to the goal: showing hydrogen move as temperature changes.

Web version, same content: https://claude.ai/code/artifact/3c183ec2-2d13-4669-91ea-802f7c1053a5

---

## The dataset

**YH₂ pellet M080924J in a TZM can**, heated in-situ while imaging on HIPPO FP4.
1,682 runs, 7 Nov – 4 Dec 2025.

| | |
|---|---|
| stacks | `/Users/hsin/Desktop/hippo/M080924J/tiffs` |
| filename | `<run>_t1e-05_T2400_p1e-07_P100.tiff.gz` |
| thermal open beam | `openbeam_furnace_sum_smoothed_t1e-05_T2400_p1e-07_P100.tif` |
| epithermal open beam | `openbeam_furnace_sum_smoothed_t2.5e-07_T3800_p1e-07_P100.tiff` |
| TIFFs present | 110005 – 111569, with many gaps |
| can | TZM — OD 10.2 mm, ID 8.2 mm, wall 1.0 mm |
| pellet | ≤ 8.2 mm (bounded by the bore) |
| run log | `titles.doc` — run, times, title, **proton charge**, pulses |

### Campaign structure

| phase | runs | N | live | when |
|---|---|---|---|---|
| tomography, 3 rotations | 107007–107009 | 3 | 3 | Nov 7 |
| **RT before** | 110006–110017 | 12 | 12 | Nov 28, 12:29–14:08 |
| heat ramp #1 (beam down) | 110018–110107 | 90 | 33 | Nov 28, 14:13–15:44 |
| cool | 110110–110123 | 14 | 14 | Nov 28, 18:35–20:42 |
| **heat ramp #2** (clean) | 110124–110213 | 90 | 90 | Nov 28, 20:50–22:21 |
| **hold at 950 °C** | 110214–111053 | 840 | 761 | 27 hours |
| cool | 111054–111396 | 343 | 172 | Nov 30, 01:35–07:49 |
| slow cool | 111398–111531 | 134 | 126 | Nov 30, 10:06–21:14 |
| **RT after** | 111532–111683 | 152 | 34 | Nov 30 → Dec 4 |

**435 of 1,682 runs have zero proton charge.** Beam outages scattered throughout.
Always filter on charge > 0 before averaging anything. Heat ramp #1 is mostly dead
(33/90) — use ramp #2, which is 90/90. The long RT-after sequence is mostly dead too.

**The sample was heated to ~950 °C twice before the hold** — ramp #1, a cool, then ramp #2.
Irrelevant for total loss across the campaign; it matters for a desorption *onset*, since
whatever left during ramp #1 is already gone by ramp #2.

---

## Start here — the measurement that needs no calibration

Difference two room-temperature states. Same temperature, same sample, same can, same
detector, so σ(T), Debye-Waller and thermal expansion cancel exactly.

| anchor | runs | N live | total charge |
|---|---|---|---|
| RT before | 110006–110008 | 3 | 6.6180e6 |
| RT after | 111546–111569 | 24 | 9.3166e6 |

Write out the optical thickness with charge normalisation and **the open beam cancels
algebraically**:

```
Δ(Σz) = ln[ (C_after / q_after) / (C_before / q_before) ]
```

No open beam, no `norm`, no flight path, no cross-section, no pellet diameter.
`CHAN` only has to select *the same bins in both stacks* — it need not correspond to a
known wavelength, because both share a detector and a binning. Positive means the sample
attenuates less than it did: hydrogen left.

Per pixel, that is the 2D hydrogen-loss map. Statistical error is
`sqrt(1/C_before + 1/C_after)`.

### The two controls are the whole validity argument

Compute Δ(Σz) in an **unobstructed field** ROI and in a **TZM-can-only** ROI. Both must sit
near zero — the first tests whether beam and detector held over six days, the second tests
it again in a material whose composition cannot have changed. Any offset they share is a
systematic that subtracts off the sample region. Without these two numbers the map is not
evidence.

### Then, in order

1. **The 27-hour hold** — 761 live frames at 950 °C. Desorption kinetics: how fast hydrogen
   leaves and whether it plateaus. The richest part of the dataset.
2. **Same-temperature pairing across the ramps** — heat-up vs cool-down at matched setpoints.
   The gap is hydrogen that did not come back; the lowest temperature where it clears the
   drift floor is the desorption onset. See `erni-toolkit/tools/branches.py`.
3. **The statistics ladder** — RT-before was taken as 20 min, 5 min, 1 min and 20 s
   exposures, three each. That is precision versus counting time, measured, which answers
   the resolution-per-count-time question directly.

---

## Calibration status — nothing numeric from 111859 carries over

Different detector position, different furnace, different can, different sample.
Method transfers; numbers do not.

| parameter | 111859 value | for YH₂ |
|---|---|---|
| flight path L | 8.95 m | unknown — re-derive |
| L0, t0 | 0.99746, 1e-07 | re-derive with L |
| CHAN band | bins 100–300 | bins map to different λ — pick from this data |
| norm | 0.3249 | use proton charge, per run |
| pixel size | 0.026 mm/px | derive from the can OD, 10.2 mm |
| can path | 0.20 cm Al | TZM, exact geometry (below) |
| α₀, β₀ | library defaults | **calibratable here** — see below |
| scatter fraction | 0.41% of beam | re-measure in-frame |

### The can path is exact geometry, not a fitted parameter

With Rₒ = 5.1 mm and Rᵢ = 4.1 mm, a ray at height y crosses

```
z_TZM(y) = 2 · [ sqrt(Ro² − y²) − sqrt(Ri² − y²) ]
```

2.0 mm on the axis, growing toward the rim, then a full outer chord where the ray misses
the bore entirely. Combined with the pellet chord that is the complete geometric model,
with nothing left to fit.

### The TZM can is a wavelength standard, present in every frame

TZM is ~99% molybdenum — bcc, a = 3.147 Å, lattice parameter known to five figures, first
Bragg edge at 4.45 Å. **L and t₀ fall out of the edge position; α₀ and β₀ fall out of its
shape.** That is exactly the calibration run Vogel's thesis prescribes (§3.3.3: gather during
a calibration run, hold constant afterwards), and it costs no beam time.

Statistics are excellent: summing the can-only region over the 27-hour hold gives ~1.7e9
proton charge, and Mo attenuates far more than the Al wall that made this impossible on
111859. **The "α and β can never be calibrated" conclusion was true for the ZrH₂ dataset and
is not true here.**

---

## Traps — each cost a full debugging cycle

**nbragg's default response is tied to your binning, not the instrument.**
`kind="jorgensen"` builds its kernel on a fixed 0.1 Å grid and applies it sample-wise via
`convolve1d`, so the physical width scales with your wavelength step. nbragg documents this
in the `jorgensen_inv` docstring. Use `jorgensen_inv` whenever α/β are meant to transfer.
α₀ = 3.67, β₀ = 3.06 are library defaults, never physical values.

**The polynomial background is unphysical — do not trust a fit that needs it.**
On 111859 it reached 2.6% at short λ and went *negative* past 5 Å, while correlating with
thickness at +0.956. It was absorbing a model error, not describing a background. The
configuration that fit *best* on χ² was the one to reject.

**With only measured inputs, the model stopped fitting.** One free parameter, scatter
subtracted, no background fudge: χ²ᵥ = 38, while R² still read 0.993 — invisible on a plot.
The shape of Σ(λ) is wrong. Last suspect standing is the cross-section file, never validated
against measurement. Expect the same on YH₂.

**NCrystal ships no ZrH₂, and probably no YHₓ.** Check with `NC.browseFiles()` early. If
absent it must be composed from a CIF plus a hydrogen VDOS — days of work, not hours. There
are starting points at `erni-toolkit/materials/delta-YH2_SKELETON.ncmat` and
`delta-ZrH2_SKELETON.ncmat`. `Mo_sg229` for the can most likely does ship. Note that
`ZrH1p6_bct.ncmat` is mislabelled — it is stoichiometric ZrH₂, ε phase.

**Differences cancel nearly everything; absolutes do not.** A wrong cross-section, a wrong
diameter, a wrong `norm` all move every fitted path in the same direction by roughly the same
factor. Subtract two and the error largely cancels. This is why the loss measurement is in
good shape while the absolute H/Y is not.

**Verify by executing.** Every real bug this stack produced was invisible to reading — a
background that fits beautifully and goes negative, a response whose parameters do not mean
what they say, a "flat profile" that was constant geometry rather than uniform hydrogen.

---

## Open asks

| ask | who | unblocks |
|---|---|---|
| **Pellet diameter, measured** — the bore bounds it at ≤ 8.2 mm, but the fit is not that | Kohnert | Converts path to H/Y, and pins the pixel size independently |
| **Do sample runs exist in the 250 ns binning?** | Vogel | An epithermal open beam exists, so someone intended resonance analysis. If sample runs match it, resonance Doppler gives sample temperature measured *in the same pixels* rather than a furnace setpoint. The 21 "with TPX" runs are the likely candidates |
| What is TPX, and were event files kept? | Vogel | If Timepix3, event mode can be re-binned to any TOF resolution after the fact |
| Diffraction on the same volume | Vogel | Independent H content for cross-checking. The lattice-parameter route may be insensitive for δ-YHₓ — *unverified, check before planning on it* |
| Proton charge for the summed open beams | DAQ | They are `sum_smoothed`, so their charge is unknown. Harmless for differences, blocking for absolute normalisation |

---

## Scripts

Under `erni-toolkit/tools/`. Most were written for 111859's geometry and flight path — copy
them for reference, not to run unchanged.

| file | does | status |
|---|---|---|
| `inspect_stack.py` | gates a new TOF stack: usable bins, λ coverage, layout | run this first on any YH₂ stack |
| `map2d.py` | 2D optical-thickness map, row/column marginals, chord fit | needs new ROIs and geometry |
| `profiles.py` | row and column optical-thickness profiles side by side | needs new ROIs |
| `can_subtract.py` | separates can from pellet; tests for instrumental tilt | switch Al → Mo |
| `time_series.py` | optical thickness vs time/temperature per region | **written for exactly this campaign, never run** |
| `branches.py` | heat-up vs cool-down pairing, hysteresis gap, onset | **written for exactly this campaign, never run** |
| `model_locked.py` | nbragg model with the instrument bolted down | re-derive every constant |
| `edge_visibility.py` | predicts Bragg-edge size and counts needed | rerun for Mo and YH₂ |
| `hydrogen_sensitivity.py` | NCrystal dΣ/dx per unit H content | header says NOT TESTED — check its sanity block |
| `multiregion.py`, `rowscan.py`, `jointfit.py` | multi-region fits, row scans, joint chord fit | 111859-specific |
| `roi_tool.py`, `make_ncmat.py`, `tif2png.py` | ROI selection, material composition, previews | general |

`braggIterations.py` at the repo root is Brendt Wohlberg's original analysis script — the
reference implementation, and the source of L = 8.95, norm ≈ 0.33 and the SVD open-beam trick.

---

## Not in this repo

Left on the personal Mac at `~/Desktop/LANL`: PDFs and papers, `repos/` (public clones of
nbragg / NCrystal / save_roi), `annotated/` (the annotated-notebooks deliverable), `Admin/`,
and the `.docx` reports and drafts. Add whichever of those you want — they were excluded for
size, licensing, or because they may be personal.
