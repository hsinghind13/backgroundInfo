# ERNI run 111859 — resume point

Last worked **2026-08-23**. Analysis lives on the **work machine** at `~/Desktop/hippo`;
this file and `erni-toolkit/tools/` are the persistent copy on the personal Mac.

---

## Where we are in one line

We can measure the ZrH₂-equivalent neutron path through the pellet to ~5%.
We cannot yet convert that to H/Zr, because two of the three inputs are unmeasured.

---

## The data

| | |
|---|---|
| sample | `111859_t1e-05_T2400_p1e-07_P100.npz` |
| open beam | `111711_t1e-05_T2400_p1e-07_P100.npz` |
| geometry | 2400 TOF bins × 10 µs, 512×512, 32-bit **integer counts** (Poisson valid) |
| flight path | **L = 8.95 m** (from the author's wavelength constant, not 9.014) |
| location | work machine, `~/Desktop/hippo/nbragg/runs/{openbeam,onsample}/` |

Materials at `~/Desktop/hippo/nbragg/ncmat/` — `Al_sg225.ncmat`, `ZrH1p6_bct.ncmat`.

---

## Established

**The pellet is a cylinder lying axis-horizontal, beam across the diameter.**
Horizontal profile flat (constant chord along the axis); vertical profile a **dome**
(chord = 2√(R²−y²)). An earlier flat horizontal profile had been misread as uniform
hydrogen — it only showed constant geometry.

**Row-to-row comparisons need a chord correction.** Three regions from the original
script gave a 53% spread in ZrH path, entirely from sitting at different dome heights.
Column-direction variation is where hydrogen shows cleanly.

**Measured:** ZrH₂-equivalent path at the centre line, **P_peak ≈ 0.98 ± 0.05 cm**.

**Fit quality:** with the error model corrected (Poisson-of-the-mean, not spatial StdDev)
`redchi` ≈ 4.75 for a single region. `thickness` ± 8.6% once `norm` and `t0` are fixed.

---

## Assumed, not measured — the honest gap

```
H/Zr = 2 × P_peak / D
```

| input | status | sensitivity |
|---|---|---|
| D = 10 mm | Thor's recollection | 9→11 mm moves H/Zr 2.18→1.78 |
| norm = 0.3187 | **fitted from this data — self-referential** | ±10% moves H/Zr ±0.11 |
| `.ncmat` cross section | assumed correct | — |

Quoted ±0.10 covers only the fit. A defensible total is nearer **±0.2**.

**Red flag:** the joint fit returned **χ²ᵥ = 0.02** — the data is not constraining the
model, so it absorbs whatever D it is handed. Test: set `D_MM` to 9 and 11 and confirm
H/Zr tracks 1/D exactly. If it does, the answer is being read back from the input.

---

## Two things that are wrong or mislabelled

**`ZrH1p6_bct.ncmat` is not ZrH₁.₆.** DYNINFO fractions are 2/3 H, 1/3 Zr —
stoichiometric **ZrH₂**. Spacegroup 139, a = 3.536, c = 4.44, c/a = 1.256 → **ε phase,
not δ**. Real VDOS so it is fittable, but wrong for the reactor-relevant δ regime.

**No Bragg edge falls in the fitted range.** Al's first is 4.676 Å, ε-ZrH₂'s is 5.532 Å;
the fit stops at 3.5 Å. Without edges there is no phase, lattice-parameter or texture
information, and `thickness` correlates with the phase split at 0.9996.

---

## Scripts (copies in `erni-toolkit/tools/`)

| file | does |
|---|---|
| `multiregion.py` | fits several regions, overview + per-region zoom and spectrum |
| `map2d.py` | 2D optical-thickness map with row and column marginals, chord fit |
| `rowscan.py` | nbragg per row band vs the chord model, residual panel |
| `jointfit.py` | joint fit of P_peak, R, y₀; derives pixel size from known D |
| `hydrogen_sensitivity.py` | NCrystal dΣ/dx — ~4.5% in Σ per ΔH/Zr of 0.1 |
| `inspect_stack.py` | gates a new TOF stack: usable bins, λ coverage, layout |

Transfer by `pbpaste > file.py` then `%run -i file.py` — pasting into a Jupyter cell
corrupts them (auto-indent dropped ~25 lines once).

`komplot` installs from PyPI. `result.fit_report_text()` is real — nbragg monkey-patches
`fit_report` to HTML and preserves lmfit's text version under that name.

---

## Asks, ranked

**Tier 1 — blocks the measurement**
1. **Control run number** — cancels geometry, norm and background at once
2. **Proton charge or live counting time for 111711 and 111859** — makes `norm` external
3. **Pellet diameter with an error bar** (Kohnert) — dome fit suggests 9.4–10 mm
4. **Confirm orientation** — axis-horizontal, beam across the diameter (inferred, not told)

**Tier 2 — needed to interpret**
5. Thermal history of 111859 — temperature, duration, atmosphere, gradient or isothermal
6. What else is in frame — there is a feature at rows 100–190 that is not the pellet
7. Al or TZM? The script says "Al tube"; Thor says later samples are TZM

**Tier 3 — future**
8. A δ-ZrH₁.₆ material file (Mehta computed δ-ZrH₁.₄–₁.₇)
9. A thinner or differently oriented run — needed for any Bragg-edge work
10. Where `0.2*al` came from — physical estimate or placeholder? (ask Brendt)

---

## Next steps

1. Run the D-sensitivity test above — confirm whether H/Zr is measured or assumed
2. Send the Tier 1 asks
3. Once the control run exists: same regions, same settings, difference the ZrH paths.
   That is the hydrogen-loss measurement and it needs neither D nor norm.

---

## Artifacts

- Problem → solution overview: https://claude.ai/code/artifact/e9b5a284-e168-417b-af51-257d2109b937
- Why the 53% spread was geometry: https://claude.ai/code/artifact/52c034e0-0b43-45a6-a96a-03808427280c

---

## 2026-09-02 — long-wavelength survey and the response term

**Bragg-edge work on this pellet is dead, and it is now measured rather than argued.**

- Measured T is flat at ~0.002 from 2.5 to 8 Å and *rises* to ~0.005 by 10.5 Å.
  Real transmission would fall ~40% across that span. A rising ratio as both
  beams die is two backgrounds dividing into each other.
- The `.ncmat` predicts a 32% step at 5.000 Å and 22% at 5.532 Å. Measured:
  4.91 → 0.00174, 4.99 → 0.00209, 5.08 → 0.00190, all ±0.00013. Nothing.
- **Correction to the note above:** "no Bragg edge falls in the fitted range" is
  wrong. Six ε-ZrH₂ edges fall below 3.5 Å — (200) 3.536, (112) 3.320,
  (211) 2.980, (202) 2.766, (220) 2.501, (004) 2.220 Å. They carry no weight
  because the pellet is opaque there. Different diagnosis, different fix.
- Optimal edge thickness is Σz ≈ 2 → **~3 mm**, against the current ~10 mm at
  Σz ≈ 6. That is the number to attach to ask #9.

**Background.** Row profiles at 5–7 Å: upper pellet 0.00457, dome centre
~0.0021, lower pellet 0.00167. Real chord-dependent structure on a floor of
roughly 0.0016–0.0021. Signal and background are the same order at long λ and
**cannot be separated from this data alone.** A black body is still needed —
Gd foil ~0.5 mm; Cd is transparent at 0.44 Å, inside the analysis band.

**The response term.** nbragg's default `kind="jorgensen"` builds its kernel on
a fixed 0.1 Å internal grid and applies it with `scipy.ndimage.convolve1d`,
which is sample-based. Physical width = N_samples × data_dwl, so **α/β are tied
to the binning, not the instrument** (nbragg documents this in the
`jorgensen_inv` docstring). Here data_dwl = 0.0044 Å, so the applied kernel is
~23× narrower than the parameter values imply.

Scan of z_ZrH over α₀/β₀ ∈ {0.3 … 10}:

| response | z_ZrH range | redchi range |
|---|---|---|
| none | 0.4425 | 6.906 |
| `jorgensen` | 0.4404 – 0.4458 (**<1%**) | 5.34 – 7.33 |
| `jorgensen_inv` | 0.3997 – 0.4465 (**~5%**) | **5.57 – 1073** |

α₀ = 3.67, β₀ = 3.06 are library defaults, not physical values. Use
`response="jorgensen_inv"` if α/β are ever to transfer.

**RESOLVED 2026-09-02 — and P_peak ≈ 0.98 cm above does not survive.**
Start-value scans (0.5 → 2.5 cm) converge to one minimum, so there is no path
dependence. With the background frozen, z_ZrH = 0.4458 (chisqr 4728). Letting
the background float, z_ZrH = 0.5358 at **chisqr 3249.8 — better than the
original 8-parameter fit's 3697.7, with half the parameters.** The original
thickness of 1.179 cm was never the optimum; it is where an 8-parameter fit
with C(thickness,p1) = 0.9996 happened to stop.

**Current best: z_ZrH ≈ 0.45–0.54 cm**, roughly half the earlier figure.

Error budget, measured rather than argued:

| input | effect on z_ZrH |
|---|---|
| response α₀/β₀ over 30× | < 1% |
| weight constraint tied vs free | 1.3% |
| z_Al over 0.15–0.25 cm | ± 3.5% |
| **background fixed vs free** | **+20%** |

**The background is the dominant systematic by 6×.** The black-body / Gd frame
now outranks the pellet diameter and the proton charge on the ask list.

**The Al path is measured, not assumed.** Three independent routes agree:
redchi minimum in a z_Al scan gives 0.20–0.22 cm, weight-free fit gives 0.219,
original fit gives 0.209. So ~2.1 mm total Al path, a ~1.05 mm wall crossed
twice. `0.2*al` (ask #10) was a good estimate. Material still unconfirmed
(ask #7) — 2.1 mm of Mo is a very different cross-section.

**What the new number implies.** If the centre chord is ~1.0 cm, then 0.54 cm
of ZrH₂-equivalent path means the material is about half as attenuating as
stoichiometric ZrH₂ (~0.64 cm after correcting for the file being ZrH₂ rather
than δ-ZrH₁.₆). Candidates, none ruled out: lower H content, porosity or
microcracking (Torres saw both), a wrong cross-section, or a pellet smaller
than 10 mm. Ask #3 separates the last from the rest.

---

## 2026-09-03 — norm measured; the "background" is probably sample scatter

**`norm` is no longer self-referential.** Measured in rows 10–60, columns
200–350 — pixels the pellet fit never uses. T there is flat from 3 to 8 Å at
**~0.32**, mean 0.3407 over 0.44–3.5 Å, against the fitted 0.3187. Agreement to
7%. Use the flat asymptote (~0.32), not the mean: an exposure ratio is
wavelength-independent by definition, so the flat part is the clean estimate.

**The fitted polynomial background is not a background.**

| λ | fitted bg |
|---|---|
| 0.5 | +0.0263 |
| 3.5 | +0.0069 |
| 5.5 | −0.00009 |
| 7.0 | −0.0044 |

It is 2.6% at short λ, goes **negative** past 5 Å, and disagrees in sign with
the measured floor (+0.0016 to +0.0021). `C(thickness, bg0) = +0.9557` — it
trades one-for-one with the thing being measured. A **constant** background
pinned at the measured floor fits far worse (χ² 8500–9100 vs 3250), so the
wavelength dependence is needed but does not belong in the background term.

**New lead.** The open region is *not* flat below ~1.5 Å — it rises ~15% above
its own asymptote, i.e. **counts arriving that did not come down the direct
path**. Excess ≈ 0.05 in T units at 0.5 Å, the same order and sign as the fitted
bg. Prime suspect: neutrons scattered out of the pellet. Test in progress:
does the excess grow with proximity to the sample (scatter) or stay uniform
(a spectral mismatch between 111859 and 111711)?

If it is scatter, nbragg already has the hook — `models.py` carries
`k = kwargs.get("k", 1.)`, a "sample dependent background factor" — and the
correction is measurable in-frame on every exposure, which would also solve the
per-frame background problem for a temperature ramp.

**Still open:** the `.ncmat` has never been validated against EXFOR (CLAUDE.md
gate #2). Schmidt 1967 (EXFOR 23424) and Whittemore 1964 (14174/002-003) are
worked up in the TRIGA notebook. If the scatter hypothesis fails, a wrong
Σ(λ) shape from an unvalidated VDOS is the next suspect for the fake background.

---

## 2026-09-03b — scatter measured; the model itself is what fails

**Retraction.** The "P_peak ≈ 0.98 cm does not survive" note above is withdrawn.
With the measured scatter subtracted and no background fudge, the fit returns
**z_ZrH = 1.008 cm** — essentially the original 0.970. The 0.536 that prompted
the retraction is the one configuration of three carrying an unphysical
(negative) background.

| configuration | z_ZrH | redchi |
|---|---|---|
| original 8-parameter free fit | 0.970 | 4.75 |
| locked, free polynomial background | 0.536 | 4.15 |
| locked, measured scatter subtracted, **no** background | **1.008** | **38.2** |

**Defensible statement: the hydride path is 0.5–1.0 cm, and the spread between
configurations is the real uncertainty.** Each fit's own error bar (0.13% here)
is meaningless beside it.

**redchi 38 is the finding.** With every fudge removed and only thickness free,
the model fails. R² still reads 0.993, so this is invisible on a plot. The free
polynomial background was hiding a genuine model failure.

**Scatter is real but does not explain the background.** Measured: 0.41% of the
open beam in 0.44–1.33 Å, **12.7% of the counts in the pellet ROI**. The fitted
polynomial background was 2.6% at 0.5 Å — 6× larger. An earlier note claiming
the magnitudes matched compared the wrong quantities: the open strip (rows
25–75) sits near the top edge of the beam disc where illumination is ~7× lower,
so the same absolute scatter appears as a much larger *fraction* there.

Scatter subtraction is still worth doing and needs no extra beam time — the
open rows of every exposure carry it, which also makes it per-frame for a ramp.

**Suspect list is down to one.** Response blur <1%, weight parametrisation 1.3%,
Al path ±3.5%, `norm` measured and agreeing, scatter measured and 6× too small.
What is left is the **cross-section's wavelength dependence** — CLAUDE.md gate
#2, never validated against EXFOR (Schmidt 1967 / 23424; Whittemore 1964 /
14174/002-003, both in the TRIGA notebook).

**Caveat on the corrected fit:** the scatter estimate goes noise-dominated above
~1.5 Å, swinging three decades. The 0.44–3.5 Å range corrects much of its span
with noise and may carry a good share of the 38. Re-run at wlmax = 2.0.

**norm measured = 0.3249** (open rows, 3–8 Å), against 0.3187 fitted.
