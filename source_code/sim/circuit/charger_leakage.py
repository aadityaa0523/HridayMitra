"""CHARGER LEAKAGE in LTspice: why the stool has a CHARGE / USE switch (IEC 60601-1 patient leakage, type BF).

A phone charger couples its output to the mains through its Y-capacitor (about 1 nF in a good one, 4.7 nF in a cheap
one). With the charger connected, that leakage can flow from the electrodes through the patient to earth (worst case:
bare feet on a wet, earthed floor, 1 kohm). The CHARGE / USE switch (SW6, 2 poles) cuts BOTH USB wires in USE, leaving
only its ~2 pF open contacts; in CHARGE the firmware refuses to measure (GPIO39 sense).
Limits (patient leakage, AC rms): normal condition 100 uA, single fault 500 uA.
Run:  python sim/circuit/charger_leakage.py        Out: charger_leakage_results.csv
"""
import csv, pathlib
import trunk_paths as TP

D = pathlib.Path(__file__).parent
# name, switch, charger Y-capacitance, charger insulation failed (live tied to its output), condition
CASES = [("USE, cheap charger (4.7 nF) plugged in", "USE", "4.7n", False, "NC"),
         ("CHARGE, good charger (1 nF): if someone measured anyway", "CHARGE", "1n", False, "NC"),
         ("CHARGE, cheap charger (4.7 nF): if someone measured anyway", "CHARGE", "4.7n", False, "NC"),
         ("USE, charger insulation failed (live on its output)", "USE", "4.7n", True, "SFC"),
         ("CHARGE, charger insulation failed", "CHARGE", "4.7n", True, "SFC")]
LIMIT = {"NC": 100e-6, "SFC": 500e-6}


def netlist():
    tab = lambda name, vals: f".param {name}=table(case," + ",".join(f"{k},{v}" for k, v in enumerate(vals)) + ")"
    steps = [".tran 0 0.2 0 10u", f".step param case 0 {len(CASES) - 1} 1",
             tab("cy", [c[2] for c in CASES]), tab("rf", ["1m" if c[3] else "1T" for c in CASES]),
             tab("rsw", ["0.05" if c[1] == "CHARGE" else "1T" for c in CASES]),
             ".meas TRAN ileak RMS I(Rpe) FROM=0.1 TO=0.2"]
    t = TP.netlist(5e3, lambda p: steps, "charger leakage through the patient")
    extra = ["* --- mains and charger: live 325 V peak to earth; charger output coupled to live by Cy (or shorted) ---",
             "Vmains live earth SIN(0 325 50)", "Rearth earth 0 1T", "Cy live chgg {cy}", "Rf live chgg {rf}",
             "* --- SW6 CHARGE/USE, the ground pole (the +5 V pole is in series with the same charger output) ---",
             "Rsw chgg 0 {rsw}", "Csw chgg 0 2p",
             "Cdev 0 earth 30p", "Rpe PV earth 1k", ".save I(Rpe)"]
    return t.replace(".end", "\n".join(extra) + "\n.end")


if __name__ == "__main__":
    cir = D / "charger_leakage.cir"
    cir.write_text(netlist())
    i = TP.read_meas(TP.run(cir), "ileak", len(CASES))
    rows = []
    for k, (name, sw, cy, fail, cond) in enumerate(CASES):
        rows.append(dict(case=name, switch=sw, condition=cond, leak_uA=round(i[k] * 1e6, 2), limit_uA=round(LIMIT[cond] * 1e6),
                         verdict="PASS" if i[k] <= LIMIT[cond] else "FAIL"))
        print(f"{name:58s} {cond:4s} {i[k] * 1e6:10.2f} uA  limit {LIMIT[cond] * 1e6:4.0f}  {rows[-1]['verdict']}")
    with open(D / "charger_leakage_results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
