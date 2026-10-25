"""HRIDAYMITRA-HF BENCHMARK v2: fixed splits, one scorer, every baseline graded the same way.

Splits (benchmark/splits.json, made from the synthetic cohorts in data/processed; no real person in any of them):
  dev       140 patients x 60 days   features + labels: tune anything here
  test      60 held-out patients     score ONCE, after freezing
  external  1000 patients x 180 days (the "real-world" cohort: more mess, longer)   score once
  stress    the 60 test patients re-made with weaker assumptions (leg reading only half responds in weight-silent
            patients)   score once
Run:  python benchmark/bench.py    Out: benchmark/splits.json, benchmark/leaderboard.csv, benchmark/LEADERBOARD.md,
      benchmark/submissions/<system>_test.csv (example submissions in the scorer's format)
"""
import hashlib, json, pathlib, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine")); sys.path.insert(0, str(ROOT / "benchmark"))
import alert_engine as A, baselines as B, evaluate as E, hybrid as H
from score import score

B_DIR = ROOT / "benchmark"
SOURCES = {"dev": "data/processed", "test": "data/processed", "external": "data/processed/realworld",
           "stress": "data/processed/sensitivity_silent05"}
T = json.loads((ROOT / "engine/frozen_params_v3.json").read_text())["T"]


def test_ids():
    p = pd.read_csv(ROOT / "data/processed/patients.csv")
    return set(np.random.default_rng(42).choice(p.patient_id.to_numpy(), size=int(0.3 * len(p)), replace=False))


def split(name):
    """(daily features, patients) for one split."""
    f, p = (pd.read_csv(ROOT / SOURCES[name] / x) for x in ("daily_features.csv", "patients.csv"))
    if name in ("dev", "test", "stress"):
        ids = test_ids()
        keep = p.patient_id.isin(ids) if name != "dev" else ~p.patient_id.isin(ids)
        p = p[keep]; f = f[f.patient_id.isin(p.patient_id)]
    return f, p


def write_splits():
    sha = lambda path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:16]
    out = {}
    for name, src in SOURCES.items():
        f, p = split(name)
        out[name] = dict(source=src, features_sha256=sha(f"{src}/daily_features.csv"), patients=len(p),
                         events=int(p.event.sum()), patient_days=len(f), patient_ids=sorted(p.patient_id))
    (B_DIR / "splits.json").write_text(json.dumps(out, indent=1))
    return out


def scored(g):
    g = g.reset_index(drop=True)
    return g.patient_id.iloc[0], A.scores(g)


def all_scores(f):
    with ProcessPoolExecutor() as pool:
        return dict(pool.map(scored, [g for _, g in f.groupby("patient_id")], chunksize=8))


def lights_table(f, fn):
    rows = []
    for pid, g in f.groupby("patient_id", sort=False):
        L = fn(pid, g.reset_index(drop=True))
        rows.append(pd.DataFrame(dict(patient_id=pid, day=g.day.to_numpy(), light=L)))
    return pd.concat(rows, ignore_index=True)


if __name__ == "__main__":
    splits = write_splits()
    print({k: (v["patients"], v["events"]) for k, v in splits.items()})
    fd, pd_ = split("dev")
    dev_sc = all_scores(fd)
    P = H.fit(dev_sc, pd_)                                          # frozen before any test patient is scored
    print("hybrid frozen:", {k: P[k] for k in ("T_h", "thr", "dev_sensitivity", "dev_false_alerts")})
    # logistic-only baseline (the ML comparator's best simple model): same features, red = 2 of last 3 days above thr
    Xd = {pid: H.features(sc) for pid, sc in dev_sc.items()}
    pi = pd_.set_index("patient_id", drop=False)
    from sklearn.linear_model import LogisticRegression
    X = np.vstack([x[E.EVAL_FROM:] for x in Xd.values()])
    y = np.concatenate([H.window_labels(len(x), pi.loc[pid])[E.EVAL_FROM:] for pid, x in Xd.items()])
    lr = LogisticRegression(max_iter=2000, class_weight="balanced").fit(X, y)
    ml_states = lambda prob, thr: np.array([2 if (prob[max(0, t - 2):t + 1] >= thr).sum() >= 2 else 0 for t in range(len(prob))])
    best = None
    for thr in np.quantile(lr.predict_proba(X)[:, 1], np.linspace(0.8, 0.999, 60)):
        s = E.summarize(pd.DataFrame([E.score_patient(ml_states(lr.predict_proba(Xd[pid])[:, 1], thr), pi.loc[pid]) for pid in Xd]))
        if s["false_alerts_per_patient_month"] <= H.FA_BUDGET and (best is None or s["sensitivity"] > best[1]):
            best = (thr, s["sensitivity"])
    lr_thr = best[0]
    rows = []
    for name in ("test", "external", "stress"):
        f, p = split(name)
        sc = all_scores(f)
        systems = {
            "Weight rule (SCALE-HF, >=2 kg / 2-3 days)": lambda pid, g: B.weight_rule_1(g),
            "Weight trend MACD (Gyllensten)": lambda pid, g: B.weight_rule_macd(g),
            "Logistic regression only (ML)": lambda pid, g: ml_states(lr.predict_proba(H.features(sc[pid]))[:, 1], lr_thr),
            f"HridayMitra rules engine v3 (T {T})": lambda pid, g: A.lights(sc[pid], T),
            "HridayMitra hybrid (rules propose, ML confirms)": lambda pid, g: H.hybrid_lights(sc[pid], H.features(sc[pid]), P),
        }
        for sname, fn in systems.items():
            sub = lights_table(f, fn)
            if name == "test":
                (B_DIR / "submissions").mkdir(exist_ok=True)
                sub.to_csv(B_DIR / "submissions" / f"{sname.split(' (')[0].lower().replace(' ', '_')}_test.csv", index=False)
            rows.append(dict(split=name, system=sname, **score(sub, name)))
            print(name, "|", sname, {k: rows[-1][k] for k in ("sensitivity", "specificity", "median_lead_days", "false_alerts_per_patient_month")}, flush=True)
    lb = pd.DataFrame(rows)
    lb.to_csv(B_DIR / "leaderboard.csv", index=False)
    md = ["# Leaderboard (HridayMitra-HF benchmark v2)", "",
          "Every system tuned on **dev** only, under a budget of 0.21 false alerts per patient-month, then scored once. "
          "Brackets: 95 % range from 1,000 patient bootstrap resamples. Synthetic data: this ranks methods, it does not prove clinical accuracy.", ""]
    for name in ("test", "external", "stress"):
        md += [f"## {name} ({splits[name]['patients']} patients, {splits[name]['events']} events)", "",
               "| System | Caught episodes | Normal days quiet | Median lead (days) | False alerts / patient-month |", "|---|---|---|---|---|"]
        for r in lb[lb.split == name].sort_values("sensitivity", ascending=False).itertuples():
            md.append(f"| {r.system} | {r.sensitivity:.0%} [{r.sensitivity_ci}] | {r.specificity:.1%} | {r.median_lead_days:g} | {r.false_alerts_per_patient_month:.3f} [{r.false_alerts_per_patient_month_ci}] |")
        md.append("")
    (B_DIR / "LEADERBOARD.md").write_text("\n".join(md), encoding="utf8")
