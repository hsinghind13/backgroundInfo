# LANL — Hydride Moderators: YH_x / ZrH_x, Hydrogen Loss, Claddings

Thor (Harsh Singh), LANL internship **2026-08-03 → 2026-10-02**.

**Scope:** **YH_x and ZrH_x moderators and their claddings — how hydrogen is lost, measured by neutron diffraction and other techniques, worked up into transmission spectra.** PI **Sven Vogel**, MST-8. Proposal **20261257CR** ("ERNI & The Moderators"), $100K.

Secondary thread: 20 kWe NEP reactor design with **Siddharth Sivakumar** (ANL/INL).

> A reactor you can launch — or run on HALEU — has to be small → small means thermal neutrons → thermal means hydrogen → hydrogen won't hold still when it's hot → neutrons are the only practical way to see where it went.

---

## Read these first, in this order

1. **`HANDBOOK-II.md`** — **the current context.** Scope correction, the Y vs Zr materials science, hydrogen-loss mechanisms, claddings, the HIPPO+LumaCam measurement, paper reviews, revised open questions. **Supersedes HANDBOOK.md wherever they conflict.**
2. **`Vogel_IMS_IR_ERNIAndTheModerators_Submit (1).pdf`** — the statement of work. Four pages. Not background; it's the spec.
3. `HANDBOOK.md` — the earlier deep dive. Still good on ZrH₂ transmission physics, structure factors, and the NCrystal/nbragg stack. **Wrong or incomplete on: yttrium (absent entirely), the instrument (unidentified), diffraction's role (understated).** See HANDBOOK-II §7.

---

## The five things that gate any code you write

1. **Both materials are in scope.** The SOW's first sentence: *"Hydrides of yttrium or zirconium are candidate materials."* HANDBOOK.md dropped Y entirely — that was its biggest error.
2. **NCrystal ships no ZrH₂, no ZrH, and no YH₂.** Both materials must be composed from CIF + real VDOS (not the auto-generated dummy Debye) and **validated against EXFOR before fitting anything real.** The `ncrystal-extra` file `ZrH_T296.0K_ENDF8_massconvert_inelasticonly_dummydensity.ncmat` is unusable: wrong stoichiometry, no unit cell, no Bragg edges, `@DENSITY 1 g_per_cm3 #FIXME`. EXFOR data ready-made in the TRIGA notebook: Schmidt 1967 (23424), Whittemore 1964 (14174/002,003).
3. **The lattice parameter is a hydrogen meter for Zr and nearly useless for Y.** δ-YH_x sits at 0.5200–0.5207 nm across the *entire* range 1.50 < H/Y < 2.00 (~0.13%). For yttrium, read hydrogen from the **α-Y / δ-YH₂ phase fraction** (`f_δ[%] = 53C − 1.05`) and from **edge-height ratios** — (111) is exactly blind to hydrogen in fluorite and is a free internal standard. HANDBOOK-II §2.4.
4. **Texture is the dominant systematic.** These pellets are twinned and microcracked (Torres SEM). Get the ODF from the simultaneous diffraction, fix the orientation weights, *then* fit transmission. Hirsh et al. needed 13 orientation components on steel and hit NCrystal's mosaicity ceiling on uranium.
5. **L and t₀ are published** — you are not blocked on them. L = 9.014 ± 0.001 m, t₀ = 0.10 ± 0.01 µs (Hirsh et al. 2025).

---

## The instrument

**HIPPO**, Flight Path 4, Lujan Center, **LANSCE** — TOF diffractometer with the **LumaCam** event camera integrated 10 cm behind the sample. Diffraction and energy-resolved imaging **simultaneously, same volume, same run.**

| | |
|---|---|
| Flight path (moderator → camera) | **9.014 ± 0.001 m** · t₀ = **0.10 ± 0.01 µs** |
| Flux / beam | ~10⁷ n/cm²/s · spot 10 mm · L/D ≈ 130 |
| Diffraction detectors | 1200 He-3 tubes, 45 panels, 5 rings @ 40/60/90/120/140°, ~20% of 4π |
| Camera | ⁶LiF-ZnO:Zn 450 µm → intensifier ×10⁶ → TimePix3 256×256, 55 µm pitch |
| Field of view | **~14 × 14 mm²** · smallest usable spectral ROI **16×16 px** |
| Binning | Bragg-edge: 512×512, **10 µs** · resonance: 512×512, 250 ns |
| Exposure | 10–30 min per orientation |
| Background | **~2.5%** (vs ~20% on ERNI/FP5 — gamma rejection) |

Short flight path (~9 m vs IMAT 20 m, CSNS 35 m) with no choppers or curved guides → thermal **and** epithermal in one pulse → Bragg-edge imaging + resonance imaging + diffraction in parallel. Resonance Doppler broadening gives sample temperature with no inserted thermocouple.

Conversions: λ[Å] = 3956/v[m/s] · E[meV] = 81.81/λ[Å]²

---

## Reference links — canonical list

Do not ask Thor to re-paste these.

| Resource | URL | Verdict |
|---|---|---|
| **nbragg** | https://github.com/TsvikiHirsh/nbragg | **Essential** — the fitting engine (lmfit `Model` over NCrystal), ref [6] of the SOW. **Branch `master`, not `main`.** Author **Tsviki Hirsh is first author of the HIPPO/LumaCam paper with Vogel** — the tool was built for this instrument |
| **save_roi** | https://github.com/TsvikiHirsh/save_roi/blob/main/QUICK_START.md | **Essential** — 3D TIFF stack (slices = TOF bins) → per-region 1D spectra. `--tilt` straightens a tilted symmetry axis, built for cylindrical pellets |
| **NCrystal** | https://github.com/mctools/ncrystal | **Essential** — the physics under nbragg, refs [8–10] of the SOW |
| **TSL_School — Transmission** | https://github.com/highness-eu/TSL_School (`openmc/Examples/Transmission`) | **Priority 1. Nobody linked it; it's the most useful.** Recovers Σ_tot = −ln(T)/dx — structurally identical to the measurement. Clone it, swap in the hydride |
| ncrystal-notebooks (advanced) | https://github.com/mctools/ncrystal-notebooks | Priority 2: `ncrystal2_advanced_01/02/03` — NCMATComposer, CIF import, PhononDOSAnalyser+QE. **The actual job** (see gate #2) |
| Water/Ice notebook (NEUWAVE-12) | https://github.com/mctools/ncrystal-notebooks/blob/main/notebooks/contributed/NEUWAVE-12/NEUWAVE_12_Examples_Water_Ice.ipynb | Useful **as method, not topic** — compose → replace dummy Debye with real VDOS → validate vs EXFOR. The water is irrelevant |
| NCrystal tutorial deck | https://indico.ess.eu/event/3439/sessions/7330/attachments/15695/30086/2024-09-05-neuwave-workshop.pdf | Orienting. **Not a NEUWAVE talk** — Kittelmann's NCrystal satellite tutorial deck, LINXS, 5 Sept 2024 |
| TSL_School — TRIGA cell | https://github.com/highness-eu/TSL_School/blob/main/openmc/Examples/ReactorCell/TSL_School-TRIGA_cell.ipynb | **Lowest priority — but its null result is the project's justification.** ENDF path (no Bragg edges) and NCrystal path (Bragg edges) agree on k-eff to 0.0004. **Bragg edges are exactly what this project measures.** A ZrH TSL validated against k-eff is *not* validated for imaging |
| **Hirsh et al. 2025** (instrument) | https://doi.org/10.1038/s41598-025-96790-1 · LA-UR-24-28723 | **Open access. The method paper — read cover to cover.** HIPPO+LumaCam, calibration, Beer-Lambert + Jorgensen + NCrystal + LMFIT, texture workflow |
| ORNL YH_x handbook | https://info.ornl.gov/sites/publications/Files/Pub160401.pdf | **Free.** ORNL/TM-2021/2052 — the YH_x property database (structure, thermal, mechanical, TDS, irradiation) |
| Parkison/Kohnert (Zircaloy→δ-ZrH) | https://arxiv.org/abs/2305.02249 | Free. Kohnert co-author. Fabrication route from cladding alloy |
| SRP_interns2026 | https://github.com/RWillat/SRP_interns2026 | **Blocked — private.** Request access as `hsinghind13` |
| VTB / MRAD | https://github.com/idaholab/virtual_test_bed | NEP thread only. Template; needs NCRC. Useful models are S8ER / KRUSTY / hpmr_h2 |

**Toolchain:** save_roi → NCrystal (σ) → nbragg/LMFIT (fit, Jorgensen response) for transmission; **GSAS/gsaslanguage** (Rietveld) and **MAUD → MTEX** (texture/ODF) for diffraction; **SAMMY/PLEIADES** for resonances. `export NCRYSTAL_ONLINEDB_CACHEDIR=...` early.

---

## Top open questions (full list in HANDBOOK-II §8.2)

1. **Y or Zr — or both?** SOW says "yttrium or zirconium," but the five characterized pellets are ZrH₂. Second dataset, follow-on, or scope to open?
2. **Which reading of "claddings"?** Barrier/enclosure *for* hydride moderators (TZM, Nb, SS316L, Al₂O₃–Cr₂O₃), or hydrogen *in* Zircaloy cladding? Both are supported by the sources; the analysis differs.
3. **The five pellets' thermal histories** (samples A, C, D, E, F + unexposed control) — temperatures, durations, atmosphere, and whether any were held under a *gradient* rather than isothermally. Without this the phase maps have nothing to be read against.
4. Was diffraction collected simultaneously with the 2,500 radiographs? Get both — the texture workflow needs it.
5. Any heated / in-situ dataset, or all ex-situ at RT? (The RT state may not be the operating state.)
6. `SRP_interns2026` access as `hsinghind13`; what does "SRP" stand for?

---

## People

| Who | Where | Role |
|---|---|---|
| **Sven Vogel** (sven@lanl.gov) | LANL MST-8 | **PI.** Neutron physics; HIPPO instrument scientist; wrote `gsaslanguage`; PhD thesis is the Rietveld-transmission method itself |
| **Tsviki Hirsh** (tsviki@soreq.gov.il) | Soreq NRC, Israel | Author of **nbragg** and **save_roi**; first author of the HIPPO/LumaCam paper. Direct collaborator |
| **Caitlin Kohnert** | LANL | POC for moderators, microreactor program. Co-author on Torres et al. and the Zircaloy→δ-ZrH paper |
| Brendt Wohlberg | LANL | Computational imaging; leads Python/data (0.08 FTE) |
| Elizabeth Kardoulaki | LANL | Hydride characterization coordination (0.02 FTE) |
| **Vedant Mehta** | LANL NEN | First author on **both** the δ-ZrH_x and δ-YH₂₋ₓ TSL papers, and on MARM multiphysics. The TSL person |
| Aditya Shivprasad · Tarik Saleh | LANL | Torres et al. supervision / project admin + funding |
| Daniel Rehn (rehnd@lanl.gov) | LANL Comp Physics | AIMD/TSL; on both flagged papers |
| Charles Bouman | Purdue | Radiographic/tomographic methods (unfunded collaborator) |
| **Siddharth Sivakumar** | ANL/INL | NEP thread — 20 kWe thermal power / efficiency |
| RWillat | ? | Owns `SRP_interns2026` |

---

## Local files

| File | What |
|---|---|
| **`ERNI-RESUME.md`** | **Live analysis state for run 111859 — read before touching the data.** What is measured vs assumed, the scripts, the ranked asks. |
| `erni-toolkit/tools/` | Analysis scripts (row scan, 2D map, joint fit, sensitivity) |
| **`HANDBOOK-II.md`** | **Current context. Start here.** |
| `Vogel_IMS_IR_ERNIAndTheModerators_Submit (1).pdf` | **The statement of work** (20261257CR, $100K) |
| `HANDBOOK.md` | Earlier deep dive — good on ZrH₂ transmission physics, superseded on scope/instrument |
| `jne-05-00022.pdf` | **Mehta, Rehn & Olsson 2024**, J. Nucl. Eng. 5, 330–346 — δ-ZrH₁.₄–₁.₇ TSLs from AIMD. **Theory side.** Reviewed in HANDBOOK-II §6.1 |
| `1-s2.0-S0022311524005373-main.pdf` | **Torres et al. 2025**, J. Nucl. Mater. 603, 155437 — ε-ZrH₁.₈ from Zircaloy-4, on HIPPO. **Vogel + Kohnert co-authors — the group's own paper.** Reviewed in HANDBOOK-II §6.2 |
| `Design and Fabrication of the Brayton Rotating Unit.pdf` | NASA CR-1870. **NEP thread only.** Table 2 (PDF p.30) is the one that matters — but see HANDBOOK.md §6.3: it does *not* vindicate 26% |
| `2026 W4.pdf`, `W4 DD Reminders.pdf`, `Direct Deposit Authorization…pdf` | Onboarding paperwork — not technical |

---

## Standing corrections — do not re-derive these wrong

**Hydride thread:**
- **The reactor-relevant ZrH phase is δ (1.56 ≤ H/Zr ≤ 1.64), not ε.** ε-ZrH₂ is the validation endpoint. At 800–1000 K the whole ZrH₁.₄–ZrH₁.₇ range is single-phase δ.
- **Phase matters more than stoichiometry.** ε→δ changes the TSL more than varying H content within δ does (Mehta et al.). Nail the phase first.
- **ENDF/B-VIII.0's ZrH TSLs have no Bragg edges** — both sublattices done under the incoherent approximation via LEAPR. The standard evaluated data structurally cannot describe this measurement.
- **YH_x carries more composition information in its TSL than ZrH_x does** (Mehta et al.) — good news for the Y thread.
- **NJOY's THERMR module smears the H optical phonon.** Via ACE/MCNP you lose it; NCrystal direct keeps it.
- **137 meV is the ENDF Einstein-oscillator parameter**; the ab-initio/INS DOS peak is ~140–145 meV. Both right in context — not the same claim.
- **A Zircaloy hydride is not a pure-Zr hydride.** Torres measured CTE ~30% below pure-Zr literature values. Don't transfer numbers across.
- **Trellue et al. is JOM 2021** 73(11) 3513–3518, not 2023.

**NEP thread:**
- **"BRU got 30%, so 26% is conservative" is backwards.** BRU's 30% rides on a **300 K cold end** costing 4× the radiator area of a 425 K one. In space power, efficiency and radiator area are the same trade — **an efficiency quoted without its cold-end temperature is not a number.** 26% is a *converter* figure, optimistic as a *system* figure.
- **NEP, not NTP.** DRACO was NTP and was cancelled under FY2026 — never cite it as precedent.
- BRU is **2.25–10.5 kWe** at 0.217/0.30/0.32. BIPS is **1.3 kWe**. SNAP-10A flew at **1.43%**. SP-100 is **2.5 MWt**.
- The Acta Astronautica paper is a **100 kWe Brayton review** — no 20 kWe, no Stirling. Full text never read (ScienceDirect blocked); **26% may not literally appear in it.** Pull via UTK access before quoting the critique.

---

## Calibrations and correction factors — standing rule

**Every calibration, correction factor, fixed parameter or bound must have a physical basis, stated at the time it is applied.** Fudge factors are acceptable; unexplained ones are not.

Before fixing or adjusting anything, say out loud:
1. **What physical quantity is this?** (a flight path, an exposure ratio, a detector pitch, a phase fraction)
2. **Where does the number come from?** — measured, published, derived from geometry, or fitted from this same data
3. **What happens to the answer if it is wrong by 10%?**

**Never choose a correction because it moves the result toward an expected value.** If a result is unphysical, enumerate *all* the candidate causes before picking one, and say which of them you have not ruled out.

**A number fitted from the data cannot then be used to validate that same data.** Flag self-referential inputs explicitly (e.g. `norm` fixed at a value the fit itself produced).

**Distinguish measured from assumed in the error bar.** A quoted uncertainty must state which inputs it covers. If the dominant uncertainty is an assumed input, say so and give the sensitivity.

**Where the physical basis is uncertain, ask Thor rather than choosing.** Sample dimensions, run conditions, instrument geometry and material identity are his to supply, not mine to infer.

---

## Working notes

- Vault context (Active tasks, project logs, daily notes) lives in `~/Desktop/VaultFlow` and is handled by a separate JARVIS session. **This folder is technical work only** — don't write vault files from here.
- Thor is direct, no padding. Push back when something doesn't hold up.
