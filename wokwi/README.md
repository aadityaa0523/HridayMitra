# HridayMitra in Wokwi: the whole stool, simulated, with a virtual patient you can make sick

`python run.py wokwi` (or `python tools/make_wokwi.py`) rebuilds both projects from the real firmware, compiles the three
custom chips to WebAssembly and compiles both sketches. Everything below is generated, so never edit it by hand.

## What is in the stool project (`wokwi/stool/`)
| Part | What it does in the simulation |
|---|---|
| ESP32 DevKitC running `sketch.ino` | The **production firmware** built with `HM_WOKWI`: no Bluetooth, 1 s = 1 minute, 20 days of history preloaded, beeps instead of voice |
| **Patient digital twin** chip (`hm-body`, 180×230 screen) | A body with its 8 electrodes. While the stool measures, the **current path lights up through the limbs** (legs, arms, right side, left side), the legs and chest **fill with blue** as fluid builds, and live impedances and warnings show underneath. Electrically it's the 8-electrode impedance front end: answers the path select (S0/S1) and body/R5 select with the 5 kHz signal the LTspice-verified circuit makes. Sliders: **leg fluid %**, **chest fluid %**, **foot lifted**, **mains hum** |
| **MAX30102** chip | I2C 0x57, real FIFO with a pulse waveform. Sliders: **pulse**, **SpO₂**, **finger on/off** |
| **Stool monitor** chip (`hm-monitor`, 220×170 screen) | Listens to the stool's serial output and shows the on-chip engine's decision: a big GREEN/AMBER/RED light, the score against the frozen threshold, a **trend graph of the last 24 check-ins**, the reasons in words, the readings, the SMS count and the self-test status |
| **SIM800L + family phone** chip | Answers the AT commands and shows every SMS on a **phone screen**. Sliders: **family reply 1/2/3**, **ASHA reply**, **missed call**, **network outage**, **battery**, **signal** |
| HX711 + 50 kg load cell | One of the stool's four corner cells: **15.5 kg on the slider = 62 kg on the stool** |
| Buttons GO/NO (green), YES (red), SOS (yellow); tablet-drawer switch; 4 LEDs (OK, CHECK AGAIN, ALERT, seat vibration) | As on the real stool |

Screens: `reports/wokwi_live_screens.jpg` (captured live in Wokwi) and `reports/wokwi_chip_screens_preview.png` (rendered on a laptop by `tests/sil/chip_preview.c`).

## Run it in the browser (2 minutes, no install)
1. Open **https://wokwi.com/projects/new/esp32**.
2. Click the ▾ next to the file tabs and choose **Upload file(s)...**. Select every file in `wokwi/stool/` except `wokwi.toml` and the `chips/` folder.
3. Wokwi keeps its own `sketch.ino` and `diagram.json`: open each of those two tabs and paste in the contents of ours.
4. Press ▶. The serial monitor shows `{"t":"ready"}` and a note that 20 days of history are loaded.

## Demo script (what to show judges)
1. Click the load cell and set it to **15.5 kg**. Press **GO**. Hold YES/NO when asked (red = yes, green = no), then set the load cell to **0** ("stand up"). The serial monitor shows the check-in report, and the **OK** LED lights.
2. Click the virtual-patient chip and drag **leg fluid to 12 %** and **chest fluid to 10 %**. Raise the **pulse** to 85 on the finger sensor. Do another 2–3 check-ins answering **YES**. The light goes **CHECK AGAIN**, then **ALERT**, and the **phone screen** shows the SMS with the reasons and the doctor's plan.
3. Wait about 30 seconds (= 30 minutes): family member 2 is messaged. At 2 minutes: the ASHA. Set **ASHA reply = 1** and the doctor is not disturbed. Or set **family reply = 3** to stop the ladder.
4. Robustness: set **foot lifted = 1** (leg reading becomes "no reading"), **hum = 100 mV** (the reading doesn't change: Goertzel), **network outage = 1** during an SOS (the SMS waits and is sent when you set it back to 0), **battery = 3300** (service SMS at the next 07:00 self-test).

## Run it in VS Code (Wokwi extension, free licence)
Open `wokwi/stool/` and press F1 → **Wokwi: Start Simulator**. `wokwi.toml` points at `build/sketch.ino.merged.bin` and the chips in `chips/*.chip.wasm` (both made by `python run.py wokwi`).

## Amulet project (`wokwi/amulet/`)
ESP32-C3 + MPU6050 + SOS button, running the amulet firmware. Move the MPU6050 sliders: tilt it flat (lying) and back (sitting) to count night sit-ups, shake it hard and then lay it flat to trigger a fall SOS. The summary prints on the serial monitor (Wokwi has no Bluetooth, so it isn't sent to the stool).

## What this proves and what it doesn't
- **Proves:** the real firmware runs on an emulated ESP32 with the real pin map and talks to every part correctly. The alert logic, care loop and edge cases also run in the faster laptop emulator (`tests/test_firmware_sil.py`, 26/26 checks).
- **Doesn't prove:** analog behaviour of real parts. The virtual-patient chip uses the LTspice results; the bench test with real resistors and electrodes is still needed.
