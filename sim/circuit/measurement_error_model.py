"""Measurement error model for the leg-impedance reading (Z1), built on the LTspice results.

LTspice gives the clean signal amplitudes (z1_results.csv). This script adds what LTspice did not:
12-bit ADC quantisation, ADC noise, mains hum, excitation drift between the two sequential
measurements, then runs the same 5 kHz Goertzel measurement the firmware will use (40 ksps, 100 ms).
Output: data/processed/measurement_error_model.json (used by the patient simulator) and a figure.
All noise levels are ASSUMPTIONS (the ESP32 ADC noise is board dependent): change them in NOISE_LSB.
Run:  python sim/circuit/measurement_error_model.py
"""
import json, pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
CSV = ROOT / "sim" / "circuit" / "z1_results.csv"
OUT = ROOT / "data" / "processed"
R5, FS, F0, T = 220.0, 40_000, 5_000, 0.1          # sense resistor, ADC rate, tone, window
LSB = 3.3 / 4096
NOISE_LSB = [2, 4, 8]                                # ADC noise (rms, in LSB): good, typical, poor
DRIFT_PCT = 0.5                                      # excitation amplitude drift between the two measurements
HUM_MV = 5.0                                         # 50 Hz mains pickup, peak
N_TRIALS = 400
rng = np.random.default_rng(42)
t = np.arange(int(FS * T)) / FS
kern = np.exp(-2j * np.pi * F0 * t)


def measure(a_pk, noise_lsb):
    """One 100 ms Goertzel amplitude estimate of a tone with peak amplitude a_pk (volts)."""
    x = 1.65 + a_pk * np.sin(2 * np.pi * F0 * t + rng.uniform(0, 2 * np.pi))
    x += HUM_MV * 1e-3 * np.sin(2 * np.pi * 50 * t + rng.uniform(0, 2 * np.pi))
    x += rng.normal(0, noise_lsb * LSB, t.size)
    x = np.round(x / LSB) * LSB                       # 12-bit quantisation
    return 2 * abs(np.dot(x, kern)) / t.size


df = pd.read_csv(CSV)
base = df[(df.f_hz == 5000) & (df.fluid == 1.0)].set_index("contact_ohm")
res = []
for nl in NOISE_LSB:
    for rc, row in base.iterrows():
        zt = row.z_true
        a_body, a_sense = row.body_pp_v / 2, row.sense_pp_v / 2
        z = []
        for _ in range(N_TRIALS):
            drift = 1 + rng.normal(0, DRIFT_PCT / 100)
            z.append(R5 * measure(a_body, nl) / measure(a_sense * drift, nl))
        z = np.array(z)
        z3 = np.median(z[: N_TRIALS // 3 * 3].reshape(-1, 3), axis=1)      # firmware takes the median of 3
        res.append(dict(noise_lsb=nl, contact_ohm=int(rc), z_true=zt,
                        bias_pct=round(100 * (z.mean() - zt) / zt, 3), sd_pct=round(100 * z.std() / zt, 3),
                        sd_pct_median3=round(100 * z3.std() / zt, 3)))
r = pd.DataFrame(res)
# fluid sensitivity from LTspice: +10 % fluid -> about -8.7 % in Z, so 1 % of fluid = 0.87 % of Z
SENS = 0.87
r["fluid_resolution_pct_pts_median3"] = (r.sd_pct_median3 / SENS).round(2)
OUT.mkdir(parents=True, exist_ok=True)
r.to_csv(OUT / "measurement_error_model.csv", index=False)
model = {"assumptions": dict(adc_bits=12, fs=FS, window_s=T, f0=F0, drift_pct=DRIFT_PCT, hum_mv_pk=HUM_MV,
                             note="noise levels are assumptions; z sensitivity from LTspice"),
         "z_sensitivity_pct_per_pct_fluid": SENS,
         "table": r.to_dict(orient="records")}
(OUT / "measurement_error_model.json").write_text(json.dumps(model, indent=2))
print(r.to_string(index=False))

fig, ax = plt.subplots(figsize=(6.2, 4))
for nl, col in zip(NOISE_LSB, ["#2a6f42", "#0d6b6e", "#b3261e"]):
    s = r[r.noise_lsb == nl]
    ax.plot(s.contact_ohm, s.sd_pct_median3, "o-", color=col, label=f"ADC noise {nl} LSB")
ax.set_xscale("log"); ax.set_xlabel("electrode contact resistance (ohm)"); ax.set_ylabel("leg-Z error, 1 sd (%)")
ax.set_title("Leg impedance reading: noise after median of 3\n(assumed ADC noise, 0.5 % excitation drift, mains hum)")
ax.legend(); fig.tight_layout(); fig.savefig(OUT / "measurement_error_model.png", dpi=130)
print("wrote", OUT / "measurement_error_model.json")
