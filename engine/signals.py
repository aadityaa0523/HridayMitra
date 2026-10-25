"""RAW SIGNALS -> DAILY NUMBERS: the step before the alert engine (same maths the ESP32 firmware will run).

  impedance(): ADC samples of the body and of R5 -> ohms, by a 5 kHz Goertzel (single-frequency DFT). Hum-proof
               (LTspice: 0.17 % worst with a charger plugged in); peak-to-peak is never used.
  trunk():     the chest value from the 4 paths: (Z3 + Z4 - Z1 - Z2) / 2.
  pulse_spo2(): MAX30102 red + infrared samples -> pulse (peak spacing) and SpO2 (ratio of ratios).
  breathing(): amulet chest-axis motion at night -> breaths per minute (strongest rhythm 6-40 per minute).
  situps():    amulet tilt -> number of times the person sat up at night.
  walk6():     amulet movement -> steps in the best 6 minutes (the 6-minute walk test, same as walk_core.h).
Each returns None with a reason when the signal is not trustworthy ("no reading" is better than a wrong number).
The make_* functions create synthetic raw signals with a known answer, for the tests and the demo.
"""
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

ADC_MAX, FS_Z, F0 = 4095, 40_000, 5_000


def goertzel(x, fs=FS_Z, f0=F0):
    x = np.asarray(x, float) - np.mean(x)
    n = np.arange(len(x))
    return abs(np.dot(x, np.exp(-2j * np.pi * f0 * n / fs))) * 2 / len(x)


def impedance(body, ref, r5=220.0, fs=FS_Z):
    """Body and reference ADC codes (same amplifier, select low/high) -> (ohms, reason)."""
    body, ref = np.asarray(body), np.asarray(ref)
    if (body <= 5).mean() > 0.01 or (body >= ADC_MAX - 5).mean() > 0.01:
        return None, "clipped: a plate is open or a foot is lifted"
    a_ref = goertzel(ref, fs)
    if a_ref < 5:
        return None, "no current: check the plates"
    return r5 * goertzel(body, fs) / a_ref, "ok"


def trunk(z1, z2, z3, z4):
    return None if None in (z1, z2, z3, z4) else (z3 + z4 - z1 - z2) / 2


def _band(x, fs, lo, hi):
    b, a = butter(2, [lo / (fs / 2), hi / (fs / 2)], "band")
    return filtfilt(b, a, x)


def pulse_spo2(red, ir, fs=100):
    """(pulse bpm, SpO2 %, reason). SpO2 uses the common linear calibration 110 - 25 R (needs a per-sensor check)."""
    red, ir = np.asarray(red, float), np.asarray(ir, float)
    if ir.mean() < 20_000:
        return None, None, "no finger on the sensor"
    ac_ir = _band(ir, fs, 0.7, 4)
    pi = ac_ir.std() / ir.mean()
    if pi < 0.0005:
        return None, None, "pulse too weak: warm the finger, hold still"
    peaks, _ = find_peaks(ac_ir, distance=fs * 0.33, prominence=ac_ir.std() * 0.5)
    ibi = np.diff(peaks) / fs
    if len(ibi) < 4 or np.std(ibi) / np.mean(ibi) > 0.25:
        return None, None, "irregular or moving: hold still and try again"
    ac_red = _band(red, fs, 0.7, 4)
    r = (ac_red.std() / red.mean()) / (ac_ir.std() / ir.mean())
    return 60 / np.median(ibi), float(np.clip(110 - 25 * r, 70, 100)), "ok"


def breathing(acc, fs=10):
    """Chest-axis acceleration during quiet sleep -> breaths per minute, or None if too much movement."""
    x = _band(np.asarray(acc, float), fs, 0.1, 0.7)
    if np.asarray(acc).std() > 0.05:                     # g; rolling over / walking, not quiet breathing
        return None, "moving: skipped this window"
    f = np.fft.rfftfreq(len(x), 1 / fs)
    p = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    band = (f >= 0.1) & (f <= 0.67)
    return 60 * f[band][np.argmax(p[band])], "ok"


def situps(pitch_deg, fs=1, up=60, down=30):
    """Count lying -> sitting transitions (with hysteresis so wobbling around one angle counts once)."""
    n, sitting = 0, False
    for a in pitch_deg:
        if not sitting and a > up:
            n, sitting = n + 1, True
        elif sitting and a < down:
            sitting = False
    return n


def walk_window(x, lag_min=6, lag_max=30, r_min=0.5, sd_min=0.008):
    """One 5 s window of accelerometer magnitude (g, 20 Hz) -> steps in it (0 if not walking). Walking is a strong
    rhythm of 0.3-1.5 s per step; the step period comes from the autocorrelation. Same maths as walk_core.h."""
    x = np.asarray(x, np.float32); n = len(x); m = x.mean(); d = x - m; v = float((d * d).mean())
    if np.sqrt(v) < sd_min:
        return 0.0
    r = {L: float((d[:n - L] * d[L:]).sum()) / ((n - L) * v) for L in range(lag_min - 1, lag_max + 2)}
    rmax = max(r[L] for L in range(lag_min, lag_max + 1))
    if rmax < r_min:
        return 0.0
    for L in range(lag_min, lag_max + 1):                # first strong peak = one step (a later one may be a stride)
        if r[L] >= r[L - 1] and r[L] >= r[L + 1] and r[L] >= 0.6 * rmax:
            den = r[L - 1] - 2 * r[L] + r[L + 1]
            return n / (L + (0.5 * (r[L - 1] - r[L + 1]) / den if den < 0 else 0))
    return 0.0


def walk6(mag, win=100, slots=72):
    """Magnitude (g, 20 Hz) -> (total steps, best steps in any 6 minutes = 72 consecutive 5 s windows)."""
    w = [walk_window(mag[i:i + win]) for i in range(0, len(mag) - win + 1, win)]
    c = np.concatenate([[0], np.cumsum(w)])
    best = max((c[i + slots] - c[i] for i in range(len(w) - slots + 1)), default=c[-1])
    return float(c[-1]), float(best)


# ---------- synthetic raw signals with a known answer ----------
def make_z(z, contact_noise=2.0, hum_mv=0.0, seed=0, r5=220.0, i_ua=100, gain=10, fs=FS_Z, n=4000):
    """ADC codes for body and reference windows of a body of `z` ohms (20 ms windows by default = 1 mains cycle)."""
    rng = np.random.default_rng(seed)
    t = np.arange(n) / fs
    code = lambda v: np.clip(np.round((1.65 + v) / 3.3 * ADC_MAX + rng.normal(0, contact_noise, n)), 0, ADC_MAX)
    hum = hum_mv / 1000 * np.sin(2 * np.pi * 50 * t)
    s = np.sin(2 * np.pi * F0 * t)
    return code(gain * (i_ua * 1e-6 * z * s + hum)), code(gain * i_ua * 1e-6 * r5 * s)


def make_ppg(bpm, spo2, fs=100, sec=20, seed=0):
    rng = np.random.default_rng(seed)
    t = np.arange(fs * sec) / fs
    beat = np.sin(2 * np.pi * bpm / 60 * t) + 0.3 * np.sin(4 * np.pi * bpm / 60 * t)
    r = (110 - spo2) / 25
    ir = 100_000 * (1 + 0.01 * beat) + rng.normal(0, 30, len(t))
    red = 80_000 * (1 + 0.01 * r * beat) + rng.normal(0, 30, len(t))
    return red, ir


def make_breath(rpm, fs=10, sec=120, seed=0):
    rng = np.random.default_rng(seed)
    t = np.arange(fs * sec) / fs
    return 0.01 * np.sin(2 * np.pi * rpm / 60 * t) + rng.normal(0, 0.002, len(t))


def make_walk(cadence, sec, amp=0.12, seed=0, sway=0.3, cord=0.02, start=0, pad=60, fs_out=20):
    """Pendant accelerometer magnitude (g, 20 Hz) for `sec` seconds of walking at `cadence` steps per minute, with
    `pad` s of sitting before and after. Trunk bounce once per step (amp g, 2nd harmonic), left-right sway once per
    stride, cord swing, step-time jitter, MPU6050 10 Hz low-pass, then 20 Hz sampling. Returns (mag, true steps)."""
    rng = np.random.default_rng(seed)
    fs = 1000; n = int((sec + 2 * pad) * fs); t = np.arange(n) / fs
    walking = (t >= pad + start) & (t < pad + start + sec)
    f = cadence / 60 * (1 + 0.03 * np.cumsum(rng.normal(0, 1, n)) / np.sqrt(fs * 60))   # slow cadence drift
    ph = 2 * np.pi * np.cumsum(f) / fs + rng.normal(0, 0.15, n).cumsum() / np.sqrt(fs)
    a = amp * (np.sin(ph) + 0.35 * np.sin(2 * ph + 1) + sway * np.sin(ph / 2 + 0.4))
    a += cord * np.sin(2 * np.pi * 0.9 * t + rng.uniform(0, 6)) * (1 + np.sin(ph))      # pendant swinging on its cord
    mag = 1 + a * walking + rng.normal(0, 0.004, n)
    b, c = butter(2, 10 / (fs / 2)); mag = filtfilt(b, c, mag)
    true = int(round(np.sum(np.diff(np.floor(ph[walking] / (2 * np.pi))) > 0)))
    k = fs // fs_out; return mag[rng.integers(0, k)::k], true


def make_still(kind, sec=600, seed=0):
    """Pendant magnitude (g, 20 Hz) for things that are NOT walking: sitting, fidgeting, riding an auto-rickshaw or bus,
    turning in bed. The walk counter must find no steps in any of them."""
    from scipy.signal import lfilter
    r = np.random.default_rng(seed); n = sec * 20; t = np.arange(n) / 20; m = 1 + r.normal(0, 0.004, n)
    if kind == "sitting":
        return m + 0.003 * np.sin(2 * np.pi * 0.25 * t)
    if kind == "fidget":
        for k in r.integers(0, n - 6, 60): m[k:k + 6] += r.normal(0, 0.15, 6)
    elif kind == "auto-rickshaw":                       # road vibration and bumps, 1-9 Hz
        b, a = butter(2, [1 / 10, 9 / 10], "band"); m += lfilter(b, a, r.normal(0, 0.12, n))
    elif kind == "turning in bed":
        for k in r.integers(0, n - 60, 10): m[k:k + 60] += 0.2 * np.sin(np.linspace(0, 3 * np.pi, 60))
    return m
