# HridayMitra: where we started, what changed, and why

## 1. Initial ideas → final product

| Stage | Idea | What happened |
|---|---|---|
| First idea | Wrist band + SMS | Dropped: a wrist cannot measure fluid in the legs or chest; elders forget to charge and wear bands |
| Explored | Ankle band, toe ring, stole pendant | Toe ring rejected (not worn by men); pendant kept, as the amulet |
| Rejected by the team | Vest, smart pillow | "No one will wear a vest"; the pillow did not suit rural homes or shared beds |
| Locked | Foldable **check-in stool** (weight, 8-electrode impedance, finger PPG, voice, buttons, SIM800L) + **Kavach amulet** + **SMS care loop** | Satisfies every PS requirement under ₹5,000 |
| Build guide v1 → v3 | v2 added hand electrodes (chest by segmental subtraction) and the INA126; v3 cut cost (one HX711 bridge, voice from flash, no boot pins) | v3 is the build reference |

## 2. Decisions taken during the build (most recent last)

| # | Decision | Why | Evidence |
|---|---|---|---|
| 1 | Pretend patients built on a hidden "congestion" number, with every parameter marked as published / LTspice / ASSUMPTION | No human data allowed; every number must be traceable | `data/processed/DATA.md` |
| 2 | Guest days 3% → 1% | Weight rule gave 3× the published false-alert rate; calibrated to published results | `reports/calibration_check.csv` |
| 3 | Thresholds tuned on training patients only, then frozen | Honest testing; judges check this | `engine/frozen_params_v2.json` |
| 4 | Engine v2 (T = 7 → 6.5) | +9 points sensitivity at the same false alerts | `reports/leadtime_v2_results.csv` |
| 5 | No slow-drift (CUSUM) detector | Gave 5–7 days lead but 5× the false-alert budget | `reports/leadtime_v2_grid.csv` |
| 6 | Amber = patient-only "check again"; red = SMS | Amber gives 4 days' notice but fires 1–2× a month; only red should reach the family | `reports/amber_lead_results.csv` |
| 7 | ASHA always told at 2 h unless the family replies "fine" | First design left 14% of alerts never reviewed; now 6% | `reports/careloop_results.csv` |
| 8 | Care-loop ladder: family 1 → family 2 (30 min) → ASHA (2 h) → PHC doctor (6 h) | Best simulated result (92% reviewed before the visit); replaces the older product-brief version | `sim/careloop/careloop.py` |
| 9 | **R8/R9 bias resistors 1 MΩ → 10 MΩ** | Monte Carlo of 100 cheap-part stools: 1 MΩ gave up to 12% error and an unusable chest reading; 10 MΩ: 99% within 2% | `sim/circuit/montecarlo.py` |
| 10 | Firmware reads impedance with a Goertzel filter, never peak-to-peak; measure on battery | Mains hum: peak-to-peak 18% wrong with a charger; Goertzel ≤ 0.17% | `sim/circuit/hum.py` |
| 11 | Toe-ring / plate check in the engine (> 25% jump → "no reading") | LTspice showed a ring bridging plates reads 58–86% high | `tests/test_alert_engine.py` |
| 12 | Amulet radio: **Bluetooth Low Energy**, summary in the advertisement (no pairing) | Built into both ESP32s (₹0), low power, works offline, nothing to pair for elders | `firmware/hridaymitra_amulet/` |
| 13 | Cost counted as build cost only (no shipping) | Team decision | `tools/cost_sim.py` |
| 14 | Engine runs **on the ESP32** (C++ port), the laptop only logs and shows | PS demands offline operation; proven identical to Python (100% of 3,231 days) | `tests/test_engine_parity.py` |
| 15 | "No check-in today" now holds yesterday's light; new "still learning" state for the first ~10 days | Found a gap: the no-data path never fired; cold start was silent | `engine/alert_engine.py` |
| 16 | Keep the rule engine, not machine learning, as the main decider | Logistic regression catches 6–12 points more but with 3–5× the false alarms; rules explain themselves and run in 7 KB | `reports/ml_comparator.csv` |
| 17 | Voice prompts from Windows' offline speech engine for now; recorded human clips override them | Gives working audio today; Hindi/Tamil need a human voice | `tools/make_voice_clips.py` |
| 18 | Missed days on the stool detected from the SIM800L network clock | No RTC on the board; keeps the history true | `clockNow()` in the stool firmware |
| 19 | **Product layer** around the engine (lights unchanged, so all frozen results stay valid): doctor's sick-day plan, coaching tips, two users per stool, daily self-test with service SMS, 11:00 missed check-in reminder, Sunday ASHA summary, village dashboard, OPD report, ABDM/FHIR export | Another team also built a chair; the difference has to be the product around it | `engine/product.py`, `tests/test_product.py`, firmware `duties()` |
| 20 | Seat vibration motor on GPIO19 (₹40) and tablet-drawer switch on GPIO36 (₹25); AD8232 LO− dropped to free GPIO36 | Hearing loss is common in elders; medicine adherence is measured instead of asked. Build cost now ₹4,243–4,397 | `tools/make_schematic.py` (ERC 0), build guide v3 section 4 |
| 21 | Battery level and signal strength read from the SIM800L (AT+CBC, AT+CSQ) | No free analog pin needed for the self-test | `selfTest()` |
| 23 | **Wokwi with three custom chips**: virtual patient with an 8-electrode front end (sliders: leg/chest fluid, lifted foot, hum), MAX30102 (pulse, SpO₂, finger), SIM800L with a phone screen (replies, missed call, outage, battery) | Wokwi has none of these parts; judges can make the virtual patient sick and watch the real firmware react. Production firmware builds with `HM_WOKWI` (no BLE, 1 s = 1 min, 20 days preloaded) | `wokwi/`, `tools/make_wokwi.py` |
| 22 | **Software-in-the-loop proof**: the real firmware is compiled on a laptop against an emulated world (body impedance through the ADC, HX711 bits, MAX30102 FIFO, SIM800L AT commands, buttons, BLE, flash) and lives a scripted month | No boards yet; this proves the firmware's logic end to end. It found 3 real bugs, now fixed: user 1's usual weight started at 0 kg; a red day could pass with no SMS after an earlier red; user 1 was not recognised once a second user was enrolled. Also fixed a rare lost-reply race | `tests/sil/`, `tests/test_firmware_sil.py`, `reports/sil_run.log` |

## 3. Where it can still improve (after the hackathon)

1. **Bench build vs simulation**: build the resistor phantom and the stool, compare with LTspice (the biggest open risk).
2. **Real voices**: record Hindi and Tamil prompts (drop WAVs into `firmware/voice/hi/`, run `python tools/make_voice_clips.py --lang hi`).
3. **SpO₂ calibration** against a reference oximeter (the formula is generic).
4. **Hybrid engine**: add learned weights (logistic regression) inside the two-witness rules, aiming for its +6–12 points without its false alarms.
5. **Lead time**: a trend detector that respects the alert budget (the drift detector gave 5–7 days but too many alarms).
6. **A ₹100 real-time clock (DS3231)** so missed days are known even without network time.
7. **Amulet**: validate breathing and sit-up detection on a breathing phantom or recorded motion data; tune the fall threshold.
8. **Clinical pilot** (ethics-approved): compare the chest reading with lung ultrasound B-lines; refit the alert threshold on real data.
9. **Wokwi** simulation of the firmware's check-in flow (optional, for the demo).
10. **Hardware**: a printed circuit board from the KiCad schematic, stainless-steel plates, and a splash-proof enclosure.
