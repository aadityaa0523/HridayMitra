"""Day-by-day engine output for the 200 synthetic patients, so a reader can see every light and its reason.
`light` is what the stool's ESP32 shows (rules v3, frozen T in engine/frozen_params_v3.json); `hybrid_red` is the
laptop hybrid's red alert (engine/frozen_hybrid.json), the system behind the headline results. Column `split` says whether the patient was used for tuning (dev)
or held out (test); only test rows count for the reported results.
Run:  python tools/export_alerts.py      Out: 03_Data/1_main_200_patients/alerts.csv
"""
import json, pathlib, sys
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import alert_engine as A
import hybrid as H

P = json.loads((ROOT / "engine/frozen_hybrid.json").read_text())
T = json.loads((ROOT / "engine/frozen_params_v3.json").read_text())["T"]
splits = json.loads((ROOT / "benchmark/splits.json").read_text())
test = set(splits["test"]["patient_ids"])                      # every other patient here is dev
df = pd.read_csv(ROOT / "data/processed/daily_features.csv")
LIGHT = {0: "green", 1: "amber", 2: "red"}

rows = []
for pid, g in df.groupby("patient_id", sort=False):
    g = g.reset_index(drop=True)
    sc = A.scores(g)
    hyb = H.hybrid_lights(sc, H.features(sc), P) == 2
    for r, light, h in zip(sc, A.lights(sc, T), hyb):
        cause, parts = A.explain(g, r) if light > 0 else ("", [])
        rows.append(dict(patient_id=pid, day=r["day"], split="test" if pid in test else "dev", score=round(r["S"], 2),
                         fluid=round(r["fam_fluid"], 2), heart_lungs=round(r["fam_heart_lungs"], 2),
                         daily_life=round(r["fam_daily_life"], 2), light=LIGHT[int(light)],
                         reason="; ".join(parts), likely_cause=cause, hybrid_red=int(h)))
out = pd.DataFrame(rows)
assert len(out) == len(df) and out.light.isin(LIGHT.values()).all()
dst = ROOT / "03_Data/1_main_200_patients/alerts.csv"
out.to_csv(dst, index=False)
print(dst, len(out), out.light.value_counts().to_dict())
