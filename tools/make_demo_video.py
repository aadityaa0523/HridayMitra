"""RECORDED DEMO RUN: one simulated month of the real stool, as a video for judges (no browser, no Wokwi account).

The REAL stool firmware ran a month in the laptop emulator (tests/sil): its check-in reports and every SMS it sent are in
reports/sil_checkins.jsonl and reports/sil_sms.jsonl. Here those exact lines drive the REAL Wokwi chip code (patient
twin, stool monitor, SIM800L phone, compiled for the laptop by tests/sil/chip_preview.c in script mode), frame by
frame, and the frames become a video. The twin's fluid colour comes from the firmware's own leg and chest readings.
Run:  python tools/make_demo_video.py     (after python -m pytest tests/test_firmware_sil.py)
Out:  docs/demo/hridaymitra_month_demo.mp4 and docs/demo/hridaymitra_month_demo_poster.png
"""
import json, pathlib, shutil, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
SIL, OUT = ROOT / "tests" / "sil", ROOT / "docs" / "demo"
LIGHT = {0: ("GREEN", (60, 200, 90)), 1: ("AMBER", (240, 170, 40)), 2: ("RED", (230, 60, 60))}
WHO = {"+910000000001": "Family 1", "+910000000002": "Family 2", "+910000000003": "ASHA", "+910000000004": "PHC doctor"}
FONT = lambda size, bold=False: ImageFont.truetype(f"C:/Windows/Fonts/{'segoeuib' if bold else 'segoeui'}.ttf", size)


def renderers():
    for k in ("BODY", "MONITOR", "PHONE"):
        exe = SIL / f"script_{k}.exe"
        subprocess.run([sys.executable, "-m", "ziglang", "cc", "-O2", f"-DSCRIPT_{k}", "chip_preview.c", "-o", exe.name],
                       cwd=SIL, check=True, capture_output=True)


def load():
    raw = (ROOT / "reports/sil_checkins.jsonl").read_text().splitlines()
    checkins = []
    for l in raw:
        day = int(l[7:l.index(",")]); rep = l[l.index('"report":') + 9:-1].replace(":nan", ":null").replace(":-nan", ":null")
        checkins.append((day, json.loads(rep)))
    sms = [json.loads(l) for l in (ROOT / "reports/sil_sms.jsonl").read_text().splitlines()]
    return checkins, sms


def script():
    """Commands for the three chips plus the frame list [(body, monitor, phone, caption dict)]."""
    checkins, sms = load()
    p1 = [r for _, r in checkins if r["id"] == "P001" and r.get("leg_z_ohm") is not None][:7]
    z0, t0 = np.median([r["leg_z_ohm"] for r in p1]), np.median([r["trunk_z_ohm"] for r in p1])
    cmd = {"BODY": [], "MONITOR": [], "PHONE": []}
    snap = {"BODY": "b0", "MONITOR": "m0", "PHONE": "p0"}
    for k, n in snap.items():
        cmd[k].append(f"snap {n}")
    frames, n = [], [0]

    def shot(k):
        n[0] += 1; snap[k] = f"{k[0].lower()}{n[0]}"; cmd[k].append(f"snap {snap[k]}")

    def frame(cap, repeat=1):
        frames.extend([(snap["BODY"], snap["MONITOR"], snap["PHONE"], cap)] * repeat)

    days = sorted({d for d, _ in checkins} | {m["day"] for m in sms})
    for day in days:
        for _, r in [c for c in checkins if c[0] == day]:
            leg, tr = r.get("leg_z_ohm"), r.get("trunk_z_ohm")
            mine = r["id"] == "P001" and not r.get("guest")
            legf = max(0.0, (1 - leg / z0) / 0.87 * 100) if (mine and leg) else 0
            chf = max(0.0, (1 - tr / t0) / 0.91 * 100) if (mine and tr) else 0
            cmd["BODY"] += [f"set legFluid {min(legf, 30):.1f}", f"set chestFluid {min(chf, 30):.1f}", f"set footLifted {int(leg is None)}", "pin SEL 0"]
            label, col = ("LEARNING", (150, 160, 255)) if r.get("learning") else LIGHT[r["light"]]
            cap = dict(day=day, date=r.get("date", ""), who=r["id"] + (" (guest: not saved)" if r.get("guest") else ""), light=label, col=col,
                       why=r.get("why") or "no warning signs", nums=f"weight {r['weight_kg']:.1f} kg   leg {leg or float('nan'):.0f} ohm   "
                       f"pulse {r.get('pulse_bpm') or float('nan'):.0f}   SpO2 {r.get('spo2') or float('nan'):.0f}%", event="Check-in on the stool")
            busy = r["light"] > 0 or not r.get("learning") and day >= 18 or leg is None
            for path in (range(4) if busy else (0,)):
                cmd["BODY"] += ["pin EXC 1", f"pin S0 {path & 1}", f"pin S1 {path >> 1}"]; shot("BODY")
                frame(dict(cap, light="measuring...", col=(120, 200, 255), phase=("path", path),
                           why=["legs", "arms", "right side", "left side"][path] + " (5 kHz, 4 electrodes)"))
            if busy:                                       # the same current through the precision reference
                cmd["BODY"].append("pin SEL 1"); shot("BODY")
                frame(dict(cap, light="reference", col=(120, 220, 160), phase=("ref",),
                           why="same current through Rcal 100 ohm 0.1 %: Z = Rcal x V(body) / V(Rcal)"))
                cmd["BODY"].append("pin SEL 0")
            cmd["BODY"].append("pin EXC 0"); shot("BODY")
            cmd["MONITOR"].append("line " + json.dumps(r, separators=(",", ":"))); shot("MONITOR")
            frame(cap, 3 if busy else 1)
        for m in [m for m in sms if m["day"] == day]:
            cmd["PHONE"].append(f"sms {m['to']} {m['text']}"); shot("PHONE")
            cmd["MONITOR"].append("line " + json.dumps(dict(t="sms", to=m["to"], text="."), separators=(",", ":"))); shot("MONITOR")
            frame(dict(day=day, date="", who=f"SMS to {WHO.get(m['to'], m['to'])}  ({m['minute'] // 60:02d}:{m['minute'] % 60:02d})",
                       light="SMS", col=(200, 200, 200), why=m["text"], nums="", event="Care loop"), 3)
    return cmd, frames


# ---- the circuit panel: the real KiCad schematic (impedance front end), with the parts at work highlighted ----
CLIP = (40, 70, 1480, 452)                                  # front-end band of hardware/kicad/hridaymitra_schematic.pdf (pt)
SCH_W = 1540
PATHS = {0: ("LF_FORE", "RF_FORE", "LF_HEEL", "RF_HEEL"), 1: ("LH_OUT", "RH_OUT", "LH_IN", "RH_IN"),   # tools/make_schematic.py
         2: ("RH_OUT", "RF_FORE", "RH_IN", "RF_HEEL"), 3: ("LH_OUT", "LF_FORE", "LH_IN", "LF_HEEL")}     # PATH_TABLE, by S1 S0
# boxes around each part, in PDF points, anchored on its reference label
CURRENT = {"U1B": (-20, -8, 100, 50), "C2": (-14, -30, 20, 66), "C3": (-14, -30, 20, 66), "R4": (-16, -15, 22, 80),
           "U4": (-65, 0, 100, 150), "C4": (-14, -22, 24, 74)}
SENSE = {"U5": (-58, -5, 75, 112), "R8": (-12, -5, 18, 90), "R9": (-12, -5, 18, 90), "U3": (-62, -5, 72, 112),
         "U2": (-22, 15, 88, 110), "R11": (-12, -20, 20, 70)}
REF = {"R5": (-14, -15, 24, 80), "R22": (-14, -22, 40, 74), "U3": (-62, -5, 72, 112), "U2": (-22, 15, 88, 110)}


def schematic():
    import pymupdf
    pg = pymupdf.open(ROOT / "hardware/kicad/hridaymitra_schematic.pdf")[0]
    z = SCH_W / (CLIP[2] - CLIP[0])
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*CLIP))
    base = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    words = pg.get_text("words")
    at = {w[4]: (w[0], w[1]) for w in words if w[1] < CLIP[3]}
    j1 = [(w[4], (w[0], w[1], w[2], w[3])) for w in words if 920 <= w[0] <= 965 and 300 <= w[1] <= 370]   # J1 pin labels
    px = lambda x, y: ((x - CLIP[0]) * z, (y - CLIP[1]) * z)
    return base, at, j1, px


def circuit_panel(sch, phase):
    base, at, j1, px = sch
    img = base.copy(); ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)

    def mark(parts, rgb):
        for ref, (a, b, c_, e) in parts.items():
            if ref in at:
                x, y = at[ref]; x0, y0 = px(x + a, y + b); x1, y1 = px(x + c_, y + e)
                d.rounded_rectangle((x0, y0, x1, y1), 8, fill=rgb + (55,), outline=rgb + (255,), width=3)
    if phase and phase[0] == "path":
        mark(CURRENT, (255, 140, 30)); mark(SENSE, (40, 180, 255))
        live = PATHS[phase[1]]
        for name, (x0, y0, x1, y1) in j1:                  # the 4 electrodes in use on J1
            if name.replace("_E", "") in live:
                d.rounded_rectangle((*px(x0 - 2, y0 - 1), *px(x1 + 2, y1 + 1)), 4, fill=(255, 230, 0, 120), outline=(200, 140, 0, 255), width=2)
    elif phase and phase[0] == "ref":
        mark(REF, (40, 200, 110))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def compose(frames, shots, tmp):
    big, small, mid, tiny = FONT(30, True), FONT(19), FONT(23, True), FONT(17)
    sch = schematic()
    paths = []
    for i, (b, m, p, c) in enumerate(frames):
        img = Image.new("RGB", (1600, 900), (16, 20, 28)); d = ImageDraw.Draw(img)
        d.text((30, 14), "HridayMitra: one month of the real stool firmware", font=big, fill=(240, 240, 240))
        d.text((30, 54), "Software-in-the-loop run; screens are the real Wokwi chip code; circuit is the KiCad schematic. "
                         "Synthetic patient. Monitoring, not diagnosis.", font=tiny, fill=(150, 160, 175))
        for name, (x, y) in ((b, (30, 90)), (m, (340, 90)), (p, (715, 90))):
            im = Image.open(shots / f"{name}.ppm"); img.paste(im.resize((int(im.width * 1.6), int(im.height * 1.6)), Image.NEAREST), (x, y))
        x0 = 990
        d.text((x0, 90), f"Day {c['day']}  {c['date']}", font=big, fill=(240, 240, 240))
        d.text((x0, 132), f"{c['event']}: {c['who']}", font=small, fill=(190, 200, 210))
        d.rounded_rectangle((x0, 166, x0 + 200, 210), 10, fill=c["col"]); d.text((x0 + 14, 173), c["light"], font=mid, fill=(10, 10, 10))
        d.text((x0, 222), c["nums"], font=tiny, fill=(190, 200, 210))
        words, line, y = c["why"].split(), "", 252
        for w_ in words:                                   # wrap the reason / SMS text
            if d.textlength(line + " " + w_, font=small) > 590:
                d.text((x0, y), line, font=small, fill=(230, 230, 230)); y += 26; line = w_
            else:
                line = (line + " " + w_).strip()
        d.text((x0, y), line, font=small, fill=(230, 230, 230))
        ph = c.get("phase")
        img.paste(circuit_panel(sch, ph), (30, 490))
        if ph and ph[0] == "path":
            live = PATHS[ph[1]]
            note = f"current {live[0]} -> {live[1]} (orange)     voltage sensed {live[2]} / {live[3]} (blue)     electrodes in use (yellow)"
        elif ph:
            note = "self-calibrating reference: R5 + Rcal 100 ohm 0.1 % on the spare 74HC4053 switch (green)"
        else:
            note = "impedance front end: MCP6002 current source, 74HC4052 path switches, 74HC4053 body / reference select, INA126"
        d.text((30, 464), note, font=tiny, fill=(255, 210, 120) if ph else (150, 160, 175))
        f = tmp / f"f{i:05d}.png"; img.save(f); paths.append(f)
    return paths


if __name__ == "__main__":
    renderers()
    cmd, frames = script()
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        tmp = pathlib.Path(t); shots = tmp / "shots"; shots.mkdir()
        for k, lines in cmd.items():
            subprocess.run([str(SIL / f"script_{k}.exe"), str(shots)], input="\n".join(lines) + "\n", text=True,
                           check=True, capture_output=True, encoding="utf8")
        paths = compose(frames, shots, tmp)
        import imageio_ffmpeg
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-framerate", "5", "-i", str(tmp / "f%05d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-crf", "23", str(OUT / "hridaymitra_month_demo.mp4")], check=True)
        red = next((i for i, f in enumerate(frames) if f[3]["light"] == "RED"), len(frames) - 1)
        shutil.copy(paths[red + 2 if red + 2 < len(paths) else red], OUT / "hridaymitra_month_demo_poster.png")
    mp4 = OUT / "hridaymitra_month_demo.mp4"
    print(f"{len(frames)} frames, {len(frames) / 5:.0f} s, {mp4.stat().st_size / 1e6:.1f} MB -> {mp4}")
