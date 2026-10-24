"""PRODUCT LAYER around the alert engine (the engine's lights are unchanged; the frozen results stay valid).
Same rules as the stool firmware, so the dashboard and the stool say the same thing.

  A  plan_message()     the doctor's own sick-day plan, triggered by the light history
  C  nudge_due() / weekly_summary()   missed check-in reminder, Sunday summary for the ASHA / doctor
  D  coaching()         one practical tip from the pattern (salt, missed tablets, infection-like)
  E  identify()         two people on one stool: who is this, from weight + leg reading
  F  fhir_bundle()      export in HL7 FHIR R4, the format India's digital health mission (ABDM) uses
"""
import datetime as dt
import numpy as np

DEFAULT_PLAN = {   # set by the patient's doctor; these are placeholders, not medical advice
    "amber2": "Your doctor's plan: cut salt today, weigh again tomorrow, and call the ASHA if you feel worse.",
    "red": "Your doctor's plan: take the extra water tablet your doctor prescribed for bad days, and visit the PHC today.",
}


def plan_message(lights, plan=DEFAULT_PLAN):
    """lights: daily 0/1/2 up to today. Red today -> red plan; amber on the last 2 days -> amber plan."""
    if len(lights) and lights[-1] == 2:
        return plan["red"]
    if len(lights) >= 2 and lights[-1] == 1 and lights[-2] == 1:
        return plan["amber2"]
    return None


def coaching(g, row):
    """One tip for today. g: the patient's daily table up to today; row: the engine's scores row for today."""
    t, z = row["day"], row["z"]
    took = g["took_pills"].iloc[max(0, t - 4): t + 1]
    if (took == 0).sum() >= 2:
        return "Tablets were missed on 2 or more days this week. Keep them in the stool drawer and take them after the check-in."
    if row["fam_heart_lungs"] >= 2 and row["fam_fluid"] < 1:
        return "Pulse and breathing are up but fluid is steady: this looks like an infection. Please see the doctor."
    w = g["weight_kg"].to_numpy(float)
    if t >= 2 and not np.isnan(w[t - 1]) and not np.isnan(w[t]) and z.get("weight_kg", 0) >= 1 and z.get("leg_z_ohm", 0) < 1:
        return "Weight went up but the legs look normal: yesterday's food may have been salty. Less salt and pickle today."
    if row["fam_fluid"] >= 1.5:
        return "Fluid is building. Limit drinks to what your doctor allows and avoid salty food."
    return None


def identify(weight, leg_z, profiles, kg_tol=3.0, z_tol=0.15):
    """profiles: {user_id: (usual weight kg, usual leg reading ohm)}. Returns the closest matching user or None (guest)."""
    best, best_d = None, 1e9
    for uid, (w0, z0) in profiles.items():
        dw = abs(weight - w0) / kg_tol
        dz = abs(leg_z / z0 - 1) / z_tol if leg_z == leg_z and z0 else 0.0
        d = max(dw, dz)
        if d <= 1 and d < best_d:
            best, best_d = uid, d
    return best


def nudge_due(now, last_checkin_date, already_sent, hour=11):
    """Missed check-in reminder for the family: once a day, after 11:00, if nobody checked in today."""
    return now.hour >= hour and last_checkin_date != now.date() and not already_sent


def weekly_summary(pid, g, lights):
    """One-line Sunday SMS for the ASHA / doctor (last 7 days)."""
    last = g.tail(7)
    done = int(last["weight_kg"].notna().sum())
    marks = "".join("-" if np.isnan(w) else "GAR"[l] for w, l in zip(last["weight_kg"], lights[-len(last):]))
    w = g["weight_kg"].dropna()
    trend = w.iloc[-1] - w.iloc[-8:-1].median() if len(w) >= 8 else float("nan")
    return (f"HridayMitra weekly {pid}: {done}/7 check-ins, lights {marks}, weight {trend:+.1f} kg vs last week. "
            "Monitoring, not diagnosis.")


LOINC = {"weight_kg": ("29463-7", "Body weight", "kg"), "pulse_bpm": ("8867-4", "Heart rate", "/min"),
         "spo2": ("59408-5", "Oxygen saturation by pulse oximetry", "%"), "night_rr": ("9279-1", "Respiratory rate", "/min"),
         "leg_z_ohm": (None, "Leg bioimpedance at 5 kHz", "Ohm"), "trunk_z_ohm": (None, "Trunk bioimpedance at 5 kHz", "Ohm")}


def fhir_bundle(pid, g, start=dt.date(2026, 1, 1)):
    """FHIR R4 collection Bundle of Observations (one per measured value per day)."""
    entries = []
    for _, r in g.iterrows():
        when = (start + dt.timedelta(days=int(r["day"]))).isoformat()
        for col, (code, text, unit) in LOINC.items():
            v = r.get(col)
            if v is None or v != v:
                continue
            coding = [{"system": "http://loinc.org", "code": code, "display": text}] if code else []
            entries.append({"resource": {
                "resourceType": "Observation", "status": "final",
                "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs"}]}],
                "code": {"coding": coding, "text": text}, "subject": {"reference": f"Patient/{pid}"},
                "effectiveDateTime": when, "valueQuantity": {"value": round(float(v), 2), "unit": unit}}})
    return {"resourceType": "Bundle", "type": "collection", "entry": entries}
