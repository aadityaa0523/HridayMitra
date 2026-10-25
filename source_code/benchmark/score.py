"""SCORER for the HridayMitra-HF benchmark. Your submission is a CSV with columns patient_id, day, light
(0 green, 1 amber, 2 red), one row for EVERY patient-day of the split. Rule: the light on day t may only use days <= t
(no peeking); tune only on the dev split.
Run:  python benchmark/score.py my_submission.csv test        (splits: dev, test, external, stress)
"""
import pathlib, sys
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine")); sys.path.insert(0, str(ROOT / "benchmark"))
import evaluate as E


def score(sub, split_name, n_boot=1000):
    import bench
    f, p = bench.split(split_name)
    sub = sub[["patient_id", "day", "light"]]
    if not sub.light.isin([0, 1, 2]).all():
        raise ValueError("light must be 0, 1 or 2")
    key = lambda d: set(zip(d.patient_id, d.day))
    if key(sub) != key(f) or len(sub) != len(f):
        raise ValueError(f"submission must have exactly one row per patient-day of '{split_name}' ({len(f)} rows)")
    pi = p.set_index("patient_id", drop=False)
    r = pd.DataFrame([dict(patient_id=pid, **E.score_patient(g.sort_values("day").light.to_numpy(), pi.loc[pid]))
                      for pid, g in sub.groupby("patient_id")])
    s, ci = E.summarize(r), E.bootstrap(r, n_boot)
    return {**{k: round(v, 4) for k, v in s.items()}, **{f"{k}_ci": f"{lo:.2f}-{hi:.2f}" for k, (lo, hi) in ci.items()}}


if __name__ == "__main__":
    out = score(pd.read_csv(sys.argv[1]), sys.argv[2])
    for k, v in out.items():
        print(f"{k:34s} {v}")
