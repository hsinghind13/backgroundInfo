# erni-toolkit

Everything needed to run the ERNI hydrogen-mapping pipeline on a machine that
has the real data but no Claude.

## Quick start

```bash
git clone <your-fork>/erni-toolkit.git ~/erni-toolkit
cd ~/erni-toolkit
bash bootstrap_macos.sh          # installs everything, then self-tests
```

Then follow **[RUNBOOK.md](RUNBOOK.md)** from step 1.

## What is here

| Path | What it does |
|---|---|
| `bootstrap_macos.sh` | Clones the 4 upstream repos at pinned commits, installs pinned deps, installs `nbragg`/`save_roi` from source, runs the self-test. Writes only inside `$HOME`. |
| `verify_install.py` | 14 checks proving the stack works, on demo data that ships in the repos. Never touches your measurement files. |
| `requirements.lock.txt` | Exact pinned versions. The comments are load-bearing — read before floating anything. |
| `RUNBOOK.md` | Step-by-step: raw TOF stack → hydrogen map, with the traps and the sanity checks. |
| `tools/inspect_stack.py` | Step 1. Gates a new TIFF: usable bins, wavelength coverage, sample/beam layout. |
| `tools/make_ncmat.py` | Builds the δ-ZrH₂ / δ-YH₂ materials NCrystal does not ship. |
| `tools/roi_tool.py` | Programmatic ROI creation (the documented interactive selector never shipped). |
|  `tools/ratio` | 10 lines. Quick-look image: sum(thermal slices)/sum(short-lambda slices), the ImageJ Z-project + Image Calculator + B&C workflow. Display product, not a transmission -- do not fit it. |
| `materials/*_SKELETON.ncmat` | Structure-verified placeholders. Correct Bragg-edge **positions**, wrong H dynamics — not valid for fitting. |

## Two things that will bite you

**`nbragg` and `save_roi` are not installable from PyPI at these versions.** They
are installed from the git checkouts. `nbragg`'s default branch is **`master`**,
not `main`.

**NCrystal ships no ZrH₂, no ZrH, no YH₂.** They must be composed from a CIF plus
a real vibrational DOS before any fit can run. This is the critical path and it
does not depend on having data — see RUNBOOK step 5.

## Layout the bootstrap creates

```
~/erni/
  repos/        nbragg, save_roi, ncrystal-notebooks, TSL_School
  tools/        the scripts above
  materials/    .ncmat files
  data/         <- put your TOF stacks here
  work/         <- extracted spectra, fits, maps
```

## Verified state

Pinned to the stack confirmed working 2026-08-17:
NCrystal 4.4.6 · nbragg 1.0.0 (`ecaf764`) · save-roi 0.2.0 (`abf97d4`) ·
numpy 1.26.4 · pandas 2.2.2 · lmfit 1.3.4 · roifile 2024.9.15 · gemmi 0.7.5
