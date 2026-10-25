"""6-MINUTE WALK TEST ACCURACY on synthetic pendant signals (no human data). Step error of the best-6-minute count
for paces 60-120 steps/min and step strengths 0.05-0.3 g, loose (0.02 g swing) vs snug (0.005 g) cord, and steps
falsely counted while not walking.   Run:  python engine/walk_accuracy.py   Out: reports/walk_accuracy.csv"""
import csv, pathlib
import numpy as np
import signals as S

ROOT = pathlib.Path(__file__).resolve().parents[1]
rows = []
for cord, label in ((0.02, "loose cord"), (0.005, "snug cord")):
    for cad in (60, 75, 90, 105, 120):
        for amp in (0.05, 0.08, 0.15, 0.3):
            errs = [S.walk6(m)[1] / t - 1 for m, t in (S.make_walk(cad, 360, amp=amp, cord=cord, seed=cad * 7 + s) for s in range(3))]
            rows.append(dict(case=label, cadence=cad, step_g=amp, error_pct=round(100 * float(np.mean(errs)), 1)))
for kind in ("sitting", "fidget", "auto-rickshaw", "turning in bed"):
    rows.append(dict(case=f"not walking: {kind} (30 min)", cadence="", step_g="",
                     error_pct=f"{sum(S.walk6(S.make_still(kind, seed=s))[0] for s in range(3)):.0f} steps"))
with open(ROOT / "reports/walk_accuracy.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for label in ("loose cord", "snug cord"):
    print(label)
    for cad in (60, 75, 90, 105, 120):
        print(f"  {cad:3d}/min", "  ".join(f"{r['step_g']} g {r['error_pct']:+5.1f}%" for r in rows if r["case"] == label and r["cadence"] == cad))
for r in rows[40:]: print(r["case"], r["error_pct"])
