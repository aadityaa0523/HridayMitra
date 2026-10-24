"""BASELINES: simple published weight rules. Our system must beat these, and they also test that
the pretend patients behave like real ones (calibration). Both return red (2) or green (0) per day.

Rule 1 ("SCALE-HF comparator"): alert if weight rose more than 1.4 kg since the last reading,
        or more than 2.3 kg compared with about a week ago. (published rule, SCALE-HF 1 comparison)
Rule 2 ("MACD", Gyllensten 2016): alert if the 9-day average weight is more than 0.62 kg above the 20-day average.
Both use ONLY weight, with no identity check, so a guest on the scale fools them (real scales have this problem).
"""
import numpy as np
import pandas as pd


def weight_rule_1(g):
    w = g["weight_kg"].to_numpy()
    n = len(w)
    out = np.zeros(n, int)
    last = np.nan
    for t in range(n):
        if np.isnan(w[t]):
            continue
        week = w[max(0, t - 8): max(0, t - 5) + 1]           # readings about 5-8 days ago
        week = week[~np.isnan(week)]
        day_gain = w[t] - last if not np.isnan(last) else 0.0
        week_gain = w[t] - week.mean() if len(week) else 0.0
        if day_gain > 1.4 or week_gain > 2.3:
            out[t] = 2
        last = w[t]
    return out


def weight_rule_macd(g, short=9, long=20, thr=0.62):
    w = pd.Series(g["weight_kg"].to_numpy())
    out = np.zeros(len(w), int)
    for t in range(len(w)):
        s, l = w[max(0, t - short + 1): t + 1].dropna(), w[max(0, t - long + 1): t + 1].dropna()
        if len(s) >= 3 and len(l) >= 10 and s.mean() - l.mean() > thr:
            out[t] = 2
    return out
