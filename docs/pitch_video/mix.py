"""Mix voice over music with ducking: python mix.py voice.wav music.wav out.wav"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

vsr, v = wavfile.read(sys.argv[1]); msr, m = wavfile.read(sys.argv[2])
v = resample_poly(v.astype(np.float32) / 32768, msr, vsr); m = m.astype(np.float32) / 32768
n = max(len(v), len(m)); v = np.pad(v, (0, n - len(v))); m = np.pad(m, ((0, n - len(m)), (0, 0)))
v *= 0.9 / np.abs(v).max()
# duck the music while someone speaks: envelope with fast attack, slow release
blk = msr // 100; e = np.sqrt(np.add.reduceat(v ** 2, np.arange(0, n, blk)) / blk) > 0.02
g = np.empty(len(e)); cur = 1.0
for i, on in enumerate(e):
    tgt = 0.32 if on else 1.0
    cur += (tgt - cur) * (0.35 if tgt < cur else 0.04); g[i] = cur
gain = np.repeat(g, blk)[:n] * 0.55
out = m * gain[:, None] + v[:, None]
out *= 0.95 / np.abs(out).max()
wavfile.write(sys.argv[3], msr, (out * 32767).astype(np.int16))
