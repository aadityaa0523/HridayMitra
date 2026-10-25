// Reads lines "n w1 w2 ... wn" (platform kg at 10 S/s) and prints the firmware's sit-to-stand fit: "D h q" (tests/test_sts.py).
#include <cstdio>
#include "../firmware/hridaymitra_stool/engine_core.h"

int main() {
  int n;
  static float w[hm::STS_MAX];
  while (scanf("%d", &n) == 1) {
    for (int i = 0; i < n; i++) if (scanf("%f", &w[i]) != 1) return 1;
    float h, q, D = hm::stsFit(w, n < hm::STS_MAX ? n : hm::STS_MAX, 10.0f, &h, &q);
    printf("%.4f %.4f %.4f\n", D, h, q);
  }
}
