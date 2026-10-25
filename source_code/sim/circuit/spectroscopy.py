"""SPECTROSCOPY PROOF in LTspice: does the leg impedance ratio |Z50|/|Z5| see extracellular fluid, and ignore the
things that change a single-frequency reading for no medical reason?

The same front end as the leg/trunk netlists (ratiometric against R5, 10 Mohm bias), legs path, at 5, 20 and 50 kHz.
Scenarios on both legs (Cole segments Re || Ri+Cm):
  0 baseline   1 extracellular fluid +10 % (Re / 1.1)   2 foot position / limb size / temperature +3 % (all tissue x 1.03)
  3 cells +10 % (intracellular water up: Ri / 1.1)     4 fluid +10 % AND position +3 % together
Run:  python sim/circuit/spectroscopy.py     Out: spectroscopy_results.csv, spectroscopy.png
"""
import csv, pathlib, re, sys
import numpy as np
import trunk_paths as TP
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))
import bis

D = pathlib.Path(__file__).parent
FREQS = [5e3, 20e3, 50e3]
SC = [("baseline", 1.0, 1.0, 1.0), ("extracellular fluid +10%", 1.1, 1.0, 1.0), ("position / limb / temperature +3%", 1.0, 1.0, 1.03),
      ("cells (intracellular water) +10%", 1.0, 1 / 1.1, 1.0), ("fluid +10% and position +3%", 1.1, 1.0, 1.03)]
LEG = TP.SEG["leg"]


def netlist(f):
    per = 1 / f
    t_end = max(0.02, 200 * per)
    steps = [f".tran 0 {t_end:g} 0 {per / 40:g}", ".step param selv list 0 3.3", f".step param sc 0 {len(SC) - 1} 1",
             f".meas TRAN vpp PP V(adc) FROM={0.4 * t_end:g} TO={t_end:g}"]
    t = TP.netlist(f, lambda p: steps, f"spectroscopy, legs path, {f / 1e3:g} kHz")
    t = t.replace(" fl=1 path=1", " path=1 sc=0")
    for limb in ("LF", "RF"):                                         # legs follow the scenario table
        t = re.sub(rf"^Re{limb} (\S+) (\S+) \S+$", rf"Re{limb} \1 \2 {{{LEG[0]:g}*geo/fl}}", t, flags=re.M)
        t = re.sub(rf"^Ri{limb} (\S+) (\S+) \S+$", rf"Ri{limb} \1 \2 {{{LEG[1]:g}*ri*geo}}", t, flags=re.M)
        t = re.sub(rf"^Cm{limb} (\S+) (\S+) \S+$", rf"Cm{limb} \1 \2 {{{LEG[2]:g}/geo}}", t, flags=re.M)
    tabs = [f".param {n}=table(sc," + ",".join(f"{k},{s[i + 1]:g}" for k, s in enumerate(SC)) + ")" for i, n in enumerate(("fl", "ri", "geo"))]
    return t.replace(".end", "\n".join(tabs) + "\n.end")


def true_z(f, fl, ri, geo):
    return abs(2 * bis.segment(f, LEG[0] * geo / fl, LEG[1] * ri * geo, LEG[2] / geo))


if __name__ == "__main__":
    meas = {}
    for f in FREQS:
        cir = D / f"spectroscopy_{f / 1e3:g}khz.cir"
        cir.write_text(netlist(f))
        v = TP.read_meas(TP.run(cir), "vpp", 2 * len(SC))
        for k in range(len(SC)):
            meas[(f, k)] = 100 * v[2 * k] / v[2 * k + 1]           # selv fastest: body, then R5
    rows = []
    for k, (name, fl, ri, geo) in enumerate(SC):
        z = [meas[(f, k)] for f in FREQS]
        fit = bis.fit_cole(FREQS, z)
        rows.append(dict(scenario=name, z5=round(z[0], 2), z20=round(z[1], 2), z50=round(z[2], 2),
                         z5_err_pct=round(100 * (z[0] / true_z(5e3, fl, ri, geo) - 1), 3),
                         z50_err_pct=round(100 * (z[2] / true_z(50e3, fl, ri, geo) - 1), 3),
                         ir=round(z[2] / z[0], 5), r0=round(fit["r0"], 2), rinf=round(fit["rinf"], 2), ewi=round(fit["ewi"], 5),
                         fit_rms_pct=round(fit["rms_error_pct"], 3)))
    base = rows[0]
    for r in rows:
        r["z5_change_pct"] = round(100 * (r["z5"] / base["z5"] - 1), 2)
        r["ir_change_pct"] = round(100 * (r["ir"] / base["ir"] - 1), 2)
        r["ewi_change_pct"] = round(100 * (r["ewi"] / base["ewi"] - 1), 2)
    with open(D / "spectroscopy_results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"{'scenario':38s} {'Z5 chg':>8s} {'IR chg':>8s} {'EWI chg':>8s} {'Z5 err':>7s} {'Z50 err':>8s} {'fit rms':>8s}")
    for r in rows:
        print(f"{r['scenario']:38s} {r['z5_change_pct']:+7.2f}% {r['ir_change_pct']:+7.2f}% {r['ewi_change_pct']:+7.2f}% "
              f"{r['z5_err_pct']:+6.3f}% {r['z50_err_pct']:+7.3f}% {r['fit_rms_pct']:7.3f}%")

    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    fs = np.logspace(3, 5.3, 80)
    for (name, fl, ri, geo), col in zip(SC, ["k", "#2C7BE0", "#888888", "#E08A2C", "#1E8E4F"]):
        ax[0].plot(fs / 1e3, [true_z(f, fl, ri, geo) for f in fs], color=col, label=name)
        k = SC.index((name, fl, ri, geo))
        ax[0].scatter([f / 1e3 for f in FREQS], [meas[(f, k)] for f in FREQS], color=col, zorder=3)
    ax[0].set_xscale("log"); ax[0].set_xlabel("frequency (kHz)"); ax[0].set_ylabel("|Z| legs (ohm)")
    ax[0].set_title("LTspice readings (dots) on the exact body curves"); ax[0].legend(fontsize=7)
    names = [r["scenario"].replace(" (intracellular water)", "") for r in rows[1:]]
    x = np.arange(len(names))
    ax[1].bar(x - 0.2, [r["z5_change_pct"] for r in rows[1:]], 0.4, color="#888888", label="5 kHz reading alone")
    ax[1].bar(x + 0.2, [r["ir_change_pct"] for r in rows[1:]], 0.4, color="#2C7BE0", label="ratio |Z50|/|Z5|")
    ax[1].axhline(0, color="k", lw=0.8); ax[1].set_xticks(x, names, rotation=15, fontsize=8); ax[1].set_ylabel("% change vs baseline")
    ax[1].set_title("The ratio sees fluid, ignores position / temperature"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(D / "spectroscopy.png", dpi=130)
