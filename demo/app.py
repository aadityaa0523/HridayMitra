"""HridayMitra demo: one pretend patient through the FROZEN v2 alert engine, seen by the patient, the family and the
ASHA/doctor, with "break it" switches that add real-life mess live. Synthetic data only. Monitoring, not diagnosis.
Run:  streamlit run demo/app.py
"""
import json, pathlib, sys, time
import numpy as np
import pandas as pd
import streamlit as st
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import alert_engine as A, product as P

T = json.loads((ROOT / "engine/frozen_params_v3.json").read_text())["T"]
COLOR, NAME = {0: "#2e9e5b", 1: "#e0a100", 2: "#c0392b"}, {0: "GREEN", 1: "AMBER", 2: "RED"}
SAY = {0: ("All fine today.", "सब ठीक है।", "எல்லாம் சரி."),
       1: ("Please check again tomorrow.", "कल फिर से जाँच करें।", "நாளை மீண்டும் சோதிக்கவும்."),
       2: ("Message sent to your family and ASHA.", "परिवार और आशा दीदी को संदेश भेजा गया।", "குடும்பத்துக்கும் ஆஷாவுக்கும் செய்தி அனுப்பப்பட்டது.")}


@st.cache_data
def load():
    f = pd.read_csv(ROOT / "data/processed/realworld/daily_features.csv")
    p = pd.read_csv(ROOT / "data/processed/realworld/patients.csv")
    return f, p


st.set_page_config("HridayMitra demo", layout="wide")
st.title("HridayMitra: heart-failure early warning at home")
st.caption("Pretend (synthetic) patients. Monitoring, not diagnosis. Always follow your doctor.")
f, p = load()
sick = p[p.event].patient_id.tolist()
live_files = sorted((ROOT / "data/live").glob("*.csv"))
with st.sidebar:
    screen = st.radio("Screen", ["Patient", "ASHA village view"])
    source = st.radio("Data", ["Synthetic cohort"] + (["Live stool"] if live_files else []),
                      help="Live stool = check-ins logged by tools/stool_bridge.py from the real stool (or its --simulate mode)")
    if source == "Live stool":
        live = st.selectbox("Stool log", live_files, format_func=lambda f: f.stem)
        refresh = st.checkbox("Auto-refresh every 5 s", value=False)
    else:
        pid = st.selectbox("Patient", sick[:20] + p[~p.event].patient_id.tolist()[:10])
    st.subheader("Break it")
    guest = st.checkbox("A guest sits on the stool (day 40)")
    ring = st.checkbox("Toe ring touches both plates (days 50-52)")
    cut = st.checkbox("Power cut: no check-ins for 4 days before the visit")
    amulet = st.checkbox("Amulet not worn for the last 10 days")

@st.cache_data
def village(ids):
    """Latest state of every patient for the ASHA: red first, then amber, then not checked in, then green."""
    rows = []
    for pid_ in ids:
        g_ = f[f.patient_id == pid_].reset_index(drop=True)
        sc_ = A.scores(g_); L = A.lights(sc_, T)
        last = g_.weight_kg.last_valid_index()
        rows.append(dict(patient=pid_, light=NAME[int(L[-1])], days_since_checkin=len(g_) - 1 - (last if last is not None else -99),
                         why="; ".join(A.explain(g_, sc_[-1])[1]) or "-", tip=P.coaching(g_, sc_[-1]) or "-",
                         weekly_sms=P.weekly_summary(pid_, g_, L)))
    order = {"RED": 0, "AMBER": 1, "GREEN": 3}
    return pd.DataFrame(rows).sort_values("light", key=lambda c: c.map(order))


if screen == "ASHA village view":
    st.subheader("ASHA village view: who needs a visit today")
    ids = sick[:12] + p[~p.event].patient_id.tolist()[:18]
    v = village(tuple(ids))
    st.dataframe(v.drop(columns="weekly_sms").style.map(lambda x: f"background-color:{COLOR[{'GREEN': 0, 'AMBER': 1, 'RED': 2}[x]]};color:white"
                 if x in ("GREEN", "AMBER", "RED") else "", subset=["light"]), width="stretch", hide_index=True)
    st.caption("Sunday summary SMS the ASHA receives for each patient:")
    st.code(chr(10).join(v.weekly_sms.head(5)), language=None)
    st.stop()

if source == "Live stool":
    g = pd.read_csv(live).reset_index(drop=True)
    pid, info = live.stem, pd.Series({"event": False})
    if len(g) < 15:
        st.info(f"{len(g)} check-ins so far: the stool is still learning this person's normal (about 10 days).")
else:
    g = f[f.patient_id == pid].reset_index(drop=True).copy()
    info = p.set_index("patient_id").loc[pid]
if guest and len(g) > 40:
    g.loc[40, ["weight_kg", "leg_z_ohm", "pulse_bpm"]] = [g.weight_kg.median() + 14, 640, 80]
if ring and len(g) > 52:
    g.loc[50:52, "leg_z_ohm"] *= 1.8
if cut:
    g.loc[len(g) - 6:len(g) - 3, g.columns[2:]] = np.nan
if amulet:
    g.loc[len(g) - 10:, ["night_rr", "night_situps", "activity_min"]] = np.nan

sc = A.scores(g)
st_ = A.lights(sc, T)
day = st.slider("Day", 0, len(g) - 1, len(g) - 1) if len(g) > 1 else 0
light = int(st_[day])
cause, why = A.explain(g, sc[day])

c1, c2, c3 = st.columns([1, 1.2, 2])
with c1:
    st.subheader("Patient (stool)")
    st.markdown(f"<div style='background:{COLOR[light]};color:white;border-radius:50%;width:160px;height:160px;"
                f"display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:700'>{NAME[light]}</div>",
                unsafe_allow_html=True)
    for line in SAY[light]:
        st.write("🔊 " + line)
    plan = P.plan_message(list(st_[:day + 1]))
    tip = P.coaching(g, sc[day])
    if plan:
        st.write("🩺 " + plan)
    if tip:
        st.write("💡 " + tip)
    if sc[day]["learning"]:
        st.write("🔊 Still learning your normal (first ~10 days): only the danger rules are active.")
with c2:
    st.subheader("Family (SMS)")
    if light == 2:
        st.code(f"HridayMitra: {pid} RED on day {day}.\nWhy: {'; '.join(why) or 'several signs together'}.\n"
                f"Possible cause: {cause}.\nReply 1 = I am checking, 2 = need help, 3 = patient is fine.\n"
                "Not a diagnosis. If breathless at rest, call 108.", language=None)
        st.code(P.plan_message(list(st_[:day + 1])) or "", language=None)
        st.caption("No reply in 30 min → family member 2. 2 h → ASHA. 6 h → PHC doctor.")
    else:
        st.write("No message today.")
with c3:
    st.subheader("ASHA / doctor")
    if info.event:
        st.write(f"Worsening started day {int(info.worsen_start_day)}, hospital visit day {int(info.admit_day)} (hidden truth, shown for the demo).")
        first = np.flatnonzero(st_[int(info.worsen_start_day):] == 2)
        st.write(f"First red: day {int(info.worsen_start_day) + int(first[0])} → **{int(info.admit_day) - int(info.worsen_start_day) - int(first[0])} days early**"
                 if len(first) else "Missed by the red alert (this happens: sensitivity is about 66 %).")
    st.line_chart(pd.DataFrame({"warning score": [r["S"] for r in sc], "red line (T)": T}).iloc[:day + 1])
    st.line_chart(g[["weight_kg"]].iloc[:day + 1])
    st.line_chart(g[["leg_z_ohm"]].iloc[:day + 1])
    st.write("Reasons today: " + ("; ".join(why) if why else "none") + f" · cause tag: {cause}")
    st.caption("Weekly SMS to the ASHA: " + P.weekly_summary(pid, g.iloc[:day + 1], st_[:day + 1]))
    rep = g.iloc[max(0, day - 29):day + 1].assign(light=[NAME[int(x)] for x in st_[max(0, day - 29):day + 1]])
    opd = (f"<h2>HridayMitra 30-day report: {pid}</h2><p>Monitoring, not diagnosis. Light today: {NAME[light]}. "
           f"Reasons: {'; '.join(why) or 'none'}. Cause tag: {cause}.</p>"
           + rep[["day", "light", "weight_kg", "leg_z_ohm", "pulse_bpm", "spo2", "night_rr", "breathless", "orthopnea"]].round(1).to_html(index=False))
    d1, d2 = st.columns(2)
    d1.download_button("OPD report (print to PDF)", opd, f"{pid}_opd_report.html", "text/html")
    d2.download_button("Export to ABDM / FHIR", json.dumps(P.fhir_bundle(pid, g.iloc[:day + 1]), indent=1), f"{pid}_fhir.json", "application/json")
    if sc[day]["guest"]:
        st.info("Today's stool reading ignored: weight does not fit this patient (guest).")

if source == "Live stool" and refresh:
    time.sleep(5); st.rerun()
