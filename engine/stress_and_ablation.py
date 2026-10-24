"""STRESS TESTS AND ABLATIONS with the FROZEN v2 engine (no retuning).
Ablation = switch signals off to see what each one adds. Stress = make life messier to see where it breaks.
Every stress case is also run on the SCALE-HF weight rule, so "does it still beat the rule?" is answered each time.
Uses the external real-world cohort: all 100 sick patients + 300 stable ones (fixed seed). 95% ranges re-draw patients.
Run:  python engine/stress_and_ablation.py
"""
import json, pathlib, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import evaluate as E, alert_engine as A, baselines as B

ROOT = pathlib.Path(__file__).resolve().parents[1]
T = json.loads((ROOT / "engine" / "frozen_params_v3.json").read_text())["T"]
f = pd.read_csv(ROOT / "data/processed/realworld/daily_features.csv")
p = pd.read_csv(ROOT / "data/processed/realworld/patients.csv")
rng = np.random.default_rng(7)
keep = list(p[p.event].patient_id) + list(rng.choice(p[~p.event].patient_id, 300, replace=False))
f, p = f[f.patient_id.isin(keep)].reset_index(drop=True), p[p.patient_id.isin(keep)]
STOOL = ["weight_kg", "leg_z_ohm", "trunk_z_ohm", "pulse_bpm", "spo2", "standup_s"]
AMULET = ["night_rr", "night_situps", "activity_min"]


def off(cols):
    def fn(x):
        x = x.copy(); x[cols] = np.nan; return x
    return fn


def missing(frac):
    def fn(x):
        x = x.copy(); m = np.random.default_rng(1).random(len(x)) < frac
        x.loc[m, x.columns[2:]] = np.nan; return x
    return fn


def guests(frac):
    def fn(x):
        x = x.copy(); r = np.random.default_rng(2); m = r.random(len(x)) < frac
        x.loc[m, "weight_kg"] = r.normal(70, 12, m.sum()); x.loc[m, "leg_z_ohm"] = r.normal(620, 100, m.sum())
        x.loc[m, "pulse_bpm"] = r.normal(76, 9, m.sum()); return x
    return fn


def wet(frac):
    def fn(x):
        x = x.copy(); m = np.random.default_rng(3).random(len(x)) < frac
        x.loc[m, "leg_z_ohm"] *= 0.95; return x
    return fn


def amulet_off(frac):
    def fn(x):
        x = x.copy(); m = np.random.default_rng(4).random(len(x)) < frac
        x.loc[m, AMULET] = np.nan; return x
    return fn


def power_cuts(per_month):
    """Power cuts / travel: whole runs of 2-5 days with no stool and no amulet upload."""
    def fn(x):
        x = x.copy(); r = np.random.default_rng(5)
        for _, idx in x.groupby("patient_id").groups.items():
            idx = list(idx)
            for _ in range(r.poisson(per_month * len(idx) / 30)):
                s = r.integers(0, len(idx)); x.loc[idx[s:s + r.integers(2, 6)], x.columns[2:]] = np.nan
        return x
    return fn


def electrode_ageing(pct_per_month):
    """Foot plates slowly corrode: leg reading creeps DOWN (the fluid direction), the worst case for false alerts."""
    def fn(x):
        x = x.copy(); x["leg_z_ohm"] *= 1 - pct_per_month / 100 * x["day"] / 30; return x
    return fn


def everything(x):
    for fn in (missing(0.20), guests(0.05), wet(0.10), amulet_off(0.30), power_cuts(1), electrode_ageing(1)):
        x = fn(x)
    return x


CASES = [
    ("Full engine (frozen)", "baseline", lambda x: x),
    ("Without leg and chest impedance", "ablation", off(["leg_z_ohm", "trunk_z_ohm"])),
    ("Without weight", "ablation", off(["weight_kg"])),
    ("Without amulet", "ablation", off(AMULET)),
    ("Without symptom answers", "ablation", off(["breathless", "orthopnea"])),
    ("Weight only", "ablation", off([c for c in STOOL + AMULET + ["breathless", "orthopnea"] if c != "weight_kg"])),
    ("30% of days missing", "stress", missing(0.30)),
    ("50% of days missing", "stress", missing(0.50)),
    ("10% guest days", "stress", guests(0.10)),
    ("15% wet-feet days", "stress", wet(0.15)),
    ("Amulet worn only half the time", "stress", amulet_off(0.50)),
    ("Power cut / travel: 2 gaps of 2-5 days a month", "stress", power_cuts(2)),
    ("Electrode ageing: leg reading -1% a month", "stress", electrode_ageing(1)),
    ("Electrode ageing: leg reading -3% a month", "stress", electrode_ageing(3)),
    ("Everything bad at once", "stress", everything),
]


def ci(r, key):
    lo, hi = E.bootstrap(r, 300)[key]
    return f"{lo:.2f}-{hi:.2f}"


def one_case(i):
    name, kind, change = CASES[i]
    x = change(f)
    r = E.run(A.make_system(T), x, p, check_no_peeking=False)
    s = E.summarize(r)
    row = dict(case=name, kind=kind, sensitivity=round(s["sensitivity"], 3), sensitivity_ci=ci(r, "sensitivity"),
               specificity=round(s["specificity"], 4), median_lead_days=s["median_lead_days"],
               false_alerts_per_patient_month=round(s["false_alerts_per_patient_month"], 3),
               fa_ci=ci(r, "false_alerts_per_patient_month"))
    if kind != "ablation":                                                   # same mess, published weight rule
        b = E.summarize(E.run(B.weight_rule_1, x, p, check_no_peeking=False))
        row.update(rule1_sensitivity=round(b["sensitivity"], 3), rule1_fa=round(b["false_alerts_per_patient_month"], 3),
                   beats_rule1=bool(s["sensitivity"] > b["sensitivity"] and s["false_alerts_per_patient_month"] < b["false_alerts_per_patient_month"]))
    return row


if __name__ == "__main__":
    with ProcessPoolExecutor() as pool:
        rows = list(pool.map(one_case, range(len(CASES))))
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "reports" / "stress_and_ablation.csv", index=False)
    print(f"frozen v2 engine, T={T}")
    print(out.to_string(index=False))
