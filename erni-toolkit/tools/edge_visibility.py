# edge_visibility.py -- is there an edge worth calibrating on, and is there
# any flux where it sits?  Answer this BEFORE writing calibration code.
#
#   python3 edge_visibility.py
#
# Pure NCrystal prediction. No measured data, nothing fitted.

import numpy as np
import matplotlib.pyplot as plt
import NCrystal as NC

NCMAT_AL = "nbragg/ncmat/Al_sg225.ncmat"
NCMAT_ZRH = "nbragg/ncmat/ZrH1p6_bct.ncmat"

AL_PATH_CM = 0.20      # 2 walls x 1 mm. THOR TO CONFIRM -- ask #7, and Al vs TZM
ZRH_PATH_CM = 1.0      # pellet chord, from P_peak ~ 0.98 cm

WL = np.linspace(0.5, 8.0, 3000)

def sigma(cfg):
    m = NC.load(cfg)
    s = np.array([m.scatter.xsect(wl=w) + m.absorption.xsect(wl=w) for w in WL])
    return s, m.info.numberdensity

s_al, n_al = sigma(NCMAT_AL)
s_zrh, n_zrh = sigma(NCMAT_ZRH)

# Sigma [1/cm] = n [atoms/A^3] * sigma [barn]
Sig_al = n_al * s_al
Sig_zrh = n_zrh * s_zrh
OT_al = Sig_al * AL_PATH_CM
OT_zrh = Sig_zrh * ZRH_PATH_CM

def edge_step(wl, ot, lam, half=0.08):
    lo = (wl > lam - half) & (wl < lam - 0.005)
    hi = (wl > lam + 0.005) & (wl < lam + half)
    a = float(np.mean(ot[lo]))
    b = float(np.mean(ot[hi]))
    return a, b, a - b

print("path lengths assumed:  Al", AL_PATH_CM, "cm   ZrH", ZRH_PATH_CM, "cm")
print()
for lab, ot, lam in [("Al (111)", OT_al, 4.676), ("eps-ZrH2 (101)", OT_zrh, 5.532)]:
    a, b, d = edge_step(WL, ot, lam)
    T_a = np.exp(-a)
    T_b = np.exp(-b)
    print(lab, "at", lam, "A")
    print("   optical thickness below/above edge :", round(a, 4), "/", round(b, 4))
    print("   step in Sigma*z                    :", round(d, 4))
    print("   step in transmission               :", round(float(T_b - T_a), 5),
          " = ", round(float(100 * (T_b - T_a)), 3), "%")
    n3 = 9.0 / max(float(T_b - T_a) ** 2, 1e-12)
    print("   counts needed in the ROI for 3 sigma:", format(n3, ".3g"))
    print()

fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
a0 = ax[0]
a0.plot(WL, Sig_al, label="Al")
a0.plot(WL, Sig_zrh, label="ZrH (file)")
a0.axvline(4.676, color="C0", ls=":", lw=0.8)
a0.axvline(5.532, color="C1", ls=":", lw=0.8)
a0.axvline(3.5, color="r", ls="--", lw=1.0)
a0.set_xlabel("wavelength [A]")
a0.set_ylabel("Sigma [1/cm]")
a0.set_title("red = current wlmax; dotted = first edges")
a0.grid(alpha=0.3)
a0.legend(fontsize=8)

a1 = ax[1]
a1.plot(WL, np.exp(-OT_al), label="Al can, 2 walls")
a1.plot(WL, np.exp(-OT_zrh), label="ZrH pellet, 1 cm")
a1.axvline(4.676, color="C0", ls=":", lw=0.8)
a1.axvline(5.532, color="C1", ls=":", lw=0.8)
a1.axvline(3.5, color="r", ls="--", lw=1.0)
a1.set_xlabel("wavelength [A]")
a1.set_ylabel("transmission")
a1.set_title("what the edges actually look like in T")
a1.grid(alpha=0.3)
a1.legend(fontsize=8)

plt.tight_layout()
plt.show()
