"""Look at the pretend patients: print simple facts and draw a picture of 6 patients.
Run:  python sim/patients/check_patients.py      (after make_patients.py)
"""
import pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / "data" / "processed"
f, pat, tr = (pd.read_csv(D / n) for n in ["daily_features.csv", "patients.csv", "truth_daily.csv"])
ev = pat[pat.event]

print(f"patients: {len(pat)}   with hospital visit: {len(ev)} ({len(ev)/len(pat):.0%})   patient-days: {len(f)}")
print(f"worsening starts {ev.lead_days.min():.0f} to {ev.lead_days.max():.0f} days before the visit (PS rule: 3 to 10)")
print(f"weight-silent events: {ev.weight_silent.mean():.0%} (target about 35%)")
print("share of days with no reading, per number:")
print((f[["weight_kg", "leg_z_ohm", "trunk_z_ohm", "pulse_bpm", "spo2", "night_rr"]].isna().mean() * 100).round(1).to_string())

# how much does each number move between normal days and the day before the visit?
rows = []
for _, p in ev.iterrows():
    g = f[f.patient_id == p.patient_id].set_index("day")
    base, last = g.loc[:29], g.loc[int(p.admit_day) - 1: int(p.admit_day)]
    rows.append(dict(silent=p.weight_silent,
                     d_weight=last.weight_kg.mean() - base.weight_kg.mean(),
                     d_leg_pct=100 * (last.leg_z_ohm.mean() / base.leg_z_ohm.mean() - 1),
                     d_pulse=last.pulse_bpm.mean() - base.pulse_bpm.mean()))
m = pd.DataFrame(rows)
print("\nChange from normal to the day before the visit (average over patients):")
print(m.groupby("silent").mean().round(2).rename(index={False: "weight rises", True: "weight-silent"}).to_string())

# picture
rng = np.random.default_rng(1)
pick = list(ev[~ev.weight_silent].patient_id.sample(2, random_state=1)) + list(ev[ev.weight_silent].patient_id.sample(1, random_state=1)) \
    + list(pat[~pat.event].patient_id.sample(3, random_state=1))
fig, ax = plt.subplots(3, 6, figsize=(18, 7), sharex=True)
for j, pid in enumerate(pick):
    g, p = f[f.patient_id == pid], pat[pat.patient_id == pid].iloc[0]
    for i, (col, lab) in enumerate([("weight_kg", "weight (kg)"), ("leg_z_ohm", "leg reading (ohm)"), ("pulse_bpm", "pulse (bpm)")]):
        ax[i, j].plot(g.day, g[col], ".-", color="#0d6b6e", lw=1, ms=3)
        if p.event:
            ax[i, j].axvline(p.worsen_start_day, color="#8a5300", ls="--"); ax[i, j].axvline(p.admit_day, color="#b3261e")
        if j == 0: ax[i, j].set_ylabel(lab)
    tag = ("event, weight-silent" if p.weight_silent else "event") if p.event else "stable"
    ax[0, j].set_title(f"{pid}  {tag}", fontsize=10)
for a in ax[2]: a.set_xlabel("day")
fig.suptitle("Pretend patients (dashed = worsening starts, red = hospital visit)")
fig.tight_layout(); fig.savefig(ROOT / "reports" / "patients_sample.png", dpi=110)
print("\nwrote reports/patients_sample.png")
