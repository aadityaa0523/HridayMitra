"""FRONT-END SHEET: the custom hardware part (8-electrode bioimpedance front end + ESP32) as a wired schematic, drawn
stage by stage, with the LTspice waveform at every test point underneath ("simulation proof" on the same page).
Values and connections are the same as tools/make_schematic.py (KiCad, ERC-checked) and sim/circuit/trunk_paths.py.
Run:  python sim/circuit/testpoints.py && python tools/make_frontend_sheet.py
Out:  docs/hardware/frontend_sheet.png and .pdf
"""
import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "hardware"
TPC = "#e8590c"                                            # test-point colour
GREEN = "#2b8a3e"


def tp(d, xy, name, where="top"):
    d += elm.Dot(radius=0.16).at(xy).color(TPC).label(name, loc=where, color=TPC, fontsize=11, ofst=0.2)


def L(d, *pts):
    """Orthogonal wire through the given points."""
    for a, b in zip(pts, pts[1:]):
        d += elm.Line().at(a).to(b)


def vref(d, xy, up=False):
    d += (elm.Vdd().up() if up else elm.Vdd().down()).at(xy).label("VREF", fontsize=9)


def frame(d, bb, title, color):
    x0, y0, x1, y1 = bb
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        d += elm.Line().at(a).to(b).color(color).linestyle("--").linewidth(1.3)
    d += elm.Label().at((x0 + 0.15, y1 - 0.45)).label(title, color=color, fontsize=12, halign="left")


def schematic(ax):
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=10, unit=2.2)
    Y = 10.0
    # ---- 1. current source: DAC -> C2 -> MCP6002 follower (biased at VREF by R3) -> C3 -> R4 ----
    d += elm.Dot().at((0, Y)).label("ESP32 DAC\nGPIO25\n5 / 20 / 50 kHz", loc="left", fontsize=10)
    tp(d, (0, Y), "TP1", "bottom")
    c2 = d.add(elm.Capacitor().at((0, Y)).right().label("C2 1 µF"))
    d += elm.Dot().at(c2.end)
    r3 = d.add(elm.Resistor().at(c2.end).down(2.4).label("R3\n100 k", loc="bottom"))
    vref(d, r3.end)
    u1 = d.add(elm.Opamp().right().at((c2.end[0] + 0.8, Y)).anchor("in2").label("U1B\nMCP6002", loc="center", ofst=(-0.35, 0), fontsize=9))
    L(d, c2.end, u1.in2)
    xo, yo = u1.out[0], u1.out[1]
    L(d, u1.out, (xo + 0.5, yo), (xo + 0.5, yo + 1.6), (u1.in1[0] - 0.5, yo + 1.6), (u1.in1[0] - 0.5, u1.in1[1]), u1.in1)
    L(d, (xo + 0.5, yo), (xo + 0.9, yo))
    tp(d, (xo + 0.9, yo), "TP2", "bottom")
    c3 = d.add(elm.Capacitor().at((xo + 0.9, yo)).right().label("C3 1 µF\nDC block"))
    r4 = d.add(elm.Resistor().at(c3.end).right().label("R4 4.7 k 1 %\ncurrent limit"))
    tp(d, r4.end, "TP3", "bottom")
    # ---- 2. current-pair switch U4 and the body (legs path: X0 = LF_FORE, Y0 = RF_FORE) ----
    u4 = d.add(elm.Ic(pins=[elm.IcPin(name="X", side="left", slot="2/2"), elm.IcPin(name="Y", side="left", slot="1/2"),
                            elm.IcPin(name="X0", side="right", slot="2/2"), elm.IcPin(name="Y0", side="right", slot="1/2")],
                      pinspacing=1.8, edgepadW=1.8, leadlen=0.6, label="U4\n74HC4052\ncurrent pair", lblsize=10).right()
               .at((r4.end[0] + 1.0, yo)).anchor("X"))
    X, Yp, X0, Y0 = (u4.absanchors[k] for k in ("X", "Y", "X0", "Y0"))
    L(d, r4.end, X)
    d += elm.Label().at((X[0] + 1.6, Yp[1] - 1.5)).label("S0 GPIO33, S1 GPIO27\nX1-3 / Y1-3: arms, sides", fontsize=8)
    xb = X0[0] + 3.2                                           # the body column
    top = X0[1]
    L(d, X0, (xb, top))
    d += elm.Label().at((xb - 1.5, top + 0.35)).label("LF_FORE plate", fontsize=8)
    rcl = d.add(elm.Resistor().at((xb, top)).down(1.8).label("Rc 1 k skin", loc="top", fontsize=8))
    A = rcl.end
    d += elm.Dot().at(A)
    lleg = d.add(elm.RBox(w=1.0, h=0.5).at(A).down().label("left leg\nRe ‖ (Ri+Cm)", loc="bottom", fontsize=8))
    d += elm.Dot().at(lleg.end).label("pelvis", loc="left", fontsize=8)
    rleg = d.add(elm.RBox(w=1.0, h=0.5).at(lleg.end).down().label("right leg\nRe ‖ (Ri+Cm)", loc="bottom", fontsize=8))
    B = rleg.end
    d += elm.Dot().at(B)
    rcr = d.add(elm.Resistor().at(B).down(1.8).label("Rc 1 k skin", loc="top", fontsize=8))
    bot = rcr.end[1]
    L(d, Y0, (xb - 1.2, Y0[1]), (xb - 1.2, bot), (xb, bot))
    d += elm.Label().at((xb - 2.7, bot - 0.35)).label("RF_FORE plate", fontsize=8)
    # ---- return: U4 Y -> C4 -> RET -> R5 -> NCAL -> Rcal (0.1 %) -> VREF ----
    yr = bot - 2.8
    L(d, Yp, (Yp[0] - 0.8, Yp[1]), (Yp[0] - 0.8, yr))
    c4 = d.add(elm.Capacitor().at((Yp[0] - 0.8, yr)).right().label("C4 1 µF DC block", loc="bottom"))
    d += elm.Dot().at(c4.end).label("RET", loc="top")
    r5 = d.add(elm.Resistor().at(c4.end).right().label("R5 120", loc="bottom"))
    d += elm.Dot().at(r5.end).label("NCAL", loc="top")
    rc = d.add(elm.Resistor().at(r5.end).right().label("Rcal 100 Ω 0.1 %", loc="bottom").color(GREEN))
    L(d, rc.end, (rc.end[0] + 0.7, rc.end[1])); vref(d, (rc.end[0] + 0.7, rc.end[1]), up=True)
    d += elm.Label().at((c4.start[0], yr - 1.5)).label(
        "RTAP = NCAL or RET (U3 switch C, GPIO12): the reference across Rcal, or across R5 + Rcal for the self-check (ratio 2.2)",
        fontsize=8, halign="left", color=GREEN)
    # ---- 3. sense pair U5 (LF_HEEL, RF_HEEL) -> 1 k protection -> 10 M bias to VREF ----
    hl = d.add(elm.Resistor().at(A).right(2.8).label("Rc 1 k (LF_HEEL)", fontsize=8))
    hr = d.add(elm.Resistor().at(B).right(2.8).label("Rc 1 k (RF_HEEL)", loc="bottom", fontsize=8))
    u5 = d.add(elm.Ic(pins=[elm.IcPin(name="X0", side="left", slot="2/2"), elm.IcPin(name="Y0", side="left", slot="1/2"),
                            elm.IcPin(name="X", side="right", slot="2/2"), elm.IcPin(name="Y", side="right", slot="1/2")],
                      pinspacing=A[1] - B[1], edgepadW=1.6, leadlen=0.6, label="U5\n74HC4052\nsense pair", lblsize=10).right()
               .at((hl.end[0] + 0.5, hl.end[1])).anchor("X0"))
    L(d, hl.end, u5.absanchors["X0"]); L(d, hr.end, u5.absanchors["Y0"])
    r6 = d.add(elm.Resistor().at(u5.absanchors["X"]).right().label("R6 1 k"))
    r7 = d.add(elm.Resistor().at(u5.absanchors["Y"]).right().label("R7 1 k", loc="bottom"))
    sa, sb = r6.end, r7.end
    L(d, sa, (sa[0] + 2.0, sa[1])); L(d, sb, (sb[0] + 2.0, sb[1]))
    d += elm.Dot().at((sa[0] + 0.9, sa[1])).label("SA", loc="top"); d += elm.Dot().at((sb[0] + 0.9, sb[1])).label("SB", loc="top")
    r8 = d.add(elm.Resistor().at((sa[0] + 0.9, sa[1])).down(1.7).label("R8 10 M", loc="bottom", fontsize=9)); vref(d, r8.end)
    r9 = d.add(elm.Resistor().at((sb[0] + 0.9, sb[1])).down(1.7).label("R9 10 M", loc="bottom", fontsize=9)); vref(d, r9.end)
    tp(d, (sa[0] + 0.3, sa[1]), "TP4 = SA - SB", "bottom")
    # ---- 4. select: U3 74HC4053 (A: SA or RTAP, B: SB or VREF) -> INA126 (G = 10) -> 1.5 k / 10 n -> ESP32 ADC ----
    u3 = d.add(elm.Ic(pins=[elm.IcPin(name="A0", side="left", slot="4/4"), elm.IcPin(name="A1", side="left", slot="3/4"),
                            elm.IcPin(name="B1", side="left", slot="2/4"), elm.IcPin(name="B0", side="left", slot="1/4"),
                            elm.IcPin(name="A", side="right", slot="4/4"), elm.IcPin(name="B", side="right", slot="1/4")],
                      pinspacing=(sa[1] - sb[1]) / 3, edgepadW=1.8, leadlen=0.6, label="U3\n74HC4053\nSEL GPIO18", lblsize=10).right()
               .at((sa[0] + 3.6, sa[1])).anchor("A0"))
    L(d, (sa[0] + 2.0, sa[1]), u3.absanchors["A0"]); L(d, (sb[0] + 2.0, sb[1]), u3.absanchors["B0"])
    a1, b1 = u3.absanchors["A1"], u3.absanchors["B1"]
    L(d, a1, (a1[0] - 0.5, a1[1])); d += elm.Label().at((a1[0] - 0.6, a1[1])).label("RTAP", halign="right", fontsize=9, color=GREEN)
    L(d, b1, (b1[0] - 0.5, b1[1])); d += elm.Label().at((b1[0] - 0.6, b1[1])).label("VREF", halign="right", fontsize=9)
    ua, ub = u3.absanchors["A"], u3.absanchors["B"]
    mid = (ua[1] + ub[1]) / 2
    ina = d.add(elm.Opamp().right().flip().at((ua[0] + 2.0, mid - 0.625)).anchor("in1")
                .label("U2 INA126\nG = 10\nRG 16 k", loc="center", ofst=(-0.35, 0), fontsize=9))
    L(d, ua, (ua[0] + 1.0, ua[1]), (ua[0] + 1.0, ina.in2[1]), ina.in2)
    L(d, ub, (ub[0] + 0.6, ub[1]), (ub[0] + 0.6, ina.in1[1]), ina.in1)
    L(d, ina.out, (ina.out[0] + 0.6, ina.out[1]))
    tp(d, (ina.out[0] + 0.6, ina.out[1]), "TP5 / TP7")
    r11 = d.add(elm.Resistor().at((ina.out[0] + 0.6, ina.out[1])).right().label("R11 1.5 k", loc="bottom"))
    tp(d, r11.end, "TP6")
    c5 = d.add(elm.Capacitor().at(r11.end).down(1.8).label("C5 10 n", loc="bottom")); d += elm.Ground().at(c5.end)
    L(d, r11.end, (r11.end[0] + 1.2, r11.end[1]))
    d += elm.Dot().at((r11.end[0] + 1.2, r11.end[1])).label("ESP32 ADC\nGPIO35", loc="top", fontsize=10)
    d += elm.Label().at((ua[0] - 0.2, sb[1] - 2.2)).label(
        "ESP32: DMA 200 kS/s, Goertzel at 5 / 20 / 50 kHz\nZ = Rcal × |TP5| / |TP7|  (amplifier gain and current cancel)",
        fontsize=10, halign="left", color="#e67700")
    # ---- stage frames + safety note ----
    hi = top + 2.2
    frame(d, (-3.8, r3.end[1] - 1.2, r4.end[0] + 0.5, hi), "1  Current source (100 µA)", "#1864ab")
    frame(d, (X[0] - 0.6, bot - 1.0, xb + 1.7, hi), "2  Path switch + body (legs path)", "#c92a2a")
    frame(d, (c4.start[0] - 0.4, yr - 2.1, rc.end[0] + 1.2, yr + 1.5), "Reference chain (self-calibrating)", GREEN)
    frame(d, (xb + 1.9, r9.end[1] - 1.0, sa[0] + 2.4, hi), "3  Sense pair + 10 MΩ bias", "#5f3dc4")
    frame(d, (sa[0] + 2.6, r9.end[1] - 1.0, r11.end[0] + 2.6, hi), "4  Select + INA126 + anti-alias", "#e67700")
    d += elm.Label().at((-3.8, yr - 3.2)).label(
        "Patient safety (IEC 60601-1 type BF, LTspice): C3 and C4 in series block DC; R4 limits the current; every single fault stays ≥ 12.8× under the limit.  "
        "CHARGE / USE switch (SW6) cuts both charger wires while measuring: leakage 0.19 µA instead of 339 µA.", fontsize=9, halign="left", color="#555")
    d.draw()
    return d


def waveforms(fig, cells):
    w = np.load(ROOT / "sim" / "circuit" / "testpoints.npz")
    items = [("TP1", "DAC out", "V"), ("TP2", "buffer out", "V"), ("TP3", "current through the body", "µA"),
             ("TP4", "voltage across the legs", "mV"), ("TP5", "INA126 out (body)", "V"), ("TP6", "ADC pin", "V"),
             ("TP7", "INA126 out (Rcal)", "V")]
    for cell, (k, title, unit) in zip(cells, items):
        ax = fig.add_subplot(cell); y = w[k]
        ax.plot(w["t_ms"], y, color=TPC if k != "TP7" else GREEN, lw=1.4)
        ax.set_title(f"{k}  {title}", fontsize=10, color="#333")
        ax.set_xlabel("ms", fontsize=8); ax.set_ylabel(unit, fontsize=8)
        ax.tick_params(labelsize=7); ax.grid(alpha=0.3)
        ax.text(0.02, 0.04, f"±{(y.max() - y.min()) / 2:.3g} {unit}", transform=ax.transAxes, fontsize=9, color="#333",
                bbox=dict(fc="white", ec="none", alpha=0.8))
    return w


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(23.4, 16.5))                # A3 landscape
    gs = fig.add_gridspec(2, 7, height_ratios=[3.6, 1], hspace=0.22, wspace=0.35, left=0.03, right=0.98, top=0.91, bottom=0.05)
    ax = fig.add_subplot(gs[0, :]); ax.axis("off")
    schematic(ax)
    w = waveforms(fig, [gs[1, i] for i in range(7)])
    z = 100 * (w["TP5"].max() - w["TP5"].min()) / (w["TP7"].max() - w["TP7"].min())
    fig.suptitle("HridayMitra custom hardware: 8-electrode bioimpedance front end + ESP32 (legs path shown)", fontsize=20, x=0.03, ha="left", y=0.975)
    fig.text(0.03, 0.935, f"Bottom row: LTspice at each test point (legs path, 5 kHz, 1 kΩ skin contacts). Result: Z = {z:.1f} Ω (exact 578.5 Ω). "
             "Same values as the KiCad schematic (ERC 0) and the LTspice netlists. Monitoring, not diagnosis.", fontsize=12, color="#555")
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"frontend_sheet.{ext}", dpi=110)
    print("wrote", OUT / "frontend_sheet.png", f"Z = {z:.1f} ohm")
