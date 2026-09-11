#!/usr/bin/env python3
"""How much does Sigma move per unit H/Zr?  ->  converts a Sigma*z map into hydrogen.

    python3 hydrogen_sensitivity.py ZrH1p6_bct.ncmat

NOT TESTED -- written on a machine where NCrystal could not run.  Check the
sanity block at the end before trusting the numbers.

Method: at the wavelengths you actually have (< ~1.8 A) hydrogen's INCOHERENT
scattering dominates and is structure-insensitive, so
      Sigma(x) ~= n_Zr * ( sigma_Zr + x * sigma_H )
We get sigma_H by differencing the hydride against pure Zr metal.
"""
import sys
import numpy as np
import NCrystal as NC

mat = sys.argv[1] if len(sys.argv) > 1 else "ZrH1p6_bct.ncmat"
WL  = np.array([0.4, 0.8, 1.2, 1.6, 2.0])       # your usable range

def sigma_and_n(cfg):
    m = NC.load(cfg)
    n = m.info.numberdensity                     # atoms per Angstrom^3
    s = np.array([m.scatter.xsect(wl=w) + m.absorption.xsect(wl=w) for w in WL])
    return s, n, m.info

s_hyd, n_hyd, info_hyd = sigma_and_n(mat)
s_zr,  n_zr_metal, _   = sigma_and_n("Zr_sg194.ncmat")

# atom fractions in the hydride, read from the file itself
fracs = {di.atomData.displayLabel(): di.fraction for di in info_hyd.dyninfos}
fH  = fracs.get("H", 2/3)
fZr = fracs.get("Zr", 1/3)
x_file = fH / fZr                                # H/Zr of the .ncmat as written

# per-atom sigma is averaged over the compound; recover per-element
sigma_per_formula = s_hyd * (1 + x_file)         # sigma per Zr + x*H
sigma_H = (sigma_per_formula - s_zr) / x_file    # per H atom
n_Zr = n_hyd * fZr                               # Zr atoms per A^3

print(f"material              : {mat}")
print(f"H/Zr in the file      : {x_file:.3f}")
print(f"number density        : {n_hyd:.5f} atoms/A^3   (Zr sublattice {n_Zr:.5f})")
print()
print(" lambda   sigma_H     Sigma(x=1.6)   dSigma/dx   frac. change per dx=0.1")
print(" [A]      [barn]      [1/cm]         [1/cm]      [%]")
for i, w in enumerate(WL):
    dSdx  = n_Zr * sigma_H[i]                    # Sigma[1/cm] = n[A^-3] * sigma[barn]
    Sig16 = n_Zr * (s_zr[i] + 1.6 * sigma_H[i])
    print(f" {w:4.1f}    {sigma_H[i]:8.2f}   {Sig16:9.3f}     {dSdx:8.3f}    {100*0.1*dSdx/Sig16:6.2f}")

print()
print("USE IT:  dx  =  d(Sigma*z) / (dSigma/dx * z)")
print("         relative form (z cancels, needs no thickness):")
print("           dx / x  =  d(Sigma*z) / (Sigma*z) * [Sigma / (x * dSigma/dx)]")
print()
print("SANITY CHECKS before trusting any of this:")
print(f"  - Sigma(x=1.6) at 1.2 A should be roughly 2-4 /cm for a hydride")
print(f"  - sigma_H should be ~80 barn at short lambda (H bound incoherent)")
print(f"  - number density for ZrH2 should be ~0.09 atoms/A^3")
