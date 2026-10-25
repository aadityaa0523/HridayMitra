"""CALIBRATION CHECK: do our synthetic patients behave like real ones? The published weight rules, applied exactly as
the trials defined them, should score on our cohorts about what they scored on real heart-failure patients.

Published anchors (weight rule on real patients):
  FAST (Abraham 2011, 156 pts):   +3 lb in 1 day or +5 lb in 3 days -> sensitivity 23 %, 4.3 unexplained alerts / pt-year
  SCALE-HF 1 (2024, 69 events):   >3 lb in 1 day or >5 lb in 7 days -> sensitivity 35 % (24/69), 4.18 alerts / pt-year
Our false alerts per patient-month x 12 = alerts per patient-year (the trials' "unexplained" alerts are the closest match).
A synthetic cohort is CALIBRATED if both rules land inside a band around the published values: sensitivity within
+-12 points (the trials' own 95 % ranges are about that wide) and unexplained alerts within half to double.
Run:  python engine/calibrate_published.py        Out: reports/calibration_published.csv
"""
import pathlib, sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import evaluate as E

ROOT = pathlib.Path(__file__).resolve().parents[1]
LB = 0.4536
PUBLISHED = {"FAST (Abraham 2011)": (0.23, 4.3), "SCALE-HF 1 (2024)": (0.35, 4.18)}


def rule(short_days, short_lb, long_days, long_lb, strict):
    """Red on day t if weight rose by the limit versus 1 day / `long_days` days earlier (last available reading)."""
    def system(g):
        w = pd.Series(g.weight_kg.to_numpy(float)).ffill().to_numpy()
        out = np.zeros(len(w), int)
        for t in range(len(w)):
            for d, lb in ((short_days, short_lb), (long_days, long_lb)):
                if t >= d and not np.isnan(w[t]) and not np.isnan(w[t - d]):
                    gain = (w[t] - w[t - d]) / LB
                    if (gain > lb) if strict else (gain >= lb):
                        out[t] = 2
        return out
    return system


RULES = {"FAST (Abraham 2011)": rule(1, 3, 3, 5, strict=False), "SCALE-HF 1 (2024)": rule(1, 3, 7, 5, strict=True)}


if __name__ == "__main__":
    rows = []
    for cohort, folder in [("PS cohort (200 x 60 d)", "data/processed"), ("Real-world cohort (1000 x 180 d)", "data/processed/realworld")]:
        f, p = pd.read_csv(ROOT / folder / "daily_features.csv"), pd.read_csv(ROOT / folder / "patients.csv")
        for name, sys_ in RULES.items():
            s = E.summarize(E.run(sys_, f, p, check_no_peeking=False))
            sens0, ua0 = PUBLISHED[name]
            ua = s["false_alerts_per_patient_month"] * 12
            ok = abs(s["sensitivity"] - sens0) <= 0.12 and ua0 / 2 <= ua <= ua0 * 2
            rows.append(dict(cohort=cohort, rule=name, sensitivity=round(s["sensitivity"], 3), published_sensitivity=sens0,
                             unexplained_alerts_per_year=round(ua, 2), published_alerts_per_year=ua0, calibrated=ok))
            print(rows[-1])
    pd.DataFrame(rows).to_csv(ROOT / "reports/calibration_published.csv", index=False)
