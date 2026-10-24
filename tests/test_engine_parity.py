"""The ESP32 engine (firmware/hridaymitra_stool/engine_core.h) must give the same daily light as the Python engine.
Compiled on the laptop with zig (pip install ziglang); skipped if zig is missing."""
import json, pathlib, subprocess, sys
import numpy as np
import pandas as pd
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import alert_engine as A

COLS = ["weight_kg", "leg_z_ohm", "trunk_z_ohm", "pulse_bpm", "night_rr", "spo2", "activity_min", "standup_s",
        "breathless", "orthopnea", "night_situps"]
EXE = ROOT / "tests" / "engine_parity.exe"


def build():
    try:
        subprocess.run([sys.executable, "-m", "ziglang", "c++", "-O2", "-std=c++17", str(ROOT / "tests/engine_parity.cpp"),
                        "-o", str(EXE)], check=True, capture_output=True, timeout=600)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.skip(f"no C++ compiler: {e}")


def test_cpp_engine_matches_python():
    build()
    T = json.loads((ROOT / "engine/frozen_params_v2.json").read_text())["T"]
    f = pd.read_csv(ROOT / "data/processed/daily_features.csv")
    ids = f.patient_id.unique()[:60]
    f = f[f.patient_id.isin(ids)]
    out = subprocess.run([str(EXE)], input=f[["patient_id"] + COLS].to_csv(index=False, header=False, na_rep=""),
                         capture_output=True, text=True, check=True).stdout
    cpp = pd.read_csv(pd.io.common.StringIO(out), names=["patient_id", "day", "light"])
    py = np.concatenate([A.lights(A.scores(g.reset_index(drop=True)), T) for _, g in f.groupby("patient_id", sort=False)])
    agree = float((cpp.light.to_numpy() == py).mean())
    print(f"C++ vs Python daily lights: {agree:.4%} agree over {len(py)} patient-days")
    assert agree >= 0.995
