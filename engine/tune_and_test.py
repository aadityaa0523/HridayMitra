"""Tune on training patients, FREEZE, then test once on patients the engine has never seen.
Run:  python engine/tune_and_test.py
Rules: the split is by patient (each patient is wholly train or wholly test). The threshold T is chosen on training
patients only: the highest sensitivity whose false alerts stay at or below 0.21 per patient-month (2.5 per year).
T is written to engine/frozen_params.json BEFORE any test patient is scored.
"""
import json, pathlib, sys, hashlib, datetime
import numpy as np
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import evaluate as E, baselines as B, alert_engine as A

ROOT = pathlib.Path(__file__).resolve().parents[1]
FA_BUDGET = 0.21
GRID = [2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8]


def load(folder):
    return pd.read_csv(ROOT / folder / "daily_features.csv"), pd.read_csv(ROOT / folder / "patients.csv")


def grade_from_scores(sc_by_pid, pats, T):
    p = pats.set_index("patient_id", drop=False)
    return pd.DataFrame([dict(patient_id=pid, **E.score_patient(A.lights(sc, T), p.loc[pid])) for pid, sc in sc_by_pid.items()])


f, p = load("data/processed")
ids = p.patient_id.to_numpy()
rng = np.random.default_rng(42)
test_ids = set(rng.choice(ids, size=int(0.3 * len(ids)), replace=False))
train = p[~p.patient_id.isin(test_ids)]
test = p[p.patient_id.isin(test_ids)]

# ---- tune on training patients only ----
sc_train = {pid: A.scores(g) for pid, g in f[f.patient_id.isin(train.patient_id)].groupby("patient_id")}
grid = []
for T in GRID:
    s = E.summarize(grade_from_scores(sc_train, train, T))
    grid.append(dict(T=T, **s))
grid = pd.DataFrame(grid)
ok = grid[grid.false_alerts_per_patient_month <= FA_BUDGET]
best = ok.sort_values(["sensitivity", "T"], ascending=[False, True]).iloc[0] if len(ok) else grid.iloc[-1]
T = float(best["T"])
frozen = dict(T=T, fa_budget_per_patient_month=FA_BUDGET, frozen_at=datetime.datetime.now().isoformat(timespec="seconds"),
              train_patients=len(train), test_patients=len(test),
              train_ids_sha=hashlib.sha256(",".join(sorted(train.patient_id)).encode()).hexdigest()[:12])
(ROOT / "engine" / "frozen_params.json").write_text(json.dumps(frozen, indent=2))
print("TRAINING grid:\n" + grid.round(3).to_string(index=False))
print(f"\nFROZEN: T = {T}\n")

# ---- test once ----
system = A.make_system(T)
rows = []
cohorts = [("PS cohort, held-out test patients", f[f.patient_id.isin(test_ids)], test),
           ("Real-world cohort (external, 1000 x 180 d)", *load("data/processed/realworld")),
           ("Weaker-assumption cohort (test patients)", *[x[x.patient_id.isin(test_ids)] for x in load("data/processed/sensitivity_silent05")])]
for name, ff, pp in cohorts:
    for sname, sys_ in [("HridayMitra engine", system), ("weight rule 1 (SCALE-HF)", B.weight_rule_1),
                        ("weight MACD (Gyllensten)", B.weight_rule_macd)]:
        r = E.run(sys_, ff, pp, check_no_peeking=(sname == "HridayMitra engine" and "held-out" in name))
        rows.append(dict(cohort=name, **E.report(sname, r)))
        print(name, "|", sname, {k: rows[-1][k] for k in ["sensitivity", "specificity", "median_lead_days", "false_alerts_per_patient_month"]}, flush=True)
res = pd.DataFrame(rows)
res.to_csv(ROOT / "reports" / "phase1_results.csv", index=False)
grid.to_csv(ROOT / "reports" / "phase1_tuning_grid.csv", index=False)

# ---- one example explanation ----
pid = test[test.event].patient_id.iloc[0]
g = f[f.patient_id == pid].reset_index(drop=True)
sc = A.scores(g)
st = A.lights(sc, T)
red_days = np.flatnonzero(st == 2)
if len(red_days):
    d0 = int(red_days[0]); cause, parts = A.explain(g, sc[d0])
    pv = test.set_index("patient_id").loc[pid]
    print(f"\nExample {pid}: first red on day {d0}, hospital visit day {int(pv.admit_day)} -> {cause}: " + "; ".join(parts))
