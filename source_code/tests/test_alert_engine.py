"""Small, hand-made patients that check the alert brain's rules. Run: python -m pytest tests -q"""
import pathlib, sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "engine"))
import alert_engine as A

COLS = ["weight_kg", "leg_z_ohm", "trunk_z_ohm", "pulse_bpm", "spo2", "standup_s", "breathless", "orthopnea",
        "took_pills", "quality", "amulet_worn", "night_rr", "night_situps", "activity_min"]


def patient(n=50, worsen_from=None, seed=0):
    rng = np.random.default_rng(seed)
    d = dict(weight_kg=60 + rng.normal(0, .3, n), leg_z_ohm=600 * (1 + rng.normal(0, .01, n)), trunk_z_ohm=28 + rng.normal(0, 2, n),
             pulse_bpm=70 + rng.normal(0, 1.5, n), spo2=96 + rng.normal(0, .4, n), standup_s=2.3 + rng.normal(0, .05, n),
             breathless=np.zeros(n), orthopnea=np.zeros(n), took_pills=np.ones(n), quality=np.full(n, .9),
             amulet_worn=np.ones(n), night_rr=16 + rng.normal(0, .5, n), night_situps=np.zeros(n), activity_min=200 + rng.normal(0, 8, n))
    g = pd.DataFrame(d)
    if worsen_from is not None:
        k = np.clip((np.arange(n) - worsen_from) / 8, 0, 1)
        g["weight_kg"] += 3 * k; g["leg_z_ohm"] *= 1 - 0.10 * k; g["pulse_bpm"] += 8 * k; g["night_rr"] += 2 * k
    g.insert(0, "day", np.arange(n)); g.insert(0, "patient_id", "T1")
    return g


def test_stable_patient_stays_green():
    assert (A.make_system(4)(patient()) < 2).all()


def test_clear_worsening_turns_red_after_it_starts():
    st = A.make_system(4)(patient(worsen_from=35))
    red = np.flatnonzero(st == 2)
    assert len(red) and red[0] >= 35


def test_guest_on_the_stool_is_ignored():
    g = patient()
    g.loc[30, "weight_kg"] = 85                      # someone else steps on
    sc = A.scores(g)
    assert sc[30]["guest"] and (A.make_system(4)(g) < 2).all()


def test_toe_ring_bridging_plates_is_ignored():
    g = patient(worsen_from=35)
    clean = A.scores(g)
    g.loc[40:42, "leg_z_ohm"] *= 1.8                 # LTspice: a toe ring across the plates reads about +80 %
    sc = A.scores(g)
    assert all("leg_z_ohm" not in sc[t]["info"] or sc[t]["info"]["leg_z_ohm"][0] < 700 for t in range(40, 43))
    assert sc[42]["S"] >= 0.7 * clean[42]["S"]       # worsening still shows (only that day's leg reading is lost)


def test_no_peeking_into_the_future():
    g = patient(worsen_from=35)
    full = A.make_system(4)(g)
    g2 = g.copy(); g2.iloc[30:, 2:] = np.nan
    assert (A.make_system(4)(g2)[:30] == full[:30]).all()


def test_low_oxygen_is_red_at_once():
    g = patient(); g.loc[25, "spo2"] = 88
    assert A.make_system(4)(g)[25] == 2


def test_every_red_has_reasons():
    g = patient(worsen_from=35)
    sc = A.scores(g); st = A.lights(sc, 4)
    d0 = int(np.flatnonzero(st == 2)[0])
    cause, parts = A.explain(g, sc[d0])
    assert cause and len(parts) >= 1
