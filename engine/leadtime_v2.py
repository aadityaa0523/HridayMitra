"""Lead-time fix (v2). Chooses between the v1 engine and v1 + slow-drift detector ON TRAINING PATIENTS ONLY,
freezes the choice and T in engine/frozen_params_v2.json, then tests once. Same split and same false-alert budget as v1.
Run:  python engine/leadtime_v2.py
"""
import json, pathlib, sys, datetime
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import evaluate as E, alert_engine as A

ROOT = pathlib.Path(__file__).resolve().parents[1]
FA_BUDGET, GRID = 0.21, [5, 6, 6.5, 7, 8, 9, 10, 11, 12, 14, 16]
VERSIONS = [(False, 0.5, 2.0)] + [(True, k, sc) for k in (0.75, 1.0, 1.5) for sc in (2.0, 3.0)]


def score_all(args):
    g, cusum, k, sc = args
    return g.patient_id.iloc[0], A.scores(g, cusum, k, sc)


def grade(sc, pats, T):
    p = pats.set_index("patient_id", drop=False)
    return pd.DataFrame([dict(patient_id=k, **E.score_patient(A.lights(v, T), p.loc[k])) for k, v in sc.items()])


def run_frozen(ff, pp, T, v, pool):
    sc = dict(pool.map(score_all, [(g.reset_index(drop=True), *v) for _, g in ff.groupby("patient_id")], chunksize=8))
    return grade(sc, pp, T)


if __name__ == "__main__":
    f, p = pd.read_csv(ROOT / "data/processed/daily_features.csv"), pd.read_csv(ROOT / "data/processed/patients.csv")
    rng = np.random.default_rng(42)
    test_ids = set(rng.choice(p.patient_id.to_numpy(), size=int(0.3 * len(p)), replace=False))   # same split as v1
    train, test = p[~p.patient_id.isin(test_ids)], p[p.patient_id.isin(test_ids)]
    with ProcessPoolExecutor() as pool:
        choices = []
        for cusum, k, scl in VERSIONS:
            sc = dict(pool.map(score_all, [(g.reset_index(drop=True), cusum, k, scl) for _, g in f[f.patient_id.isin(train.patient_id)].groupby("patient_id")]))
            for T in GRID:
                s = E.summarize(grade(sc, train, T))
                choices.append(dict(cusum=cusum, k=k, scale=scl, T=T, **s))
        grid = pd.DataFrame(choices)
        ok = grid[grid.false_alerts_per_patient_month <= FA_BUDGET]
        best = ok.sort_values(["sensitivity", "median_lead_days"], ascending=False).iloc[0]
        cusum, T, k, scl = bool(best["cusum"]), float(best["T"]), float(best["k"]), float(best["scale"])
        (ROOT / "engine/frozen_params_v2.json").write_text(json.dumps(dict(T=T, cusum=cusum, k=k, scale=scl, fa_budget_per_patient_month=FA_BUDGET,
            frozen_at=datetime.datetime.now().isoformat(timespec="seconds")), indent=2))
        print("TRAINING (best per version under the budget):")
        print(ok.sort_values(["sensitivity", "median_lead_days"], ascending=False).groupby(["cusum", "k", "scale"]).head(1).round(3).to_string(index=False))
        print(f"FROZEN v2: cusum={cusum}, T={T}\n")
        rows = []
        for name, ff, pp in [("PS held-out", f[f.patient_id.isin(test_ids)], test),
                             ("Real-world (external)", pd.read_csv(ROOT / "data/processed/realworld/daily_features.csv"),
                              pd.read_csv(ROOT / "data/processed/realworld/patients.csv"))]:
            for label, v_, t_ in [("v1 engine (T=7)", (False, 0.5, 2.0), 7.0), ("v2 engine (frozen)", (cusum, k, scl), T)]:
                s = E.summarize(run_frozen(ff, pp, t_, v_, pool))
                rows.append(dict(cohort=name, system=label, **{k: round(v, 3) for k, v in s.items()}))
                print(rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(ROOT / "reports/leadtime_v2_results.csv", index=False)
    grid.to_csv(ROOT / "reports/leadtime_v2_grid.csv", index=False)
