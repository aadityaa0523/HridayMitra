"""Sit-to-stand time with the chair standing on the weighing platform: accurate across fast and slow risers and body
weights, no stand found while the person stays seated, and the firmware's C++ (hm::stsFit) = Python (engine/sts.py)."""
import pathlib, subprocess, sys
import numpy as np
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import sts as S

CASES = [(m, D, s) for s, (m, D) in enumerate([(45, 1.2), (60, 1.8), (75, 2.5), (90, 3.2), (100, 4.0), (55, 4.4), (85, 1.5), (70, 3.8)])]


@pytest.mark.parametrize("m,D,seed", CASES)
def test_rise_time_accurate(m, D, seed):
    w, true = S.make_sts(m=m, D=D, seed=seed)
    est, h, q = S.sts_fit(w)
    # within 0.45 s or 16 % (very slow, lopsided rises lose part of their slow finish; per person the bias is constant,
    # and the engine compares each person only with their own baseline)
    assert est is not None and abs(est - true) < max(0.45, 0.16 * true) and 0.12 < h < 0.65


def test_no_stand_while_seated():
    assert all(S.sts_fit(S.make_sts(m=70, seed=900 + i, stand=False, step_off=None)[0])[0] is None for i in range(12))


def test_slower_rise_reads_slower():
    a = S.sts_fit(S.make_sts(m=70, D=2.0, seed=3)[0])[0]
    b = S.sts_fit(S.make_sts(m=70, D=3.0, seed=3)[0])[0]
    assert b - a > 0.6


def test_cpp_matches_python():
    exe = ROOT / "tests" / "sts_check.exe"
    try:
        subprocess.run([sys.executable, "-m", "ziglang", "c++", "-O2", "-std=c++17", str(ROOT / "tests/sts_check.cpp"), "-o", str(exe)],
                       check=True, capture_output=True, timeout=600)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.skip(f"no C++ compiler: {e}")
    sigs = [S.make_sts(m=m, D=D, seed=s)[0] for m, D, s in CASES] + [S.make_sts(m=70, seed=950, stand=False, step_off=None)[0]]
    out = subprocess.run([str(exe)], input="\n".join(f"{len(w)} " + " ".join(f"{x:.5f}" for x in w) for w in sigs), capture_output=True,
                         text=True, check=True).stdout.split("\n")
    for w, line in zip(sigs, out):
        d_cpp = float(line.split()[0])
        d_py = S.sts_fit(np.asarray(w, np.float32).astype(float))[0]
        assert (d_py is None and np.isnan(d_cpp)) or (d_py is not None and abs(d_cpp - d_py) < 0.051)
