"""PATIENT ELECTRICAL SAFETY in LTspice (IEC 60601-1, patient auxiliary current, type BF applied part).

The stool drives a small current through the body on purpose. The standard limits that current, in normal condition
(NC) and with any single fault (SFC):
    DC:  NC 10 uA, SFC 50 uA
    AC:  NC 100 uA rms, SFC 500 uA rms, multiplied by the frequency in kHz above 1 kHz (never above 10 mA)
Each fault below is injected into the real front end (legs path, 1 kohm skin contacts, the 10 Mohm design), and the
current through the patient's foot electrode is measured at 5, 20 and 50 kHz (all spectroscopy frequencies).
Run:  python sim/circuit/safety.py        Out: safety_results.csv
"""
import csv, pathlib
import trunk_paths as TP

D = pathlib.Path(__file__).parent
FAULTS = [("normal condition", "NC"), ("current-limit resistor R4 shorted", "SFC"), ("coupling capacitor C3 shorted", "SFC"),
          ("coupling capacitor C4 shorted", "SFC"), ("op-amp U1B output stuck at 3.3 V", "SFC"),
          ("op-amp U1B output stuck at 0 V", "SFC"), ("DAC at full scale (3.3 V p-p)", "SFC"),
          ("C3 shorted AND op-amp stuck at 3.3 V (double fault)", "double")]
FREQS = [5e3, 20e3, 50e3]


def netlist(f):
    per = 1 / f
    t_end = max(0.05, 200 * per)
    tab = lambda name, vals: f".param {name}=table(fault," + ",".join(f"{k},{v}" for k, v in enumerate(vals)) + ")"
    steps = [f".tran 0 {t_end:g} 0 {per / 40:g}", f".step param fault 0 {len(FAULTS) - 1} 1",
             tab("r4v", ["4.7k", "1m", "4.7k", "4.7k", "4.7k", "4.7k", "4.7k", "4.7k"]),
             tab("rc3", ["1T", "1T", "1m", "1T", "1T", "1T", "1T", "1m"]),
             tab("rc4", ["1T", "1T", "1T", "1m", "1T", "1T", "1T", "1T"]),
             tab("stuck", [0, 0, 0, 0, 1, 2, 0, 1]),
             tab("amp", [0.83, 0.83, 0.83, 0.83, 0.83, 0.83, 1.65, 0.83]),
             f".meas TRAN irms RMS I(RciLF) FROM={0.5 * t_end:g} TO={t_end:g}",
             f".meas TRAN idc AVG I(RciLF) FROM={0.5 * t_end:g} TO={t_end:g}",
             f".meas TRAN ipk MAX abs(I(RciLF)) FROM={0.5 * t_end:g} TO={t_end:g}"]
    t = TP.netlist(f, lambda p: steps, f"patient-current faults at {f / 1e3:g} kHz")
    t = t.replace("Vdac dac 0 SIN(1.65 0.83 {f})", "Vdac dac 0 SIN(1.65 {amp} {f})")
    t = t.replace("Bu1b excout 0 V=limit(V(excin),0.05,3.25)",
                  "Bu1b excout 0 V=if(stuck==1,3.3,if(stuck==2,0,limit(V(excin),0.05,3.25)))")
    t = t.replace("R4 n1 injP 4.7k", "R4 n1 injP {r4v}")
    t = t.replace(".end", "Rc3x excout n1 {rc3}\nRc4x injN ret {rc4}\n.save I(RciLF)\n.end")
    return t


def limits(f, kind):
    k = max(1.0, f / 1e3)
    if kind == "NC":
        return 10e-6, min(100e-6 * k, 10e-3)
    return 50e-6, min(500e-6 * k, 10e-3)


if __name__ == "__main__":
    rows = []
    for f in FREQS:
        cir = D / f"safety_{f / 1e3:g}khz.cir"
        cir.write_text(netlist(f))
        log = TP.run(cir)
        n = len(FAULTS)
        irms, idc, ipk = (TP.read_meas(log, m, n) for m in ("irms", "idc", "ipk"))
        for k, (name, kind) in enumerate(FAULTS):
            dc_lim, ac_lim = limits(f, kind if kind != "double" else "SFC")
            ac = (irms[k] ** 2 - idc[k] ** 2) ** 0.5 if irms[k] > abs(idc[k]) else 0.0
            rows.append(dict(f_khz=f / 1e3, fault=name, condition=kind, ac_rms_uA=round(ac * 1e6, 2), dc_uA=round(abs(idc[k]) * 1e6, 3),
                             peak_uA=round(ipk[k] * 1e6, 1), ac_limit_uA=round(ac_lim * 1e6), dc_limit_uA=round(dc_lim * 1e6),
                             ac_margin_x=round(ac_lim / max(ac, 1e-12), 1), dc_ok=abs(idc[k]) <= dc_lim, ac_ok=ac <= ac_lim))
    with open(D / "safety_results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"{'kHz':>4} {'fault':52s} {'cond':6s} {'AC uA rms':>9s} {'limit':>6s} {'DC uA':>7s} {'limit':>5s}  verdict")
    for r in rows:
        ok = r["dc_ok"] and r["ac_ok"]
        print(f"{r['f_khz']:4.0f} {r['fault']:52s} {r['condition']:6s} {r['ac_rms_uA']:9.1f} {r['ac_limit_uA']:6d} {r['dc_uA']:7.3f} {r['dc_limit_uA']:5d}  "
              f"{'PASS' if ok else ('FAIL' if r['condition'] != 'double' else 'outside the standard (double fault)')}")
