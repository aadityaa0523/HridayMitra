"""Makes docs/HridayMitra wiring guide.pdf  (no load cell / HX711 yet). Run: python tools/make_wiring_guide.py"""
import pathlib, subprocess, shutil, html
ROOT = pathlib.Path(__file__).resolve().parents[1]
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def overview():
    W, H = 700, 400
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="10.5">']
    s.append('<rect x="265" y="30" width="170" height="340" rx="8" fill="#e6f1f1" stroke="#0d6b6e"/>')
    s.append('<text x="350" y="52" text-anchor="middle" font-weight="bold" font-size="13">ESP32 WROOM-32</text>')
    s.append('<text x="350" y="68" text-anchor="middle" fill="#5b6a6f">3.3 V logic, one shared GND</text>')

    def box(x, y, w, title, lines, side):
        h = 22 + 14 * len(lines)
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#fff6dc" stroke="#8a5300"/>')
        s.append(f'<text x="{x+8}" y="{y+15}" font-weight="bold">{html.escape(title)}</text>')
        for i, t in enumerate(lines):
            s.append(f'<text x="{x+8}" y="{y+30+i*14}">{html.escape(t)}</text>')
        ex = x + w if side == "L" else x
        tx = 265 if side == "L" else 435
        s.append(f'<line x1="{ex}" y1="{y+h/2}" x2="{tx}" y2="{y+h/2}" stroke="#0d6b6e" stroke-width="2"/>')
    box(15, 20, 235, "LEDs + buttons", ["GPIO13, 23, 2 > 220R > LED > GND", "GPIO4, 5, 15 > button > GND", "(green, red, SOS)"], "L")
    box(15, 120, 235, "MAX30102 pulse sensor", ["GPIO21 = SDA, GPIO22 = SCL", "3V3, GND"], "L")
    box(15, 200, 235, "AD8232 ECG (optional)", ["OUT > GPIO34, LO+ > 39 (LO- unused)", "3V3, GND (not with impedance on)"], "L")
    box(15, 280, 235, "Amulet (separate board)", ["S3 Sense + MPU6050 + LiPo", "talks to the laptop over Bluetooth"], "L")
    box(450, 20, 235, "Impedance board (Z1)", ["GPIO25 DAC > excitation", "GPIO35 < amplifier output", "GPIO18 > selector (74HC4053)", "GPIO33, 27 > 74HC4052 (later)"], "R")
    box(450, 140, 235, "SIM800L (SMS)", ["GPIO17 > 1k > RX (2.2k to GND)", "GPIO16 < TX", "power: battery rail + 1000 uF"], "R")
    box(450, 235, 235, "Voice: PAM8403 + speaker", ["GPIO26 > 1 uF > 10k pot > input", "PAM8403 on 5 V"], "R")
    box(450, 310, 235, "Reserved for later", ["HX711 (load cells): GPIO32 data,", "GPIO14 clock"], "R")
    s.append("</svg>")
    return "".join(s)


def table(head, rows):
    h = "".join(f"<th>{c}</th>" for c in head)
    r = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f"<table><tr>{h}</tr>{r}</table>"


CSS = """@page{size:A4;margin:13mm 12mm}body{font-family:'Segoe UI',Arial,sans-serif;font-size:9.3pt;line-height:1.4;color:#1b2427}
h1{font-size:20pt;color:#0d4f52;margin:0 0 4px}h2{font-size:12.5pt;color:#0d4f52;border-bottom:1.5px solid #0d6b6e;padding-bottom:3px;margin:15px 0 6px;break-after:avoid}
h3{font-size:10pt;margin:9px 0 3px;break-after:avoid}table{border-collapse:collapse;width:100%;margin:4px 0 8px;font-size:8.3pt}
th,td{border:1px solid #cfd8da;padding:3px 5px;vertical-align:top;text-align:left}th{background:#e6f1f1}tr{break-inside:avoid}
.box{background:#fff6dc;border-radius:6px;padding:6px 9px;margin:7px 0}.pb{break-before:page}p,li{margin:2px 0}ul,ol{margin:3px 0 3px 18px;padding:0}code{font-family:Consolas,monospace;font-size:8.3pt}"""

BODY = f"""
<h1>HridayMitra: wiring guide (no load cell yet)</h1>
<p><b>Monitoring only, not a diagnosis tool.</b> Pin numbers are the ESP32 DevKit GPIO numbers. Pin numbers on the ICs follow the standard layouts: <b>check each datasheet before you power up.</b></p>
<div class="box"><b>Golden rules.</b> 1) All logic is 3.3 V and all grounds join at one point. 2) Wire one block, run its test, then the next. 3) Put a 100 nF capacitor across the power pins of every IC, close to the chip. 4) Power off before you change wires. 5) Never connect the impedance board to a person until the resistor phantom test passes, and never to anyone with a pacemaker or defibrillator. 6) When a person touches the electrodes, run from battery or USB from a laptop on battery, not a mains charger. 7) Wire colours: red = 3.3 V, black = GND, yellow/white = signals, orange = 5 V, blue = battery.</div>
<h2>1. Overview</h2>{overview()}
<h2>2. Power</h2>
<ul><li><b>For now: USB.</b> Plug the ESP32 into the laptop. Its 3V3 pin powers the MAX30102, impedance board, AD8232 and LEDs. This is the safest way to start.</li>
<li><b>Battery version (later):</b> 18650 cell &rarr; TP4056 (B+ and B-) &rarr; the TP4056 OUT+ / OUT- is the <b>battery rail</b> (3.7-4.2 V). Boost module input from the battery rail, output set to 5 V &rarr; ESP32 VIN and PAM8403. SIM800L takes the battery rail directly (not 3V3, not 5 V) with a 1000 &micro;F capacitor across its power pins.</li></ul>
{table(["Rail", "Where it comes from", "What it powers"], [
 ["3.3 V", "ESP32 3V3 pin", "MAX30102, AD8232, MCP6002/6022, INA126, 74HC4053/4052, LED and button logic"],
 ["5 V", "USB (VIN pin) or boost module", "PAM8403 amplifier"],
 ["Battery rail 3.7-4.2 V", "TP4056 OUT", "SIM800L only (needs up to 2 A bursts)"],
 ["GND", "All grounds joined at the ESP32 GND", "Everything"]])}
<h2 class="pb">3. Pin map</h2>
{table(["ESP32 pin", "Goes to", "Notes"], [
 ["GPIO13, 23, 2", "LED green, amber, red", "each through 220 &#937; to GND"],
 ["GPIO4, 5, 15", "Buttons green, red, SOS", "other leg of each button to GND; internal pull-ups"],
 ["GPIO21 (SDA), GPIO22 (SCL)", "MAX30102", "3.3 V, GND"],
 ["GPIO25 (DAC1)", "Impedance excitation", "5 kHz sine"],
 ["GPIO35 (ADC1)", "Impedance amplifier output", "input only"],
 ["GPIO18", "74HC4053 select (A and B tied)", "low = body, high = reference (across Rcal when GPIO12 is high)"],
 ["GPIO33, GPIO27", "74HC4052 path select S0, S1", "only for the trunk paths, later"],
 ["GPIO26 (DAC2)", "Voice to PAM8403", "through 1 &micro;F and 10 k&#937; pot"],
 ["GPIO17 (TX2), GPIO16 (RX2)", "SIM800L", "TX through a divider (see section 8)"],
 ["GPIO34, 39", "AD8232 OUT, LO+", "inputs only; optional"],
 ["GPIO19", "Seat vibration motor", "1 k to 2N2222 base; motor 5 V to collector; 1N4148 across motor"],
 ["GPIO36", "Tablet-drawer microswitch", "switch to GND; 10 k pull-up to 3V3 (no internal pull-up)"],
 ["GPIO12", "Self-calibration select (74HC4053 S3)", "boot pin: only this high-impedance input, no pull-up"],
 ["GPIO32, GPIO14", "Reserved: HX711 data, clock", "when the load cells arrive"],
 ["GPIO0, GPIO12", "<b>Leave empty</b>", "boot pins"]])}
<h2>4. Block 1: LEDs and buttons (test first)</h2>
{table(["From", "To"], [["GPIO13 &rarr; 220 &#937; &rarr; green LED long leg", "LED short leg &rarr; GND"], ["GPIO23 &rarr; 220 &#937; &rarr; amber LED", "short leg &rarr; GND"], ["GPIO2 &rarr; 220 &#937; &rarr; red LED", "short leg &rarr; GND"],
 ["GPIO4, GPIO5, GPIO15", "each to one leg of a button; the other leg to GND"]])}
<p><b>Test:</b> a sketch that blinks each LED and prints the button on the Serial Monitor. Pass: each LED lights, each press prints.</p>
<h2>5. Block 2: MAX30102 pulse sensor</h2>
{table(["Module pin", "Connect to"], [["VIN", "3V3 (if your module says 3.3-5 V; some need 5 V: read the board)"], ["GND", "GND"], ["SDA", "GPIO21"], ["SCL", "GPIO22"], ["INT", "not used"]])}
<p><b>Test:</b> an I2C scanner shows address <code>0x57</code>; then a MAX30102 example prints a heart rate when you rest a finger on it. Pass: it matches your wrist pulse.</p>
<h2 class="pb">6. Block 3: the impedance board (legs path Z1)</h2>
<p>Build on the breadboard from <b>left to right</b>: Vref and op-amp, selector, amplifier. Keep the DAC wire (GPIO25) away from the ADC wire (GPIO35). Parts: U1 = MCP6002 (or MCP6022), U2 = INA126, U3 = 74HC4053. Standard dual op-amp pins: 1 OUTA, 2 INA-, 3 INA+, 4 V-, 5 INB+, 6 INB-, 7 OUTB, 8 V+. INA126 DIP-8: 1 RG, 2 -IN, 3 +IN, 4 V-, 5 REF, 6 OUT, 7 V+, 8 RG (verify).</p>
{table(["Net", "Connect"], [
 ["Power", "U1 pin 8, U2 pin 7, U3 VCC &rarr; 3V3. U1 pin 4, U2 pin 4, U3 GND, VEE, INH and select C &rarr; GND. 100 nF across each IC's power pins; 10 &micro;F across the 3V3 rail."],
 ["VREF (1.65 V)", "3V3 &rarr; R1 10 k&#937; &rarr; node VREFIN &rarr; R2 10 k&#937; &rarr; GND. C1 10 &micro;F from VREFIN to GND. VREFIN &rarr; U1 pin 3. U1 pin 1 tied to U1 pin 2. U1 pin 1 is <b>VREF</b>."],
 ["Excitation", "GPIO25 &rarr; C2 1 &micro;F &rarr; node EXC_IN. R3 100 k&#937; from EXC_IN to VREF. EXC_IN &rarr; U1 pin 5. U1 pin 7 tied to U1 pin 6. U1 pin 7 is <b>EXC_OUT</b>."],
 ["Current path", "EXC_OUT &rarr; C3 1 &micro;F &rarr; R4 4.7 k&#937; &rarr; <b>FORE_L</b> (left forefoot plate). <b>FORE_R</b> (right forefoot plate) &rarr; C4 1 &micro;F &rarr; node <b>RET</b> &rarr; R5 120 &#937; &rarr; node <b>NCAL</b> &rarr; <b>Rcal 100 &#937; 0.1%</b> &rarr; VREF. 74HC4053 switch C: C0 = RET, C1 = NCAL, common <b>RTAP</b> &rarr; switch A input A1; select S3 = GPIO12 (self-calibration)."],
 ["Sensing", "<b>HEEL_L</b> &rarr; R6 1 k&#937; &rarr; node SA. <b>HEEL_R</b> &rarr; R7 1 k&#937; &rarr; node SB. R8 10 M&#937; from SA to VREF. R9 10 M&#937; from SB to VREF (10 M, not 1 M: see Monte Carlo)."],
 ["Selector U3 (74HC4053)", "Select pins A and B tied together &rarr; GPIO18. X0 = SA, X1 = RET, X common &rarr; INA126 pin 3 (+IN). Y0 = SB, Y1 = VREF, Y common &rarr; INA126 pin 2 (-IN). (Use your datasheet's names for these pins.)"],
 ["Amplifier U2 (INA126)", "RG 16 k&#937; (15 k&#937; + 1 k&#937;) between pins 1 and 8. REF pin 5 &rarr; VREF. OUT pin 6 &rarr; R11 1.5 k&#937; &rarr; node ADC &rarr; <b>GPIO35</b>. C5 10 nF from ADC node to GND."]])}
<h3>Test 6a: voltages with a multimeter (no plates connected)</h3>
<ul><li>VREF reads about <b>1.65 V</b>. EXC_IN and EXC_OUT also about 1.65 V (DC).</li><li>Short INA pin 2 and pin 3 together: OUT (pin 6) reads about 1.65 V.</li></ul>
<h3>Test 6b: the resistor phantom (instead of legs)</h3>
<p>No plates yet? Use a resistor: put <b>330 &#937;</b> between FORE_L and FORE_R. Wire HEEL_L to the FORE_L end and HEEL_R to the FORE_R end. Run the measurement: Z should read about 330 &#937;. Repeat with 680 &#937; and 1 k&#937; (within about 5%). Then add 1-5 k&#937; in series with each outer lead: Z should barely move.</p>
<h2>7. Block 4 (optional): AD8232 ECG</h2>
{table(["Module pin", "Connect to"], [["3.3V", "3V3"], ["GND", "GND"], ["OUTPUT", "GPIO34"], ["LO+", "GPIO39"], ["SDN", "leave open"]])}
<p>Electrode leads: RA (red) right side, LA (yellow) left side, RL (green) reference. <b>Do not connect the ECG leads and the impedance board to the same electrodes at once.</b> Test: plot GPIO34 on the Serial Plotter; you should see heartbeats.</p>
<h2 class="pb">8. Block 5: SIM800L (SMS)</h2>
{table(["Module pin", "Connect to"], [["VCC", "Battery rail (3.7-4.2 V) with 1000 &micro;F across VCC-GND. Not 3V3."], ["GND", "GND (common)"], ["TX", "GPIO16"], ["RX", "GPIO17 &rarr; 1 k&#937; &rarr; RX, and RX &rarr; 2.2 k&#937; &rarr; GND (a divider, about 2.3 V)"], ["Antenna", "Screw on the antenna; SIM card in (Airtel, Vi or BSNL)"]])}
<p><b>Test:</b> send <code>AT</code> at 9600 baud: it answers <code>OK</code>. <code>AT+CSQ</code> shows signal; then send one SMS to your own phone. If it resets while sending, the supply is too weak: add the capacitor, shorten wires, use a better 18650.</p>
<h2>9. Block 6: voice (PAM8403 and speaker)</h2>
{table(["From", "To"], [["GPIO26", "1 &micro;F capacitor &rarr; 10 k&#937; potentiometer top"], ["Pot bottom", "GND"], ["Pot wiper", "PAM8403 L input (R input to GND)"], ["PAM8403 5 V, GND", "5 V rail, GND"], ["PAM8403 L output + and -", "Speaker (4 &#937; 3 W)"]])}
<p><b>Test:</b> play one short clip from flash. Pass: clear and loud with the pot about half. If it hums, shorten the input wire and keep it away from the SIM800L.</p>
<h2>10. Block 7: amulet (separate board)</h2>
<p>Example for a Seeed XIAO ESP32S3 Sense (check your board's pin names): MPU6050 VCC &rarr; 3V3, GND &rarr; GND, SDA &rarr; D4 (GPIO5), SCL &rarr; D5 (GPIO6), AD0 &rarr; GND (address 0x68). SOS button between D1 and GND. LiPo battery to the BAT+ and BAT- pads on the underside (<b>check polarity</b>). <b>Test:</b> an I2C scan finds 0x68; the tilt angle changes when you tilt the board against a protractor.</p>
<h2>11. Order and quick checklist</h2>
{table(["#", "Block", "Pass when"], [["1", "ESP32 and USB", "Serial Monitor prints"], ["2", "LEDs and buttons", "Each LED and button works"], ["3", "MAX30102", "0x57 found; pulse matches wrist"], ["4", "Impedance: voltages (6a)", "VREF 1.65 V; INA shorted = 1.65 V"], ["5", "Impedance: phantom (6b)", "330, 680, 1 k&#937; within about 5%"], ["6", "SIM800L", "AT = OK; SMS arrives"], ["7", "Voice", "Clear and loud"], ["8", "Amulet", "0x68 found; tilt works"], ["9", "ECG (optional)", "Heartbeats visible"]])}
<h2>12. If something misbehaves</h2>
{table(["Symptom", "Check"], [["ESP32 won't boot or upload", "Anything wired to GPIO0 or GPIO12; unplug the board from the breadboard to flash"], ["I2C scan finds nothing", "SDA and SCL swapped; module powered; pull-ups"], ["Impedance stuck at one value", "Selector pins A and B tied to GPIO18; INA REF at VREF; no short to GND"], ["Impedance jumps around", "Loose breadboard contact; long wires near the DAC; no 100 nF decoupling"], ["Reads depend on contact", "R8 and R9 10 M&#937; missing or 1 M fitted by mistake; the 1 k&#937; protection resistors missing"], ["SIM800L resets", "Weak supply; add the 1000 &micro;F capacitor"], ["Hum in the speaker", "Shared ground wiring; shield the input; separate it from the SIM800L"]])}
<p><b>Not verified:</b> IC pin numbers (check the datasheets), the pin map on your exact board, and all values (starting values from the simulation).</p>
"""

html_doc = f"<!doctype html><html><head><meta charset='utf-8'><title>HridayMitra wiring guide</title><style>{CSS}</style></head><body>{BODY}</body></html>"
tmp = pathlib.Path(r"C:\Users\Aadityaa\AppData\Local\Temp\hmpdf"); tmp.mkdir(exist_ok=True)
(tmp / "wiring.html").write_text(html_doc, encoding="utf-8")
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", rf"--user-data-dir={tmp}\prof6",
                rf"--print-to-pdf={tmp}\wiring.pdf", (tmp / "wiring.html").as_uri()], check=True, capture_output=True, timeout=180)
shutil.copy(tmp / "wiring.pdf", ROOT / "docs" / "HridayMitra wiring guide.pdf")
print("wrote docs/HridayMitra wiring guide.pdf")
