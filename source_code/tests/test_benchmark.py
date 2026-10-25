"""Benchmark v2 and the hybrid engine: the scorer rejects malformed submissions and reproduces the leaderboard, and
the frozen hybrid never looks at future days."""
import json, pathlib, sys
import pandas as pd
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine")); sys.path.insert(0, str(ROOT / "benchmark"))
import evaluate as E, hybrid as H, bench
from score import score

SUB = ROOT / "benchmark/submissions/hridaymitra_hybrid_test.csv"


def test_scorer_rejects_bad_submissions():
    sub = pd.read_csv(SUB)
    with pytest.raises(ValueError):
        score(sub.iloc[1:], "test", n_boot=10)                     # a missing patient-day
    with pytest.raises(ValueError):
        score(sub.assign(light=sub.light.replace(2, 3)), "test", n_boot=10)


def test_scorer_reproduces_the_leaderboard():
    lb = pd.read_csv(ROOT / "benchmark/leaderboard.csv")
    row = lb[(lb.split == "test") & lb.system.str.startswith("HridayMitra hybrid")].iloc[0]
    assert score(pd.read_csv(SUB), "test", n_boot=10)["sensitivity"] == pytest.approx(row.sensitivity)


def test_hybrid_is_causal_and_within_budget_on_dev():
    P = json.loads(H.FROZEN.read_text())
    assert P["dev_false_alerts"] <= H.FA_BUDGET
    f, p = bench.split("test")
    ids = p.patient_id.iloc[:12]
    E.run(H.make_system(P), f[f.patient_id.isin(ids)], p[p.patient_id.isin(ids)], check_no_peeking=True)
