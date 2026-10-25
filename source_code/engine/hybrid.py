"""HYBRID ENGINE: the rules propose, a small learned model confirms.

The rules engine (alert_engine.py) runs at a LOWER threshold T_h, so it raises more possible reds. A logistic model
reads the same per-signal worsening scores and family scores; a red goes out only if the model's probability was at
or above `thr` on one of the last 3 days. Otherwise the day stays amber ("check again"). A danger reading (SpO2 below
90 %) is always red. The reasons shown to the family are still the rules' reasons, so every alert stays explainable.
Logistic regression is one weighted sum and a sigmoid: it fits on the ESP32 next to engine_core.h.

Trained ONLY on the dev patients (benchmark/splits.json). T_h and thr are chosen on dev under the same false-alert
budget as the rules engine (0.21 per patient-month) and frozen in engine/frozen_hybrid.json before any test patient
is scored.   Run:  python engine/hybrid.py   (or via benchmark/bench.py)
"""
import json, pathlib, sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import alert_engine as A, evaluate as E

ROOT = pathlib.Path(__file__).resolve().parents[1]
KEYS = list(A.SIGNALS) + ["symptoms", "night_situps"]
FA_BUDGET = 0.21
FROZEN = ROOT / "engine" / "frozen_hybrid.json"


def features(sc):
    return np.array([[r["z"].get(k, 0.0) for k in KEYS] + [r[f"fam_{f}"] for f in A.FAMILIES] for r in sc])


def window_labels(n, p):
    d = np.arange(n)
    return ((d >= p.worsen_start_day) & (d < p.admit_day)) if p.event else np.zeros(n, bool)


def hybrid_lights(sc, X, P):
    base = A.lights(sc, P["T_h"])
    prob = 1 / (1 + np.exp(-(X @ np.asarray(P["w"]) + P["b"])))
    confirmed = np.array([prob[max(0, t - 2):t + 1].max() >= P["thr"] for t in range(len(prob))])
    danger = np.array([r["danger"] for r in sc])
    out = base.copy()
    out[(base == 2) & ~confirmed & ~danger] = 1
    return out


def make_system(P):
    def system(g):
        sc = A.scores(g)
        return hybrid_lights(sc, features(sc), P)
    return system


def fit(dev_scores, dev_pats):
    """dev_scores: {patient_id: A.scores(...)}. Returns the frozen parameters (also written to FROZEN)."""
    pi = dev_pats.set_index("patient_id", drop=False)
    Xs = {pid: features(sc) for pid, sc in dev_scores.items()}
    X = np.vstack([x[E.EVAL_FROM:] for x in Xs.values()])
    y = np.concatenate([window_labels(len(x), pi.loc[pid])[E.EVAL_FROM:] for pid, x in Xs.items()])
    m = LogisticRegression(max_iter=2000, class_weight="balanced").fit(X, y)
    w, b = m.coef_[0].tolist(), float(m.intercept_[0])
    probs = 1 / (1 + np.exp(-(X @ np.asarray(w) + b)))
    best = None
    for T_h in [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]:
        for thr in np.quantile(probs, np.linspace(0.5, 0.99, 25)):
            P = dict(T_h=T_h, thr=float(thr), w=w, b=b)
            s = E.summarize(pd.DataFrame([E.score_patient(hybrid_lights(sc, Xs[pid], P), pi.loc[pid]) for pid, sc in dev_scores.items()]))
            if s["false_alerts_per_patient_month"] <= FA_BUDGET and (best is None or s["sensitivity"] > best[1]["sensitivity"]):
                best = (P, s)
    P = dict(best[0], keys=KEYS + [f"fam_{f}" for f in A.FAMILIES], fa_budget_per_patient_month=FA_BUDGET,
             dev_sensitivity=round(best[1]["sensitivity"], 3), dev_false_alerts=round(best[1]["false_alerts_per_patient_month"], 3),
             trained_on=f"{len(dev_scores)} dev patients (benchmark/splits.json)")
    FROZEN.write_text(json.dumps(P, indent=1))
    return P


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "benchmark"))
    import bench
    f, p = bench.split("dev")
    print(fit({pid: A.scores(g.reset_index(drop=True)) for pid, g in f.groupby("patient_id")}, p))
