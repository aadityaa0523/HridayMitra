# HridayMitra: early warning of worsening heart failure at home

[![tests](https://github.com/aadityaa0523/HridayMitra/actions/workflows/tests.yml/badge.svg)](https://github.com/aadityaa0523/HridayMitra/actions/workflows/tests.yml)
![python](https://img.shields.io/badge/python-3.11-blue)
![node](https://img.shields.io/badge/node-22.12%2B-green)
![data](https://img.shields.io/badge/data-synthetic%20only-orange)
![status](https://img.shields.io/badge/status-research%20prototype-lightgrey)
![license](https://img.shields.io/badge/license-MIT-brightgreen)

> **Monitoring, not diagnosis.** Research prototype for the Transfinitte 2026 hackathon (hardware track, problem statement by Dare 2 Dream Ventures).
> All patient data in this repository is **synthetic** (plus public PhysioNet BIDMC ECG for heart rate). No human data was collected.

## The idea: turn **any chair at home** into a heart-failure check-in

<p align="center"><img src="Deliverables/concept_any_chair.webp" width="900" alt="HridayMitra concept: a weighing platform with foot electrodes under the family's own chair, and a hand sensor bar held on the lap or fixed to the armrests"></p>

**No special chair to buy. No patch to wear.**

- **Use the chair you already have.** A stool, a plain wooden chair, a plastic chair or an armchair: put it on our thin weighing platform. Nothing is fixed to the chair. (Not for wheeled or wobbly chairs.)
- **Just sit, feet on the plates.** 4 stainless foot plates (heel and forefoot of each foot) and 4 load cells in the platform.
- **Hands on the sensor bar,** held on the lap **or fixed to the chair's armrests or handles:** 4 hand strips, a fingertip pulse sensor, ✓ / ✗ / SOS buttons, a speaker and a status light.
- **90 seconds a day.** A voice guides the elder in their language. Weight, fluid in the legs and **chest (without touching the chest)**, pulse, oxygen, sit-to-stand speed and 3 yes/no questions.
- **It learns each person's own normal** and warns the family by **SMS about 3 days before** a hospital visit, with the reason in plain words: family → ASHA worker → PHC doctor.
- **Kavach amulet** worn on a cord adds night breathing, sitting up at night and daily walking.
- **₹4,402** build cost (limit ₹5,000), because the family's own chair costs nothing.

**In one line:** any household chair + a weighing platform + a hand bar + an amulet = a 90-second daily check-in that warns the family about **3 days before** a heart-failure hospital visit, for about **₹4,400**.

## For judges: start here

**Browse by area** (each folder has its own README with images, results and links to the code):

| Folder | Inside |
|---|---|
| [📁 Deliverables](Deliverables/) | Concept image (any chair), pitch video, report, storyboard, block diagram, schematics, cost report, PCB, simulation video |
| [📁 01_Hardware_Design](01_Hardware_Design/) | Prototype photo, block diagram, 4 schematic sheets, front end with test points, power budget, routed PCB + Gerbers, parts list (₹4,402) |
| [📁 02_Software_and_Analytics](02_Software_and_Analytics/) | Signal processing, personal-baseline alert engine, hybrid ML, firmware engine, care loop, Saathi app, a real alert SMS |
| [📁 03_Data](03_Data/) | Synthetic dataset card, sample patients, how noise is modelled |
| [📁 04_Testing_and_Validation](04_Testing_and_Validation/) | The four PS measures with 95 % ranges, assumption and stress tests, PhysioNet real-data checks, 217 automated tests |
| [📁 05_Simulation](05_Simulation/) | Live Wokwi, demo video, LTspice results, firmware emulator, PCB DRC |


<p align="center"><img src="Deliverables/prototype_photo.jpg" width="320" alt="Working prototype: breadboard check-in unit on a household chair, Kavach amulet worn on a cord"></p>

| Deliverable (PS requirement) | Where |
|---|---|
| 5-minute pitch video | [Deliverables/5min_pitch.mp4](Deliverables/5min_pitch.mp4) |
| **Live simulation (Wokwi, runs in the browser)** | **[wokwi.com/projects/478945371100594177](https://wokwi.com/projects/478945371100594177)** |
| Simulation demo video (one patient month, circuit + SMS) | [Deliverables/simulation_demo.mp4](Deliverables/simulation_demo.mp4) |
| Technical report | [Deliverables/report.pdf](Deliverables/report.pdf) |
| User-journey storyboard | [Deliverables/user_journey_storyboard.pdf](Deliverables/user_journey_storyboard.pdf) |
| Block diagram | [Deliverables/block_diagram.webp](Deliverables/block_diagram.webp) · production set [HM-HW-001](docs/hardware/HM-HW-001_block_diagram.pdf) |
| PCB of the custom sensor board (2-layer, 70 × 50 mm, fully routed, 0 DRC errors) | [3D view](Deliverables/pcb_3d.png) · [Gerbers](Deliverables/pcb_gerbers.zip) · [KiCad files](hardware/pcb/) |
| Schematics (4 sheets) and power budget | [Deliverables/schematics.pdf](Deliverables/schematics.pdf) · [HM-HW-003](docs/hardware/HM-HW-003_power_budget.pdf) |
| Cost report (₹4,402, under ₹5,000) | [Deliverables/cost_report.pdf](Deliverables/cost_report.pdf) |
| Working phone app (Saathi, offline, 10 languages) | [app/](app/) |
| Firmware (stool + amulet, ESP32) | [firmware/](firmware/) |

### User-journey storyboard

[![HridayMitra user journey storyboard](Deliverables/user_journey_storyboard.png)](Deliverables/user_journey_storyboard.pdf)

**The four PS measures** (hybrid engine, held-out test set): sensitivity **86 %**, specificity **97.9 %**, median lead time **3 days**, false alerts **0.19 per patient per month**.

**Headline results** (synthetic benchmark, tuned on dev only, scored once; 95 % bootstrap range in brackets; full table in [benchmark/LEADERBOARD.md](benchmark/LEADERBOARD.md)):

| System | Caught episodes | False alerts / patient-month | Median warning |
|---|---|---|---|
| **HridayMitra hybrid** (test, 60 patients) | **86 % [73–95]** | 0.19 [0.08–0.30] | 3 days |
| **HridayMitra hybrid** (external, 1,000 patients) | **86 % [79–93]** | 0.09 | 3 days |
| Weight rule, SCALE-HF (today's standard, test) | 40 % [25–57] | 0.53 | 2 days |

**Checked automatically:** 67 Python tests, 109 app tests, 41 firmware-emulator checks; firmware compiles (66 % of flash). Real-data checks on public PhysioNet BIDMC: pulse median error 0.91 bpm, breathing 1.0 breath/min.

**Jump to:** [For judges](#for-judges-start-here) · [The problem](#the-problem-and-the-idea) · [How it works](#how-it-works) · [Results](#results) · [Quick start](#quick-start) · [Saathi phone app](#saathi-phone-app) · [Hardware and firmware](#hardware-and-firmware) · [Simulate it](#simulate-it-no-hardware) · [Reproduce](#reproduce-everything) · [Repository map](#repository-map) · [Documents](#documents) · [Troubleshooting](#troubleshooting) · [Honest limits](#honest-limits)

---

## The problem and the idea

Fluid builds up silently for days before a heart-failure admission. A daily weight rule catches about one event in three and floods families with false alarms. Elders will not wear sticky patches, and rural homes have power cuts, 2G and low literacy.

HridayMitra measures what a weight scale cannot (fluid in the legs and chest) in the way an elder will actually accept (sit down, hands on a bar), learns each person's *own* normal, and tells the family **why** it raised an alert, by SMS, with no internet.

| Part | What it is | What it measures |
|---|---|---|
| **Check-in set** | A weighing platform under the patient's own chair (4 load cells, 4 stainless foot plates) plus a hand sensor bar (4 hand strips, fingertip optical cradle, ✓ / ✗ / SOS buttons, speaker, status light). No chair modification; never on wheeled chairs. | Weight; 8-electrode bioimpedance spectroscopy at 5 / 20 / 50 kHz (legs, arms, both sides → chest fluid by segmental subtraction; water outside the cells from a Cole-model fit, which cancels foot position and skin temperature); pulse and SpO₂; sit-to-stand speed from the platform's force; 3 spoken yes/no questions |
| **Kavach amulet** | ESP32-C3 + accelerometer on a breakaway cord, no magnets | Night breathing, night sit-ups, activity, a weekly 6-minute walk test (it finds the best 6 minutes itself, no button), falls, SOS |
| **Offline alert engine** | Runs on the ESP32 | Personal baseline, green / amber / red, reasons in plain words |
| **Care loop** | SMS over 2G with retries | family 1 → family 2 (30 min) → ASHA worker (2 h) → PHC doctor (6 h) |
| **Saathi app** | Offline PWA, 10 Indian languages | Elder, family, ASHA and doctor views |

## What is new here

1. **Chest fluid without touching the chest.** 8 electrodes (2 per foot, 2 per hand) give legs, arms and both body sides; subtracting them isolates the trunk. No vest, no patch.
2. **Fluid outside the cells, not just "impedance".** Readings at 5, 20 and 50 kHz are fitted with a Cole model. The ratio cancels foot position and skin temperature, the two things that break home bioimpedance.
3. **Sit-to-stand time with no extra sensor.** The weighing platform already sees the force of standing up; we integrate it twice into the rise of the body's centre of mass and fit a smooth rise curve.
4. **A 6-minute walk test nobody has to start.** The amulet finds the best 6 minutes of walking in the week by itself.
5. **Two witnesses before red.** A red alert needs two independent body systems (for example fluid and heart-lungs) to agree, which is why false alerts stay at about 0.19 per patient per month.
6. **Works with no smartphone and no internet.** The engine runs on the ESP32; alerts go by 2G SMS, family → ASHA → PHC doctor.

## Using it every day (90 seconds)

| Step | Elder does | Device does |
|---|---|---|
| 1 | Sits on their own chair at the usual time (an SMS reminder if the check-in is missed) | Platform recognises the person by weight; a guest is ignored |
| 2 | Puts bare feet on the plates, holds the bar, finger in the cradle | Checks contact; if bad, the voice asks again ("no reading", never a made-up number) |
| 3 | Sits still about 60 s | Weight, 8-electrode impedance at 3 frequencies, pulse and SpO₂ |
| 4 | Answers 3 spoken questions with ✓ / ✗ | Breathless? Extra pillows? Tablets taken? |
| 5 | Stands up | Sit-to-stand time from the platform force |
| 6 | Sees the light: green / amber / red | Amber: check again tomorrow. Red: SMS to family with the reason |

The amulet needs nothing: it is worn on a cord day and night and charges on the dock beside the chair.

**Why they keep using it for months**
- **One habit, no setup:** the same chair, the same time, 90 seconds, guided by voice in their language. No app, no reading, no charging cables to manage for the elder.
- **Someone is watching:** a missed check-in sends a reminder, and the ASHA worker gets a Sunday summary, so a skipped week does not go unnoticed.
- **It gives something back:** a green light and "your reading is normal" every day; a coaching tip on amber days; tablet reminders.
- **Few false alarms:** about one false alert every 5 months per patient, so families do not learn to ignore it.
- **Survives Indian homes:** runs on battery through power cuts, retries SMS on weak 2G, ignores guests, toe rings and lifted feet.

## Is the synthetic data circular?

We designed the patients, so we tested what happens when our guesses are wrong ([reports/assumption_sensitivity.csv](reports/assumption_sensitivity.csv), [reports/stress_and_ablation.csv](reports/stress_and_ablation.csv)):

- **Every assumption pushed to both extremes:** the engine stays within the false-alert budget in all cases and beats the weight rule in all cases. Sensitivity moves most with how long and how fast worsening happens (30–98 %), which is honest: it depends on the disease, not on our hardware guesses.
- **Leg reading gives no signal in weight-silent patients** (worst case): sensitivity drops from 67 % to 52 %, still above the weight rule (29 %).
- **Real life:** 50 % of days missed, power-cut gaps, guests, wet feet, amulet worn half the time, electrodes ageing: the engine still beats the weight rule in every case except guest days, where the weight rule catches 1 point more but sends 33× more false alerts (3.2 vs 0.10 per patient-month).
- **Remove one part at a time:** without the amulet sensitivity falls to 54 %, without impedance to 65 %, weight alone catches 1 %. Each part earns its place.

This shows the method is robust to our assumptions. It does not replace a clinical study.

## How it works

```mermaid
flowchart LR
  A[Kavach amulet<br/>ESP32-C3 + MPU6050] -- BLE advertisement, no pairing --> S
  S[Check-in set<br/>ESP32 + load cells + 8-electrode impedance + finger sensor<br/>offline alert engine] -- light + voice --> E[Elder]
  S -- SMS over 2G --> C[Care loop<br/>family 1 → family 2 → ASHA → PHC doctor]
  S -- BLE or USB --> P[Saathi phone app]
  S -- USB, optional --> D[Laptop bridge → live dashboard]
```

### Signals the engine scores

| Signal | Sensor and position | Family | Weight in family | Worse when |
|---|---|---|---|---|
| Body weight | 4 load cells under the platform (corners) → HX711 | fluid | 1.0 | up |
| Leg reading (5 kHz impedance) | 4 stainless foot plates + 4 hand strips, 8 electrodes, ESP32 DAC excitation via MCP6002 → INA126 | fluid | 1.0 | down |
| Leg water outside cells (EWI) | same electrodes, spectroscopy at 5 / 20 / 50 kHz, Cole-model fit (cancels foot position, skin temperature) | fluid | 1.0 | up |
| Chest reading | segmental subtraction of the same 8-electrode readings | fluid | 0.5 | down |
| Resting pulse | MAX30102 in the hand bar's fingertip cradle | heart-lungs | 1.0 | up |
| Night breathing rate | Kavach amulet accelerometer (MPU6050), chest motion at night | heart-lungs | 1.0 | up |
| Oxygen (SpO₂, trend only) | MAX30102 | heart-lungs | 0.5 | down (below 90 % = red at once) |
| Activity + 6-minute walk | Kavach amulet, steps and best 6 minutes of the week | daily life | 1.0 | down |
| Sit-to-stand time | platform force, double-integrated centre-of-mass rise, min-jerk fit | daily life | 1.0 | up |
| Night sit-ups (can't lie flat) | Kavach amulet posture | daily life | 1.0 per sit-up beyond 1 in 3 days | up |
| 3 spoken questions (breathless, extra pillows, tablets) | speaker + ✓ / ✗ buttons, local language | daily life | 1.2 per "yes" beyond 1 in 3 days | yes |

Each signal is scored in "spread units" against the person's **own** normal (median of days t−35..t−7), only in the worsening direction. Family score = strongest sign + half the second. Red needs two families to agree. Source: [engine/alert_engine.py](engine/alert_engine.py).

### Data files (all synthetic)

| File | One row per | Contents |
|---|---|---|
| [data/processed/patients.csv](data/processed/patients.csv) | patient | sex, age, event yes/no, worsening start, admission day, lead days, weight-silent flag, cause, sensitivity |
| [data/processed/daily_features.csv](data/processed/daily_features.csv) | patient-day | what the devices report after quality checks (empty = no reading) |
| [data/processed/truth_daily.csv](data/processed/truth_daily.csv) | patient-day | hidden truth: congestion, guest on platform, infection, salty meal… (never shown to the engine) |
| [data/processed/labels.csv](data/processed/labels.csv) | patient | answer key: worsening start and admission day |
| [benchmark/splits.json](benchmark/splits.json) | — | dev / test / external / stress patient split (each patient in one split only) |
| [engine/frozen_hybrid.json](engine/frozen_hybrid.json) | — | frozen threshold and model weights, tuned on dev only |
| [docs/DATA.md](docs/DATA.md) | — | how the patients were built: every parameter with its published source or marked ASSUMPTION |

**The alert engine** (`engine/alert_engine.py`): each person's baseline is the median/MAD of their own days t−35..t−7. Only the worsening direction is scored. Red needs **two independent witnesses** (for example weight and leg fluid), and bad-data guards ignore guests on the platform, a toe ring bridging two plates, lifted feet and noisy fingers. The same engine exists three times and is held identical by tests:

| Where | File | Checked by |
|---|---|---|
| Python (research, dashboard) | `engine/alert_engine.py` | reference |
| C++ on the ESP32 | `firmware/hridaymitra_stool/engine_core.h` | `tests/test_engine_parity.py`: 100% of 3,231 days |
| TypeScript in the app | `app/src/engine/` | `app/tests/engine.test.ts` against `docs/app/engine_test_vectors.json` (2,732 comparisons) |

**Hybrid engine** (`engine/hybrid.py`): rules propose, a 13-weight logistic model trained on dev only must agree before red. It runs on the laptop and in the benchmark; the stool itself runs rules v3.

## Results

Synthetic cohorts; thresholds tuned on training patients, frozen, then tested once.

| | Rules engine v3 | Hybrid (rules + ML) | Weight rule (SCALE-HF) |
|---|---|---|---|
| Sensitivity, held-out patients | **66%** | **86%** | 40% |
| Sensitivity, external 1,000-patient cohort | **72%** | **86%** | 31% |
| Specificity (held-out) | 98.7% | 97.9% | 97.6% |
| False alerts per patient-month (held-out / external) | **0.06 / 0.06** | 0.19 / 0.09 | 0.53 / 0.38 |
| Median lead time before the visit | 3 days | 3 days | 2 days |

Full tables with 95% ranges and an open scorer anyone can run: [`benchmark/LEADERBOARD.md`](benchmark/LEADERBOARD.md), [`benchmark/README.md`](benchmark/README.md).

- **Calibrated to real trials.** The published FAST and SCALE-HF 1 weight rules score on our external cohort 20% / 33% caught and 4.8 / 4.85 unexplained alerts per year, against the published 23% / 35% and 4.3 / 4.18.
- **Robust.** It beats the weight rule in all 52 assumption-sensitivity scenarios and 14 of 15 stress cases. In the 15th (10% guest days) the rule catches more but fires about 30× more false alerts.
- **Care loop.** In simulation 92% of red alerts get a clinical review before the hospital visit, versus 27% with a single SMS.
- **Circuit.** LTspice puts every path within 0.05% of the exact answer. A Monte Carlo of 100 stools built from 5% parts keeps 99% of readings within 2%, and it found a real design bug (bias resistors 1 MΩ → 10 MΩ).
- **Heart rate on real ECG.** All 15 PhysioNet BIDMC CHF records: median error 0.15 bpm, 13 of 15 within 0.5 bpm. It fails on chf12, a very noisy recording.
- **Cost.** Parts list ₹3,917 (low) to ₹4,890 (plan price). Monte Carlo of price noise: median ₹4,402, 5th–95th percentile ₹4,319–4,486, under ₹5,000 in every draw. Build cost only, no shipping.
- **Firmware.** The whole firmware runs through an emulated month: 26/26 claims pass and every light equals the Python engine.

Details: `reports/phase1_summary.md`, `reports/phase2_summary.md`, `sim/circuit/HOW_TO_VERIFY.md`, [`docs/EVIDENCE.md`](docs/EVIDENCE.md) (every problem-statement requirement → proof file, plus a failure-modes table).

## Quick start

Requires Python 3.11.

```bash
python run.py setup     # install packages, generate the synthetic cohorts if missing
python run.py test      # pytest suite, incl. the real firmware in an emulated month and C++ engine = Python engine
python run.py demo      # dashboard: patient light + voice, family SMS, ASHA/doctor trends, "break it" switches
```

| What you want | Command |
|---|---|
| Watch a pretend patient arrive live in the dashboard (no hardware) | `python run.py live --simulate P0022`, then `python run.py demo` → "Live stool" |
| Compile both boards (needs `arduino-cli` with the esp32 core) | `python run.py firmware` |
| Flash the stool (COM5) and the amulet (COM6) | `python run.py firmware --upload COM5 --amulet-port COM6` |
| Log the real stool's check-ins into the dashboard | `python run.py live --port COM5` |
| Prove the real stool decides exactly like the tested engine | `python run.py hil --port COM5` |
| Simulate the whole stool in Wokwi | `python run.py wokwi`, then `wokwi/README.md` |
| Re-run every result / rebuild every document | `python run.py reproduce` / `python run.py docs` |
| Everything | `python run.py all` |

In the dashboard, try patient **P0022**: slide to the red day, then tick "guest" and "toe ring" and watch the light refuse to lie.

## Saathi phone app

`app/` is **HridayMitra Saathi**: an offline-first PWA (React 18 + TypeScript + Vite, Tailwind, Workbox, Dexie) for one Android phone with role switching.

- **Elder mode:** big status orb, voice commands (offline Vosk packs), medicine reminders, a cancellable two-step emergency button that only opens the dialler.
- **Family:** trends, alerts, medicines, adherence, care contacts. **ASHA:** prioritised visit list, referral PDF and QR, weekly PHC summary. **Doctor:** timeline, care plan versions, labs, consult notes, sensitivity what-if.
- **Reports:** nine English/Hindi PDF formats, FHIR R4 JSON export, offline animated-QR transfer.
- **Device link:** BLE GATT or Web Serial to the stool (same JSON protocol as `firmware/hridaymitra_stool/app_link.h`), plus a built-in simulator.
- **Privacy:** records are encrypted at rest (AES-GCM, PBKDF2 PIN key). PINs are a demo mechanism, not production authentication.
- **Languages:** 10 UI languages (extra ones flagged "machine-translated, needs review"); light, dark and high-contrast themes; 48 pre-generated Hindi audio clips.
- **Verified:** 108 unit tests, 27 browser tests, mobile Lighthouse accessibility 100 (see `docs/app/PHASE_9.md`).

```bash
cd app
python ../tools/prepare_voice_models.py   # optional: 82 MB voice packs, not in git
npm ci && npm test && npm run dev
```

Node.js 22.12+. End-to-end tests: `npm run test:e2e` (Playwright, Pixel 5 viewport).

### Install it on a phone

A PWA installs only from **HTTPS or `localhost`**; plain `http://<lan-ip>` does not work.

**Option A: host it.** `cd app && npm ci && npm run build`, then upload `app/dist/` to the **root** of a static host (Netlify Drop, or Vercel / Cloudflare Pages with root directory `app`, build `npm run build`, output `dist`). The app uses root-absolute paths (`/models/`, `/audio/`), so it cannot sit under a sub-path such as GitHub Pages `/HridayMitra/`. On the phone: Android Chrome → menu → *Install app*; iPhone Safari → Share → *Add to Home Screen*.

**Option B: USB, no hosting (Android).** Enable *Developer options → USB debugging*, connect the phone, then:

```bash
cd app && npm ci && npm run build
npm run preview -- --port 4173          # serves the production build
adb reverse tcp:4173 tcp:4173           # in a second terminal
# phone: Chrome → http://localhost:4173 → menu → Install app
```

Open the installed app once while connected and wait for "App ready offline"; it then works without the cable. Web Bluetooth pairing needs Chrome on Android (not iOS). Per-phase details: `app/README.md`, `docs/app/PHASE_*.md`.

## Hardware and firmware

<p align="center"><img src="docs/hardware/HM-HW-004_pcb_3d_top.png" width="520" alt="Routed 2-layer PCB of the 8-electrode impedance front end, KiCad 3D view"></p>

| Path | Contents |
|---|---|
| `firmware/hridaymitra_stool/` | ESP32 DevKit. 90 s check-in, HX711 weight (one HX711 for all four cells), 4 impedance paths with Goertzel, MAX30102 pulse/SpO₂, 3 questions, sit-to-stand fit, amulet scan, **the alert engine on the chip** (`engine_core.h`), SMS ladder with retries, replies and missed calls, engine state in flash, daily self-test, CHARGE / USE safety switch. Phone numbers and timings are in `config.h`. |
| `firmware/hridaymitra_amulet/` | ESP32-C3 + MPU6050. Night breathing, sit-ups, activity, 6-minute walk (`walk_core.h`), falls, SOS, sent in the BLE advertisement (no pairing). |
| `hardware/kicad/` | KiCad 9 schematic generated from code (ERC 0), netlist, PDF. |
| `docs/hardware/` | HM-HW-001 block diagram, HM-HW-002 schematic set, HM-HW-003 power budget, HM-HW-004 routed PCB of the impedance front end (`tools/make_pcb.py`: KiCad + Freerouting, DRC clean, Gerbers ready to order), system architecture, front-end sheet with LTspice test points. |
| `sim/circuit/` | LTspice netlists, Monte Carlo of 100 devices, mains-hum test, spectroscopy, self-calibration, IEC 60601-1 fault analysis, charger leakage. |

Safety design: two series coupling capacitors plus a current-limit resistor (every single fault within IEC 60601-1 type-BF limits, margin ≥ 12.8×), battery-only measuring, a CHARGE / USE switch that cuts both USB wires, impedance and ECG switchable off for pacemaker / ICD users.

Voice prompts: `python tools/make_voice_clips.py`. Recorded Hindi / Tamil WAVs in `firmware/voice/<lang>/` replace the built-in English voice.

## Simulate it (no hardware)

- **Wokwi** (`wokwi/`): the production firmware on an emulated ESP32 with a *virtual patient* chip (drag leg fluid, chest fluid, lifted foot, mains hum), a MAX30102 chip, a monitor chip showing the engine's decision, and a SIM800L chip with a phone screen that receives the SMS ladder. Build with `python run.py wokwi`; run in the browser in two minutes, see [`wokwi/README.md`](wokwi/README.md).
- **Software-in-the-loop** (`tests/test_firmware_sil.py`, `tests/sil/`): the same firmware compiled for the laptop and driven through a month.
- **Demo video:** [`docs/demo/hridaymitra_month_demo.mp4`](docs/demo/hridaymitra_month_demo.mp4), one month of the stool firmware driving the Wokwi screens.

## Reproduce everything

| Step | Command |
|---|---|
| Synthetic patients (PS cohort, 200 × 60 days) | `python sim/patients/make_patients.py` |
| Real-world cohort (1,000 × 180 days) | `python sim/patients/make_patients.py --patients 1000 --days 180 --event-fraction 0.1 --seed 43 --out data/processed/realworld` |
| Tune on training patients, freeze, test once | `python engine/leadtime_v2.py` |
| Stress tests and ablations | `python engine/stress_and_ablation.py` |
| Assumption sensitivity | `python engine/assumption_sensitivity.py` |
| Published-trial calibration | `python engine/calibrate_published.py` |
| ML comparator, hybrid engine, benchmark | `python engine/ml_comparator.py`, `python engine/hybrid.py`, `python benchmark/bench.py` |
| Score your own method | `python benchmark/score.py my_submission.csv test` |
| Care-loop simulator | `python sim/careloop/careloop.py` |
| Heart rate on PhysioNet BIDMC CHF | `python engine/validate_bidmc_hr.py` |
| LTspice: legs, chest paths, Monte Carlo, hum (needs LTspice) | `python sim/circuit/trunk_paths.py`, `montecarlo.py`, `hum.py` |
| KiCad schematic + ERC + netlist checks (needs KiCad 9) | `python tools/make_schematic.py` |
| Block diagram, cost simulation | `python tools/make_block_diagram.py`, `python tools/cost_sim.py` |

Every synthetic-patient parameter carries a source or is marked ASSUMPTION in [`data/processed/DATA.md`](data/processed/DATA.md); each ASSUMPTION was pushed low and high in the sensitivity sweep.

## Repository map

| Folder | What is inside |
|---|---|
| `engine/` | `signals.py` (raw → numbers), `alert_engine.py` (baseline, scores, lights, reasons), `hybrid.py`, `product.py` (sick-day plan, coaching, two users, FHIR), `sts.py` (sit-to-stand), `evaluate.py` (the four PS measures, no-peeking check), baselines, tuning scripts, frozen thresholds |
| `benchmark/` | Open benchmark v2: fixed splits with sha256, public scorer with bootstrap ranges, 5 baselines, leaderboard |
| `sim/patients/` | Synthetic patient generator |
| `sim/circuit/` | LTspice netlists and analyses |
| `sim/careloop/` | alert → family → ASHA → doctor simulator |
| `firmware/` | Stool (ESP32) and amulet (ESP32-C3) sketches |
| `hardware/kicad/` | Schematic, ERC report, netlist |
| `wokwi/` | Wokwi projects and custom chips |
| `app/` | Saathi PWA |
| `demo/` | Streamlit dashboard |
| `tools/` | Generators for documents, schematics, voice clips, Wokwi projects, stool bridge, cost simulation, `progress.py` |
| `tests/` | pytest suite plus C++ parity checks |
| `data/` | Synthetic cohorts and public BIDMC ECG |
| `reports/` | All results (CSV, PNG, summaries) |
| `docs/` | Report, pitch, build guide, wiring guide, evidence, decisions, app phase docs |
| `research_notes/` | Background research that shaped the design |
| `progress.json` | Workstream progress, rendered by `tools/progress.py` |

## Documents

- `docs/HridayMitra report.pdf` (2 pages) and `docs/HridayMitra pitch deck.pdf`, plus `docs/PITCH_SCRIPT.md`; regenerated from live results by `python run.py docs`.
- [`docs/EVIDENCE.md`](docs/EVIDENCE.md): requirement traceability, failure modes and safeguards, assumption ledger.
- [`docs/DECISIONS.md`](docs/DECISIONS.md): starting ideas, every design decision with evidence, next improvements.
- Build guide v3, wiring guide, physical build pack, user journey storyboard, block diagram: `docs/`.

## Troubleshooting

| Problem | Fix |
|---|---|
| Imports fail in `python run.py test` | Use Python 3.11, then `python run.py setup` |
| `npm run build` complains about missing `/models/*.bin` | `python tools/prepare_voice_models.py` (downloads and checks sha256) |
| "Install app" not offered on the phone | Not HTTPS / localhost, or first load unfinished; reload and wait for "App ready offline" |
| Phone cannot reach `localhost:4173` | Re-run `adb reverse tcp:4173 tcp:4173`; check `adb devices` lists the phone |
| No Bluetooth button in the app | Use Chrome on Android; iOS Safari has no Web Bluetooth |
| Firmware compile or upload fails | Install the `esp32` core for `arduino-cli`; check the COM port; hold BOOT while flashing if the board does not enter download mode |

## Honest limits

- **Synthetic data.** Patients are synthetic and calibrated to published weight-rule results. This shows the method works on the patterns we modelled; it is not clinical accuracy.
- **Lead time.** The 2–3 day lead is mostly set by how worsening is defined (3–10 days, speeding up at the end). The sweep shows this matters more than any hardware assumption.
- **Chest reading.** A weak signal: a +10% change stands out only after about a week of averaging, so it supports the leg and weight readings.
- **Untested on people.** The circuit is simulated with a textbook body model and not yet compared with a bench build. SpO₂ calibration is generic.
- **Safety.** Never use on anyone with a pacemaker or ICD, and measure on battery only while a person touches the electrodes.

## License

[MIT](LICENSE). The medical-safety limits above still apply: this is a research prototype, not a medical device.
