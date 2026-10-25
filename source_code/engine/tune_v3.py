"""ENGINE v3 = v2 + leg spectroscopy (extracellular-water index). Tunes the threshold T ON TRAINING PATIENTS ONLY under
the same false-alert budget (0.21 per patient-month), freezes it in engine/frozen_params_v3.json, then tests once.
v2 is the same engine with the spectroscopy column removed, so the comparison changes exactly one thing.
Run:  python engine/tune_v3.py        Out: engine/frozen_params_v3.json, reports/v3_results.csv
"""
import datetime, json, pathlib, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import evaluate as E, alert_engine as A

ROOT = pathlib.Path(__file__).resolve().parents[1]
FA_BUDGET, GRID = 0.21, [5, 5.5, 6, 6.5, 7, 7.5, 8, 9, 10, 11, 12, 14]


def sc(args):
    g, ewi = args
    g = g.reset_index(drop=True)
    return g.patient_id.iloc[0], A.scores(g if ewi else g.drop(columns="leg_ewi"))


def grade(S, pats, T):
    pi = pats.set_index("patient_id", drop=False)
    return E.summarize(pd.DataFrame([E.score_patient(A.lights(v, T), pi.loc[k]) for k, v in S.items()]))


if __name__ == "__main__":
    f, p = pd.read_csv(ROOT / "data/processed/daily_features.csv"), pd.read_csv(ROOT / "data/processed/patients.csv")
    test_ids = set(np.random.default_rng(42).choice(p.patient_id.to_numpy(), size=int(0.3 * len(p)), replace=False))
    train, test = p[~p.patient_id.isin(test_ids)], p[p.patient_id.isin(test_ids)]
    rw_f, rw_p = pd.read_csv(ROOT / "data/processed/realworld/daily_features.csv"), pd.read_csv(ROOT / "data/processed/realworld/patients.csv")
    T2 = json.loads((ROOT / "engine/frozen_params_v2.json").read_text())["T"]
    with ProcessPoolExecutor() as pool:
        S_tr = dict(pool.map(sc, [(g, True) for _, g in f[f.patient_id.isin(train.patient_id)].groupby("patient_id")], chunksize=8))
        grid = pd.DataFrame([dict(T=T, **grade(S_tr, train, T)) for T in GRID])
        ok = grid[grid.false_alerts_per_patient_month <= FA_BUDGET]
        T3 = float(ok.sort_values(["sensitivity", "median_lead_days"], ascending=False).iloc[0]["T"])
        (ROOT / "engine/frozen_params_v3.json").write_text(json.dumps(dict(T=T3, signals="v2 + leg_ewi", fa_budget_per_patient_month=FA_BUDGET,
            frozen_at=datetime.datetime.now().isoformat(timespec="seconds")), indent=2))
        print("TRAINING grid (v3):"); print(grid.round(3).to_string(index=False)); print(f"FROZEN v3: T = {T3}\n")
        rows = []
        for name, ff, pp in [("PS held-out", f[f.patient_id.isin(test_ids)], test), ("Real-world (external)", rw_f, rw_p)]:
            for label, ewi, T in [("v2 (no spectroscopy)", False, T2), ("v3 (with spectroscopy)", True, T3)]:
                S = dict(pool.map(sc, [(g, ewi) for _, g in ff.groupby("patient_id")], chunksize=8))
                rows.append(dict(cohort=name, system=label, T=T, **{k: round(v, 3) for k, v in grade(S, pp, T).items()}))
                print(rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(ROOT / "reports/v3_results.csv", index=False)
