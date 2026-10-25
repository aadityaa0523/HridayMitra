"""ALERT BRAIN: learns each patient's own normal and warns when several signs drift the wrong way.

Day by day, for one patient, using ONLY today and earlier days:
  1. Guest check   : if today's weight jumps more than 2.5 kg from the recent median, it is probably someone else
                     standing on the stool, so today's stool readings are ignored (and logged as "guest").
  2. Normal        : for every signal, the patient's normal = median of their readings 7 to 35 days ago
                     (the 7-day gap stops a slow worsening from becoming the new normal).
  3. How far off   : today's level (average of the last 3 days) compared with normal, in "spread units" (robust z).
                     Only the BAD direction counts (weight up, leg reading down, pulse up...), so one good number
                     cannot hide a bad one.
  4. Families      : fluid (weight, leg, chest), heart-lungs (pulse, night breathing, oxygen),
                     daily life (activity, stand-up speed, night sit-ups, symptom answers).
                     Family score = strongest sign + half of the second strongest.
  5. Total score S : sum of the three family scores.
  6. Lights        : AMBER if S >= 0.6 x T (please check again).
                     RED if S >= T on 2 of the last 3 days AND at least 2 families agree (two witnesses),
                     or one family stays very high (>= T) for 3 days in a row.
                     Red stays on until S falls below 0.4 x T (no flickering).
                     Danger rule: oxygen below 90 % -> red at once.
  7. Why           : every red comes with its top reasons in plain words and a cause tag.
T is the only tuned number. It is tuned on training patients and then frozen (see tune_and_test.py).
"""
import numpy as np
import pandas as pd

# column: (family, bad direction, minimum spread, spread is relative to the normal level?, weight in its family)
SIGNALS = {
    "weight_kg":    ("fluid", +1, 0.30, False, 1.0),
    "leg_z_ohm":    ("fluid", -1, 0.010, True, 1.0),
    "trunk_z_ohm":  ("fluid", -1, 3.0, False, 0.5),
    "leg_ewi":      ("fluid", +1, 0.003, True, 1.0),     # extracellular-water index (spectroscopy); position/temperature cancel
    "pulse_bpm":    ("heart_lungs", +1, 2.0, False, 1.0),
    "night_rr":     ("heart_lungs", +1, 0.7, False, 1.0),
    "spo2":         ("heart_lungs", -1, 0.7, False, 0.5),
    "activity_min": ("daily_life", -1, 0.08, True, 1.0),
    "standup_s":    ("daily_life", +1, 0.04, True, 1.0),
}
STOOL = ["weight_kg", "leg_z_ohm", "trunk_z_ohm", "leg_ewi", "pulse_bpm", "spo2", "standup_s"]
FAMILIES = ["fluid", "heart_lungs", "daily_life"]
WORDS = {"weight_kg": ("weight", "kg", 1), "leg_z_ohm": ("leg reading", "%", 0), "trunk_z_ohm": ("chest reading", "%", 0), "leg_ewi": ("leg water outside cells", "%", 1),
         "pulse_bpm": ("resting pulse", "bpm", 0), "night_rr": ("night breathing", "per min", 1), "spo2": ("oxygen", "%", 1),
         "activity_min": ("activity", "%", 0), "standup_s": ("stand-up time", "%", 0)}
GUEST_JUMP_KG, BASE_FROM, BASE_TO, MIN_BASE = 2.5, 35, 7, 6
PLATE_JUMP = 0.25            # leg reading more than 25 % from last week's median = plates bridged or badly placed


CUSUM_K, CUSUM_SCALE = 0.5, 2.0   # drift detector: ignore daily drifts under 0.5 spread; 2 spreads of build-up = 1 z


def scores(g, cusum=False, k=CUSUM_K, scale=CUSUM_SCALE):
    """Per-day scores for one patient (no thresholds yet). Uses only past and present rows.
    cusum=True adds a slow-drift detector: small bad changes that keep coming add up day after day, so a steady
    worsening is noticed before any single day looks alarming (Gyllensten 2016 used this for impedance)."""
    g = g.reset_index(drop=True)
    n = len(g)
    vals = {c: (g[c].to_numpy(float).copy() if c in g else np.full(len(g), np.nan)) for c in SIGNALS}
    drift = {c: 0.0 for c in SIGNALS}
    guest = np.zeros(n, bool)
    w = vals["weight_kg"]
    for t in range(n):                                         # 1. guest check
        if np.isnan(w[t]):
            continue
        prev = w[max(0, t - 7):t]
        prev = prev[~np.isnan(prev)]
        if len(prev) >= 3 and abs(w[t] - np.median(prev)) > GUEST_JUMP_KG:
            guest[t] = True
            for c in STOOL:
                if c in vals:
                    vals[c][t] = np.nan
    z = vals["leg_z_ohm"]
    for t in range(n):                                         # plate check: a toe ring bridging plates reads +58..86 %
        prev = z[max(0, t - 7):t]                              # (LTspice jewellery test); no body changes that fast
        prev = prev[~np.isnan(prev)]
        if len(prev) >= 3 and abs(z[t] / np.median(prev) - 1) > PLATE_JUMP:
            z[t] = np.nan
            vals["trunk_z_ohm"][t] = np.nan
            vals["leg_ewi"][t] = np.nan
    answered = (g["breathless"].notna() | g["orthopnea"].notna()).to_numpy()
    yes =(g["breathless"].fillna(0).to_numpy() + g["orthopnea"].fillna(0).to_numpy())
    sit = g["night_situps"].to_numpy(float)
    rows = []
    for t in range(n):
        z, info = {}, {}
        for c, (fam, sgn, floor, rel, wt) in SIGNALS.items():
            base = vals[c][max(0, t - BASE_FROM): max(0, t - BASE_TO + 1)]
            base = base[~np.isnan(base)]
            lvl = vals[c][max(0, t - 2): t + 1]
            lvl = lvl[~np.isnan(lvl)]
            if len(base) < MIN_BASE or len(lvl) == 0:
                continue
            med = np.median(base)
            spread = max(1.4826 * np.median(np.abs(base - med)), floor * (abs(med) if rel else 1))
            dz = (lvl.mean() - med) / spread * sgn                       # 3. bad direction only
            if cusum and not np.isnan(vals[c][t]):
                drift[c] = max(0.0, drift[c] + (vals[c][t] - med) / spread * sgn - k)
                dz = max(dz, drift[c] / scale)
            z[c] = wt * float(np.clip(dz, 0, 5))
            info[c] = (lvl.mean(), med)
        sym = yes[max(0, t - 2): t + 1].sum()                          # symptom "yes" answers, last 3 days
        s3 = sit[max(0, t - 2): t + 1]
        s3 = s3[~np.isnan(s3)]
        z["symptoms"] = 1.2 * max(0.0, sym - 1)
        if len(s3):
            z["night_situps"] = 1.0 * max(0.0, s3.sum() - 1)
        fam_of = lambda c: SIGNALS[c][0] if c in SIGNALS else "daily_life"
        fam = {}
        for f in FAMILIES:                                              # 4. families
            zz = sorted([v for c, v in z.items() if fam_of(c) == f], reverse=True)
            fam[f] = (zz[0] + 0.5 * zz[1]) if len(zz) > 1 else (zz[0] if zz else 0.0)
        has_data = any(not np.isnan(vals[c][t]) for c in SIGNALS) or answered[t]       # no check-in today: hold the light
        learning = not any(c in z for c in SIGNALS)                    # cold start: no personal normal yet (first ~10 days)
        rows.append(dict(day=t, S=sum(fam.values()), n_fam=sum(v >= 1.5 for v in fam.values()),
                         max_fam=max(fam.values()), danger=bool(g["spo2"].iloc[t] < 90) if not guest[t] else False,
                         guest=guest[t], data=has_data, learning=learning, z=z, info=info, **{f"fam_{f}": fam[f] for f in FAMILIES}))
    return rows


def lights(sc, T):
    """Turn scores into 0 green / 1 amber / 2 red, with two-witness, persistence and hysteresis."""
    out, red, high, fam_high = [], False, [], []
    for r in sc:
        high.append(r["S"] >= T)
        fam_high.append(r["max_fam"] >= T)
        if not r["data"]:                                               # nothing measured today: keep yesterday's light
            out.append(out[-1] if out else 0)
            continue
        if r["danger"]:
            red = True
        elif red:
            red = r["S"] >= 0.4 * T                                     # hysteresis: clear only when well below
        else:
            red = (sum(high[-3:]) >= 2 and r["n_fam"] >= 2) or (len(fam_high) >= 3 and all(fam_high[-3:]))
        out.append(2 if red else (1 if r["S"] >= 0.6 * T else 0))
    return np.array(out)


def explain(g, r):
    """Plain-words reasons for one day's scores, plus a cause tag."""
    parts = []
    for c, v in sorted(r["z"].items(), key=lambda kv: -kv[1])[:3]:
        if v < 1:
            continue
        if c == "symptoms":
            parts.append("breathless or extra pillows reported")
        elif c == "night_situps":
            parts.append("sitting up at night")
        else:
            name, unit, dec = WORDS[c]
            lvl, med = r["info"][c]
            delta = (lvl - med) if unit != "%" else 100 * (lvl / med - 1)
            parts.append(f"{name} {delta:+.{dec}f} {unit} vs normal")
    t = r["day"]
    took = g["took_pills"].iloc[max(0, t - 4): t + 1]
    if (took == 0).any():
        cause = "after missed medicine"
    elif r["fam_heart_lungs"] >= 2 and r["fam_fluid"] < 1:
        cause = "infection-like (pulse and breathing up, fluid steady)"
    elif r["fam_fluid"] >= 1.5:
        cause = "heart-failure-like (fluid building)"
    else:
        cause = "unclear: please check"
    return cause, parts


def make_system(T, cusum=False, k=CUSUM_K, scale=CUSUM_SCALE):
    return lambda g: lights(scores(g, cusum, k, scale), T)
