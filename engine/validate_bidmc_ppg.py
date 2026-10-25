"""Real-data check 2: pulse from a finger PPG and breathing rate, on the BIDMC PPG and Respiration dataset (PhysioNet).

53 ICU patients, 8 min each, 125 Hz: finger PPG (PLETH), impedance-pneumography breathing (RESP), the monitor's
1-per-second PULSE numeric, and every breath marked by two human annotators.
  Pulse:     the stool's exact code (signals.pulse_spo2) on 15 s windows resampled to 100 Hz, as the MAX30102 runs,
             against the monitor's PULSE (median over the same 15 s). SpO2 is not tested: the dataset has one PPG
             wavelength, and SpO2 needs red + infrared.
  Breathing: the AMULET FIRMWARE's method (two moving averages, zero crossings, 60 s windows at 10 Hz, line for line
             from hridaymitra_amulet.ino) and the laptop's spectral method (signals.breathing), on the chest
             breathing signal, against annotator 1's breath count in the same 60 s. The amulet senses chest motion
             with an accelerometer; RESP is chest impedance, the closest public stand-in (an honest limit).
Run:  python engine/validate_bidmc_ppg.py        Out: reports/bidmc_ppg_validation.csv, reports/bidmc_ppg_summary.json
"""
import json, pathlib, sys, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from scipy.signal import resample_poly
import wfdb

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import signals as S

RAW, REP, FS = ROOT / "data" / "raw", ROOT / "reports", 125
RECORDS = [f"bidmc{i:02d}" for i in range(1, 54)]


def retry(fn, tries=10):
    for k in range(tries):
        try:
            return fn()
        except Exception:
            time.sleep(3 * (k + 1))
    raise RuntimeError("PhysioNet did not answer")


def load(rec):
    """Cached as data/raw/bidmc_ppg_<rec>.npz (PPG, RESP, PULSE numeric, annotator-1 breaths)."""
    cache = RAW / f"bidmc_ppg_{rec}.npz"
    if not cache.exists():
        r = retry(lambda: wfdb.rdrecord(rec, pn_dir="bidmc"))
        n = retry(lambda: wfdb.rdrecord(rec + "n", pn_dir="bidmc"))
        a = retry(lambda: wfdb.rdann(rec, "breath", pn_dir="bidmc"))
        col = lambda rr, name: rr.p_signal[:, [s.strip(", ") for s in rr.sig_name].index(name)]
        breaths = np.asarray(a.sample)[np.asarray(a.aux_note) == "ann1"]
        np.savez_compressed(cache, ppg=col(r, "PLETH").astype(np.float32), resp=col(r, "RESP").astype(np.float32),
                            pulse=col(n, "PULSE").astype(np.float32), breaths=breaths)
    return dict(np.load(cache))


def amulet_rr(x10):
    """hridaymitra_amulet.ino breathing, line for line: g -> slow (0.01) and fast (0.3) moving averages, their
    difference, zero crossings / 2 = breaths in the 60 s window."""
    lp_slow, lp_fast, prev, cross = x10[0], x10[0], 0.0, 0
    for g in x10:
        lp_slow += (g - lp_slow) * 0.01; lp_fast += (g - lp_fast) * 0.3
        hp = lp_fast - lp_slow
        if (hp > 0) != (prev > 0):
            cross += 1
        prev = hp
    return cross / 2


def windows(rec):
    d = load(rec)
    ppg, resp, pulse, breaths = d["ppg"].astype(float), d["resp"].astype(float), d["pulse"].astype(float), d["breaths"]
    rows = []
    for t0 in range(0, len(ppg) // FS - 15 + 1, 15):                     # pulse: 15 s windows
        seg = resample_poly(ppg[t0 * FS:(t0 + 15) * FS], 4, 5)              # 125 -> 100 Hz
        ir = 100_000 + 1_000 * (seg - np.nanmin(seg))                       # PPG is 0-1 normalised: give it a DC level
        bpm, _, why = S.pulse_spo2(ir, ir, fs=100)
        ref = np.nanmedian(pulse[t0:t0 + 15])
        rows.append(dict(record=rec, kind="pulse", t0=t0, got=bpm, ref=ref, why=why))
    for t0 in range(0, len(resp) // FS - 60 + 1, 60):                     # breathing: 60 s windows
        seg = resp[t0 * FS:(t0 + 60) * FS]
        x10 = resample_poly(seg, 2, 25)                                     # 125 -> 10 Hz, the amulet's rate
        x10 = 1 + 0.004 * (x10 - x10.mean()) / max(x10.std(), 1e-9)          # chest-motion scale: quiet breathing, ~0.004 g
        ref = int(((breaths >= t0 * FS) & (breaths < (t0 + 60) * FS)).sum())
        spec, _ = S.breathing(x10, fs=10)
        rows.append(dict(record=rec, kind="breath_amulet", t0=t0, got=amulet_rr(x10), ref=ref, why="ok"))
        rows.append(dict(record=rec, kind="breath_spectral", t0=t0, got=spec, ref=ref, why="ok" if spec else "skipped"))
    return rows


def summary(df):
    out = {}
    for kind, g in df.groupby("kind"):
        ok = g.dropna(subset=["got", "ref"])
        err = (ok.got - ok.ref).abs()
        out[kind] = dict(windows=len(g), reported=len(ok), coverage=round(len(ok) / len(g), 3),
                         median_abs_err=round(float(err.median()), 2), p90_abs_err=round(float(err.quantile(0.9)), 2),
                         within_5=round(float((err <= 5).mean()), 3), within_2=round(float((err <= 2).mean()), 3),
                         bias=round(float((ok.got - ok.ref).mean()), 2))
        per = ok.assign(e=err).groupby("record").e.median()
        out[kind]["records_median_err_over_5"] = sorted(per[per > 5].index.tolist())
    return out


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(6) as ex:                                       # PhysioNet streams slowly
        rows = [r for rs in ex.map(windows, RECORDS) for r in rs]
    df = pd.DataFrame(rows)
    df.to_csv(REP / "bidmc_ppg_validation.csv", index=False)
    s = summary(df)
    (REP / "bidmc_ppg_summary.json").write_text(json.dumps(s, indent=1))
    for k, v in s.items():
        print(f"{k:16s} {v}")
