"""Cost simulation checks. Run: python -m pytest tests/test_cost_sim.py -q"""
import pathlib, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cost_sim as C


def test_parsed_totals_match_the_guide():
    items, guide = C.load_parts()
    assert abs(items.low.sum() - guide[0]) <= 5 and abs(items.high.sum() - guide[1]) <= 5


def test_probability_valid_and_deterministic():
    items, _ = C.load_parts()
    t1 = C.simulate(items).sum(axis=1)
    assert 0 <= (t1 <= C.LIMIT).mean() <= 1 and t1.max() <= items.high.sum() + 1e-6   # build cost never above all-high prices
    assert np.array_equal(t1, C.simulate(items).sum(axis=1))
