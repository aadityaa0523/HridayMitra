"""ML COMPARATOR: could a trained model beat our hand-built engine? Same inputs (the engine's per-signal worsening
scores against each person's own normal), same patient split, same false-alert budget, same grader.
Models: logistic regression and gradient-boosted trees, trained to spot "inside a worsening window" days on the
140 training patients; their alarm threshold is chosen on training only (budget 0.21 false alerts per patient-month),
red = above threshold on 2 of the last 3 days (the engine's persistence rule). Then tested once.
Run:  python engine/ml_comparator.py        Out: reports/ml_comparator.csv
"""
import json, pathlib, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import evaluate as E, alert_engine as A

ROOT = pathlib.Path(__file__).resolve().parents[1]
KEYS = list(A.SIGNALS) + ["symptoms", "night_situps"]
T = json.loads((ROOT / "engine/frozen_params_v3.json").read_text())["T"]


def features(g):
    g = g.reset_index(drop=True)
    sc = A.scores(g)
    X = np.array([[r["z"].get(k, 0.0) for k in KEYS] + [r[f"fam_{f}"] for f in A.FAMILIES] for r in sc])
    return g.patient_id.iloc[0], X, A.lights(sc, T)


def labels(n, p):
    d = np.arange(n)
    return ((d >= p.worsen_start_day) & (d < p.admit_day)) if p.event else np.zeros(n, bool)


def states(prob, thr):
    hi = prob >= thr
    return np.array([2 if hi[max(0, t - 2):t + 1].sum() >= 2 else 0 for t in range(len(hi))])


def grade(feats, pats, model, thr):
    pi = pats.set_index("patient_id", drop=False)
    return E.summarize(pd.DataFrame([E.score_patient(states(model.predict_proba(X)[:, 1], thr), pi.loc[pid])
                                     for pid, X, _ in feats]))


def engine_row(feats, pats):
    pi = pats.set_index("patient_id", drop=False)
    return E.summarize(pd.DataFrame([E.score_patient(L, pi.loc[pid]) for pid, _, L in feats]))


if __name__ == "__main__":
    f, p = pd.read_csv(ROOT / "data/processed/daily_features.csv"), pd.read_csv(ROOT / "data/processed/patients.csv")
    test_ids = set(np.random.default_rng(42).choice(p.patient_id.to_numpy(), size=int(0.3 * len(p)), replace=False))
    rw_f, rw_p = pd.read_csv(ROOT / "data/processed/realworld/daily_features.csv"), pd.read_csv(ROOT / "data/processed/realworld/patients.csv")
    with ProcessPoolExecutor() as pool:
        F = list(pool.map(features, [g for _, g in f.groupby("patient_id")], chunksize=8))
        RW = list(pool.map(features, [g for _, g in rw_f.groupby("patient_id")], chunksize=8))
    pi = p.set_index("patient_id")
    train = [x for x in F if x[0] not in test_ids]; test = [x for x in F if x[0] in test_ids]
    Xtr = np.vstack([X[E.EVAL_FROM:] for _, X, _ in train])
    ytr = np.concatenate([labels(len(X), pi.loc[pid])[E.EVAL_FROM:] for pid, X, _ in train])
    rows = []
    for name, model in [("Logistic regression", LogisticRegression(max_iter=2000, class_weight="balanced")),
                        ("Gradient-boosted trees", HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05,
                                                                                   class_weight="balanced", random_state=0))]:
        model.fit(Xtr, ytr)
        p_tr, best = p[~p.patient_id.isin(test_ids)], None
        for thr in np.quantile(model.predict_proba(Xtr)[:, 1], np.linspace(0.80, 0.999, 60)):
            s = grade(train, p_tr, model, thr)
            if s["false_alerts_per_patient_month"] <= 0.21 and (best is None or s["sensitivity"] > best[1]["sensitivity"]):
                best = (thr, s)
        thr = best[0]
        for cohort, feats, pats in [("PS held-out", test, p[p.patient_id.isin(test_ids)]), ("Real-world", RW, rw_p)]:
            rows.append(dict(cohort=cohort, system=name, **{k: round(v, 3) for k, v in grade(feats, pats, model, thr).items()}))
    for cohort, feats, pats in [("PS held-out", test, p[p.patient_id.isin(test_ids)]), ("Real-world", RW, rw_p)]:
        rows.append(dict(cohort=cohort, system="HridayMitra engine (frozen v3)", **{k: round(v, 3) for k, v in engine_row(feats, pats).items()}))
    out = pd.DataFrame(rows).sort_values(["cohort", "system"])
    out.to_csv(ROOT / "reports/ml_comparator.csv", index=False)
    pd.set_option("display.width", 200); print(out.to_string(index=False))
