# δ-YH₂ scattering kernels — ENDF/B-VIII.1

Ten NCMAT files, one per evaluated temperature: **293.6, 400, 500, 600, 700, 800,
1000, 1200, 1400, 1600 K**.

## Provenance

| | |
|---|---|
| source | ENDF/B-VIII.1 thermal scattering sublibrary |
| files | `tsl_H(YH2)_0005` (MAT 5), `tsl_Y(YH2)_0055` (MAT 55) |
| evaluators | Wormald, Zerkle & Holmes, Naval Nuclear Laboratory, EVAL-FEB24 |
| underlying work | Zerkle & Holmes, *NDS* **148**, 1 (2018); *EPJ Web Conf.* **2** (2021) |
| method | phonon DOS for H and Y from MedeA (DFT); kernels via NJOY LEAPR |
| ENDF download | https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.1/tsl/ |
| NCMAT conversion | https://github.com/mctools/ncrystal-extra/tree/master/data/unvalidated |

Each file carries `type scatknl` — the full S(α,β) scattering kernel — for both H
and Y. Not a Debye approximation, and not a bare VDOS.

## Local modification — read before use

The ncrystal-extra files are `inelasticonly_dummydensity`: they carry a
placeholder `@DENSITY` of 1 g/cm³ and therefore **no coherent elastic scattering
and no Bragg edges**. The upstream file says so itself:

```
@DENSITY
  1 g_per_cm3 #FIXME. Dummy number!!! (update or add unit cell sections...)
```

The `@CELL` / `@SPACEGROUP` / `@ATOMPOSITIONS` block was grafted on locally from
`../delta-YH2_SKELETON.ncmat` — fluorite, SG-225, a = 5.203 Å, 8×H + 4×Y per cell
— which restores the elastic part. Nothing else was changed. The `NCMAT v2`
version header was kept, and the cell written as explicit `lengths`/`angles`
rather than the newer `cubic` shorthand, so the files load on older NCrystal.

Upstream places these under `data/unvalidated/`. **They are not validated, and
neither is the graft.**

## Verify before trusting

None of this was executed — NCrystal could not be run on the machine where these
files were assembled.

1. `NC.load('YH2_sg225_T293.6K.ncmat;temp=293.6K')` — number density should come
   out near **0.0567 atoms/Å³** (8 H + 4 Y in a 5.203 Å cube). A wrong lattice
   constant or a failed graft shows up here first.
2. First Bragg edge, the (111), should sit near **6.01 Å**. If there are no edges
   at all, the graft did not take.
3. Total cross section against EXFOR.

## Using them

Each file is valid at **one temperature only** — load with a matching `temp=`.
For the M080924J campaign: 293.6 K for the RT anchors, 1200 K for the 950 °C hold
(1223 K, so interpolate or take the nearest).

## The stoichiometry caveat

From the evaluation literature: substoichiometric YH₂₋ₓ deviates from
stoichiometric YH₂ by as much as **30% in elastic and 60% in inelastic** cross
section across YH₁.₃₁–YH₁.₉₁.

**These files are stoichiometric YH₂.** If the pellet is substoichiometric — which
is what the experiment exists to measure — the *shape* of Σ(λ) is wrong, not just
its scale. A pure scale error largely cancels in a before/after difference; a
shape error does not cancel in the same way, and it is the same class of problem
that produced χ²ᵥ = 38 on the ZrH₂ fit.

Worth checking whether the substoichiometric TSL set (YH₁.₃₁ through YH₁.₉₁ in
steps of ≈0.1, produced for MCNP) is obtainable — with it, H/Y could in principle
be fitted from the cross-section shape rather than from path length alone.
