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

Build cost: **₹4,188–4,343** (Monte Carlo of the parts list); the limit is ₹5,000.

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

## Quick start (Python 3.11)

```bash
pip install -r requirements.txt
python -m pytest tests -q                        # 31 tests (the 4 schematic tests skip without KiCad)
streamlit run demo/app.py                        # patient, family and ASHA/doctor views, with "break it" switches
```

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
| `demo/` | Streamlit demo |
| `docs/` | build guide v3, wiring guide, physical build pack, block diagram, phase plan |
| `reports/` | all results (CSV, PNG, summaries) |
| `tests/` | pytest suite |

## Honest limits
- **Synthetic data:** the patient data is synthetic and calibrated to published weight-rule results. It shows the method works on the patterns we modelled; it isn't clinical accuracy.
- **Lead time:** the 2-day lead time is mostly set by how worsening is defined (3–10 days, speeding up at the end). The assumption sweep shows this matters more than any hardware assumption.
- **Chest reading:** it's a weak signal. A +10% change stands out only after about a week of averaging, so it supports the leg and weight readings rather than replacing them.
- **Untested on people:** the circuit is simulated with a textbook body model and hasn't been compared with a bench build yet. The SpO₂ calibration is generic.
- **Safety:** never use it on anyone with a pacemaker or ICD, and run on battery only while a person touches the electrodes.
