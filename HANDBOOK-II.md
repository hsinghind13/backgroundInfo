# HANDBOOK II — YH_x / ZrH_x, Hydrogen Loss, Claddings, and the Two-Modality Measurement

**Assembled 2026-08-07.** Supersedes `HANDBOOK.md` wherever the two conflict. HANDBOOK.md was built from the resource dump alone and got the ZrH₂ transmission physics substantially right, but it (a) dropped yttrium entirely, (b) never identified the instrument, and (c) treated diffraction as a validation afterthought rather than a co-equal modality. All three are corrected here.

**Scope, corrected:** *YH_x and ZrH_x moderators and their claddings — how hydrogen is lost, measured by neutron diffraction and other techniques, worked up into transmission spectra.*

---

# 0. What changed, and why it matters

| HANDBOOK.md said | Actually |
|---|---|
| ZrH₂ only | **The SOW's first sentence names both:** *"Hydrides of yttrium or zirconium are candidate materials for solid-state high-temperature moderators."* Y is not a side note — it is the material the DOE microreactor program and ORNL's TCR actually selected |
| "Probably ε — confirm with Vogel" | Both phases are in play, and **the ε↔δ transition IS the hydrogen-loss signature.** For Y the question is different and more interesting (§2.3) |
| Diffraction = ground truth for milestone 3 | **Diffraction and imaging are collected simultaneously on the same instrument, on the same volume, in the same run.** HIPPO + LumaCam. This is the whole point |
| "You cannot convert TOF→λ without L and t₀" | **Published:** L = 9.014 ± 0.001 m, t₀ = 0.10 ± 0.01 µs (§5.4) |
| Instrument unknown | HIPPO, Flight Path 4, Lujan Center, LANSCE. Vogel co-wrote both the instrument paper and the texture-analysis method it uses |
| nbragg is "a tool Vogel cited" | **nbragg's author, Tsviki Hirsh, is first author of the HIPPO/LumaCam paper with Vogel.** The tool was built for this instrument by a direct collaborator |

The one thing HANDBOOK.md got *most* right is worth keeping: **crystal symmetry is a hydrogen meter.** That stays true. It just reads differently in Y than in Zr, and that difference is the single most important materials-science fact in this project.

---

# 1. The nuclear engineering picture

## 1.1 Why a solid moderator exists at all

Two independent drivers converge on the same material:

**Microreactors on HALEU.** Commercial and research reactors want to drop off HEU. HALEU caps at <19.75 at.% ²³⁵U. Less fissile material means less reactivity, and the way you buy it back is to soften the spectrum — thermalize the neutrons so each ²³⁵U nucleus is far more likely to fission. Water is the usual answer and it is unavailable here: keeping water liquid above ~600 K demands prohibitive pressure. A **solid-state moderator** operates at 800–1000 K at ambient pressure, and can sit inside the core adjacent to the fuel.

**Space power.** A reactor you can launch has to be small; small means thermal; thermal means hydrogen. Same conclusion, different constraint.

Historical precedent is deep, not speculative: SNAP, TRIGA, the Soviet TOPAZ reactors, and the US Aircraft Nuclear Propulsion program all used metal hydride. Current programs — MARVEL (INL), the Transformational Challenge Reactor (ORNL), NTP concepts — all specify hydride moderation.

## 1.2 The 500× that pays for everything

²³⁵U's fission cross section is **585 barns at thermal (0.0253 eV)** and **1.2 barns at 1 MeV**, where fission neutrons are born. That factor of ~500 is the entire economic case for moderation.

Hydrogen is not merely the best moderator available — it is the best one *possible*, because it alone shares the neutron's mass:

| Nucleus | A | α = ((A−1)/(A+1))² | Max energy loss per collision | ξ | Collisions to thermalize |
|---|:--:|:--:|:--:|:--:|:--:|
| **Hydrogen** | 1 | **0** | **100%** | **1.000** | **~18** |
| Deuterium | 2 | 0.111 | 89% | 0.725 | ~25 |
| Carbon | 12 | 0.716 | 28% | 0.158 | ~115 |
| **Zirconium** | 91 | 0.957 | **4.3%** | 0.022 | **~835** |
| **Yttrium** | 89 | 0.956 | 4.4% | ~0.022 | ~820 |

Zr and Y are nearly identical as moderators — which is to say, both are useless. **The metal is scaffolding.** Hydrogen does essentially all the moderation; the metal's only jobs are to hold the hydrogen at temperature and to stay out of the way neutronically.

## 1.3 Y vs Zr — the actual trade

This is the central engineering decision of the field, and it is a clean two-variable trade.

**Hydrogen retention (Y wins, decisively).** At 1 atm H₂ equilibrium, ZrH_x holds ~7×10²² H/cm³ up to roughly 800 °C, then falls off a cliff and is essentially empty past ~1100 °C. YH_x starts higher (~8×10²²), declines gently, and still holds ~5×10²² H/cm³ at **~1350 °C**. ORNL states the crossover plainly: YH_x "retains a higher hydrogen content at elevated temperatures **above 1,143 K**." ZrH use is capped at <1000 K; that cap is the reason Y exists as a program.

**Parasitic absorption (Zr wins).**

| | b_coh | σ_scatter (bound) | **σ_absorb (2200 m/s)** |
|---|---|---|---|
| Zr | +7.16 fm | 6.46 b | **0.185 b** |
| Y | +7.75 fm | 7.7 b (7.55 coh + 0.15 inc) | **1.28 b** |
| H | **−3.739 fm** | **82.02 b** (1.76 coh + **80.27 inc**) | 0.333 b |

**Yttrium absorbs ~6.9× more thermal neutrons than zirconium.** That is a real reactivity penalty paid on every metal atom in the core. Zirconium's near-transparency (0.185 b) is precisely why it became the nuclear industry's structural metal in the first place.

**So the trade is: Y buys you roughly 250–400 K of operating temperature, and you pay for it in neutron economy.** Which side wins depends entirely on the core design. That is why both materials are still live, and why this project characterizes both.

A second, subtler cost: **yttrium is an oxygen getter.** Oxygen solubility in Y reaches 10 at.% at 1273 K, and ORNL notes Y's affinity for oxygen is "insatiable." Any oxygen ingress is absorbed by the moderator rather than passing through — a safety and performance concern in its own right, and a contamination hazard during characterization.

## 1.4 Why the hydrogen leaves — three distinct mechanisms

Do not conflate these. They have different physics, different signatures, and different fixes.

**(a) Thermal decomposition / dissociation.** A hydride in contact with an environment at lower hydrogen partial pressure than its own equilibrium pressure will desorb until the two match. In an open system there is no equilibrium to reach — desorption continues until all the hydrogen is gone and you are left with bare metal. This is thermodynamics, not damage; it is governed by the PCT (pressure–composition–temperature) surface of the binary system.

**(b) Permeation loss through the enclosure.** Even in a sealed system, H₂ diffuses through the containment wall and is lost to the coolant or the environment. This is a kinetics problem in the *cladding*, not the hydride — and it is the reason claddings exist (§4).

**(c) Redistribution under a temperature gradient — the Soret effect.** This one loses no hydrogen at all from the system, and is arguably the worst. Hydrogen migrates **down the thermal gradient**, from the hot side toward the cold side. Inside a real core, one face of a moderator pellet is fuel-facing (hot) and the other is heat-pipe-facing (cold). The SOW names exactly this geometry.

The Soret flux adds to ordinary Fick diffusion:

$$J = -D\left(\nabla C + \frac{C\,Q^*}{RT^2}\nabla T\right)$$

where **Q\*** is the heat of transport. Measured values for hydrogen in Zircaloy are **25 ± 3 kJ/mol when H is in solution** and **116 ± 17 kJ/mol when stable hydrides are present** — a ~5× jump that means the driving force is far stronger once you are in the hydride field. Q* for YH_x has not been measured; ORNL flags it as an open need.

**Why (c) is the nastiest:** it is a coupled feedback loop. Hydrogen leaves the hot zone → less moderation there → less local thermalization → the local power shape changes → the temperature profile changes → the gradient driving the migration changes. Fabricate a uniform ZrH₁.₆ pellet and it evolves in-service into a ZrH₁.₅₅–ZrH₁.₆₅ profile. **A bulk mass measurement sees none of this** — total hydrogen is conserved. Only a spatially resolved measurement can see it. That is the entire reason this project is funded.

## 1.5 The bonus: hydride is also *why the reactor is safe*

Hydrogen bound in ZrH sits in a near-Einstein optical mode — the ENDF `c_H_in_ZrH` model places the oscillator at **137 meV**; ab initio and INS put the DOS peak nearer **140–145 meV** (Couch 1971, Evans 1996; Mehta et al. Fig. 4). Either way it is far above kT (25.9 meV at 300 K, 86.2 meV at 1000 K).

When the core heats, more of those oscillators are thermally excited, and they **upscatter** neutrons — hand energy *back* to them. The spectrum hardens, ²³⁵U's cross section drops, reactivity falls. This is a prompt, physically inherent negative temperature coefficient. It is the reason TRIGA reactors can be pulsed safely by undergraduates.

**So hydrogen concentration is not one design parameter among many. It sets the moderation, and it sets the safety feedback. Losing it degrades both simultaneously.**

---

# 2. The materials science picture

## 2.1 One structure underlies everything

> Take **fcc metal**. Pour hydrogen into the **tetrahedral holes**. There are exactly **2 per metal atom** — "all holes full" = MH₂ = **fluorite** (CaF₂ type, Fm-3m).

Both systems are built from this. What differs is what happens as you empty the holes.

- **Holes mostly full, vacancies disordered** → stays cubic → **δ phase**
- **Holes nearly all full** → in Zr, the lattice can no longer stay cubic → **tetragonal distortion** → **ε phase**
- **Holes ordered at partial filling** → different tetragonal distortion → γ-ZrH (metastable, contested)

These are *interstitial* (metallic) hydrides — hydrogen sits in the lattice, donating/accepting charge with the metal d-band. XPS on YH₂ shows charge transfer from Y to H, i.e. anionic-type Y–H bonding. The bond is strongly ionic, there are few slip systems, and **the material is intrinsically brittle** as a result.

## 2.2 The Zr–H system

| Phase | Structure | Space group | H/Zr | Notes |
|---|---|---|---|---|
| α-Zr | hcp | P6₃/mmc (#194) | ~0 → 0.06 | NCrystal ships this (`Zr_sg194.ncmat`) |
| β-Zr | bcc | Im-3m (#229) | to ~0.6 | >550 °C only |
| γ-ZrH | fc tetragonal | P4₂/n (#86) | ≈1.0 | metastable; equilibrium status contested |
| **δ-ZrH_x** | **fcc fluorite** | **Fm-3m (#225)** | **1.5 – ~1.63** | **The reactor phase.** Mehta: stable δ for 1.56 ≤ H/Zr ≤ 1.64 |
| **ε-ZrH_x** | **fc tetragonal** | **I4/mmm (#139)** | **~1.63 – 2.0** | Hägg: δ→ε shear transition at 62 at.% H |

Eutectoid **550 °C** (β → α + δ). Oxygen contamination stabilizes δ and pushes the two-phase region out to x ≈ 1.75.

**Key nuance HANDBOOK.md missed:** the *reactor operating regime* is δ, not ε. Mehta et al. is explicit — for microreactor operating temperatures of 800–1000 K, the entire range ZrH₁.₄ to ZrH₁.₇ exists as a single δ phase. ε-ZrH₂ is studied mainly to validate methodology against the well-characterized stoichiometric endpoint.

**The δ↔ε signature in a diffraction/transmission pattern is a splitting, not a shift.** I4/mmm is the fcc cell rotated 45° in-plane:

| δ-ZrH₁.₆ (cubic) | | ε-ZrH₂ (tetragonal, I-centred: h+k+l even) |
|---|---|---|
| (111) → **5.52 Å** | → | (101) → **5.51 Å** — *barely moves* |
| (200) → **4.78 Å** | → | **(110) @ 4.99 + (002) @ 4.41** — **SPLITS** |
| (220) → **3.38 Å** | → | **(200) @ 3.53 + (112) @ 3.31** — **SPLITS** |

> **The trap:** the longest-wavelength edge — biggest, most obvious, the one you would check first — is identical in both phases (5.51 vs 5.52 Å). Validate on that alone and both phases pass. The phase information lives in the 2nd and 3rd edges tearing into pairs ~0.6 Å apart.

**And a second lattice-parameter trap that HANDBOOK.md does not state:** the lattice parameter depends on **both** hydrogen content and temperature. Torres et al. measured both for ε-ZrH₁.₈₄ (§6.2). Read H content off a lattice parameter measured hot without removing thermal expansion first and you get the wrong hydrogen.

## 2.3 The Y–H system — and why it is NOT the same

| Phase | Structure | Space group | H/Y | Notes |
|---|---|---|---|---|
| α-Y | **hcp** | P6₃/mmc | 0 → ~0.21 at RT (21 at.% H) | solid solution, H in tetrahedral sites |
| **δ-YH₂** | **fcc fluorite** | **Fm-3m** | ~1.5 → 2.0 | **stable to ~1300 °C** — this is the moderator |
| γ-YH₃ | hexagonal | — | ~3.0 | forms below ~350 °C; not a reactor phase |

Volume expansion: α-Y → δ-YH₂ ≈ **4.5%** (ORNL measured 4.5–5.0% from density); δ-YH₂ → γ-YH₃ ≈ **12%**.

**Yttrium has no ε analogue. δ-YH₂ stays cubic all the way to stoichiometry.** There is no tetragonal distortion, no c/a ratio, no edge splitting. That single structural fact changes the entire measurement strategy.

## 2.4 The critical asymmetry — what actually reads out hydrogen in each system

This is the most important thing in this document.

**For ZrH_x, the lattice itself is the hydrogen meter.** Torres measured, for ε-ZrH_x at RT over 1.7 ≤ x ≤ 2.0, that `a` rises and `c/a` falls with H content along well-fit parabolas (their Table 2). Tetragonality is a direct, sensitive readout of stoichiometry. Plus the δ↔ε splitting gives you a phase readout on top.

**For YH_x, the lattice is nearly blind to hydrogen.** ORNL's Rietveld refinements give δ-YH_x lattice parameters of **0.5200–0.5207 nm across the entire range 1.50 < x < 2.00** — a spread of 0.0007 nm, about **0.13%**. Their own conclusion: *"the dependence of the hydrogen concentration on the lattice parameter of YH_x (1.50 < x < 1.92) was negligible."*

**So for yttrium you must read hydrogen a different way. Two handles:**

**(i) Phase fraction.** At room temperature, sub-stoichiometric YH_x is a **two-phase α-Y + δ-YH₂ mixture**, and the phase fraction tracks composition linearly:

$$f_{\delta\text{-}YH_2}[\%] = 53 \times C - 1.05 \qquad (1.50 < C < 1.90)$$

where C = H/Y. Phase fractions are exactly what Rietveld refinement and Bragg-edge fitting are best at. The SOW anticipates this — it lists "areal densities of atoms **or material parameters such as lattice parameters or phase fractions**" as the fitted quantities.

**(ii) Structure factors.** Fluorite structure factors with H site occupancy *y* (H/M = 2y), using b_H = −3.739 fm:

| Reflection | F | δ-YH₂ (y=1) | YH₁.₉ (y=0.95) | YH₁.₅ (y=0.75) | bare Y |
|---|---|---|---|---|---|
| **(111)** | b_Y | **7.75** | **7.75** | **7.75** | **7.75** |
| **(200)** | b_Y − 2y·b_H | +15.23 | +14.85 | +13.36 | 7.75 |
| **(220)** | b_Y + 2y·b_H | **+0.27** | +0.65 | +2.14 | 7.75 |

Three consequences, and they carry over from the Zr case almost unchanged because b_Y (+7.75) ≈ b_Zr (+7.16):

1. **(111) is blind to hydrogen — exactly, at any H content.** The two H sublattices interfere destructively and cancel. That edge sees only the metal. It is a **free internal reference**, which is precisely what the prior art (Buitrago et al.) needed a fabricated internal standard to obtain. This is a structural property of fluorite, so it holds identically for δ-ZrH_x and δ-YH₂.
2. **(200) and (220) run in opposite directions**, because b_H is negative. Hydrogen *strengthens* (200) and *annihilates* (220). Intensity goes as F²: from YH₁.₅ to YH₁.₉ the (220) intensity changes by ~**11×**, while (200) changes by only ~1.2×.
3. **Edge-height ratios divide out the geometry.** Thickness, number density, and beam normalization are common factors in every edge, so **(200)/(220)**, or either against the hydrogen-blind **(111)**, gives occupancy *without knowing the sample thickness.* This is the independent route around the thickness/concentration degeneracy that most threatens the measurement.

**A consequence worth stating out loud, and worth checking with Vogel** *(my inference from the two sources, not a statement either paper makes):* at reactor temperature you are in the single-phase δ field; at room temperature after cooling you are in the two-phase α+δ field. **The ex-situ room-temperature state is therefore not the operating state.** If that holds, phase-fraction analysis on a cooled pellet measures the cooling path as much as the service condition — which is an argument for in-situ heated measurement, and HIPPO supports exactly that (furnace, plus resonance Doppler-broadening thermometry with no inserted sensor).

## 2.5 Mechanical consequences — why these pellets crack

Both hydrides are brittle ceramics with strongly ionic M–H bonding and few slip systems.

**YH_x (ORNL, direct-hydrided rods, RT):**
- Vickers hardness: H[GPa] = 0.89·C + 0.65 → 1.8–2.5 GPa
- Elastic modulus: E[GPa] = 48.43·C + 43.01 (~125–140 GPa for C > 1.80)
- Shear modulus: G[GPa] = 20.11·C + 16.66 (47–57 GPa)
- Poisson's ratio: 0.21–0.26, **no clear H dependence**
- Density: ρ = 4.37 − 0.0582·C g/cm³
- Fracture: **Weibull modulus m = 3.0–7.0**, mean equibiaxial failure strength **51–93 MPa**

That Weibull modulus is the headline. m ≈ 3–7 is brittle-ceramic territory — failure is flaw-dominated and statistically scattered. More hydrogen means harder, stiffer, and **more brittle** (both from the electronic structure and from the increasing δ-YH₂ fraction).

**ε-ZrH₁.₈₁ (Torres, RUS, first complete elastic tensor for ε):** E = 63 ± 2 GPa, ν = **0.43**, c₁₁ = 177 ± 6 GPa, c₄₄ = 22.06 ± 2 GPa. Compare α-Zr (Zircaloy-4): E = 98 ± 1 GPa, ν = 0.33; and δ-ZrH₁.₄₇: E = 137.8 GPa. **ε hydride is dramatically softer than both the base metal and the δ hydride** — Torres attribute the scatter in the literature (50–90 GPa) largely to microcracking.

**Where the cracks come from — two independent sources:**

1. **Volume expansion on hydriding.** Up to **20%** for α-Zr → ε hydride; ~4.5% for α-Y → δ-YH₂. ORNL found that a fast hydrogen loading rate (50 sccm) sets up a steep H concentration gradient across the workpiece, and the differential volume expansion generates enough internal stress to produce **twin structures** in YH₁.₇₀ and YH₁.₈₈. Drop to 25 sccm and the hydrogen distributes uniformly and the twinning largely disappears. **Fabrication history is written into the microstructure.**
2. **Anisotropic thermal expansion.** Torres measured, over 293–769 K, anisotropic lattice thermal strain of **+1.7% along c and −0.3% along a** for ε-ZrH₁.₈₄ — the crystal stretches one way and shrinks the other. In a polycrystal this generates large intergranular strains and microcracking on every thermal cycle.

**Why this matters for the neutron measurement, not just for engineering:** twins and preferred orientation are **texture**, and texture is the dominant systematic in Bragg-edge transmission (§5.6). The Torres SEM shows a completely banded twin microstructure in ε-ZrH₁.₈₄. These samples are textured, and you cannot fit them as randomly-oriented powders.

## 2.6 Thermal transport and the order–disorder transition

YH_x shows a **λ-type endothermic second-order transition** — a hydrogen order–disorder transition on the interstitial sublattice — that appears consistently in heat capacity, thermal diffusivity, *and* CTE. The transition temperature is inversely proportional to hydrogen content:

- YH₁.₈₈ → **648 K**
- YH₁.₅₂ → **920 K**

That is squarely inside the operating range, and it means the thermophysical properties change slope in service. CTE for YH_x runs 8–16.5 × 10⁻⁶/K over 400–973 K.

Thermal conductivity increases with H content and decreases with temperature. The mechanism is instructive: YH_x is a poor electronic conductor, so phonon (Umklapp) scattering dominates — and **hydrogen vacancies are phonon scattering centers.** Higher H/Y means fewer vacancies means less scattering means higher diffusivity. **So losing hydrogen also degrades heat removal**, on top of degrading moderation and safety feedback.

---

# 3. Hydrogen loss: the mechanisms, and what each looks like in a neutron measurement

## 3.1 Thermodynamics — the PCT surface

A hydride's equilibrium hydrogen pressure rises steeply with temperature and with H/M ratio. The consequences are counterintuitive and worth internalizing:

- **Stoichiometric is not optimal.** ORNL: pushing to YH₂.₀ "requires higher equilibrium hydrogen partial pressure to maintain that stoichiometry," is harder to fabricate (larger volume expansion), and "might result in **over-moderating** neutrons." More hydrogen is not automatically better.
- **In an open system, all the hydrogen eventually leaves.** ORNL: "When YH_x is located in an open space, hydrogen desorption will continue, and eventually all hydrogen will be lost, leaving pure yttrium behind." There is no stable operating point without containment or an imposed H₂ overpressure.
- **A flowing-H₂ overpressure works in the lab and fails in a reactor.** Under a core-wide temperature gradient at a single ambient H₂ pressure, the cold zones over-absorb and the hot zones under-absorb — you build the very non-uniformity you were trying to prevent. Plus flowing gas is an oxygen ingress path into an oxygen-hungry material.

## 3.2 Kinetics — and a mechanism that is tailor-made for imaging

ORNL's thermal desorption spectroscopy on YH_x discs (~6 mm × 0.5 mm, 0.5 K/s ramp) resolves **four stages**:

| Sample | Stage I (no desorption) | Stage II (main release) | Stage III (plateau) | Stage IV |
|---|---|---|---|---|
| YH₁.₇₆ | 300 – 936 K | 936 – 1094 K | 1094 – 1106 K | 1106 – 1126 K |
| YH₁.₈₄ | 300 – 843 K | 843 – 1028 K | 1028 – 1042 K | 1042 – 1068 K |
| YH₁.₈₇ | 300 – 813 K | 813 – 1013 K | 1013 – 1028 K | 1028 – 1053 K |

**Note the direction: higher hydrogen content means a *lower* onset temperature for significant desorption.** The most-loaded material is the least thermally stable.

**And here is the mechanism, which is the reason spatially resolved imaging is the right tool:** dehydriding is **diffusion limited**. Hydrogen leaves from the surface first, building a concentration gradient inward. The near-surface region eventually depletes to the point where **α-Y precipitates out**, and the process becomes a **two-phase moving boundary** — an α-Y rim eating inward into a δ-YH₂ core.

> **That is a spatial structure, not a scalar.** A mass measurement returns one number and cannot distinguish "lost 5% uniformly" from "grew a 200 µm fully-dehydrided rim." Those two states have entirely different remaining lifetimes and entirely different neutronic behaviour. **Only a spatially resolved phase map tells them apart.**

**A genuine Y/Zr contrast worth knowing:** YH_x desorption flux depends on both temperature *and* hydrogen concentration. δ-ZrH_x shows **zero-order desorption kinetics with no discernible concentration dependence.** The two materials do not lose hydrogen the same way.

## 3.3 What each mechanism looks like in the data

| Mechanism | Signature in a spatially resolved phase/composition map |
|---|---|
| **Uniform decomposition** (overheat) | H content drops everywhere at once; in Zr, edges *merge* as ε → ε+δ → δ; in Y, δ fraction falls and α-Y appears uniformly |
| **Surface-limited desorption** | **α-rim on a hydride core.** Sharp moving boundary, radially symmetric. In Zr: α-Zr edges appear at ~5.60 Å that were not there before |
| **Soret redistribution** | H **gradient across the pellet with total H conserved.** In Zr: ε on the cool face, δ on the hot face — *a phase boundary inside one intact pellet.* In Y: a δ/α phase-fraction gradient |
| **Fabrication non-uniformity** | Correlated with twin/texture structure, not with the thermal geometry. Present in the unexposed control |

**That last column is the deliverable.** And the SOW's sample set is designed to separate exactly these: five pellets with different thermal history (labelled A, C, D, E, F) plus an **unexposed control** — the control isolates fabrication artifacts from service-induced change.

---

# 4. Claddings

## 4.1 Why cladding is the engineering answer

Given §3.1 — an unclad hydride in an open system loses all its hydrogen, and gas overpressure fails in a real core — the practical mitigation is a physical barrier. ORNL puts it directly: *"A more practical method to mitigate hydrogen loss is to develop cladding protection as a barrier."*

## 4.2 The down-selection criteria and the state of the art

ORNL's stated criteria for cladding material selection: **hydrogen permeability, neutronic properties, chemical compatibility with the hydride, radiation stability, and fabricability.** Those five pull against each other, which is why this is unsolved.

| Approach | Status |
|---|---|
| **SS316L** | ORNL/TCR near-term choice for YH_x — permeability "sufficiently low for the operating regime of the TCR," with little impact on moderator hydrogen content. Explicitly a stopgap: *"better cladding materials with lower neutron absorption cross sections and lower permeability to hydrogen are necessary for long-term use"* |
| **TZM (Ti-Zr-Mo) canning** | DOE Microreactor Program baseline for YH₂₋ₓ. Acceptable retention to **~700 °C**; needs improvement above that and for power transients |
| **ANL Advanced Moderator Module** | YH₂₋ₓ inside a flexible **Nb liner** carrying an ANL-developed H₂ barrier coating; refractory metals + CMCs + coatings |
| **Al₂O₃–Cr₂O₃ sol-gel coating** | Dip-coat, calcine 600–800 °C. **>90% permeation reduction at 900 °C**, survives thermal cycling |
| **Bulk barriers** | 500 µm pure **W** cladding; Al₂O₃ coating on 316 SS — reported as most effective |
| **Mo** | Used for the HFIR irradiation capsules specifically for high-temperature performance and hydrogen leakage resistance |

**The neutronic cost is the crux.** Every cladding atom is parasitic absorption sitting directly in the thermal flux next to the moderator. SS316L has a large absorption cross section (Fe, Cr, Ni). W is worse. Nb and Mo are better but not free. **You are trading neutron economy for hydrogen retention — and that is the same currency you already spent choosing Y over Zr.** A cladding good enough to let YH_x run at 1000 °C, but absorbing enough to cancel the reactivity that the extra hydrogen bought, is a net loss. That is the real design problem.

## 4.3 One ambiguity in "claddings" — flag for Thor

"YH_x and ZrH_x claddings" admits two readings, and both are live in these sources:

1. **Cladding *for* hydride moderators** — the enclosure/permeation-barrier problem above (ORNL, ANL, TCR). The dominant reading, and where the hydrogen-loss framing points.
2. **Hydrogen in zirconium-alloy cladding** — Zircaloy is *the* cladding alloy, and hydrogen pickup and hydride precipitation in it is a classic fuel-degradation problem. This reading is also directly supported: **Torres et al. hydrided Zircaloy-4** (not pure Zr) to make their ε-hydride, and the SOW's own reference [5] is **Buitrago et al., "Determination of very low concentrations of hydrogen in zirconium alloys by neutron imaging"** — the paper that sets the 5 wt ppm benchmark. A companion LANL paper (Parkison, Tunes, Nizolek, Saleh, Hosemann, **Kohnert**, arXiv:2305.02249) fabricates bulk δ-ZrH moderator *from Zircaloy-4*.

They are not really separate problems — the group makes hydride moderators out of cladding alloy, and the measurement technique came out of the cladding-hydrogen literature. But **which one is Thor's task changes what to look for**: a thin barrier layer and interface at the surface (reading 1) versus a bulk hydrogen/hydride distribution (reading 2). **Worth one question to Vogel or Kohnert.**

---

# 5. The measurement

## 5.1 Why neutrons, and why nothing else works

**Hydrogen is invisible to X-rays and brilliant to neutrons.** X-rays scatter off electrons; H has one, Zr has 40, Y has 39. In a hydride, hydrogen contributes ~2% of the electron density — it is noise. The SOW states it flatly: *"hydrogen atoms in the presence of Zr or Y are essentially invisible to X-rays for CT or diffraction measurements."*

Neutrons scatter off nuclei, and hydrogen's cross section is anomalous: **82 barns bound**, against 6.46 b for Zr and 7.7 b for Y. The SOW: *"The interaction probabilities of hydrogen atoms for neutrons are approximately ten times stronger than for the host metals Y and Zr."*

The reason is nuclear spin. The n–p system has two spin channels with wildly different scattering lengths (b₊ = +10.85 fm, b₋ = −47.5 fm). Their spin-average is small (b_coh = −3.739 fm) but their *variance* is enormous — which shows up as an **80.27 barn incoherent** cross section. This pays twice: the huge incoherent baseline gives sensitivity to total H areal density regardless of crystallinity, while the negative *coherent* length flips the sign of hydrogen's contribution to structure factors, which is what makes the (111)/(200)/(220) trick in §2.4 work.

And neutrons penetrate centimetres of metal, so you measure an **intact pellet**, non-destructively.

## 5.2 Diffraction and transmission — two views of the same physics

| | **Neutron diffraction** (scattered) | **Energy-resolved transmission / Bragg-edge imaging** |
|---|---|---|
| Measures | Where scattered neutrons *go* | What is *missing* from the through-beam |
| Gives | Phase composition, lattice parameters, texture/ODF, dislocation density, site occupancy — via Rietveld | Spatially resolved: per-pixel transmission spectrum → phase, thickness, areal density, orientation |
| Resolution | Excellent in *d*, but **volume-averaged over the sampled gauge** | Excellent spatially (µm–mm), coarser spectrally |
| Blind to | Where in the sample it came from | Fine minor phases, low-symmetry detail, anything below crystallographic contrast |

**They are duals.** A Bragg edge is what a diffraction peak looks like from behind: at λ = 2d_hkl, that family can no longer satisfy Bragg's law, scattering out of the beam abruptly stops, and transmission jumps up. Hirsh et al. show this literally — overlaying the HIPPO diffraction pattern (plotted on λ = 2d) on the transmission spectrum, *"the positions and intensities of the diffraction peaks align well with the positions and heights of the Bragg edges."*

**Why running both simultaneously is not a convenience but a requirement here** — three reasons, all from Hirsh et al.:
1. **Transmission needs the texture.** Fitting a textured transmission spectrum blind is under-determined. Get the ODF from diffraction, fix those weights, fit transmission. That is the workflow they demonstrate.
2. **At elevated temperature, you must confirm the phase did not change.** Their words: combining the two *"enables direct confirmation of the anticipated crystallographic phase, ensuring the material remains stable and does not decompose during characterization."* **That is the hydrogen-loss problem stated as a metrology requirement.** Heating a hydride to measure it can destroy the thing you are measuring.
3. **Imaging tells diffraction where to look.** They name the case explicitly: imaging *"can provide critical insights into the spatial homogeneity of hydrogen uptake and release during in-situ diffraction investigation of the synthesis or decomposition of hydrogen-bearing materials."* Diffraction returns a volume average; if hydrogen is leaving as a moving rim (§3.2), the average is a fiction.

## 5.3 The instrument — HIPPO + LumaCam at LANSCE

**HIPPO** (High-Pressure/Preferred-Orientation), **Flight Path 4**, Lujan Neutron Scattering Center, LANSCE.

- FP4 views a high-intensity **water moderator** on the lower tier of the TMRS; flux ~10⁷ n/cm²/s, peaked thermal with a tail into epithermal
- **1200 He-3 tubes** on 45 panels in five rings at nominal 2θ = **40, 60, 90, 120, 140°**, covering ~20% of 4π
- Robotic sample changer arm holding orientation and rotating about any axis → tomography-capable
- Beam spot 10 mm diameter; collimator entrance 1 cm, length 30 cm, ~130 cm from sample → **L/D ≈ 130**

**LumaCam** (event-mode imaging camera), integrated onto HIPPO, positioned **10 cm downstream of the sample**:

- **⁶LiF-ZnO:Zn scintillator**, 450 µm thick, 40 × 40 mm — chosen over the brighter ⁶LiF-ZnS:Ag for timing (1 µs decay vs 5/80 µs components)
- Dual-stage image intensifier, gain ~10⁶ → **TimePix3**, single 256 × 256 sensor, 55 µm pitch
- **Field of view ≈ 14 × 14 mm²**
- Time-of-arrival resolution 1.5625 ns; T₀ from the spallation trigger via TDC
- EMPIR event reconstruction: two-stage clustering + pulse-shape discrimination for gamma rejection

**Why HIPPO's *short* flight path is an advantage here.** At ~9 m it is much shorter than IMAT@ISIS (20 m) or CSNS (35 m), and it runs with **no curved guides and no chopper**. So a single beam pulse delivers thermal *and* epithermal neutrons — which means **Bragg-edge imaging, neutron resonance imaging, and diffraction all in parallel.** Resonance imaging brings a bonus for hot experiments: **Doppler broadening of absorption resonances measures the sample temperature directly, with no inserted thermocouple.**

## 5.4 The numbers HANDBOOK.md said you were blocked on

Calibrated by Hirsh et al. against a 200 µm Ta foil (resonances) and a 30 mm Al can of α-Fe powder (Bragg edges):

| Quantity | Value |
|---|---|
| **Flight path, moderator → event camera** | **9.014 ± 0.001 m** |
| **t₀ (delay vs accelerator trigger)** | **0.10 ± 0.01 µs** |
| Moderator → sample (nominal HIPPO) | 8.91 m (camera 10 cm behind) |
| **TOF binning, Bragg-edge mode** | 512 × 512 px, **10 µs** |
| TOF binning, resonance mode | 512 × 512 px, 250 ns |
| Typical exposure | 10–30 min per image/orientation |
| Smallest usable spectral ROI | **16 × 16 px** |
| **Instrumental background** | **~2.5%** of total transmission (vs ~20% on ERNI/FP5) |

Conversions: λ[Å] = 3956 / v[m/s]; E[meV] = 81.81 / λ[Å]²

**That background number deserves attention.** The SOW names energy-dependent, sample-induced background as *"a crucial part of this problem"* and the top project risk. HIPPO+LumaCam's 2.5% instrumental background is ~8× better than the dedicated imaging beamline, attributed to the camera's gamma rejection. The remaining background will be sample-induced scatter — which is exactly what the SOW proposes to attack by iterating per-pixel background estimates from observed attenuation.

## 5.5 The analysis chain

Transmission is modelled as Beer–Lambert with an additive background and an instrument-convolved cross section:

$$T = \frac{I}{I_0} = e^{-n\sigma'(\lambda)d}\cdot(1-B) + B, \qquad B = B_0 + B_1\lambda + \frac{B_2}{\lambda}, \qquad \sigma'(\lambda) = R(\lambda) * \sigma(\lambda)$$

with *n* = atomic number density (atoms/barn-cm), *d* = mean thickness over the ROI (cm). For resonances the background switches form: B = B₀ + B₁/√E + B₂√E.

| Step | Tool |
|---|---|
| Reduce 3D TIFF stack (slices = TOF bins) → per-region 1D spectra | **save_roi** (`--tilt` straightens a tilted symmetry axis — built for cylindrical pellets) |
| Simulate σ(λ) from crystal structure, with/without texture | **NCrystal** Python API |
| Fit | **LMFIT** — and **nbragg**, which wraps exactly this (NCrystal σ under an lmfit `Model`) |
| Instrument response R(λ) for Bragg edges | **Jorgensen** back-to-back-exponential model — nbragg's default. Calibrated params (from ERNI/FP5, same moderator): v₁=6.8, v₂=4.3, w₁=0.54, t₁=5.28 µs, T₁=3.48 µs, t₂=2.27 µs, T₂=5.1 µs |
| Texture: diffraction → ODF | **MAUD** (fits wavelength-resolved peak intensities across all detector rings) |
| Pole figures / orientation components | **MTEX** |
| Resonance fitting (isotopics, thickness, temperature) | **SAMMY**, via **PLEIADES** Python interface |
| Rietveld on the diffraction side | **GSAS** / **gsaslanguage** (Vogel's own scripting layer) |

**The intellectual foundation is Vogel's own PhD thesis** — *"A Rietveld-approach for the analysis of neutron time-of-flight transmission data,"* Kiel, 2000, cited as ref [4] of the SOW. The whole method is: treat a transmission spectrum the way you treat a diffraction pattern, and refine a structural model against it. nbragg is that idea, thirty years on, in Python.

**And at 50k+ pixels, nbragg's killer feature is `GroupedFitResult.fit(data, query="redchi > 2")`** — selectively refit only the pixels that fitted badly, warm-started from the global solution.

## 5.6 The systematics that will actually bite

Ranked by how much of the summer they can eat.

**1. Texture — the big one.** Hirsh et al. needed **13 orientation components** to fit a large-grain steel, and for the depleted-uranium cylinder the fit drove mosaicity to **η = 50 ± 1.5°**, which is *NCrystal's upper limit for that parameter*. The hydride samples are textured for two independent reasons (§2.5): twin structures from fast hydriding, and anisotropic-thermal-expansion damage. **Mitigation: take the ODF from the simultaneous diffraction, fix the orientation weights, then fit transmission.** That is the demonstrated workflow and it is available for free because both modalities run at once.

**2. The thickness/concentration degeneracy.** The exponent is n·σ·d — you cannot separate how much material from how much hydrogen without an extra constraint. Three independent routes, and you should use more than one:
   - the SOW's milestone #2: **cylindrical-symmetry geometry constraint** (a central ray sees more material than a rim ray, and you know the pellet diameter)
   - **edge-height ratios** against the hydrogen-blind (111) — §2.4, and it needs no geometry at all
   - the simultaneous **diffraction** lattice parameters / phase fractions on the identical volume

**3. Extinction.** Real, live, and being actively worked in this exact group: Xu, DiJulio, Márquez Damián, **Vogel**, Long, **Hirsh**, Kittelmann, Kuksenko, Muhrer, *"Impact of extinction effects on neutron transmission in solid beryllium metal,"* Acta/Applied Crystallography 58(6), 2025 — ref [3] of the SOW. Large or highly perfect grains scatter multiply within a single crystallite and the simple kinematic cross section overestimates attenuation. nbragg exposes `ext_*` parameters and the NEUWAVE extinction exercise teaches the Sabine model.

**4. Sample-induced background.** The SOW's named top risk. §5.4.

**5. Statistics.** ~10 minutes per orientation gave Hirsh et al. enough for 16×16 pixel ROIs but *"insufficient counting statistics to detect spatial changes in lattice parameters or texture"* on the uranium sample. Spatial resolution and concentration resolution trade directly against count time — which is precisely why estimating that trade is milestone #4.

**6. Temperature/composition confounding in the lattice parameter.** §2.2. Remove thermal expansion before reading hydrogen content.

---

# 6. The two papers Thor flagged

## 6.1 Mehta, Rehn & Olsson (2024) — *"Evaluation of δ-Phase ZrH₁.₄ to ZrH₁.₇ Thermal Neutron Scattering Laws Using Ab Initio Molecular Dynamics Simulations,"* J. Nucl. Eng. 5, 330–346. doi:10.3390/jne5030022

LANL (Nuclear Engineering & Nonproliferation, and Computational Physics) + Malmö/Lund. **This is the theory side — what the neutron cross section *should* be.**

**Method:** AIMD in VASP (PBE-GGA, GW PAW, 525 eV static / 350 eV MD, 4×4×4 fcc supercell, 64 Zr + up to 109 H) → velocity autocorrelation → Fourier transform → phonon DOS → TSL S(α,β) via the phonon expansion. Random H occupancy of tetrahedral sites, 15 relaxed configurations per composition, lowest-energy near-cubic one selected. **NJOY+NCrystal** (the ESS toolkit) converts to ACE for MCNP.

**Findings that matter to Thor:**

1. **The reactor-relevant phase is δ, and the reactor-relevant range is sub-stoichiometric.** δ-ZrH₂₋ₓ, x = 0.3–0.6, stable for 1.56 ≤ H/Zr ≤ 1.64. For 800–1000 K the whole ZrH₁.₄–ZrH₁.₇ range is single-phase δ. **This corrects HANDBOOK.md's "probably ε, and H = 2/3, Zr = 1/3" framing for the reactor case.**
2. **Phase matters more than stoichiometry.** Varying hydrogen vacancy concentration and site (ZrH₁.₄ vs ZrH₁.₇) changed the TSLs *less* than the ε→δ lattice transformation did. **Implication: nail the phase first; stoichiometry precision is second-order.** That is a direct argument for prioritising phase mapping.
3. **ENDF/B-VIII.0's ZrH TSLs have no Bragg edges.** Both Zr-in-ZrH and H-in-ZrH were generated under the incoherent approximation via NJOY's LEAPR. Coherent elastic scattering from the zirconium sublattice — i.e. the Bragg edges — was neglected. **Bragg edges are exactly what this project measures.** So the standard evaluated data is structurally unable to describe the measurement.
4. **YH_x is more sensitive to sub-stoichiometry than ZrH_x.** Their words: the TSL "varies due to the vacancy defects but not as significantly as in other metal–hydrogen systems such as YH_x." **Good news for the Y thread — the neutron signal carries more composition information in yttrium.** (Their ref [60] is the Y companion paper; see §8.)
5. **NJOY's THERMR module smears the optical phonon.** ACE files regenerate the H optical oscillation at much lower resolution than NCrystal alone. First noted by Zerkle & Holmes — for yttrium hydride. **If you go through ACE/MCNP you lose optical-phonon detail; NCrystal direct keeps it.**
6. **MCNP permits only one TSL per nuclide per material** — so a genuinely two-phase system (α + δ, or δ + ε) cannot be represented natively. Relevant given §2.3 and §3.2.
7. EXFOR validation data, already unit-converted: **Schmidt 1967** (EXFOR 23424) and **Whittemore 1964** (14174/002,003).

## 6.2 Torres et al. (2025) — *"High-temperature structure, elasticity, and thermal expansion of ε-ZrH₁.₈,"* J. Nucl. Mater. 603, 155437. doi:10.1016/j.jnucmat.2024.155437

LANL + ORNL. **Sven Vogel and Caitlin Kohnert are co-authors — this is the group's own paper**, and it is the experimental counterpart to Mehta. Funded by **NASA STMD, Space Nuclear Propulsion**. Measured at **LANSCE** (and HFIR).

**Why it is directly on point:**

- **Samples are hydrided Zircaloy-4** — nuclear-grade, low-Hf zirconium *alloy*, i.e. cladding material — not pure Zr. ZrH₁.₈₀–₁.₈₄, x determined by mass gain (±0.02).
- **Measured on HIPPO** by time-of-flight neutron powder diffraction, Rietveld-refined in **GSAS** via **gsaslanguage** (Vogel's own scripting layer). This is the same instrument and the same analysis stack Thor will use.
- Complemented by dilatometry (314–1324 K) and resonant ultrasound spectroscopy.

**Findings that matter:**

1. **The lattice-parameter → H content calibration for ε.** Parabolic fits a(x), c(x), c/a(x) over 1.7 ≤ x ≤ 2.0 in fct geometry (their Table 2). **This is the decoder ring HANDBOOK.md wanted from Zuzek — but measured, recent, and by this group.**
2. **The temperature dependence, separately** (Table 3): ZrH₁.₈₄ from 294 → 769 K, a: 4.9712 → 4.9555 Å, c: 4.5115 → 4.5912 Å, c/a: 0.9075 → 0.9265. **Both H content and temperature move the lattice — you need both calibrations to invert one measurement.**
3. **Where the hydrogen goes, thermally.** ε stable in air to at least 770 K. At 769 K a small amount (<5 wt%) of **δ appears**. Dilatometry inflects ~830 K. Strong contraction at **950–970 K** = hydride decomposition back to metal. Moore & Young saw δ at ~955 K for ZrH₁.₈₁. **That is the ε → ε+δ → δ → α+H₂ hydrogen-loss path, with temperatures attached.**
4. **First complete elastic tensor for ε-phase** by RUS: E = 63 ± 2 GPa, ν = 0.43, c₁₁ = 177 ± 6, c₄₄ = 22.06 ± 2 GPa. ε is much softer than α-Zr (98 GPa) and δ (127–138 GPa).
5. **CTE ~6–7 ppm/K, about 30% lower than hydrides made from pure Zr** — alloying, hydrogen content, or microstructure; they could not separate which. **A Zircaloy hydride is not a pure-Zr hydride, and the literature values do not transfer.**
6. **Anisotropic thermal strain +1.7% (c) / −0.3% (a)** → large intergranular strain → microcracking. Confirmed by SEM: completely banded twin microstructure, visible microcracks. **This is the texture problem (§5.6) documented in the exact material.**
7. High-temperature RUS failed above ~350 K — acoustic dissipation from twin-boundary mobility (Q⁻¹ rises exponentially, reversible on cooling). **A materials-characterization technique defeated by the same twins that will complicate the neutron fit.**

**One incidental detail worth noticing:** their XRD found a minor **Y₂O₃** peak, attributed to yttrium oxide residue from sample preparation. Yttrium is already in this lab's sample stream.

---

# 7. Corrections to HANDBOOK.md

*Kept in the same spirit as its own §8 — the errors are instructive.*

1. **Dropping yttrium was the biggest error**, and it was avoidable: the SOW's own problem statement opens with *"Hydrides of yttrium or zirconium."* **Lesson: read the funded statement of work for scope, not the tooling links for scope.** The resource dump was all NCrystal/ZrH₂ because that is the *software* thread, not the *science* thread.
2. **"You cannot convert TOF→λ without L and t₀"** — true, but they were published, by the PI, in a paper cited *in the proposal Thor already had*. **Lesson: chase the proposal's own reference list before declaring a blocker.**
3. **Treating diffraction as milestone-3 validation.** It is a simultaneous co-modality on the same instrument, and transmission analysis practically *depends* on it for texture. **Lesson: "compare with diffraction" in a proposal can mean "the same run," not "a separate experiment."**
4. **"ε is probably your phase" was half right.** The pellets are ε-ish; the *reactor regime* is δ; and the transition between them is the measurement. Not a preliminary to settle — plausibly the answer.
5. **The 137 meV figure** is the ENDF Einstein-oscillator parameter for H-in-ZrH. Ab initio and INS put the actual DOS peak at ~140–145 meV. Both numbers are correct in their own context; do not treat them as the same claim.
6. **Trellue et al. is JOM 2021, 73(11), 3513–3518** — not 2023. (Mehta's reference list is right; a search result mis-stated the year.)
7. **Still-open caveats from HANDBOOK.md §8 that this round did not resolve:** the Acta Astronautica full text remains unread; §3.4's Zr–H lattice parameters remain from-memory (though Torres Table 2/3 now supersedes them for ε); γ-ZrH's equilibrium status is still genuinely contested.

---

# 8. What to acquire, and what to ask

## 8.1 Papers to get — ranked

| # | Paper | Why |
|---|---|---|
| **1** | **Mehta, Cooper, Wilkerson, Kotlyar, Rao, Vogel**, *"Evaluation of Yttrium Hydride (δ-YH₂₋ₓ) Thermal Neutron Scattering Laws and Thermophysical Properties,"* Nucl. Sci. Eng. **195**(6), 563–577 (2021). doi:10.1080/00295639.2020.1851632 | **The Y counterpart to the ZrH TSL paper — and Vogel is a co-author.** The one paper that most directly fills the Y gap |
| **2** | **Hirsh, Leong, Losko, Wolfertz, Savage, Jäger, Rakovan, Wall, Long, Vogel**, *"Energy-resolved neutron imaging and diffraction including grain orientation mapping using event camera technology,"* Sci. Rep. **15**, 12901 (2025). LA-UR-24-28723 | **The instrument paper. Open access.** Already read for this document, but Thor should read it cover to cover — it is the method |
| **3** | **Vogel, S.**, *"A Rietveld-approach for the analysis of neutron time-of-flight transmission data,"* PhD thesis, Kiel, 2000 | The intellectual foundation of the entire technique, by the PI |
| **4** | **Buitrago et al.**, *"Determination of very low concentrations of hydrogen in zirconium alloys by neutron imaging,"* J. Nucl. Mater. **503**, 98–109 (2018) | The 5 wt ppm / 10 wt ppm benchmark ERNI is trying to match **without** an internal standard. Also the cladding-hydrogen link |
| **5** | **Xu, DiJulio, Márquez Damián, Vogel, Long, Hirsh, Kittelmann, Kuksenko, Muhrer**, *"Impact of extinction effects on neutron transmission in solid beryllium metal,"* Appl. Cryst. **58**(6) (2025) | Extinction, by this group, this year. Systematic #3 |
| **6** | **Trellue, Long, Luther, Carver, Mehta**, *"Effects of Hydrogen Redistribution at High Temperatures in Yttrium Hydride Moderator Material,"* JOM **73**(11), 3513–3518 (2021) | Hydrogen redistribution in YH_x, measured by neutron imaging. The Y version of Thor's exact problem |
| **7** | **Hu, Wang, Linton, Le Coq, Terrani**, *Handbook on the Material Properties of Yttrium Hydride for High-Temperature Moderator Applications,* ORNL/TM-2021/2052 (2021) | **Free PDF, already used throughout this document.** The YH_x property database |
| **8** | **Parkison, Tunes, Nizolek, Saleh, Hosemann, Kohnert**, *"Fabrication of bulk delta-phase zirconium hydride from Zircaloy-4 for use as moderators in microreactors,"* arXiv:2305.02249 | Free. Kohnert co-author. The Zircaloy → δ-ZrH fabrication route |
| 9 | Mehta, Patterson, Wagner, *MARVEL Fuel Fabrication Strategy*, INL/RPT-22-66550 | The other hydride-moderated program |
| 10 | Mehta, Kotlyar, Rao, *"Capturing multiphysics effects in hydride moderated microreactors using MARM,"* Ann. Nucl. Energy **172**, 109067 (2022) | The coupled H-migration ↔ neutronics feedback loop, modelled |

## 8.2 Questions for Vogel / Kohnert — revised

The old list is largely superseded. What is actually still open:

1. **Y or Zr — or both?** The SOW says "yttrium or zirconium," but the five characterized pellets in Figure 1 are ZrH₂. **Is the Y work a second dataset, a follow-on, or scope Thor is expected to open?** This is the top question; it determines everything below.
2. **Which reading of "claddings"?** Barrier/enclosure for hydride moderators, or hydrogen in Zircaloy cladding? (§4.3) They are adjacent but the analysis differs.
3. **What are the five pellets' thermal histories?** Samples A, C, D, E, F plus the unexposed control. Temperatures, durations, atmosphere, and whether any were held under a *gradient* (Soret) rather than isothermally. **Without this the phase maps have nothing to be interpreted against.**
4. **Phase of the as-received pellets — ε, δ, or mixed?** Still worth asking, but now with the sharper framing: given Mehta's result that phase dominates the TSL over stoichiometry, and given they may have moved through the ε+δ field during heat treatment, the phase is a *result*, not an input.
5. **Was the diffraction collected simultaneously with the 2,500 radiographs?** The SOW says lattice parameters were "measured simultaneously... viewing the exact same volume." Confirm — and get the diffraction data alongside the imaging data, because the texture workflow (§5.6) needs it.
6. **Is there a heated / in-situ dataset**, or is everything ex-situ at room temperature? (§2.4 — the RT state may not be the operating state.)
7. **Detector/binning actually used for *this* dataset** — Hirsh et al. give 512×512 at 10 µs, but confirm for the pellet data.
8. Repo access to `SRP_interns2026` as `hsinghind13`; what does "SRP" stand for? *(unchanged, still open)*

## 8.3 First moves — revised

1. **Read Hirsh et al. 2025 end to end.** It is the method, the instrument, and the calibration, and it is open access.
2. **Get the Mehta Y TSL paper** (NSE 195(6)) — via UTK access.
3. **Do the `TSL_School/openmc/Examples/Transmission` notebook**, then `ncrystal2_advanced_01/02/03`. *(unchanged — still the right order)*
4. **Build the material models.** NCrystal ships no ZrH₂, no ZrH, and **no YH₂ either** — so both materials must be composed from CIF + VDOS and validated against EXFOR before fitting anything real. δ-YH₂ is Fm-3m fluorite, so it is structurally the *easier* of the two.
5. **Reproduce the Hirsh calibration** on the Ta foil and Fe powder if that data is available — it validates the whole chain (flight path, t₀, response function, background model) before touching the science data.
6. **Ask questions 1 and 3 above in one message.** Both are blocking and neither takes anyone long to answer.
7. Apply for NCRC Level 1 naming Sockeye — longest lead time of anything. *(unchanged)*
8. `export NCRYSTAL_ONLINEDB_CACHEDIR=...` *(unchanged)*

---

# 9. The one-paragraph version

Microreactors on HALEU and reactors you can launch both need to be small, so both need thermal neutrons, so both need hydrogen held solid at 800–1000 K — and hydrogen is not merely the best moderator available but the best one possible, because it alone shares the neutron's mass. Zirconium hydride is the classical answer and yttrium hydride the high-temperature one: YH_x still holds hydrogen at 1350 °C where ZrH_x is empty by 1100 °C, and pays for it with ~7× the parasitic neutron absorption. Hydrogen leaves either way — by dissociation, by permeation through the enclosure, or by migrating down the very temperature gradient the reactor creates — and that last mechanism loses nothing from the system while quietly restructuring the pellet, degrading moderation, heat transport, and the 137 meV upscattering that gives the reactor its inherent safety, all at once. Claddings — TZM, Nb liners, alumina–chromia coatings, SS316L for now — are the engineering answer, and they buy retention with the same neutron economy you already spent choosing yttrium. Hydrogen is invisible to X-rays and brilliant to neutrons, by an accident of nuclear spin that makes its cross-section enormous and its coherent scattering length negative; so you fly time-of-flight neutrons through intact pellets on HIPPO at LANSCE, collect diffraction and per-pixel transmission spectra from the same volume in the same run, take the texture from the diffraction and hand it to the transmission fit, and read hydrogen out of the Bragg-edge structure, the incoherent baseline, and — for yttrium, whose lattice parameter is nearly blind to composition — the α/δ phase fraction. What you get that no bulk measurement and no criticality benchmark can give is *where the hydrogen went*: a rim, a gradient, or a fabrication artifact, mapped non-destructively inside a pellet that is still whole.
