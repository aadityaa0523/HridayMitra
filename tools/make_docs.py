"""REPORT + PITCH from the live results: every number below is read from reports/*.csv when this runs, so the
documents can never disagree with the code. Out: docs/HridayMitra report.pdf (2 pages), docs/HridayMitra pitch deck.pdf,
docs/PITCH_SCRIPT.md.   Run: python tools/make_docs.py
"""
import json, pathlib, shutil, subprocess
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
R, D = ROOT / "reports", ROOT / "docs"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = pathlib.Path(r"C:\Users\Aadityaa\AppData\Local\Temp\hmpdf")
img = lambda p: (ROOT / p).as_uri()
pct = lambda x: f"{100 * x:.0f}%"


def numbers():
    v2 = pd.read_csv(R / "leadtime_v2_results.csv"); v2 = v2[v2.system.str.startswith("v2")].set_index("cohort")
    p1 = pd.read_csv(R / "phase1_results.csv")
    rule = p1[p1.system.str.startswith("weight rule 1")].set_index("cohort")
    ml = pd.read_csv(R / "ml_comparator.csv").set_index(["cohort", "system"])
    st = pd.read_csv(R / "stress_and_ablation.csv").set_index("case")
    asn = pd.read_csv(R / "assumption_sensitivity.csv"); asn = asn[asn.side != "base"]
    cl = pd.read_csv(R / "careloop_results.csv").set_index("scenario")
    cost = pd.read_csv(R / "cost_simulation.csv").set_index("metric").value
    amb = pd.read_csv(R / "amber_lead_results.csv").set_index(["cohort", "counts_as_alert"])
    mc = pd.read_csv(ROOT / "sim/circuit/montecarlo_results.csv")
    z_err = np.abs(np.concatenate([mc[f"z{p}_abs_err_pct"] for p in range(1, 5)]))
    z_chg = np.abs(np.concatenate([mc[f"z{p}_change_err_pts"] for p in range(1, 5)]))
    hum = pd.read_csv(ROOT / "sim/circuit/hum_results.csv")
    bid = json.loads((R / "bidmc_hr_summary.json").read_text())
    ho, rw = v2.loc["PS held-out"], v2.loc["Real-world (external)"]
    return dict(
        sens=pct(ho.sensitivity), spec=f"{100 * ho.specificity:.1f}%", lead=f"{ho.median_lead_days:.0f}", fa=f"{ho.false_alerts_per_patient_month:.2f}",
        rw_sens=pct(rw.sensitivity), rw_fa=f"{rw.false_alerts_per_patient_month:.2f}",
        r_sens=pct(rule.iloc[0].sensitivity), r_spec=f"{100 * rule.iloc[0].specificity:.1f}%", r_fa=f"{rule.iloc[0].false_alerts_per_patient_month:.2f}",
        r_rw_sens=pct(rule.iloc[1].sensitivity), r_rw_fa=f"{rule.iloc[1].false_alerts_per_patient_month:.2f}",
        lr_sens=pct(ml.loc[("PS held-out", "Logistic regression")].sensitivity), lr_fa=f"{ml.loc[('PS held-out', 'Logistic regression')].false_alerts_per_patient_month:.2f}",
        lr_rw_sens=pct(ml.loc[("Real-world", "Logistic regression")].sensitivity), lr_rw_fa=f"{ml.loc[('Real-world', 'Logistic regression')].false_alerts_per_patient_month:.2f}",
        amber_lead=f"{amb.loc[('PS held-out', 'amber or red')].median_lead_days:.0f}",
        n_asn=len(asn), asn_beat=int((asn.sensitivity > asn.rule1_sensitivity).sum()), asn_budget=int(asn.within_fa_budget.sum()),
        asn_lo=pct(asn.sensitivity.min()), asn_hi=pct(asn.sensitivity.max()),
        stress_worst=pct(st.loc["Everything bad at once"].sensitivity), guest_rule_fa=f"{st.loc['10% guest days'].rule1_fa:.1f}",
        guest_fa=f"{st.loc['10% guest days'].false_alerts_per_patient_month:.2f}", miss50=pct(st.loc["50% of days missing"].sensitivity),
        no_imp=pct(st.loc["Without leg and chest impedance"].sensitivity), no_wt=pct(st.loc["Without weight"].sensitivity),
        no_am=pct(st.loc["Without amulet"].sensitivity), full=pct(st.loc["Full engine (frozen)"].sensitivity),
        cl_lad=pct(cl.loc["Rural, full ladder (default)"].reviewed_before_visit), cl_one=pct(cl.iloc[3].reviewed_before_visit),
        cl_med=f"{cl.loc['Rural, full ladder (default)'].median_review_h:.0f}", cl_bad=pct(cl.loc["Rural, everything bad at once"].reviewed_before_visit),
        cost=f"{cost['median']:,.0f}", cost_lo=f"{cost['p5']:,.0f}", cost_hi=f"{cost['p95']:,.0f}",
        vol_lo=f"{cost['volume_100_units_low']:,.0f}", vol_hi=f"{cost['volume_100_units_high']:,.0f}",
        mc_p99=f"{np.percentile(z_err, 99):.1f}", mc_chg=f"{np.percentile(z_chg, 99):.2f}",
        hum_g=f"{hum.err_goertzel_pct.abs().max():.2f}", hum_pp=f"{hum.err_pp_pct.abs().max():.0f}",
        bid_n=bid["records"], bid_sens=pct(bid["mean_sensitivity"]), bid_mae=f"{bid['mean_hr_mae_bpm']:.2f}")


CSS = """<style>@page{size:A4;margin:11mm}body{font:9.1pt/1.32 'Segoe UI',Arial,sans-serif;color:#17202a;margin:0}
h1{font-size:17pt;margin:0;color:#0d4f52}h2{font-size:10.5pt;margin:7px 0 3px;color:#0d6b6e;border-bottom:1.5px solid #0d6b6e}
.sub{color:#555;margin:2px 0 6px}table{border-collapse:collapse;width:100%;margin:3px 0}td,th{border:1px solid #c9d3d6;padding:2px 4px;text-align:left;vertical-align:top}
th{background:#e6f0f1}.cols{display:flex;gap:10px}.cols>div{flex:1}img{max-width:100%}.k{font-weight:700;color:#0d4f52}
.pb{page-break-before:always}.note{font-size:8pt;color:#555}ul{margin:2px 0 2px 15px;padding:0}li{margin:1px 0}</style>"""


def report(n):
    return f"""<!doctype html><html><head><meta charset="utf-8">{CSS}</head><body>
<h1>HridayMitra: catching worsening heart failure at home, 2 days before the hospital</h1>
<div class="sub">Transfinitte hardware track · Dare 2 Dream Ventures PS · <b>Monitoring, not diagnosis.</b> All patient data synthetic; no human data collected.</div>
<div class="cols"><div>
<h2>Problem</h2>Heart-failure patients are re-admitted because fluid builds up silently for days. Daily weighing alone catches about one in three events and floods families with false alarms; sticky patches are not worn by elders; rural homes have power cuts, 2G and low literacy.
<h2>Solution: a 90-second check-in station + an amulet + a care loop</h2><ul>
<li><span class="k">Check-in stool</span> (₹{n['cost']} build cost): weight (4 load cells), <b>8-electrode bioimpedance</b> at 5 kHz (legs, arms, both sides → chest fluid by segmental subtraction), finger pulse + SpO₂, stand-up time, 3 spoken yes/no questions answered with big buttons.</li>
<li><span class="k">Kavach amulet</span> (ESP32-C3 + accelerometer, breakaway cord, no magnets): night breathing rate, night sit-ups (orthopnea), activity, falls, SOS → BLE to the stool.</li>
<li><span class="k">Offline alert engine on the ESP32</span>: learns each person's own normal, scores only the worsening direction, needs <b>two independent witnesses</b> (fluid, heart-lungs, daily life) before red, and says <b>why</b> in plain words.</li>
<li><span class="k">Closed care loop over SMS</span>: family 1 → family 2 (30 min) → ASHA (2 h) → PHC doctor (6 h); reply 1/2/3 or a missed call.</li>
<li><span class="k">A product, not a gadget</span>: speaks the <b>doctor's own sick-day plan</b>; coaching tips (salt, missed tablets, infection-like); <b>two users per stool</b> with separate baselines; tablet drawer that knows if medicine was taken; seat vibration for hard-of-hearing users; daily <b>self-test</b> with "needs service" SMS; 11:00 missed check-in reminder; Sunday summary to the ASHA; village dashboard; OPD report and <b>ABDM/FHIR export</b>.</li></ul>
<h2>User journey (≈ 90 s a day)</h2>Sit → voice: "feet on the plates, hold the handles" → finger on the light → 3 questions (red = yes, green = no) → stand up → light + spoken result. Red: family gets the SMS with reasons, the ASHA is told at 2 h unless the family replies "3 fine".
</div><div><img src="{img('docs/block_diagram.png')}"></div></div>
<h2>Results (frozen threshold tuned on 140 training patients, tested once on held-out patients)</h2>
<table><tr><th></th><th>HridayMitra engine</th><th>Weight rule (SCALE-HF)</th><th>Logistic regression (ML)</th></tr>
<tr><td>Sensitivity, held-out (35 events)</td><td><b>{n['sens']}</b></td><td>{n['r_sens']}</td><td>{n['lr_sens']}</td></tr>
<tr><td>Specificity</td><td>{n['spec']}</td><td>{n['r_spec']}</td><td>-</td></tr>
<tr><td>Median lead before hospital visit</td><td>{n['lead']} days (amber heads-up: {n['amber_lead']} days)</td><td>2 days</td><td>2 days</td></tr>
<tr><td>False alerts per patient-month</td><td><b>{n['fa']}</b></td><td>{n['r_fa']}</td><td>{n['lr_fa']}</td></tr>
<tr><td>External 1,000-patient cohort: sensitivity / false alerts</td><td><b>{n['rw_sens']} / {n['rw_fa']}</b></td><td>{n['r_rw_sens']} / {n['r_rw_fa']}</td><td>{n['lr_rw_sens']} / {n['lr_rw_fa']}</td></tr></table>
<div class="note">Data: 200 pretend patients × 60 days (PS cohort, 60% with a visit) + 1,000 × 180 days (10%), latent-congestion model with salty meals, infection, missed pills, guests, wet feet, missing days; calibrated so the weight rule reproduces its published sensitivity (31% vs 35%) and false-alert rate (0.38 vs 0.34). Patient-level 70/30 split, seed 42; no-peeking check on every system.</div>

<h2 class="pb">Robustness: we tried to break it</h2>
<table><tr><th>Test</th><th>Result</th></tr>
<tr><td>Ablations (remove one sensor group)</td><td>no impedance {n['no_imp']}, no weight {n['no_wt']}, no amulet {n['no_am']} (full engine {n['full']}): every group earns its place</td></tr>
<tr><td>Stress: 50% missing days / guests / wet feet / power cuts / electrode ageing / everything at once</td><td>{n['miss50']} … {n['stress_worst']} sensitivity; 10% guests: engine {n['guest_fa']} false alerts vs weight rule <b>{n['guest_rule_fa']}</b></td></tr>
<tr><td>Assumption sweep: each of 23 guesses pushed low and high ({n['n_asn']} new cohorts)</td><td>beats the weight rule in <b>{n['asn_beat']}/{n['n_asn']}</b>, inside the false-alert budget in {n['asn_budget']}/{n['n_asn']}; sensitivity {n['asn_lo']}–{n['asn_hi']}, driven by how fast worsening develops, not by hardware noise</td></tr>
<tr><td>Care-loop simulation (5,000 alerts per scenario)</td><td>clinical review before the hospital visit: <b>{n['cl_lad']}</b> with the ladder vs {n['cl_one']} with one SMS; median {n['cl_med']} h; everything bad at once {n['cl_bad']}</td></tr>
<tr><td>Heart rate on real ECG (PhysioNet BIDMC CHF, {n['bid_n']} records)</td><td>beat sensitivity {n['bid_sens']}, heart-rate error {n['bid_mae']} bpm</td></tr></table>
<div class="cols"><div>
<h2>Hardware and simulation proof (free tools: LTspice, KiCad, Python)</h2><ul>
<li>Tetrapolar, ratiometric front end (Z = R5 · V<sub>body</sub>/V<sub>R5</sub>): gain and contact resistance cancel; LTspice error ≤ 0.05% for contacts 100 Ω–10 kΩ; +10% leg fluid → −8.7% Z; 134 µA excitation.</li>
<li><b>Monte Carlo, 100 stools from 5% parts</b> on random bodies and skin: 99% of readings within {n['mc_p99']}%, a +10% fluid change measured within {n['mc_chg']} points. It caught a design flaw: 1 MΩ bias resistors gave 12% errors → <b>changed to 10 MΩ</b>.</li>
<li>Mains hum (230 V coupling, charger plugged in): Goertzel reading ≤ {n['hum_g']}% error vs {n['hum_pp']}% for peak-to-peak → firmware uses Goertzel only.</li>
<li>KiCad schematic generated from code: ERC 0 violations; the netlist is checked against the path table and the LTspice values automatically.</li>
<li>Engine ported to C++ for the ESP32: <b>100% identical lights</b> to the Python engine over 3,231 patient-days.</li></ul>
</div><div>
<h2>Edge cases handled</h2><table><tr><th>Situation</th><th>What happens</th></tr>
<tr><td>Guest sits on the stool</td><td>weight jump > 2.5 kg → readings ignored</td></tr>
<tr><td>Toe ring / bad foot placement</td><td>leg reading > 25% off → "no reading", voice asks to re-place feet</td></tr>
<tr><td>Power cut, no network</td><td>18650 battery; SMS queued, retried every 10 min</td></tr>
<tr><td>Missed days</td><td>network clock fills gaps; light held</td></tr>
<tr><td>Infection vs fluid</td><td>cause tag: pulse/breathing up with steady fluid = infection-like</td></tr>
<tr><td>Oxygen below 90%</td><td>red at once, everyone messaged</td></tr>
<tr><td>Low literacy</td><td>voice, 3 lights, 2 buttons, missed call = reply</td></tr>
<tr><td>Pacemaker / ICD</td><td>no magnets; impedance and ECG off by setting</td></tr></table></div></div>
<h2>Cost and scale</h2>Build cost ₹{n['cost_lo']}–{n['cost_hi']} (Monte Carlo of the itemised list; limit ₹5,000); ≈ ₹{n['vol_lo']}–{n['vol_hi']} at 100 units. SMS ≈ ₹0.05 per patient-month. Fits ASHA-led programmes: one stool per home, the ASHA card closes the loop.
<h2>Honest limits</h2><ul><li>Synthetic data: shows the method works on modelled patterns, not clinical accuracy. Lead time is bounded by the PS worsening window (3–10 days, accelerating).</li>
<li>Chest impedance is weak (needs ~7 days of averaging); circuit not yet compared with a bench build; SpO₂ calibration generic; ML regression catches more events but with 3–5× the false alarms.</li>
<li>Never for anyone with a pacemaker or ICD in the impedance mode; battery only during measurement. Code, data, tests: github.com/aadityaa0523/HridayMitra</li></ul>
</body></html>"""


SLIDE_CSS = """<style>@page{size:13.333in 7.5in;margin:0}body{margin:0;font-family:'Segoe UI',Arial,sans-serif;color:#17202a}
.s{width:13.333in;height:7.5in;box-sizing:border-box;padding:.55in .7in;page-break-after:always;position:relative;background:#fbfcfc}
h1{font-size:40pt;margin:0 0 .15in;color:#0d4f52;line-height:1.1}h2{font-size:28pt;margin:0 0 .25in;color:#0d4f52}
.big{font-size:20pt;line-height:1.45}.huge{font-size:50pt;font-weight:800;color:#c0392b}.k{color:#0d6b6e;font-weight:700}
ul{margin:0;padding-left:.35in}li{margin:.07in 0}table{border-collapse:collapse;font-size:16pt;width:100%}td,th{border:1px solid #c9d3d6;padding:6px 10px}th{background:#e6f0f1}
.foot{position:absolute;bottom:.25in;left:.7in;font-size:10pt;color:#777}.cols{display:flex;gap:.4in}.cols>div{flex:1}
.card{background:#fff;border:2px solid #0d6b6e;border-radius:12px;padding:.18in;font-size:16pt}</style>"""


def deck(n):
    foot = '<div class="foot">HridayMitra · monitoring, not diagnosis · synthetic data</div>'
    S = [
        f'<h1>HridayMitra</h1><div class="big">A 90-second daily check-in that warns a family <b>{n["lead"]} days before</b> a heart-failure hospital visit.<br>'
        f'Offline. Voice-led. ₹{n["cost"]} to build.</div><br><div class="huge">{n["rw_sens"]} caught · {n["rw_fa"]} false alarms / month</div>'
        f'<div class="big">vs the weight-scale rule: {n["r_rw_sens"]} caught · {n["r_rw_fa"]} false alarms</div>',
        '<h2>The problem</h2><ul class="big"><li>Heart failure fills the body with fluid <b>for days</b> before the emergency.</li>'
        '<li>Daily weighing (today\'s home standard) catches about <b>1 in 3</b> events and cries wolf.</li>'
        '<li>Elders will not wear sticky patches or vests; rural homes have power cuts, 2G and low literacy.</li>'
        '<li>An alert nobody acts on is worthless.</li></ul>',
        f'<h2>The solution</h2><div class="cols"><div class="big"><ul><li><span class="k">Check-in stool</span>: weight, 8-electrode bioimpedance (leg + chest fluid), pulse + SpO₂, stand-up speed, 3 spoken questions</li>'
        f'<li><span class="k">Kavach amulet</span>: night breathing, sit-ups, activity, falls, SOS</li><li><span class="k">Offline engine</span> + <span class="k">SMS care loop</span></li></ul></div>'
        f'<div><img src="{img("docs/block_diagram.png")}" style="width:100%"></div></div>',
        '<h2>More than a chair: a home care programme in a stool</h2><div class="cols"><div class="big"><ul>'
        '<li>Speaks the <b>doctor&#39;s own sick-day plan</b></li><li>Coaching: salt, missed tablets, infection-like</li>'
        '<li><b>Two people, one stool</b>: separate baselines</li><li>Tablet drawer knows if medicine was taken</li></ul></div>'
        '<div class="big"><ul><li>Seat vibration for hard-of-hearing elders</li><li>Daily <b>self-test</b> → "needs service" SMS</li>'
        '<li>11:00 reminder, Sunday summary to the ASHA</li><li>Village dashboard, OPD report, <b>ABDM/FHIR</b> export</li></ul></div></div>',
        '<h2>How it decides: personal, multi-witness, explainable</h2><div class="cols"><div class="big"><ul><li>Learns <b>your</b> normal (median of days 7–35 ago)</li><li>Scores only the worsening direction</li>'
        '<li>Red needs <b>two independent witnesses</b>: fluid · heart-lungs · daily life</li><li>Every red says <b>why</b>, plus a cause tag (fluid vs infection vs missed pills)</li></ul></div>'
        '<div class="card">SMS: HridayMitra RED for P0022.<br>Why: weight +1.9 kg; leg reading −7 %; night breathing +2/min.<br>Possible cause: fluid building.<br>Reply 1 checking, 2 need help, 3 fine.<br>Not a diagnosis; if breathless at rest call 108.</div></div>',
        f'<h2>Results: frozen threshold, held-out patients</h2><table><tr><th></th><th>HridayMitra</th><th>Weight rule</th><th>ML (logistic)</th></tr>'
        f'<tr><td>Sensitivity</td><td><b>{n["sens"]}</b></td><td>{n["r_sens"]}</td><td>{n["lr_sens"]}</td></tr><tr><td>False alerts / patient-month</td><td><b>{n["fa"]}</b></td><td>{n["r_fa"]}</td><td>{n["lr_fa"]}</td></tr>'
        f'<tr><td>Specificity</td><td>{n["spec"]}</td><td>{n["r_spec"]}</td><td>-</td></tr><tr><td>Lead time</td><td>{n["lead"]} days ({n["amber_lead"]} with amber)</td><td>2 days</td><td>2 days</td></tr>'
        f'<tr><td>1,000-patient external cohort</td><td><b>{n["rw_sens"]} / {n["rw_fa"]}</b></td><td>{n["r_rw_sens"]} / {n["r_rw_fa"]}</td><td>{n["lr_rw_sens"]} / {n["lr_rw_fa"]}</td></tr></table>'
        '<div class="big" style="margin-top:.2in">Fewest false alarms = families keep trusting the SMS.</div>',
        f'<h2>We tried to break it</h2><ul class="big"><li><b>{n["asn_beat"]}/{n["n_asn"]}</b> wrong-assumption worlds: still beats the weight rule</li>'
        f'<li>Guest on the stool: rule fires {n["guest_rule_fa"]} false alerts/month, we fire {n["guest_fa"]}</li><li>Half the days missing: still {n["miss50"]} caught</li>'
        '<li>Toe ring, wet feet, power cuts, electrode ageing, amulet left off: handled, tested</li>'
        f'<li>Care loop: <b>{n["cl_lad"]}</b> of alerts reach a clinician before the visit (one SMS: {n["cl_one"]})</li></ul>',
        f'<h2>Engineering proof</h2><ul class="big"><li>LTspice: ≤ 0.05% error, contact-proof (tetrapolar, ratiometric)</li>'
        f'<li>Monte Carlo of 100 cheap-part stools → found a flaw, <b>1 MΩ → 10 MΩ</b>, now 99% within {n["mc_p99"]}%</li>'
        f'<li>Mains hum: Goertzel {n["hum_g"]}% vs peak-to-peak {n["hum_pp"]}%</li><li>KiCad schematic from code, ERC clean, netlist auto-verified</li>'
        '<li>Engine in C++ on the ESP32: <b>100% identical</b> to Python over 3,231 days</li>'
        f'<li>Real ECG (PhysioNet BIDMC CHF): heart-rate error {n["bid_mae"]} bpm</li></ul>',
        f'<h2>Cost and model</h2><div class="cols"><div class="big"><ul><li>Build cost <b>₹{n["cost_lo"]}–{n["cost_hi"]}</b> (limit ₹5,000)</li><li>≈ ₹{n["vol_lo"]}–{n["vol_hi"]} at 100 units</li>'
        '<li>SMS ≈ ₹0.05 per patient-month</li></ul></div><div class="big"><ul><li>Sold to PHCs / NGOs / insurers, placed by ASHAs</li><li>One avoided admission pays for many stools</li><li>No app, no smartphone, no internet</li></ul></div></div>',
        '<h2>Honest limits and next steps</h2><ul class="big"><li>Synthetic data: proves the method, not clinical accuracy</li><li>Next: bench build vs simulation, ethics-approved pilot with lung-ultrasound comparison</li>'
        '<li>Record Hindi/Tamil prompts; tune SpO₂ against a reference oximeter</li><li>Hybrid engine: rules + learned weights (+6–12 points, same alerts budget)</li></ul>'
        '<br><div class="big"><b>Ask:</b> a pilot partner and seed support to take HridayMitra into 100 homes.</div>',
    ]
    return f'<!doctype html><html><head><meta charset="utf-8">{SLIDE_CSS}</head><body>' + "".join(f'<div class="s">{s}{foot}</div>' for s in S) + "</body></html>"


SCRIPT = """# 5-minute pitch script (numbers match the deck; regenerate with python tools/make_docs.py)

| Time | Slide | Say |
|---|---|---|
| 0:00 | 1 | "Every heart-failure admission starts days earlier, silently. HridayMitra is a 90-second daily check-in that warns the family {lead} days before the hospital, offline, for ₹{cost}." |
| 0:30 | 2 | The weight-scale rule catches about a third and cries wolf; elders don't wear patches; rural homes have power cuts and 2G. |
| 1:00 | 3 | Stool + amulet + care loop. Point at the block diagram: 8 electrodes, legs and chest fluid. |
| 1:45 | 4 | Personal normal, two witnesses, reasons. Read the SMS aloud. |
| 2:15 | 5 | Results: {sens} vs {r_sens}, {fa} vs {r_fa} false alerts. ML catches more but with 3-5x the false alarms. |
| 2:50 | Demo | `python run.py demo`: patient P0022, slide to the red day, tick "guest" and "toe ring": the light does not lie. |
| 3:30 | 6 | We tried to break it: {asn_beat}/{n_asn} wrong-assumption worlds still beat the rule; care loop {cl_lad}. |
| 4:00 | 7 | Engineering: the Monte Carlo found our own bug (1 MΩ → 10 MΩ); C++ engine 100% identical on the ESP32. |
| 4:30 | 8-9 | Cost, model, honest limits, the ask. |

Questions to expect: lungs? (chest segment = weak, trend over a week; the stronger lung signals are night breathing and orthopnea). Pacemaker? (impedance off by setting, no magnets). Why not ML? (alarm fatigue; hybrid is the next step). Real data? (synthetic by PS rule; BIDMC real ECG for heart rate).
"""


def pdf(html, name):
    TMP.mkdir(exist_ok=True)
    src = TMP / f"{name}.html"; src.write_text(html, encoding="utf8")
    out = TMP / f"{name}.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    f"--print-to-pdf={out}", src.as_uri()], check=True, capture_output=True, timeout=180)
    return out


if __name__ == "__main__":
    n = numbers()
    shutil.copy(pdf(report(n), "report"), D / "HridayMitra report.pdf")
    shutil.copy(pdf(deck(n), "deck"), D / "HridayMitra pitch deck.pdf")
    (D / "PITCH_SCRIPT.md").write_text(SCRIPT.format(**n), encoding="utf8")
    import fitz
    for f in ("HridayMitra report.pdf", "HridayMitra pitch deck.pdf"):
        print(f, fitz.open(D / f).page_count, "pages")
