"""Raw-signal checks: known synthetic inputs must give the known answer, bad inputs must give 'no reading'."""
import pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "engine"))
import signals as S


def test_impedance_recovers_known_value_with_hum():
    for z in (300, 600, 1000):
        body, ref = S.make_z(z, hum_mv=20)
        got, why = S.impedance(body, ref)
        assert why == "ok" and abs(got / z - 1) < 0.005


def test_open_plate_is_rejected():
    body, ref = S.make_z(600, hum_mv=300)        # floating 10 Mohm input: hum saturates the amplifier
    assert S.impedance(body, ref)[0] is None


def test_trunk_formula():
    assert S.trunk(578.5, 658.4, 646.4, 646.4) == (646.4 + 646.4 - 578.5 - 658.4) / 2
    assert S.trunk(1, 2, None, 4) is None


def test_pulse_and_spo2():
    for bpm, spo2 in ((60, 97), (90, 93), (110, 88)):
        hr, s, why = S.pulse_spo2(*S.make_ppg(bpm, spo2))
        assert why == "ok" and abs(hr - bpm) < 2 and abs(s - spo2) < 1.5


def test_no_finger():
    red, ir = S.make_ppg(70, 97)
    assert S.pulse_spo2(red * 0.01, ir * 0.01)[0] is None


def test_breathing_rate_and_movement():
    for rpm in (12, 18, 26):
        got, why = S.breathing(S.make_breath(rpm))
        assert why == "ok" and abs(got - rpm) < 1
    assert S.breathing(S.make_breath(16) + np.random.default_rng(1).normal(0, 0.2, 1200))[0] is None


def test_situps_counted_once_each():
    pitch = [5] * 10 + [70, 65, 72] + [10] * 5 + [80] * 3 + [20] * 3
    assert S.situps(pitch) == 2
