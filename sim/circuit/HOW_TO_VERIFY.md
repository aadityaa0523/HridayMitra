# How to check the LTspice simulations yourself (about 10 minutes)

Yes, you can run them on any Windows or Mac laptop. LTspice is free and needs no licence.

## 1. Install LTspice (one time)
1. Go to analog.com, search for "LTspice", and download LTspice for Windows (or macOS).
2. Install with the default options. You don't need to sign in.

## 2. Check the chest (trunk) circuit by hand: `trunk_open_me.cir`
1. Open LTspice, choose **File > Open**, set the file type to "Netlists (*.cir)", and pick `sim/circuit/trunk_open_me.cir`.
2. Press **Run** (the running-man icon). It runs 4 times, once for each electrode path, in a few seconds.
3. Choose **View > SPICE Output Log** and scroll down to `zmeas`. You should see 4 numbers close to these:

   | Path | What it measures | Expected (ohm) |
   |---|---|---|
   | 1 | left foot to right foot (legs) | 578.5 |
   | 2 | left hand to right hand (arms) | 658.4 |
   | 3 | left hand to left foot | 646.4 |
   | 4 | right hand to right foot | 646.4 |

4. Work out the chest value: (Z3 + Z4 − Z1 − Z2) / 2. Expected about **27.9 ohm**. **Pass** if every number is within 1%. Our run was 0.04% off.
5. See the signal: right-click the plot window and choose **Add Trace > V(adc)**. The first 20 ms is the body signal; the next 20 ms is the signal across the 220 Ω reference resistor.

### Two experiments that show the idea works
- **More chest fluid:** on the `.param` line near the top, change `ft=1` to `ft=1.1` and run again. The chest value should fall about **9%**, to about 25.4 Ω.
- **Dry or dirty skin:** change `Rc=1k` to `Rc=10k` and run again. The numbers should hardly move. That is why we use 4 electrodes instead of 2: contact resistance cancels out.

## 3. Check the leg circuit: `z1_open_me.cir`
- **Steps:** same as above. Open the file, press Run, and look for `zmeas` in the log.
- **Expected:** about **603.5 Ω** with `fl=1`.
- **Fluid test:** `fl=1.1` (+10% leg fluid) should give about 551 Ω, which is −8.7%.

## 4. Re-run everything automatically (the same way the results were made)
You need Python 3 with numpy and matplotlib installed. In a terminal, from the project folder, run:
```
python sim/circuit/trunk_paths.py
```
- **What it does:** writes the netlists, runs LTspice in batch mode for 96 runs, compares every reading with the exact formula, and saves `trunk_results.csv` and `trunk_results.png`.
- **If LTspice is installed somewhere else:** edit `LTSPICE = ...` at the top of the script.
- **Manual batch run:** `LTspice.exe -b trunk_paths_5khz.cir` writes `trunk_paths_5khz.log` with all the measured values.

## 5. Monte Carlo: 100 stools from cheap parts (`python sim/circuit/montecarlo.py`, about 4 minutes)
- **Setup:** each simulated stool gets random part values: 5% resistors, a 1.3% R5 (1% part plus temperature), 20% capacitors, amplifier gain ±0.5%, CMRR 60–80 dB and input bias current 5–25 nA. Each is used on a random body (0.7–1.4× size) with 8 random skin contacts from 200 Ω to 10 kΩ. That makes 800 LTspice runs.
- **Design change from this test:** with **1 MΩ** bias resistors (R8/R9), 1% of stools were off by more than 7.6% (worst 12%), and the chest reading was unusable. Cause: a high return-foot contact pushes the whole body's voltage up and down together, and unequal sense contacts working against 1 MΩ turn that into a false difference. **R8/R9 are now 10 MΩ** (same price). All netlists and the wiring guide are updated.
- **With 10 MΩ:**

  | Check | Result |
  |---|---|
  | Absolute error, 99% of readings | 2.0% (1.4% after a one-time check of R5) |
  | Error of a +10% fluid **change**, 99% of readings (this is what the alert engine uses) | **0.13 points** |
  | Chest change error, 99% of readings | 1.7 points on a −9% change |
  | Amplifier output range | 0.49–2.81 V (no clipping) |

- **Jewellery:** a metal toe ring bridging a foot's inject and sense plates makes the reading **58–86% too high**. The alert engine now treats any leg reading more than 25% from last week's normal as "no reading" and asks the patient to place their feet again. It can't cause a false alarm because the jump goes in the healthy direction. Tested in `tests/test_alert_engine.py`.

## 6. Mains hum (`python sim/circuit/hum.py`, about 10 seconds)
- **Setup:** 230 V / 50 Hz mains is coupled into the body (100–300 pF), the floor (100–200 pF) and the sense wires (0.5–5 pF, unequal on the two wires). The two left plates are dry (5 kΩ) and the right ones sweaty (300 Ω), which is the worst case. The device ground either floats on its battery (30 pF to earth) or is tied to mains by a phone charger (4.7 nF).
- **Method:** Python reads the LTspice waveform, samples it like the ESP32 ADC (40 kHz, 12-bit) and takes the 5 kHz Goertzel amplitude, exactly as the firmware will.

  | Scenario | Goertzel error (firmware method) | Peak-to-peak error |
  |---|---|---|
  | No hum | 0.14% | 0.1% |
  | Battery, normal room | 0.17% | 0.7% |
  | Battery, next to wiring, long unshielded wires | 0.16% | 1.6% |
  | Charger plugged in, normal room | 0.13% | 6.8% |
  | Charger plugged in, next to wiring | 0.14% | **17.8%** |

- **Clipping:** none in any case; the amplifier stayed within 1.16–2.14 V.
- **Window length:** windows of 7.5, 20 and 25 ms all stayed within 0.17%.
- **Rules that follow:** the firmware must use the Goertzel amplitude, never peak-to-peak. Measure on battery with the charger unplugged, which is also the safety rule.
- **Not modelled:** a sense plate left completely open (foot lifted). Then the 10 MΩ node floats and hum can saturate it, and the quality check must reject that reading as "no reading". On the bench, test this by lifting one heel.

## 7. Bioimpedance spectroscopy (`python sim/circuit/spectroscopy.py`, about 1 minute)
- **Setup:** the same front end measures the legs at **5, 20 and 50 kHz**. A Cole-model fit gives Rinf/R0, the share of water outside the cells (the "extracellular-water index").

  | Scenario | 5 kHz reading alone | Index |
  |---|---|---|
  | Fluid outside cells +10% (congestion) | −9.1% | **+3.0%** |
  | Foot position / limb / temperature +3% | **+3.0%** (a false signal) | **0.0%** |
  | Fluid inside cells +10% | 0.0% | **−2.9%** (opposite sign) |

- **Accuracy:** LTspice readings are within 0.05% of the exact values. On the ESP32 the fit is an exact closed form (`hm::ewiClosedForm`), and the firmware emulator measures the index within 0.6% of the true body value (worst 0.51% over a simulated month).

## 8. Patient electrical safety (`python sim/circuit/safety.py`, about 2 minutes)
- **Test:** body current with each single fault, measured at 5, 20 and 50 kHz, against IEC 60601-1 limits for type BF parts (DC 10/50 µA; AC 100/500 µA × f in kHz).
- **Faults tested:** current-limit resistor shorted, either coupling capacitor shorted, op-amp output stuck at either rail, DAC at full scale, plus one double fault.
- **Result:** every case passes. The smallest margin is **6.6×** in normal use; it's 12.8× with a single fault. The two series capacitors mean no single fault can drive DC through the patient.
- **Charger leakage (`python sim/circuit/charger_leakage.py`):** mains (325 V peak) couples through the charger's Y-capacitor; the patient stands barefoot on a wet, earthed floor (1 kΩ). Patient leakage limits: 100 µA normal, 500 µA single fault.

  | Case | Leakage through the patient | Verdict |
  |---|---|---|
  | Switch on **USE**, cheap charger plugged in | **0.19 µA** | pass |
  | Switch on **USE**, charger insulation failed | **0.19 µA** | pass |
  | Switch on CHARGE, good charger (1 nF), if someone measured anyway | 72 µA | pass |
  | Switch on CHARGE, cheap charger (4.7 nF) | 339 µA | fail (3.4× over) |
  | Switch on CHARGE, charger insulation failed | 72 mA | fail (dangerous) |

- **So the stool has a CHARGE / USE switch (SW6):** in USE both USB wires are cut; in CHARGE, GPIO39 sees the charger and the firmware refuses to measure (firmware emulator check: no excitation current is ever switched on). Two independent protections, so no single failure exposes the patient. The optional laptop bridge must run on a laptop on battery.

## 9. Self-calibrating reference (`python sim/circuit/selfcal.py`)
- **Design:** the reference is **Rcal, 100 Ω 0.1%**, in series with an ordinary R5 (120 Ω). The spare 74HC4053 switch (GPIO12) reads across Rcal for every reading, and across both for an integrity check: the ratio must be 2.2.
- **Integrity check:** a good board reads 2.200, the R5 tolerance range reads 2.14–2.26, and every fault or build mistake is rejected (wrong R5, short, open, bad joint).
- **Monte Carlo of 100 stools:** absolute error median 0.77% → **0.16%**, 99% of readings 1.96% → **1.32%**, worst 2.56% → **1.65%**.

## What the simulation shows, and what it doesn't
- **It proves:**
  - the circuit design measures the body model accurately: every reading within 0.12%, contact resistance from 300 Ω to 3 kΩ;
  - the excitation current is safe and small (134 µA peak);
  - the signal stays inside the ADC range;
  - the chest value can be recovered from 4 paths.
- **It doesn't prove** real-body accuracy. The body here is a textbook model (Cole segments), and real skin, posture and electrode placement add noise. With our noise model, a single day's chest reading carries ±2.2 Ω of noise on 28 Ω. A +10% chest-fluid change only stands out reliably (3× the noise) after averaging about a week of check-ins. That is why chest is a supporting signal and legs plus weight are the main fluid signals.
- **Next step on real hardware:** build the bench check described in the build guide. Use fixed resistors and capacitors as a "body" (for example 290 Ω in parallel with 650 Ω + 3.3 nF) and compare the ESP32 reading with these simulation numbers.
