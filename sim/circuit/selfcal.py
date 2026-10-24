"""SELF-CALIBRATING REFERENCE (C2): the stool checks its own reference chain at every check-in.

Reference chain: R5 (120 ohm, ordinary 5 %) in series with Rcal (100 ohm, 0.1 %). The spare third switch of the 74HC4053
(CAL, GPIO12) lets the amplifier read across Rcal alone (used as THE reference for every impedance) or across R5 + Rcal.
Ratio = V(R5 + Rcal) / V(Rcal) must be 2.2 (2.14-2.26 with a 5 % R5). Outside 2.0-2.4 the stool rejects the readings and
sends a service SMS. This script simulates the ratio for a good board and for build mistakes and faults.
Run:  python sim/circuit/selfcal.py      Out: selfcal_results.csv
"""
import csv, pathlib
import trunk_paths as TP

D = pathlib.Path(__file__).parent
CASES = [("good board", "120", "100"), ("R5 at -5 % (tolerance)", "114", "100"), ("R5 at +5 % (tolerance)", "126", "100"),
         ("old 220 ohm R5 fitted by mistake", "220", "100"), ("R5 shorted", "1m", "100"), ("Rcal shorted", "120", "1m"),
         ("Rcal wrong value (1 kohm)", "120", "1k"), ("solder joint +30 ohm in R5", "150", "100")]
LO, HI = 2.0, 2.4


def netlist():
    steps = [".tran 0 0.02 0 5u", ".param selv=3.3", ".step param calv list 3.3 0", f".step param case 0 {len(CASES) - 1} 1",
             ".meas TRAN vpp PP V(adc) FROM=0.008 TO=0.02"]
    t = TP.netlist(5e3, lambda p: steps, "self-calibration integrity check")
    t = t.replace(" selv=0 calv=3.3", "").replace("R5 ret ncal 120", "R5 ret ncal {r5v}").replace("Rcal ncal vref 100", "Rcal ncal vref {rcv}")
    tab = lambda n, i: f".param {n}=table(case," + ",".join(f"{k},{c[i]}" for k, c in enumerate(CASES)) + ")"
    return t.replace(".end", tab("r5v", 1) + "\n" + tab("rcv", 2) + "\n.end")


if __name__ == "__main__":
    cir = D / "selfcal.cir"
    cir.write_text(netlist())
    v = TP.read_meas(TP.run(cir), "vpp", 2 * len(CASES))     # LTspice sorts the list: calv 0 (R5 + Rcal) first, then 3.3 (Rcal)
    rows = []
    for k, (name, r5, rc) in enumerate(CASES):
        ratio = v[2 * k] / v[2 * k + 1] if v[2 * k + 1] > 1e-6 else float("inf")
        rows.append(dict(case=name, r5=r5, rcal=rc, ratio=round(ratio, 3), verdict="OK" if LO <= ratio <= HI else "REJECT + service SMS"))
        print(f"{name:36s} ratio {ratio:8.3f}  {rows[-1]['verdict']}")
    with open(D / "selfcal_results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
