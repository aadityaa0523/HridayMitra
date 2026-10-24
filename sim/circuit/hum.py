"""MAINS HUM: does 230 V / 50 Hz pickup spoil the reading now that the sense inputs are 10 Mohm?

Hum paths modelled (stray capacitances, ASSUMPTION ranges from typical biopotential-amplifier notes):
  mains wiring -> body (Cbm), body -> floor/earth (Cbe), mains -> each sense wire (Cw, unequal on the two wires),
  device ground -> earth (Cdev): about 30 pF when on its battery, about 4.7 nF when a phone charger is plugged in
  (the charger's Y-capacitor ties the circuit to mains).
The reading is taken the way the firmware does it: a 5 kHz Goertzel (single-frequency) amplitude over exactly
20 ms (one full 50 Hz cycle), body then the 220 ohm reference. A plain peak-to-peak reading is shown for comparison.
Run:  python sim/circuit/hum.py        Out: hum_results.csv
"""
import csv, pathlib
import trunk_paths as TP

D = pathlib.Path(__file__).parent
# scenario: (name, Cbm, Cbe, Cdev, Cw+, Cw-)
SC = [("no hum (reference)", 1e-18, 1e-18, 1e-18, 1e-18, 1e-18),
      ("battery, normal room", 100e-12, 200e-12, 30e-12, 1e-12, 0.5e-12),
      ("battery, next to wiring, long unshielded wires", 300e-12, 100e-12, 30e-12, 5e-12, 1e-12),
      ("charger plugged in, normal room", 100e-12, 200e-12, 4.7e-9, 1e-12, 0.5e-12),
      ("charger plugged in, next to wiring", 300e-12, 100e-12, 4.7e-9, 5e-12, 1e-12)]
NAMES = ["cbm", "cbe", "cdev", "cwp", "cwn"]


def tab(i):
    return f".param {NAMES[i]}=table(sc," + ",".join(f"{k},{s[i + 1]:g}" for k, s in enumerate(SC)) + ")"


def pp(tag, a, b):
    return [f".meas TRAN {tag}pp PP V(adc) FROM={a} TO={b}"]


def read_raw(path):
    """LTspice binary .raw (real, stepped): per point a float64 time + float32 per variable. Split steps on time reset."""
    import numpy as np
    d = path.read_bytes()
    k = d.find(("Binary:" + chr(10)).encode("utf-16-le"))
    head = d[:k].decode("utf-16-le")
    nvar = int(head.split("No. Variables:")[1].split()[0])
    names = [ln.split()[1] for ln in head.split("Variables:")[2].strip().splitlines()]
    rec = np.dtype([("time", "<f8")] + [(n, "<f4") for n in names[1:]])
    a = np.frombuffer(d[k + len(("Binary:" + chr(10)).encode("utf-16-le")):], dtype=rec)
    cut = np.flatnonzero(np.diff(np.abs(a["time"])) < 0) + 1
    return [dict(t=np.abs(x["time"]), **{n: x[n].astype(float) for n in names[1:]}) for x in np.split(a, cut)], nvar


def goertzel_amp(step, a, b, fs=40e3, f0=5e3, bits=12):
    """What the ESP32 does: sample the ADC pin at 40 kHz with 12 bits, one-bin DFT at 5 kHz over [a, b)."""
    import numpy as np
    t = np.arange(a, b, 1 / fs)
    v = np.interp(t, step["t"], step["V(adc)"])
    v = np.round(v / 3.3 * (2 ** bits - 1))                     # ADC codes
    v = v - v.mean()
    w = np.exp(-2j * np.pi * f0 * t)
    return abs((v * w).sum()) * 2 / len(t)


STEPS = [".tran 0 0.1 0 2u", ".step param path list 1 3", f".step param sc 0 {len(SC) - 1} 1",
         ".save V(adc) V(ina) V(vref)", ".options plotwinsize=0"] + pp("b", 0.02, 0.04) + pp("r", 0.07, 0.09) + [
         ".meas TRAN zpp PARAM 220*bpp/rpp",
         ".meas TRAN amax MAX V(ina) FROM=0.02 TO=0.09", ".meas TRAN amin MIN V(ina) FROM=0.02 TO=0.09"]
HUM = ["* --- mains hum: 325 V peak 50 Hz between the mains wire and earth; device ground floats via Cdev ---",
       "Vmains mains earth SIN(0 325 50)", "Rearth earth 0 1T", "Cbm mains PV {cbm}", "Cbe PV earth {cbe}",
       "Cdev 0 earth {cdev}", "Cwp mains sLF {cwp}", "Cwn mains sRF {cwn}", "Cwh mains sLH {cwp}"] + [tab(i) for i in range(5)]


def netlist():
    t = TP.netlist(5e3, lambda per: STEPS, "mains hum test (10 Mohm sense bias)")
    t = t.replace("Vsel sel 0 {selv}", "Vsel sel 0 PULSE(0 3.3 0.05 1u 1u 0.05 0.2)   ; body 0-50 ms, reference 50-100 ms")
    t = t.replace(".param f=5000 Rc=1k", ".param f=5000 Rc=1k sc=0")
    # unequal skin: dry left plates, sweaty right plates (worst case for turning hum into a difference)
    t = t.replace("RcsLF sLF LF {Rc}", "RcsLF sLF LF 5k").replace("RciLF iLF LF {Rc}", "RciLF iLF LF 5k")
    t = t.replace("RcsRF sRF RF {Rc}", "RcsRF sRF RF 300").replace("RcsLH sLH LH {Rc}", "RcsLH sLH LH 5k")
    return t.replace(".end", "\n".join(HUM) + "\n.end")


if __name__ == "__main__":
    cir = D / "hum.cir"
    cir.write_text(netlist())
    log = TP.run(cir)
    n = 2 * len(SC)
    zpp = TP.read_meas(log, "zpp", n)
    steps, _ = read_raw(cir.with_suffix(".raw"))
    assert len(steps) == n, len(steps)
    zg = [220 * goertzel_amp(st, 0.02, 0.04) / goertzel_amp(st, 0.07, 0.09) for st in steps]
    amax, amin = TP.read_meas(log, "amax", n), TP.read_meas(log, "amin", n)
    rows = []
    for i in range(n):                                          # step order: path fastest, then scenario
        p, s = (1, 3)[i % 2], i // 2
        zt = TP.true_z(p, 1.0, 5e3)
        rows.append(dict(scenario=SC[s][0], path=p, z_true=round(zt, 2), z_goertzel=round(zg[i], 2),
                         err_goertzel_pct=round(100 * (zg[i] / zt - 1), 3), z_peak_to_peak=round(zpp[i], 2),
                         err_pp_pct=round(100 * (zpp[i] / zt - 1), 2), amp_min_v=round(amin[i], 2), amp_max_v=round(amax[i], 2),
                         clipped=bool(amin[i] < 0.06 or amax[i] > 3.24)))
    with open(D / "hum_results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(f"{r['scenario']:<48} path {r['path']}: Goertzel {r['err_goertzel_pct']:+.2f} %   peak-to-peak {r['err_pp_pct']:+.1f} %"
              f"   amplifier {r['amp_min_v']}-{r['amp_max_v']} V{'  CLIPPED' if r['clipped'] else ''}")
