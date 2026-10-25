"""PCB OF THE CUSTOM PART (HM-HW-004): the 8-electrode bioimpedance AFE as a 2-layer 70 × 50 mm board.
  1. (Python)        export the AFE parts + nets from tools/make_schematic.py (same netlist as the KiCad schematic)
  2. (KiCad Python)  place real footprints in signal-flow order, export Specctra DSN
  3. (Freerouting)   auto-route both layers
  4. (KiCad Python)  import the routes, GND pour on both layers, save; kicad-cli: DRC, Gerbers + drill, 3D render
Run:  python tools/make_pcb.py       Out: hardware/pcb/hridaymitra_afe.kicad_pcb, gerbers/, drc.json, docs/hardware/HM-HW-004_*.png
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PCB = ROOT / "hardware" / "pcb"
KICAD = pathlib.Path(r"C:\Program Files\KiCad\9.0\bin")
FR = pathlib.Path(r"C:\Users\Aadityaa\tools\freerouting")
FP = r"C:\Program Files\KiCad\9.0\share\kicad\footprints"
BOARD_W, BOARD_H, X0, Y0 = 70.0, 50.0, 100.0, 100.0
HOST = {"1": "+3V3", "2": "GND", "3": "DAC_EXC", "4": "Z_ADC", "5": "PATH_S0", "6": "PATH_S1", "7": "SEL", "8": "CAL_SEL"}
FOOT = {"R": ("Resistor_SMD", "R_0805_2012Metric"), "C": ("Capacitor_SMD", "C_0805_2012Metric"),
        "OPA": ("Package_SO", "SOIC-8_3.9x4.9mm_P1.27mm"), "INA": ("Package_SO", "SOIC-8_3.9x4.9mm_P1.27mm"),
        "MUX4": ("Package_SO", "SOIC-16_3.9x9.9mm_P1.27mm"), "MUX2": ("Package_SO", "SOIC-16_3.9x9.9mm_P1.27mm"),
        "J8": ("Connector_JST", "JST_XH_B8B-XH-A_1x08_P2.50mm_Vertical"), "HOST": ("Connector_PinHeader_2.54mm", "PinHeader_1x08_P2.54mm_Vertical")}
# placement in mm from the board's top-left corner (x right, y down), rotation in degrees; signal flows left → right
PLACE = {"J1": (5, 33, 90), "R6": (15, 12, 90), "R7": (15, 18, 90), "R12": (15, 32, 90), "R13": (15, 38, 90),
         "U4": (25, 13, 0), "U5": (25, 37, 0), "C6": (25, 4, 0), "C7": (25, 46, 0),
         "R8": (34, 31, 90), "R9": (34, 37, 90), "U3": (42, 34, 0), "C8": (42, 25, 0),
         "U2": (53, 34, 0), "R10": (53, 41, 0), "C9": (53, 28, 0), "R11": (60, 30, 90), "C5": (60, 37, 90),
         "C2": (33, 6, 0), "R3": (33, 11, 0), "U1": (42, 9, 0), "C13": (42, 3, 0), "C3": (50, 5, 0), "R4": (50, 10, 0),
         "R1": (38, 17, 90), "R2": (42, 17, 90), "C1": (46, 17, 90), "C4": (25, 25, 90), "R5": (30, 22, 90), "R22": (34, 22, 90),
         "J13": (66, 16, 0)}
HOLES = [(3.5, 3.5), (BOARD_W - 3.5, 3.5), (3.5, BOARD_H - 3.5), (BOARD_W - 3.5, BOARD_H - 3.5)]


def export_netlist():
    sys.path.insert(0, str(ROOT / "tools"))
    import make_schematic as S
    parts = {}
    for block, ref, sym, value, unit, pins in S.PARTS:
        if block != S.FE:
            continue
        p = parts.setdefault(ref, dict(sym=sym, value=value, pins={}))
        p["pins"].update(pins)
    parts["J13"] = dict(sym="HOST", value="to ESP32 DevKit", pins=HOST)
    missing = set(parts) - set(PLACE)
    assert not missing, f"no placement for {missing}"
    PCB.mkdir(parents=True, exist_ok=True)
    (PCB / "afe_netlist.json").write_text(json.dumps(parts, indent=1))
    return parts


def build_board(route=False):
    """Runs inside KiCad's Python (pcbnew)."""
    import pcbnew
    parts = json.loads((PCB / "afe_netlist.json").read_text())
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(2)
    ds = b.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetTrackWidth(pcbnew.FromMM(0.25)); nc.SetClearance(pcbnew.FromMM(0.2)); nc.SetViaDiameter(pcbnew.FromMM(0.6)); nc.SetViaDrill(pcbnew.FromMM(0.3))
    mm = lambda x, y: pcbnew.VECTOR2I(pcbnew.FromMM(X0 + x), pcbnew.FromMM(Y0 + y))
    # outline with rounded corners
    r = 2.0
    for (ax_, ay, bx, by) in [(r, 0, BOARD_W - r, 0), (BOARD_W, r, BOARD_W, BOARD_H - r), (BOARD_W - r, BOARD_H, r, BOARD_H), (0, BOARD_H - r, 0, r)]:
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(pcbnew.FromMM(0.1))
        s.SetStart(mm(ax_, ay)); s.SetEnd(mm(bx, by)); b.Add(s)
    for cx, cy, sx, sy in [(r, r, 0, r), (BOARD_W - r, r, BOARD_W - r, 0), (BOARD_W - r, BOARD_H - r, BOARD_W, BOARD_H - r), (r, BOARD_H - r, r, BOARD_H)]:
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(pcbnew.FromMM(0.1))
        s.SetCenter(mm(cx, cy)); s.SetStart(mm(sx, sy)); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T)); b.Add(s)
    nets = {}
    def net(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(b, name); b.Add(n); nets[name] = n
        return nets[name]
    for ref, p in parts.items():
        lib, name = FOOT[p["sym"]] if ref != "J13" else FOOT["HOST"]
        fp = pcbnew.FootprintLoad(f"{FP}\\{lib}.pretty", name)
        fp.SetReference(ref); fp.SetValue(p["value"][:24])
        x, y, rot = PLACE[ref]
        fp.SetPosition(mm(x, y)); fp.SetOrientationDegrees(rot)
        b.Add(fp)
        for pad in fp.Pads():
            n = p["pins"].get(pad.GetNumber())
            if n:
                pad.SetNet(net(n))
    for i, (x, y) in enumerate(HOLES):
        fp = pcbnew.FootprintLoad(f"{FP}\\MountingHole.pretty", "MountingHole_3.2mm_M3"); fp.SetReference(f"H{i + 1}")
        fp.SetPosition(mm(x, y)); b.Add(fp)
    # silkscreen title
    t = pcbnew.PCB_TEXT(b); t.SetText("HridayMitra AFE  HM-HW-004 Rev A"); t.SetLayer(pcbnew.F_SilkS); t.SetPosition(mm(35, 47.6))
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.0), pcbnew.FromMM(1.0))); b.Add(t)
    t2 = pcbnew.PCB_TEXT(b); t2.SetText("PATIENT SIDE - TYPE BF - BATTERY ONLY"); t2.SetLayer(pcbnew.F_SilkS); t2.SetPosition(mm(14, 1.6))
    t2.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8))); b.Add(t2)
    return b, pcbnew


def kicad_stage(stage):
    import pcbnew
    path = PCB / "hridaymitra_afe.kicad_pcb"
    if stage == "place":
        b, _ = build_board()
        b.Save(str(path))
        b = pcbnew.LoadBoard(str(path))
        assert pcbnew.ExportSpecctraDSN(b, str(PCB / "hridaymitra_afe.dsn")), "DSN export failed"
    else:
        b = pcbnew.LoadBoard(str(path))
        assert pcbnew.ImportSpecctraSES(b, str(PCB / "hridaymitra_afe.ses")), "SES import failed"
        gnd = b.FindNet("GND")
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(gnd); z.SetLocalClearance(pcbnew.FromMM(0.3))
            z.SetMinThickness(pcbnew.FromMM(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
            ol = z.Outline(); ol.NewOutline()
            for x, y in [(0.5, 0.5), (BOARD_W - 0.5, 0.5), (BOARD_W - 0.5, BOARD_H - 0.5), (0.5, BOARD_H - 0.5)]:
                ol.Append(pcbnew.FromMM(X0 + x), pcbnew.FromMM(Y0 + y))
            b.Add(z)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        b.Save(str(path))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("place", "finish"):        # called by KiCad's python
        kicad_stage(sys.argv[1]); sys.exit(0)
    parts = export_netlist()
    print(f"{len(parts)} parts, {len({n for p in parts.values() for n in p['pins'].values()})} nets")
    kpy = str(KICAD / "python.exe")
    subprocess.run([kpy, __file__, "place"], check=True)
    java = sorted((FR / "jre").glob("*/bin/java.exe"))[-1]                  # newest JRE: Freerouting 2.x needs Java 25
    subprocess.run([str(java), "-jar", str(FR / "freerouting.jar"), "-de", str(PCB / "hridaymitra_afe.dsn"), "-do", str(PCB / "hridaymitra_afe.ses"),
                    "-mp", "100", "--gui.enabled=false"], check=True, timeout=1200)
    subprocess.run([kpy, __file__, "finish"], check=True)
    cli = str(KICAD / "kicad-cli.exe"); pcb = str(PCB / "hridaymitra_afe.kicad_pcb")
    subprocess.run([cli, "pcb", "drc", "--format", "json", "--severity-error", "--schematic-parity", "-o", str(PCB / "drc.json"), pcb], capture_output=True)
    drc = json.loads((PCB / "drc.json").read_text())
    print("DRC errors:", len(drc.get("violations", [])), " unconnected:", len(drc.get("unconnected_items", [])))
    (PCB / "gerbers").mkdir(exist_ok=True)
    subprocess.run([cli, "pcb", "export", "gerbers", "-o", str(PCB / "gerbers"), pcb], check=True, capture_output=True)
    subprocess.run([cli, "pcb", "export", "drill", "-o", str(PCB / "gerbers") + "\\", pcb], check=True, capture_output=True)
    out = ROOT / "docs" / "hardware"
    for side, extra in (("top", []), ("bottom", ["--side", "bottom"])):
        subprocess.run([cli, "pcb", "render", "-o", str(out / f"HM-HW-004_pcb_3d_{side}.png"), "--width", "1600", "--height", "1150",
                        "--quality", "high", "--zoom", "1.1"] + extra + [pcb], capture_output=True)
    subprocess.run([cli, "pcb", "render", "-o", str(out / "HM-HW-004_pcb_3d_angle.png"), "--width", "1600", "--height", "1150",
                    "--quality", "high", "--rotate", "-45,0,30", "--zoom", "1.0", pcb], capture_output=True)
    print("done")
