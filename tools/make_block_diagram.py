"""BLOCK DIAGRAM generated from code, so it can be regenerated when a pin or part changes.
Names, pins and parts come from the build guide v3 (sections 4, 5, 8, 9); the amulet link and the care-loop
timers come from the product brief / final design and sim/careloop/careloop.py.
Run:  python tools/make_block_diagram.py
Outputs: docs/block_diagram.svg, docs/block_diagram.png (PNG is a headless-Chrome screenshot of the SVG)
"""
import html, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
W, H = 1320, 990
FILL = {"stool": "#e3f1f1", "esp": "#e4ebf7", "out": "#e6f3e6", "amulet": "#efe6f6", "power": "#fbeedd", "care": "#fbe6e6"}
els = []


def esc(s):
    return html.escape(s, quote=False)


def box(x, y, w, h, lines, kind, dashed=False, note=False):
    fill, stroke = ("#fff8e6", "#b7791f") if note else (FILL[kind], "#5b6a6f")
    dash = ' stroke-dasharray="6 4"' if dashed or note else ""
    els.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.4"{dash}/>')
    top = y + h / 2 - (len(lines) - 1) * 8.5 + 4.5
    for i, s in enumerate(lines):
        first = i == 0 and not note
        els.append(f'<text x="{x + w / 2}" y="{top + i * 17}" text-anchor="middle" font-size="{13 if first else 12}" '
                   f'font-weight="{700 if first else 400}" fill="{"#7a4a00" if note else "#1b2427"}">{esc(s)}</text>')


def arrow(pts, dashed=False, label=None, lx=0, ly=0):
    d = " ".join(f"{px},{py}" for px, py in pts)
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    els.append(f'<polyline points="{d}" fill="none" stroke="#33454a" stroke-width="1.6"{dash} marker-end="url(#a)"/>')
    if label:
        els.append(f'<text x="{lx}" y="{ly}" font-size="12" fill="#33454a">{esc(label)}</text>')


def text(x, y, s, size=12, weight=400, fill="#33454a", extra=""):
    els.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" {extra}>{esc(s)}</text>')


text(20, 34, "HridayMitra home unit: block diagram", 22, 700, "#1b2427")
text(20, 56, "Check-in stool + Kavach amulet + SMS care loop. Solid arrows = signal or data flow; dashed yellow boxes = what happens when something fails.", 13, 400, "#5b6a6f")
for x, s in ((20, "SENSORS ON THE STOOL"), (470, "ESP32 WROOM-32 (STATION BRAIN)"), (900, "OUTPUTS AND POWER")):
    text(x, 84, s, 14, 700, "#0d6b6e", 'letter-spacing="1"')

# --- column 1: sensors
box(20, 96, 400, 56, ["4 load cells, wired as one full bridge", "HX711: data GPIO32, clock GPIO14"], "stool")
box(20, 168, 270, 50, ["8 electrodes", "4 foot plates + 4 hand strips"], "stool")
box(20, 234, 270, 62, ["2 x 74HC4052 path mux", "legs, arms, right side, left side", "S0 GPIO33, S1 GPIO27"], "stool")
box(20, 312, 270, 50, ["74HC4053 body / R5 selector", "select on GPIO18"], "stool")
box(20, 378, 270, 50, ["INA126 instrumentation amp", "single 3.3 V, gain about 10"], "stool")
box(310, 234, 110, 128, ["Excitation", "ESP32 DAC", "GPIO25, 5 kHz", "MCP6002 buffer", "current path", "(R5 220 ohm)"], "stool")
box(20, 444, 400, 50, ["MAX30102 finger pulse and SpO2", "I2C on GPIO21, GPIO22"], "stool")
box(20, 510, 400, 50, ["2 answer buttons + SOS button", "GPIO4, GPIO5, GPIO15"], "stool")
box(20, 576, 400, 62, ["AD8232 ECG (optional)", "only on amber days; off for pacemaker / ICD", "GPIO34, GPIO39, GPIO36"], "stool", dashed=True)
box(20, 654, 400, 48, ["Bad contact or toe ring: 'no reading',", "the voice asks to place the feet again"], "stool", note=True)
box(20, 714, 400, 48, ["Guest on the stool: readings are ignored", "(weight and impedance do not fit the patient)"], "stool", note=True)
arrow([(155, 218), (155, 234)]); arrow([(155, 296), (155, 312)]); arrow([(155, 362), (155, 378)])
arrow([(310, 265), (290, 265)])
arrow([(290, 403), (470, 403)], label="ADC GPIO35", lx=335, ly=397)
arrow([(470, 330), (420, 330)])
arrow([(420, 124), (470, 124)]); arrow([(420, 469), (470, 469)]); arrow([(420, 535), (470, 535)])
arrow([(420, 607), (470, 607)], dashed=True)

# --- column 2: ESP32
els.append('<rect x="470" y="96" width="380" height="504" rx="10" fill="#f4f7fc" stroke="#3b5ea8" stroke-width="2"/>')
box(490, 116, 340, 78, ["Signal processing", "Goertzel at 5 kHz (never peak-to-peak)", "quality checks: steady load, contact,", "pulse quality; 'no reading' if bad"], "esp")
box(490, 208, 340, 78, ["Personal baseline + alert engine", "runs offline on the ESP32", "green / amber / red, with a spoken reason"], "esp")
box(490, 300, 340, 56, ["Voice prompts from flash", "8-bit clips played on DAC2 (GPIO26)"], "esp")
box(490, 370, 340, 70, ["Message queue + modem control", "messages wait in memory when power", "or network fails, then are sent"], "esp")
box(490, 520, 340, 60, ["Amulet data in", "7 days of data, handed over when in range"], "esp")

# --- column 3: power and outputs
box(900, 100, 400, 70, ["Power", "18650 (protected) + TP4056 charger + MT3608 boost", "battery-only while measuring, charger unplugged"], "power")
box(900, 178, 400, 36, ["Power cut: runs on the battery, messages queue"], "power", note=True)
box(900, 222, 400, 50, ["3 LEDs: green, amber, red", "GPIO13, GPIO23, GPIO2"], "out")
box(900, 297, 400, 62, ["Voice out", "DAC2 > PAM8403 amp > 4 ohm 3 W speaker"], "out")
box(900, 372, 400, 66, ["SIM800L, 2G SMS (Airtel, Vi, BSNL; not Jio)", "UART2: GPIO17, GPIO16"], "out")
box(900, 448, 330, 36, ["No network: SIM800L retries every 10 min"], "out", note=True)
arrow([(900, 135), (850, 135)])
arrow([(850, 247), (900, 247)]); arrow([(850, 328), (900, 328)]); arrow([(850, 405), (900, 405)])

# --- amulet
box(470, 640, 380, 128, ["Kavach amulet (worn day and night)", "ESP32-C3 + motion sensor (demo: S3 Sense + MPU6050)",
                         "night breathing, sit-ups, steps, falls, SOS button", "stores 7 days; charges in the stool's side dock",
                         "Bluetooth Low Energy to the stool (built into both ESP32s)"], "amulet")
arrow([(660, 640), (660, 580)], dashed=True)
text(672, 616, "BLE sync when in range; 7-day buffer if out of range", 12)

# --- care loop
arrow([(1270, 438), (1270, 798), (140, 798), (140, 828)])
text(150, 792, "SMS alert from the SIM800L", 12)
text(170, 818, "CARE LOOP (SMS over 2G)", 14, 700, "#0d6b6e", 'letter-spacing="1"')
steps = [("Family member 1", "SMS at once"), ("Family member 2", "no reply after 30 min"),
         ("ASHA worker", "after 2 h, unless family replies 3 (fine)"), ("PHC doctor", "after 6 h if nobody has examined the patient")]
for i, (a, b) in enumerate(steps):
    x = 20 + i * 330
    box(x, 828, 270, 56, [a, b], "care")
    if i:
        arrow([(x - 60, 856), (x, 856)])
text(20, 912, "Replies to the stool: 1 = I am checking, 2 = need help (goes straight to the ASHA), 3 = patient is fine; "
              "a missed call counts as 1. Timers as simulated in sim/careloop (92% reviewed before the hospital visit).", 12.5, 400, "#1b2427")
text(20, 972, "Monitoring, not diagnosis.", 15, 700, "#1b2427")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">'
       '<defs><marker id="a" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#33454a"/></marker></defs>'
       f'<rect width="{W}" height="{H}" fill="#fbfcfc"/>' + "".join(els) + "</svg>")
out = ROOT / "docs"
(out / "block_diagram.svg").write_text(svg, encoding="utf-8")
subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                f"--window-size={W},{H}", f"--screenshot={out / 'block_diagram.png'}", (out / "block_diagram.svg").as_uri()],
               check=True, capture_output=True)
print("wrote docs/block_diagram.svg and docs/block_diagram.png")
