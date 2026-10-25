"""Tests for the pretend-patient maker. Run:  python -m pytest tests -q"""
import pathlib, subprocess, sys, hashlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "sim" / "patients" / "make_patients.py"


def make(tmp, seed=7, patients=60):
    subprocess.run([sys.executable, str(SCRIPT), "--patients", str(patients), "--days", "60", "--seed", str(seed),
                    "--out", str(tmp.relative_to(ROOT))], check=True, capture_output=True)
    return {n: pd.read_csv(tmp / f"{n}.csv") for n in ["daily_features", "patients", "labels", "truth_daily"]}


def test_same_seed_gives_same_data(tmp_path_factory):
    a = ROOT / "data" / "test_a"; b = ROOT / "data" / "test_b"
    make(a); make(b)
    h = lambda p: hashlib.sha256((p / "daily_features.csv").read_bytes()).hexdigest()
    assert h(a) == h(b)


def test_worsening_starts_3_to_10_days_before_the_visit():
    d = make(ROOT / "data" / "test_a")["patients"]
    ev = d[d.event]
    assert len(ev) > 0
    assert ((ev.admit_day - ev.worsen_start_day).between(3, 10)).all()
    assert (ev.worsen_start_day >= 30).all()          # never inside the 30 baseline days


def test_event_patients_stop_at_the_visit_day():
    d = make(ROOT / "data" / "test_a")
    last = d["daily_features"].groupby("patient_id").day.max()
    ev = d["patients"][d["patients"].event].set_index("patient_id")
    assert (last.loc[ev.index] == ev.admit_day).all()


def test_no_secret_columns_leak_into_the_features():
    f = make(ROOT / "data" / "test_a")["daily_features"]
    for secret in ["congestion", "guest", "infection", "event", "admit_day", "worsen_start_day", "pill_missed"]:
        assert secret not in f.columns


def test_some_events_are_weight_silent_and_some_are_not():
    p = make(ROOT / "data" / "test_a", patients=200)["patients"]
    share = p[p.event].weight_silent.mean()
    assert 0.2 < share < 0.5
