"""Real-data check: heart-rate detection on the BIDMC Congestive Heart Failure database (PhysioNet).

Streams the first MINUTES of each record (no full download), detects R peaks with NeuroKit2,
compares with the database's beat annotations, and reports beat-level and heart-rate-window errors.
Run:  python engine/validate_bidmc_hr.py
"""
import pathlib, json
import numpy as np
import pandas as pd
import wfdb
import neurokit2 as nk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, REP = ROOT / "data" / "raw", ROOT / "reports"
RECORDS = ["chf01", "chf02", "chf03"]   # add more later; each 30 min streams in a few minutes on a slow link
MINUTES = 30
TOL_S = 0.075          # a detected peak within 75 ms of an annotated beat counts as a match
WIN_S = 30             # heart-rate window
FS_DEFAULT = 250


def retry(fn, tries=8):
    """The PhysioNet stream sometimes drops mid-read; try again."""
    import time
    for k in range(tries):
        try:
            return fn()
        except Exception as e:
            if k == tries - 1:
                raise
            time.sleep(2 + k)


def match(det, ref, tol):
    """Greedy one-to-one matching of sorted sample indices within tol samples."""
    tp, j = 0, 0
    for r in ref:
        while j < len(det) and det[j] < r - tol:
            j += 1
        if j < len(det) and abs(det[j] - r) <= tol:
            tp += 1
            j += 1
    return tp


def hr_windows(peaks, fs, n, win_s):
    out = []
    for k in range(0, n - win_s * fs + 1, win_s * fs):
        p = peaks[(peaks >= k) & (peaks < k + win_s * fs)]
        out.append(60 * fs / np.median(np.diff(p)) if len(p) > 3 else np.nan)
    return np.array(out)


rows, wins = [], []
for rec in RECORDS:
    cache = RAW / f"bidmc_chf_{rec}_{MINUTES}min.npz"
    if cache.exists():
        z = np.load(cache); sig, fs, ann = z["sig"], int(z["fs"]), z["ann"]
    else:
        fs, parts, step = FS_DEFAULT, [], FS_DEFAULT * 60 * 5       # 5-minute chunks, each retried
        for a0 in range(0, FS_DEFAULT * 60 * MINUTES, step):
            parts.append(retry(lambda: wfdb.rdrecord(rec, pn_dir="chfdb", sampfrom=a0, sampto=a0 + step,
                                                     channels=[0]).p_signal[:, 0]))
        sig = np.concatenate(parts)
        ann = np.asarray(retry(lambda: wfdb.rdann(rec, "ecg", pn_dir="chfdb", sampto=fs * 60 * MINUTES).sample))
        np.savez_compressed(cache, sig=sig, fs=fs, ann=ann)
    sig = np.nan_to_num(sig)
    clean = nk.ecg_clean(sig, sampling_rate=fs, method="neurokit")
    _, info = nk.ecg_peaks(clean, sampling_rate=fs, method="neurokit")
    det = np.asarray(info["ECG_R_Peaks"])
    tol = int(TOL_S * fs)
    tp = match(det, ann, tol)
    se, ppv = tp / max(len(ann), 1), tp / max(len(det), 1)
    hr_det, hr_ref = hr_windows(det, fs, len(sig), WIN_S), hr_windows(ann, fs, len(sig), WIN_S)
    err = hr_det - hr_ref
    rows.append(dict(record=rec, fs=fs, minutes=MINUTES, ref_beats=len(ann), det_beats=len(det),
                     sensitivity=round(se, 4), ppv=round(ppv, 4),
                     hr_mae_bpm=round(float(np.nanmean(np.abs(err))), 2),
                     hr_within_5bpm_pct=round(float(100 * np.nanmean(np.abs(err) <= 5)), 1)))
    wins.append(pd.DataFrame(dict(record=rec, hr_ref=hr_ref, hr_det=hr_det)))
    print(rows[-1], flush=True)

df, w = pd.DataFrame(rows), pd.concat(wins)
REP.mkdir(exist_ok=True)
df.to_csv(REP / "bidmc_hr_validation.csv", index=False)
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].scatter(w.hr_ref, w.hr_det, s=6, alpha=.5, color="#0d6b6e"); lim = [40, 140]
ax[0].plot(lim, lim, "k--", lw=1); ax[0].set(xlabel="reference HR from annotations (bpm)", ylabel="detected HR (bpm)",
                                             title="BIDMC CHF: 30 s heart-rate windows")
ax[1].hist((w.hr_det - w.hr_ref).dropna(), bins=60, color="#0d6b6e"); ax[1].set(xlabel="error (bpm)", title="HR error distribution")
fig.tight_layout(); fig.savefig(REP / "bidmc_hr_validation.png", dpi=130)
summary = dict(records=len(df), mean_sensitivity=float(df.sensitivity.mean()), mean_ppv=float(df.ppv.mean()),
               mean_hr_mae_bpm=float(df.hr_mae_bpm.mean()), pct_windows_within_5bpm=float(df.hr_within_5bpm_pct.mean()))
(REP / "bidmc_hr_summary.json").write_text(json.dumps(summary, indent=2))
print(summary)
