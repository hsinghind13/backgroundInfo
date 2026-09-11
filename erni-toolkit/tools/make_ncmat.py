#!/usr/bin/env python3
"""Compose hydride .ncmat files that NCrystal does not ship.

NCrystal's stdlib has CaH2, MgH2, SrH2, LiH -- but no ZrH2, no ZrH, no YH2.
nbragg cannot fit what it cannot load, so these must be built before any
transmission analysis can run.

    python3 make_ncmat.py --skeletons          # placeholder Debye, structure only
    python3 make_ncmat.py --vdos H_dos.csv ... # the real thing

WARNING ON SKELETONS
--------------------
--skeletons emits materials whose hydrogen dynamics are a Debye approximation.
They are useful for checking Bragg-edge POSITIONS (which depend only on the
lattice) and for smoke-testing the pipeline.  They are NOT valid for fitting
hydrogen content, because the H incoherent/inelastic cross section -- the very
thing that carries the hydrogen signal -- is wrong.  Replace the DYNINFO with a
real VDOS before any quantitative result.
"""
import argparse
import sys

try:
    from NCrystal.ncmat import NCMATComposer
except ImportError:
    sys.exit("NCrystal not importable -- run verify_install.py first.")


# --- structures -------------------------------------------------------------
# NCMAT @ATOMPOSITIONS wants EVERY atom in the conventional cell, not the
# asymmetric unit.  Giving only the asymmetric unit makes spglib report the
# wrong space group and .write() will refuse the file.

FCC_METAL = [(0, 0, 0), (0, .5, .5), (.5, 0, .5), (.5, .5, 0)]
TETRA_8C  = [(.25, .25, .25), (.25, .75, .75), (.75, .25, .75), (.75, .75, .25),
             (.25, .75, .25), (.25, .25, .75), (.75, .75, .75), (.75, .25, .25)]

STRUCTURES = {
    # delta-ZrH2: fluorite type, Fm-3m.  a from Mehta Fig.3 (H/Zr ~1.6 -> ~4.78 A)
    "delta-ZrH2": dict(metal="Zr", a=4.78, sg=225,
                       metal_sites=FCC_METAL, h_sites=TETRA_8C,
                       note="delta-ZrH2, fluorite (CaF2) type, Fm-3m"),
    # delta-YH2: same structure type; a = 5.203 A, and NOTE the lattice parameter
    # is nearly blind to H content across 1.50 < H/Y < 2.00 (0.13% span).
    "delta-YH2":  dict(metal="Y", a=5.203, sg=225,
                       metal_sites=FCC_METAL, h_sites=TETRA_8C,
                       note="delta-YH2, fluorite type, Fm-3m"),
}

# Placeholder Debye temperatures (K).  PLACEHOLDERS ONLY.
DEBYE = {"Zr": 250, "Y": 250, "H": 1500}


def build(name, spec, vdos=None, a_override=None):
    a = a_override if a_override else spec["a"]
    c = NCMATComposer()
    c.set_cellsg_cubic(a, spacegroup=spec["sg"])
    c.set_atompos([(spec["metal"], *p) for p in spec["metal_sites"]]
                  + [("H", *p) for p in spec["h_sites"]])

    if vdos:
        for el, (egrid, dens) in vdos.items():
            c.set_dyninfo_vdos(el, egrid, dens)
    else:
        c.set_dyninfo_debyetemp(spec["metal"], debye_temp=DEBYE[spec["metal"]])
        c.set_dyninfo_debyetemp("H", debye_temp=DEBYE["H"])
    return c


def load_vdos_csv(path):
    """Read a two-column CSV: energy_eV, density.  One file per element."""
    import numpy as np
    d = np.loadtxt(path, delimiter=",", skiprows=1)
    egrid, dens = d[:, 0], d[:, 1]
    if egrid.max() < 0.160:
        print(f"  !! WARNING {path}: grid stops at {egrid.max()*1000:.0f} meV. "
              "The H optical peak sits at 140-145 meV; a grid below ~160 meV "
              "truncates the feature that makes hydrogen visible.")
    return egrid, dens


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skeletons", action="store_true",
                    help="emit placeholder-Debye materials (structure only)")
    ap.add_argument("--material", default=None, choices=sorted(STRUCTURES),
                    help="build just one (default: all)")
    ap.add_argument("--a", type=float, default=None,
                    help="override lattice parameter in Angstrom")
    ap.add_argument("--vdos-metal", default=None, help="CSV: energy_eV,density for the metal")
    ap.add_argument("--vdos-h", default=None, help="CSV: energy_eV,density for hydrogen")
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()

    if not args.skeletons and not (args.vdos_metal and args.vdos_h):
        ap.error("give --skeletons, or both --vdos-metal and --vdos-h")

    names = [args.material] if args.material else sorted(STRUCTURES)
    for name in names:
        spec = STRUCTURES[name]
        vdos = None
        if args.vdos_metal:
            vdos = {spec["metal"]: load_vdos_csv(args.vdos_metal),
                    "H": load_vdos_csv(args.vdos_h)}

        suffix = "_SKELETON" if args.skeletons else ""
        out = f"{args.outdir.rstrip('/')}/{name}{suffix}.ncmat"
        c = build(name, spec, vdos=vdos, a_override=args.a)
        c.write(out)          # runs spglib verification; refuses a wrong structure
        print(f"wrote {out}")
        print(f"   {spec['note']}, a = {args.a or spec['a']} A")
        d111 = (args.a or spec["a"]) / 3 ** 0.5
        print(f"   predicted first Bragg edge 2*d(111) = {2*d111:.4f} A")
        if args.skeletons:
            print("   PLACEHOLDER DYNINFO -- positions only, not valid for fitting H")
        print()


if __name__ == "__main__":
    main()
