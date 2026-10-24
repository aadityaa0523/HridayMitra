"""KICAD SCHEMATIC FROM CODE: the custom part (impedance front end) + ESP32 + peripherals, as in build guide v3.

Every part and every net is listed once in PARTS below (the same values as the LTspice netlists). The script places the
symbols, gives every pin a short wire with a net label (connection by label name), marks unused pins "not connected",
then runs KiCad's electrical rules check (ERC) and exports a PDF. A second check compares the values with the LTspice
netlist so the schematic and the simulation can never drift apart.
Run:  python tools/make_schematic.py
Out:  hardware/kicad/hridaymitra.kicad_sch (+ .kicad_pro), hardware/kicad/hridaymitra_schematic.pdf, erc.json
"""
import json, math, pathlib, re, subprocess, uuid
from kicad_lib import Symbol

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "hardware" / "kicad"
CLI = r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
G = 2.54
U = lambda: str(uuid.uuid4())

SYM = {k: Symbol(*v) for k, v in {
    "R": ("Device", "R"), "C": ("Device", "C"), "CP": ("Device", "C_Polarized"), "LED": ("Device", "LED"),
    "POT": ("Device", "R_Potentiometer"), "SPK": ("Device", "Speaker"), "BAT": ("Device", "Battery_Cell"),
    "MUX4": ("Analog_Switch", "CD4052B"), "MUX2": ("Analog_Switch", "CD4053B"), "INA": ("Amplifier_Instrumentation", "INA128"),
    "OPA": ("Amplifier_Operational", "LM2904"), "LDO": ("Regulator_Linear", "AP1117-15"), "ESP": ("RF_Module", "ESP32-WROOM-32"),
    "BTN": ("Switch", "SW_Push"), "SPST": ("Switch", "SW_SPST"), "J4": ("Connector_Generic", "Conn_01x04"),
    "J5": ("Connector_Generic", "Conn_01x05"), "J6": ("Connector_Generic", "Conn_01x06"), "J8": ("Connector_Generic", "Conn_01x08"),
    "FLAG": ("power", "PWR_FLAG"), "NPN": ("Device", "Q_NPN"), "D": ("Device", "D"), "MOT": ("Motor", "Motor_DC")}.items()}

# (block, ref, symbol, value, unit, {pin number: net}). Pins not listed are marked "not connected".
# Pin-compatible stand-ins: INA128 symbol = INA126 (same 8-pin pinout), CD4052B = 74HC4052, CD4053B = 74HC4053,
# LM2904 = MCP6002 (same dual op-amp pinout), AP1117 = the 3.3 V regulator already on the ESP32 DevKit board.
FE, MCU, PER, PWR = "Impedance front end (custom circuit)", "ESP32 DevKit (WROOM-32)", "Sensors, user interface, SMS", "Power (battery only while measuring)"
PARTS = [
    (FE, "R1", "R", "10k 1%", 1, {"1": "+3V3", "2": "VREF_IN"}),
    (FE, "R2", "R", "10k 1%", 1, {"1": "VREF_IN", "2": "GND"}),
    (FE, "C1", "C", "10u", 1, {"1": "VREF_IN", "2": "GND"}),
    (FE, "U1", "OPA", "MCP6002", 1, {"3": "VREF_IN", "2": "VREF", "1": "VREF"}),
    (FE, "U1", "OPA", "MCP6002", 2, {"5": "EXC_IN", "6": "EXC_OUT", "7": "EXC_OUT"}),
    (FE, "U1", "OPA", "MCP6002", 3, {"8": "+3V3", "4": "GND"}),
    (FE, "C2", "C", "1u", 1, {"1": "DAC_EXC", "2": "EXC_IN"}),
    (FE, "R3", "R", "100k", 1, {"1": "EXC_IN", "2": "VREF"}),
    (FE, "C3", "C", "1u", 1, {"1": "EXC_OUT", "2": "N1"}),
    (FE, "R4", "R", "4.7k 1%", 1, {"1": "N1", "2": "I_SRC"}),
    (FE, "U4", "MUX4", "74HC4052 (current pair)", 1, {"13": "I_SRC", "12": "LF_FORE", "14": "LH_OUT", "15": "RH_OUT", "11": "LH_OUT",
        "3": "I_SNK", "1": "RF_FORE", "5": "RH_OUT", "2": "RF_FORE", "4": "LF_FORE", "10": "PATH_S0", "9": "PATH_S1",
        "6": "GND", "7": "GND", "8": "GND", "16": "+3V3"}),
    (FE, "C4", "C", "1u", 1, {"1": "I_SNK", "2": "RET"}),
    (FE, "R5", "R", "120", 1, {"1": "RET", "2": "NCAL"}),
    (FE, "R22", "R", "100 0.1% (Rcal)", 1, {"1": "NCAL", "2": "VREF"}),
    (FE, "R6", "R", "1k", 1, {"1": "LF_HEEL_E", "2": "LF_HEEL"}),
    (FE, "R7", "R", "1k", 1, {"1": "RF_HEEL_E", "2": "RF_HEEL"}),
    (FE, "R12", "R", "1k", 1, {"1": "LH_IN_E", "2": "LH_IN"}),
    (FE, "R13", "R", "1k", 1, {"1": "RH_IN_E", "2": "RH_IN"}),
    (FE, "U5", "MUX4", "74HC4052 (sense pair)", 1, {"13": "SA", "12": "LF_HEEL", "14": "LH_IN", "15": "RH_IN", "11": "LH_IN",
        "3": "SB", "1": "RF_HEEL", "5": "RH_IN", "2": "RF_HEEL", "4": "LF_HEEL", "10": "PATH_S0", "9": "PATH_S1",
        "6": "GND", "7": "GND", "8": "GND", "16": "+3V3"}),
    (FE, "R8", "R", "10M", 1, {"1": "SA", "2": "VREF"}),
    (FE, "R9", "R", "10M", 1, {"1": "SB", "2": "VREF"}),
    (FE, "U3", "MUX2", "74HC4053 (body / reference / self-cal)", 1, {"14": "INA_P", "12": "SA", "13": "RTAP", "15": "INA_N", "2": "SB",
        "1": "VREF", "11": "SEL", "10": "SEL", "4": "RTAP", "5": "RET", "3": "NCAL", "9": "CAL_SEL",
        "6": "GND", "7": "GND", "8": "GND", "16": "+3V3"}),
    (FE, "U2", "INA", "INA126", 1, {"3": "INA_P", "2": "INA_N", "1": "RG1", "8": "RG2", "5": "VREF", "6": "INA_OUT",
        "7": "+3V3", "4": "GND"}),
    (FE, "R10", "R", "16k (15k+1k)", 1, {"1": "RG1", "2": "RG2"}),
    (FE, "R11", "R", "1.5k", 1, {"1": "INA_OUT", "2": "Z_ADC"}),
    (FE, "C5", "C", "10n", 1, {"1": "Z_ADC", "2": "GND"}),
    (FE, "J1", "J8", "Electrodes: 4 foot plates + 4 hand strips", 1, {"1": "LF_FORE", "2": "LF_HEEL_E", "3": "RF_FORE",
        "4": "RF_HEEL_E", "5": "LH_OUT", "6": "LH_IN_E", "7": "RH_OUT", "8": "RH_IN_E"}),
] + [(FE, f"C{n}", "C", "100n", 1, {"1": "+3V3", "2": "GND"}) for n in (6, 7, 8, 9, 13)] + [
    (MCU, "U6", "ESP", "ESP32-WROOM-32 (DevKit)", 1, {"2": "+3V3", "1": "GND", "10": "DAC_EXC", "7": "Z_ADC", "30": "SEL",
        "9": "PATH_S0", "12": "PATH_S1", "8": "HX_DT", "13": "HX_SCK", "11": "VOICE_DAC", "33": "SDA", "36": "SCL",
        "6": "ECG_OUT", "5": "ECG_LOP", "4": "DRAWER", "31": "VIBRA", "16": "LED_G", "37": "LED_A", "24": "LED_R", "26": "BTN_G",
        "29": "BTN_R", "23": "BTN_SOS", "14": "CAL_SEL", "28": "GSM_TX", "27": "GSM_RX", "3": "EN"}),
    (MCU, "R19", "R", "10k (on DevKit)", 1, {"1": "+3V3", "2": "EN"}),
    (PER, "D1", "LED", "green", 1, {"2": "LED_G", "1": "LED_G_K"}),
    (PER, "R14", "R", "220", 1, {"1": "LED_G_K", "2": "GND"}),
    (PER, "D2", "LED", "amber", 1, {"2": "LED_A", "1": "LED_A_K"}),
    (PER, "R15", "R", "220", 1, {"1": "LED_A_K", "2": "GND"}),
    (PER, "D3", "LED", "red", 1, {"2": "LED_R", "1": "LED_R_K"}),
    (PER, "R16", "R", "220", 1, {"1": "LED_R_K", "2": "GND"}),
    (PER, "SW1", "BTN", "green button", 1, {"1": "BTN_G", "2": "GND"}),
    (PER, "SW2", "BTN", "red button", 1, {"1": "BTN_R", "2": "GND"}),
    (PER, "SW3", "BTN", "SOS button", 1, {"1": "BTN_SOS", "2": "GND"}),
    (PER, "J2", "J4", "MAX30102 module (finger)", 1, {"1": "+3V3", "2": "GND", "3": "SCL", "4": "SDA"}),
    (PER, "J3", "J4", "HX711 module: VCC GND DT SCK", 1, {"1": "+3V3", "2": "GND", "3": "HX_DT", "4": "HX_SCK"}),
    (PER, "J4", "J4", "HX711 module: E+ E- A- A+", 1, {"1": "LC_EP", "2": "LC_EN", "3": "LC_AN", "4": "LC_AP"}),
    (PER, "J5", "J4", "4 load cells as one bridge", 1, {"1": "LC_EP", "2": "LC_EN", "3": "LC_AN", "4": "LC_AP"}),
    (PER, "C11", "C", "1u", 1, {"1": "VOICE_DAC", "2": "VOICE_AC"}),
    (PER, "RV1", "POT", "10k volume", 1, {"1": "VOICE_AC", "2": "AMP_IN", "3": "GND"}),
    (PER, "J6", "J6", "PAM8403 module: 5V GND LIN RIN L+ L-", 1, {"1": "+5V", "2": "GND", "3": "AMP_IN", "4": "GND",
        "5": "SPK_P", "6": "SPK_N"}),
    (PER, "LS1", "SPK", "4 ohm 3 W", 1, {"1": "SPK_P", "2": "SPK_N"}),
    (PER, "R17", "R", "1k", 1, {"1": "GSM_TX", "2": "GSM_RXD"}),
    (PER, "R18", "R", "2.2k", 1, {"1": "GSM_RXD", "2": "GND"}),
    (PER, "J8", "J4", "SIM800L module: VCC GND TXD RXD", 1, {"1": "VBAT", "2": "GND", "3": "GSM_RX", "4": "GSM_RXD"}),
    (PER, "C12", "CP", "1000u", 1, {"1": "VBAT", "2": "GND"}),
    (PER, "J11", "J5", "AD8232 (optional; off for pacemaker/ICD; LO- unused)", 1, {"1": "+3V3", "2": "GND", "3": "ECG_OUT",
        "4": "ECG_LOP"}),
    (PER, "R21", "R", "1k", 1, {"1": "VIBRA", "2": "VIB_B"}),
    (PER, "Q1", "NPN", "2N2222 (vibration driver)", 1, {"B": "VIB_B", "C": "VIB_C", "E": "GND"}),
    (PER, "M1", "MOT", "coin vibration motor (seat)", 1, {"1": "+5V", "2": "VIB_C"}),
    (PER, "D4", "D", "1N4148 flyback", 1, {"1": "+5V", "2": "VIB_C"}),
    (PER, "R20", "R", "10k", 1, {"1": "+3V3", "2": "DRAWER"}),
    (PER, "SW5", "BTN", "tablet-drawer microswitch", 1, {"1": "DRAWER", "2": "GND"}),
    (PWR, "BT1", "BAT", "18650 (protected)", 1, {"1": "BAT_P", "2": "GND"}),
    (PWR, "J9", "J4", "TP4056 module: B+ B- OUT+ OUT-", 1, {"1": "BAT_P", "2": "GND", "3": "VBAT_RAW", "4": "GND"}),
    (PWR, "SW4", "SPST", "power switch", 1, {"1": "VBAT_RAW", "2": "VBAT"}),
    (PWR, "J10", "J4", "MT3608 module: IN+ IN- OUT+ OUT-", 1, {"1": "VBAT", "2": "GND", "3": "+5V", "4": "GND"}),
    (PWR, "U7", "LDO", "3.3 V LDO (on DevKit)", 1, {"3": "+5V", "1": "GND", "2": "+3V3"}),
    (PWR, "C10", "C", "10u", 1, {"1": "+3V3", "2": "GND"}),
    (PWR, "#FLG1", "FLAG", "PWR_FLAG", 1, {"1": "GND"}),
    (PWR, "#FLG2", "FLAG", "PWR_FLAG", 1, {"1": "VBAT"}),
    (PWR, "#FLG3", "FLAG", "PWR_FLAG", 1, {"1": "+5V"}),
]


def snap(v):
    return round(v / G) * G


def pins_of(sym, unit):
    return [p for p in sym.pins if p["unit"] in (0, unit) and not p["hidden"]]


def side_text(sym, unit):
    """Small vertical parts (R, C, pot) get their name and value on the right, like KiCad does by default."""
    ps = pins_of(sym, unit)
    return len(ps) <= 3 and all(p["angle"] in (90.0, 270.0) for p in ps)


def extent(sym, unit, nets, ref="", val=""):
    """Bounding box of a placed symbol in schematic units, including stubs, labels and its name/value text."""
    xs, ys = [], []
    for p in pins_of(sym, unit):
        lab = 2 * G + 1.1 * len(nets.get(p["number"], "")) + 1
        dx, dy = -round(math.cos(math.radians(p["angle"]))), round(math.sin(math.radians(p["angle"])))
        xs += [p["x"], p["x"] + dx * lab]; ys += [-p["y"], -p["y"] + dy * lab]
    a, b, c, d = (min(xs) - G, max(xs) + G, min(ys) - 2 * G, max(ys) + 2 * G) if xs else (-5, 5, -5, 5)
    if side_text(sym, unit):
        b = max(b, G + 1.0 * max(len(ref), len(val)) + 2)
    else:
        half = 0.55 * max(len(val), len(ref))
        a, b = min(a, -half), max(b, half)
    return a, b, c, d


def place(parts, x0, y0, width):
    """Pack parts left to right in rows inside [x0, x0+width]. Returns positions and the bottom y."""
    pos, x, y, row_h = {}, x0, y0, 0
    for i, (blk, ref, s, val, unit, nets) in enumerate(parts):
        a, b, c, d = extent(SYM[s], unit, nets, ref, val)
        w, h = b - a + 4 * G, d - c + 2 * G
        if x + w > x0 + width and x > x0:
            x, y, row_h = x0, y + row_h, 0
        pos[i] = (snap(x - a), snap(y - c))
        x += w; row_h = max(row_h, h)
    return pos, y + row_h


def sexpr_symbol(ref, s, val, unit, at, root):
    sym = SYM[s]
    x, y = at
    a, b, c, d = extent(sym, unit, {})
    power = ref.startswith("#")
    if side_text(sym, unit):
        rx, ry, vx, vy, just = x + G, y - 1.27, x + G, y + 1.27, "(justify left)"
    else:
        rx, ry, vx, vy, just = x, y + c - 1, x, y + d + 1, ""
    pins = "".join(f'\n\t\t(pin "{p["number"]}" (uuid "{U()}"))' for p in sym.pins if p["unit"] in (0, unit))
    hide = "(hide yes)"
    return f'''\t(symbol (lib_id "{sym.lib_id}") (at {x:.2f} {y:.2f} 0) (unit {unit})
\t\t(exclude_from_sim no) (in_bom {"no" if power else "yes"}) (on_board {"no" if power else "yes"}) (dnp no) (uuid "{U()}")
\t\t(property "Reference" "{ref}" (at {x:.2f} {y + c - 1:.2f} 0) (effects (font (size 1.27 1.27)) {hide if power else ""}))
\t\t(property "Value" "{val}" (at {x:.2f} {y + d + 1:.2f} 0) (effects (font (size 1.27 1.27)) {hide if power else ""}))
\t\t(property "Footprint" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) {hide}))
\t\t(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) {hide})){pins}
\t\t(instances (project "hridaymitra" (path "/{root}" (reference "{ref}") (unit {unit}))))
\t)'''


def connections(s, unit, nets, at):
    """Wire stub + label for every used pin, a no-connect flag for every unused one."""
    import math
    out, x0, y0 = [], *at
    for p in pins_of(SYM[s], unit):
        px, py = x0 + p["x"], y0 - p["y"]
        net = nets.get(p["number"])
        if net is None:
            if SYM[s].lib_id != "power:PWR_FLAG":
                out.append(f'\t(no_connect (at {px:.2f} {py:.2f}) (uuid "{U()}"))')
            continue
        dx, dy = -round(math.cos(math.radians(p["angle"]))), round(math.sin(math.radians(p["angle"])))
        ex, ey = px + dx * G, py + dy * G
        ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[(dx, dy)]
        just = "left" if ang in (0, 90) else "right"
        out.append(f'\t(wire (pts (xy {px:.2f} {py:.2f}) (xy {ex:.2f} {ey:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
        out.append(f'\t(label "{net}" (at {ex:.2f} {ey:.2f} {ang}) (fields_autoplaced yes) '
                   f'(effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid "{U()}"))')
    return out


def build():
    root = U()
    blocks = [FE, MCU, PER, PWR]
    layout = {FE: (20, 30, 550), MCU: (20, None, 150), PER: (185, None, 385), PWR: (20, None, 550)}
    body, positions, y = [], {}, 30
    for blk in blocks:
        x0, _, w = layout[blk]
        if blk == PER:
            y_blk = y_mcu
        else:
            y_blk = y
        parts = [(i, p) for i, p in enumerate(PARTS) if p[0] == blk]
        pos, bottom = place([p for _, p in parts], x0, y_blk + 8, w)
        for k, (i, _) in enumerate(parts):
            positions[i] = pos[k]
        body.append(f'\t(text "{blk}" (exclude_from_sim no) (at {x0:.2f} {y_blk + 3:.2f} 0) '
                    f'(effects (font (size 2.54 2.54) (bold yes)) (justify left bottom)) (uuid "{U()}"))')
        if blk == FE:
            y = bottom + 12; y_mcu = y
        elif blk == MCU:
            mcu_bottom = bottom
        elif blk == PER:
            y = max(bottom, mcu_bottom) + 12
        else:
            y = bottom
    for i, (blk, ref, s, val, unit, nets) in enumerate(PARTS):
        body.append(sexpr_symbol(ref, s, val, unit, positions[i], root))
        body += connections(s, unit, nets, positions[i])
    notes = ["Monitoring, not diagnosis. Battery power only while a person touches the electrodes; never test on anyone with a pacemaker or ICD.",
             "Z = R5 x V(body) / V(R5): the gain cancels. Paths (S1 S0): 00 legs, 01 arms, 10 right side, 11 left side. Trunk = (Z3 + Z4 - Z1 - Z2) / 2.",
             "R8/R9 = 10 Mohm (LTspice Monte Carlo: 1 Mohm gave up to 12 % error). Firmware reads the 5 kHz Goertzel amplitude, never peak-to-peak (mains hum).",
             "Pin-compatible symbols: INA128 symbol used for INA126, CD4052B/CD4053B for 74HC4052/74HC4053, LM2904 for MCP6002."]
    for k, n in enumerate(notes):
        body.append(f'\t(text "{n}" (exclude_from_sim no) (at 25 {y + 8 + 5 * k:.2f} 0) '
                    f'(effects (font (size 1.8 1.8)) (justify left bottom)) (uuid "{U()}"))')
    libs = "\n".join("\t\t" + SYM[k].raw.replace("\n", "\n\t\t") for k in sorted({p[2] for p in PARTS}))
    height = y + 8 + 5 * len(notes) + 20
    paper = f"User {600} {int(height + 25)}"           # page sized to the drawing (title block needs ~25 mm)
    return f'''(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid "{root}") (paper "User" {paper.split()[1]} {paper.split()[2]})
\t(title_block (title "HridayMitra stool: impedance front end + ESP32") (date "2026-10-24") (rev "v3.1 (R8/R9 10M)")
\t\t(company "Transfinitte hardware track") (comment 1 "Generated by tools/make_schematic.py from the same values as the LTspice netlists")
\t\t(comment 2 "Monitoring, not diagnosis"))
\t(lib_symbols
{libs}
\t)
{chr(10).join(body)}
\t(sheet_instances (path "/" (page "1")))
\t(embedded_fonts no)
)
''', paper


def check_against_ltspice():
    """Values that exist in both the schematic and sim/circuit/trunk_paths.py must be equal."""
    net = (ROOT / "sim/circuit/trunk_paths.py").read_text()
    want = {"R3": "100k", "R4": "4.7k", "R5": "120", "R6": "1k", "R7": "1k", "R8": "10Meg", "R9": "10Meg",
            "C2": "1u", "C3": "1u", "C4": "1u", "R11": "1.5k", "C5": "10n"}
    sch = {p[1]: p[3].split()[0].replace("M", "Meg") for p in PARTS}
    bad = []
    for ref, v in want.items():
        in_spice = re.search(rf'"{ref} \S+ \S+ ([^"\s]+)"', net) or re.search(rf"\b{ref} \S+ \S+ (\S+)", net)
        spice_v = in_spice.group(1) if in_spice else None
        if sch.get(ref) != v or spice_v != v:
            bad.append((ref, "schematic", sch.get(ref), "ltspice", spice_v, "expected", v))
    if sch.get("R22") != "100" or '"Rcal ncal vref 100"' not in net:     # precision reference: R22 in KiCad, Rcal in LTspice
        bad.append(("R22/Rcal", sch.get("R22"), "expected 100"))
    return bad


# build guide v3, section 5: (S1, S0) -> current in, current out, sense +, sense -
PATH_TABLE = {(0, 0): ("LF_FORE", "RF_FORE", "LF_HEEL", "RF_HEEL"), (0, 1): ("LH_OUT", "RH_OUT", "LH_IN", "RH_IN"),
              (1, 0): ("RH_OUT", "RF_FORE", "RH_IN", "RF_HEEL"), (1, 1): ("LH_OUT", "LF_FORE", "LH_IN", "LF_HEEL")}


def netlist_nets(path):
    """{net name: set of 'REF.pin'} from a KiCad s-expression netlist."""
    from kicad_lib import parse
    tree = parse(path.read_text(encoding="utf8"))[0][0]
    nets = {}
    for n in next(x for x in tree if isinstance(x, list) and x[0] == "nets")[1:]:
        name = next(x for x in n if isinstance(x, list) and x[0] == "name")[1].strip("/")
        nets[name] = {f"{next(y for y in m if y[0] == 'ref')[1]}.{next(y for y in m if y[0] == 'pin')[1]}"
                      for m in n if isinstance(m, list) and m[0] == "node"}
    return nets


def check_paths(nets):
    """For every select code, follow the 74HC4052 channels in the NETLIST and compare with the guide's path table."""
    of = {pin: name for name, pins in nets.items() for pin in pins}
    xch, ych = {0: "12", 1: "14", 2: "15", 3: "11"}, {0: "1", 1: "5", 2: "2", 3: "4"}      # CD4052B X0-X3, Y0-Y3 pins
    assert of["U4.10"] == of["U5.10"] == "PATH_S0" and of["U4.9"] == of["U5.9"] == "PATH_S1"
    assert of["U4.13"] == "I_SRC" and of["U4.3"] == "I_SNK" and of["U5.13"] == "SA" and of["U5.3"] == "SB"
    bad = []
    for (s1, s0), want in PATH_TABLE.items():
        ch = 2 * s1 + s0                                      # B = S1 (GPIO27), A = S0 (GPIO33)
        got = (of[f"U4.{xch[ch]}"], of[f"U4.{ych[ch]}"], of[f"U5.{xch[ch]}"], of[f"U5.{ych[ch]}"])
        sense = tuple(g.replace("_E", "") for g in got[2:])
        same_limb = got[0][:2] == sense[0][:2] and got[1][:2] == sense[1][:2]   # 4-electrode rule: sense on the current limbs
        if got != want or not same_limb:
            bad.append(((s1, s0), got, want))
    return bad


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    text, paper = build()
    sch = OUT / "hridaymitra.kicad_sch"
    sch.write_text(text, encoding="utf8")
    (OUT / "hridaymitra.kicad_pro").write_text(json.dumps({"meta": {"filename": "hridaymitra.kicad_pro", "version": 1}}), encoding="utf8")
    r = subprocess.run([CLI, "sch", "erc", "--format", "json", "--severity-all", "-o", str(OUT / "erc.json"), str(sch)],
                       capture_output=True, text=True)
    print(r.stdout.strip()[-400:], r.stderr.strip()[-400:])
    erc = json.loads((OUT / "erc.json").read_text())
    viol = [v for s in erc.get("sheets", []) for v in s.get("violations", [])]
    print(f"paper {paper}; ERC violations: {len(viol)}")
    for v in viol[:25]:
        print("  ", v["severity"], v["type"], "|", v["description"], "|", [i.get("description") for i in v.get("items", [])][:2])
    subprocess.run([CLI, "sch", "export", "pdf", "-o", str(OUT / "hridaymitra_schematic.pdf"), str(sch)], capture_output=True)
    bad = check_against_ltspice()
    print("values match LTspice:", "yes" if not bad else bad)
    subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", str(OUT / "hridaymitra.net"), str(sch)],
                   capture_output=True)
    nets = netlist_nets(OUT / "hridaymitra.net")
    wrong = check_paths(nets)
    print(f"netlist: {len(nets)} nets; electrode paths match the guide's table:", "yes (all 4)" if not wrong else wrong)
