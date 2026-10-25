// HridayMitra alert engine, C++ port of engine/alert_engine.py (frozen v2, cusum off) so it runs OFFLINE on the ESP32.
// Engine v3 = v2 + leg spectroscopy (extracellular-water index). Same rules, same numbers: guest gate, plate (toe-ring) gate, robust personal baseline (days t-35..t-7), worsening-only
// z scores, three families, two-witness red with hysteresis, oxygen danger rule.
// Plain C++ (no Arduino calls) so tests/engine_parity.cpp can compile it on a laptop and compare with Python.
#pragma once
#include <math.h>
#include <string.h>
#include <algorithm>

namespace hm {

enum Sig { WEIGHT, LEG, TRUNK, PULSE, NIGHT_RR, SPO2, ACTIVITY, STANDUP, LEG_EWI, N_SIG };
// family 0 fluid, 1 heart_lungs, 2 daily_life;  bad direction;  minimum spread;  spread relative?;  weight in family
static const int   FAM[N_SIG]   = {0, 0, 0, 1, 1, 1, 2, 2, 0};
static const float SGN[N_SIG]   = {+1, -1, -1, +1, +1, -1, -1, +1, +1};
static const float FLOOR_[N_SIG] = {0.30f, 0.010f, 3.0f, 2.0f, 0.7f, 0.7f, 0.08f, 0.04f, 0.003f};
static const bool  REL[N_SIG]   = {false, true, false, false, false, false, true, true, true};
static const float WT[N_SIG]    = {1, 1, 0.5f, 1, 1, 0.5f, 1, 1, 1};
static const bool  STOOL[N_SIG] = {true, true, true, true, false, true, false, true, true};
static const char* NAME[N_SIG]  = {"weight", "leg reading", "chest reading", "resting pulse", "night breathing",
                                  "oxygen", "activity", "stand-up time", "leg water outside cells"};
static const char* UNIT[N_SIG]  = {"kg", "%", "%", "bpm", "/min", "%", "%", "%", "%"};

const int HIST = 40, BASE_FROM = 35, BASE_TO = 7, MIN_BASE = 6;
const float GUEST_JUMP_KG = 2.5f, PLATE_JUMP = 0.25f, T_FROZEN = 7.0f;   // engine v3 (engine/frozen_params_v3.json)

struct DayIn {                 // one daily check-in; NAN = not measured
  float v[N_SIG];
  float breathless, orthopnea, situps;   // 0/1 answers (NAN = not answered), night sit-ups count
};

struct Result {
  int light;                   // 0 green, 1 amber, 2 red
  float S, fam[3], z[N_SIG + 2];// z[N_SIG] = symptoms, z[N_SIG+1] = night sit-ups
  float level[N_SIG], normal[N_SIG];
  bool guest, learning, danger, data;
};

// Which foot plate lost contact, from which of the 4 paths failed (z: legs, arms, right side, left side; NAN = failed).
// The left foot is in the legs and left-side paths, the right foot in legs and right side. 0 none, 1 left, 2 right, 3 unclear.
inline int liftedFoot(const float z[4]) {
  if (!isnan(z[0])) return 0;
  bool l = isnan(z[3]), r = isnan(z[2]);
  return (l && !r) ? 1 : (r && !l) ? 2 : 3;
}

inline float median(float* a, int n) {
  std::sort(a, a + n);
  return n % 2 ? a[n / 2] : 0.5f * (a[n / 2 - 1] + a[n / 2]);
}

class Engine {
 public:
  float T = T_FROZEN;
  Engine() { reset(); }
  const DayIn& latestGated() const { return at(n - 1); }   // today's readings after the guest/plate gates (app export)
  void reset() { n = 0; red = false; for (int i = 0; i < 3; i++) high[i] = famHigh[i] = false; hn = 0; lastLight = 0; }

  Result add(const DayIn& in) {
    Result r; memset(&r, 0, sizeof r);
    DayIn d = in;
    const int t = n;
    // 1. guest gate on weight (compares with the last 7 kept weights)
    r.guest = false;
    if (!isnan(d.v[WEIGHT])) {
      float buf[7]; int k = 0;
      for (int j = std::max(0, t - 7); j < t; j++) if (!isnan(at(j).v[WEIGHT])) buf[k++] = at(j).v[WEIGHT];
      if (k >= 3 && fabsf(d.v[WEIGHT] - median(buf, k)) > GUEST_JUMP_KG) {
        r.guest = true;
        for (int s = 0; s < N_SIG; s++) if (STOOL[s]) d.v[s] = NAN;
      }
    }
    // 2. plate gate on the leg reading (toe ring / bad placement)
    if (!isnan(d.v[LEG])) {
      float buf[7]; int k = 0;
      for (int j = std::max(0, t - 7); j < t; j++) if (!isnan(at(j).v[LEG])) buf[k++] = at(j).v[LEG];
      if (k >= 3 && fabsf(d.v[LEG] / median(buf, k) - 1) > PLATE_JUMP) { d.v[LEG] = NAN; d.v[TRUNK] = NAN; d.v[LEG_EWI] = NAN; }
    }
    store(d);
    // 3. per-signal worsening score against the personal normal
    bool any = false;
    for (int s = 0; s < N_SIG; s++) {
      r.z[s] = -1;                                           // -1 = no score
      float base[BASE_FROM]; int nb = 0;
      for (int j = std::max(0, t - BASE_FROM); j < std::max(0, t - BASE_TO + 1); j++)
        if (!isnan(at(j).v[s])) base[nb++] = at(j).v[s];
      float lsum = 0; int nl = 0;
      for (int j = std::max(0, t - 2); j <= t; j++) if (!isnan(at(j).v[s])) { lsum += at(j).v[s]; nl++; }
      if (nb < MIN_BASE || nl == 0) continue;
      float med = median(base, nb), dev[BASE_FROM];
      for (int i = 0; i < nb; i++) dev[i] = fabsf(base[i] - med);
      float spread = std::max(1.4826f * median(dev, nb), FLOOR_[s] * (REL[s] ? fabsf(med) : 1.0f));
      float dz = (lsum / nl - med) / spread * SGN[s];
      r.z[s] = WT[s] * std::min(5.0f, std::max(0.0f, dz));
      r.level[s] = lsum / nl; r.normal[s] = med; any = true;
    }
    float yes = 0, sit = 0; bool anySit = false;
    for (int j = std::max(0, t - 2); j <= t; j++) {
      const DayIn& q = at(j);
      yes += (isnan(q.breathless) ? 0 : q.breathless) + (isnan(q.orthopnea) ? 0 : q.orthopnea);
      if (!isnan(q.situps)) { sit += q.situps; anySit = true; }
    }
    r.z[N_SIG] = 1.2f * std::max(0.0f, yes - 1);
    r.z[N_SIG + 1] = anySit ? std::max(0.0f, sit - 1) : -1;
    // 4. families: strongest + half of the second
    for (int f = 0; f < 3; f++) {
      float a = -1, b = -1;
      for (int s = 0; s < N_SIG + 2; s++) {
        int fam = s < N_SIG ? FAM[s] : 2;
        if (fam != f || r.z[s] < 0) continue;
        float v = r.z[s];
        if (v > a) { b = a; a = v; } else if (v > b) b = v;
      }
      r.fam[f] = a < 0 ? 0 : a + (b < 0 ? 0 : 0.5f * b);
    }
    r.S = r.fam[0] + r.fam[1] + r.fam[2];
    int nFam = 0; float maxFam = 0;
    for (int f = 0; f < 3; f++) { nFam += r.fam[f] >= 1.5f; maxFam = std::max(maxFam, r.fam[f]); }
    r.danger = !r.guest && in.v[SPO2] < 90;                   // NAN < 90 is false
    r.learning = !any;
    bool answered = !isnan(in.breathless) || !isnan(in.orthopnea);
    r.data = answered;
    for (int s = 0; s < N_SIG; s++) r.data |= !isnan(d.v[s]);
    // 5. lights with persistence, two witnesses and hysteresis
    push(r.S >= T, maxFam >= T);
    if (!r.data) { r.light = lastLight; return r; }
    if (r.danger) red = true;
    else if (red) red = r.S >= 0.4f * T;
    else red = (cnt(high) >= 2 && nFam >= 2) || (hn >= 3 && cnt(famHigh) == 3);
    r.light = red ? 2 : (r.S >= 0.6f * T ? 1 : 0);
    lastLight = r.light;
    return r;
  }

  // top reasons in plain words, e.g. "weight +1.8 kg; leg reading -6 %"
  static void reasons(const Result& r, char* out, int len) {
    int idx[N_SIG + 2]; for (int i = 0; i < N_SIG + 2; i++) idx[i] = i;
    std::sort(idx, idx + N_SIG + 2, [&](int a, int b) { return r.z[a] > r.z[b]; });
    out[0] = 0; int used = 0;
    for (int k = 0; k < 3; k++) {
      int s = idx[k]; if (r.z[s] < 1) break;
      char part[64];
      if (s == N_SIG) snprintf(part, sizeof part, "breathless or extra pillows");
      else if (s == N_SIG + 1) snprintf(part, sizeof part, "sitting up at night");
      else if (UNIT[s][0] == '%') snprintf(part, sizeof part, "%s %+.0f %%", NAME[s], 100 * (r.level[s] / r.normal[s] - 1));
      else snprintf(part, sizeof part, "%s %+.1f %s", NAME[s], r.level[s] - r.normal[s], UNIT[s]);
      used += snprintf(out + used, len - used, "%s%s", used ? "; " : "", part);
    }
  }

 private:
  DayIn ring[HIST]; int n; bool red, high[3], famHigh[3]; int hn, lastLight;
  const DayIn& at(int j) const { return ring[j % HIST]; }
  void store(const DayIn& d) { ring[n % HIST] = d; n++; }
  void push(bool h, bool fh) { for (int i = 0; i < 2; i++) { high[i] = high[i + 1]; famHigh[i] = famHigh[i + 1]; } high[2] = h; famHigh[2] = fh; hn++; }
  static int cnt(const bool* a) { return a[0] + a[1] + a[2]; }
};

// Extracellular-water index from |Z| at 3 frequencies, exact Cole fit for alpha = 1 (same as engine/bis.py
// ewi_closed_form): y_i = A + f_i^2 B - f_i^2 y_i C with y = |Z|^2, A = R0^2, B = Rinf^2/fc^2, C = 1/fc^2. Returns NAN if unsolvable.
inline float ewiClosedForm(const double f[3], const double z[3]) {
  double M[3][4];
  for (int i = 0; i < 3; i++) { double f2 = f[i] * f[i], y = z[i] * z[i]; M[i][0] = 1; M[i][1] = f2; M[i][2] = -f2 * y; M[i][3] = y; }
  for (int c = 0; c < 3; c++) {                          // Gauss-Jordan with partial pivoting
    int piv = c; for (int r = c + 1; r < 3; r++) if (fabs(M[r][c]) > fabs(M[piv][c])) piv = r;
    if (fabs(M[piv][c]) < 1e-30) return NAN;
    for (int k = 0; k < 4; k++) { double t = M[c][k]; M[c][k] = M[piv][k]; M[piv][k] = t; }
    for (int r = 0; r < 3; r++) if (r != c) { double q = M[r][c] / M[c][c]; for (int k = c; k < 4; k++) M[r][k] -= q * M[c][k]; }
  }
  double A = M[0][3] / M[0][0], B = M[1][3] / M[1][1], C = M[2][3] / M[2][2];
  if (A <= 0 || B <= 0 || C <= 0) return NAN;
  return (float)(sqrt(B / C) / sqrt(A));
}

}  // namespace hm
