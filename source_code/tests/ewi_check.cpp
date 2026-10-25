// Reads lines "z5 z20 z50" (ohm) and prints the firmware's extracellular-water index for each (tests/test_engine_parity.py).
#include <cstdio>
#include "../firmware/hridaymitra_stool/engine_core.h"

int main() {
  double f[3] = {5e3, 20e3, 50e3}, z[3];
  while (scanf("%lf %lf %lf", &z[0], &z[1], &z[2]) == 3) printf("%.9f\n", hm::ewiClosedForm(f, z));
}
