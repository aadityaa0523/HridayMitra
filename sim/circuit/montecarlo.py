"""MONTE CARLO: do 100 stools built from cheap local-shop parts, on 100 different bodies, still measure correctly?

Each simulated "device" gets its own random part values (tolerances below), its own body size and eight random electrode
contacts (dry to sweaty skin). It is measured on all 4 paths at normal fluid and at +10 % fluid (legs and chest).
The random values are drawn in Python and written into LTspice with table(), so all 8 runs of one device share them.
Two questions:
  1. ABSOLUTE error: is the ohm reading right? (part tolerance of R5 sets a fixed gain error per device)
  2. CHANGE error: is a +10 % fluid change measured as the right % change? This is what the alert engine uses, because it
     compares each patient with their OWN baseline on the SAME device, so fixed per-device errors cancel.
Also a jewellery test: a metal toe ring bridging the inject and sense plates of one foot.
Run:  python sim/circuit/montecarlo.py        Out: montecarlo_results.csv, jewellery_results.csv, montecarlo.png
"""
import csv, math, pathlib, re
import numpy as np
import trunk_paths as TP

D = pathlib.Path(__file__).parent
N, SEED = 100, 7
# name: (nominal, tolerance as a fraction, distribution). Typical cheap parts: 1 % metal film for R5, 5 % carbon for the
# rest, 20 % ceramic/electrolytic capacitors. Temperature 15-45 C at 100 ppm/C adds 0.3 % to resistors (folded in).
TOL = {"r3": (100e3, .05), "r4": (4.7e3, .05), "r5": (220, .013), "r6": (1e3, .05), "r7": (1e3, .05),
       "r8": (10e6, .05), "r9": (10e6, .05), "r11": (1.5e3, .05), "c2": (1e-6, .2), "c3": (1e-6, .2), "c4": (1e-6, .2),
       "c5": (10e-9, .1), "gain": (10, .005), "amp": (0.83, .08)}
ELEMENT = {"R3": "r3", "R4": "r4", "R5": "r5", "R6": "r6", "R7": "r7", "R8": "r8", "R9": "r9", "R11": "r11",
           "C2": "c2", "C3": "c3", "C4": "c4", "C5": "c5"}


def draw():
    rng = np.random.default_rng(SEED)
    runs = []
    for _ in range(N):
        r = {k: v * (1 + rng.uniform(-t, t)) for k, (v, t) in TOL.items()}
        r["cmrr"] = rng.choice([-1, 1]) * 10 ** (-rng.uniform(60, 80) / 20)     # INA126: 60-80 dB at 5 kHz
        r["sz"] = rng.uniform(0.7, 1.4)                                         # small to large adult
        r["ibp"], r["ibn"] = rng.uniform(5e-9, 25e-9, 2)                        # INA126 input bias current (max 25 nA)
        for limb in TP.LIMBS:
            for e in "is":
                r[f"rc{e}{limb}"] = float(np.exp(rng.uniform(np.log(200), np.log(10e3))))   # each plate on its own
        runs.append(r)
    return runs


def table(name, runs):
    pairs = ",".join(f"{i},{r[name]:.6g}" for i, r in enumerate(runs, 1))
    return f".param {name}=table(run,{pairs})"


def mc_netlist(runs, steps, title, extra=""):
    txt = TP.netlist(5e3, lambda per: steps, title)
    out = []
    for line in txt.splitlines():
        tok = line.split()
        if tok and tok[0] in ELEMENT:
            tok[-1] = "{" + ELEMENT[tok[0]] + "}"
            line = " ".join(tok)
        elif tok and re.match(r"^(Re|Ri)(LH|RH|LF|RF|T)$", tok[0]):
            tok[-1] = "{" + tok[-1].strip("{}") + "*sz}"
            line = " ".join(tok)
        elif tok and re.match(r"^Cm(LH|RH|LF|RF|T)$", tok[0]):
            tok[-1] = "{" + tok[-1] + "/sz}"
            line = " ".join(tok)
        elif tok and re.match(r"^Rc[is](LH|RH|LF|RF)$", tok[0]):
            tok[-1] = "{rc" + tok[0][2] + tok[0][3:] + "}"
            line = " ".join(tok)
        elif line.startswith("Vdac"):
            line = "Vdac dac 0 SIN(1.65 {amp} {f})"
        elif line.startswith("Bina"):
            line = "Bina ina 0 V=limit(V(vref)+{gain}*(V(inp)-V(inn))+{gain}*{cmrr}*((V(inp)+V(inn))/2-V(vref)),0.05,3.25)"
        elif line.startswith("Vsel"):
            line = "Vsel sel 0 PULSE(0 3.3 0.02 1u 1u 0.02 0.1)"
        elif line.startswith(".param f="):
            line = ".param f=5000 path=1 fx=1\n.param fl={fx} ft={fx}"
        out.append(line)
    extra = chr(10).join(["Ibp sa 0 {ibp}", "Ibn sb 0 {ibn}", extra])    # bias current flows out of each INA input
    names = list(TOL) + ["cmrr", "sz", "ibp", "ibn"] + [f"rc{e}{l}" for l in TP.LIMBS for e in "is"]
    body = "\n".join(out).replace(".end", "\n".join(table(n, runs) for n in names) + "\n" + extra + "\n.end")
    return body


STEPS = [".tran 0 0.04 0 5u", ".save V(adc) V(ina)",
         ".meas TRAN amax MAX V(ina) FROM=0.008 TO=0.039", ".meas TRAN amin MIN V(ina) FROM=0.008 TO=0.039",
         ".step param fx list 1 1.1", ".step param path list 1 2 3 4", f".step param run 1 {N} 1",
         ".meas TRAN vbody PP V(adc) FROM=0.008 TO=0.019",
         ".meas TRAN vsens PP V(adc) FROM=0.028 TO=0.039",
         ".meas TRAN zmeas PARAM 220*vbody/vsens"]


def jewellery():
    """Metal toe ring bridging inject and sense plates of the left foot (path 1, legs). Fixed nominal parts."""
    runs = [dict({k: v for k, (v, _) in TOL.items()}, cmrr=0.0, sz=1.0, ibp=10e-9, ibn=10e-9, **{f"rc{e}{l}": 1000.0 for l in TP.LIMBS for e in "is"})]
    steps = [".tran 0 0.04 0 5u", ".step param rj list 1 10 100 1k 1G", ".param run=1",
             ".meas TRAN vbody PP V(adc) FROM=0.008 TO=0.019", ".meas TRAN vsens PP V(adc) FROM=0.028 TO=0.039",
             ".meas TRAN zmeas PARAM 220*vbody/vsens"]
    cir = D / "jewellery.cir"
    cir.write_text(mc_netlist(runs, steps, "jewellery: toe ring bridging the left-foot plates", "Rj iLF sLF {rj}"))
    z = TP.read_meas(TP.run(cir), "zmeas", 5)
    zt = TP.true_z(1, 1.0, 5e3)
    rows = [dict(ring_ohm=rj, z_meas=round(v, 2), z_true=round(zt, 2), err_pct=round(100 * (v - zt) / zt, 2))
            for rj, v in zip(["1", "10", "100", "1k", "none"], z)]
    with open(D / "jewellery_results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(f"  toe ring {r['ring_ohm']:>4} ohm between plates: {r['z_meas']} ohm ({r['err_pct']:+.2f} %)")


def pct(a, q):
    return float(np.percentile(np.abs(a), q))


if __name__ == "__main__":
    runs = draw()
    cir = D / "montecarlo_5khz.cir"
    cir.write_text(mc_netlist(runs, STEPS, f"Monte Carlo, {N} devices x 4 paths x 2 fluid levels"))
    log = TP.run(cir)
    z = TP.read_meas(log, "zmeas", 8 * N)
    amax, amin = TP.read_meas(log, "amax", 8 * N), TP.read_meas(log, "amin", 8 * N)
    rows = []
    for d, r in enumerate(runs):
        zz = {(p, fx): z[d * 8 + pi * 2 + k] for pi, p in enumerate(TP.PATHS) for k, fx in enumerate((1.0, 1.1))}
        tr = {fx: (zz[(3, fx)] + zz[(4, fx)] - zz[(1, fx)] - zz[(2, fx)]) / 2 for fx in (1.0, 1.1)}
        true = {(p, fx): r["sz"] * TP.true_z(p, fx, 5e3, fl=fx) for p in TP.PATHS for fx in (1.0, 1.1)}
        ttr = {fx: r["sz"] * TP.true_trunk(fx, 5e3) for fx in (1.0, 1.1)}
        row = dict(device=d + 1, size=round(r["sz"], 3), r5_err_pct=round(100 * (r["r5"] / 220 - 1), 3),
                   contact_min=round(min(v for k, v in r.items() if k.startswith("rc"))),
                   contact_max=round(max(v for k, v in r.items() if k.startswith("rc"))))
        for p in TP.PATHS:
            row[f"z{p}_abs_err_pct"] = round(100 * (zz[(p, 1.0)] / true[(p, 1.0)] - 1), 3)
            meas_chg, true_chg = zz[(p, 1.1)] / zz[(p, 1.0)] - 1, true[(p, 1.1)] / true[(p, 1.0)] - 1
            row[f"z{p}_change_err_pts"] = round(100 * (meas_chg - true_chg), 3)
        row["trunk_abs_err_pct"] = round(100 * (tr[1.0] / ttr[1.0] - 1), 3)
        row["trunk_change_err_pts"] = round(100 * ((tr[1.1] / tr[1.0] - 1) - (ttr[1.1] / ttr[1.0] - 1)), 3)
        row["trunk_ohm"], row["leg_change_meas_pct"] = round(tr[1.0], 2), round(100 * (zz[(1, 1.1)] / zz[(1, 1.0)] - 1), 2)
        rows.append(row)
    with open(D / "montecarlo_results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    col = lambda k: np.array([r[k] for r in rows])
    zabs = np.concatenate([col(f"z{p}_abs_err_pct") for p in TP.PATHS])
    zchg = np.concatenate([col(f"z{p}_change_err_pts") for p in TP.PATHS])
    zcorr = np.concatenate([col(f"z{p}_abs_err_pct") + col("r5_err_pct") for p in TP.PATHS])
    print(f"{N} devices, {8 * N} LTspice runs, bias resistors {TOL['r8'][0] / 1e6:g} Mohm, INA bias current 5-25 nA")
    print(f"amplifier output range over all runs: {min(amin):.2f} to {max(amax):.2f} V (clips at 0.05 / 3.25)")
    print(f"Z1-Z4 absolute error      : p50 {pct(zabs, 50):.2f} %  p99 {pct(zabs, 99):.2f} %  worst {pct(zabs, 100):.2f} %")
    print(f"  after 1-point calibration (R5 known): p99 {pct(zcorr, 99):.2f} %  worst {pct(zcorr, 100):.2f} %")
    print(f"Z1-Z4 +10% fluid CHANGE   : p99 {pct(zchg, 99):.3f} pts  worst {pct(zchg, 100):.3f} pts (true change about -8 to -9 %)")
    print(f"trunk absolute error      : p99 {pct(col('trunk_abs_err_pct'), 99):.2f} %  worst {pct(col('trunk_abs_err_pct'), 100):.2f} %")
    print(f"trunk +10% fluid CHANGE   : p99 {pct(col('trunk_change_err_pts'), 99):.2f} pts  worst {pct(col('trunk_change_err_pts'), 100):.2f} pts")
    print("jewellery:")
    jewellery()

    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(14, 4))
    ax[0].hist(zabs, bins=30, color="#0d6b6e"); ax[0].set_title("absolute error, Z1-Z4 (%)")
    ax[0].set_xlabel("mostly the 1 % tolerance of R5 (fixed per device)")
    ax[1].hist(zchg, bins=30, color="#2a6f42"); ax[1].set_title("error of a +10 % fluid CHANGE (% points)")
    ax[1].set_xlabel("what the alert engine actually uses")
    ax[2].scatter(col("contact_max"), col("trunk_abs_err_pct"), s=12, color="#b3261e")
    ax[2].set_xscale("log"); ax[2].set_xlabel("worst electrode contact on the device (ohm)"); ax[2].set_title("trunk absolute error (%)")
    fig.suptitle(f"LTspice Monte Carlo: {N} devices from 5 % parts, random body size and skin contact")
    fig.tight_layout(); fig.savefig(D / "montecarlo.png", dpi=130)
