# ZrH₂ / NEP Internship Handbook

> ## ⚠️ PARTIALLY SUPERSEDED — see `HANDBOOK-II.md` (2026-08-07)
>
> This file was assembled from the resource dump alone, before the statement of work was read closely. Three things in it are wrong or incomplete:
>
> 1. **Scope.** The SOW's first sentence names **"hydrides of yttrium or zirconium."** This handbook drops yttrium entirely. The Y–H system behaves *differently* in the one way that matters most: δ-YH_x's lattice parameter is nearly independent of hydrogen content (~0.13% across 1.50 < H/Y < 2.00), so hydrogen must be read from **α/δ phase fraction** and **edge-height ratios** instead. HANDBOOK-II §2.3–2.4.
> 2. **The instrument was never identified.** It is **HIPPO + LumaCam at LANSCE**, running diffraction and energy-resolved imaging *simultaneously on the same volume*. §4.4's "you cannot convert TOF→λ without L and t₀" is resolved: **L = 9.014 ± 0.001 m, t₀ = 0.10 ± 0.01 µs**, published by the PI in a paper cited *in the proposal*. HANDBOOK-II §5.3–5.4.
> 3. **Diffraction is not milestone-3 validation.** It is a co-equal modality, and the transmission fit practically depends on it for texture. HANDBOOK-II §5.2.
>
> Also revised: the reactor-relevant ZrH phase is **δ**, not ε (§3.4's "probably your pellets" is half right); phase matters more than stoichiometry for the TSL; and Torres et al. now supersede §3.4's from-memory lattice parameters for ε. Full list in **HANDBOOK-II §7**.
>
> **Still good in this file:** the ZrH₂ transmission physics, the δ↔ε edge-splitting analysis (§3.4), the fluorite structure factors (§3.5 — they transfer to δ-YH₂ almost unchanged), the NCrystal/nbragg/save_roi stack (§5), the NEP thread (§6), and the corrections log (§8).

**Assembled 2026-07-16** from the resource dump (LANL + ANL/INL) and the physics worked through alongside it.
Covers both threads: energy-resolved neutron imaging of ZrH₂ moderators (LANL), and the 20 kWe NEP reactor design (ANL/INL).

**In this folder:**
- `HANDBOOK-II.md` — **current context. Read first.**
- `Vogel_IMS_IR_ERNIAndTheModerators_Submit (1).pdf` — **your statement of work.** Four pages; read it directly.
- `jne-05-00022.pdf` — Mehta, Rehn & Olsson 2024, δ-ZrH TSLs (theory side).
- `1-s2.0-S0022311524005373-main.pdf` — Torres et al. 2025, ε-ZrH₁.₈ from Zircaloy-4 on HIPPO (**Vogel + Kohnert co-authors**).
- `Design and Fabrication of the Brayton Rotating Unit.pdf` — NASA CR-1870, 390 pp. NEP thread only. Table 2 (PDF p.30) is the one that matters.
- `HANDBOOK.md` — this file.

---

# 0. The arc — the whole project in one thread

> A reactor you can launch has to be **small**. Making it small means **slowing neutrons down**. Slowing neutrons down means **hydrogen**. Hydrogen **won't hold still when it's hot**. And neutrons are the only practical way to **see where the hydrogen went**.

**You're using neutrons to find the hydrogen that makes the reactor that flies.**

- **LANL thread** = the "see where it went" step.
- **ANL/INL thread** = the "reactor that flies" step.

Same physical object — a hydride moderator pellet — approached from two ends. They are not two internships; they're two views of one problem.

---

# 1. Quick reference

## 1.1 People

| Who | Where | Role |
|---|---|---|
| **Sven Vogel** (sven@lanl.gov) | LANL MST-8 | PI of the ERNI proposal; neutron physics |
| **Caitlin Kohnert** | LANL | POC for moderators, microreactor program |
| Brendt Wohlberg | LANL | Computational imaging; leads Python/data (0.08 FTE) |
| Elizabeth Kardoulaki | LANL | Hydride characterization coordination |
| Charles Bouman | Purdue | Radiographic/tomographic methods (unfunded collaborator) |
| **Siddharth Sivakumar** | ANL/INL | 20 kWe NEP thermal power / efficiency |
| **RWillat** | ? | Owns `SRP_interns2026`; reviews commits |
| Nicolas Stauff (nstauff@anl.gov), Yinbin Miao (ymiao@anl.gov) | ANL | MRAD / HP-MR contacts |

## 1.2 Neutron & material constants

| Quantity | Value |
|---|---|
| Fission neutron birth energy | ~2 MeV |
| Thermal neutron energy / speed | 0.0253 eV / **2200 m/s** |
| U-235 fission xs, thermal vs 1 MeV | **585 b** vs 1.2 b (**~500×**) |
| σ_scatter H (**bound**) | **82.02 b** (coh 1.76 + **inc 80.27**) |
| σ_scatter H (**free**, fast) | 20.5 b — bound = 4× free |
| σ_scatter Zr | 6.46 b |
| σ_absorb H / Zr | 0.3326 b / 0.185 b |
| b_coh: **H** / Zr | **−3.739 fm** (negative!) / +7.16 fm |
| H spin channels | b₊ = +10.85 fm, b₋ = **−47.5 fm** |
| H number density in ZrH₂ | **7.2×10²² cm⁻³** (liquid water: 6.7×10²²) |
| ZrH₂ density | ~5.6 g/cm³ |
| H optical (Einstein) mode in ZrH | **~137 meV** |
| kT at 300 K / 1000 K | 25.9 meV / 86.2 meV |
| Conversions | λ[Å] = 3956/v[m/s] ; E[meV] = 81.81/λ[Å]² |

## 1.3 Moderation table

| Nucleus | A | α = ((A−1)/(A+1))² | Max loss/collision | ξ | **Collisions to thermalize** |
|---|:--:|:--:|:--:|:--:|:--:|
| **Hydrogen** | 1 | **0** | **100%** | **1.000** | **~18** |
| Deuterium | 2 | 0.111 | 89% | 0.725 | ~25 |
| Carbon | 12 | 0.716 | 28% | 0.158 | ~115 |
| **Zirconium** | 91 | 0.957 | **4.3%** | 0.022 | **~835** |
| Uranium-238 | 238 | 0.983 | 1.7% | 0.0084 | ~2170 |

## 1.4 Links

| Resource | URL | Verdict |
|---|---|---|
| nbragg | github.com/TsvikiHirsh/nbragg (**branch `master`**) | **Essential** |
| save_roi | github.com/TsvikiHirsh/save_roi | **Essential** |
| NCrystal | github.com/mctools/ncrystal | **Essential** |
| ncrystal-notebooks | github.com/mctools/ncrystal-notebooks | Priority: advanced 01/02/03 |
| TSL_School | github.com/highness-eu/TSL_School | **Do `Transmission`**, not TRIGA |
| NEUWAVE deck | indico.ess.eu/event/3439/... | Orienting; it's Kittelmann's NCrystal tutorial |
| VTB / MRAD | github.com/idaholab/virtual_test_bed | Template only; needs NCRC |
| SRP_interns2026 | github.com/RWillat/SRP_interns2026 | **Private — request access** |

## 1.5 Questions to ask, first week

1. **Which phase are the pellets — ε (tetragonal) or δ (cubic)?** Not trivia; it determines your CIF, your NCMAT, and your expected edges. (§3.4)
2. **What's the LANSCE flight path length L, and the t₀ offset?** You cannot convert TOF→λ without them. (§4.4)
3. **Can I be added to `SRP_interns2026` as `hsinghind13`?** (§6.5)
4. **What does "SRP" stand for?** Unresolved; also tells you which lab owns that thread.
5. **Is there a Zuzek-based lattice-parameter → H/Zr calibration the group already uses?** (§3.4)
6. **Which detector / what's the pixel pitch and TOF bin width?** Sets your resolution ceiling.

---

# 2. Physics: why this project exists

## 2.1 Why a space reactor at all

Solar dies. Past Jupiter sunlight is ~4% of Earth's; at Uranus ~0.25%. In a 14-day lunar night, or a Mars dust storm, it's nothing. Want power there → bring your own.

**NEP vs NTP — keep these straight, people conflate them constantly:**

| | **NTP** (Thermal Propulsion) | **NEP** (Electric Propulsion) |
|---|---|---|
| Reactor is… | **the engine** | **a power plant** |
| Mechanism | H₂ through the core → 2500 °C → nozzle | heat → conversion → electricity → ion/Hall thrusters |
| Isp | ~900 s | 1,500–4,000+ s |
| Thrust | huge (tens of kN) | tiny (milli-newtons) |
| Burn | minutes | **months–years, continuous** |

**You're on NEP.** DARPA/NASA's **DRACO was NTP** and was cancelled under FY2026 — don't cite it as precedent.

**Why 20 kWe is deliberately small:** ~20× KRUSTY (1 kWe), ~5× below SP-100 (100 kWe), and 2–3 orders below the MW-class a crewed Mars tug needs. Its job is to be *first*, not useful — retire launch survival, in-space startup, zero-g conversion, shielding, and regulatory precedent at the smallest scale that closes. Real mission niche: a **robotic outer-planet tug**, where NEP is the only way to *orbit* an ice giant rather than fly past. **Not** a cubesat tug — shield + converter + radiator mass has a hard floor.

## 2.2 Why moderators — the 500× that drives everything

Fission neutrons are born **fast (~2 MeV)**. But U-235's appetite depends enormously on speed:

- **thermal (0.025 eV): 585 barns**
- **1 MeV (as born): 1.2 barns**

**~500×.** So:

- **Fast reactor** — don't slow them, compensate with much more fissile material → heavy → can't launch.
- **Thermal reactor** — slow them, get 500× more fission per neutron, need far less fuel → **launchable.**

**Compact reactor ⟹ thermal spectrum ⟹ hydrogen.** That's why your project exists.

## 2.3 How hydrogen slows neutrons — billiard balls

The coincidence everything rests on:

$$m_n = 1.00866\ \text{u} \qquad m_p = 1.00728\ \text{u} \qquad \text{(differ by 0.14\%)}$$

An object hitting an *identical* stationary object head-on **stops dead and transfers everything.** Pool break. Newton's cradle.

$$\frac{E'_{\text{min}}}{E} = \alpha = \left(\frac{A-1}{A+1}\right)^2 \qquad\xrightarrow{A=1}\qquad \alpha = 0$$

**Hydrogen is the unique root**, and it's unique because A=1 is the only mass matching the neutron. See §1.3 for the full table.

**Why heavy nuclei fail:** to take energy, the target must *move*. Since KE = p²/2m, a large m soaks up almost no energy for a given momentum kick. Ping-pong ball off a bowling ball: momentum conserved, energy retained. To a neutron, zirconium is a wall.

## 2.4 Why hydrogen does **not** stop neutrons — three reasons

A natural inference from §2.3 is that hydrogen would just *stop* neutrons. It doesn't, and the reasons are the most important physics in the project.

**Reason 1 — head-on essentially never happens.** For hydrogen, post-collision energy is **uniformly distributed on [0, E₀]**. So average energy retained is **50%**, chance of losing >90% in one hit is 10%, and chance of an exact stop is **zero** (measure-zero event). *The "~18 collisions" number is itself the proof* — if hydrogen stopped neutrons, the answer would be 1.

**Reason 2 — there's a floor: thermal equilibrium, not rest.** Protons aren't still; they jiggle with ~kT. Once the neutron reaches ~kT it's as likely to be **kicked back up** as slowed (*detailed balance*). It **thermalizes**, joining the Maxwell-Boltzmann distribution. And thermal isn't slow: **2200 m/s = Mach 6.4.**

*(Hydrogen does absorb — n + p → D + γ — but at 0.33 b against 82 b scattering: ~250 bounces per absorption, and you only need 18. Not zero, though: this is exactly why light-water reactors need enriched fuel while heavy-water reactors burn natural uranium — **D absorbs 640× less**.)*

**Reason 3 — the hydrogen is BOUND. This is the one that matters.**

Everything in §2.3 assumed a **free proton**. Yours is locked in a Zr cage, vibrating as a **quantum oscillator at ~137 meV**, and a bound oscillator **only accepts energy in quanta**.

- **Neutron above ~137 meV** → can excite the oscillator → behaves roughly free.
- **Neutron below ~137 meV** → *cannot excite anything*. The collision becomes **neutron vs. the entire lattice**, effective mass → ∞:

$$\alpha = \left(\tfrac{A-1}{A+1}\right)^2 \xrightarrow{A\to\infty} 1 \qquad\Longrightarrow\qquad \text{max energy loss} \to \mathbf{0}$$

> **Below ~137 meV, chemical binding turns hydrogen from the best moderator in nature into an effectively infinite-mass wall.**

The binding is even visible in the cross section: **σ_bound = σ_free·((A+1)/A)² = 4σ_free** for A=1 → 20.5 b becomes **82 b**. *The 82 barns you rely on is itself a binding effect.*

**This is why NCrystal exists.** Below ~1 eV, behavior depends on crystal structure, vibrational spectrum, and temperature — not on α and ξ. That's the whole point of thermal scattering laws, S(α,β), and why the notebooks obsess over vibrational density of states.

## 2.5 Why ZrH₂ — and the scaffolding insight

You need hydrogen at **800–1100 K**. Water boils, polyethylene melts. Metal hydrides don't.

> **ZrH₂ holds ~7.2×10²² H/cm³. Liquid water holds ~6.7×10²².**
> A block of zirconium hydride is a **denser source of hydrogen than water.**

Now combine "how often" (cross section) and "how much" (kinematics) into the real figure of merit — **slowing-down power ξΣ_s**, computed for the two elements *in the same pellet*:

| In ZrH₂ | N (cm⁻³) | σ_s | ξ | **ξΣ_s** |
|---|---|---|---|---|
| **Hydrogen** | 7.2×10²² | 82 b | 1.000 | **5.9 cm⁻¹** |
| **Zirconium** | 3.6×10²² | 6.5 b | 0.022 | **0.005 cm⁻¹** |

> **Hydrogen does 99.9% of the moderating. Zirconium does essentially none.**

**ZrH₂ is not a "zirconium hydride moderator." It's a *hydrogen* moderator, and the zirconium is scaffolding** — a shelf whose only job is holding hydrogen still at 1000 K. **When hydrogen leaves a region, that region stops being a moderator.** Not "moderates less" — the physics leaves.

Scale: ~1.7 mm between H collisions, ~18 collisions needed → thermalization over **millimetres to centimetres**. That's why hydride cores are tens of cm while graphite reactors are metres. **It's also why a gradient across a single pellet is a reactor-physics problem, not a materials footnote — the neutron physics lives on the same length scale as the gradient.**

## 2.6 The hydrogen problem — why it moves

Hydrogen in a metal hydride is dissolved and mobile. Two failure modes:

1. **Decomposition** — heat it far enough and it releases H₂ gas. H/Zr drops from 2.0.
2. **Soret effect (thermal diffusion)** — the killer.

$$\frac{\partial c_H}{\partial t} = \nabla\cdot\left[-D\left(\nabla c_H + \frac{Q^* c_H}{RT^2}\nabla T\right)\right] \qquad\xrightarrow{\text{steady state}}\qquad \frac{\nabla c_H}{c_H} = -\frac{Q^*}{RT^2}\nabla T$$

In a real core, one pellet face touches **fuel** (hot), the other a **heat pipe** (cooler). Permanent gradient across millimetres, for years. For H in Zr, **Q\* > 0 → hydrogen accumulates on the cold side, depletes on the hot side.** (Same physics makes hydride blisters at cold spots in fuel cladding.)

**And there's nowhere to hide:** H solubility in α-Zr at RT is a few atomic **ppm**. Hydrogen leaving a hydride precipitates as a second phase or leaves as gas. No gentle solid-solution gradient.

**Why it compounds:** local H/Zr → local moderation → local fission rate → local temperature → *more* migration. A **coupled feedback loop.** Don't know the hydrogen distribution → don't know your reactor.

Vogel's exact framing: *"the local hydrogen concentration in ZrH₂ can deviate from the stoichiometric H/Zr=2 due to fabrication, overheating... or as a response to a temperature gradient."* **Those are your five pellets — same material, different thermal histories.**

## 2.7 The bonus — hydride is also *why the reactor is safe*

The 137 meV oscillator runs **backwards** too. If already excited (hot fuel), it **gives** the neutron ~137 meV. The neutron **speeds up** — **upscattering** — out of the 585-barn fission resonance. Fission drops. Power falls. Milliseconds, no operator, no electronics.

Bose-Einstein occupancy, n = 1/(e^{ħω/kT} − 1):

| T | kT | ħω/kT | **Oscillators excited** |
|---|---|---|---|
| 300 K | 26 meV | 5.3 | **0.5%** |
| **1000 K** (hot fuel) | 86 meV | 1.6 | **26%** |

**~50× more excited oscillators available to upscatter.** That is the entire safety case of a hydride reactor, in one line of Bose-Einstein statistics. It's why a TRIGA can be *pulsed* — deliberately driven prompt-supercritical in a university building — and shut itself down.

> **H/Zr isn't an efficiency knob. It's the safety case.** Lose hydrogen locally and you lose negative feedback exactly where you're hottest.

**The inversion worth remembering:** hydrogen doesn't stop neutrons. **Hot hydrogen speeds them back up — on purpose, and that's the feature.**

---

# 3. Physics: the measurement

## 3.1 Why neutrons — "the only practical way"

Not that nothing else detects hydrogen. That **only neutrons do all four at once**:

1. sensitive to H against heavy Zr · 2. penetrate cm of metal · 3. spatially resolved · 4. non-destructive

| Technique | H-sensitive | Penetrates | Spatial | Non-destructive |
|---|:--:|:--:|:--:|:--:|
| Weigh the pellet | ✅ | ✅ | ❌ **total only** | ✅ |
| Section + chem analysis | ✅ | — | ✅ | ❌ |
| X-ray CT | ❌ | ✅ | ✅ | ✅ |
| SIMS / surface | ✅ | ❌ µm | ✅ | ❌ |
| Neutron **diffraction** | ✅ | ✅ | ❌ **bulk avg** | ✅ |
| **Neutron imaging (ERNI)** | ✅ | ✅ | ✅ | ✅ |

**"Weigh it" fails on the word *went*.** If hydrogen migrates face-to-face, **pellet mass doesn't change.** A scale reads zero. All the information is in *where*.

**Neutron diffraction fails on spatial** — which is exactly why Vogel uses it as the **cross-check** (milestone 3), not the measurement. Two techniques, same beam, complementary blindnesses.

### Why hydrogen is invisible to X-rays

**X-rays scatter off electrons** (amplitude ∝ Z). H: Z=1. Zr: Z=40. In ZrH₂, hydrogen is 2/42 = **4.8% of the electrons**, and that lone electron is smeared into a diffuse bonding cloud.

**Neutrons scatter off nuclei**, and — the key fact — **neutron cross sections have no relationship to Z.** They're accidents of nuclear structure:

| | X-ray (∝Z) | **Neutron σ_s** |
|---|---|---|
| **Hydrogen** | 1 | **82.0 b** |
| Zirconium | 40 | 6.5 b |

Same arithmetic on ZrH₂, for neutrons: $\frac{2\times82.0}{2\times82.0 + 6.5} = \mathbf{96\%}$

> - To an **X-ray**: ZrH₂ is zirconium with a 5% hydrogen contamination it can barely register.
> - To a **neutron**: ZrH₂ is **96% hydrogen** with some zirconium in the way.

*As far as a neutron is concerned, the material is made of hydrogen.* That's what "the only practical way" means.

### The proof that neutrons see nuclei

| | Electrons | X-rays see | **Neutron σ_inc** |
|---|---|---|---|
| ¹H | 1 | identical | **80.3 b** |
| ²H (D) | 1 | identical | **2.0 b** |

Same element, same chemistry, same electron. **Indistinguishable to X-rays. 40× apart to neutrons.** Only the nucleus changed.

### Why H's cross section is so absurd — and why it pays twice

Spin. The neutron (½) and proton (½) pair two ways with wildly different — **oppositely signed** — scattering lengths:

$$b_+ = +10.85\ \text{fm (triplet)} \qquad b_- = -47.5\ \text{fm (singlet)}$$

**Those two numbers produce both of your gifts** (verified):

$$b_{\text{coh}} = \tfrac34 b_+ + \tfrac14 b_- = \mathbf{-3.738\ fm} \quad\text{(lit. −3.739)}$$
$$\sigma_{\text{inc}} = 4\pi\cdot\tfrac{3}{16}(b_+-b_-)^2 = \mathbf{80.2\ b} \quad\text{(lit. 80.27)}$$

> The singlet channel is so violently negative it **drags the spin-average below zero** (→ negative scattering length → **edge *heights* encode hydrogen**, §3.5) **and** makes the variance enormous (→ 80 barns incoherent → **you can see hydrogen at all**, §3.1).
>
> **One accident of nuclear spin. Two gifts. Both load-bearing.**

X-rays have no analogue — photons don't care about nuclear spin.

*(Honest caveat: X-ray CT isn't literally blind to hydriding — ZrH₂ is less dense than Zr, so hydride regions can sometimes be inferred from density contrast. But that's inferring hydrogen from a volume effect, not detecting it. Weak, indirect, won't give H/Zr.)*

## 3.2 Why *energy-resolved* — and how TOF gives it free

**White-beam radiography** = one gray value per pixel = total attenuation. But attenuation = (how much) × (what kind) × (how thick) — **degenerate.** A thick low-H region looks like a thin high-H region. Prior work needed fabricated **internal standards** to break it. **Vogel wants to do it without one.**

**ERNI** makes every pixel a **full spectrum**. LANSCE is **pulsed**: at t=0 neutrons of all energies leave together, then sort themselves by speed over the flight path L:

$$v = L/t \qquad \lambda[\text{Å}] = \frac{3956}{v[\text{m/s}]} \qquad E[\text{meV}] = \frac{81.81}{\lambda[\text{Å}]^2}$$

**Arrival time *is* wavelength.** "2,500 radiographs" = 2,500 time bins = 2,500 wavelength slices of the same image.

## 3.3 Bragg edges

$$\lambda = 2d_{hkl}\sin\theta \qquad\text{and}\qquad \sin\theta \le 1 \qquad\Longrightarrow\qquad \lambda_{\max} = 2d_{hkl}$$

Beyond λ = 2d_hkl, that plane **can no longer diffract at all**. In **transmission**, scattering switches **off** → transmission **jumps up** in a sharp step. That's a **Bragg edge**.

```
   T(λ)
    │            ┌──────────  ← beyond 2·d_max: nothing left to diffract
    │       ┌────┘
    │   ┌───┘                 ← each step = one lattice plane switching off
    │───┘
    └──────────────────────► λ
         edges at λ = 2·d_hkl
```

What each part gives you:

- **Edge positions** → d-spacings → **lattice parameter** → H/Zr via Zuzek [7]
- **Edge heights** → structure factors → **phase fractions, texture, H occupancy** (§3.5)
- **Smooth baseline between edges** → H's incoherent + inelastic → **where the H concentration signal lives**

> **Your hydrogen signal is mostly in the baseline, not the edges.** The edges pin down the *geometry* so the baseline can be read as *composition*. And the baseline **is bound-hydrogen physics** (§2.4, Reason 3) — which is why you need a real quantum scattering model, not billiard balls.

## 3.4 The Zr–H phase map — your decoder ring

$$\text{H/Zr} \rightarrow \text{phase} \rightarrow \text{structure} \rightarrow d\text{-spacings} \rightarrow \textbf{edge positions}$$

You measure the right end and read leftward. **Zuzek et al. 1990, "The H-Zr system"** is reference **[7]** because it's the lookup table for milestone 3.

| Phase | Structure | Space group | H/Zr | Notes |
|---|---|---|---|---|
| **α-Zr** | hcp | P6₃/mmc (#194) | ~0 → 0.06 | **NCrystal ships this** (`Zr_sg194.ncmat`) |
| **β-Zr** | bcc | Im-3m (#229) | to ~0.6 | >550 °C only |
| **γ-ZrH** | fc tetragonal | P4₂/n (#86) | ≈1.0 | metastable; equilibrium status **contested** |
| **δ-ZrH_x** | **fcc fluorite** | Fm-3m (#225) | **1.5–1.7** | **TRIGA fuel; what ENDF `c_H_in_ZrH` was evaluated for** |
| **ε-ZrH_x** | fc **tetragonal** | I4/mmm (#139) | **1.74–2.0** | **near-stoichiometric — probably your pellets** |

Eutectoid **~550 °C** (β → α + δ).

### There's only one structure

> Take **fcc zirconium**. Pour hydrogen into the **tetrahedral holes**. There are exactly **2 per metal atom** — "all holes full" = ZrH₂ = fluorite.

- **δ** — holes 75–85% full, vacancies disordered → stays **cubic**
- **ε** — holes nearly full → can't stay cubic → **distorts tetragonally**
- **γ** — holes half full but *ordered* → different tetragonal distortion

**δ→ε at H/Zr ≈ 1.7 is a cubic→tetragonal symmetry break driven purely by filling the last hydrogen sites.**

> **Crystal symmetry is a hydrogen meter.**

Lattice parameters: **δ-ZrH₁.₆** cubic **a ≈ 4.78 Å** · **ε-ZrH₂** tetragonal **a ≈ 3.5274, c ≈ 4.4148 Å** (mp-24286).

They look unrelated until you see I4/mmm is the fcc cell rotated 45° in-plane: **a√2 = 4.99 Å** vs **c = 4.41 Å**, against δ's 4.78 → **in-plane +4.4%, c-axis −7.6%.**

### What it does to your edges (verified)

| **δ-ZrH₁.₆** (cubic) | | **ε-ZrH₂** (tetragonal, I-centred: h+k+l even) |
|---|---|---|
| (111) → **5.52 Å** | → | (101) → **5.51 Å** — *barely moves* |
| (200) → **4.78 Å** | → | **(110) @ 4.99 + (002) @ 4.41** — **SPLITS** |
| (220) → **3.38 Å** | → | **(200) @ 3.53 + (112) @ 3.31** — **SPLITS** |

> **The δ→ε signature isn't a shift. It's a *splitting* — single edges tearing into pairs.**

**The trap:** the **longest-wavelength edge — biggest, most obvious, the one you'd check first — is identical in both phases (5.51 vs 5.52 Å).** Validate on that alone and both phases pass; you learn nothing. Phase info is in the **2nd and 3rd edges splitting**, ~0.6 Å apart.

This is exactly what the TSL_School TRIGA notebook silently glosses: it calls the material "ZrH2," models it as **tetragonal ε**, and applies ENDF's `c_H_in_ZrH`, evaluated for **cubic δ**. Two crystals in one notebook. **k-eff never noticed. Your measurement would.**

## 3.5 Structure factors — and the way around the degeneracy

Fluorite structure factors with H occupancy *x* (H/Zr = 2x), using b_H = **−3.739** fm, b_Zr = +7.16 fm (all verified):

| Reflection | F | **ZrH₂** (x=1) | ZrH₁.₆ (x=0.8) | bare Zr (x=0) |
|---|---|---|---|---|
| **(111)** | b_Zr | **7.16** | **7.16** | **7.16** |
| **(200)** | b_Zr − 2x·b_H | **+14.64** | +13.14 | 7.16 |
| **(220)** | b_Zr + 2x·b_H | **−0.32** | +1.18 | 7.16 |

**1. (111) is blind to hydrogen.** The two H sublattices interfere destructively and cancel **exactly, at any H content**. That edge sees only zirconium. **A free internal reference** — the thing prior work needed a fabricated standard for.

**2. (200) and (220) run opposite.** Because b_H < 0, hydrogen **strengthens (200)** and **annihilates (220)**. Bare Zr → ZrH₂: **(220) collapses ~507×**, **(200) grows 4.2×**. Two edges moving opposite ways with H content is a very strong signal.

**3. The one to take to Vogel — edge-height *ratios* divide out the geometry.**

> Thickness, number density, and beam normalization are **common factors** in every edge. So **(200)/(220)**, or either against the hydrogen-blind **(111)**, gives hydrogen occupancy **without knowing the thickness.**

That's an independent route around the §4.3 degeneracy — and independent of the milestone-2 symmetry constraint. **Two handles on the one degeneracy that most threatens the measurement.**

### Your five pellets, decoded

- **Fully hydrided** → **ε**, split edges
- **Lost some H** → through the **ε+δ two-phase field** toward **δ** — edges *merge*
- **Lost a lot** → **δ + α-Zr**, and **hcp α-Zr edges appear at ~5.60 Å** that weren't there before
- **Held in a gradient** → **ε on the cool face, δ on the hot face** — a **phase boundary inside one pellet**

That last is the money shot, and it's concrete: **edge structure changing across the image**, splitting and merging pixel to pixel. A 2D phase map, non-destructive, in an intact pellet.

> **"Which phase are my pellets?" isn't a preliminary you settle and move past. It may be the answer.**

---

# 4. The analysis

## 4.1 The four milestones, decoded

| # | Proposal says | Means |
|---|---|---|
| **1** | Fit H concentration from energy-dependent cross-sections | Hundreds of thousands of spectra; bin pixels (2×2, 32×1) to buy Poisson statistics |
| **2** | Implement constraints from cylindrical symmetry | The pellets *are* cylinders — a central ray sees more material than a rim ray. **Use known geometry to kill the thickness degeneracy** (§4.3) |
| **3** | Integrate to per-pellet values; compare with lattice parameters | **Diffraction (HIPPO), same volume, is your ground truth**, via Zuzek |
| **4** | Estimate spatial & concentration resolution for the count time | So future experiments know what to ask for |

**Success criterion (literal):** ERNI and diffraction agree on overall H **within error bars**.
**Named risk (literal):** energy-dependent, **sample-induced background** — *"a crucial part of this problem."* Believe it; it will eat your summer. Mitigation in the proposal: iterate background estimates per-pixel from observed attenuation.
**Benchmark:** prior art achieved ~5 wt ppm resolution, ~10 wt ppm accuracy, 25 µm × 5 mm × 10 mm — **but with white beam + internal standards.** ERNI aims for comparable **without** a standard.
**Deliverable:** a reusable Python analysis framework, not just a number. Stretch: 3D tomography, ML.
**No beam-time risk** — uses existing data.

## 4.2 The pipeline

```bash
# 1. Reduce to per-pixel/per-region spectra (slices = TOF bins)
save-roi -t sample.tiff   -m grid --grid-size 4 --tilt pellet_axis -o sample_spectra -j -1
save-roi -t openbeam.tiff -m grid --grid-size 4 --smooth            -o ob_spectra     -j -1
```
```python
# 2. Load as grouped data — glob straight onto save_roi's filenames
import nbragg
data = nbragg.Data.from_grouped(
    "sample_spectra/grid_4x4_x*_y*.csv",
    "ob_spectra/grid_4x4_x*_y*.csv",
    tstep=10.0e-6, L=<LANSCE FP length, m>, t0=<offset, bins>,
    query="80<x<230 and 0<y<350",     # crop before loading
    n_jobs=-1)

# 3. Two-phase model: the fitted weight `zrh2` IS your hydrogen handle
xs = nbragg.CrossSection(zrh2="zrh2.ncmat", zr="Zr_sg194.ncmat")
model = nbragg.TransmissionModel(xs, vary_weights=True,
                                 vary_background=True, vary_response=True)
result = model.fit(data, wlmin=2, wlmax=8, method="rietveld",
                   n_jobs=-1, backend="loky")

# 4. Maps + QC
result.plot_parameter_map("zrh2")
result.plot_parameter_map("zrh2_err")
result.plot_parameter_map("redchi", cmap="hot")

# 5. Selective refit of only the bad pixels, warm-started
result2 = result.fit(data, query="redchi > 2", n_jobs=-1)
result2.save("zrh2_map.json")
```

**They're co-designed** though save_roi never names nbragg: nbragg's TOF column aliases include **`stack`** (save_roi's exact output column), and its filename regex carries a comment about avoiding matches on dimension specs like `16x16` — precisely save_roi's `grid_16x16_x{x}_y{y}.csv`.

## 4.3 The degeneracy — and three ways around it

nbragg's model:

$$T(\lambda) = \text{norm}\cdot e^{-\sigma(\lambda)\cdot \textbf{thickness}\cdot \textbf{n}}\cdot(1-bg) + k\cdot bg$$

**Stare at the exponent: σ, thickness, and n all multiply.** They fight each other. Worse, **nbragg computes `atomic_density` (n) once and caches it — it does NOT update as weights vary.** So fitted weights are *relative phase fractions at fixed n*, and absolute H density partly folds into `thickness`.

**Three independent attacks:**

| Route | Mechanism | Source |
|---|---|---|
| **Fix thickness from geometry** | Pellets are cylinders of known diameter; `--tilt` straightens the axis first | Practical |
| **Cylindrical symmetry constraint** | Milestone 2 — geometric | Proposal |
| **Edge-height ratios** | (200)/(220) or /(111); thickness is a **common factor and divides out** | §3.5 |

Use more than one. They fail differently.

## 4.4 Traps

- **`stack` is a 1-indexed bin number, not physical TOF.** Set `t0`/`L0` to absorb both ImageJ's 1-indexing and the LANSCE t₀/shutter delay. **Fit `vary_tof=True` on a summed high-statistics ROI first, then freeze** for the per-pixel run.
- **Multiphase cfg-strings use volume fractions, not mass fractions.** Silent bug when converting to at.% H.
- **Unmodelled systematics bias H directly**, and NCrystal gives you none of them by default:
  - **Texture** — powder approximation only. Pressed/sintered pellets *have* texture. → `CrysText` plugin or nbragg's MTEX path.
  - **Extinction** — → `CrysExtn` plugin (`pip install git+https://github.com/XuShuqi7/ncplugin-CrysExtn`); nbragg supports it natively.
  - **In-scattering** — → NEUWAVE `In_scattering` notebook.
  - **Grain size** — no correction exists in NCrystal at all.
- **nbragg's default branch is `master`, not `main`** — raw URLs on main 404. Pin **≥0.8.2** for in-memory materials + `loky`.
- **save_roi is not on PyPI** — `git clone && pip install -e .`. It also **doesn't read event-mode data**; event→bin reduction stays upstream.
- **`--smooth`** borrows TOF spectral *shape* from the full image and rescales to local intensity, with covariance-aware errors — the right way to build a low-noise **open beam**.

---

# 5. The software stack

## 5.1 NCrystal

C++11 library for **thermal** neutron transport. Apache 2.0, v4.4.6. Refs: `10.1016/j.cpc.2019.07.015`, `10.1016/j.cpc.2021.108082`.

$$\sigma_{tot} = \underbrace{\sigma_{coh,el}}_{\text{Bragg edges}} + \underbrace{\sigma_{inc,el} + \sigma_{inel}}_{\textbf{the H baseline}} + \sigma_{abs}$$

Three objects: **cfg-string → `Info`** (structure, HKL, VDOS, composition) **→ `Scatter`** (xs + MC sampling) **→ `Absorption`** (1/v only). `NC.load(cfg)` = `createLoadedMaterial`, bundles all three.

Cfg-strings are universal across Python/McStas/OpenMC/Geant4:
```
"Al_sg225.ncmat;density=2.6gcm3;temp=250K;comp=elas"
"phases<0.1*PbS_sg225.ncmat&0.9*Epoxy.ncmat>;temp=250K"     # VOLUME fractions
"solid::B4C/2.52gcm3/B_is_0.95_B10_0.05_B11"
```
Components: `coh_elas` (alias **`bragg`**), `incoh_elas`, `sans`, `inelas`; `elas` = all but inelas. **Use `comp=` toggling to decompose your model and see what each term contributes before trusting a fit.**

Inelastic uses **VDOS→S(α,β) on the fly via the Sjölander method** (same as NJOY/LEAPR) — **temperature dependence for free**, unlike a static tabulated kernel valid at one T. Knob: `vdoslux` (default 3; leave it, or ±1).

**MCNP has no direct binding** — path is NCMAT → `ncmat2endf` → NJOY → ACE. OpenMC: `openmc.Material.from_ncrystal()`. CLI: `nctool --dump/--browse/--extract`.

## 5.2 nbragg

lmfit `Model` subclass over NCrystal. `pip install nbragg`. Active (v0.8.2, June 2026).

- Fit methods: **`rietveld`** (default, staged with accumulating params), `staged`, `least-squares`
- Responses: `jorgensen` (default, back-to-back exponentials), `square`, `none`… Backgrounds: `polynomial3` (default), `constant`, `sample_dependent`, `none`
- `CrossSection(name=...)` per phase, each with `mat, temp, weight, mos, dir1/dir2, a/b/c, ext_*, sans, comp`
- **Phase weights are named after your phases**: `CrossSection(zrh2=..., zr=...)` + `vary_weights=True` → a fitted parameter literally called **`zrh2`**, via a softmax parameterization (`p_i = log(w_i/w_N)`, bounded ±14) guaranteeing weights sum to 1
- `vary_*` flags: `basic, weights, background, tof, response, orientation, lattice, extinction, sans`
- `GroupedFitResult`: `.plot_parameter_map()`, `.summary()`, `.fit_report(i)`, `.save()/.load()`, and **selective refit** `.fit(data, query="redchi > 2")` warm-started per pixel — **the killer feature at 50k pixels**
- Custom materials: `nbragg.register_material(cif_source="codid::XXXXXX", material_name="ZrH2")`
- Tutorials: `notebooks/grouped_fits_tutorial.ipynb` ← **yours**, `Rietveld_in_nbragg_tutorial.ipynb`

## 5.3 save_roi

Collapses a 3D TIFF stack (slices = TOF bins) → per-region 1D spectra. Modes: `roi` (ImageJ .roi/.zip), `full`, `grid`, `pixel`. Reads `.tiff/.tif/.tiff.gz`. Parallel via shared memory.
Output: **`(stack, counts, err)`**, err = √counts. Names: `pixel_x{x}_y{y}.csv`, `grid_{gs}x{gs}_x{x}_y{y}.csv`.
Key flags: `--tilt ROI_NAME` (straighten a tilted symmetry axis — **for your cylindrical pellets**), `--smooth` (open beams), `-j/--jobs`.

## 5.4 ⚠️ The ZrH₂ material gap — read before you start

> **NCrystal ships no ZrH₂. No ZrH. No Zr hydride of any kind.**

It has `Zr_sg194.ncmat` (hcp α-Zr) and four hydrides (CaH₂, MgH₂, SrH₂, LiH) out of ~143 files. No plugin supplies one.

`mctools/ncrystal-extra` has LANL's own evaluation:
`data/unvalidated/ZrH_T296.0K_ENDF8_massconvert_inelasticonly_dummydensity.ncmat` (+ 400…1200 K)

**Read the filename — it's unusable as-is for Bragg-edge fitting:**
- **ZrH, not ZrH₂** (`fraction 1/2` each; you need H=2/3, Zr=1/3)
- **`inelasticonly` + `dummydensity`** → **no unit cell → no Bragg edges**, and `@DENSITY 1 g_per_cm3 #FIXME. Dummy number!!!`
- The ENDF evaluation itself approximated the tetragonal lattice as **fcc**
- It lives in `data/unvalidated/`

**So you must compose it** — which is exactly what the Water/Ice notebook teaches, cell for cell:

1. `nccif.CIFSource('codid::...')` → `NC.NCMATComposer.from_cif(...)` (spglib-verified). The auto-generated file falls back to a **dummy Debye temperature** with a loud warning — placeholder, not physics.
2. Replace with a real VDOS: `NC.PhononDOSAnalyser([('H',x,y),('Zr',x,y)])` → `.plot_cutoff_effects(...)` → `.apply_cutoff(...)` → `.apply_to(c)` → `.write('zrh2.ncmat')`
   - *Alternative:* splice the `@DYNINFO type=scatknl` blocks from the ncrystal-extra file onto a real `@CELL`/`@ATOMPOSITIONS`/`@SPACEGROUP` — **but fix the fractions to 2/3 H, 1/3 Zr**, and you're locked to the 8 tabulated temperatures. The VDOS route gives temperature dependence free.
3. **Validate against EXFOR before fitting anything real.** If you can't reproduce a measured σ_tot(λ), your fitted H number means nothing. Watch per-atom vs per-molecule (×3 for ZrH₂).
   - Ready-made ZrH data, already unit-converted, is embedded in the TRIGA notebook: **Schmidt 1967** (EXFOR 23424), **Whittemore 1964** (14174/002,003).
4. **Pick the right phase** (§3.4) — ε (I4/mmm, mp-24286) vs δ (Fm-3m). **Confirm with Vogel.**

`export NCRYSTAL_ONLINEDB_CACHEDIR=...` early so COD fetches cache and notebooks stay reproducible offline.

## 5.5 Notebook priority

Setup: `python3 -mpip install "ncrystal[all]" jupyterlab ipympl pandas tqdm`

| Rank | Notebook | Why |
|---|---|---|
| **1** | **`TSL_School/openmc/Examples/Transmission`** | *"Energy dependent transmission (and fixing OpenMC thermal scattering data)."* **Nobody linked it; it's the most useful.** Pencil beam → slab → tally spheres, recovering Σ_tot = −ln(T)/dx. **Structurally identical to your measurement.** The instructor used it to **find a bug in a LANL-evaluated polyethylene TSL** that criticality calcs had lived with for years. Clone it, swap in ZrH₂. |
| **2** | `ncrystal2_advanced_01` / `_02` / `_03` | NCMATComposer / CIF import / PhononDOSAnalyser+QE. **Your actual job** (§5.4) |
| **3** | NEUWAVE `Extinction_correction_exercise` | hkl → coherent elastic xs, modified by the **Sabine model**. nbragg exposes exactly this |
| **4** | NEUWAVE `Installing_Plugins_Texture_exercise`, `In_scattering` | Live systematics for pressed pellets |
| **5** | `NEUWAVE_12_Examples_Water_Ice` (the linked one) | Value is the **method** (compose → replace Debye with VDOS → validate vs EXFOR), not the water. Start with `ncrystal1_basic_01`. |
| **6** | `TSL_School-TRIGA_cell` | **Lowest — but the null result is the point.** See below. |

### The TRIGA notebook's real lesson

Its **ENDF path** (H-in-ZrH TSL only, Zr as free gas, **no Bragg edges**) and its **NCrystal path** (full tetragonal crystal, both sublattices, **Bragg edges present**) give **k-eff agreeing to 0.0004 — inside 1σ.** Materially different physics; k-eff can't tell them apart, because it integrates over the spectrum and is dominated by H's 137 meV upscatter.

**But Bragg edges are exactly what ERNI measures.** Two consequences, both yours to say out loud:

- **ERNI constrains structure/phase detail no criticality benchmark can ever discriminate.** *That's the argument for why this work is worth $100K.*
- **A ZrH TSL validated against k-eff is NOT validated for imaging.** People will assume it is. It isn't.

Also: ENDF `c_H_in_ZrH` is tabulated at **8 temperatures with a hard 296 K floor and 1200 K ceiling**. A space reactor runs 800–1100 K, near the sparse top. **NCrystal's on-the-fly path removes the limit at zero runtime cost** (14.7 s vs 15.4 s in the notebook's own timings) — the most transferable result for the NEP thread.

*(Subtlety the notebook doesn't call out: its "293 K" ENDF case runs because OpenMC's default 10 K tolerance lets 296→293 pass. **It's actually 296 K data.** The 275 K case fails outright. Silent in production.)*

### Context

- **NEUWAVE** = **Neu**tron **Wave**length-dependent imaging workshop — your field's workshop series (Bragg-edge imaging, resonance absorption imaging, detectors). **NEUWAVE-12**: 1–4 Sept 2024, Lund, hosted by ESS.
- **The linked PDF** (`2024-09-05-...`) is dated the day *after* — it's **Thomas Kittelmann's** (NCrystal's lead author) deck for the **NCrystal satellite workshop at LINXS, 5 Sept 2024**, a full-day hands-on tutorial. Tutorials by Kittelmann, Di Julio, and **Márquez Damián** (who wrote the Water/Ice notebook and the CAB water models).
- **TSL_School** = HighNESS International School on Thermal Neutron Scattering Kernel Generation, 22–26 May 2023, ESS Campus, Lund. Curriculum: scattering theory (Granada) → DFT/Quantum Espresso for VDOS → NCrystal (Kittelmann) → OpenMC (Márquez Damián).
- **HighNESS** = EU H2020 project (grant 951782, ~€3M) designing a second, cold/very-cold/ultracold neutron source below the ESS target. The school exists because designing novel moderators means **generating kernels for materials that don't have them** — the throughline is DFT → VDOS → kernel → transport → validate vs EXFOR. Which is your project.

---

# 6. The reactor thread

## 6.1 The power chain and the T⁴ tyrant

**Reactor (heat) → conversion → electricity → Hall thrusters.** At 20 kWe and ~20% efficient: **~100 kWt in, ~80 kWt of waste heat out.**

> **In space there is no convection and no conduction to anything. The only way to reject heat is to radiate it.**

$$P = \varepsilon\sigma A T^4$$

**That T⁴ is the tyrant of the entire design.** It's why radiators dominate system mass, and why the trade isn't "maximize efficiency" — it's **"minimize total mass."**

## 6.2 The 26% question — two independent problems

**Siddharth's baseline:** *"~26% thermal efficiency seems reasonable... target thermal power of about 80 kWt"* (20/0.26 = 76.9). He cited a paper and **asked for other sources.**

**Problem 1 — the paper is about a 5× larger system.** It is:
> **"Performance design and optimization for 100 kWe space nuclear power system: A review"** — Jiang Baihui, Ji Yu, Sun Jun, Wu Yingjie, Shi Lei (all **Tsinghua/INET**, the HTR-10/HTR-PM group). *Acta Astronautica* **242** (May 2026) 107–118. DOI **10.1016/j.actaastro.2026.01.026**. CNSA-funded (D010102).

Reviews **100 kWe-class**; concludes He-Xe + closed Brayton wins on efficiency/specific power/compactness. Reference list 100% Brayton. **No 20 kWe design, no Stirling, no thermoelectric.** And Brayton scaling runs the **wrong way**: *"At power levels below ~1 MW, Brayton cycle technology generally becomes less efficient due to tip clearance and higher rotational speed windage losses"* (Dyson, **Rao (LANL)**, Duchek, Mason — NTRS 20220002293).

**Problem 2 — 26% is a *converter* number, never a *system* number.**

| Source | 26%-class figure | What it delivers |
|---|---|---|
| FSP 2010 (NASA/TM-2010-216772) | conversion *"projected at **26 percent**"* | **net system 21.5%** |
| FSP 2022 (Oleson, NETS) | convertor **26.1%** | **end-to-end 18.1%** |
| Sandia GCR-CBC NEP (SAND2006-2518) | 108 kWe, **26.9%**, 400 kWt | net of 92% alternator, **excludes PMAD** |
| SP-100+Brayton (TM-105637) | engine 27.9% | net 26.1% — at **379 K CIT, 260 m² radiator** |

> **Nothing in the NASA corpus achieves 26% reactor-thermal-to-bus, at any scale, with any technology.** PMAD (87–95%), thermal losses (~18–20%) and parasitics strip 15–30% relative off the converter figure.

**The decisive measured evidence** — FSP Technology Demonstration Unit, ~12 kWe Stirling, **spec'd at 26%**:

| Condition | PCU η | System η |
|---|---|---|
| **Electrically heated** | **25.5%** ← met spec | — |
| **NaK-coupled, nominal** | **21.7%** | **17.2%** |

**Electrically heated it hit spec. Bolted to a real liquid-metal loop it delivered 21.7%, and 17.2% to the bus.** That gap is exactly what a converter number hides.

**NASA Glenn's loss ladder** (NTRS 20060005159) — a **50 kWe** He-Xe CBC at 1150/400 K, adding real losses one at a time:

| Model fidelity | η |
|---|---|
| Idealized | 31.9% |
| + 2% compressor bleed | 30.1% |
| + map-based turbomachinery | 25.1% |
| + bearing loss | 23.8% |
| + windage | 22.4% |
| **+ EM = realistic** | **21.7%** |

Their warning: *"Efficiency errors of 30% and mass estimate errors of 20% are possible using even moderately unrealistic representations."* **A 50 kWe machine lands at 21.7% — below 26%, at 2.5× the power in question.**

### Sizing recommendation

| η | Q_reactor | Waste heat | Basis |
|---|---|---|---|
| 26% | 76.9 kWt | 56.9 | converter mistaken for system ← **current figure** |
| **23.1%** | **86.6 kWt** | 66.6 | **Kilopower design point — if Stirling** |
| 21.5% | 93.0 kWt | 73.0 | FSP 2010 net |
| **18–20%** | **100–111 kWt** | 80–91 | **if Brayton** |

**80 kWt is ~8–30% optimistic.**

**Also worth raising: at 12–20 kWe, Stirling beats Brayton by ~5–7 points.** NASA designed a 12 kWe closed Brayton at conditions *identical* to the 12 kWe Stirling TDU (CR-2010-215673): **19.0% cycle / 18.1% system (0.32 of Carnot)** vs Stirling's **25.5% measured (0.46 of Carnot)**.

**Carnot-fraction rules of thumb: Stirling 0.46–0.57 · Brayton 0.32–0.45 · thermoelectric 0.07–0.16.**

A 20 kWe NEP sits in **Stirling territory** — *but* NASA's Aug 2025 directive moved FSP to **≥100 kWe, <15 t, closed Brayton**, chosen for **extensibility despite** the low-power efficiency deficit. If the team tracks NASA architecture, Brayton is right and **the efficiency must come down.**

**Specific mass:** three independent routes converge on **~100–150 kg/kWe** at 20 kWe (Kilopower extrapolation ~125–145; Gibson's 8 kWe NEP = 1142 kg / 8 kWe = **143**; JIMO Brayton scaling ~100). **Radiator ~40 m²** at 4–8 kg/m².

**Better citations than the Tsinghua review:** **SAND2006-2518** (closest design point: 108 kWe, 26.9%, 1144 K/319 K, 264 m² radiator), **NTRS 20060005159** (loss ladder), **NASA/TM-2015-218460** (Kilopower), **TM-2016** (measured NaK penalty).

## 6.3 CR-1870 / the BRU — and why it does *not* rescue the 26%

**NASA CR-1870**, "Design and Fabrication of the Brayton Rotating Unit," J. E. Davis, **AiResearch Manufacturing Company of Arizona**, March 1972, for NASA Lewis (contract NAS 3-9427, PM James H. Dunn; AiResearch APS-5334-R). 390 pp, unclassified/unlimited. **The canonical flight-adjacent closed-Brayton turboalternator.**

**Design point (Table 1, p.5):** single shaft, **36,000 rpm**, **2.25–10.5 kWe** at 1200 Hz 3-phase (6.0 kWe reference), **Xe-He, MW 83.8**, turbine inlet **2060 °R (1144 K)**, compressor inlet **540 °R (300 K)**, PR 1.90/1.75, tilting-pad gas journal bearings + step-sector gas thrust bearing on a gimbal, **175 lb** with insulation and ducting, **5-year life**, 0-g or terrestrial.

**Table 2, p.15 — PDF page 30** *(body page N = PDF page N+15)*:

| Net generator output | 2.25 kWe | 6.0 kWe | 10.5 kWe |
|---|---|---|---|
| **Cycle efficiency (net output / Q_in)** | **0.217** | **0.30** | **0.32** |
| Compressor / turbine / generator η | 0.79/0.85/0.85 | 0.80/0.87/0.92 | 0.80/0.87/0.92 |
| Recuperator effectiveness | 0.95 | 0.95 | 0.95 |
| 1−(ΔP/P) total system | 0.92 | 0.92 | 0.92 |

**Measured at LeRC** (TM X-67846), 1144 K/300 K: **gross 33.5%, net 30%, 15.2 kWe** at terminals. **BRU-F** with gas foil bearings reached **15 kWe** — the closest hardware to 20 kWe ever built. BRU ran on Kr or Ar with no configuration changes.

**Trap in your favour:** CR-1870 *labels* this "cycle efficiency" but **defines** it as net output ÷ Q_in — already net of field excitation, speed control, VRE and radiator-loop pump. **Closer to a net system efficiency than a bare cycle number.**

### ⚠️ Why "BRU got 30%, so 26% is safe" is wrong

**The cold end is doing the work.** BRU's compressor inlet is **300 K**. Carnot(1144/300) = **73.8%**, so 0.30 is **0.41 of Carnot**. But rejecting at 300 K in space costs radiator area:

$$\left(\frac{425}{300}\right)^4 = \mathbf{4.03}$$

**BRU's "better" efficiency costs 4× the radiator area.** Real space systems deliberately run a **hotter** cold end (400–425 K) to shrink the radiator and pay in efficiency. **That's why BRU's 30% beats JIMO's predicted 21.7% (411 K CIT) despite being 33 years older — not progress running backwards.**

> **Comparing efficiencies without stating the rejection temperature is meaningless.**

**And efficiency falls with power** — BRU itself: 0.32 → 0.30 → **0.217** at 10.5 → 6.0 → 2.25 kWe.

**Send Table 2 to Siddharth as the closest measured hardware — not as vindication of 26%.**

## 6.4 MRAD & the Virtual Test Bed

**MRAD = "Micro-Reactor Application Drivers"** — a DOE-NE **NEAMS** *program area*, **not a reactor name.** The reactor is **HP-MR** (Heat-Pipe Micro-Reactor), a generic non-proprietary **ANL** modeling exercise.

| | |
|---|---|
| Power | **2 MWt** (~25× your thermal power) — **terrestrial** |
| Fuel | TRISO/UCO, 19.95% LEU, 40% packing in graphite (IG-110) |
| Moderator | **YH₂ pins**, SS-clad, He gaps both sides |
| Coolant | **none — potassium heat pipes** (192 in the 1/6-core model) |
| Control | 12 drums + central rod · k_eff 1.050 |

**Coupling:** **Griffin** (neutronics, DFEM-S_N with CMFD) → **BISON** (heat conduction) → **Sockeye** (one per heat pipe), via MOOSE **MultiApps** with Picard iteration. **Serpent-2** offline for multigroup XS → **ISOXML** → Griffin. Run via the **BlueCRAB/DireWolf** super-app.

**Its moderator model is crude:** no hydrogen transport at all; `HeatConductionMaterial` literally carries `specific_heat = 500 # random value`. He gaps aren't meshed.

**Value = methodology template**, not design analogue: the MultiApp pattern, XS tabulation on (T_f, T_m, c_H), Reactor Module drum meshing, and the Griffin-vs-BISON mesh-resolution lesson (energy closure 93.3% → 99.3% with the fine mesh).

### The models actually on-point for you

| Model | Why |
|---|---|
| **S8ER** (SNAP-8) | **600 kWt, HEU U-ZrH, NaK**, BeO/Be reflectors, **hydrogen diffusion barrier**. Explicitly framed around validating NEAMS tools against SNAP data for *"high temperature solid moderators prone to hydrogen migration."* **Closest VTB analogue to a space NEP power reactor.** Extra data: github.com/CORE-GATECH-GROUP/SNAP-REACTORS |
| **KRUSTY** | **Real flight-heritage space reactor**, built on ICSBEP benchmark HEU-MET-FAST-101 → a **validation** case, not a demo |
| **`microreactors/hpmr_h2`** | **Solves the Soret equation** (§2.6) for H redistribution in BISON, XS tabulated on **H:Y = {1.7, 1.8, 1.9}**. **This is the bridge to your LANL work.** Trick: sets D=1 for steady state, since the asymptotic distribution is independent of D |
| **STARTR** | **OpenMC + MCNP, fully open**, UZrH TRIGA-type fuel, Na-cooled. ⚠️ Known open bug: MCNP and OpenMC **disagree significantly on partially-rotated drum worths** — unresolved, released as-is |

## 6.5 Code access — the blocker to handle early

**Every code MRAD needs is NCRC-licensed:**

| Restricted (NCRC) | Open source |
|---|---|
| **Griffin, BISON, Sockeye, BlueCRAB, DireWolf**, Pronghorn, SAM, RELAP-7, Grizzly | **MOOSE, OpenMC, Cardinal, NekRS, MASTODON, TMAP8** |
| Serpent (separate VTT license) | |

**BISON and Sockeye are commonly but wrongly assumed to be open. They are not.**

- **Path in:** NCRC **Level 1 (HPC Binary)** on INL HPC (Sawtooth/Bitterroot/WindRiver) — the realistic intern route. **Explicitly request Sockeye** — it's an optional BlueCRAB module and the MRAD decks won't run without it. Go through an **INL/ANL staff contact**, not a cold application. RSA 2FA for export-controlled apps.
- **What runs today, free:** **all mesh generation** (mesh decks use only MOOSE + Reactor Module → `--mesh-only` reproduces the real HP-MR mesh — best zero-friction way to learn the geometry); **STARTR**; **gold CSVs are committed throughout**, so converged results are studyable without running anything.
- `Serpent_Model/TRISO_U900_PF40_R100.inp` is **git-LFS** — `lfs pull` or you get a pointer stub.
- **TMAP8** (github.com/idaholab/TMAP8) is **open source**, purpose-built for **hydrogen isotope transport in solids** — likely **more useful to your ZrH₂ work than MRAD**, and installable today.

```bash
# Meshes (Griffin and BISON use DIFFERENT meshes)
griffin-opt -i HPMR_OneSixth_Core_meshgenerator_tri.i --mesh-only out.e
# Steady state — required before ANY transient (provides restart/checkpoint)
mpirun -n 40 dire_wolf-opt -i HPMR_dfem_griffin_ss.i
# Null transient to verify SS convergence (everything should stay flat)
mpirun -n 40 transient_null/HPMR_dfem_griffin_trN.i
```

## 6.6 `SRP_interns2026` — you can't see it, and it's not your fault

**Verified:** anonymous fetch 404s; `gh repo view` and `gh api repos/...` both 404; repo search `total_count: 0`; all case variants 404.

GitHub returns **404, not 403**, for private repos you can't see — so a bare 404 can't distinguish "private" from "nonexistent." **But** `gh api users/RWillat` succeeds and reports **`"public_repos": 0`**. **So if it exists, it is necessarily private.**

Your `gh` **is** authenticated as **`hsinghind13`**, scopes `gist, read:org, repo, workflow`. **The `repo` scope is present — the token just has no grant.** Nothing about your tooling is broken.

**→ Ask RWillat to add `hsinghind13` as a collaborator.** Then follow the standing instruction: **own branches for experimenting; RWillat reviews commits.**

**About the account:** created **2026-06-24** (fits a summer-2026 cohort start), completely blank profile, zero public repos/gists/followers/orgs. Searches for "Willat" + Argonne/INL/LANL/nuclear/LinkedIn found **nothing**. Cannot be attributed to an institution from public sources.

**"SRP" is unresolved.** Ranked: **(a) "Space Reactor Program"** — most consistent, since the repo description says it serves *"the 20 kWe NEP fission reactor design team,"* which reads cleanly as "SRP interns 2026" *being* that team; NASA's 2026 missions are literally SR-1/LR-1. But no official NASA/DOE office by that name was found. **(b) Argonne "Student Research Participation"** — a real, confirmed program (10–11 weeks, early June–mid August, $400/week, spans divisions incl. Fission), but ANL's nuclear portfolio is terrestrial and no ANL space-reactor work surfaced. **Ruled out:** LANL's undergrad program is **UGS** (at LANL, "SRP" = the unrelated Stockpile Responsiveness Program); DOE **SULI** is separately named; CSNR/USRA runs "Summer Fellows." **Just ask.**

---

# 7. Resource verdicts

| Resource | From | Verdict | Why |
|---|---|---|---|
| **`Vogel_...ERNIAndTheModerators.pdf`** | Vogel | **THE SPEC** | Not background — the funded statement of work. 20261257CR, $100K. Everything else is its cited tooling |
| **nbragg** | Vogel | **Essential** | The fitting engine, ref [6] in the proposal |
| **save_roi** | Vogel | **Essential** | Upstream reduction; co-designed with nbragg |
| **NCrystal** | Vogel | **Essential** | The physics under nbragg, refs [8–10] |
| NEUWAVE PDF | Vogel | Useful, orienting | Not a NEUWAVE talk — Kittelmann's NCrystal satellite tutorial deck |
| Water/Ice notebook | Vogel | Useful **as method** | Teaches material composition, which you need (§5.4). The water is irrelevant |
| TSL_School TRIGA cell | Vogel | **Lowest — but instructive** | Its null result is the argument for your project's value (§5.5) |
| **CR-1870 (BRU)** | — | **High, with care** | Closest measured hardware; but see §6.3 — does *not* vindicate 26% |
| **Acta Astronautica paper** | Siddharth | **Doesn't support the claim** | 100 kWe Brayton review; no 20 kWe, no Stirling (§6.2) |
| **MRAD / VTB** | Siddharth | **Template only** | 2 MWt terrestrial; needs NCRC. The useful models are S8ER / KRUSTY / hpmr_h2 (§6.4) |
| **SRP_interns2026** | RWillat | **Blocked** | Private; request access as `hsinghind13` (§6.6) |

---

# 8. Corrections log

*Kept deliberately — the errors are instructive.*

**1. "BRU got 30%, so 26% is conservative — you have margin."** **Wrong.** I compared efficiency numbers without controlling for the **rejection temperature**. BRU's 30% rides on a **300 K cold end** that costs **4× the radiator area** of a 425 K one. The correct reading is the opposite: **26% is a converter number and is optimistic as a system figure.** *Lesson: in space power, efficiency and radiator area are the same trade. An efficiency quoted without its cold-end temperature is not a number.*

**2. The obvious-looking notebook (TRIGA) is the least useful; the one nobody linked (Transmission) is the most.** *Lesson: match the resource to your measurement geometry, not its topic label.*

**3. "The material must exist in NCrystal, it's a standard moderator."** **It doesn't.** No ZrH₂, no ZrH, nothing (§5.4). *Lesson: check the data library before planning around it.*

**4. Numbers corrected along the way:** BRU is **2.25–10.5 kWe** at **0.217/0.30/0.32** (not "~29 kWe / ~29%"); **BIPS is 1.3 kWe**, not 2–10; **SNAP-10A flew at 1.43%**, not 1.6%; **SP-100 is 2.5 MWt** (100/2500 = 4.0%).

**Open caveats:**
- The **Acta paper's full text was never read** (ScienceDirect blocked scraping); identity via Crossref PII index + OpenAlex. **26% may not literally appear in it** — pull it via UTK access before quoting the critique.
- **Phase boundaries and lattice parameters in §3.4 are from memory** with real literature spread. I verified the internal crystallography (d-spacings, I-centering, structure factors) and ε matches mp-24286 independently — **but δ's lattice parameter itself drifts with H content, which *is* the Zuzek relationship.** Pull the real numbers from Zuzek [7].
- **γ-ZrH's equilibrium status is genuinely contested.** An unexpected tetragonal phase near H/Zr ≈ 1 isn't necessarily a broken fit.

---

# 9. First moves

1. **Ask for repo access** as `hsinghind13`, and ask what SRP stands for. One message, unblocks a thread. (§6.6)
2. **Reply to Siddharth on efficiency.** He asked for other sources. The honest answer: his paper is a *100 kWe* Brayton review with no 20 kWe content, and 26% is a **converter** figure everywhere it appears (FSP 2010: 26% converter → 21.5% system; the 12 kWe TDU measured 25.5% electrically heated but **21.7% on a real NaK loop**). Recommend **~87 kWt (Stirling)** or **~100–111 kWt (Brayton)**. Send CR-1870 Table 2 as the closest measured hardware — noting its 300 K cold end. (§6.2–6.3)
3. **Apply for NCRC Level 1 now, naming Sockeye explicitly.** Longest lead time of anything here. (§6.5)
4. **Confirm the pellet phase with Vogel** — ε or δ. Determines your CIF, NCMAT, and expected edges. (§3.4)
5. **Get L and t₀ for the LANSCE flight path.** You can't convert TOF→λ without them. (§4.4)
6. **Do the `Transmission` notebook**, then `ncrystal2_advanced_01/02/03`. (§5.5)
7. **Build the ZrH₂ NCMAT and validate against EXFOR *before* fitting real data.** If you can't reproduce a measured σ_tot(λ), the fitted H number means nothing. (§5.4)
8. **Install TMAP8** — open source, hydrogen transport in solids, useful today. (§6.5)
9. `export NCRYSTAL_ONLINEDB_CACHEDIR=...` (§5.4)

---

# 10. The one-paragraph version

Space reactors must be small, so they need thermal neutrons, so they need hydrogen — and hydrogen is not just the best moderator available but the best one *possible*, because it alone shares the neutron's mass. ZrH₂ is the way to hold it at 1000 K, and it's really a hydrogen moderator with zirconium as scaffolding: hydrogen does 99.9% of the work. Hydride also hands the reactor its inherent safety, through a 137 meV quantum oscillator that upscatters neutrons when hot. But that same hydrogen migrates down the very temperature gradient the reactor creates, degrading exactly the property the design depends on, in a coupled feedback loop. Hydrogen is invisible to X-rays and brilliant to neutrons — by an accident of nuclear spin that simultaneously makes its cross-section enormous and its scattering length negative. So you fly time-of-flight neutrons through five pellets with different thermal histories, turn each pixel into a wavelength spectrum, fit crystal-structure-derived cross-sections to it, read hydrogen out of both the Bragg-edge structure and the incoherent baseline, validate against diffraction — and thereby test the transport models that a 20 kWe flight reactor is being designed with right now.
