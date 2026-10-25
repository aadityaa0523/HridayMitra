# Leaderboard (HridayMitra-HF benchmark v2)

Every system tuned on **dev** only, under a budget of 0.21 false alerts per patient-month, then scored once. Brackets: 95 % range from 1,000 patient bootstrap resamples. Synthetic data: this ranks methods, it does not prove clinical accuracy.

## test (60 patients, 35 events)

| System | Caught episodes | Normal days quiet | Median lead (days) | False alerts / patient-month |
|---|---|---|---|---|
| HridayMitra hybrid (rules propose, ML confirms) | 86% [0.73-0.95] | 97.9% | 3 | 0.188 [0.08-0.30] |
| Logistic regression only (ML) | 80% [0.65-0.91] | 98.8% | 2.5 | 0.115 [0.04-0.21] |
| HridayMitra rules engine v3 (T 7.0) | 66% [0.49-0.81] | 98.7% | 3 | 0.058 [0.01-0.11] |
| Weight rule (SCALE-HF, >=2 kg / 2-3 days) | 40% [0.25-0.57] | 97.6% | 2 | 0.534 [0.36-0.72] |
| Weight trend MACD (Gyllensten) | 23% [0.09-0.38] | 94.5% | 2 | 0.216 [0.12-0.33] |

## external (1000 patients, 100 events)

| System | Caught episodes | Normal days quiet | Median lead (days) | False alerts / patient-month |
|---|---|---|---|---|
| HridayMitra hybrid (rules propose, ML confirms) | 86% [0.79-0.93] | 99.0% | 3 | 0.087 [0.08-0.09] |
| Logistic regression only (ML) | 81% [0.73-0.89] | 99.2% | 2 | 0.083 [0.08-0.09] |
| HridayMitra rules engine v3 (T 7.0) | 72% [0.63-0.80] | 99.0% | 2 | 0.056 [0.05-0.06] |
| Weight rule (SCALE-HF, >=2 kg / 2-3 days) | 31% [0.22-0.41] | 98.4% | 2 | 0.376 [0.36-0.39] |
| Weight trend MACD (Gyllensten) | 20% [0.13-0.28] | 95.3% | 3 | 0.206 [0.19-0.22] |

## stress (60 patients, 35 events)

| System | Caught episodes | Normal days quiet | Median lead (days) | False alerts / patient-month |
|---|---|---|---|---|
| HridayMitra hybrid (rules propose, ML confirms) | 86% [0.73-0.95] | 97.9% | 3 | 0.188 [0.08-0.30] |
| Logistic regression only (ML) | 77% [0.61-0.89] | 98.8% | 2 | 0.115 [0.04-0.21] |
| HridayMitra rules engine v3 (T 7.0) | 63% [0.46-0.78] | 98.7% | 2.5 | 0.058 [0.01-0.11] |
| Weight rule (SCALE-HF, >=2 kg / 2-3 days) | 40% [0.25-0.57] | 97.6% | 2 | 0.534 [0.36-0.72] |
| Weight trend MACD (Gyllensten) | 23% [0.09-0.38] | 94.5% | 2 | 0.216 [0.12-0.33] |
