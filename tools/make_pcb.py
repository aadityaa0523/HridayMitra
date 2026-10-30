"""PCB LAYOUT (Rev A draft) for the custom part: impedance front end + ESP32, from the schematic's netlist.

Reads hardware/kicad/hridaymitra.net (exported by tools/make_schematic.py's KiCad 9 schematic), gives every part a
footprint, places the parts by function (analog front end / ESP32 / power / user interface / module headers), makes a
2-layer 140 x 100 mm board, and writes a Specctra DSN for autorouting. With a routed .ses it adds the tracks and vias,
pours ground on both layers and runs DRC.

Needs KiCad 7+ (its pcbnew Python module and footprint library) and Java 17+ for Freerouting:
  python3 tools/make_pcb.py                                   -> hardware/kicad/hridaymitra_pcb.dsn
  java -jar freerouting-1.9.0.jar -de hardware/kicad/hridaymitra_pcb.dsn -do routed.ses -mp 30
  python3 tools/make_pcb.py routed.ses                        -> hardware/kicad/hridaymitra.kicad_pcb + DRC report
Draft for review: not fabricated, not checked by a layout engineer. The ESP32 antenna overhangs the top edge.
"""
import pathlib, re, sys
from collections import Counter, defaultdict
import pcbnew

ROOT = pathlib.Path(__file__).resolve().parents[1]
KI = ROOT / "hardware" / "kicad"
FP = pathlib.Path("/usr/share/kicad/footprints")
MM = pcbnew.FromMM
W, H, OX, OY = 140, 100, 50, 50          # board size and where it sits on the sheet (mm)

FOOTPRINT = {                            # schematic part -> (library, footprint)
    "Device:R": ("Resistor_SMD", "R_0805_2012Metric"),
    "Device:C": ("Capacitor_SMD", "C_0805_2012Metric"),
    "Device:C_Polarized": ("Capacitor_SMD", "CP_Elec_6.3x5.4"),
    "Device:LED": ("LED_SMD", "LED_0805_2012Metric"),
    "Device:D": ("Diode_SMD", "D_SOD-123"),
    "Device:Q_NPN": ("Package_TO_SOT_SMD", "SOT-23"),
    "Device:R_Potentiometer": ("Potentiometer_THT", "Potentiometer_Bourns_3386P_Vertical"),
    "Device:Speaker": ("Connector_JST", "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical"),
    "Motor:Motor_DC": ("Connector_JST", "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical"),
    "Device:Battery_Cell": ("Connector_JST", "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical"),
    "Switch:SW_Push": ("Button_Switch_THT", "SW_PUSH_6mm"),
    "Switch:SW_SPST": ("Button_Switch_THT", "SW_DIP_SPSTx01_Slide_6.7x4.1mm_W7.62mm_P2.54mm_LowProfile"),
    "Switch:SW_DPDT_x2": ("Button_Switch_THT", "SW_CK_JS202011CQN_DPDT_Straight"),
    "Amplifier_Operational:LM2904": ("Package_SO", "SOIC-8_3.9x4.9mm_P1.27mm"),
    "Amplifier_Instrumentation:INA128": ("Package_SO", "SOIC-8_3.9x4.9mm_P1.27mm"),
    "Analog_Switch:CD4052B": ("Package_SO", "SOIC-16_3.9x9.9mm_P1.27mm"),
    "Analog_Switch:CD4053B": ("Package_SO", "SOIC-16_3.9x9.9mm_P1.27mm"),
    "RF_Module:ESP32-WROOM-32": ("RF_Module", "ESP32-WROOM-32"),
    "Regulator_Linear:AP1117-15": ("Package_TO_SOT_SMD", "SOT-223-3_TabPin2"),
}
for n in (2, 4, 5, 6, 8):
    FOOTPRINT[f"Connector_Generic:Conn_01x{n:02d}"] = ("Connector_PinHeader_2.54mm", f"PinHeader_1x{n:02d}_P2.54mm_Vertical")
PIN = {"Device:Q_NPN": {"B": "1", "E": "2", "C": "3"}}      # MMBT2222A SOT-23 pinout

# placement regions (x0, y0, x1, y1 in mm inside the board) and the parts that anchor each one
REGION = {"afe": (9, 4, 86, 58), "mcu": (94, 0, 136, 40), "hdr": (86, 44, 136, 64),
          "power": (9, 64, 72, 96), "ui": (74, 68, 136, 96)}
ANCHOR = {"afe": "U1 U2 U3 U4 U5 J1", "mcu": "U6", "power": "U7 BT1 J9 J12 SW4 SW6 C12",
          "ui": "SW1 SW2 SW3 SW5 D1 D2 D3 Q1 D4 M1 LS1 RV1 J6"}


def read_netlist(path):
    s = path.read_text()
    comps = {r: (v, f"{l}:{p}") for r, v, l, p in
             re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\).*?\(libsource \(lib "([^"]+)"\) \(part "([^"]+)"\)', s, re.S)}
    nets = {}
    for name, body in re.findall(r'\(net \(code "\d+"\) \(name "([^"]*)"\)(.*?)(?=\(net \(code|\Z)', s, re.S):
        nets[name] = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', body)
    return comps, nets


def group_of(comps, nets):
    grp = {r: g for g, refs in ANCHOR.items() for r in refs.split()}
    for r, (_, part) in comps.items():
        if r not in grp and part.startswith("Connector_Generic"):
            grp[r] = "hdr"
    touch = defaultdict(Counter)                     # passives follow the anchored part they share most nets with
    for name, nodes in nets.items():
        if name.upper() in ("GND", "+3V3", "+5V", "VBAT") or len(nodes) > 8:
            continue
        refs = {r for r, _ in nodes}
        for r in refs:
            for o in refs - {r}:
                if o in grp:
                    touch[r][grp[o]] += 1
    for r in comps:
        if r not in grp:
            grp[r] = touch[r].most_common(1)[0][0] if touch[r] else "afe"
    return grp


def place(board, fps, grp):
    for g, (x0, y0, x1, y1) in REGION.items():
        items = sorted([f for r, f in fps.items() if grp[r] == g], key=lambda f: -bbox(f)[1])
        x, y, row = x0, y0, 0.0
        for f in items:
            w, h = bbox(f)
            if x + w > x1:
                x, y, row = x0, y + row + 2.0, 0.0
            move_to(f, OX + x, OY + y)
            x, row = x + w + 2.0, max(row, h)
        if y + row > y1:
            print(f"warning: region {g} overflows by {y + row - y1:.1f} mm")


def bbox(f):
    b = f.GetBoundingBox(False, False)
    return pcbnew.ToMM(b.GetWidth()), pcbnew.ToMM(b.GetHeight())


def move_to(f, x, y):                               # top-left of the footprint's courtyard-ish box at (x, y) mm
    b = f.GetBoundingBox(False, False)
    f.Move(pcbnew.VECTOR2I(MM(x) - b.GetX(), MM(y) - b.GetY()))


def build():
    comps, nets = read_netlist(KI / "hridaymitra.net")
    board = pcbnew.BOARD()
    ds = board.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    netobj = {}
    for name in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        netobj[name] = n
    fps = {}
    for r, (val, part) in comps.items():
        if part not in FOOTPRINT:
            continue                                  # PWR_FLAG and similar have no copper
        lib, name = FOOTPRINT[part]
        f = pcbnew.FootprintLoad(str(FP / f"{lib}.pretty"), name)
        f.SetReference(r)
        f.SetValue(val[:24])
        board.Add(f)
        fps[r] = f
    for name, nodes in nets.items():
        for r, pin in nodes:
            if r not in fps:
                continue
            pad_no = PIN.get(comps[r][1], {}).get(pin, pin)
            pads = [p for p in fps[r].Pads() if p.GetNumber() == pad_no]
            if not pads:
                raise SystemExit(f"{r} ({comps[r][1]}) has no pad {pad_no}")
            for p in pads:
                p.SetNet(netobj[name])
    grp = group_of(comps, nets)
    place(board, fps, grp)
    u6 = fps["U6"]                                    # ESP32: antenna end over the top edge, nothing under it
    b = u6.GetBoundingBox(False, False)
    u6.Move(pcbnew.VECTOR2I(MM(OX + W - 4) - b.GetRight(), MM(OY - 6) - b.GetY()))
    edge = pcbnew.PCB_SHAPE(board)
    edge.SetShape(pcbnew.SHAPE_T_RECT)
    edge.SetStart(pcbnew.VECTOR2I(MM(OX), MM(OY)))
    edge.SetEnd(pcbnew.VECTOR2I(MM(OX + W), MM(OY + H)))
    edge.SetLayer(pcbnew.Edge_Cuts)
    edge.SetWidth(MM(0.15))
    board.Add(edge)
    for i, (x, y) in enumerate([(3.5, 3.5), (W - 3.5, H - 3.5), (3.5, H - 3.5), (88, 3.5)]):
        m = pcbnew.FootprintLoad(str(FP / "MountingHole.pretty"), "MountingHole_3.2mm_M3")
        m.SetReference(f"H{i + 1}")
        m.SetPosition(pcbnew.VECTOR2I(MM(OX + x), MM(OY + y)))
        board.Add(m)
    t = pcbnew.PCB_TEXT(board)
    t.SetText("HridayMitra Rev A draft: 8-electrode front end + ESP32 (not fabricated)")
    t.SetPosition(pcbnew.VECTOR2I(MM(OX + 45), MM(OY + H - 2)))
    t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(MM(1.2), MM(1.2)))
    board.Add(t)
    nc = ds.m_NetSettings.m_DefaultNetClass
    nc.SetTrackWidth(MM(0.25))
    nc.SetClearance(MM(0.2))
    nc.SetViaDiameter(MM(0.7))
    nc.SetViaDrill(MM(0.35))
    return board, nets


def add_routes(board, ses):
    s = pathlib.Path(ses).read_text()
    res = float(re.search(r"\(resolution um (\d+)\)", s).group(1))
    k = 1000.0 / res                                  # SES units -> nm
    nets = {n.GetNetname(): n for n in board.GetNetsByName().values()}
    layer = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}
    for name, body in re.findall(r'\(net "?([^"\s()]+)"?\s+(.*?)(?=\(net |\)\s*\)\s*\)\s*$)', s, re.S):
        net = nets.get(name.strip('"'))
        for lay, width, pts in re.findall(r"\(wire\s*\(path (\S+) (\d+)\s+([-\d\s]+)\)", body):
            xy = list(map(float, pts.split()))
            for i in range(0, len(xy) - 2, 2):
                tr = pcbnew.PCB_TRACK(board)
                tr.SetStart(pcbnew.VECTOR2I(int(xy[i] * k), int(-xy[i + 1] * k)))
                tr.SetEnd(pcbnew.VECTOR2I(int(xy[i + 2] * k), int(-xy[i + 3] * k)))
                tr.SetWidth(int(float(width) * k))
                tr.SetLayer(layer[lay])
                if net:
                    tr.SetNet(net)
                board.Add(tr)
        for x, y in re.findall(r"\(via \S+ (-?\d+) (-?\d+)", body):
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pcbnew.VECTOR2I(int(float(x) * k), int(-float(y) * k)))
            v.SetDrill(MM(0.35))
            v.SetWidth(MM(0.7))
            if net:
                v.SetNet(net)
            board.Add(v)
    gnd = board.FindNet("GND")
    for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(lay)
        z.SetNet(gnd)
        z.SetLocalClearance(MM(0.3))
        z.SetMinThickness(MM(0.25))
        o = z.Outline()
        o.NewOutline()
        for x, y in ((0, 0), (W, 0), (W, H), (0, H)):
            o.Append(MM(OX + x), MM(OY + y))
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


if __name__ == "__main__":
    board, _ = build()
    if len(sys.argv) > 1:
        add_routes(board, sys.argv[1])
        out = KI / "hridaymitra.kicad_pcb"
        pcbnew.SaveBoard(str(out), board)
        pcbnew.WriteDRCReport(board, str(KI / "pcb_drc.rpt"), pcbnew.EDA_UNITS_MILLIMETRES, True)
        print("saved", out)
    else:
        pcbnew.SaveBoard(str(KI / "hridaymitra_pcb_unrouted.kicad_pcb"), board)
        print("dsn", pcbnew.ExportSpecctraDSN(board, str(KI / "hridaymitra_pcb.dsn")))
