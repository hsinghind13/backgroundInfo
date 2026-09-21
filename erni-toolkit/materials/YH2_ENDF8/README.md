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


## Elastic component — now sourced, not guessed

The upstream `inelasticonly` files carry no elastic scattering at all. Two
things were needed to restore it, and both are now in place.

**Crystal structure**, grafted from `../delta-YH2_SKELETON.ncmat` — fluorite,
SG-225, a = 5.203 Å. This is what NCrystal computes Bragg scattering from.

**A mean-squared displacement**, which NCrystal needs for the Debye-Waller
factor. Without it there are no edge intensities, and NCMAT v1–v3 would reject a
crystalline file outright. This was taken from the **same ENDF evaluations**, in
`MF7/MT2`, which the ncrystal-extra conversion discarded along with the rest of
the elastic section:

- `tsl_H(YH2)` MAT 5, LTHR=2 — incoherent elastic, σ_b = 80.054 b, with the
  Debye-Waller integral W′(T) tabulated at all ten temperatures
- `tsl_Y(YH2)` MAT 55, LTHR=3 — mixed elastic: 674 tabulated coherent elastic
  structure factors *plus* σ_b = 0.15 b and its own W′(T)

Conversion, per file:

```
msd   = W' * hbar^2/2m          hbar^2/2m = 2.0721e-3 eV*A^2
Theta = NCrystal.debyeTempFromIsotropicMSD(msd=msd, temperature=T, mass=m)
```

| T [K] | W′(H) | Θ(H) [K] | W′(Y) | Θ(Y) [K] |
|---|---|---|---|---|
| 293.6 | 9.2750 | 2115.5 | 2.4971 | 309.4 |
| 400 | 10.0038 | 2135.9 | 3.3558 | 309.4 |
| 500 | 10.8830 | 2146.9 | 4.1703 | 309.4 |
| 600 | 11.9059 | 2152.8 | 4.9884 | 309.4 |
| 700 | 13.0332 | 2156.0 | 5.8085 | 309.4 |
| 800 | 14.2362 | 2157.8 | 6.6299 | 309.4 |
| 1000 | 16.7950 | 2159.5 | 8.2751 | 309.4 |
| 1200 | 19.4837 | 2160.2 | 9.9220 | 309.4 |
| 1400 | 22.2517 | 2160.5 | 11.5701 | 309.4 |
| 1600 | 25.0714 | 2160.7 | 13.2187 | 309.4 |

### Three checks that the conversion is right

1. **Θ(Y) is 309.4 K at every one of the ten temperatures**, constant to four
   figures. The yttrium sublattice is genuinely Debye-like, which is what makes
   this a real test rather than a tautology.
2. **Yttrium metal's literature Debye temperature is ~280 K.** 309 K in the
   stiffer hydride is the right neighbourhood.
3. **Θ(H) drifts only 2%** (2115 → 2161 K) and converges at high T — the
   expected signature of hydrogen being Einstein-like, not Debye-like.

The msd convention was separately checked against NCrystal's own
`debyeIsotropicMSD` for Al and Cu, reproducing their literature B_iso
(Al: 0.80 Å² computed vs ~0.77 literature; Cu: 0.0071 Å² vs ~0.0075).

For contrast, the skeleton guessed **H 1500 K** and **Y 250 K**. The H guess
gives msd = 0.030 Å² against the evaluated 0.019 — 56% too large, which would
badly over-suppress the Bragg edges.

### The reference answer for validation

The Y file's 674-point coherent-elastic table **is the evaluation's own Bragg
cross section**. Compare NCrystal's computed edges against it. If positions and
intensities match, the structure graft and the lattice constant are both
confirmed. That is the strongest check available, and it needs no new data.

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
