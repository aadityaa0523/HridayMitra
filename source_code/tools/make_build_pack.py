"""Makes docs/HridayMitra physical build pack.pdf (drawings + cut list + steps + tests). Run: python tools/make_build_pack.py"""
import pathlib, subprocess, shutil
ROOT = pathlib.Path(__file__).resolve().parents[1]
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

COL = dict(ply="#e9dfcf", cell="#EF9F27", plate="#1D9E75", stool="#5F5E5A", box="#7F77DD", post="#444441", ink="#1b2427")


def top_view():
    S, O = 8, 30                                    # 8 px per cm
    X = lambda x: O + x * S
    Y = lambda y: O + y * S
    s = [f'<svg viewBox="0 0 {O*2+50*S+260} {O*2+70*S}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11">']
    def rect(x, y, w, h, fill, stroke=COL["ink"], dash=False, label=None, lc=COL["ink"], fs=10):
        da = ' stroke-dasharray="5 3"' if dash else ""
        s.append(f'<rect x="{X(x)}" y="{Y(y)}" width="{w*S}" height="{h*S}" fill="{fill}" stroke="{stroke}" stroke-width="1"{da}/>')
        if label: s.append(f'<text x="{X(x)+w*S/2}" y="{Y(y)+h*S/2+3}" text-anchor="middle" font-size="{fs}" fill="{lc}">{label}</text>')
    rect(0, 0, 50, 70, COL["ply"], label=None)
    s.append(f'<text x="{X(25)}" y="{Y(70)+16}" text-anchor="middle">plywood base plate 50 x 70 cm, 18 mm  (front = top of drawing)</text>')
    for cx, cy in [(5, 5), (45, 5), (5, 65), (45, 65)]:
        rect(cx - 3.75, cy - 1, 7.5, 2, COL["cell"], label=None)
        s.append(f'<circle cx="{X(cx)}" cy="{Y(cy)}" r="4" fill="{COL["cell"]}" stroke="{COL["ink"]}"/>')
    for fx in (11, 31):                              # left and right foot
        rect(fx, 6, 8, 8, COL["plate"], label="fore-foot", lc="#fff", fs=9)
        rect(fx + 0.5, 22, 7, 7, COL["plate"], label="heel", lc="#fff", fs=9)
    rect(10, 36, 30, 30, "none", dash=True, label=None)
    for lx, ly in [(11, 37), (37, 37), (11, 63), (37, 63)]:
        rect(lx, ly, 2.5, 2.5, COL["stool"])
    rect(17.5, 48, 15, 10, COL["box"], label="electronics box", lc="#fff", fs=9)
    s.append(f'<circle cx="{X(25)}" cy="{Y(4)}" r="{2*S}" fill="{COL["post"]}"/>')
    s.append(f'<text x="{X(25)}" y="{Y(4)-18}" text-anchor="middle">post 40 mm</text>')
    s.append(f'<text x="{X(25)}" y="{Y(35)}" text-anchor="middle" fill="{COL["stool"]}">stool seat 30 x 30 (dashed)</text>')
    # notes at right
    nx = O + 50 * S + 14
    notes = ["Load cells (amber): 4, each 5 cm", "from the long edges and 5 cm from the", "front and back edges, UNDER the plate.",
             "", "Foot plates (green), stainless:", "fore-foot 8 x 8 cm (current)", "heel 7 x 7 cm (sense)",
             "gap between them about 8 cm", "(the arch of the foot), feet 20 cm", "apart centre to centre.", "",
             "Keep every plate 1 cm or more", "from the plate edge and from each", "other. Nothing metal touches the stool."]
    for i, t in enumerate(notes):
        s.append(f'<text x="{nx}" y="{Y(2)+i*15}" font-size="10.5">{t}</text>')
    s.append("</svg>")
    return "".join(s)


def side_view():
    S, O = 5, 100                                    # 5 px per cm, left margin for labels
    H = 108
    X = lambda d: O + d * S                          # depth from front
    Y = lambda h: O + (H - h) * S                    # height above floor
    s = [f'<svg viewBox="0 0 {O*2+70*S+250} {O*2+H*S}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11">']
    def rect(d, h, w, ht, fill, label=None, lc="#fff"):
        s.append(f'<rect x="{X(d)}" y="{Y(h+ht)}" width="{w*S}" height="{ht*S}" fill="{fill}" stroke="{COL["ink"]}" stroke-width="0.8"/>')
        if label: s.append(f'<text x="{X(d)+w*S/2}" y="{Y(h+ht/2)+3}" text-anchor="middle" fill="{lc}" font-size="9">{label}</text>')
    def dim(h, text, d=-6):
        s.append(f'<line x1="{X(d)}" y1="{Y(0)}" x2="{X(d)}" y2="{Y(h)}" stroke="{COL["ink"]}" stroke-width="0.8"/>')
        s.append(f'<text x="{X(d)-4}" y="{Y(h/2)}" text-anchor="end">{text}</text>')
    rect(0, 0, 70, 0.1, COL["ink"])                  # floor line
    rect(3, 0, 4, 3.5, COL["cell"]); rect(63, 0, 4, 3.5, COL["cell"])        # load cell + rubber feet
    rect(0, 3.5, 70, 1.8, COL["ply"], "plywood plate 18 mm", COL["ink"])
    rect(6, 5.3, 23, 0.8, COL["plate"])                                       # foot plates
    rect(36, 5.3, 2.5, 42, COL["stool"]); rect(63.5, 5.3, 2.5, 42, COL["stool"])
    rect(34, 47.3, 34, 3, COL["stool"], "stool seat", "#fff")
    rect(48, 5.3, 15, 12, COL["box"], "box", "#fff")
    rect(2, 5.3, 4, 90, COL["post"])                                          # post
    rect(6, 73, 25, 2.5, COL["post"])                                         # handle bar
    rect(8, 75.5, 6, 1.5, COL["plate"]); rect(20, 75.5, 6, 1.5, COL["plate"]) # hand electrodes
    rect(1, 95.3, 14, 9, COL["box"], "panel", "#fff")
    rect(2.5, 75.5, 4.5, 3, COL["cell"])                                      # finger clip
    dim(47.3, "seat 42 cm", -4); dim(73, "handle 68 cm", -12); dim(95.3, "post 90 cm", -20)
    nx = O + 70 * S + 14
    for i, t in enumerate(["Side view (not to scale)", "", "Handle bar 25 cm, pointing to the", "patient, grips with 2 stainless", "strips per hand (green).", "Finger clip on the bar next to",
                           "the post (amber).", "", "Panel on top of the post: 3 LEDs,", "3 buttons, speaker.", "", "Seat height 42 cm, handle bar 68 cm",
                           "above the plate: adjust to the", "stool you buy: handle bar should be", "about elbow height when seated."]):
        s.append(f'<text x="{nx}" y="{Y(100)+i*15}" font-size="10.5">{t}</text>')
    s.append("</svg>")
    return "".join(s)


CSS = """@page{size:A4;margin:13mm 12mm}body{font-family:'Segoe UI',Arial,sans-serif;font-size:9.4pt;line-height:1.4;color:#1b2427}
h1{font-size:20pt;color:#0d4f52;margin:0 0 4px}h2{font-size:12.5pt;color:#0d4f52;border-bottom:1.5px solid #0d6b6e;padding-bottom:3px;margin:16px 0 7px;break-after:avoid}
table{border-collapse:collapse;width:100%;margin:5px 0 9px;font-size:8.4pt}th,td{border:1px solid #cfd8da;padding:3px 5px;vertical-align:top;text-align:left}
th{background:#e6f1f1}tr{break-inside:avoid}.box{background:#fff6dc;border-radius:6px;padding:6px 9px;margin:7px 0}.pb{break-before:page}p,li{margin:2px 0}ul,ol{margin:3px 0 3px 18px;padding:0}"""

HTML = f"""<!doctype html><html><head><meta charset="utf-8"><title>HridayMitra physical build pack</title><style>{CSS}</style></head><body>
<h1>HridayMitra: physical build pack</h1>
<p><b>Monitoring only, not a diagnosis tool. Never test on anyone with a pacemaker or defibrillator. Run from battery when a person touches the electrodes.</b></p>
<div class="box"><b>Read first.</b> These are <b>starting dimensions</b>, not tested. Buy the stool first, then adjust sizes to fit it. Two changes from the v3 guide: (1) the gap between the fore-foot and heel plate is now about <b>8 cm</b> (the arch of the foot), not 2 cm, because a real foot only touches the ball and the heel; the circuit does not care. (2) The post is a <b>40 mm wooden post</b> (easier than PVC, and the cables run outside it in clips). The impedance board still needs the phantom test before any foot touches it.</div>
<h2>1. What you are building</h2>
<p>A flat plywood plate that rests on 4 load cells. Everything the patient touches (stool, post, handle, foot plates) is fixed to the plate, so leaning on the handle does not change the weight. The laptop engine reads the numbers over USB.</p>
{top_view()}
<h2 class="pb">2. Side view</h2>
{side_view()}
<h2>3. Cut list and materials (physical parts only)</h2>
<table><tr><th>Part</th><th>Qty</th><th>Size</th><th>Material and note</th></tr>
<tr><td>Base plate</td><td>1</td><td>50 x 70 cm, 18 mm</td><td>Plywood or MDF. Ask the shop to cut it. Sand the edges.</td></tr>
<tr><td>Load cells</td><td>4</td><td>50 kg, about 75 mm bar or half-bridge type</td><td>Check the type with the seller (see build guide v3). One end bolted to the plate, the other on a rubber foot.</td></tr>
<tr><td>Load-cell spacers and bolts</td><td>8 + 8</td><td>M5 x 25 mm, washers, 5-6 mm spacers</td><td>The cell must have a gap of about 1 mm to flex. Follow the mounting picture on the seller's page.</td></tr>
<tr><td>Rubber feet</td><td>4</td><td>Hard rubber, about 3 cm</td><td>Under the free end of each cell</td></tr>
<tr><td>Stool</td><td>1</td><td>Flat 30 x 30 cm seat, 42 cm high, rated 100 kg+</td><td>Fix each leg with an L-bracket or two screws through a wooden block glued to the plate. The stool must not lift or slide.</td></tr>
<tr><td>Post</td><td>1</td><td>40 x 40 mm, 90 cm</td><td>Wood. Fix with 2 L-brackets and 4 screws to the plate at the front centre.</td></tr>
<tr><td>Handle bar</td><td>1</td><td>25 mm round, 28 cm</td><td>Wooden dowel or PVC pipe, screwed to the post at 68 cm</td></tr>
<tr><td>Foot plates</td><td>4</td><td>2 of 8 x 8 cm, 2 of 7 x 7 cm</td><td>Stainless steel 304, 0.5-1 mm. Round every corner. M3 screw and nut at the centre; wire on the underside.</td></tr>
<tr><td>Hand strips</td><td>4</td><td>10 x 2 cm</td><td>Stainless. Wrap and screw to the handle bar, 3 cm or more between strips.</td></tr>
<tr><td>Electronics box</td><td>1</td><td>150 x 100 x 50 mm</td><td>Screwed to the plate between the stool legs</td></tr>
<tr><td>Panel box</td><td>1</td><td>about 14 x 9 cm</td><td>On top of the post: 3 LEDs, 3 buttons, speaker</td></tr>
<tr><td>Cable clips, zip ties, cable sleeve</td><td>1 set</td><td></td><td>Cables run along the post to the box</td></tr></table>
<p><b>Tools:</b> drill and 3.2 / 5.5 mm bits, screwdrivers, spanner for M5, tin snips or hacksaw, file and sandpaper, ruler, pencil, soldering iron, multimeter, wire strippers, crimper.</p>
<h2 class="pb">4. Assembly steps, in order (about 5-6 hours)</h2>
<table><tr><th>Step</th><th>Do</th><th>Check before moving on</th></tr>
<tr><td>1. Plate</td><td>Cut and sand the plate. Mark the 4 load-cell positions (5 cm from the edges) and drill holes.</td><td>Plate lies flat; holes line up with the cells</td></tr>
<tr><td>2. Load cells</td><td>Bolt each cell to the underside with spacers, rubber foot on the free end. Wire to the HX711 (per build guide v3, section 4).</td><td>Readings change when you press <b>each</b> corner, and return to zero. Do this <b>before</b> adding anything else.</td></tr>
<tr><td>3. Calibrate</td><td>Put 1, 2 and 5 L water bottles on the plate (1 L is about 1 kg). Store the scale factor.</td><td>5 kg reads 5 kg within 0.1 kg at the centre and at each corner</td></tr>
<tr><td>4. Stool and post</td><td>Fix the stool and the post. Tighten everything.</td><td>No wobble; sit on it: no sliding; the weight reads sensibly (your weight within 0.3 kg of a bathroom scale)</td></tr>
<tr><td>5. Foot plates</td><td>Screw the 4 plates on the layout in section 1. Run wires to the underside, ring terminals on the screws, shielded cable to the box.</td><td>Multimeter: no two plates connect (more than 1 M&#937; dry); each plate connects to its wire</td></tr>
<tr><td>6. Handle and hand strips</td><td>Fix the bar to the post. Wrap and screw the 4 strips (OUT strips toward the fingers, IN strips toward the wrist). Fit the finger clip near the post.</td><td>Strips do not touch each other; no metal touches the post or screws</td></tr>
<tr><td>7. Electronics box</td><td>Screw the box under the seat. Mount ESP32, HX711, impedance board (after its phantom test), battery.</td><td>Nothing loose; all grounds joined at one point</td></tr>
<tr><td>8. Cables</td><td>Route sense cables away from current cables and from the speaker and SIM800L. Clip along the post. Leave slack at the plate (the cells must be free).</td><td>Cables do not pull on any load cell: weight reads the same with cables moved</td></tr>
<tr><td>9. Panel</td><td>Fix the 3 LEDs, 3 buttons and speaker to the panel box on the post top.</td><td>Each LED lights, each button prints</td></tr>
<tr><td>10. Power-up</td><td>Battery only, laptop connected over USB. Run the readings.</td><td>Weight, pulse, impedance phantom, buttons all show on the laptop</td></tr></table>
<h2>5. Tests before a person uses it</h2>
<ul>
<li><b>Mechanical:</b> sit and stand 10 times: no creak, slide or lift. Total load should not exceed the cells' rating (200 kg for four 50 kg cells).</li>
<li><b>Weight:</b> same weight within 0.3 kg after stepping on and off 5 times; same reading when you sit slightly left or right.</li>
<li><b>Electrical safety:</b> battery only; dry feet only at first; phantom test passed first (build guide v3, section 5); stop at any tingle.</li>
<li><b>Edge cases to try:</b> a heavy bag (guest weight), wet feet, one heel lifted, a hand off the grip, unplug one electrode: the laptop should say "no reading" and never a wrong number.</li></ul>
<h2>6. Common problems</h2>
<table><tr><th>Problem</th><th>Likely cause</th><th>Fix</th></tr>
<tr><td>Weight drifts or jumps</td><td>Cable pulling on a cell; stool touching the floor; loose bolt</td><td>Re-route slack; check clearance; tighten</td></tr>
<tr><td>One corner reads backwards</td><td>Cell wired the wrong way</td><td>Swap that cell's wires</td></tr>
<tr><td>Weight changes when you lean on the handle</td><td>Something touches the floor or a wall</td><td>Everything touched must stand on the plate only</td></tr>
<tr><td>Impedance reading unstable</td><td>Dirty or dry plates; cable noise; loose ring terminal</td><td>Clean with alcohol; shorten and shield; re-tighten</td></tr>
<tr><td>Metal plates tarnish</td><td>Not stainless</td><td>Replace with SS 304</td></tr></table>
<h2>7. Not verified</h2>
<p>All dimensions, the load-cell mounting, the 8 cm plate gap and the wooden post are my proposals. The load cells' exact type and mounting depend on what you buy. Nothing here has been built.</p>
</body></html>"""

tmp = pathlib.Path(r"C:\Users\Aadityaa\AppData\Local\Temp\hmpdf"); tmp.mkdir(exist_ok=True)
(tmp / "pack.html").write_text(HTML, encoding="utf-8")
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", rf"--user-data-dir={tmp}\prof5",
                rf"--print-to-pdf={tmp}\pack.pdf", (tmp / "pack.html").as_uri()], check=True, capture_output=True, timeout=180)
shutil.copy(tmp / "pack.pdf", ROOT / "docs" / "HridayMitra physical build pack.pdf")
print("wrote docs/HridayMitra physical build pack.pdf")
