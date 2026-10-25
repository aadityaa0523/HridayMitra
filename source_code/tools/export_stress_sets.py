"""Save every real-life stress dataset exactly as engine/stress_and_ablation.py builds it (same seeds), so a reader can
open the messy data behind each row of reports/stress_and_ablation.csv.
Base: the external cohort (all 100 sick + 300 stable patients, data/processed/realworld).
Run:  python tools/export_stress_sets.py      Out: ../03_Data/4_stress_real_life/<case>.csv, patients.csv, labels.csv
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import stress_and_ablation as S

OUT = ROOT.parent / "03_Data" / "4_stress_real_life"     # judge folder sits beside source_code/
OUT.mkdir(parents=True, exist_ok=True)
for name, kind, change in S.CASES:
    if kind != "stress":
        continue
    x = change(S.f)
    assert len(x) == len(S.f)
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    x.to_csv(OUT / f"{slug}.csv", index=False, float_format="%.4g")
    print(slug, len(x))
S.f.to_csv(OUT / "clean_before_stress.csv", index=False, float_format="%.4g")
S.p.to_csv(OUT / "patients.csv", index=False)
S.p[["patient_id", "worsen_start_day", "admit_day"]].to_csv(OUT / "labels.csv", index=False)
