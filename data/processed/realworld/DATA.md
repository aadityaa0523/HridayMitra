# Dataset card: HridayMitra pretend patients (synthetic)

Made by `sim/patients/make_patients.py` with seed 43. Fully fake: no real person is in this data.

- Patients: 1000. Days per stable patient: 180. Patients with a hospital visit: 10%; their data ends on the visit day.
- First 30 days are normal (the patient's baseline). Worsening starts 3-10 days before the visit.
- Files: `daily_features.csv` (what the devices report; empty cell = no reading), `patients.csv` (who, truth about events),
  `labels.csv` (answer key for testing), `truth_daily.csv` (hidden truth: congestion, guest, infection... never given to the alert brain).
- Reproducible: same seed gives the same files. SHA-256 of daily_features.csv: `115daddb78088489`

## Every parameter and where it comes from

| Parameter | Value | Source |
|---|---|---|
| warmup_days | 30 | design: first days are the patient's normal, no worsening yet |
| worsen_lead_days | (3, 10) | problem statement: worsening starts 3 to 10 days before the hospital visit |
| ramp_exponent | 1.5 | ASSUMPTION: worsening shape; 1 = straight line, above 1 = slow start, fast end |
| weight_gain_kg | (1.0, 4.5) | published: Chaudhry 2007, gains of 2-10 lb in the days before admission |
| weight_silent_fraction | 0.35 | published (rough): many admissions show no weight gain (FAST trial, Gyllensten 2016) |
| silent_gain_kg | (0.0, 0.5) | ASSUMPTION: weight-silent patients gain almost nothing |
| weight_day_sd_kg | 0.42 | ASSUMPTION: normal day-to-day weight wobble |
| leg_z_pct_per_fluid_pct | 0.87 | LTspice: +10% leg fluid lowers the 5 kHz leg reading by about 8.7% |
| fluid_peak_fraction | (0.05, 0.15) | ASSUMPTION: leg fluid up 5-15% at the worst point |
| silent_leg_response | 1.0 | KEY ASSUMPTION: the leg reading still falls fully in weight-silent patients (1.0). TEST with 0.5 and 0.0 |
| leg_bio_noise_pct | 1.5 | ASSUMPTION: the body itself changes by about 1.5% day to day |
| trunk_drop_per_fluid | 0.6 | ASSUMPTION: chest reading falls 0.6 x the fluid fraction (weak, very noisy signal) |
| trunk_noise_ohm | 4.0 | ASSUMPTION: subtracting four readings amplifies noise (trunk is only about 25 ohm) |
| hr_gain_bpm | (2.0, 8.0) | published (rough): resting heart rate rises 3-8 bpm before events (WEARIT-France, van Es 2025) |
| hr_day_sd_bpm | 2.5 | ASSUMPTION |
| spo2_drop | (0.0, 2.0) | ASSUMPTION |
| rr_gain | (1.2, 2.2) | published: night breathing rate +1.5 to 2.1 per minute (NOTICE-HF) |
| activity_drop | (0.1, 0.25) | published (rough): activity falls 10-25% (Kelly 2020) |
| situps_peak | 2.5 | ASSUMPTION: extra night sit-ups at the worst point |
| symptom_peak_prob | 0.5 | published (rough): orthopnea/night breathlessness about 52% sensitive as symptoms |
| infection_fraction | 0.15 | ASSUMPTION: 15% of patients have an infection episode |
| infection_hr_bpm | (8, 15) | published pattern: infection raises pulse more than heart failure does (Gardner 2021) |
| infection_rr | (2.0, 4.0) | ASSUMPTION |
| salty_meals_per_patient | 2 | ASSUMPTION: about 2 salty-meal days per patient |
| salty_weight_kg | (0.5, 1.5) | ASSUMPTION: a salty meal adds 0.5-1.5 kg that fades in 2 days |
| pill_miss_episodes | 1.0 | ASSUMPTION: about one missed-pill episode per patient |
| pills_cause_fraction | 0.35 | ASSUMPTION: 35% of events are triggered by missed pills |
| guest_prob | 0.01 | CALIBRATED: was 3%; weight-rule false alerts were 3x the published rate (almost all from guest days), so 1% |
| wet_feet_prob | 0.05 | ASSUMPTION: 5% of days feet are wet |
| jewellery_step_prob | 0.1 | ASSUMPTION: 10% of patients change jewellery once (leg reading shifts 1-3%) |
| missing_day_prob | 0.07 | ASSUMPTION: 7% of days nobody does the check |
| amulet_worn_prob | 0.9 | ASSUMPTION: amulet is worn on 90% of days |
| button_error_prob | 0.03 | ASSUMPTION: 3% of button answers are wrong |
| ewi_icw_ecw_person_sd | 0.15 | ASSUMPTION: people differ 15% in cell-water vs outside-water resistance (Ri/Re) |
| ewi_bio_noise_pct | 0.4 | ASSUMPTION: day-to-day change of the extracellular-water index that is NOT position/temperature (those cancel in the ratio, LTspice) |
| ewi_meas_noise_pct | 0.1 | ASSUMPTION: 3-frequency Cole-fit noise (Goertzel SNR at 50 kHz is about 0.03%; margin added) |

Leg-reading measurement noise (0.35%) comes from `sim/circuit/measurement_error_model.py`.

## What this data is NOT

- It is not real patient data and does not prove clinical accuracy. It only shows that an alert system can find the
  patterns we put in, and how it copes with mess (missing days, guests, infection, missed pills).
- Every value marked ASSUMPTION is our guess. The test reports must show results when these guesses change.
- Not modelled yet: atrial fibrillation, medicine changes, seasons, a calibration against published alert rates.