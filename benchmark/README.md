# HridayMitra-HF benchmark v2: early warning of worsening heart failure at home

An open benchmark for **home early-warning systems**. Given one patient's daily home readings, raise a red alert
*while the patient is getting worse*, before the hospital visit, without crying wolf. **Fully synthetic: no real
person is in this data.** Results rank methods; they do not prove clinical accuracy.

## The task
- **Input:** one row per patient-day, from `daily_features.csv`: weight, leg and chest impedance, the leg
  extracellular-water index (3-frequency spectroscopy), pulse, SpO₂, stand-up time, two yes/no symptom answers,
  amulet night breathing, night sit-ups and activity, plus whether the amulet was worn and the reading quality.
  An empty cell means no reading.
- **Output:** a light per patient-day: 0 green, 1 amber, 2 red.
- **Rules:**
  1. The light on day *t* may use days ≤ *t* only.
  2. Tune and train only on **dev**.
  3. Freeze your method, then score **test**, **external** and **stress** once each.

## Splits (`splits.json` lists every patient id and the source file's sha256)
| Split | Patients | What it is |
|---|---|---|
| dev | 140 × 60 days | the PS cohort minus the held-out 30 % (seed 42): features **and** labels |
| test | 60 × 60 days | held out |
| external | 1,000 × 180 days | a separately generated, messier and longer cohort |
| stress | the 60 test patients | re-made with a weaker key assumption: in weight-silent patients the leg reading only half responds |

## Scoring (`score.py`, definitions fixed in `engine/evaluate.py`)
- **Caught:** a red on at least one day between worsening onset and the day before the visit.
- **Normal days quiet (specificity):** the share of normal days with no red.
- **Median lead:** the number of days from the first red in the worsening window to the visit.
- **False alerts per patient-month:** red *runs* that start on a normal day. A long run counts once.
- **Learning days:** days before day 14 are not scored (that is when every method learns the patient's normal).
- **Uncertainty:** a 95 % range from 1,000 bootstrap resamples of patients.

```
python benchmark/score.py my_submission.csv test
```
Your submission has columns `patient_id, day, light`, one row for every patient-day of the split.
Example submissions are in `submissions/`.

## Baselines (`bench.py`, results in `LEADERBOARD.md`)
Every baseline is tuned on dev under the same budget: **0.21 false alerts per patient-month**.
- **Weight rule:** ≥ 2 kg in 2–3 days (SCALE-HF). This is what most programmes use.
- **Weight trend MACD** (Gyllensten 2016).
- **Logistic regression:** built on per-signal worsening scores against each person's own normal.
- **HridayMitra rules engine v3:** personal baselines, worsening-only scores, three signal families, a two-witness
  red rule and hysteresis.
- **HridayMitra hybrid:** the rules propose a red at a lower threshold; a logistic model trained on dev must
  confirm it.

## Datasheet
- **Made by:** `sim/patients/make_patients.py` (seeds in each `DATA.md`). Every parameter is listed with its source.
  Parameters marked ASSUMPTION are guesses and are stress-tested in `engine/assumption_sensitivity.py`.
- **Physiology** comes from published studies: weight gain before admission, night breathing rate (NOTICE-HF),
  heart rate, and the share of weight-silent admissions.
- **Measurement** comes from our LTspice and Monte Carlo circuit simulations: impedance noise and how impedance
  responds to fluid.
- **Mess included:** missing days, a guest on the stool, jewellery bridging the foot plates, wet feet, wrong button
  answers, salty meals, infections that raise pulse without fluid, and missed tablets.
- **Not included:** real patients, atrial fibrillation, medicine changes, seasons, and comorbidities beyond infection.
- **Intended use:** comparing early-warning methods and stress-testing them. **Not for** clinical decisions,
  device approval, or training models meant for patients.
- **Privacy:** no human data was collected or used.
- **Version:** v2 adds the spectroscopy column (`leg_ewi`), fixed splits, a public scorer and the stress split.
  v1 was weight, impedance, pulse and symptoms only.
- **License:** not yet chosen by the team (suggested: CC BY 4.0 for the data, MIT for the code).
