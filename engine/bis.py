"""BIOIMPEDANCE SPECTROSCOPY: from |Z| at a few frequencies to body-water information.

At low frequency the current cannot cross cell membranes, so it only flows through the fluid OUTSIDE the cells
(extracellular water, where heart-failure congestion collects). At higher frequency it also flows through the cells.
  impedance_ratio(): IR = |Z50| / |Z5|. Rises when extracellular water rises; does not change when everything scales
                     together (foot position, limb length, skin temperature), because those cancel in a ratio.
  fit_cole():        fits the Cole model |Z(f)| = |Rinf + (R0 - Rinf) / (1 + (j f / fc)^alpha)| to the readings, giving
                     R0 (extracellular resistance) and Rinf (all water); Rinf / R0 is the extracellular-water index.
Each segment of the body model is Re || (Ri + Cm): R0 = Re, Rinf = Re*Ri/(Re+Ri), fc = 1 / (2 pi Cm (Re + Ri)), alpha = 1.
"""
import numpy as np
from scipy.optimize import least_squares


def cole(f, r0, rinf, fc, alpha=1.0):
    return rinf + (r0 - rinf) / (1 + (1j * np.asarray(f, float) / fc) ** alpha)


def segment(f, re, ri, cm):
    """Exact impedance of one Re || (Ri + Cm) segment (the LTspice body model)."""
    zc = 1 / (1j * 2 * np.pi * np.asarray(f, float) * cm)
    return re * (ri + zc) / (re + ri + zc)


def impedance_ratio(z5, z50):
    return None if z5 is None or z50 is None or z5 != z5 or z50 != z50 or z5 <= 0 else z50 / z5


def fit_cole(freqs, mags, alpha=1.0):
    """Least-squares Cole fit to magnitudes. Returns dict(r0, rinf, fc, ewi = rinf / r0, rms_error_pct)."""
    f, m = np.asarray(freqs, float), np.asarray(mags, float)
    def resid(p):
        r0, rinf, lfc = p
        return (np.abs(cole(f, r0, rinf, np.exp(lfc), alpha)) - m) / m
    p0 = [m.max() * 1.02, m.min() * 0.8, np.log(np.sqrt(f.min() * f.max()) * 3)]
    r = least_squares(resid, p0, bounds=([m.max() * 0.9, 1, np.log(1e3)], [m.max() * 1.5, m.min(), np.log(1e7)]))
    r0, rinf, lfc = r.x
    return dict(r0=r0, rinf=rinf, fc=float(np.exp(lfc)), ewi=rinf / r0, rms_error_pct=100 * float(np.sqrt(np.mean(r.fun ** 2))))


def ewi_closed_form(freqs, mags):
    """Exact Cole fit for alpha = 1 (the firmware's method, no iterations). With y = |Z|^2 and u = 1/fc^2:
    y = R0^2 + f^2 u (Rinf^2 - y)  ->  y_i = A + f_i^2 B - f_i^2 y_i C  with A = R0^2, B = u Rinf^2, C = u (linear).
    Three frequencies solve it exactly; more are solved by least squares. Returns (R0, Rinf, Rinf / R0)."""
    f2, y = np.asarray(freqs, float) ** 2, np.asarray(mags, float) ** 2
    M = np.column_stack([np.ones_like(f2), f2, -f2 * y])
    A, B, C = np.linalg.lstsq(M, y, rcond=None)[0]
    r0, rinf = np.sqrt(A), np.sqrt(B / C)
    return r0, rinf, rinf / r0
