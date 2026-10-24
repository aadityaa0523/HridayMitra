"""Do the pretend patients behave like real ones? Run the published weight rules on them and compare
with the published numbers. Run:  python engine/calibrate_check.py
Published targets (rough, from the papers we read):
  FAST trial weight rule        : sensitivity about 23 %, about 4.3 false alerts per patient-year (0.36 per month)
  SCALE-HF 1 weight comparator  : sensitivity about 35 %, about 4.13 false alerts per patient-year (0.34 per month)
  Gyllensten 2016 weight MACD   : sensitivity about 33 %, specificity about 91 %
"""
import pathlib, sys
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import evaluate as E, baselines as B

ROOT = pathlib.Path(__file__).resolve().parents[1]
rows = []
for name, folder in [("PS cohort (200 x 60d)", "data/processed"), ("Real-world cohort (1000 x 180d)", "data/processed/realworld"),
                     ("Weaker-assumption cohort", "data/processed/sensitivity_silent05")]:
    f, p = pd.read_csv(ROOT / folder / "daily_features.csv"), pd.read_csv(ROOT / folder / "patients.csv")
    for rname, rule in [("weight rule 1 (SCALE-HF)", B.weight_rule_1), ("weight MACD (Gyllensten)", B.weight_rule_macd)]:
        r = E.run(rule, f, p, check_no_peeking=(folder == "data/processed"))
        rows.append(dict(cohort=name, **E.report(rname, r)))
        print(rows[-1], flush=True)
out = pd.DataFrame(rows)
out.to_csv(ROOT / "reports" / "calibration_check.csv", index=False)
print("\n" + out[["cohort", "system", "events", "sensitivity", "specificity", "median_lead_days",
                  "false_alerts_per_patient_month"]].to_string(index=False))
