"""Care-loop and assumption-sweep checks. Run: python -m pytest tests -q"""
import pathlib, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim" / "careloop")); sys.path.insert(0, str(ROOT / "engine"))
import careloop as C


def test_night_message_is_seen_in_the_morning():
    assert C.seen_at(23 * 60, (22, 6)) == 30 * 60          # 23:00 Monday -> 06:00 Tuesday
    assert C.seen_at(12 * 60, (22, 6)) == 12 * 60


def test_asha_never_visits_on_sunday():
    sunday_10am = (6 * 24 + 10) * 60
    assert C.next_open(sunday_10am, (9, 17)) == (7 * 24 + 9) * 60


def test_perfect_world_is_fast():
    p = C.params(sms_ok_per_try=1.0, outage_prob=0.0, phone_reachable=1.0, can_type_prob=1.0)
    s = C.summarize(C.simulate(p, n=500))
    assert s["ack_within_1h"] > 0.9 and s["never_reviewed"] < 0.12    # what is left is mostly reply 3 "patient is fine"


def test_ladder_beats_a_single_sms():
    lad = C.summarize(C.simulate(C.params(), n=1500, seed=1))
    one = C.summarize(C.simulate(C.params(escalation=False, family=1), n=1500, seed=1))
    assert lad["never_reviewed"] < one["never_reviewed"] - 0.3


def test_outage_delays_delivery():
    rng = np.random.default_rng(0)
    p = C.params(sms_ok_per_try=1.0)
    assert C.deliver(rng, 100, p, (50, 400)) == 400.5


def test_assumption_sweep_resets_guesses_between_scenarios():
    import assumption_sensitivity as S
    f0, _ = S.cohort()
    S.cohort("guest_prob", 0.5)                                 # a wild guess must not leak into the next scenario
    f1, _ = S.cohort()
    assert f0.equals(f1)
