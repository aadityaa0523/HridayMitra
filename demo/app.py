"""HridayMitra demo: one pretend patient through the FROZEN v2 alert engine, seen by the patient, the family and the
ASHA/doctor, with "break it" switches that add real-life mess live. Synthetic data only. Monitoring, not diagnosis.
Run:  streamlit run demo/app.py
"""
import json, pathlib, sys
import numpy as np
import pandas as pd
import streamlit as st
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import alert_engine as A

T = json.loads((ROOT / "engine/frozen_params_v2.json").read_text())["T"]
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
with st.sidebar:
    pid = st.selectbox("Patient", sick[:20] + p[~p.event].patient_id.tolist()[:10])
    st.subheader("Break it")
    guest = st.checkbox("A guest sits on the stool (day 40)")
    ring = st.checkbox("Toe ring touches both plates (days 50-52)")
    cut = st.checkbox("Power cut: no check-ins for 4 days before the visit")
    amulet = st.checkbox("Amulet not worn for the last 10 days")

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
day = st.slider("Day", 14, len(g) - 1, len(g) - 1)
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
with c2:
    st.subheader("Family (SMS)")
    if light == 2:
        st.code(f"HridayMitra: {pid} RED on day {day}.\nWhy: {'; '.join(why) or 'several signs together'}.\n"
                f"Possible cause: {cause}.\nReply 1 = I am checking, 2 = need help, 3 = patient is fine.\n"
                "Not a diagnosis. If breathless at rest, call 108.", language=None)
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
    if sc[day]["guest"]:
        st.info("Today's stool reading ignored: weight does not fit this patient (guest).")
