"""POWER BUDGET (HM-HW-003): every load on every rail, datasheet typical currents, firmware duty cycles, converted to
battery current through the MT3608 boost and the DevKit LDO. Gives battery life per charge and the worst-case peak.
Currents are datasheet TYPICAL values (not measured): the bench build must measure them (test plan, HM-HW-006).
Run:  python tools/power_budget.py     Out: docs/hardware/HM-HW-003_power_budget.csv/.png, reports/power_budget.json
"""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "hardware"
VBAT, BOOST_EFF, CELL_MAH, USABLE = 3.7, 0.88, 2500, 0.85
CHECKINS_PER_DAY, CHECKIN_S = 2, 90                       # patient check-in (+ a guest / retry allowance)
SMS_PER_DAY, SMS_TX_S = 3, 3                              # weekly summary, reminders, care loop: average
BLE_SCAN_DUTY = 4 / 60                                    # firmware: 4 s scan every 60 s
VOICE_S_PER_CHECKIN = 60

# (part, rail, idle mA, active mA during a check-in, source)
LOADS = [
    ("ESP32 CPU 240 MHz (radio off)", "3V3", 40, 45, "Espressif ESP32 datasheet: 30-68 mA modem-sleep"),
    ("ESP32 BLE scan (4 s / 60 s)", "3V3", 100 * BLE_SCAN_DUTY, 100 * BLE_SCAN_DUTY, "ESP32 datasheet: ~100 mA RX"),
    ("CP2102 USB-UART (suspended)", "3V3", 0.1, 0.1, "SiLabs CP2102: 80 µA suspend"),
    ("AMS1117 LDO quiescent", "5V", 5, 5, "AMS1117 datasheet: 5 mA"),
    ("MAX30102 (LEDs only while finger)", "3V3", 0.0007, 15, "Maxim: 600 µA + 2 × 7 mA LEDs"),
    ("HX711 + load-cell bridge", "3V3", 1.5 + 3.3, 1.5 + 3.3, "Avia HX711 1.5 mA; 1 kΩ bridge 3.3 mA"),
    ("AFE: MCP6002 + INA126 + 3 × 74HC405x", "3V3", 0.33, 0.43, "MCP6002 100 µA ×2, INA126 175 µA, 74HC ~1 µA; +100 µA excitation"),
    ("Status LED (one lit after a check-in)", "3V3", 6, 6, "220 Ω, 2 V LED"),
    ("PAM8403 amp (quiescent / speaking)", "5V", 10, 10 + 180 * VOICE_S_PER_CHECKIN / CHECKIN_S, "Diodes PAM8403: 10 mA Iq, ~0.9 W average speech"),
    ("SIM800L idle, registered", "VBAT", 18, 18, "SIMCom: 18.7 mA idle (DRX)"),
    ("MT3608 boost quiescent", "VBAT", 0.1, 0.1, "Aerosemi MT3608"),
]


# Rev B power plan (firmware + one P-MOSFET): what changes in IDLE (check-in currents unchanged)
REV_B = {"ESP32 CPU 240 MHz (radio off)": (0.8 + 45 * 1 / 60, "light-sleep 0.8 mA; awake 1 s per minute"),
         "ESP32 BLE scan (4 s / 60 s)": (100 * BLE_SCAN_DUTY, "unchanged: the SOS scan stays"),
         "HX711 + load-cell bridge": (0.001, "PD_SCK high between check-ins (< 1 µA)"),
         "Status LED (one lit after a check-in)": (6 * 0.02, "50 ms blink every 2.5 s"),
         "PAM8403 amp (quiescent / speaking)": (0.001, "P-MOSFET on its 5 V, on only while speaking (+₹5)"),
         "SIM800L idle, registered": (1.0, "AT+CSCLK=1 sleep; RI pin wakes the ESP32 on an SMS")}


def battery_ma(rail, ma):
    """Current drawn from the cell for `ma` on `rail` (LDO passes current; boost scales by voltage and efficiency)."""
    if rail == "VBAT":
        return ma
    return ma * 5.0 / (VBAT * BOOST_EFF)                    # 3V3 comes from 5 V through the LDO (same current)


if __name__ == "__main__":
    rows, idle, act = [], 0.0, 0.0
    for part, rail, i_idle, i_act, src in LOADS:
        bi, ba = battery_ma(rail, i_idle), battery_ma(rail, i_act)
        idle += bi; act += ba
        rows.append(dict(part=part, rail=rail, idle_mA=round(i_idle, 3), checkin_mA=round(i_act, 2),
                         battery_idle_mA=round(bi, 2), battery_checkin_mA=round(ba, 2), source=src))
    idle_b = sum(battery_ma(rail, REV_B.get(part, (i_idle,))[0]) for part, rail, i_idle, _, _ in LOADS)
    sms_mah = SMS_PER_DAY * SMS_TX_S / 3600 * 350             # SIM800L ~350 mA average while sending (2 A peaks)
    day_mah = idle * 24 + (act - idle) * CHECKINS_PER_DAY * CHECKIN_S / 3600 + sms_mah
    days = CELL_MAH * USABLE / day_mah
    day_b = idle_b * 24 + (act - idle_b) * CHECKINS_PER_DAY * CHECKIN_S / 3600 + sms_mah
    days_b = CELL_MAH * USABLE / day_b
    peak = act + 2000                                        # GSM transmit burst on VBAT during a check-in
    out = dict(idle_battery_mA=round(idle, 1), checkin_battery_mA=round(act, 1), sms_mAh_per_day=round(sms_mah, 2),
               mAh_per_day=round(day_mah, 0), days_per_charge=round(days, 1), worst_peak_mA=round(peak, 0),
               rev_b_idle_battery_mA=round(idle_b, 1), rev_b_mAh_per_day=round(day_b, 0), rev_b_days_per_charge=round(days_b, 1),
               cell=f"18650 {CELL_MAH} mAh, {USABLE:.0%} usable", note="datasheet typical currents; measure on the bench")
    (ROOT / "reports" / "power_budget.json").write_text(json.dumps(out, indent=1))
    import csv
    with open(OUT / "HM-HW-003_power_budget.csv", "w", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    # ---- sheet ----
    fig = plt.figure(figsize=(16.5, 8.6))
    fig.text(0.04, 0.95, "HridayMitra stool: power budget", fontsize=20, weight="bold")
    fig.text(0.04, 0.91, f"Doc HM-HW-003  Rev A  ·  {out['cell']}  ·  boost {BOOST_EFF:.0%}  ·  {CHECKINS_PER_DAY} check-ins/day × {CHECKIN_S} s, "
             f"{SMS_PER_DAY} SMS/day  ·  datasheet typical currents (to be measured on the bench)", fontsize=10.5, color="#57606a")
    ax = fig.add_axes([0.04, 0.56, 0.92, 0.33]); ax.axis("off")
    tab = ax.table(cellText=[[r["part"], r["rail"], f"{r['idle_mA']:g}", f"{r['checkin_mA']:g}", f"{r['battery_idle_mA']:.1f}",
                              f"{r['battery_checkin_mA']:.1f}", f"{battery_ma(r['rail'], REV_B.get(r['part'], (r['idle_mA'],))[0]):.1f}",
                              REV_B[r["part"]][1] if r["part"] in REV_B else r["source"]] for r in rows] +
                   [["TOTAL from the 18650", "", "", "", f"{idle:.1f}", f"{act:.1f}", f"{idle_b:.1f}", "boost + LDO losses included"]],
                   colLabels=["Load", "Rail", "Idle mA", "Check-in mA", "Battery idle mA", "Battery check-in mA", "Rev B battery idle mA", "Source / Rev B change"],
                   colWidths=[0.22, 0.04, 0.06, 0.07, 0.09, 0.1, 0.1, 0.32], loc="upper left", cellLoc="left")
    tab.auto_set_font_size(False); tab.set_fontsize(9); tab.scale(1, 1.55)
    for (r, c), cell in tab.get_celld().items():
        if r == 0 or r == len(rows) + 1:
            cell.set_text_props(weight="bold"); cell.set_facecolor("#f6f8fa")
    kp = [("Idle, Rev A (as built)", f"{idle:.0f} mA"), ("Per charge, Rev A", f"{days:.1f} days"),
          ("Idle, Rev B plan", f"{idle_b:.0f} mA"), ("Per charge, Rev B", f"{days_b:.1f} days"), ("Worst peak (GSM TX)", f"{peak / 1000:.1f} A")]
    for i, (k, v) in enumerate(kp):
        x = 0.04 + i * 0.185
        fig.patches.append(plt.Rectangle((x, 0.41), 0.17, 0.12, transform=fig.transFigure, fc="#f6f8fa", ec="#d0d7de"))
        fig.text(x + 0.012, 0.50, k, fontsize=11, color="#57606a")
        fig.text(x + 0.012, 0.435, v, fontsize=24, weight="bold", color="#cf222e" if i < 2 else ("#1a7f37" if i < 4 else "#0969da"))
    fig.text(0.04, 0.35, "Design consequences:", fontsize=11, weight="bold")
    for i, l in enumerate(["• Rev A (firmware as built) needs charging every night. Rev B is firmware power management plus one ₹5 P-MOSFET (column 'Rev B').",
                           "• The SIM800L's 2 A transmit bursts come straight from the cell (VBAT), never through the boost; 1000 µF at the module.",
                           "• Either way the stool stays on CHARGE overnight (SW6; it refuses to measure while charging) and keeps scanning for an SOS."]):
        fig.text(0.04, 0.32 - 0.03 * i, l, fontsize=10)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"HM-HW-003_power_budget.{ext}", dpi=110)
    print(out)
