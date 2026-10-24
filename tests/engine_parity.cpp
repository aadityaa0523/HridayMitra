// Reads daily rows (CSV from stdin: patient_id, then the 11 engine inputs) and prints "patient_id,day,light" per row.
// Used by tests/test_engine_parity.py to prove the ESP32 engine gives the same lights as the Python engine.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include "../firmware/hridaymitra_stool/engine_core.h"

static float num(const char* s) { return (s[0] == 0 || s[0] == '\n') ? NAN : (float)atof(s); }

int main() {
  char line[1024]; std::string cur; hm::Engine e; int day = 0;
  while (fgets(line, sizeof line, stdin)) {
    char* f[16]; int k = 0; char* p = line;
    f[k++] = p;
    while (*p && k < 16) { if (*p == ',') { *p = 0; f[k++] = p + 1; } p++; }
    if (k < 12) continue;
    if (cur != f[0]) { cur = f[0]; e.reset(); day = 0; }
    hm::DayIn d;
    for (int s = 0; s < hm::N_SIG; s++) d.v[s] = num(f[1 + s]);
    d.breathless = num(f[9]); d.orthopnea = num(f[10]); d.situps = num(f[11]);
    printf("%s,%d,%d\n", cur.c_str(), day++, e.add(d).light);
  }
}
