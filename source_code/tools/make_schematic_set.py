"""SCHEMATIC SET (HM-HW-002): production-style multi-sheet schematics with border zones and title blocks.
  1 index + conventions   2 analog front end (custom part)   3 ESP32 + peripherals   4 power + CHARGE/USE isolation
Net flags (global labels) join sheets, as in KiCad. Same parts, values and pins as tools/make_schematic.py (KiCad,
ERC 0, netlist path check) and the firmware pin map.   Run:  python tools/make_schematic_set.py
Out:  docs/hardware/HM-HW-002_schematics.pdf (4 pages) + one PNG per sheet
"""
import pathlib, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
import schemdraw
import schemdraw.elements as elm

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "hardware"
sys.path.insert(0, str(ROOT / "tools"))
INK = "#1b1f24"
NETC = {"+3V3": "#0969da", "+5V": "#e16f24", "VBAT": "#d1242f", "VREF": "#8250df", "GND": "#57606a"}
SHEETS = ["Index and conventions", "Analog front end (custom part)", "ESP32 and peripherals", "Power and CHARGE / USE isolation"]


def frame(fig, n, title):
    """A3 border with zone letters / numbers and the title block."""
    fig.patches.append(Rectangle((0.01, 0.01), 0.98, 0.98, transform=fig.transFigure, fill=False, ec=INK, lw=2))
    fig.patches.append(Rectangle((0.025, 0.025), 0.95, 0.95, transform=fig.transFigure, fill=False, ec=INK, lw=0.8))
    for i in range(8):
        fig.text(0.025 + 0.95 * (i + 0.5) / 8, 0.0155, str(i + 1), ha="center", va="center", fontsize=8)
        fig.text(0.025 + 0.95 * (i + 0.5) / 8, 0.9825, str(i + 1), ha="center", va="center", fontsize=8)
    for j, c in enumerate("DCBA"):
        fig.text(0.0175, 0.025 + 0.95 * (j + 0.5) / 4, c, ha="center", va="center", fontsize=8)
        fig.text(0.9825, 0.025 + 0.95 * (j + 0.5) / 4, c, ha="center", va="center", fontsize=8)
    x, y, w, h = 0.70, 0.025, 0.275, 0.095
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure, fc="white", ec=INK, lw=1.2))
    for yy in (y + 0.03, y + 0.06):
        fig.lines.append(plt.Line2D([x, x + w], [yy, yy], transform=fig.transFigure, color=INK, lw=0.6))
    fig.text(x + 0.006, y + 0.085, f"HridayMitra stool: {title}", fontsize=11, weight="bold", va="top")
    fig.text(x + 0.006, y + 0.054, "Doc HM-HW-002   Rev A   2026-10-25   Size A3", fontsize=8.5, va="top", family="monospace")
    fig.text(x + 0.006, y + 0.024, f"Sheet {n} / {len(SHEETS)}   Checked: KiCad ERC 0 · LTspice · firmware emulator", fontsize=8.5, va="top", family="monospace")


def flag(ax, xy, name, right=True):
    """Net flag (global label) at the end of a wire."""
    c = NETC.get(name, INK)
    ax.text(xy[0] + (0.08 if right else -0.08), xy[1], name, ha="left" if right else "right", va="center", fontsize=8.5, color=c,
            family="monospace", weight="bold", bbox=dict(boxstyle=("rarrow" if right else "larrow") + ",pad=0.25", fc="white", ec=c, lw=1))


def W(d, *pts):
    for a, b in zip(pts, pts[1:]):
        d += elm.Line().at(a).to(b)


def gnd(d, xy):
    d += elm.Ground().at(xy)


# ------------------------------------------------------------------ sheet 1
def sheet_index(fig):
    ax = fig.add_axes([0.04, 0.14, 0.92, 0.8]); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.text(0, 9.7, "Schematic set HM-HW-002: contents", fontsize=20, weight="bold", va="top")
    for i, s in enumerate(SHEETS):
        ax.text(0.2, 8.9 - 0.45 * i, f"Sheet {i + 1}   {s}", fontsize=13, va="top", family="monospace")
    ax.text(0, 6.7, "Conventions", fontsize=15, weight="bold", va="top")
    conv = ["Signals flow left to right. Net flags (arrow boxes) are global labels: the same name on any sheet is one net.",
            "Power nets: +3V3 (blue), +5V (orange), VBAT 3.0-4.2 V (red), VREF 1.65 V (violet), GND (grey).",
            "Values match the KiCad project hardware/kicad/ (ERC 0, netlist path check) and the LTspice netlists in sim/circuit/.",
            "Patient side = applied part, IEC 60601-1 type BF. Battery only while a person touches the electrodes (SW6 on USE).",
            "Never on anyone with a pacemaker or ICD (weight-only mode). Monitoring, not diagnosis.",
            "Related documents: HM-HW-001 block diagram · HM-HW-003 power budget · HM-HW-004 PCB · HM-HW-005 BOM · HM-HW-006 verification."]
    for i, c in enumerate(conv):
        ax.text(0.2, 6.1 - 0.45 * i, "• " + c, fontsize=11.5, va="top")
    ax.text(0, 2.9, "Revision history", fontsize=15, weight="bold", va="top")
    for i, r in enumerate(["A   2026-10-25   first release: 8-electrode AFE, 3-frequency spectroscopy, Rcal self-calibration, CHARGE/USE isolation"]):
        ax.text(0.2, 2.3 - 0.45 * i, r, fontsize=11.5, va="top", family="monospace")


# ------------------------------------------------------------------ sheet 2
def sheet_afe(fig):
    import make_frontend_sheet as F
    ax = fig.add_axes([0.03, 0.13, 0.94, 0.83]); ax.axis("off")
    F.schematic(ax)
    for name, xy in (("DAC_EXC  ← ESP32 GPIO25 (sheet 3)", (0.03, 0.93)), ("Z_ADC  → ESP32 GPIO35 (sheet 3)", (0.03, 0.905)),
                     ("PATH_S0, PATH_S1, SEL, CAL_SEL  ← ESP32 (sheet 3)", (0.03, 0.88))):
        fig.text(*xy, name, fontsize=9.5, family="monospace", color=INK, weight="bold")


# ------------------------------------------------------------------ sheet 3
def sheet_mcu(fig):
    ax = fig.add_axes([0.03, 0.13, 0.94, 0.83]); ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False); d.config(fontsize=9, unit=1.6)
    left = [("GPIO25", "DAC_EXC"), ("GPIO35", "Z_ADC"), ("GPIO33", "PATH_S0"), ("GPIO27", "PATH_S1"), ("GPIO18", "SEL"), ("GPIO12", "CAL_SEL"),
            ("GPIO21", "SDA"), ("GPIO22", "SCL"), ("GPIO32", "HX_DT"), ("GPIO14", "HX_SCK"), ("GPIO39", "CHG_SENSE"), ("GPIO34", "ECG_OUT")]
    right = [("GPIO13", "LED_G"), ("GPIO23", "LED_A"), ("GPIO2", "LED_R"), ("GPIO4", "BTN_G"), ("GPIO5", "BTN_R"), ("GPIO15", "BTN_SOS"),
             ("GPIO36", "DRAWER"), ("GPIO19", "VIBRA"), ("GPIO26", "VOICE_DAC"), ("GPIO17", "GSM_TX"), ("GPIO16", "GSM_RX")]
    pins = [elm.IcPin(name=g, side="left", anchorname="L" + n) for g, n in left] + \
           [elm.IcPin(name=g, side="right", anchorname="R" + n) for g, n in right] + \
           [elm.IcPin(name="3V3", side="top", anchorname="V"), elm.IcPin(name="GND", side="bottom", anchorname="G")]
    u6 = d.add(elm.Ic(pins=pins, pinspacing=0.75, edgepadW=5.4, edgepadH=0.6, leadlen=0.6,
                      label="U6\nESP32-WROOM-32\n(DevKitC V4)\n\n240 MHz ×2\n4 MB flash · BLE 4.2", lblsize=10).right().at((14, 9)))
    A = u6.absanchors
    for g, n in left:
        p = A["L" + n]; W(d, p, (p[0] - 1.0, p[1])); flag(ax, (p[0] - 1.0, p[1]), n, right=False)
    for g, n in right:
        p = A["R" + n]; W(d, p, (p[0] + 1.0, p[1])); flag(ax, (p[0] + 1.0, p[1]), n)
    W(d, A["V"], (A["V"][0], A["V"][1] + 0.6)); flag(ax, (A["V"][0], A["V"][1] + 0.6), "+3V3")
    gnd(d, A["G"])
    d += elm.Label().at((A["G"][0], A["G"][1] - 1.5)).label("On the DevKit: EN pull-up R19 10k · CP2102 USB-UART (laptop / app) · AMS1117 (sheet 4)", fontsize=8)
    # ---- left column: MAX30102, HX711, AFE link note, audio, GSM ----
    X0 = 0.5
    j2 = d.add(elm.Ic(pins=[elm.IcPin(name=n, side="right", anchorname=n) for n in ("VIN", "GND", "SCL", "SDA")], pinspacing=0.7,
                      edgepadW=1.4, leadlen=0.5, label="J2\nMAX30102\nfinger", lblsize=9).right().at((X0, 15.0)))
    for n, net in (("VIN", "+3V3"), ("SCL", "SCL"), ("SDA", "SDA")):
        p = j2.absanchors[n]; W(d, p, (p[0] + 0.6, p[1])); flag(ax, (p[0] + 0.6, p[1]), net)
    W(d, j2.absanchors["GND"], (j2.absanchors["GND"][0] + 0.3, j2.absanchors["GND"][1])); gnd(d, (j2.absanchors["GND"][0] + 0.3, j2.absanchors["GND"][1]))
    j3 = d.add(elm.Ic(pins=[elm.IcPin(name=n, side="right", anchorname=n) for n in ("VCC", "GND", "DT", "SCK")], pinspacing=0.7,
                      edgepadW=1.4, leadlen=0.5, label="J3\nHX711\nmodule", lblsize=9).right().at((X0, 11.0)))
    for n, net in (("VCC", "+3V3"), ("DT", "HX_DT"), ("SCK", "HX_SCK")):
        p = j3.absanchors[n]; W(d, p, (p[0] + 0.6, p[1])); flag(ax, (p[0] + 0.6, p[1]), net)
    W(d, j3.absanchors["GND"], (j3.absanchors["GND"][0] + 0.3, j3.absanchors["GND"][1])); gnd(d, (j3.absanchors["GND"][0] + 0.3, j3.absanchors["GND"][1]))
    d += elm.Label().at((X0, 9.2)).label("J4/J5: HX711 E+ E− A− A+ ← 4 × 50 kg half-bridge\nload cells, wired as one full bridge", fontsize=8, halign="left")
    d += elm.Label().at((X0, 7.6)).label("To sheet 2 (AFE): DAC_EXC, Z_ADC, PATH_S0, PATH_S1, SEL,\nCAL_SEL. GPIO12 is a boot strap pin: only the 74HC4053\nselect input on it, no pull-up. ECG_OUT: optional AD8232,\nnot fitted.",
                                         fontsize=8, halign="left", color="#57606a")
    y, XA = 4.2, X0 + 1.6
    flag(ax, (XA - 0.1, y), "VOICE_DAC", right=False)
    c11 = d.add(elm.Capacitor().right().at((XA, y)).label("C11 1µ", fontsize=8))
    rv1 = d.add(elm.Potentiometer().right().at(c11.end).label("RV1 10k vol", loc="bottom", fontsize=8))
    j6 = d.add(elm.Ic(pins=[elm.IcPin(name="LIN", side="left", anchorname="LIN"), elm.IcPin(name="5V", side="top", anchorname="V"),
                            elm.IcPin(name="OUT", side="right", anchorname="LP")],
                      pinspacing=0.8, edgepadW=1.4, leadlen=0.4, label="J6\nPAM8403", lblsize=8).right().at(rv1.end).anchor("LIN"))
    flag(ax, (j6.absanchors["V"][0], j6.absanchors["V"][1] + 0.1), "+5V")
    d += elm.Speaker().right().at(j6.absanchors["LP"]).label("LS1 4 Ω 3 W", fontsize=8)
    y = -0.8
    flag(ax, (XA - 0.1, y), "GSM_TX", right=False)
    r17 = d.add(elm.Resistor().right().at((XA, y)).label("R17 1k", fontsize=8))
    d += elm.Dot().at(r17.end)
    r18 = d.add(elm.Resistor().down().at(r17.end).label("R18 2.2k", loc="bottom", fontsize=8)); gnd(d, r18.end)
    j8 = d.add(elm.Ic(pins=[elm.IcPin(name="RXD", side="left", anchorname="RX"), elm.IcPin(name="TXD", side="left", anchorname="TX"),
                            elm.IcPin(name="VCC", side="top", anchorname="V"), elm.IcPin(name="GND", side="bottom", anchorname="G")],
                      pinspacing=0.8, edgepadW=1.6, leadlen=0.4, label="J8\nSIM800L", lblsize=8).right().at((r17.end[0] + 1.4, y)).anchor("RX"))
    W(d, r17.end, j8.absanchors["RX"])
    tx = j8.absanchors["TX"]; W(d, tx, (tx[0] - 0.9, tx[1])); flag(ax, (tx[0] - 0.9, tx[1]), "GSM_RX", right=False)
    flag(ax, (j8.absanchors["V"][0], j8.absanchors["V"][1] + 0.1), "VBAT"); gnd(d, j8.absanchors["G"])
    d += elm.Label().at((j8.absanchors["V"][0] + 2.6, j8.absanchors["V"][1] - 0.2)).label("C12 1000 µF at the\nmodule (2 A bursts)", fontsize=7.5, halign="left")
    d += elm.Label().at((XA, -3.8)).label("R17/R18: 3.3 V → 2.3 V into the SIM800L's 2.8 V RXD", fontsize=7.5, halign="left", color="#57606a")
    # ---- right column: LEDs, buttons, drawer, vibration ----
    XR = 26.0
    for i, (net, ref, col) in enumerate((("LED_G", "D1", "green"), ("LED_A", "D2", "amber"), ("LED_R", "D3", "red"))):
        y = 16.5 - i * 1.5
        flag(ax, (XR - 0.1, y), net, right=False)
        r = d.add(elm.Resistor().right().at((XR, y)).label(f"R{14 + i} 220", fontsize=8))
        led = d.add(elm.LED().right().at(r.end).label(f"{ref} {col}", loc="bottom", fontsize=8))
        W(d, led.end, (led.end[0] + 0.4, y)); gnd(d, (led.end[0] + 0.4, y))
    for i, (net, ref, what) in enumerate((("BTN_G", "SW1", "green / no"), ("BTN_R", "SW2", "red / yes"), ("BTN_SOS", "SW3", "SOS"))):
        y = 11.6 - i * 1.4
        flag(ax, (XR - 0.1, y), net, right=False)
        b = d.add(elm.Button().right().at((XR, y)).label(f"{ref} {what}", fontsize=8))
        W(d, b.end, (b.end[0] + 0.4, y)); gnd(d, (b.end[0] + 0.4, y))
    d += elm.Label().at((XR + 3.4, 12.6)).label("internal pull-ups", fontsize=7.5, color="#57606a")
    y = 5.8
    flag(ax, (XR - 0.1, y), "DRAWER", right=False)
    W(d, (XR, y), (XR + 1.0, y)); d += elm.Dot().at((XR + 1.0, y))
    r20 = d.add(elm.Resistor().up().at((XR + 1.0, y)).label("R20 10k", loc="bottom", fontsize=8).length(1.3)); flag(ax, r20.end, "+3V3")
    sw5 = d.add(elm.Button().right().at((XR + 1.0, y)).label("SW5 drawer", loc="bottom", fontsize=8))
    W(d, sw5.end, (sw5.end[0] + 0.4, y)); gnd(d, (sw5.end[0] + 0.4, y))
    y = 1.6
    flag(ax, (XR - 0.1, y), "VIBRA", right=False)
    r21 = d.add(elm.Resistor().right().at((XR, y)).label("R21 1k", fontsize=8))
    q1 = d.add(elm.BjtNpn(circle=True).right().anchor("base").at(r21.end).label("Q1\n2N2222", loc="right", fontsize=8))
    gnd(d, q1.emitter)
    m1 = d.add(elm.Motor().up().at(q1.collector).label("M1 ERM", loc="bottom", fontsize=8).length(1.5))
    flag(ax, m1.end, "+5V")
    d4 = d.add(elm.Diode().up().at((q1.collector[0] + 1.4, q1.collector[1])).label("D4 1N4148", loc="bottom", fontsize=8).length(1.5))
    W(d, q1.collector, (q1.collector[0] + 1.4, q1.collector[1])); W(d, m1.end, (d4.end[0], m1.end[1]))
    d.draw()


# ------------------------------------------------------------------ sheet 4
def sheet_power(fig):
    ax = fig.add_axes([0.03, 0.25, 0.94, 0.72]); ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False); d.config(fontsize=9, unit=2.0)
    YG, YP = 12.0, 9.0                                       # charger ground line, charger +5 V line
    # ---- J12 USB-C in ----
    j12 = d.add(elm.Ic(pins=[elm.IcPin(name="GND", side="right", anchorname="G", slot="2/2"), elm.IcPin(name="VBUS", side="right", anchorname="V", slot="1/2")],
                       pinspacing=YG - YP, edgepadW=1.4, leadlen=0.5, label="J12\nUSB-C\n5 V in", lblsize=9).right().at((0, YP)).anchor("V"))
    # ---- SW6: one pole in each charger wire, mechanically linked ----
    W(d, j12.absanchors["G"], (2.0, YG)); W(d, j12.absanchors["V"], (2.0, YP))
    sg = d.add(elm.Switch().right().at((2.0, YG)).label("SW6a", fontsize=8))
    sp = d.add(elm.Switch().right().at((2.0, YP)).label("SW6b", loc="bottom", fontsize=8))
    ax.plot([3.0, 3.0], [YP + 0.35, YG - 0.05], ls=":", color=INK, lw=1.2, zorder=2)
    ax.text(3.25, (YP + YG) / 2, "SW6 CHARGE / USE\n(DPDT, poles a + b)\nUSE: both charger\nwires open", fontsize=8.5, color="#cf222e", va="center")
    W(d, sg.end, (7.0, YG)); W(d, sp.end, (7.0, YP))
    d += elm.Dot().at((5.2, YP)).label("CHG_IN", loc="top", fontsize=8)
    r23 = d.add(elm.Resistor().down().at((5.2, YP)).label("R23 100k", loc="bottom", fontsize=8).length(1.6))
    d += elm.Dot().at(r23.end); flag(ax, (r23.end[0] - 0.1, r23.end[1]), "CHG_SENSE", right=False)
    r24 = d.add(elm.Resistor().down().at(r23.end).label("R24 100k", loc="bottom", fontsize=8).length(1.6)); gnd(d, r24.end)
    d += elm.Dot().at((4.6, YG)); gnd(d, (4.6, YG - 0.0)) if False else None
    # ---- J9 TP4056 charger + BT1 ----
    tp = d.add(elm.Ic(pins=[elm.IcPin(name="IN−", side="left", anchorname="IN", slot="2/2"), elm.IcPin(name="IN+", side="left", anchorname="IP", slot="1/2"),
                            elm.IcPin(name="OUT−", side="right", anchorname="ON", slot="2/2"), elm.IcPin(name="OUT+", side="right", anchorname="OP", slot="1/2"),
                            elm.IcPin(name="B+", side="bottom", anchorname="BP", slot="1/2"), elm.IcPin(name="B−", side="bottom", anchorname="BN", slot="2/2")],
                      pinspacing=YG - YP, edgepadW=1.8, leadlen=0.5, label="J9\nTP4056\n1 A CC/CV\n+ DW01", lblsize=9).right().at((7.0, YP)).anchor("IP"))
    W(d, (7.0, YG), tp.absanchors["IN"]) if abs(tp.absanchors["IN"][1] - YG) < 1e-6 else None
    bp, bn = tp.absanchors["BP"], tp.absanchors["BN"]
    bt = d.add(elm.BatteryCell().down().at((bp[0], bp[1] - 0.3)).label("BT1 18650\n2500 mAh", loc="bottom", fontsize=8))
    W(d, bp, (bp[0], bp[1] - 0.3)); W(d, bt.end, (bt.end[0], bt.end[1] - 0.4), (bn[0], bt.end[1] - 0.4), bn)
    gnd(d, (bn[0], bt.end[1] - 0.4))
    # ---- SW4, VBAT, C12 ----
    on, op = tp.absanchors["ON"], tp.absanchors["OP"]
    W(d, on, (on[0] + 0.6, on[1])); gnd(d, (on[0] + 0.6, on[1]))
    sw4 = d.add(elm.Switch().right().at(op).label("SW4 power", fontsize=8))
    W(d, sw4.end, (sw4.end[0] + 0.6, YP)); d += elm.Dot().at((sw4.end[0] + 0.6, YP))
    flag(ax, (sw4.end[0] + 0.6, YP + 0.45), "VBAT")
    c12 = d.add(elm.Capacitor(polar=True).down().at((sw4.end[0] + 0.6, YP)).label("C12 1000 µF\n(at SIM800L)", loc="bottom", fontsize=8)); gnd(d, c12.end)
    # ---- J10 MT3608 boost ----
    xb = sw4.end[0] + 2.2
    W(d, (sw4.end[0] + 0.6, YP), (xb, YP))
    mt = d.add(elm.Ic(pins=[elm.IcPin(name="IN−", side="left", anchorname="IN", slot="2/2"), elm.IcPin(name="IN+", side="left", anchorname="IP", slot="1/2"),
                            elm.IcPin(name="OUT−", side="right", anchorname="ON", slot="2/2"), elm.IcPin(name="OUT+", side="right", anchorname="OP", slot="1/2")],
                      pinspacing=2.0, edgepadW=1.8, leadlen=0.5, label="J10\nMT3608\nboost 5.0 V", lblsize=9).right().at((xb, YP)).anchor("IP"))
    for k, dx in (("IN", -0.4), ("ON", 0.4)):
        p = mt.absanchors[k]; W(d, p, (p[0] + dx, p[1])); gnd(d, (p[0] + dx, p[1]))
    xo = mt.absanchors["OP"][0] + 1.0
    W(d, mt.absanchors["OP"], (xo, YP)); d += elm.Dot().at((xo, YP)); flag(ax, (xo, YP + 0.45), "+5V")
    # ---- U7 AMS1117 ----
    u7 = d.add(elm.Ic(pins=[elm.IcPin(name="VIN", side="left", anchorname="I"), elm.IcPin(name="VOUT", side="right", anchorname="O"),
                            elm.IcPin(name="GND", side="bottom", anchorname="G")], pinspacing=1.2, edgepadW=1.8, leadlen=0.5,
                      label="U7\nAMS1117-3.3\n(on DevKit)", lblsize=9).right().at((xo + 1.0, YP)).anchor("I"))
    W(d, (xo, YP), u7.absanchors["I"]); gnd(d, u7.absanchors["G"])
    xv = u7.absanchors["O"][0] + 1.2
    W(d, u7.absanchors["O"], (xv, YP)); d += elm.Dot().at((xv, YP)); flag(ax, (xv, YP + 0.45), "+3V3")
    c10 = d.add(elm.Capacitor().down().at((xv, YP)).label("C10 10 µF", loc="bottom", fontsize=8)); gnd(d, c10.end)
    # ---- notes ----
    d.draw()
    fig.text(0.04, 0.215, "USE (normal): both charger wires open; the stool runs on BT1 only. LTspice leakage through an earthed patient:\n"
             "0.19 µA (339 µA with a cheap charger connected, 72 mA if its insulation fails). CHARGE: CHG_IN high → R23/R24 →\n"
             "GPIO39 → the firmware refuses to measure. The TP4056 module's own USB socket is sealed: J12 + SW6 is the only way in.",
             fontsize=9.5, color="#cf222e", va="top")
    fig.text(0.04, 0.135, "Rails: VBAT → SIM800L directly (2 A bursts, C12 at the module) · +5V → DevKit VIN, PAM8403, ERM motor ·\n"
             "+3V3 → AFE, MAX30102, HX711, LEDs · VREF 1.65 V is made on sheet 2 (R1/R2 + U1A).\n"
             "Power budget HM-HW-003: 130 mA idle as built (0.7 days per charge); Rev B plan 22 mA (3.9 days).",
             fontsize=9.5, color="#57606a", va="top")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    with PdfPages(OUT / "HM-HW-002_schematics.pdf") as pdf:
        for n, (title, fn) in enumerate(zip(SHEETS, (sheet_index, sheet_afe, sheet_mcu, sheet_power)), 1):
            fig = plt.figure(figsize=(16.54, 11.69))       # A3 landscape
            fn(fig); frame(fig, n, title)
            pdf.savefig(fig); fig.savefig(OUT / f"HM-HW-002_sheet{n}.png", dpi=100); plt.close(fig)
            print("sheet", n, title)
