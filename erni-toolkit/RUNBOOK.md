# ERNI Runbook — raw TOF stack to hydrogen map

Operational procedure for the work machine. Every step states what you run,
what a good result looks like, and what it means when it goes wrong.

**The governing rule:** every failure mode in this pipeline is silent. Nothing
crashes — you get a converged fit with a plausible number that is wrong. The
checks below are not ceremony; they are the only thing standing between you and
a confident wrong answer.

---

## Step 0 — Install and verify

```bash
git clone <your-fork>/erni-toolkit.git ~/erni-toolkit
cd ~/erni-toolkit
bash bootstrap_macos.sh
```

This clones the four upstream repos at pinned commits, installs pinned
dependencies, installs `nbragg` and `save_roi` **from source** (they are not on
PyPI at these versions), and runs `verify_install.py`.

**Good result:** `PASS 14  SKIP 0  FAIL 0` and `Stack verified.`

**Do not continue past a FAIL.** Re-run with `-v` for tracebacks.

| Failure | Meaning |
|---|---|
| `process KILLED (out of memory?)` | Machine is out of RAM. NCrystal does its work in C++ and gets SIGKILL'd. Close things and re-run. |
| `numpy 2.x -- must be 1.x` | numpy 2 breaks pandas in this stack. `pip install 'numpy<2'`. |
| `roifile ... is too new` | roifile ≥2025 changed the ROI record layout; save_roi returns **empty ROIs with no error**. Pin to 2024.9.15. |
| `nbragg install failed` | You are on branch `main`. nbragg's default branch is **`master`**. |

Set these in `~/.zshrc` (the bootstrap prints the exact lines):

```bash
source ~/erni-env/bin/activate                    # or the --user PATH line
export NCRYSTAL_ONLINEDB_CACHEDIR="$HOME/erni/.ncrystal_cache"
```

---

## Step 1 — Inspect the stack before touching it

```bash
python3 ~/erni/tools/inspect_stack.py ~/erni/data/YOUR_STACK.tiff 10 9.014
#                                      <file>                    <tstep_us> <L_m>
```

Three gates, in order. **All three must pass before you extract anything.**

### Gate 1 — how many bins actually contain neutrons

```
EMPTY bins            : 254
usable bin range      : 159 .. 510
```

Empty bins become `counts=0, err=0`, then nbragg computes `0/0` → NaN. nbragg's
default is `dropna=False`, so those NaNs flow into the fit silently. Either trim
to the usable range or pass `dropna=True` later. Note the range — you will need it.

### Gate 2 — does your wavelength range contain your Bragg edges

```
lambda[A] = 3956 * (bin * tstep) / L
```

The script prints reachability directly:

```
  delta-ZrH (111) 5.52 A  reachable? YES, near bin 1258
  calib-free band 5.70 A  reachable? YES, near bin 1299
```

For HIPPO at L = 9.014 m with 10 µs bins, the SOW's **2,500 radiographs** reach
10.97 Å, putting the first ZrH edge around bin 1258 — mid-stack, with room past
the texture-blind threshold. **If your stack does not reach ~1,300 bins you have
no Bragg edge and no calibration-free window**, and only whole-curve fitting is
available to you.

> The calibration-free threshold is material-specific: it begins past the
> *longest* Bragg edge present. δ-ZrH₂ (a = 4.78 Å) → 5.52 Å. δ-YH₂
> (a = 5.203 Å) → **6.01 Å**. For yttrium the window opens later than for
> zirconium.

### Gate 3 — where the sample and the open beam are

The ASCII preview shows the layout:

```
    %%%%%%%%%%%%
    %%%%%###%%%%
    %%%%#++*%%%%      dark pellet centred,
    %%%%=  :%%%%      bright open beam around it
```

This matches the SOW's Figure 1: **the open beam is a region of the same
radiograph**, not a separate exposure. You do not need a second file.

---

## Step 2 — Define ROIs

Minimum set, following the SOW's own figure:

| ROI name | What it is | Used for |
|---|---|---|
| `open_beam` | beam beside the sample | I₀ — **required** |
| `pellet_center` | thickest path | the measurement |
| `pellet_rim` | thin path | thickness/concentration separation |
| `al_can` | container wall | background characterisation |
| `silica_spacer` | spacer | a known, hydrogen-free reference |

Draw them in ImageJ/Fiji on the summed image and save as `rois.zip`, or generate
programmatically:

```bash
python3 ~/erni/tools/roi_tool.py --help
```

**Trap:** avoid the specimen edge. Buitrago observed transmission **above 1**
near Zr–air interfaces from total reflection, and his instruction is explicit —
the edge region must be ignored. A rim ROI that touches the boundary will give
you `T > 1`, which is physically impossible and will poison the fit.

For a 2D map, use a grid instead of named ROIs. save_roi's grid naming
(`grid_8x8_x0_y104.csv`) is parsed by nbragg with no translation — verified.

---

## Step 3 — Extract spectra

```python
from save_roi import extract_roi_spectra
extract_roi_spectra(tiff_path="data/YOUR_STACK.tiff",
                    roi_path="rois.zip",
                    output_dir="work/spectra/")
```

**Good result:** one CSV per ROI, columns `stack, counts, err`, row count equal
to your TOF bin count.

**Check:** open `open_beam.csv`. Counts must be substantially higher than
`pellet_center.csv` at every bin. If not, your ROIs are swapped or the open-beam
ROI landed on the sample.

For cylindrical pellets, straighten first:

```python
extract_roi_spectra(..., tilt_roi_name="symmetry_line")
```

---

## Step 4 — Build transmission, and check it

```python
import nbragg
d = nbragg.Data.from_counts(signal="work/spectra/pellet_center.csv",
                            openbeam="work/spectra/open_beam.csv",
                            L=9.014, tstep=10e-6, dropna=True)
t = d.table          # columns: wavelength, trans, err
```

**Three checks, all mandatory:**

1. **`t.trans` must lie strictly in (0, 1).** Values > 1 mean edge/reflection
   contamination (Step 2 trap) or a wrong open beam. Values ≤ 0 mean empty bins
   survived Gate 1.
2. **The wavelength range must match Gate 2.** If `t.wavelength.max()` differs
   from what `inspect_stack.py` predicted, your `tstep` or `L` is wrong.
3. **The Bragg edge must appear where predicted.** Plot `trans` vs `wavelength`
   and find the step. For δ-ZrH it belongs at 5.52 Å.

**If the edge is offset:** this is the 1-indexed-bin problem. `save_roi` writes
`stack = z+1` and nbragg multiplies it straight by `tstep`, so your time origin
is set by a counting convention. **Fit `t0` and `L0`; do not pin `t0` to the
published 0.10 µs** — that value describes moderator emission, not your bin
numbering. A one-bin error is ≈0.004 Å, ten times the precision you need.

---

## Step 5 — Build the material (the actual blocker)

**NCrystal ships no ZrH₂, no ZrH, no YH₂.** nbragg cannot fit what it cannot
load. This step does not need your data and can be done at any time — do it
first.

### 5a. Skeleton (structure only, minutes)

```bash
python3 ~/erni/tools/make_ncmat.py --skeletons --outdir ~/erni/materials
```

Verifies the structure with spglib and predicts the first edge:

```
wrote materials/delta-ZrH2_SKELETON.ncmat
   predicted first Bragg edge 2*d(111) = 5.5195 A     <- matches Buitrago's 5.52
```

Good for checking edge **positions** and smoke-testing the pipeline.
**Not valid for fitting hydrogen** — the H dynamics are a Debye placeholder, so
the incoherent/inelastic cross section that carries the hydrogen signal is wrong.

### 5b. Real material (the work)

Two ingredients:

- **Structure** → `NCMATComposer.from_cif`, pulling δ-ZrH₂ from COD or Materials
  Project. See `ncrystal2_advanced_02`. Needs `gemmi` (installed).
- **Hydrogen VDOS** → Mehta's AIMD phonon DOS (published for δ-ZrH₁.₄ through
  ₁.₇ and ε-ZrH₂), or INS: Couch 1971 (δ), Evans 1996 (ε). See
  `ncrystal2_advanced_03`.

```bash
python3 ~/erni/tools/make_ncmat.py --material delta-ZrH2 \
    --vdos-metal Zr_dos.csv --vdos-h H_dos.csv --outdir ~/erni/materials
```

**Trap:** the H energy grid must extend past ~160 meV. The optical peak sits at
140–145 meV; a grid that stops short truncates the exact feature that makes
hydrogen visible. The tool warns you.

**Trap:** `@ATOMPOSITIONS` needs every atom in the conventional cell, not the
asymmetric unit. Give only the asymmetric unit and spglib reports the wrong
space group and `.write()` refuses the file. (This is a feature — let it catch you.)

### 5c. You need more than one phase

ε→δ moves the cross section more than composition does *within* a phase
(Mehta). Torres's pellets are ε; the reactor-relevant phase is δ; a heat-treated
pellet may be both. Build **δ-ZrH₂ and ε-ZrH₂**; α-Zr ships free as
`Zr_sg194.ncmat`. nbragg fits phase fractions natively:

```
phases<0.7*delta-ZrH2.ncmat & 0.3*eps-ZrH2.ncmat>
```

---

## Step 6 — Validate the cross section before fitting anything real

Non-negotiable. Compare your composed σ(λ) against measured total cross
sections: **Whittemore 1964** (EXFOR 14174/002,003) and **Schmidt 1967**
(EXFOR 23424) — both already present in the TSL_School TRIGA notebook. Mehta
validated his ε-ZrH₂ TSLs against exactly these (his Fig. 5).

`TSL_School/openmc/Examples/Transmission` is the reference implementation for
recovering Σ_tot = −ln(T)/dx. Use it as a bench, not a pipeline stage — nothing
flows from it into the analysis. (It needs `openmc`, which the bootstrap does
not install.)

**If your σ(λ) disagrees with EXFOR, stop.** Every downstream number inherits
the error.

---

## Step 7 — Fit one spectrum

Start with a single ROI, not the map. Get one right before scaling.

```python
xs    = nbragg.CrossSection({"delta": {"mat": "materials/delta-ZrH2.ncmat"}})
model = nbragg.TransmissionModel(xs, vary_tof=True)   # let t0/L0 float (Step 4)
res   = model.fit(d)
print(res.fit_report())
```

**Judge it by:**

- reduced χ² near 1 — much greater means the model is wrong, much less means
  errors are overestimated
- residuals structureless around the Bragg edge — structure there means texture
  or extinction, not hydrogen
- fitted thickness consistent with the physical pellet — if the fit needs an
  impossible thickness it is absorbing something else

**Optical depth warning.** At Σ ≈ 4 cm⁻¹ through a ~1 cm pellet, T ≈ 2%. Beam
hardening, multiple scattering, and sample-induced background all worsen
together at that depth. If residuals are systematically curved, suspect
background before you suspect the material.

---

## Step 8 — Fix texture from the diffraction, then refit

**Do not skip this.** It is the step with no automated path, which is exactly
why it gets skipped.

1. Rietveld-refine the simultaneous HIPPO diffraction (GSAS + `gsaslanguage`).
2. Extract the ODF (MAUD → MTEX).
3. Translate orientation components into the CrossSection dict and **fix** them:

```python
xs = nbragg.CrossSection({
    "c1": {"mat": "delta-ZrH2.ncmat", "mos": 0.5, "dir1": (1,0,0), "dir2": (0,1,0), "weight": 0.4},
    "c2": {"mat": "delta-ZrH2.ncmat", "mos": 0.5, "dir1": (1,1,0), "dir2": (0,0,1), "weight": 0.6},
})
```

Hirsh needed 13 components on steel and hit NCrystal's mosaicity ceiling on
uranium. This is not a small correction.

**Why it matters:** Buitrago measured the *same* 130 wt ppm specimen along two
perpendicular directions and got visibly different attenuation across 2–5.5 Å.
Texture shifts the intercept Σ₀ without touching the slope dΣ/dH — a clean bias
that reads as hydrogen. Fit without fixing it and it lands in your H parameter.

**Escape hatch:** if you have no ODF, restrict the fit to λ beyond the last
Bragg edge (>5.7 Å for ZrH, >6.01 Å for YH₂). Coherent elastic is identically
zero there, so texture cannot act. You lose flux — Buitrago's counting times
rose more than tenfold — but you gain a calibration-free, texture-blind number.

---

## Step 9 — Scale to a map

```python
data = nbragg.Data.from_grouped(signal="work/spectra/grid_*_x*_y*.csv",
                                openbeam="work/spectra/open_beam.csv",
                                L=9.014, tstep=10e-6, dropna=True)
results = model.fit(data)     # per-group lmfit results keyed by (x, y)
```

Apply the **cylindrical symmetry constraint** (SOW milestone #2): a central ray
passes through more material than a rim ray, and you know the pellet diameter.
This is what breaks the thickness × concentration degeneracy — without it,
a thin H-rich region and a thick H-poor one are indistinguishable, because
Beer–Lambert only ever sees the product Σ·z.

Group pixels (2×2, 32×1) to buy statistics. Log what you dropped.

---

## Step 10 — The success test

Integrate the map to a per-pellet H/Zr. Compare against H/Zr from the lattice
parameters measured **in the same run** by diffraction.

> "If results for overall hydrogen concentration from ERNI and diffraction agree
> within error bars, the project was successful." — the SOW, verbatim.

Then estimate achieved spatial and concentration resolution for the count time
used (milestone #4).

**Calibrate your expectations.** Buitrago's headline 5 wt ppm does **not**
transfer. 17,900 wt ppm ≡ fully dense δ-ZrH₁.₆₇, so resolving ΔH/Zr ≈ 0.1 needs
only ~1,100 wt ppm — about 200× coarser than he demonstrated. Sensitivity is not
your problem. Texture, thickness, extinction and background are.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `T > 1` somewhere | Total reflection at Zr–air interface | Exclude the edge region (Step 2) |
| NaNs through the spectrum | Empty TOF bins, `dropna=False` | Trim to usable range or `dropna=True` |
| Bragg edge at the wrong λ | 1-indexed bin vs time origin | `vary_tof=True`; never pin `t0` |
| Edge present but too shallow | Texture, or extinction | Fix the ODF (Step 8), or fit above the last edge |
| Fit converges, χ² fine, H implausible | Texture absorbed into H | You skipped Step 8 |
| Curved residuals at high attenuation | Background / beam hardening | Model background per-pixel from observed attenuation |
| `process KILLED` | Out of RAM | Free memory; NCrystal dies in C++, uncatchable |
| ROIs load but are empty | `roifile` ≥ 2025 | Pin `roifile==2024.9.15` |
| Yttrium: lattice parameter says nothing | Real — a is 0.5200–0.5207 nm across 1.50<H/Y<2.00 | Use phase fraction (f_δ[%] = 53C − 1.05) and edge-height ratios |

---

## What is not automated

Be explicit with yourself about these, because nothing will warn you:

- **ODF → nbragg orientation components** (Step 8) — manual transfer, no code path
- **VDOS → `.ncmat`** (Step 5b) — you must source and format the DOS yourself
- **EXFOR validation** (Step 6) — you must do the comparison and judge it
- **Background model** (Step 7) — the SOW names this the principal risk and
  there is no published recipe
