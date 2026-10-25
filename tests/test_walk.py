"""6-minute walk test on the amulet: accurate step counts on synthetic walking, no steps from things that are not
walking, and the C++ firmware code (walk_core.h) counts the same as Python (zig; skipped if missing)."""
import pathlib, subprocess, sys
import numpy as np
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import signals as S


@pytest.mark.parametrize("cadence", [60, 75, 90, 105, 120])
def test_walk_steps_accurate(cadence):
    for amp in (0.15, 0.3):
        mag, true = S.make_walk(cadence, 360, amp=amp, seed=cadence)
        assert abs(S.walk6(mag)[1] / true - 1) < 0.05


@pytest.mark.parametrize("kind", ["sitting", "fidget", "auto-rickshaw", "turning in bed"])
def test_no_steps_when_not_walking(kind):
    assert sum(S.walk6(S.make_still(kind, seed=s))[0] for s in range(3)) == 0


def test_best_six_minutes_found_in_a_day():
    short, n1 = S.make_walk(110, 180, seed=1)
    test, n2 = S.make_walk(95, 360, seed=2)
    total, best = S.walk6(np.concatenate([short, S.make_still("sitting", 300), test]))
    assert abs(best / n2 - 1) < 0.05 and abs(total / (n1 + n2) - 1) < 0.05


def test_cpp_walk_matches_python():
    exe = ROOT / "tests" / "walk_check.exe"
    try:
        subprocess.run([sys.executable, "-m", "ziglang", "c++", "-O2", "-std=c++17", str(ROOT / "tests/walk_check.cpp"),
                        "-o", str(exe)], check=True, capture_output=True, timeout=600)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.skip(f"no C++ compiler: {e}")
    sig = [S.make_walk(c, 120, amp=a, seed=c)[0] for c in (70, 100) for a in (0.08, 0.2)] + [S.make_still("auto-rickshaw", 120)]
    win = np.concatenate([m[:len(m) // 100 * 100] for m in sig]).astype(np.float32).reshape(-1, 100)
    out = subprocess.run([str(exe)], input="\n".join(" ".join(f"{v:.7g}" for v in w) for w in win), capture_output=True,
                         text=True, check=True).stdout.split()
    cpp, py = np.array(out, float), np.array([S.walk_window(w) for w in win])
    assert len(cpp) == len(py) and np.mean(np.abs(cpp - py) < 0.01) >= 0.98
