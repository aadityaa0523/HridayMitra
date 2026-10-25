"""The stool bridge's no-hardware mode writes a live log the dashboard can read, with the same lights as the engine."""
import json, pathlib, subprocess, sys
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import alert_engine as A


def test_simulate_writes_live_log_with_engine_lights():
    pid = pd.read_csv(ROOT / "data/processed/realworld/patients.csv").patient_id.iloc[0]   # the bridge reads this cohort first
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/stool_bridge.py"), "--simulate", pid, "--delay", "0"],
                   check=True, capture_output=True)
    log = pd.read_csv(ROOT / "data/live" / f"{pid}.csv")
    g = pd.read_csv(ROOT / "data/processed/realworld/daily_features.csv"); g = g[g.patient_id == pid].reset_index(drop=True)
    T = json.loads((ROOT / "engine/frozen_params_v3.json").read_text())["T"]
    assert len(log) == len(g) and (log.light.to_numpy() == A.lights(A.scores(g), T)).all()
    (ROOT / "data/live" / f"{pid}.csv").unlink()


def test_firmware_nan_is_parsed():
    sys.path.insert(0, str(ROOT / "tools"))
    import stool_bridge as B
    assert pd.isna(B.parse('{"t":"checkin","spo2":nan,"light":1}')["spo2"])
