"""REFERENCE-DESIGN BLOCK DIAGRAM (HM-HW-001): every part with its part number, every bus with protocol / speed /
address, power rails colour-coded, the patient-side (applied part) boundary, the power tree and a title block.
Pins and values follow tools/make_schematic.py and the firmware.   Run:  python tools/make_reference_block.py
Out:  docs/hardware/HM-HW-001_block_diagram.png and .pdf
"""
import datetime, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "hardware"
INK, MUTED = "#1b1f24", "#57606a"
RAIL = {"VBAT": "#d1242f", "5V": "#e16f24", "3V3": "#0969da", "VREF": "#8250df"}
SIG, RF = "#2d333b", "#1a7f37"
W, H = 34, 22


def blk(ax, x, y, w, h, title, pn="", lines=(), fc="#ffffff", ec=INK, lw=1.6, tfs=10.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12", fc=fc, ec=ec, lw=lw))
    ax.text(x + 0.15, y + h - 0.15, title, fontsize=tfs, weight="bold", color=INK, va="top")
    if pn:
        ax.text(x + w - 0.15, y + h - 0.17, pn, fontsize=8, color=MUTED, va="top", ha="right", family="monospace")
    for i, l in enumerate(lines):
        ax.text(x + 0.15, y + h - 0.62 - 0.36 * i, l, fontsize=8.3, color="#24292f", va="top")
    return dict(x=x, y=y, w=w, h=h)


def wire(ax, pts, color=SIG, lw=1.7, label="", at=0, side="top", arrow=True, ls="-", fs=7.8):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=3)
    if arrow:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        ax.annotate("", xy=(x1, y1), xytext=(x0 + (x1 - x0) * 0.6, y0 + (y1 - y0) * 0.6),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=13), zorder=4)
    if label:
        (x0, y0), (x1, y1) = pts[at], pts[at + 1]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ax.text(mx, my + (0.12 if side == "top" else -0.12), label, fontsize=fs, color=color, ha="center",
                va="bottom" if side == "top" else "top", family="monospace",
                bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.9), zorder=5)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(25.5, 16.5)); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    fig.subplots_adjust(0.005, 0.005, 0.995, 0.995)
    # ---- frame + title ----
    ax.add_patch(Rectangle((0.2, 0.2), W - 0.4, H - 0.4, fc="none", ec=INK, lw=2))
    ax.text(0.6, H - 0.55, "HridayMitra check-in stool: system block diagram", fontsize=20, weight="bold", color=INK, va="top")
    ax.text(0.6, H - 1.25, "Home early-warning monitor for worsening heart failure (monitoring, not diagnosis). "
            "Custom part = 8-electrode bioimpedance analog front end (AFE) + ESP32.", fontsize=11, color=MUTED, va="top")
    # ---- patient side (applied part, type BF) ----
    ax.add_patch(FancyBboxPatch((0.6, 6.0), 6.6, 13.6, boxstyle="round,pad=0,rounding_size=0.3", fc="#fff8f2", ec="#d4a373", lw=1.4, ls="--"))
    ax.text(0.8, 19.45, "PATIENT SIDE: applied part, IEC 60601-1 type BF", fontsize=9.5, weight="bold", color="#9a6700", va="top")
    ax.text(0.8, 19.05, "battery only while touched · SW6 isolates the charger", fontsize=8, color="#9a6700", va="top")
    el = blk(ax, 1.0, 14.2, 5.8, 4.3, "Electrodes J1 ×8", "SS304 plates", ["4 foot plates: forefoot = current,", "heel = sense (tetrapolar)",
             "4 hand strips: outer = current,", "inner = sense", "skin contact 0.2-10 kΩ tolerated", "4 paths: legs, arms, R side, L side"], fc="#fffdf9")
    fg = blk(ax, 1.0, 11.6, 5.8, 2.1, "Finger optical", "MAX30102", ["red 660 nm + IR 880 nm LEDs", "18-bit, 100 S/s, 7 mA LED"], fc="#fffdf9")
    lc = blk(ax, 1.0, 8.9, 5.8, 2.2, "Seat load cells ×4", "50 kg half-bridges", ["one full bridge → HX711", "24-bit, 10 S/s, 105 counts/kg"], fc="#fffdf9")
    ui = blk(ax, 1.0, 6.3, 5.8, 2.1, "User interface", "", ["GREEN / RED answer + SOS buttons", "tablet-drawer microswitch"], fc="#fffdf9")
    # ---- custom AFE board ----
    ax.add_patch(FancyBboxPatch((7.9, 8.6), 9.0, 11.0, boxstyle="round,pad=0,rounding_size=0.3", fc="#f6f8fa", ec="#0969da", lw=2.2))
    ax.text(8.1, 19.45, "CUSTOM AFE BOARD (this design, HM-HW-002)", fontsize=10, weight="bold", color="#0969da", va="top")
    mux = blk(ax, 8.2, 16.3, 4.2, 2.6, "Path switches", "74HC4052 U4/U5", ["U4 current pair", "U5 sense pair", "Ron ≈ 100 Ω (cancels)"])
    ex = blk(ax, 12.5, 16.3, 4.2, 2.6, "Current source", "MCP6002 U1", ["DAC → 1 µF → buffer", "C3 + C4 DC block", "R4 4.7 k: 100 µA rms"])
    sel = blk(ax, 8.2, 13.2, 4.2, 2.7, "Body / ref select", "74HC4053 U3", ["A/B: body or reference", "C: Rcal or R5+Rcal", "(self-check ratio 2.2)"])
    ina = blk(ax, 12.5, 13.2, 4.2, 2.7, "Instrumentation amp", "INA126 U2", ["G = 10 (RG 16 k)", "R8/R9 10 MΩ bias", "1.5 k / 10 n anti-alias"])
    ref = blk(ax, 8.2, 8.9, 8.4, 3.9, "References", "", ["Rcal 100 Ω 0.1 % 25 ppm: the impedance reference", "R5 120 Ω: self-check partner (ratio 2.2 ± 9 %)",
              "VREF 1.65 V: R1/R2 10 k 1 % + U1A buffer", "Z = Rcal · |V(body)| / |V(Rcal)|", "(current, gain and Ron cancel)"])
    # ---- ESP32 ----
    ax.add_patch(FancyBboxPatch((18.3, 6.3), 6.4, 13.3, boxstyle="round,pad=0,rounding_size=0.3", fc="#fbefff", ec="#8250df", lw=2.2))
    ax.text(18.5, 19.45, "ESP32-WROOM-32 (DevKitC)", fontsize=11, weight="bold", color="#8250df", va="top")
    ax.text(18.5, 19.0, "Xtensa LX6 ×2, 240 MHz · 520 KB SRAM · 4 MB flash", fontsize=8, color=MUTED, va="top")
    for i, l in enumerate(["DAC1 GPIO25: 5/20/50 kHz cosine", "ADC1_CH7 GPIO35: DMA 200 kS/s", "GPIO33/27 S0 S1 · 18 SEL · 12 CAL",
                           "I²C GPIO21/22 · HX711 GPIO32/14", "UART2 GPIO16/17 · DAC2 GPIO26 voice", "GPIO39 charge sense · 36 drawer",
                           "", "Firmware (C++, offline):", "· Goertzel + Cole fit (EWI)", "· alert engine v3 (= Python, 100 %)",
                           "· care-loop state machine, SMS queue", "· self-test, self-calibration", "· BLE: amulet scan + app GATT",
                           "· flash: 2 users' history, 25 voice clips"]):
        ax.text(18.55, 18.4 - 0.4 * i, l, fontsize=8.3, color="#24292f", va="top", family="monospace" if i < 6 else None)
    # ---- right side peripherals ----
    gsm = blk(ax, 26.0, 16.7, 7.4, 2.6, "GSM modem", "SIM800L", ["2G quad-band SMS · Airtel / Vi / BSNL", "2 A bursts from VBAT, 1000 µF", "RTC from network (AT+CCLK)"])
    aud = blk(ax, 26.0, 13.9, 7.4, 2.3, "Voice out", "PAM8403 + 4 Ω 3 W", ["8-bit 8 kHz clips from flash", "Hindi / English, per user"])
    led = blk(ax, 26.0, 11.3, 7.4, 2.1, "Status", "LEDs + ERM motor", ["green / amber / red, 220 Ω", "seat vibration via 2N2222"])
    usb = blk(ax, 26.0, 8.7, 7.4, 2.1, "USB-UART (on DevKit)", "CP2102", ["laptop bridge, flashing, app (USB)", "laptop on battery only"])
    amu = blk(ax, 26.0, 6.3, 7.4, 1.9, "Kavach amulet", "ESP32-C3 + MPU6050", ["breathing, sit-ups, 6-min walk, fall, SOS"], fc="#f0fff4")
    # ---- buses ----
    wire(ax, [(6.8, 17.9), (8.2, 17.9)], SIG, label="4 current", fs=7)
    wire(ax, [(6.8, 16.8), (8.2, 16.8)], SIG, label="4 sense", fs=7, side="bottom")
    wire(ax, [(12.5, 17.3), (12.4, 17.3)], SIG)
    wire(ax, [(10.3, 16.3), (10.3, 15.9)], SIG)
    wire(ax, [(12.4, 14.5), (12.5, 14.5)], SIG)
    wire(ax, [(18.3, 18.1), (16.7, 18.1)], SIG, label="DAC1 cosine", fs=7.5)
    wire(ax, [(16.7, 14.0), (17.55, 14.0), (17.55, 17.2), (18.3, 17.2)], SIG, label="ADC 1.65±0.6 V", at=0, fs=6.8, side="bottom")
    wire(ax, [(18.3, 16.4), (17.95, 16.4), (17.95, 12.2), (16.9, 12.2)], SIG, label="S0 S1 SEL CAL", at=2, fs=6.8, side="bottom")
    wire(ax, [(6.8, 12.6), (7.4, 12.6), (7.4, 8.35), (18.3, 8.35)], SIG, label="I²C 400 kHz · MAX30102 @ 0x57", at=2, fs=7.5)
    wire(ax, [(6.8, 10.0), (7.65, 10.0), (7.65, 7.75), (18.3, 7.75)], SIG, label="HX711 2-wire, 24-bit @ 10 S/s", at=2, fs=7.5, side="bottom")
    wire(ax, [(6.8, 6.9), (18.3, 6.9)], SIG, label="GPIO 4 / 5 / 15 / 36", fs=7.5)
    wire(ax, [(24.7, 18.0), (26.0, 18.0)], SIG, label="UART2 9600 8N1", fs=7, side="bottom")
    wire(ax, [(24.7, 15.0), (26.0, 15.0)], SIG, label="DAC2", fs=7)
    wire(ax, [(24.7, 12.3), (26.0, 12.3)], SIG, label="GPIO", fs=7)
    wire(ax, [(26.0, 9.7), (24.7, 9.7)], SIG, label="USB 2.0 FS", fs=7)
    wire(ax, [(26.0, 7.2), (24.7, 7.2)], RF, label="BLE 2.4 GHz adv", fs=7, ls="--")
    ax.text(29.7, 19.6, "((·)) GSM 900/1800 → family, ASHA, PHC doctor", fontsize=8.5, color=RF, ha="center", weight="bold")
    ax.text(21.5, 5.95, "((·)) BLE GATT → Saathi phone app (6e8a0001-…)", fontsize=8.5, color=RF, ha="center", weight="bold")
    # ---- power tree ----
    ax.add_patch(FancyBboxPatch((0.6, 0.6), 26.6, 4.9, boxstyle="round,pad=0,rounding_size=0.3", fc="#fffafa", ec="#d1242f", lw=1.4))
    ax.text(0.8, 5.35, "POWER TREE", fontsize=10.5, weight="bold", color="#d1242f", va="top")
    p_usb = blk(ax, 0.9, 2.3, 2.6, 2.2, "USB-C in", "5 V", ["phone charger"], ec="#d1242f")
    p_sw = blk(ax, 4.2, 2.3, 3.2, 2.2, "SW6 CHARGE/USE", "DPDT", ["USE: both wires cut", "CHARGE: GPIO39 high"], ec="#d1242f")
    p_chg = blk(ax, 8.1, 2.3, 3.2, 2.2, "Li-ion charger", "TP4056", ["1 A CC/CV, 4.2 V", "DW01 protection"], ec="#d1242f")
    p_bat = blk(ax, 12.0, 2.3, 3.2, 2.2, "18650 cell", "2500 mAh", ["3.0-4.2 V (VBAT)", "SW4 power switch"], ec="#d1242f")
    p_bst = blk(ax, 15.9, 2.3, 3.2, 2.2, "Boost", "MT3608", ["VBAT → 5.0 V", "≈ 90 % efficient"], ec="#e16f24")
    p_ldo = blk(ax, 19.8, 2.3, 3.2, 2.2, "LDO (DevKit)", "AMS1117-3.3", ["5 V → 3.3 V, 1 A", "AFE + sensors"], ec="#0969da")
    p_ref = blk(ax, 23.7, 2.3, 3.2, 2.2, "VREF", "U1A buffer", ["3V3 / 2 = 1.65 V", "AFE mid-rail"], ec="#8250df")
    for a, b, c, lab in [(p_usb, p_sw, "#d1242f", "5 V"), (p_sw, p_chg, "#d1242f", ""), (p_chg, p_bat, RAIL["VBAT"], ""),
                         (p_bat, p_bst, RAIL["VBAT"], "VBAT"), (p_bst, p_ldo, RAIL["5V"], "5 V"), (p_ldo, p_ref, RAIL["3V3"], "3V3")]:
        wire(ax, [(a["x"] + a["w"], 3.4), (b["x"], 3.4)], c, lw=2.6, label=lab, fs=7.5)
    ax.text(0.9, 1.75, "Rails: VBAT → SIM800L direct (2 A bursts) · 5 V → DevKit VIN, PAM8403, motor · 3V3 → AFE, MAX30102, HX711 · VREF → AFE bias",
            fontsize=8.5, color=MUTED, va="top")
    import json
    pb = json.loads((ROOT / "reports" / "power_budget.json").read_text())
    ax.text(0.9, 1.25, f"Budget (HM-HW-003, datasheet typical): idle {pb['idle_battery_mA']:.0f} mA → {pb['days_per_charge']} days per charge as built; "
            f"Rev B power plan {pb['rev_b_idle_battery_mA']:.0f} mA → {pb['rev_b_days_per_charge']} days · check-in {pb['checkin_battery_mA']:.0f} mA · "
            f"peak {pb['worst_peak_mA'] / 1000:.1f} A (GSM)", fontsize=8.5, color=MUTED, va="top")
    # ---- legend ----
    lx = 27.6
    ax.text(lx, 5.35, "LEGEND", fontsize=9.5, weight="bold", color=INK, va="top")
    for i, (name, c) in enumerate([("VBAT 3.0-4.2 V", RAIL["VBAT"]), ("5 V", RAIL["5V"]), ("3V3", RAIL["3V3"]), ("VREF 1.65 V", RAIL["VREF"]),
                                   ("signal / bus", SIG), ("radio link", RF)]):
        ax.plot([lx, lx + 0.8], [4.8 - 0.33 * i] * 2, color=c, lw=2.6 if i < 4 else 1.7, ls="--" if name == "radio link" else "-")
        ax.text(lx + 1.0, 4.8 - 0.33 * i, name, fontsize=8, va="center", color=INK)
    # ---- title block ----
    tb = (27.4, 0.6, 6.0, 2.1)
    ax.add_patch(Rectangle(tb[:2], tb[2], tb[3], fc="white", ec=INK, lw=1.4))
    for y_ in (1.3, 2.0):
        ax.plot([tb[0], tb[0] + tb[2]], [y_, y_], color=INK, lw=0.8)
    ax.text(tb[0] + 0.12, 2.55, "HridayMitra · system block diagram", fontsize=8.5, weight="bold", va="top")
    ax.text(tb[0] + 0.12, 1.85, f"Doc HM-HW-001   Rev A   {datetime.date(2026, 10, 25).isoformat()}", fontsize=8, va="top", family="monospace")
    ax.text(tb[0] + 0.12, 1.15, "Sheet 1 / 1   Transfinitte 2025, hardware", fontsize=8, va="top", family="monospace")
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"HM-HW-001_block_diagram.{ext}", dpi=110)
    print("wrote", OUT / "HM-HW-001_block_diagram.png")
