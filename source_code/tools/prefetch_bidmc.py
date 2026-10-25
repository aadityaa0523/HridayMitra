"""Download the 15 BIDMC CHF records (first 30 min each) in parallel into data/raw, in the cache format that
engine/validate_bidmc_hr.py reads. PhysioNet streams slowly, so 5 records at a time. Run: python tools/prefetch_bidmc.py"""
import pathlib, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import wfdb

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, MIN, FS = ROOT / "data" / "raw", 30, 250
sys.path.insert(0, str(ROOT / "engine"))


def retry(fn, tries=10):
    import time
    for k in range(tries):
        try:
            return fn()
        except Exception:
            time.sleep(3 * (k + 1))
    raise RuntimeError("PhysioNet did not answer")


def fetch(rec):
    cache = RAW / f"bidmc_chf_{rec}_{MIN}min.npz"
    if cache.exists():
        return rec, "cached"
    step = FS * 60 * 5
    parts = [retry(lambda a0=a0: wfdb.rdrecord(rec, pn_dir="chfdb", sampfrom=a0, sampto=a0 + step, channels=[0]).p_signal[:, 0])
             for a0 in range(0, FS * 60 * MIN, step)]
    ann = np.asarray(retry(lambda: wfdb.rdann(rec, "ecg", pn_dir="chfdb", sampto=FS * 60 * MIN).sample))
    np.savez_compressed(cache, sig=np.concatenate(parts), fs=FS, ann=ann)
    return rec, "downloaded"


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(5) as pool:
        for rec, how in pool.map(fetch, [f"chf{i:02d}" for i in range(1, 16)]):
            print(rec, how, flush=True)
