"""ASSUMPTION SENSITIVITY: every guess (ASSUMPTION) in the pretend patients is pushed LOW and HIGH, a fresh cohort is
made, and the FROZEN v2 engine and the SCALE-HF weight rule are graded on it. No retuning anywhere.
Same random seed in every scenario, so differences come from the changed guess, not from luck.
It answers: "if our guess is wrong, does the result fall apart?" and "do we still beat the weight rule?"
Run:  python engine/assumption_sensitivity.py
Output: reports/assumption_sensitivity.csv, reports/assumption_tornado.png
"""
import json, pathlib, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine")); sys.path.insert(0, str(ROOT / "sim" / "patients"))
import evaluate as E, alert_engine as A, baselines as B, make_patients as MP

DEFAULTS = dict(MP.P)                                 # workers are reused: reset the guesses before every scenario
T = json.loads((ROOT / "engine/frozen_params_v2.json").read_text())["T"]
N, DAYS, EVENTS, SEED = 300, 90, 0.4, 44             # fresh seed: not the cohort the threshold was tuned on

# parameter: (low, high). "leg_sd_x" scales the circuit noise from the LTspice error model.
SWEEP = {
    "ramp_exponent":          (1.0, 2.5),
    "worsen_lead_days":       ((3, 5), (7, 10)),
    "weight_silent_fraction": (0.20, 0.50),
    "silent_leg_response":    (0.0, 0.5),
    "weight_day_sd_kg":       (0.30, 0.70),
    "fluid_peak_fraction":    ((0.03, 0.08), (0.10, 0.20)),
    "leg_bio_noise_pct":      (0.75, 3.0),
    "leg_sd_x":               (1.0, 4.0),
    "trunk_noise_ohm":        (2.0, 8.0),
    "hr_gain_bpm":            ((1.0, 4.0), (4.0, 10.0)),
    "hr_day_sd_bpm":          (1.5, 4.0),
    "rr_gain":                ((0.6, 1.2), (2.0, 3.0)),
    "symptom_peak_prob":      (0.25, 0.75),
    "situps_peak":            (1.0, 4.0),
    "infection_fraction":     (0.05, 0.30),
    "salty_meals_per_patient": (1, 5),
    "pill_miss_episodes":     (0.5, 3.0),
    "missing_day_prob":       (0.03, 0.20),
    "amulet_worn_prob":       (0.60, 0.98),
    "guest_prob":             (0.0, 0.03),
    "wet_feet_prob":          (0.0, 0.15),
    "jewellery_step_prob":    (0.0, 0.30),
    "button_error_prob":      (0.0, 0.10),
}


def cohort(param=None, value=None):
    MP.P.clear(); MP.P.update(DEFAULTS)
    leg_sd = MP.leg_measurement_sd()
    if param == "leg_sd_x":
        leg_sd *= value
    elif param:
        MP.P[param] = (value, MP.P[param][1])
    rng = np.random.default_rng(SEED)
    n_ev = round(N * EVENTS)
    flags = rng.permutation([True] * n_ev + [False] * (N - n_ev))
    # one random stream per patient: a changed guess cannot reshuffle the other patients (fair comparison)
    out = [MP.simulate_patient(f"S{i:04d}", np.random.default_rng([SEED, i]), DAYS, bool(ev), leg_sd) for i, ev in enumerate(flags, 1)]
    return pd.concat([o[0] for o in out]), pd.DataFrame([o[2] for o in out])


def scenario(job):
    param, side, value = job
    f, p = cohort(param, value)
    s = E.summarize(E.run(A.make_system(T), f, p, check_no_peeking=False))
    b = E.summarize(E.run(B.weight_rule_1, f, p, check_no_peeking=False))
    return dict(parameter=param or "(default guesses)", side=side, value=str(value),
                default=str(DEFAULTS[param][0]) if param in DEFAULTS else ("1.0" if param else ""),
                sensitivity=round(s["sensitivity"], 3), specificity=round(s["specificity"], 4),
                median_lead_days=s["median_lead_days"], false_alerts_per_patient_month=round(s["false_alerts_per_patient_month"], 3),
                rule1_sensitivity=round(b["sensitivity"], 3), rule1_fa=round(b["false_alerts_per_patient_month"], 3))


def tornado(df):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    base = df[df.side == "base"].iloc[0]
    d = df[df.side != "base"].pivot(index="parameter", columns="side", values="sensitivity")
    d["swing"] = (d["low"] - d["high"]).abs()
    d = d.sort_values("swing")
    fig, ax = plt.subplots(1, 2, figsize=(12, 7), sharey=True)
    y = np.arange(len(d))
    for side, col in (("low", "#4C78A8"), ("high", "#F58518")):
        ax[0].barh(y, d[side] - base.sensitivity, left=base.sensitivity, color=col, alpha=.85, label=f"guess pushed {side}")
    ax[0].axvline(base.sensitivity, color="k", lw=1)
    rule = df[df.side != "base"].pivot(index="parameter", columns="side", values="rule1_sensitivity").loc[d.index]
    ax[0].scatter(rule.min(axis=1), y, marker="|", s=120, color="grey", label="weight rule (worst/best)")
    ax[0].scatter(rule.max(axis=1), y, marker="|", s=120, color="grey")
    ax[0].set_yticks(y, d.index); ax[0].set_xlabel("sensitivity (frozen v2 engine)"); ax[0].legend(loc="lower right", fontsize=8)
    fa = df[df.side != "base"].pivot(index="parameter", columns="side", values="false_alerts_per_patient_month").loc[d.index]
    for side, col in (("low", "#4C78A8"), ("high", "#F58518")):
        ax[1].barh(y, fa[side] - base.false_alerts_per_patient_month, left=base.false_alerts_per_patient_month, color=col, alpha=.85)
    ax[1].axvline(base.false_alerts_per_patient_month, color="k", lw=1)
    ax[1].axvline(0.21, color="red", ls="--", lw=1, label="false-alert budget"); ax[1].legend(fontsize=8)
    ax[1].set_xlabel("false alerts per patient-month")
    fig.suptitle("If our guesses are wrong: frozen engine, no retuning (synthetic data)")
    fig.tight_layout(); fig.savefig(ROOT / "reports/assumption_tornado.png", dpi=130)


if __name__ == "__main__":
    jobs = [(None, "base", None)] + [(k, side, val) for k, (lo, hi) in SWEEP.items() for side, val in (("low", lo), ("high", hi))]
    with ProcessPoolExecutor() as pool:
        rows = list(pool.map(scenario, jobs))
    df = pd.DataFrame(rows)
    df["beats_rule1_sens"] = df.sensitivity > df.rule1_sensitivity
    df["within_fa_budget"] = df.false_alerts_per_patient_month <= 0.21
    df.to_csv(ROOT / "reports/assumption_sensitivity.csv", index=False)
    tornado(df)
    pd.set_option("display.width", 250)
    print(df.to_string(index=False))
    sc = df[df.side != "base"]
    print(f"\nscenarios: {len(sc)}  beats weight rule on sensitivity: {sc.beats_rule1_sens.sum()}  "
          f"lower false alerts than rule: {(sc.false_alerts_per_patient_month < sc.rule1_fa).sum()}  "
          f"within FA budget: {sc.within_fa_budget.sum()}  sensitivity range {sc.sensitivity.min()}-{sc.sensitivity.max()}")
