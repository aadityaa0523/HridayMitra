"""Software-in-the-loop proof of the REAL stool firmware: it is compiled on the laptop against an emulated world
(tests/sil/mock: body impedance through the ADC, HX711 bits, MAX30102 FIFO, SIM800L AT commands, buttons, BLE, flash)
and lives through a scripted month (worsening, care loop, missed day, guest, lifted foot, low battery, SOS, power cut,
network outage, second user). Every claim must PASS, and every light the stool decided must equal the Python engine's
light for the same readings. Needs zig (pip install ziglang); skipped otherwise."""
import json, pathlib, subprocess, sys
import numpy as np
import pandas as pd
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
SIL = ROOT / "tests" / "sil"
sys.path.insert(0, str(ROOT / "engine"))
import alert_engine as A

COLS = ["weight_kg", "leg_z_ohm", "trunk_z_ohm", "leg_ewi", "pulse_bpm", "spo2", "standup_s", "night_rr", "night_situps",
        "activity_min", "breathless", "orthopnea", "took_pills"]


@pytest.fixture(scope="module")
def run():
    exe = SIL / "sil.exe"
    try:
        subprocess.run([sys.executable, "-m", "ziglang", "c++", "-O2", "-std=c++17", "-Wno-everything", "-Imock",
                        "-I../../firmware/hridaymitra_stool", "sil_main.cpp", "-o", str(exe)],
                       cwd=SIL, check=True, capture_output=True, timeout=900)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.skip(f"no C++ compiler: {e}")
    return subprocess.run([str(exe)], cwd=SIL, capture_output=True, text=True, timeout=900)


def test_every_firmware_claim_passes(run):
    print(run.stdout)
    assert run.returncode == 0 and "FAIL" not in run.stdout and run.stdout.count("PASS") >= 39


def test_firmware_lights_equal_python_engine(run):
    rows = [json.loads(l.replace(":nan", ":NaN").replace(":-nan", ":NaN")) for l in (ROOT / "reports/sil_checkins.jsonl").read_text().splitlines()]
    p1 = [(r["day"], r["report"]) for r in rows if r["report"]["id"] == "P001"]
    table, lights, last = [], [], None
    for day, rep in p1:                                    # the stool fills each missed calendar day with "no check-in"
        if last is not None:
            table += [dict.fromkeys(COLS, np.nan) for _ in range(day - last - 1)]
        table.append({c: rep.get(c, np.nan) for c in COLS}); lights.append(rep["light"]); last = day
    g = pd.DataFrame(table)
    T = json.loads((ROOT / "engine/frozen_params_v3.json").read_text())["T"]
    py = A.lights(A.scores(g), T)[g.weight_kg.notna() | g.leg_z_ohm.notna() | g.breathless.notna()]
    assert len(py) == len(lights) and (np.array(lights) == py).all(), (lights, list(py))
