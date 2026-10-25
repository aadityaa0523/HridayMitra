# 3. Data

All patient data is **synthetic** (computer-generated, seed 42), as the problem statement asks. No human data was collected. Real public data (PhysioNet BIDMC) is used only to check the heart-rate, pulse and breathing code.

| File | What it is |
|---|---|
| [dataset_card.md](dataset_card.md) | How the patients are built: every parameter with its published source, or marked ASSUMPTION |
| [sample_two_patients.csv](sample_two_patients.csv) | Daily device readings for one stable patient (P0001) and one who worsens and is admitted (P0002) |
| [patients_sample.png](patients_sample.png) | Example patients: signals drifting in the 3–10 days before the hospital visit |
| [measurement_error_model.png](measurement_error_model.png) | How sensor noise and bad readings are added |

**Full data:** [data/processed/](../data/processed/) (200 patients: `daily_features.csv`, `patients.csv`, `labels.csv`, `truth_daily.csv`). The 1,000-patient external set and the stress set come from the same generator ([sim/patients/](../sim/patients/)).

**Problem-statement rules met:** at least 20 patients × 30 days (we use 200 × 60, plus 1,000 external); worsening starts 3–10 days before the visit; each patient is fully in training or testing ([benchmark/splits.json](../benchmark/splits.json)).

![Sample patients](patients_sample.png)
