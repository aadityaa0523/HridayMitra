# 3. Data

All patient data is **synthetic** (computer-generated, seed 42), as the problem statement asks. No human data was collected. Real public data (PhysioNet BIDMC) is used only to check the heart-rate, pulse and breathing code.

| File | What it is |
|---|---|
| [dataset_card.md](dataset_card.md) | How the patients are built: every parameter with its published source, or marked ASSUMPTION |
| [sample_two_patients.csv](sample_two_patients.csv) | Daily device readings for one stable patient (P0001) and one who worsens and is admitted (P0002) |
| [patients_sample.png](patients_sample.png) | Example patients: signals drifting in the 3–10 days before the hospital visit |
| [measurement_error_model.png](measurement_error_model.png) | How sensor noise and bad readings are added |

## The full synthetic dataset

| Folder | Patients | Files |
|---|---|---|
| [synthetic_200_patients/](synthetic_200_patients/) | 200 (60 % have a hospital visit), 60 days each | `daily_features.csv` (what the devices report, one row per patient-day), `patients.csv` (who they are, event day, cause), `labels.csv` (answer key), `truth_daily.csv` (hidden truth, never shown to the engine), **`alerts.csv`** (the engine's light, score per body system, reason in words and likely cause for every patient-day; `split` = dev or held-out test) |
| [external_1000_patients/](external_1000_patients/) | 1,000 (100 events), a separate "real-world-like" set | `patients.csv`, `labels.csv`, dataset card; the 16 MB daily file is in [data/processed/realworld/](../data/processed/realworld/) |

Regenerate everything with `python sim/patients/make_patients.py` (same seed → same files). Original location: [data/processed/](../data/processed/).

## Scripts that build and analyse the data

| Step | Script | What it does |
|---|---|---|
| 1. Build patients | [sim/patients/make_patients.py](../sim/patients/make_patients.py) | Generates the synthetic patients from the parameters in [dataset_card.md](dataset_card.md) |
| 2. Check the data | [sim/patients/check_patients.py](../sim/patients/check_patients.py) | Prints simple facts about the patients and draws 6 of them (`patients_sample.png`) |
| 3. Sensor noise | [sim/circuit/measurement_error_model.py](../sim/circuit/measurement_error_model.py) | Turns LTspice and bench numbers into the noise added to every reading |
| 4. Alert engine | [engine/alert_engine.py](../engine/alert_engine.py), [engine/hybrid.py](../engine/hybrid.py) | Personal baseline, scores, lights, reasons |
| 5. Day-by-day output | [tools/export_alerts.py](../tools/export_alerts.py) | Writes `alerts.csv` above |
| 6. Benchmark | [benchmark/bench.py](../benchmark/bench.py), [benchmark/score.py](../benchmark/score.py) | Splits patients, tunes on dev only, scores once on test / external / stress with bootstrap ranges |
| 7. Robustness | [engine/assumption_sensitivity.py](../engine/assumption_sensitivity.py), [engine/stress_and_ablation.py](../engine/stress_and_ablation.py) | Pushes every assumption to its extremes; removes one part at a time |
| 8. Real public data | [engine/validate_bidmc_hr.py](../engine/validate_bidmc_hr.py), [engine/validate_bidmc_ppg.py](../engine/validate_bidmc_ppg.py) | Heart rate, pulse and breathing code on PhysioNet BIDMC |

**Problem-statement rules met:** at least 20 patients × 30 days (we use 200 × 60, plus 1,000 external); worsening starts 3–10 days before the visit; each patient is fully in training or testing ([benchmark/splits.json](../benchmark/splits.json)).

![Sample patients](patients_sample.png)
