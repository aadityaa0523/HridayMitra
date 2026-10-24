"""Lead time if AMBER ("please check again") counts as the early heads-up, with the FROZEN v2 engine (no retuning).
Run:  python engine/amber_lead.py
"""
import json, pathlib, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import evaluate as E, alert_engine as A

ROOT = pathlib.Path(__file__).resolve().parents[1]
T = json.loads((ROOT / "engine/frozen_params_v2.json").read_text())["T"]


def sc(g):
    return g.patient_id.iloc[0], A.scores(g.reset_index(drop=True))


if __name__ == "__main__":
    p0 = pd.read_csv(ROOT / "data/processed/patients.csv")
    test_ids = set(np.random.default_rng(42).choice(p0.patient_id.to_numpy(), size=int(0.3 * len(p0)), replace=False))
    rows = []
    with ProcessPoolExecutor() as pool:
        for name, folder, ids in [("PS held-out", "data/processed", test_ids), ("Real-world", "data/processed/realworld", None)]:
            f, p = pd.read_csv(ROOT / folder / "daily_features.csv"), pd.read_csv(ROOT / folder / "patients.csv")
            if ids:
                f, p = f[f.patient_id.isin(ids)], p[p.patient_id.isin(ids)]
            S = dict(pool.map(sc, [g for _, g in f.groupby("patient_id")], chunksize=8))
            pi = p.set_index("patient_id", drop=False)
            for tier, conv in [("red only", lambda st: st), ("amber or red", lambda st: np.where(st >= 1, 2, 0))]:
                r = pd.DataFrame([dict(patient_id=k, **E.score_patient(conv(A.lights(v, T)), pi.loc[k])) for k, v in S.items()])
                rows.append(dict(cohort=name, counts_as_alert=tier, **{k: round(v, 3) for k, v in E.summarize(r).items()}))
                print(rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(ROOT / "reports/amber_lead_results.csv", index=False)
