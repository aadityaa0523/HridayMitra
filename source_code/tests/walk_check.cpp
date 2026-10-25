// Reads lines of 100 magnitude samples (g, 20 Hz) and prints the amulet's steps for each 5 s window (tests/test_walk.py).
#include <cstdio>
#include "../firmware/hridaymitra_amulet/walk_core.h"

int main() {
  float x[hm::WALK_WIN];
  for (;;) {
    for (int i = 0; i < hm::WALK_WIN; i++) if (scanf("%f", &x[i]) != 1) return 0;
    printf("%.6f\n", hm::walkWindow(x));
  }
}
