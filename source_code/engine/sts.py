"""SIT-TO-STAND TIME ON THE PLATFORM (the chair stands on the weighing platform, so the weight never leaves it).

Physics: the platform carries chair + person all the time; the chair is in the tare, so the reading is the person's
weight m plus the inertial term m·a(t)/g while the body's centre of mass accelerates up and then brakes. So
    a(t) ≈ g · (w(t) − m) / m.
The rise is fitted with a minimum-jerk centre-of-mass path (start t0, duration D, height h): for each (t0, D) the best h
is a one-line least squares, and the (t0, D) with the smallest residual wins. A real stand needs h between 0.12 and
0.65 m and the fit to explain at least half of the signal; otherwise "no reading". Same maths as hm::stsFit in
firmware/hridaymitra_stool/engine_core.h. The reading stops at step-off (weight below half the person's).
make_sts() builds test signals with a DIFFERENT motion model (skewed velocity, forward-lean dip, sway, HX711 noise and
10 Hz averaging), so the detector is not graded on its own assumptions.
"""
import numpy as np

G = 9.81
H_MIN, H_MAX, Q_MIN = 0.12, 0.65, 0.5
D_GRID = np.round(np.arange(0.6, 6.01, 0.05), 3)


def mj_accel(t, t0, D):
    """Minimum-jerk acceleration shape for unit height: (60τ − 180τ² + 120τ³) / D², zero outside the rise."""
    tau = (t - t0) / D
    a = (60 * tau - 180 * tau ** 2 + 120 * tau ** 3) / D ** 2
    return np.where((tau >= 0) & (tau <= 1), a, 0.0)


def sts_fit(w, fs=10.0):
    """Platform readings (kg, person-only, from the 'stand up' prompt) -> (rise time s or None, height m, quality)."""
    w = np.asarray(w, float)
    m = float(np.median(w[: max(3, int(fs))]))                 # first second: still seated
    if not m > 20:
        return None, 0.0, 0.0
    off = np.flatnonzero(w < 0.5 * m)                           # stepped off the platform: stop before the drop began
    w = w[: max(0, off[0] - int(np.ceil(0.8 * fs)))] if len(off) else w
    if len(w) < 2 * fs:
        return None, 0.0, 0.0
    a = G * (w - m) / m
    z = np.cumsum(np.cumsum(a) / fs) / fs                       # centre-of-mass height change (double integral)
    t = np.arange(len(w)) / fs
    Q = np.linalg.qr(np.column_stack([np.ones_like(t), t, t * t]))[0]   # slow drift from the integration (bias in m)
    zr = z - Q @ (Q.T @ z)
    zz = float(zr @ zr)
    best = (np.inf, None, 0.0)
    for D in D_GRID:
        for t0 in t[: max(1, len(t) - int(D * fs))]:
            tau = np.clip((t - t0) / D, 0, 1)
            s = 10 * tau ** 3 - 15 * tau ** 4 + 6 * tau ** 5      # minimum-jerk rise, unit height
            sr = s - Q @ (Q.T @ s)
            ss = float(sr @ sr)
            if ss <= 1e-9:
                continue
            h = float(sr @ zr) / ss
            res = zz - h * h * ss
            if res < best[0]:
                best = (res, (t0, D), h)
    res, td, h = best
    q = 1 - res / zz if zz > 0 else 0.0
    if td is None or not (H_MIN <= h <= H_MAX) or q < Q_MIN:
        return None, h, q
    return float(td[1]), h, q


def make_sts(m=70.0, D=2.0, fs=10.0, seed=0, start=None, h=None, skew=None, lean=0.02, sway_kg=0.12, noise_kg=0.04,
             step_off=3.0, total=12.0, stand=True):
    """Platform readings (kg) at fs for a person of m kg who rises in D seconds, plus the true rise time.
    Velocity of the centre of mass: skewed bell t^p (1-t)^q (fast push, slower finish or the reverse), a forward-lean dip
    before the rise, low-frequency body sway, HX711 noise; the HX711 averages over each sample period."""
    r = np.random.default_rng(seed)
    start = r.uniform(1.2, 3.0) if start is None else start
    h = r.uniform(0.28, 0.42) if h is None else h
    skew = r.uniform(0.35, 0.65) if skew is None else skew
    F = 1000.0
    t = np.arange(0, total, 1 / F)
    z = np.zeros_like(t)
    if stand:
        tau = np.clip((t - start) / D, 0, 1)
        p, q = 2 * skew * 2.5, 2 * (1 - skew) * 2.5
        v = np.where((tau > 0) & (tau < 1), tau ** p * (1 - tau) ** q, 0.0)
        z = h * np.cumsum(v) / max(v.sum(), 1e-12)
        dip = np.where((t > start - 0.5) & (t < start + 0.3), -lean * np.sin(np.pi * (t - start + 0.5) / 0.8) ** 2, 0.0)
        z = z + dip
    acc = np.gradient(np.gradient(z, 1 / F), 1 / F)
    sway = np.convolve(r.normal(0, 1, len(t)), np.ones(400) / 400, "same")
    sway = sway / max(sway.std(), 1e-12) * sway_kg
    w = m * (1 + acc / G) + sway
    if stand and step_off is not None:
        t_off = start + D + step_off
        w = w * np.clip(1 - (t - t_off) / 0.6, 0, 1)            # steps off the platform over 0.6 s
    k = int(F / fs)
    ws = w[: len(w) // k * k].reshape(-1, k).mean(axis=1) + r.normal(0, noise_kg, len(w) // k)
    return ws, (D if stand else None)
