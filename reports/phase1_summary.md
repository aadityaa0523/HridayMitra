# Phase 1 results (synthetic data only; monitoring, not diagnosis)

Threshold T = 7.0, tuned on 140 training patients (false-alert budget 0.21 per patient-month), frozen in
engine/frozen_params.json before scoring any test patient.

| Cohort | System | Sensitivity | Specificity | Median lead (days) | False alerts / patient-month |
|---|---|---|---|---|---|
| PS held-out (60 patients, 35 events) | HridayMitra | 0.57 | 0.998 | 2 | 0.03 |
| | Weight rule 1 (SCALE-HF) | 0.40 | 0.976 | 2 | 0.53 |
| | Weight MACD (Gyllensten) | 0.23 | 0.945 | 2 | 0.22 |
| Real-world (1000 patients, 100 events, external) | HridayMitra | 0.61 | 0.993 | 2 | 0.04 |
| | Weight rule 1 | 0.31 | 0.984 | 2 | 0.38 |
| | Weight MACD | 0.20 | 0.953 | 3 | 0.21 |

Key assumption test (all 39 weight-silent events): caught 62 % when the leg reading responds fully,
36 % when it responds half as much. The held-out split has only 8 such events, too few to show this.

Limits: synthetic patients built from our own assumptions; median lead time is only 2 days (the PS asks for
several days); small held-out set (wide confidence ranges in reports/phase1_results.csv).
