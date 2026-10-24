"""CARE-LOOP SIMULATOR: what happens AFTER a red alert, minute by minute, until a human acts.

An alert is useless if nobody reads it. This simulates the HridayMitra escalation ladder in Indian homes:
  0 min   stool turns red, speaks to the patient, SIM800L sends SMS to family member 1
          (retries every 10 min if the network fails; runs on its 18650 battery during power cuts)
  +30 min no reply -> SMS to family member 2
  +2 h    SMS to the ASHA worker (her number is on the printed ASHA card) unless the family replied 3 "fine"
          or a clinic visit is already done (a family "I will check" does not stop her: closing the loop needs a trained eye)
  +6 h    nobody has examined the patient -> SMS to the PHC doctor / helpline
  Replies: 1 = "I will check now", 2 = "need help" (jumps straight to the ASHA), 3 = "patient is fine".
  A missed call to the stool counts as reply 1 (for family members who cannot type).
Danger alerts (oxygen below 90%) skip the waiting: everyone is messaged at once, with "call 108" spoken aloud.

Outputs, per scenario, over many simulated alerts:
  time until a human ACKNOWLEDGES (any reply), time until a CLINICAL REVIEW (ASHA visit, PHC visit, doctor call),
  share reviewed within 24 h, and share reviewed BEFORE the hospital visit, using the engine's real lead times.
Every number below is a guess (ASSUMPTION) or a design choice; change it and rerun. Synthetic only.
Run:  python sim/careloop/careloop.py
"""
import pathlib, sys
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
H = 60.0                                                              # minutes per hour

# (value, source). All timings in minutes.
BASE = {
    "sms_ok_per_try":     (0.90, "ASSUMPTION: rural 2G, one SMS try gets through 90% of the time"),
    "outage_prob":        (0.15, "ASSUMPTION: 15% of alerts fall in a tower/power outage"),
    "outage_h":           ((1, 8), "ASSUMPTION: outage lasts 1-8 h"),
    "battery_flat_prob":  (0.03, "ASSUMPTION: 3% chance the 18650 is flat when the outage hits (alert waits for power)"),
    "retry_min":          (10, "design: SIM800L retries every 10 min"),
    "family":             (2, "design: two family numbers"),
    "phone_reachable":    (0.75, "ASSUMPTION: a family phone is on and nearby 75% of the time"),
    "reply_median_min":   (20, "ASSUMPTION: median 20 min to read and reply (daytime)"),
    "night":              ((22, 6), "ASSUMPTION: messages between 22:00 and 06:00 are seen in the morning"),
    "reply_mix":          ((0.70, 0.20, 0.10), "ASSUMPTION: replies 1 / 2 / 3"),
    "family_to_phc":      (0.55, "ASSUMPTION: after reply 1, 55% take the patient to the PHC / call the doctor"),
    "family_to_phc_h":    (6, "ASSUMPTION: median 6 h to get there (daytime only)"),
    "asha_reply":         (0.85, "ASSUMPTION: ASHA answers 85% of SMS"),
    "asha_reply_median_min": (60, "ASSUMPTION"),
    "asha_hours":         ((9, 17), "ASSUMPTION: ASHA visits 09:00-17:00, not on Sundays"),
    "asha_visit_h":       ((1, 4), "ASSUMPTION: visit happens 1-4 h after she replies (within her hours)"),
    "doctor_reply":       (0.60, "ASSUMPTION: PHC doctor / helpline answers 60%"),
    "doctor_reply_median_min": (180, "ASSUMPTION"),
    "escalate_min":       ((30, 120, 360), "design: family 2 at 30 min, ASHA at 2 h, doctor at 6 h"),
    "escalation":         (True, "design: the ladder is on"),
    "asha_always":        (True, "design: ASHA is told at 2 h even if the family replied 1 (only reply 3 or a done review stops it)"),
    "missed_call_reply":  (True, "design: a missed call counts as reply 1 (low literacy)"),
    "can_type_prob":      (0.70, "ASSUMPTION: 70% of family members can type a digit reply"),
    "sms_cost_inr":       (0.25, "ASSUMPTION: about Rs 0.25 per SMS on a basic plan"),
}


def lognorm(rng, median):
    return float(median * rng.lognormal(0, 0.8))


def seen_at(t, night):
    """A message arriving at minute t (from Monday 00:00) is noticed at: t, or 06:00 next morning if it is night."""
    h = (t / H) % 24
    a, b = night
    if h >= a:
        return t + (24 - h + b) * H
    if h < b:
        return t + (b - h) * H
    return t


def next_open(t, hours, sunday_off=True):
    """First minute >= t inside ASHA working hours."""
    a, b = hours
    while True:
        day, h = int(t // (24 * H)), (t / H) % 24
        if sunday_off and day % 7 == 6:
            t = (day + 1) * 24 * H + a * H
            continue
        if h < a:
            return day * 24 * H + a * H
        if h >= b:
            t = (day + 1) * 24 * H + a * H
            continue
        return t


def deliver(rng, t, p, outage):
    """Minute an SMS sent at t actually arrives, with retries and outages."""
    o0, o1 = outage
    tries = 0
    while tries < 300:
        if o0 <= t < o1:
            t = o1
        if rng.random() < p["sms_ok_per_try"]:
            return t + 0.5
        t += p["retry_min"]; tries += 1
    return np.inf


def one_alert(rng, p, t0, danger=False):
    """Simulate one alert raised at minute t0. Returns (ack_min, review_min, sms_sent), measured from t0."""
    outage = (np.inf, np.inf)
    if rng.random() < p["outage_prob"]:
        s = t0 - rng.uniform(0, 3) * H
        outage = (s, s + rng.uniform(*p["outage_h"]) * H)
        if rng.random() < p["battery_flat_prob"]:
            t0 = max(t0, outage[1])                                     # stool is dead until power returns
    sms, events = 0, []                                                 # events: (time, kind) kind = ack / review
    e1, e2, e3 = (0, 0, 0) if danger else p["escalate_min"]
    if not p["escalation"]:
        e1 = e2 = e3 = np.inf

    def family(t_send):
        nonlocal sms
        sms += 1
        t = deliver(rng, t_send, p, outage)
        if rng.random() > p["phone_reachable"]:
            return None
        if not (rng.random() < p["can_type_prob"] or p["missed_call_reply"]):
            return None
        t = seen_at(t, p["night"]) + lognorm(rng, p["reply_median_min"])
        reply = rng.choice([1, 2, 3], p=p["reply_mix"])
        events.append((t, "ack"))
        if reply == 1 and rng.random() < p["family_to_phc"]:
            events.append((next_open(t + lognorm(rng, p["family_to_phc_h"] * H), (8, 20), False), "review"))
        return t, reply

    f1 = family(t0)
    f2 = family(t0 + e1) if p["family"] >= 2 and (f1 is None or f1[0] > t0 + e1) else None
    acks = [f for f in (f1, f2) if f]
    t_ack = min([f[0] for f in acks], default=np.inf)
    need_help = [f[0] for f in acks if f[1] == 2]
    said_fine = any(f[1] == 3 and f[0] <= t0 + e2 for f in acks)
    reviewed_early = min([t for t, k in events if k == "review"], default=np.inf) <= t0 + e2
    silent = t_ack > t0 + e2
    want = danger or need_help or silent or (p["asha_always"] and not said_fine and not reviewed_early)
    t_asha = min([t0 + e2] + ([t_ack] if danger else []) + need_help) if want and np.isfinite(e2) else np.inf
    if np.isfinite(t_asha):
        sms += 1
        t = deliver(rng, t_asha, p, outage)
        if rng.random() < p["asha_reply"]:
            t = next_open(t, p["asha_hours"]) + lognorm(rng, p["asha_reply_median_min"])
            events.append((t, "ack"))
            events.append((next_open(t + rng.uniform(*p["asha_visit_h"]) * H, p["asha_hours"]), "review"))
    reviewed = min([t for t, k in events if k == "review"], default=np.inf)
    if reviewed > t0 + e3 and np.isfinite(e3):
        sms += 1
        t = deliver(rng, t0 + e3, p, outage)
        if rng.random() < p["doctor_reply"]:
            t = next_open(t, (9, 17), False) + lognorm(rng, p["doctor_reply_median_min"])
            events += [(t, "ack"), (t, "review")]
    ack = min([t for t, k in events if k == "ack"], default=np.inf) - t0
    rev = min([t for t, k in events if k == "review"], default=np.inf) - t0
    return ack, rev, sms


def simulate(p, n=5000, seed=0, danger=False, leads=None):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        day = int(rng.integers(0, 7))
        hour = rng.uniform(0, 24) if danger else rng.uniform(7, 10)   # red is raised at the morning check-in
        t0 = (day * 24 + hour) * H
        ack, rev, sms = one_alert(rng, p, t0, danger)
        lead_h = 24 * float(rng.choice(leads)) if leads is not None else np.nan
        rows.append(dict(ack_h=ack / H, review_h=rev / H, sms=sms, before_visit=rev / H < lead_h))
    return pd.DataFrame(rows)


def summarize(r):
    fin = lambda x: x[np.isfinite(x)]
    return dict(median_ack_h=round(float(np.median(r.ack_h)), 2),
                ack_within_1h=round(float((r.ack_h <= 1).mean()), 3),
                median_review_h=round(float(np.median(r.review_h)), 1),
                review_within_24h=round(float((r.review_h <= 24).mean()), 3),
                never_reviewed=round(float(np.isinf(r.review_h).mean()), 3),
                reviewed_before_visit=round(float(r.before_visit.mean()), 3),
                p90_review_h=round(float(np.percentile(fin(r.review_h.to_numpy()), 90)), 1) if len(fin(r.review_h.to_numpy())) else np.nan,
                sms_per_alert=round(float(r.sms.mean()), 2))


def params(**changes):
    p = {k: v for k, (v, _) in BASE.items()}
    p.update(changes)
    return p


SCENARIOS = [
    ("Rural, full ladder (default)", {}, False),
    ("Urban (better network, closer clinic)", dict(sms_ok_per_try=0.98, outage_prob=0.05, phone_reachable=0.85, family_to_phc_h=3), False),
    ("Rural, older ladder: ASHA only if family silent", dict(asha_always=False), False),
    ("Rural, ONE SMS to one family member, no ladder", dict(escalation=False, family=1), False),
    ("Rural, ladder but no missed-call reply", dict(missed_call_reply=False), False),
    ("Rural, long outages (40%, 4-12 h)", dict(outage_prob=0.40, outage_h=(4, 12)), False),
    ("Rural, family phones mostly off (40% reachable)", dict(phone_reachable=0.40), False),
    ("Rural, ASHA post vacant (never answers)", dict(asha_reply=0.0), False),
    ("Rural, everything bad at once", dict(outage_prob=0.40, outage_h=(4, 12), phone_reachable=0.40, asha_reply=0.5, doctor_reply=0.3), False),
    ("DANGER alert (oxygen < 90%), any hour, rural", {}, True),
]


def red_leads():
    """Lead days of caught real-world events with the frozen v2 engine (cached)."""
    f = ROOT / "reports/realworld_red_leads.csv"
    if not f.exists():
        import json
        sys.path.insert(0, str(ROOT / "engine"))
        import evaluate as E, alert_engine as A
        T = json.loads((ROOT / "engine/frozen_params_v2.json").read_text())["T"]
        feats = pd.read_csv(ROOT / "data/processed/realworld/daily_features.csv")
        pats = pd.read_csv(ROOT / "data/processed/realworld/patients.csv")
        ids = pats[pats.event].patient_id
        r = E.run(A.make_system(T), feats[feats.patient_id.isin(ids)], pats[pats.event], check_no_peeking=False)
        r[r.caught == True][["patient_id", "lead"]].to_csv(f, index=False)
    return pd.read_csv(f).lead.to_numpy()


if __name__ == "__main__":
    leads = red_leads()
    rows = []
    for name, ch, danger in SCENARIOS:
        s = summarize(simulate(params(**ch), danger=danger, leads=leads))
        rows.append(dict(scenario=name, **s))
        print(rows[-1], flush=True)
    out = pd.DataFrame(rows)
    fa, true_alerts = 0.061, 0.10 * 0.66 / 6        # frozen v2 real-world: false alerts / pt-month; caught events / pt-month
    cost = (fa + true_alerts) * out.sms_per_alert.iloc[0] * BASE["sms_cost_inr"][0]
    out.to_csv(ROOT / "reports/careloop_results.csv", index=False)
    pd.set_option("display.width", 250)
    print(out.to_string(index=False))
    print(f"\nlead days used (caught real-world events): n={len(leads)}, median {np.median(leads)}")
    print(f"SMS cost: about Rs {cost:.3f} per patient per month for alerts (plus daily summaries if enabled)")
