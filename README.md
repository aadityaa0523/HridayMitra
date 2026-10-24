# HridayMitra: early warning of worsening heart failure at home

> **Monitoring, not diagnosis.** Research prototype for the Transfinitte hackathon (hardware track, PS by Dare 2 Dream Ventures).
> All patient data in this repository is **synthetic**. No human data was collected.

An elderly patient sits on a foldable **check-in stool** for about 90 seconds a day. It measures:
- **weight**, through 4 load cells;
- **leg and chest fluid**, through 8-electrode impedance at 5 kHz (4 foot plates and 4 hand strips);
- **pulse and SpO₂**, through a finger sensor;
- **stand-up speed**;
- **two spoken yes/no questions**, answered with buttons.

A worn **Kavach amulet** adds night breathing, night sit-ups, activity, falls and SOS. It syncs to the stool over Bluetooth Low Energy.

An **offline alert engine** on the ESP32 learns each patient's own normal and turns green, amber or red. Each red alert gives its reasons in plain words. It sends an SMS over 2G and starts a **care loop**: family member 1 → family member 2 (30 min) → ASHA worker (2 h) → PHC doctor (6 h).

Build cost: **₹4,243–4,397** (Monte Carlo of the parts list); the limit is ₹5,000.

## Results (synthetic cohorts, threshold frozen on training patients before testing)

| | Our engine (v2) | Weight rule (SCALE-HF comparator) |
|---|---|---|
| Sensitivity, held-out patients | **66%** | 40% |
| Specificity | 99.8% | 97.6% |
| Median lead time before hospital visit | 2 days (4 days counting amber "check again") | 2 days |
| False alerts per patient-month | **0.03** | 0.53 |
| External 1,000-patient cohort: sensitivity / false alerts | 66% / 0.06 | 31% / 0.38 |

- **Robustness:** it beats the weight rule in **all 46** assumption-sensitivity scenarios and in 14 of 15 stress cases. In the 15th (10% guest days) the rule catches more but fires about 30× more false alerts.
- **Care loop:** in simulation, 92% of red alerts get a clinical review before the hospital visit, versus 27% with a single SMS.
- **Circuit:** LTspice puts every path within 0.05% of the exact answer. A Monte Carlo of 100 stools built from 5% parts keeps 99% of readings within 2%. It also changed the design: the bias resistors are now 10 MΩ.
- **Heart rate on real ECG:** PhysioNet BIDMC CHF, 3 records: mean sensitivity 93%, heart-rate error 0.66 bpm.

Details: `reports/phase1_summary.md`, `reports/phase2_summary.md`, `sim/circuit/HOW_TO_VERIFY.md`.

## Quick start (Python 3.11): one command for everything

```bash
python run.py setup          # install packages, make the synthetic cohorts if missing
python run.py test           # 41 tests, incl. the real firmware run through an emulated month (26 claims) and C++ engine = Python engine
python run.py demo           # dashboard: patient light + voice, family SMS, ASHA/doctor trends, "break it" switches
```

| What you want | Command |
|---|---|
| Watch a pretend patient arrive live in the dashboard (no hardware) | `python run.py live --simulate P0022`, then `python run.py demo` → "Live stool" |
| Compile both boards (needs `arduino-cli` with the esp32 core) | `python run.py firmware` |
| Flash the stool (COM5) and the amulet (COM6) | `python run.py firmware --upload COM5 --amulet-port COM6` |
| Log the real stool's check-ins into the dashboard | `python run.py live --port COM5` |
| Prove the real stool decides exactly like the tested engine | `python run.py hil --port COM5` |
| Simulate the whole stool in Wokwi: drag a "leg fluid" slider and watch the SMS arrive on a virtual phone | `python run.py wokwi`, then `wokwi/README.md` |
| Re-run every result, rebuild every document | `python run.py reproduce`, `python run.py docs` |
| Everything | `python run.py all` |

**The flow:** amulet → (BLE) → stool runs the check-in and the alert engine offline → light + voice + SMS care loop → (USB, optional) laptop bridge → live dashboard.

## Firmware
- `firmware/hridaymitra_stool/`: ESP32 DevKit. The 90 s check-in, HX711 weight, 4 impedance paths with Goertzel, MAX30102 pulse/SpO₂, 3 questions, stand-up time, amulet scan, **the alert engine on the chip** (`engine_core.h`, identical to the Python engine), SMS ladder with retries, replies and missed calls, engine state saved in flash. Phone numbers go in `config.h`.
- `firmware/hridaymitra_amulet/`: ESP32-C3 + MPU6050. Night breathing, night sit-ups, activity, falls and SOS, sent in the BLE advertisement (no pairing).
- Voice prompts: `python tools/make_voice_clips.py`. Recorded Hindi/Tamil WAVs in `firmware/voice/<lang>/` replace the built-in English voice.

## Documents
- `docs/HridayMitra report.pdf` (2 pages) and `docs/HridayMitra pitch deck.pdf`, plus `docs/PITCH_SCRIPT.md`. All three are regenerated from the live results.
- `docs/EVIDENCE.md`: every PS requirement → proof file, the failure-modes table, the assumption ledger.
- `docs/DECISIONS.md`: the starting ideas, every design decision with evidence, and the next improvements.
- Build guide v3, wiring guide, physical build pack, block diagram: `docs/`. KiCad: `hardware/kicad/`.

## Reproduce everything

| Step | Command |
|---|---|
| Pretend patients (PS cohort, 200 × 60 days) | `python sim/patients/make_patients.py` |
| Real-world cohort (1,000 × 180 days) | `python sim/patients/make_patients.py --patients 1000 --days 180 --event-fraction 0.1 --seed 43 --out data/processed/realworld` |
| Tune on training patients, freeze, test once | `python engine/leadtime_v2.py` |
| Stress tests and ablations | `python engine/stress_and_ablation.py` |
| Assumption sensitivity (46 cohorts) | `python engine/assumption_sensitivity.py` |
| Care-loop simulator | `python sim/careloop/careloop.py` |
| Heart rate on PhysioNet BIDMC CHF | `python engine/validate_bidmc_hr.py` |
| LTspice: legs, chest paths, Monte Carlo, hum (needs LTspice) | `python sim/circuit/trunk_paths.py`, `montecarlo.py`, `hum.py` |
| KiCad schematic + ERC + netlist checks (needs KiCad 9) | `python tools/make_schematic.py` |
| Block diagram, cost simulation | `python tools/make_block_diagram.py`, `python tools/cost_sim.py` |

## Repository map

| Folder | What is inside |
|---|---|
| `engine/` | `signals.py` (raw → numbers), `alert_engine.py` (baseline, scores, lights, reasons), `evaluate.py` (the four PS measures, no-peeking check), baselines, tuning and test scripts, frozen thresholds |
| `sim/patients/` | synthetic patient generator; every parameter has a source or is marked ASSUMPTION |
| `sim/circuit/` | LTspice netlists, open-and-run files, Monte Carlo, hum test, how to verify |
| `sim/careloop/` | alert → family → ASHA → doctor simulator |
| `hardware/kicad/` | schematic generated from code, ERC report, netlist, PDF |
| `demo/` | Streamlit demo (synthetic cohort or live stool) |
| `firmware/` | stool (ESP32) and amulet (ESP32-C3) sketches; `engine_core.h` = the engine on the chip |
| `run.py` | one command for setup, tests, demo, live stool, firmware, results, documents |
| `docs/` | build guide v3, wiring guide, physical build pack, block diagram, phase plan |
| `reports/` | all results (CSV, PNG, summaries) |
| `tests/` | pytest suite |

## Honest limits
- **Synthetic data:** the patient data is synthetic and calibrated to published weight-rule results. It shows the method works on the patterns we modelled; it isn't clinical accuracy.
- **Lead time:** the 2-day lead time is mostly set by how worsening is defined (3–10 days, speeding up at the end). The assumption sweep shows this matters more than any hardware assumption.
- **Chest reading:** it's a weak signal. A +10% change stands out only after about a week of averaging, so it supports the leg and weight readings rather than replacing them.
- **Untested on people:** the circuit is simulated with a textbook body model and hasn't been compared with a bench build yet. The SpO₂ calibration is generic.
- **Safety:** never use it on anyone with a pacemaker or ICD, and run on battery only while a person touches the electrodes.
