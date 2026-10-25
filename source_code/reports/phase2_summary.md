# Phase 2: robustness and the care loop (synthetic data; monitoring, not diagnosis)

Engine: frozen v2 (T = 6.5, tuned on 140 training patients only). Nothing below was retuned.

## 1. Stress tests and ablations (`engine/stress_and_ablation.py` → `stress_and_ablation.csv`)
Real-world cohort: 100 sick + 300 stable patients, 180 days. 95% ranges come from re-drawing patients. Every stress case is also run on the SCALE-HF weight rule.

| Case | Sensitivity (95% range) | False alerts per patient-month | Weight rule: sensitivity / false alerts |
|---|---|---|---|
| Full engine | 0.66 (0.56–0.74) | 0.061 | 0.31 / 0.42 |
| Without impedance | 0.44 | 0.036 | – |
| Without weight | 0.51 | 0.066 | – |
| Without amulet | 0.48 | 0.023 | – |
| 50% of days missing | 0.53 | 0.152 | 0.26 / 0.24 |
| 10% guest days | 0.65 | 0.107 | 0.71 / **3.20** |
| Power cut: 2 gaps of 2–5 days a month | 0.62 | 0.076 | 0.26 / 0.33 |
| Electrode ageing: −3% a month | 0.69 | 0.136 | 0.31 / 0.42 |
| Everything bad at once | 0.56 | 0.241 | 0.47 / 1.73 |

- **Every signal group adds detection:** removing impedance, weight or the amulet costs 15–22 points of sensitivity.
- **Messy homes don't break it:** the engine never drops below the weight rule's sensitivity, except with guests. There the rule fires 3.2 false alerts per patient-month, about 30× ours.
- **One case exceeds the false-alert budget:** "Everything bad at once" (0.24 vs 0.21).
- **Electrode ageing is a pessimistic test:** four-electrode (tetrapolar) measurement already cancels contact changes (LTspice error was 0.1% for contacts from 100 Ω to 10 kΩ).

## 2. Assumption sensitivity (`engine/assumption_sensitivity.py` → `assumption_sensitivity.csv`, `assumption_tornado.png`)
- **Setup:** each of 23 guesses was pushed low and high, giving 46 fresh cohorts (300 patients × 90 days, seed 44). Each patient has their own random stream, so a scenario differs from the default only by the changed guess.
- **The engine beat the weight rule on both sensitivity and false alerts in all 46 scenarios, and stayed within the false-alert budget in all 46.**
- **What moves the result most is the shape and length of the worsening, which is not a hardware property:**
  - Worsening lasting only 3–5 days: sensitivity 0.26.
  - Worsening lasting 7–10 days: sensitivity 0.94.
  - A straight-line worsening raises sensitivity to 0.75 (lead 3 days); a late, steep one drops it to 0.33.
- **Hardware and noise guesses move it little:**
  - 4× circuit noise: 0.63 → 0.58.
  - Chest noise ×2: no change.
  - Guest rate 0–3%: 0.62.
  - Wet feet: 0.62–0.63.
- **Honest reading:** the worsening timeline matters more than any hardware assumption, so the 2-day lead time is largely set by how worsening is defined in the problem statement (3–10 days, speeding up at the end).

## 3. Care-loop simulator (`sim/careloop/careloop.py` → `careloop_results.csv`)
- **The ladder:** SMS to family member 1 → family member 2 at 30 min → ASHA at 2 h (unless the family replied "fine") → PHC doctor at 6 h.
- **Danger alerts** go to everyone at once.
- **Run:** 5,000 alerts per scenario. Leads are taken from the engine's caught real-world events (median 2 days).

| Scenario | Median time to a reply | Median time to clinical review | Reviewed before hospital visit | Never reviewed |
|---|---|---|---|---|
| Rural, full ladder | 0.6 h | 6.1 h | **92%** | 6% |
| Urban | 0.4 h | 5.3 h | 92% | 7% |
| Older ladder (ASHA only if family silent) | 0.6 h | 7.7 h | 85% | 14% |
| One SMS, no ladder (what most systems do) | 0.6 h | never | **27%** | 72% |
| Long outages (40%, 4–12 h) | 0.9 h | 7.4 h | 90% | 5% |
| Family phones mostly off | 1.2 h | 6.3 h | 91% | 7% |
| ASHA post vacant | 0.6 h | 9.1 h | 77% | 22% |
| Everything bad at once | 3.8 h | 12.4 h | 68% | 27% |
| Danger alert, any hour | 0.65 h | 9.1 h | 95% | 4% |

- **Simulation changed the design:** in the first version the ASHA was told only if the family stayed silent. 14% of alerts were never reviewed, so the ASHA is now always told at 2 h.
- **The ladder is the difference:** a single SMS leads to clinical review before the hospital visit only 27% of the time. With the ladder it is 92%.
- **The weakest link is a vacant ASHA post** (77%), so the doctor step at 6 h stays.
- **Cost:** about 3 SMS per alert, roughly ₹0.05 per patient per month.

## Limits
- All timings and probabilities in the care loop are assumptions, listed with sources in `BASE`. They are not measured in Indian homes.
- Not modelled:
  - The patient calling 108 themselves.
  - The stool re-alerting the next morning after a wrong "fine" reply.
  - Language of the message.
- The pretend-patient cohorts are synthetic. These results show robustness of the method, not clinical accuracy.
