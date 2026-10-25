"""Original music bed for the pitch video (no samples, no licences): python music.py out.wav
Heartbeats land on the ECG R peaks drawn in index.html (same path, drawn by length over 13 s)."""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR, DUR, BPM = 48000, 240.0, 100
BEAT = 60 / BPM
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)
L, R = np.zeros(N), np.zeros(N)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)


def add(sig, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N: return
    sig = sig[:N - i] * gain
    L[i:i + len(sig)] += sig * np.sqrt((1 - pan) / 2) * 1.41
    R[i:i + len(sig)] += sig * np.sqrt((1 + pan) / 2) * 1.41


def env(n, a, r):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na); e[n - nr:] *= np.linspace(1, 0, nr); return e


def lp(x, f, order=2): return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)


def saw(f, n, harm=10):
    x = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * k * x + k) / k for k in range(1, harm))


def pad(notes, dur, cutoff=1400):
    n = int(dur * SR); x = np.zeros(n)
    for m in notes:
        for det in (-0.08, 0, 0.08):
            x += saw(hz(m + det), n, 8)
    return lp(x, cutoff) * env(n, dur * 0.35, dur * 0.4) / (len(notes) * 3)


def pluck(m, dur=0.6):
    n = int(dur * SR); x = np.arange(n) / SR
    return (np.sin(2 * np.pi * hz(m) * x) + 0.3 * np.sin(4 * np.pi * hz(m) * x)) * np.exp(-x * 7)


def kick():
    n = int(0.35 * SR); x = np.arange(n) / SR
    f = 45 + 80 * np.exp(-x * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 9)


def thump(f0=55, d=0.3):
    n = int(d * SR); x = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(f0 + 40 * np.exp(-x * 25)) / SR) * np.exp(-x * 14)


def noise(d): return rng.standard_normal(int(d * SR))


# ECG R-peak times: same path as index.html, drawn by arc length over 13 s
pts = [(0, 540)]
for x in range(0, 1920, 160):
    pts += [(x + 40, 540), (x + 52, 528), (x + 62, 540), (x + 72, 540), (x + 80, 560), (x + 90, 380), (x + 100, 640),
            (x + 110, 540), (x + 128, 540), (x + 140, 512), (x + 152, 540), (x + 160, 540)]
pts = np.array(pts, float); seg = np.hypot(*np.diff(pts, axis=0).T); cum = np.concatenate([[0], np.cumsum(seg)])
peaks = [cum[i] / cum[-1] * 13 for i, p in enumerate(pts) if p[1] == 380]
for k, pt in enumerate(peaks):
    g = 0.55 + 0.35 * k / len(peaks)
    add(thump(), pt, g); add(thump(70, 0.2), pt + 0.2, g * 0.6)

CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]       # Am F C G
BAR = 4 * BEAT
# drone 0-20
add(lp(saw(hz(33), int(20.5 * SR), 6), 300) * env(int(20.5 * SR), 6, 1.5), 0, 0.25)
# riser 14-20.4
n = int(6.4 * SR); r = noise(6.4); x = np.arange(n) / n
add(hp(r, 800) * x ** 2 * 0.25, 14.0)
add(np.sin(2 * np.pi * np.cumsum(200 + 900 * x ** 2) / SR) * x ** 3 * 0.12, 14.0)
# hit at logo
add(thump(40, 1.6) * 1.4, 20.35); add(lp(noise(2.5), 3000) * np.exp(-np.arange(int(2.5 * SR)) / SR * 2.2) * 0.25, 20.35)
# pads from 20.4 to the end
start = 20.4; k = 0
while start < 236:
    add(pad([m - 12 for m in CH[k % 4]] + [CH[k % 4][0] + 12], BAR * 1.15), start, 0.7, 0.15 * np.sin(k)); start += BAR; k += 1
add(pad([45, 57, 60, 64, 69], 9, 1800), 230.5, 0.9)
# arp from 30, bass + kick from 46, hats from 78, break 113-116.5, outro from 228
t0 = 30.0
for i in range(int((228 - t0) / (BEAT / 2))):
    tt = t0 + i * BEAT / 2; ch = CH[int((tt - 20.4) // BAR) % 4]
    if 113 <= tt < 116.5: continue
    add(pluck(ch[i % 3] + 12 + (12 if i % 8 == 7 else 0)), tt, 0.16 if tt < 46 else 0.2, 0.5 if i % 2 else -0.5)
for i in range(int((228 - 46) / BEAT)):
    tt = 46 + i * BEAT
    if 113 <= tt < 116.5: continue
    ch = CH[int((tt - 20.4) // BAR) % 4]
    add(kick(), tt, 0.75)
    nb = int(BEAT * SR); xb = np.arange(nb) / SR
    add(lp(saw(hz(ch[0] - 24), nb, 5), 400) * np.exp(-xb * 3), tt, 0.35)
    if tt >= 78:
        add(hp(noise(0.06), 7000) * np.exp(-np.arange(int(0.06 * SR)) / SR * 70), tt + BEAT / 2, 0.12, 0.3)
# whooshes on scene changes
for s in [30, 46, 66, 78, 88, 96, 105, 113, 123, 131, 140, 152, 168, 182, 196, 208, 228]:
    d = 0.9; n = int(d * SR); w = np.sin(np.linspace(0, np.pi, n)) ** 2
    add(lp(hp(noise(d), 500), 4000) * w * 0.13, s - 0.6, 1.0, rng.uniform(-.6, .6))
# reverb, master
ir_n = int(2.2 * SR); dec = np.exp(-np.arange(ir_n) / SR * 3)
irL, irR = rng.standard_normal(ir_n) * dec, rng.standard_normal(ir_n) * dec
wetL, wetR = fftconvolve(L, irL)[:N] * 0.012, fftconvolve(R, irR)[:N] * 0.012
L, R = L + wetL, R + wetR
fade = np.ones(N); fn = int(4 * SR); fade[-fn:] = np.linspace(1, 0, fn) ** 2
mix = np.stack([L, R], 1) * fade[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.6) * 0.89
wavfile.write(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', SR, (mix * 32767).astype(np.int16))
print('peaks', [round(p, 2) for p in peaks])
