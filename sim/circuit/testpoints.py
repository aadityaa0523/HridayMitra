"""TEST-POINT WAVEFORMS for the schematic sheet: LTspice runs the real front end (legs path, 5 kHz, 1 kohm skin
contacts) in body mode and in reference mode, and saves the signal at each test point.
  TP1 DAC out   TP2 excitation buffer   TP3 current through the body   TP4 voltage across the legs (sense pair)
  TP5 INA126 output   TP6 ADC pin (after the 1.5 k / 10 n filter)   TP7 INA126 output in reference mode (Rcal)
Run:  python sim/circuit/testpoints.py        Out: sim/circuit/testpoints.npz (2 ms of each, after settling)
"""
import pathlib
import numpy as np
import trunk_paths as TP
from hum import read_raw

D = pathlib.Path(__file__).parent
STEPS = [".tran 0 0.302 0.3 1u", ".step param selv list 0 3.3", ".save V(dac) V(excout) I(R4) V(sa) V(sb) V(ina) V(adc)",
         ".options plotwinsize=0"]

if __name__ == "__main__":
    cir = D / "testpoints.cir"
    cir.write_text(TP.netlist(5e3, lambda p: STEPS, "test points for the schematic sheet").replace(" selv=0 ", " "))
    TP.run(cir)
    steps, _ = read_raw(cir.with_suffix(".raw"))
    body, ref = steps[0], steps[1]                          # LTspice sorts: selv 0 (body) first
    t = np.linspace(0, 0.002, 400)                         # LTspice stores time from the start of the saved window
    g = lambda s, k: np.interp(t, s["t"], s[k])
    out = dict(t_ms=t * 1e3, TP1=g(body, "V(dac)"), TP2=g(body, "V(excout)"), TP3=g(body, "I(R4)") * 1e6,
               TP4=(g(body, "V(sa)") - g(body, "V(sb)")) * 1e3, TP5=g(body, "V(ina)"), TP6=g(body, "V(adc)"), TP7=g(ref, "V(ina)"))
    np.savez(D / "testpoints.npz", **out)
    pp = lambda x: x.max() - x.min()
    print(f"TP3 body current {pp(out['TP3']) / 2:.1f} uA peak; TP4 legs {pp(out['TP4']) / 2:.1f} mV peak; "
          f"TP5 {out['TP5'].min():.2f}-{out['TP5'].max():.2f} V; Z = 100 x TP5/TP7 = {100 * pp(out['TP5']) / pp(out['TP7']):.1f} ohm")
