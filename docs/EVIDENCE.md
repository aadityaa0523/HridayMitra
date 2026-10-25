# Evidence pack: PS traceability, failure modes, assumption ledger

## 1. Every PS requirement → design → test → evidence file

| PS requirement | How HridayMitra meets it | Proof (file) |
|---|---|---|
| Effort < 2 min/day, no all-day patch | 90 s seated check-in; amulet worn like a pendant, no adhesive | `firmware/hridaymitra_stool/hridaymitra_stool.ino` (`checkin()`), `docs/block_diagram.png` |
| Local language, low literacy | Voice prompts, 3 lights, 2 big buttons, missed call = reply; clips swappable per language | `tools/make_voice_clips.py`, `demo/app.py` |
| Power cuts, weak internet | 18650 battery; engine runs on the ESP32 (no internet); SMS over 2G, queued + retried | `engine_core.h`, `tests/test_engine_parity.py`, `sim/careloop/careloop.py` |
| Home unit < ₹5,000 | Build cost ₹4,188–4,343 (Monte Carlo of the itemised list) | `tools/cost_sim.py`, `reports/cost_simulation.png` |
| Sensing method + hardware design | Weight, 8-electrode bioimpedance (legs + chest), PPG pulse/SpO₂, stand-up time, questions, amulet motion | `docs/src/HridayMitra build guide v3.html`, `docs/HridayMitra wiring guide.pdf` |
| Block diagram | Generated from code | `tools/make_block_diagram.py` → `docs/block_diagram.png` |
| Schematic of a custom part (sensor circuit + MCU) | KiCad, generated from code, ERC 0 violations, netlist auto-checked vs path table and LTspice values | `tools/make_schematic.py`, `hardware/kicad/`, `tests/test_schematic.py` |
| Parts list in INR | Itemised, low/plan prices, sources | build guide v3 section 3 |
| Simulation proof (free tool) | LTspice legs/chest paths, Monte Carlo of 100 devices, mains hum; Python signal tests | `sim/circuit/`, `sim/circuit/HOW_TO_VERIFY.md` |
| Raw signals → alerts | Goertzel impedance, PPG pulse/SpO₂, breathing, sit-ups, quality gates → engine | `engine/signals.py`, `tests/test_signals.py` |
| Personal baseline | Median/MAD of each person's days t−35..t−7 | `engine/alert_engine.py` |
| Each alert says why | Top reasons in plain words + cause tag, in the SMS and on the screen | `A.explain()`, `Engine::reasons()` |
| Simple screen for patient/family/doctor | Three views + break-it switches + live stool feed | `demo/app.py` (`python run.py demo`) |
| Public or synthetic data, ≥ 20 patients × 30 days, worsening 3–10 days before visit | 200 × 60 d PS cohort + 1,000 × 180 d external cohort; PhysioNet BIDMC CHF for heart rate | `sim/patients/make_patients.py`, `data/processed/DATA.md`, `engine/validate_bidmc_hr.py` |
| Sensitivity, specificity, median lead, false alerts per patient-month | One grader for every system, bootstrap 95% ranges | `engine/evaluate.py`, `reports/*.csv` |
| Patient-level train/test split | 70/30 by patient, seed 42, threshold frozen before testing; no-peeking check | `engine/leadtime_v2.py`, `engine/frozen_params_v2.json` |
| State limits | Report "Honest limits", README, assumption sweep | `docs/HridayMitra report.pdf`, `engine/assumption_sensitivity.py` |
| GitHub with code, setup, working demo on synthetic data | Public repo, CI, one-command flow | `README.md`, `run.py`, `.github/workflows/tests.yml` |
| ≤ 2-page report, 5-min pitch | Generated from the live results | `tools/make_docs.py` → `docs/HridayMitra report.pdf`, `docs/HridayMitra pitch deck.pdf`, `docs/PITCH_SCRIPT.md` |
| "Monitoring, not diagnosis" | On every screen, SMS, document | `demo/app.py`, firmware SMS text |
| No human data collection | Synthetic + public data + bench only | `data/processed/DATA.md` |

## 2. Failure modes and safeguards (FMEA-lite)

| Failure | Effect if unhandled | Safeguard | Tested in |
|---|---|---|---|
| Guest sits on the stool | False alert / polluted baseline | Weight jump > 2.5 kg → day's stool readings ignored | `test_guest_on_the_stool_is_ignored`, stress "10% guest days" |
| Toe ring bridges two plates | Leg reading 58–86% high, hides fluid | > 25% from last week → "no reading" + voice | `sim/circuit/montecarlo.py` (jewellery), `test_toe_ring_bridging_plates_is_ignored` |
| Foot lifted / plate open | Floating 10 MΩ input saturates | ADC clipping > 1% → "no reading" | `test_open_plate_is_rejected` |
| Dry / sweaty skin | Contact 200 Ω–10 kΩ changes reading | Tetrapolar + ratiometric; 10 MΩ bias | LTspice Monte Carlo (99% within 2%) |
| Cheap part tolerances | Device-to-device error | Personal baseline compares each stool with itself; change error 0.13 points | `montecarlo.py` |
| Mains hum (charger plugged in) | Peak-to-peak 18% wrong | Goertzel only; battery-only measuring | `sim/circuit/hum.py` |
| Foot placed differently / limb size / skin temperature | Single-frequency leg reading moves ~3% with no medical cause | Spectroscopy index (Rinf/R0 from 5/20/50 kHz) cancels it: LTspice 0.00% | `sim/circuit/spectroscopy.py`, firmware emulator check "spectroscopy index within 0.5%" |
| Wet feet | Leg reading 3–6% low | Robust baseline + two-witness rule | stress "15% wet-feet days" |
| No finger / moving finger | Wrong pulse/SpO₂ | Perfusion and regularity checks → "no reading" | `test_no_finger` |
| Missed check-ins / power cut | Gaps in history | Network clock fills gaps; light held; engine state saved in flash | stress "power cut", `test_*` (has_data) |
| No network | SMS lost | Queue + retry every 10 min; local voice + red LED still work | `careloop.py` "long outages" |
| Family does not reply | Alert ignored | Ladder: family 2 → ASHA → PHC doctor | `test_ladder_beats_a_single_sms` |
| Family wrongly replies "fine" | Missed event | Engine stays red and re-alerts next check-in | design (`Engine` hysteresis) |
| New user, no baseline | Unreliable scores | "Still learning" state; only the oxygen danger rule active | `learning` flag in engine and demo |
| Infection, not heart failure | Wrong advice | Cause tag: pulse + breathing up with fluid steady | `A.explain()` |
| Pacemaker / ICD | Electrical interference risk | Impedance and ECG off by setting; no magnets in the amulet | build guide safety section |
| Amulet left off | Fewer witnesses | Engine works with stool alone (48% sensitivity without amulet, still above the weight rule) | ablation "Without amulet" |
| Stool hardware degrades over months | Silent wrong readings | Daily self-test: scale, finger sensor, battery, signal, excitation current → "needs service" SMS to the ASHA | `selfTest()` in the firmware |
| Two people share one stool | Mixed baselines, false alerts | Two profiles matched by weight + leg reading; unknown person → nothing saved | `test_two_users_and_guest` |
| Patient forgets the check-in | Gaps, late warning | 11:00 SMS reminder to the family; Sunday summary to the ASHA | `test_nudge_once_after_11`, `test_weekly_summary_and_fhir` |
| Hard of hearing | Prompts missed | Seat vibration before every prompt, lights | firmware `say()` |
| A fault in the circuit (shorted resistor or capacitor, op-amp stuck, DAC full scale) | Unsafe current through the patient | Two series coupling capacitors + current-limit resistor; every single fault within IEC 60601-1 type-BF limits (≥ 12.8× margin) | `sim/circuit/safety.py` |
| Riding an auto-rickshaw or bus counted as walking | Walk test looks better than it is | Steps only from a strong regular rhythm (autocorrelation ≥ 0.5); 0 false steps in synthetic vehicle vibration, fidgeting, turning in bed | `tests/test_walk.py` |
| Loose pendant cord swinging while a frail person shuffles | Walk test under-counts (up to 23%) | Short cord / pendant under clothing (within 2.7%); same person, same cord each week, so the trend still holds | `reports/walk_accuracy.csv` |
| Reference resistor damaged, drifted or wrongly fitted | Every reading wrong by the same factor, silently | Precision Rcal is the reference; (R5 + Rcal)/Rcal checked at each check-in; outside 2.0–2.4 → no numbers, service SMS | `sim/circuit/selfcal.py`, firmware emulator checks |
| Firmware diverges from tested code | Untested behaviour in homes | C++ engine = Python (100% of 3,231 days); the whole firmware run in an emulated month: 26/26 claims pass and every light equals the Python engine | `tests/test_engine_parity.py`, `tests/test_firmware_sil.py`, `run.py hil` on hardware |

## 3. Assumption ledger

Every synthetic-patient parameter, with its source or "ASSUMPTION", is listed in `data/processed/DATA.md` (generated from `sim/patients/make_patients.py`). Each ASSUMPTION was pushed low and high in `engine/assumption_sensitivity.py`; the engine beat the weight rule in all 46 scenarios. The result is most sensitive to how quickly worsening develops (a PS definition), and least to hardware noise. Care-loop timings and response probabilities are assumptions listed in `sim/careloop/careloop.py` (`BASE`).
