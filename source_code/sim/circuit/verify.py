"""Verify the LTspice Z1 (legs) runs against the pass criteria. Reads the .log files, no extra libraries."""
import re, csv, pathlib, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = pathlib.Path(__file__).parent
R5 = 220.0
RC = [100, 1000, 3000, 10000]
FL = [0.9, 1.0, 1.1]
SEL = [0, 3.3]


def read_meas(log, name):
    txt = log.read_text(errors="ignore")
    block = txt.split(f"Measurement: {name}")[1].split("Measurement:")[0]
    vals = [float(m.group(2)) for m in re.finditer(r"^\s*(\d+)\s+([-\d.eE+]+)", block, re.M)]
    assert len(vals) == 24, (name, len(vals))
    return vals  # step order: selv fastest, then Rc, then fluid


def true_z(fl, f):
    """Model impedance between the sense points: 2 legs (Cole) + pelvis 25 ohm."""
    w = 2 * math.pi * f
    zc = 1 / (1j * w * 3.39e-9)
    re_, ri = 290 / fl, 650
    zleg = re_ * (ri + zc) / (re_ + ri + zc)
    return abs(2 * zleg + 25)


rows, res = [], {}
for f, fn in [(5e3, "z1_legs_5khz.log"), (50e3, "z1_legs_50khz.log")]:
    vpp = read_meas(D / fn, "vpp")
    ipk = read_meas(D / fn, "ipk")
    for i, v in enumerate(vpp):
        s, c, k = i % 2, (i // 2) % 4, i // 8
        res[(f, FL[k], RC[c], s)] = (v, ipk[i])
    for k, fl in enumerate(FL):
        for c, rc in enumerate(RC):
            vb, ib = res[(f, fl, rc, 0)]
            vs, _ = res[(f, fl, rc, 1)]
            zm = R5 * vb / vs
            zt = true_z(fl, f)
            rows.append(dict(f_hz=f, fluid=fl, contact_ohm=rc, z_meas=round(zm, 2), z_true=round(zt, 2),
                             err_pct=round(100 * (zm - zt) / zt, 2), body_pp_v=round(vb, 3), sense_pp_v=round(vs, 3),
                             i_peak_uA=round(ib * 1e6, 1)))

with open(D / "z1_results.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# pass criteria
max_err = max(abs(r["err_pct"]) for r in rows)
max_i = max(r["i_peak_uA"] for r in rows)
max_pk = max(r["body_pp_v"] for r in rows) / 2
min_sense_lsb = min(r["sense_pp_v"] for r in rows) / (3.3 / 4096)
print(f"max |error| over all cases : {max_err:.2f} %  (criterion <= 5 %)")
print(f"max injected current (pk)  : {max_i:.1f} uA  (target near 100-150 uA)")
print(f"max body output peak       : {max_pk:.2f} V around 1.65 V (rails 0.05-3.25, no clipping if < 1.55)")
print(f"min sense amplitude        : {min_sense_lsb:.0f} LSB pp on a 12-bit ADC")

def z(f, fl, rc):
    r = [x for x in rows if x["f_hz"] == f and x["fluid"] == fl and x["contact_ohm"] == rc][0]
    return r["z_meas"]

for f in (5e3, 50e3):
    z90, z100, z110 = z(f, 0.9, 1000), z(f, 1.0, 1000), z(f, 1.1, 1000)
    print(f"{f/1e3:>4.0f} kHz, Rc=1k: Z at -10%/0/+10% fluid = {z90:.1f} / {z100:.1f} / {z110:.1f} ohm; "
          f"+10% fluid changes Z by {100*(z110-z100)/z100:+.1f} %")
for fl in FL:
    r5, r50 = z(5e3, fl, 1000), z(50e3, fl, 1000)
    print(f"fluid {fl:.1f}: Z5/Z50 = {r5/r50:.3f}")
sig = abs(z(5e3, 1.1, 1000) - z(5e3, 1.0, 1000)) / z(5e3, 1.0, 1000) * 100
print(f"contact-resistance drift 100 ohm -> 10 k at 5 kHz: "
      f"{100*(z(5e3,1.0,10000)-z(5e3,1.0,100))/z(5e3,1.0,100):+.2f} % vs fluid +10 % effect {sig:.1f} %")

# plots
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
for fl, col in zip(FL, ["#2a6f42", "#0d6b6e", "#b3261e"]):
    xs = [r for r in rows if r["f_hz"] == 5e3 and r["fluid"] == fl]
    ax[0].plot([r["contact_ohm"] for r in xs], [r["z_meas"] for r in xs], "o-", color=col, label=f"fluid x{fl}")
    ax[0].axhline(xs[0]["z_true"], color=col, ls=":", lw=1)
    ax[1].plot([r["contact_ohm"] for r in xs], [r["err_pct"] for r in xs], "o-", color=col, label=f"fluid x{fl}")
ax[0].set_xscale("log"); ax[1].set_xscale("log")
ax[0].set_title("Measured leg Z at 5 kHz vs electrode contact\n(dotted = true model value)")
ax[0].set_xlabel("contact resistance per electrode (ohm)"); ax[0].set_ylabel("Z (ohm)"); ax[0].legend()
ax[1].set_title("Measurement error vs contact resistance"); ax[1].set_xlabel("contact resistance (ohm)")
ax[1].set_ylabel("error (%)"); ax[1].axhline(5, color="gray", ls="--"); ax[1].axhline(-5, color="gray", ls="--"); ax[1].legend()
fx = np.array(FL)
for f, col in [(5e3, "#0d6b6e"), (50e3, "#8a5300")]:
    zz = np.array([z(f, fl, 1000) for fl in FL]); ax[2].plot(fx, zz / zz[1], "o-", color=col, label=f"{f/1e3:.0f} kHz")
ax[2].set_title("Fluid sweep (contact 1 k): Z relative to baseline\nLower Z = more fluid"); ax[2].set_xlabel("fluid factor (1.1 = +10 %)")
ax[2].set_ylabel("Z / Z(baseline)"); ax[2].legend()
fig.tight_layout(); fig.savefig(D / "z1_results.png", dpi=130)
print("wrote z1_results.csv and z1_results.png")
