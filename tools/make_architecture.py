"""SYSTEM ARCHITECTURE (block diagram, PS deliverable 2): the whole chain from the body to the doctor in five layers,
every arrow labelled with what actually flows through it (numbers from our simulations and firmware), plus the
safety / power layer and what happens on each failure.   Run:  python tools/make_architecture.py
Out:  docs/hardware/architecture.png and .pdf
"""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "hardware"
LANES = [("BODY", "what we sense", "#fff4e6", "#e8590c"), ("ANALOG", "custom front end", "#e7f5ff", "#1864ab"),
         ("DIGITAL", "ESP32 firmware", "#f3f0ff", "#5f3dc4"), ("INTELLIGENCE", "on-device engine", "#ebfbee", "#2b8a3e"),
         ("ACTION", "people who act", "#fff0f6", "#c2255c")]
W, H = 30, 19


def box(ax, x, y, w, h, title, body, edge, face="white", fs=9.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.25", fc=face, ec=edge, lw=1.8))
    ax.text(x + w / 2, y + h - 0.32, title, ha="center", va="top", fontsize=fs + 1.5, weight="bold", color="#212529")
    ax.text(x + w / 2, y + h - 0.85, body, ha="center", va="top", fontsize=fs, color="#343a40", linespacing=1.35)
    return (x, y, w, h)


def arrow(ax, a, b, label="", color="#495057", dashed=False, rad=0.0, lpos=0.5, loff=(0, 0.22)):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=16, color=color, lw=1.8,
                                 linestyle="--" if dashed else "-", connectionstyle=f"arc3,rad={rad}"))
    if label:
        x, y = a[0] + (b[0] - a[0]) * lpos + loff[0], a[1] + (b[1] - a[1]) * lpos + loff[1]
        ax.text(x, y, label, ha="center", va="bottom", fontsize=8.6, color=color, weight="bold",
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.5))


R = lambda b: (b[0] + b[2], b[1] + b[3] / 2)
Lf = lambda b: (b[0], b[1] + b[3] / 2)
T = lambda b, f=0.5: (b[0] + b[2] * f, b[1] + b[3])
Bt = lambda b, f=0.5: (b[0] + b[2] * f, b[1])

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(24, 15.2)); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    fig.subplots_adjust(0.01, 0.01, 0.99, 0.99)
    ax.text(0.3, H - 0.35, "HridayMitra: system architecture, from the body to the doctor", fontsize=22, weight="bold", va="top")
    ax.text(0.3, H - 1.15, "Each arrow is labelled with what really flows through it (values from LTspice, the firmware emulator and the "
            "synthetic cohorts). Home unit parts ₹3,917-4,820. Monitoring, not diagnosis.", fontsize=11.5, color="#495057", va="top")
    lane_x, lane_w, top = [0.3, 5.3, 11.2, 17.6, 23.9], [4.8, 5.7, 6.2, 6.1, 5.8], H - 2.0
    for (name, sub, face, edge), x, w in zip(LANES, lane_x, lane_w):
        ax.add_patch(FancyBboxPatch((x, 4.3), w, top - 4.3, boxstyle="round,pad=0.02,rounding_size=0.3", fc=face, ec="none"))
        ax.text(x + 0.2, top - 0.25, name, fontsize=14, weight="bold", color=edge, va="top")
        ax.text(x + 0.2, top - 0.85, sub, fontsize=10, color=edge, va="top")
    E = [l[3] for l in LANES]
    # ---- BODY ----
    legs = box(ax, 0.5, 12.6, 4.4, 2.6, "Leg + chest fluid", "fluid outside cells ↑\nimpedance ↓ (−8.7 % per\n+10 % fluid), Cole model\nRe ‖ (Ri + Cm)", E[0])
    blood = box(ax, 0.5, 9.9, 4.4, 2.3, "Pulse + oxygen", "finger blood volume\nred / infrared light", E[0])
    mass = box(ax, 0.5, 7.6, 4.4, 1.9, "Body weight", "fluid gain = kg", E[0])
    chest = box(ax, 0.5, 4.6, 4.4, 2.6, "Chest motion (night)", "breathing, sitting up,\nsteps, falls\n(worn amulet)", E[0])
    # ---- ANALOG ----
    afe = box(ax, 5.5, 11.7, 5.3, 4.2, "8-electrode impedance AFE", "100 µA at 5 / 20 / 50 kHz\n4 paths: legs, arms, 2 sides\n(74HC4052 ×2)\nINA126 G = 10, 10 MΩ bias\nRcal 0.1 % self-calibration", E[1])
    ppg = box(ax, 5.5, 9.4, 5.3, 1.9, "MAX30102", "18-bit PPG, 100 S/s, I²C", E[1])
    lc = box(ax, 5.5, 7.3, 5.3, 1.7, "4 load cells + HX711", "24-bit bridge, 10 S/s", E[1])
    imu = box(ax, 5.5, 4.6, 5.3, 2.3, "Kavach amulet", "ESP32-C3 + MPU6050\n10-20 S/s accelerometer", E[1])
    # ---- DIGITAL ----
    dsp = box(ax, 11.4, 11.7, 5.8, 4.2, "Impedance DSP", "DMA ADC 200 kS/s\nGoertzel per frequency\nZ = Rcal × V(body) / V(Rcal)\n3-point Cole fit → EWI\nlifted-foot + hum checks", E[2])
    sig = box(ax, 11.4, 9.0, 5.8, 2.3, "Vital-sign extraction", "pulse from peaks, SpO₂ ratio\nstand-up time, 3 voice questions", E[2])
    amu = box(ax, 11.4, 4.6, 5.8, 4.0, "Amulet firmware", "night breathing (60 s windows)\nsit-ups (tilt hysteresis)\n6-min walk (autocorrelation)\nfall + SOS", E[2])
    # ---- INTELLIGENCE ----
    eng = box(ax, 17.8, 10.2, 5.7, 5.7, "Alert engine v3 (on chip)", "personal baseline: median of\ndays −35 … −7 (MAD spread)\nworsening-only z per signal\n3 families: fluid, heart-lungs,\ndaily life\ntwo-witness red, hysteresis\nguest + plate gates\nT = 7.0 frozen on training", E[3])
    hyb = box(ax, 17.8, 7.3, 5.7, 2.5, "Hybrid (app / laptop)", "rules propose, logistic\nmodel confirms: 86 % caught", E[3])
    why = box(ax, 17.8, 4.6, 5.7, 2.3, "Explanation", "\"weight +1.7 kg; leg reading\n−4 %; breathless\"", E[3])
    # ---- ACTION ----
    pat = box(ax, 24.1, 12.9, 5.4, 3.0, "Patient (stool)", "green / amber / red light\nHindi voice + doctor's plan\nno reading needed", E[4])
    sms = box(ax, 24.1, 8.6, 5.4, 3.9, "SMS care loop (2G)", "family 1 → family 2 (30 min)\n→ ASHA (2 h) → PHC doctor (6 h)\nreplies 1 / 2 / 3, missed call\n92 % reviewed before the visit", E[4])
    app = box(ax, 24.1, 4.6, 5.4, 3.6, "Saathi app (offline PWA)", "BLE / USB from the stool\n10 languages, voice commands\nfamily · ASHA · doctor views\nsame engine, checked daily", E[4])
    # ---- arrows with what flows ----
    arrow(ax, R(legs), Lf(afe), "Z ≈ 290 Ω / leg", E[0])
    arrow(ax, R(blood), Lf(ppg), "light", E[0])
    arrow(ax, R(mass), Lf(lc), "kg", E[0])
    arrow(ax, R(chest), Lf(imu), "g", E[0])
    arrow(ax, R(afe), Lf(dsp), "1.65 ± 0.6 V sine", E[1])
    arrow(ax, R(ppg), Lf(sig), "I²C 400 kHz", E[1])
    arrow(ax, R(lc), (11.4, 9.6), "counts", E[1])
    arrow(ax, R(imu), Lf(amu), "I²C", E[1])
    arrow(ax, R(dsp), (17.8, 14.2), "Ω, EWI", E[2])
    arrow(ax, R(sig), (17.8, 11.2), "bpm, %, s, yes/no", E[2])
    arrow(ax, (17.2, 7.0), (17.8, 10.6), "BLE advert", E[2], dashed=True, rad=-0.15, lpos=0.35, loff=(0.0, 0.1))
    arrow(ax, R(eng), Lf(pat), "light + reason", E[3])
    arrow(ax, (23.5, 12.0), Lf(sms), "red", E[3], lpos=0.55)
    arrow(ax, (23.5, 8.6), Lf(app), "JSON over BLE / USB", E[3], rad=0.1)
    arrow(ax, Bt(eng), T(hyb), "", E[3]); arrow(ax, Bt(hyb), T(why), "", E[3])
    # ---- safety + power layer ----
    ax.add_patch(FancyBboxPatch((0.3, 0.3), W - 0.6, 3.6, boxstyle="round,pad=0.02,rounding_size=0.3", fc="#f8f9fa", ec="#adb5bd", lw=1.2))
    ax.text(0.5, 3.75, "SAFETY, POWER AND FAILURES (designed in, each one tested)", fontsize=13, weight="bold", color="#495057", va="top")
    items = [("Patient safety", "IEC 60601-1 type BF: every\nsingle fault ≥ 12.8× under limit;\nC3 + C4 block DC"),
             ("CHARGE / USE switch", "cuts both charger wires:\nleakage 0.19 µA (339 µA\nwith a cheap charger)"),
             ("Power cut / no network", "18650 battery; SMS queue\nretries every 10 min;\nengine state in flash"),
             ("Bad contact / guest", "lifted foot named + re-measured;\ntoe ring > 25 % = no reading;\nguest not saved"),
             ("Part failure", "Rcal ratio checked at each\ncheck-in: outside 2.0-2.4 →\nno numbers + service SMS"),
             ("Pacemaker / ICD", "never on the plates:\nweight-only mode,\nno magnets in the amulet")]
    for i, (t, b) in enumerate(items):
        box(ax, 0.6 + i * 4.85, 0.5, 4.6, 2.8, t, b, "#868e96", fs=9)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"architecture.{ext}", dpi=110)
    print("wrote", OUT / "architecture.png")
