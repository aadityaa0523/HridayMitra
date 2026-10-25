// Walk test core: chest-pendant step counter + best 6 minutes of walking. Shared by the amulet firmware and
// tests/walk_check.cpp; engine/signals.py walk_window()/walk6() is the same maths in Python (tests/test_walk.py).
// Input: accelerometer magnitude in g at 20 samples per second. Each step lifts and drops the trunk once, so walking
// is a strong rhythm of 0.3-1.5 s; vehicle vibration, fidgeting and cord swing are not. Per 5 s window: find the
// step period by autocorrelation, steps = 5 s / period. Rolling sum of 72 windows = steps in the last 6 minutes.
#pragma once
#include <math.h>
#include <stdint.h>

namespace hm {
const int WALK_FS = 20, WALK_WIN = 100;     // 5 s windows
const int LAG_MIN = 6, LAG_MAX = 30;        // step period 0.3-1.5 s = 40-200 steps per minute
const float WALK_R = 0.5f;                  // rhythm strength needed to call it walking
const float WALK_SD = 0.008f;               // g: below this the wearer is still
const int WALK_SLOTS = 72;                  // 72 x 5 s = 6 minutes

// steps in one window of WALK_WIN samples (0 if it is not walking)
inline float walkWindow(const float* x) {
  float m = 0; for (int i = 0; i < WALK_WIN; i++) m += x[i];
  m /= WALK_WIN;
  float v = 0; for (int i = 0; i < WALK_WIN; i++) v += (x[i] - m) * (x[i] - m);
  v /= WALK_WIN;
  if (sqrtf(v) < WALK_SD) return 0;
  float r[LAG_MAX + 2];
  for (int L = LAG_MIN - 1; L <= LAG_MAX + 1; L++) {
    float s = 0; for (int i = 0; i + L < WALK_WIN; i++) s += (x[i] - m) * (x[i + L] - m);
    r[L] = s / ((WALK_WIN - L) * v);
  }
  float rmax = -1; for (int L = LAG_MIN; L <= LAG_MAX; L++) if (r[L] > rmax) rmax = r[L];
  if (rmax < WALK_R) return 0;
  for (int L = LAG_MIN; L <= LAG_MAX; L++)   // first strong peak = one step (a later one may be a full stride)
    if (r[L] >= r[L - 1] && r[L] >= r[L + 1] && r[L] >= 0.6f * rmax) {
      float den = r[L - 1] - 2 * r[L] + r[L + 1];
      float lag = L + (den < 0 ? 0.5f * (r[L - 1] - r[L + 1]) / den : 0);   // parabolic peak: sub-sample period
      return (float)WALK_WIN / lag;
    }
  return 0;
}

struct Walk {
  float buf[WALK_WIN]; int k = 0;
  float slot[WALK_SLOTS] = {0}; int cur = 0; float total = 0;
  // one sample; every 5 s returns the steps in the last 6 minutes, otherwise -1
  int add(float mag) {
    buf[k++] = mag;
    if (k < WALK_WIN) return -1;
    k = 0;
    float s = walkWindow(buf); total += s; slot[cur] = s; cur = (cur + 1) % WALK_SLOTS;
    float sum = 0; for (int i = 0; i < WALK_SLOTS; i++) sum += slot[i];
    return (int)(sum + 0.5f);
  }
};
}  // namespace hm
