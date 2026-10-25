"""SCORING: how we grade any alert system on the pretend patients. Written once, used for every system.

A "system" is a function: it gets ONE patient's daily table and returns one state per day:
    0 = green (nothing), 1 = amber (check again), 2 = red (alert).
It may only use that day and earlier days (no peeking at the future). The grader checks this rule.

The four PS numbers
  sensitivity   = share of sick patients (hospital visit) that got a red alert while they were getting worse
  specificity   = share of NORMAL days with no red alert
  median lead   = days between the first red alert and the hospital visit (middle value)
  false alerts  = red alert episodes during normal days, per patient per month (30 days)

Definitions (fixed here, so nobody can change them to look better):
  worsening window  = day W (worsening starts) to day V-1 (day before the hospital visit)
  caught            = red on at least one day inside the worsening window
  normal days       = every day of stable patients + the days of sick patients BEFORE W
  false alert       = one run of red days that starts on a normal day (a long run counts once)
  days before EVAL_FROM are not scored (the system is still learning the patient's normal)
"""
import numpy as np
import pandas as pd

EVAL_FROM = 14


def score_patient(states, p):
    """states: array of 0/1/2 per day. p: this patient's row from patients.csv."""
    n = len(states)
    d = np.arange(n)
    red = (np.asarray(states) == 2) & (d >= EVAL_FROM)
    onset = red & ~np.r_[False, red[:-1]]                   # first day of each red run
    if p.event:
        W, V = int(p.worsen_start_day), int(p.admit_day)
        in_win = red & (d >= W) & (d <= V - 1)
        caught = bool(in_win.any())
        lead = float(V - d[in_win][0]) if caught else np.nan
        normal = (d >= EVAL_FROM) & (d < W)
    else:
        caught, lead = None, np.nan
        normal = d >= EVAL_FROM
    return dict(event=bool(p.event), caught=caught, lead=lead,
                false_alerts=int((onset & normal).sum()), normal_days=int(normal.sum()),
                red_normal_days=int((red & normal).sum()))


def run(system, feats, pats, check_no_peeking=True):
    """Grade `system` on every patient. Returns one row per patient."""
    pats = pats.set_index("patient_id", drop=False)
    rows = []
    for pid, g in feats.groupby("patient_id", sort=False):
        g = g.reset_index(drop=True)
        s = np.asarray(system(g))
        if check_no_peeking:                                 # change the future: yesterday's answer must not change
            cut = len(g) // 2
            g2 = g.copy()
            g2.iloc[cut:, 2:] = np.nan
            s2 = np.asarray(system(g2))
            assert (s[:cut] == s2[:cut]).all(), f"system looked into the future on {pid}"
        rows.append(dict(patient_id=pid, **score_patient(s, pats.loc[pid])))
    return pd.DataFrame(rows)


def summarize(r):
    ev = r[r.event]
    nd = r.normal_days.sum()
    return dict(events=len(ev),
                sensitivity=float(ev.caught.astype(float).mean()),
                specificity=float(1 - r.red_normal_days.sum() / nd),
                median_lead_days=float(ev.lead.median()),
                false_alerts_per_patient_month=float(r.false_alerts.sum() / (nd / 30)))


def bootstrap(r, n=1000, seed=0):
    """95 % range by re-drawing patients with replacement (patients, not days, are the unit)."""
    rng = np.random.default_rng(seed)
    out = []
    idx = np.arange(len(r))
    for _ in range(n):
        out.append(summarize(r.iloc[rng.choice(idx, len(idx))]))
    b = pd.DataFrame(out)
    return {k: (float(b[k].quantile(0.025)), float(b[k].quantile(0.975))) for k in b.columns if k != "events"}


def report(name, r):
    s, ci = summarize(r), bootstrap(r, 400)
    return dict(system=name, **{k: round(v, 3) for k, v in s.items()},
                **{f"{k}_ci": f"{lo:.2f}-{hi:.2f}" for k, (lo, hi) in ci.items()})
