"""PRETEND PATIENTS: makes a fake (synthetic) group of heart-failure patients, day by day.

Why: we are not allowed to collect data from real people, so we build pretend patients whose
numbers behave like the ones in published studies. Some patients get sicker on purpose, starting
3 to 10 days before a hospital visit. The alert brain (later) is tested on them.

How it works, in plain words:
  1. Every patient has a hidden number called "congestion" (fluid build-up). 0 = fine, 1 = very sick.
  2. Congestion makes weight go up, the leg reading go down, pulse go up, and so on.
  3. Then we add real-life mess: normal day-to-day ups and downs, salty meals, infection,
     missed pills, a guest standing on the stool, wet feet, missing days, noisy readings.
  4. The stool and the amulet only "see" the final numbers, never the hidden congestion.

Run:  python sim/patients/make_patients.py --patients 200 --days 60 --seed 42
Output (in data/processed/): daily_features.csv  patients.csv  labels.csv  truth_daily.csv  DATA.md
"""
import argparse, hashlib, json, pathlib, zlib
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------------------------
# 1. EVERY NUMBER WE CHOOSE, AND WHERE IT COMES FROM.  (value, source)
#    "published" = from a paper we read. "LTspice" = from our own circuit simulation.
#    "ASSUMPTION" = our guess. Change a number here and everything updates.
# ---------------------------------------------------------------------------------------------
P = {
    "warmup_days":           (30,          "design: first days are the patient's normal, no worsening yet"),
    "worsen_lead_days":      ((3, 10),     "problem statement: worsening starts 3 to 10 days before the hospital visit"),
    "ramp_exponent":         (1.5,         "ASSUMPTION: worsening shape; 1 = straight line, above 1 = slow start, fast end"),
    "weight_gain_kg":        ((1.0, 4.5),  "published: Chaudhry 2007, gains of 2-10 lb in the days before admission"),
    "weight_silent_fraction": (0.35,       "published (rough): many admissions show no weight gain (FAST trial, Gyllensten 2016)"),
    "silent_gain_kg":        ((0.0, 0.5),  "ASSUMPTION: weight-silent patients gain almost nothing"),
    "weight_day_sd_kg":      (0.42,        "ASSUMPTION: normal day-to-day weight wobble"),
    "leg_z_pct_per_fluid_pct": (0.87,      "LTspice: +10% leg fluid lowers the 5 kHz leg reading by about 8.7%"),
    "fluid_peak_fraction":   ((0.05, 0.15), "ASSUMPTION: leg fluid up 5-15% at the worst point"),
    "silent_leg_response":   (1.0,         "KEY ASSUMPTION: the leg reading still falls fully in weight-silent patients (1.0). TEST with 0.5 and 0.0"),
    "leg_bio_noise_pct":     (1.5,         "ASSUMPTION: the body itself changes by about 1.5% day to day"),
    "trunk_drop_per_fluid":  (0.6,         "ASSUMPTION: chest reading falls 0.6 x the fluid fraction (weak, very noisy signal)"),
    "trunk_noise_ohm":       (4.0,         "ASSUMPTION: subtracting four readings amplifies noise (trunk is only about 25 ohm)"),
    "hr_gain_bpm":           ((2.0, 8.0),  "published (rough): resting heart rate rises 3-8 bpm before events (WEARIT-France, van Es 2025)"),
    "hr_day_sd_bpm":         (2.5,         "ASSUMPTION"),
    "spo2_drop":             ((0.0, 2.0),  "ASSUMPTION"),
    "rr_gain":               ((1.2, 2.2),  "published: night breathing rate +1.5 to 2.1 per minute (NOTICE-HF)"),
    "activity_drop":         ((0.10, 0.25), "published (rough): activity falls 10-25% (Kelly 2020)"),
    "situps_peak":           (2.5,         "ASSUMPTION: extra night sit-ups at the worst point"),
    "symptom_peak_prob":     (0.5,         "published (rough): orthopnea/night breathlessness about 52% sensitive as symptoms"),
    "infection_fraction":    (0.15,        "ASSUMPTION: 15% of patients have an infection episode"),
    "infection_hr_bpm":      ((8, 15),     "published pattern: infection raises pulse more than heart failure does (Gardner 2021)"),
    "infection_rr":          ((2.0, 4.0),  "ASSUMPTION"),
    "salty_meals_per_patient": (2,         "ASSUMPTION: about 2 salty-meal days per patient"),
    "salty_weight_kg":       ((0.5, 1.5),  "ASSUMPTION: a salty meal adds 0.5-1.5 kg that fades in 2 days"),
    "pill_miss_episodes":    (1.0,         "ASSUMPTION: about one missed-pill episode per patient"),
    "pills_cause_fraction":  (0.35,        "ASSUMPTION: 35% of events are triggered by missed pills"),
    "guest_prob":            (0.01,        "CALIBRATED: was 3%; weight-rule false alerts were 3x the published rate (almost all from guest days), so 1%"),
    "wet_feet_prob":         (0.05,        "ASSUMPTION: 5% of days feet are wet"),
    "jewellery_step_prob":   (0.10,        "ASSUMPTION: 10% of patients change jewellery once (leg reading shifts 1-3%)"),
    "missing_day_prob":      (0.07,        "ASSUMPTION: 7% of days nobody does the check"),
    "amulet_worn_prob":      (0.90,        "ASSUMPTION: amulet is worn on 90% of days"),
    "button_error_prob":     (0.03,        "ASSUMPTION: 3% of button answers are wrong"),
    "ewi_icw_ecw_person_sd": (0.15,        "ASSUMPTION: people differ 15% in cell-water vs outside-water resistance (Ri/Re)"),
    "ewi_bio_noise_pct":     (0.4,         "ASSUMPTION: day-to-day change of the extracellular-water index that is NOT position/temperature (those cancel in the ratio, LTspice)"),
    "ewi_meas_noise_pct":    (0.1,         "ASSUMPTION: 3-frequency Cole-fit noise (Goertzel SNR at 50 kHz is about 0.03%; margin added)"),
}
v = lambda key: P[key][0]


def leg_measurement_sd():
    """How noisy is the leg reading from our circuit? Read it from the circuit error model."""
    f = ROOT / "data" / "processed" / "measurement_error_model.json"
    if not f.exists():
        return 0.0035
    rows = [r for r in json.loads(f.read_text())["table"] if r["noise_lsb"] == 4]
    return float(np.mean([r["sd_pct_median3"] for r in rows])) / 100


def ar1(rng, n, sd, phi=0.7):
    """A wobble that remembers yesterday a little (bad days come in runs). sd = overall size."""
    x, out = 0.0, np.zeros(n)
    for i in range(n):
        x = phi * x + rng.normal(0, sd * np.sqrt(1 - phi ** 2))
        out[i] = x
    return out


def episodes(rng, n, count, length, first=0):
    """A True/False list over the days with `count` runs of True, each `length` days long."""
    m = np.zeros(n, bool)
    for _ in range(count):
        s = int(rng.integers(first, max(first + 1, n)))
        m[s:s + int(rng.integers(length[0], length[1], endpoint=True))] = True
    return m


def simulate_patient(pid, rng, days, is_event, leg_sd):
    warm = v("warmup_days")
    # ---- who is this person? ----
    age, sex = int(np.clip(rng.normal(66, 9), 40, 90)), str(rng.choice(["F", "M"]))
    sens = float(np.clip(rng.lognormal(0, 0.25), 0.5, 1.8))          # how strongly this body reacts
    w0 = float(np.clip(rng.normal(62, 10), 40, 100)); z0 = float(np.clip(rng.normal(600, 80), 400, 900))
    t0 = float(np.clip(rng.normal(28, 5), 15, 45)); hr0 = float(np.clip(rng.normal(72, 8), 50, 100))
    spo0 = float(np.clip(rng.normal(96, 1.2), 92, 99)); rr0 = float(np.clip(rng.normal(16, 1.8), 11, 22))
    act0 = float(np.clip(rng.normal(210, 45), 80, 350)); st0 = float(np.clip(rng.normal(2.3, 0.4), 1.2, 4.0))

    # ---- the sickness story ----
    V = W = None
    if is_event:
        lead = int(rng.integers(*v("worsen_lead_days"), endpoint=True))
        V = int(rng.integers(warm + 10, days - 2, endpoint=True))      # hospital visit day
        W = V - lead                                                     # worsening starts here
    n = V + 1 if is_event else days                                      # data stops at admission
    d = np.arange(n)
    silent = bool(is_event and rng.random() < v("weight_silent_fraction"))
    gain = rng.uniform(*(v("silent_gain_kg") if silent else v("weight_gain_kg")))
    fluid_peak = float(np.clip(rng.uniform(*v("fluid_peak_fraction")) * sens, 0.02, 0.22))

    pill_missed = episodes(rng, n, rng.poisson(v("pill_miss_episodes")), (1, 3))
    cause = "hf"
    if is_event and rng.random() < v("pills_cause_fraction"):
        pill_missed[max(0, W - 3):W] = True                              # pills missed just before it started
        cause = "pills"
    c = np.zeros(n)
    if is_event:
        run = (d >= W) & (d <= V)
        c[run] = ((d[run] - W) / (V - W)) ** v("ramp_exponent")                         # slow start, faster near the end
    c_pill = np.clip(0.05 * np.convolve(pill_missed.astype(float), np.ones(5))[:n], 0, 0.2)
    cong = np.clip(c + c_pill, 0, 1.3)                                    # THE HIDDEN NUMBER

    infection = np.zeros(n, bool)
    if rng.random() < v("infection_fraction"):
        infection = episodes(rng, n, 1, (3, 7), first=10)
    salty = np.zeros(n)
    for s in rng.integers(5, n, size=v("salty_meals_per_patient")):
        salty[s] += rng.uniform(*v("salty_weight_kg"))
        if s + 1 < n:
            salty[s + 1] += 0.5 * salty[s]

    # ---- real-life mess ----
    missing = (rng.random(n) < v("missing_day_prob")) | episodes(rng, n, int(rng.random() < 0.15), (2, 3))
    guest = (rng.random(n) < v("guest_prob")) & ~missing
    wet = (rng.random(n) < v("wet_feet_prob")) & ~missing
    quality = np.clip(rng.beta(8, 2, n) - 0.3 * wet, 0, 1)
    no_read = quality < 0.5                                               # bad contact: "no reading"
    jewel = np.zeros(n)
    if rng.random() < v("jewellery_step_prob"):
        jewel[int(rng.integers(5, n)):] = rng.choice([-1, 1]) * rng.uniform(0.01, 0.03)

    fluid = cong * fluid_peak
    # ---- the numbers the stool would show ----
    weight = w0 + ar1(rng, n, v("weight_day_sd_kg")) + gain * cong + salty
    leg_fluid = fluid * (v("silent_leg_response") if silent else 1.0)
    leg = (z0 * (1 + jewel) * (1 - v("leg_z_pct_per_fluid_pct") * leg_fluid)
           * (1 + ar1(rng, n, v("leg_bio_noise_pct") / 100)) * (1 + rng.normal(0, leg_sd, n))
           * (1 - wet * rng.uniform(0.03, 0.06, n)))
    trunk = t0 * (1 - v("trunk_drop_per_fluid") * fluid) + rng.normal(0, v("trunk_noise_ohm"), n)
    pulse = (hr0 + ar1(rng, n, v("hr_day_sd_bpm")) + rng.uniform(*v("hr_gain_bpm")) * cong
             + infection * rng.uniform(*v("infection_hr_bpm")))
    spo2 = np.clip(spo0 + rng.normal(0, 0.6, n) - rng.uniform(*v("spo2_drop")) * cong
                   - infection * rng.uniform(0, 2), 85, 100)
    standup = st0 * (1 + 0.15 * cong) * (1 + rng.normal(0, 0.05, n))
    p_sym = v("symptom_peak_prob")
    breath = rng.random(n) < (0.03 + p_sym * cong ** 1.5 + 0.2 * infection)
    orthop = rng.random(n) < (0.02 + 0.9 * p_sym * cong ** 1.5)
    err = lambda a: np.where(rng.random(n) < v("button_error_prob"), ~a, a)
    breath, orthop, took = err(breath).astype(float), err(orthop).astype(float), err(~pill_missed).astype(float)

    # a guest shows someone else's numbers
    weight = np.where(guest, rng.normal(70, 12, n), weight)
    leg = np.where(guest, rng.normal(620, 100, n), leg)
    trunk = np.where(guest, rng.normal(28, 6, n), trunk)
    pulse = np.where(guest, rng.normal(76, 9, n), pulse)

    stool = pd.DataFrame(dict(weight_kg=weight, leg_z_ohm=leg, trunk_z_ohm=trunk, pulse_bpm=pulse, spo2=spo2,
                              standup_s=standup, breathless=breath, orthopnea=orthop, took_pills=took, quality=quality))
    stool.loc[no_read, ["leg_z_ohm", "trunk_z_ohm", "pulse_bpm", "spo2"]] = np.nan
    stool.loc[missing, :] = np.nan
    worn = rng.random(n) < v("amulet_worn_prob")
    amulet = pd.DataFrame(dict(
        amulet_worn=worn.astype(float),
        night_rr=rr0 + rng.normal(0, 1.0, n) + rng.uniform(*v("rr_gain")) * cong + infection * rng.uniform(*v("infection_rr")),
        night_situps=rng.poisson(0.1 + v("situps_peak") * cong ** 1.5).astype(float),
        activity_min=act0 * (1 - rng.uniform(*v("activity_drop")) * cong - 0.25 * infection) + rng.normal(0, 15, n)))
    amulet.loc[~worn, ["night_rr", "night_situps", "activity_min"]] = np.nan
    feats = pd.concat([stool, amulet], axis=1).round(3)
    # spectroscopy: extracellular-water index Rinf/R0 of the legs (engine/bis.py, sim/circuit/spectroscopy.py). Its own
    # random stream, so adding it changes no other column. Position / temperature / contact cancel in the ratio.
    rng_e = np.random.default_rng([zlib.crc32(pid.encode()), 7])
    re0, ri0 = 289.25, 650.0 * float(rng_e.lognormal(0, v("ewi_icw_ecw_person_sd")))
    re_t = re0 / (1 + leg_fluid)
    ewi = ri0 / (re_t + ri0)
    ewi = ewi * (1 + ar1(rng_e, n, v("ewi_bio_noise_pct") / 100)) * (1 + rng_e.normal(0, v("ewi_meas_noise_pct") / 100, n))
    ewi = np.where(guest, rng_e.normal(0.69, 0.04, n), ewi)
    ewi[no_read | missing] = np.nan
    feats["leg_ewi"] = np.round(ewi, 5)
    feats.insert(0, "day", d); feats.insert(0, "patient_id", pid)
    truth = pd.DataFrame(dict(patient_id=pid, day=d, congestion=cong.round(4), guest=guest, wet_feet=wet,
                              infection=infection, salty_gain_kg=salty.round(2), pill_missed=pill_missed,
                              no_check_in=missing, no_reading=no_read))
    row = dict(patient_id=pid, sex=sex, age=age, event=is_event, worsen_start_day=W, admit_day=V,
               lead_days=(V - W) if is_event else None, weight_silent=silent, event_cause=cause if is_event else "",
               weight0_kg=round(w0, 1), leg_z0_ohm=round(z0), sensitivity=round(sens, 2), n_days=n)
    return feats, truth, row


def write_datacard(out, args, sha):
    lines = ["# Dataset card: HridayMitra pretend patients (synthetic)", "",
             f"Made by `sim/patients/make_patients.py` with seed {args.seed}. Fully fake: no real person is in this data.", "",
             f"- Patients: {args.patients}. Days per stable patient: {args.days}. Patients with a hospital visit: "
             f"{args.event_fraction:.0%}; their data ends on the visit day.",
             f"- First {v('warmup_days')} days are normal (the patient's baseline). Worsening starts 3-10 days before the visit.",
             "- Files: `daily_features.csv` (what the devices report; empty cell = no reading), `patients.csv` (who, truth about events),",
             "  `labels.csv` (answer key for testing), `truth_daily.csv` (hidden truth: congestion, guest, infection... never given to the alert brain).",
             f"- Reproducible: same seed gives the same files. SHA-256 of daily_features.csv: `{sha}`", "",
             "## Every parameter and where it comes from", "", "| Parameter | Value | Source |", "|---|---|---|"]
    lines += [f"| {k} | {val} | {src} |" for k, (val, src) in P.items()]
    lines += ["", f"Leg-reading measurement noise ({leg_measurement_sd():.2%}) comes from `sim/circuit/measurement_error_model.py`.", "",
              "## What this data is NOT", "",
              "- It is not real patient data and does not prove clinical accuracy. It only shows that an alert system can find the",
              "  patterns we put in, and how it copes with mess (missing days, guests, infection, missed pills).",
              "- Every value marked ASSUMPTION is our guess. The test reports must show results when these guesses change.",
              "- Not modelled yet: atrial fibrillation, medicine changes, seasons, a calibration against published alert rates."]
    (out / "DATA.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patients", type=int, default=200)
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--event-fraction", type=float, default=0.6)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="data/processed")
    ap.add_argument("--silent-leg-response", type=float, default=None, help="test the key assumption (default 1.0)")
    args = ap.parse_args()
    if args.silent_leg_response is not None:
        P["silent_leg_response"] = (args.silent_leg_response, P["silent_leg_response"][1])
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    rng, leg_sd = np.random.default_rng(args.seed), leg_measurement_sd()
    n_event = round(args.patients * args.event_fraction)
    flags = rng.permutation([True] * n_event + [False] * (args.patients - n_event))
    feats, truths, rows = [], [], []
    for i, ev in enumerate(flags, 1):
        f, t, r = simulate_patient(f"P{i:04d}", rng, args.days, bool(ev), leg_sd)
        feats.append(f); truths.append(t); rows.append(r)
    feats, truths, pat = pd.concat(feats), pd.concat(truths), pd.DataFrame(rows)
    feats.to_csv(out / "daily_features.csv", index=False)
    truths.to_csv(out / "truth_daily.csv", index=False)
    pat.to_csv(out / "patients.csv", index=False)
    pat[["patient_id", "worsen_start_day", "admit_day"]].to_csv(out / "labels.csv", index=False)
    sha = hashlib.sha256((out / "daily_features.csv").read_bytes()).hexdigest()[:16]
    write_datacard(out, args, sha)
    print(f"{args.patients} patients ({n_event} with a hospital visit), {len(feats)} patient-days -> {out}")
    print("sha256(daily_features.csv) =", sha)


if __name__ == "__main__":
    main()
