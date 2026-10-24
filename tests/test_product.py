"""Product features: doctor's plan, coaching, two users, nudges, weekly summary, FHIR export."""
import datetime as dt, pathlib, sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "engine"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import alert_engine as A, product as P
from test_alert_engine import patient


def test_doctor_plan_triggers():
    assert P.plan_message([0, 0, 2]) == P.DEFAULT_PLAN["red"]
    assert P.plan_message([0, 1, 1]) == P.DEFAULT_PLAN["amber2"]
    assert P.plan_message([1, 0, 1]) is None and P.plan_message([]) is None


def test_coaching_missed_tablets_and_fluid():
    g = patient(worsen_from=35)
    g.loc[44:45, "took_pills"] = 0
    sc = A.scores(g)
    assert "Tablets" in P.coaching(g, sc[46])
    g = patient(worsen_from=35)
    assert "luid" in P.coaching(g, A.scores(g)[45])
    assert P.coaching(patient(), A.scores(patient())[40]) is None


def test_two_users_and_guest():
    prof = {"P001": (62.0, 600.0), "P002": (48.0, 720.0)}
    assert P.identify(62.8, 590, prof) == "P001"
    assert P.identify(47.1, 735, prof) == "P002"
    assert P.identify(80.0, 620, prof) is None               # guest
    assert P.identify(61.0, 760, prof) is None               # right weight, wrong body: not P001


def test_nudge_once_after_11():
    now = dt.datetime(2026, 10, 25, 11, 5)
    assert P.nudge_due(now, dt.date(2026, 10, 24), False)
    assert not P.nudge_due(now, now.date(), False) and not P.nudge_due(now, dt.date(2026, 10, 24), True)
    assert not P.nudge_due(now.replace(hour=9), dt.date(2026, 10, 24), False)


def test_weekly_summary_and_fhir():
    g = patient(n=20)
    g.loc[17, "weight_kg"] = np.nan
    s = P.weekly_summary("P001", g, np.zeros(20, int))
    assert "6/7 check-ins" in s and "G-G" in s
    b = P.fhir_bundle("P001", g.head(2))
    obs = [e["resource"] for e in b["entry"]]
    assert b["resourceType"] == "Bundle" and all(o["resourceType"] == "Observation" for o in obs)
    assert any(o["code"]["coding"] and o["code"]["coding"][0]["code"] == "29463-7" for o in obs)
