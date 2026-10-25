"""Original music bed for the pitch video (no samples, no licences): python music.py out.wav
Follows timing.js (from voice.py): soft heartbeats under the story, a hit on the logo, a beat from the product scene,
a whoosh on every scene change."""
import json, pathlib, sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

TM = json.loads(pathlib.Path(__file__).with_name("timing.js").read_text().split("=", 1)[1].rstrip(";\n "))
SEG = TM["segs"]
SR, DUR, BPM = 48000, TM["total"] + 0.5, 100
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


# heartbeats under "meet" and "silent", getting faster as he gets worse
tt, k = 0.6, 0
while tt < SEG["silent"][1] - 1:
    g = 0.35 + 0.25 * tt / SEG["silent"][1]
    add(thump(), tt, g); add(thump(70, 0.2), tt + 0.2, g * 0.6)
    tt += 1.0 - 0.35 * tt / SEG["silent"][1]

CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]       # Am F C G
BAR = 4 * BEAT
LOGO = SEG["logo"][0] + 0.55
# drone under the story, riser into the logo
dn = int(LOGO * SR); add(lp(saw(hz(33), dn, 6), 300) * env(dn, 6, 1.5), 0, 0.22)
ri = 5.0; n = int(ri * SR); r = noise(ri); x = np.arange(n) / n
add(hp(r, 800) * x ** 2 * 0.2, LOGO - ri)
add(np.sin(2 * np.pi * np.cumsum(200 + 900 * x ** 2) / SR) * x ** 3 * 0.1, LOGO - ri)
add(thump(40, 1.6) * 1.4, LOGO); add(lp(noise(2.5), 3000) * np.exp(-np.arange(int(2.5 * SR)) / SR * 2.2) * 0.25, LOGO)
# pads from the logo to the end
start = LOGO; k = 0
while start < DUR - 4:
    add(pad([m - 12 for m in CH[k % 4]] + [CH[k % 4][0] + 12], BAR * 1.15), start, 0.7, 0.15 * np.sin(k)); start += BAR; k += 1
add(pad([45, 57, 60, 64, 69], 9, 1800), SEG["close"][0], 0.9)
# arp from the logo, bass + kick from the product scene, hats from the alert, outro on "close"
END, KICK, HAT = SEG["close"][0], SEG["product"][0], SEG["alert"][0]
for i in range(int((END - LOGO) / (BEAT / 2))):
    tt = LOGO + i * BEAT / 2; ch = CH[int((tt - LOGO) // BAR) % 4]
    add(pluck(ch[i % 3] + 12 + (12 if i % 8 == 7 else 0)), tt, 0.14 if tt < KICK else 0.18, 0.5 if i % 2 else -0.5)
for i in range(int((END - KICK) / BEAT)):
    tt = KICK + i * BEAT
    ch = CH[int((tt - LOGO) // BAR) % 4]
    add(kick(), tt, 0.75)
    nb = int(BEAT * SR); xb = np.arange(nb) / SR
    add(lp(saw(hz(ch[0] - 24), nb, 5), 400) * np.exp(-xb * 3), tt, 0.35)
    if tt >= HAT:
        add(hp(noise(0.06), 7000) * np.exp(-np.arange(int(0.06 * SR)) / SR * 70), tt + BEAT / 2, 0.12, 0.3)
# whooshes on scene changes
for s in [v[0] for v in SEG.values()][1:]:
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

