#!/usr/bin/env python3
"""Prove the ERNI stack works BEFORE you point it at real data.

Every check runs on demo data that ships inside the repos -- nothing here
touches or needs your measurement files.

    python3 verify_install.py --repos ~/erni/repos --materials ~/erni/materials

Exits non-zero if any check fails.  A failure here means a wrong answer later,
not a crash later -- most of these failure modes are silent.
"""
import argparse
import gzip
import shutil
import sys
import traceback
from pathlib import Path

PASS, FAIL, SKIP = [], [], []


def run_isolated(code, *argv, timeout=300):
    """Run a snippet in a child process.

    NCrystal does its heavy lifting in C++, so a bad material or a machine that
    is out of memory can take the interpreter down with SIGKILL -- which no
    try/except can catch.  Isolating these checks means you get a readable
    verdict instead of a silently truncated run.
    """
    import subprocess
    p = subprocess.run([sys.executable, "-c", code, *map(str, argv)],
                       capture_output=True, text=True, timeout=timeout)
    if p.returncode == -9:
        raise RuntimeError("process KILLED (out of memory?) -- free some RAM and re-run")
    if p.returncode != 0:
        tail = (p.stderr or p.stdout).strip().splitlines()
        raise RuntimeError(tail[-1] if tail else f"exited {p.returncode}")
    return p.stdout.strip()


def check(name, critical=True):
    def deco(fn):
        sys.stdout.write(f"  {name:<52}")
        sys.stdout.flush()
        try:
            msg = fn()
            if msg == "SKIP":
                print("\033[33mSKIP\033[0m")
                SKIP.append(name)
            else:
                print(f"\033[32mPASS\033[0m  {msg or ''}")
                PASS.append(name)
        except Exception as e:
            print(f"\033[31mFAIL\033[0m  {type(e).__name__}: {e}")
            (FAIL if critical else SKIP).append(name)
            if "-v" in sys.argv:
                traceback.print_exc()
        return fn
    return deco


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", default=str(Path.home() / "erni/repos"))
    ap.add_argument("--materials", default=str(Path.home() / "erni/materials"))
    args = ap.parse_args()
    repos = Path(args.repos).expanduser()
    mats = Path(args.materials).expanduser()

    print("\n--- versions and pins " + "-" * 44)

    @check("imports resolve")
    def _():
        import NCrystal, nbragg, save_roi, numpy, pandas, lmfit, tifffile, roifile  # noqa
        return ""

    @check("numpy < 2  (numpy 2 breaks pandas here)")
    def _():
        import numpy as np
        assert np.__version__.startswith("1."), f"numpy {np.__version__} -- must be 1.x"
        return f"numpy {np.__version__}"

    @check("roifile < 2025  (2025 silently returns empty ROIs)")
    def _():
        import roifile
        year = int(str(roifile.__version__).split(".")[0])
        assert year < 2025, f"roifile {roifile.__version__} is too new"
        return f"roifile {roifile.__version__}"

    @check("ipywidgets 8.x  (7.x renders dead widgets in Lab 4)")
    def _():
        import ipywidgets
        assert ipywidgets.__version__.startswith("8."), ipywidgets.__version__
        return f"ipywidgets {ipywidgets.__version__}"

    print("\n--- NCrystal " + "-" * 53)

    @check("NCrystal stdlib resolves standard materials")
    def _():
        return run_isolated(
            "import NCrystal as NC\n"
            "[NC.createTextData(n) for n in "
            "('Al_sg225.ncmat','Zr_sg194.ncmat','Y_sg194.ncmat')]\n"
            "print('NCrystal', NC.__version__)")

    @check("NCrystal ships NO ZrH2/YH2  (expected -- you must build them)")
    def _():
        return run_isolated(
            "import NCrystal as NC\n"
            "m=[]\n"
            "for n in ('ZrH2.ncmat','ZrH_sg225.ncmat','YH2.ncmat'):\n"
            "    try: NC.createTextData(n)\n"
            "    except Exception: m.append(n)\n"
            "assert len(m)==3, 'unexpected: a hydride resolved from stdlib'\n"
            "print('confirmed absent')")

    @check("composed delta-ZrH2 loads, first edge = 5.52 A")
    def _():
        f = mats / "delta-ZrH2_SKELETON.ncmat"
        if not f.exists():
            return "SKIP"
        return run_isolated(
            "import sys, NCrystal as NC\n"
            "info = NC.createInfo(sys.argv[1] + ';dcutoff=1.0')\n"
            "bt = info.braggthreshold; si = info.getStructureInfo()\n"
            "assert 5.50 < bt < 5.54, 'first edge %.4f A, expected ~5.52' % bt\n"
            "assert si['spacegroup']==225, 'SG-%d, expected 225' % si['spacegroup']\n"
            "print('%.4f A, SG-225, %d atoms/cell' % (bt, si['n_atoms']))",
            f)

    print("\n--- save_roi " + "-" * 53)

    demo_tiff = repos / "save_roi/notebooks/image.tiff"
    demo_gz = repos / "save_roi/notebooks/image.tiff.gz"

    @check("demo TIFF present (gunzip if needed)")
    def _():
        if demo_tiff.exists():
            return f"{demo_tiff.stat().st_size/1e6:.0f} MB"
        if demo_gz.exists():
            with gzip.open(demo_gz, "rb") as fi, open(demo_tiff, "wb") as fo:
                shutil.copyfileobj(fi, fo)
            return f"extracted, {demo_tiff.stat().st_size/1e6:.0f} MB"
        return "SKIP"

    @check("save_roi loads a TOF stack")
    def _():
        from save_roi import load_tiff_stack
        if not demo_tiff.exists():
            return "SKIP"
        st = load_tiff_stack(str(demo_tiff))
        assert st.ndim == 3, f"got {st.ndim}D, need 3D (TOF, y, x)"
        return f"{st.shape} {st.dtype}"

    @check("save_roi extracts ROI spectra end to end")
    def _():
        import contextlib
        import io
        import tempfile
        import warnings
        import pandas as pd
        from save_roi import extract_roi_spectra
        roi = repos / "save_roi/notebooks/ROI2.zip"
        if not (demo_tiff.exists() and roi.exists()):
            return "SKIP"
        with tempfile.TemporaryDirectory() as td:
            with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
                warnings.simplefilter("ignore")
                extract_roi_spectra(tiff_path=str(demo_tiff), roi_path=str(roi),
                                    output_dir=td)
            csvs = sorted(Path(td).glob("*.csv"))
            assert csvs, "no CSV written"
            d = pd.read_csv(csvs[0])
            assert list(d.columns)[:3] == ["stack", "counts", "err"], list(d.columns)
            return f"{len(csvs)} ROI(s), {len(d)} TOF bins"

    print("\n--- nbragg " + "-" * 55)

    nb = repos / "nbragg/notebooks"

    @check("nbragg reads save_roi's 'stack' column natively")
    def _():
        from nbragg.data import Data
        import pandas as pd
        df = pd.DataFrame({"stack": [1, 2, 3], "counts": [10, 20, 30], "err": [3, 4, 5]})
        out = Data._read_counts(df)
        assert list(out.columns) == ["tof", "counts", "err"], list(out.columns)
        return "alias stack -> tof works"

    @check("nbragg builds transmission from counts")
    def _():
        import nbragg
        sig, ob = nb / "large_grain_steel_0deg.csv", nb / "openbeam.csv"
        if not (sig.exists() and ob.exists()):
            return "SKIP"
        d = nbragg.Data.from_counts(signal=str(sig), openbeam=str(ob),
                                    L=9.014, tstep=10e-6)
        t = d.table
        assert {"wavelength", "trans", "err"} <= set(t.columns), list(t.columns)
        return f"{len(t)} points, lambda {t.wavelength.min():.2f}-{t.wavelength.max():.2f} A"

    @check("nbragg -> NCrystal cross section builds")
    def _():
        mat = nb / "Fe_sg229_Iron-alpha_LGS.ncmat"
        if not mat.exists():
            return "SKIP"
        return run_isolated(
            "import sys, nbragg\n"
            "xs = nbragg.CrossSection({'a': {'mat': sys.argv[1]}})\n"
            "print('CrossSection constructed')",
            mat)

    @check("grouped-fit filename parsing (save_roi grid -> nbragg)")
    def _():
        from nbragg.data import Data
        names = [f"grid_8x8_x{x}_y{y}.csv" for x in (0, 8) for y in (0, 8)]
        idx = Data._extract_indices_from_filenames(names, "auto")
        assert sorted(idx) == [(0, 0), (0, 8), (8, 0), (8, 8)], idx
        return "x/y extracted, '8x8' prefix correctly ignored"

    print("\n" + "=" * 66)
    print(f"  PASS {len(PASS)}    SKIP {len(SKIP)}    FAIL {len(FAIL)}")
    if SKIP:
        print("  skipped: " + ", ".join(SKIP))
    if FAIL:
        print("\n  \033[31mFAILED:\033[0m " + "\n           ".join(FAIL))
        print("\n  Do NOT run real data until these pass. Re-run with -v for tracebacks.")
        return 1
    print("\n  \033[32mStack verified.\033[0m Proceed to RUNBOOK.md step 1.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
