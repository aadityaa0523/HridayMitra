// HridayMitra virtual patient + impedance front end (Wokwi custom chip).
// Drives the INA126 output node (to the ESP32 ADC) exactly as the LTspice-verified front end would:
//   v = 1.65 V + gain x current x Z x cos(2 pi 5 kHz t) + mains hum
// Z depends on the path the 74HC4052s select (S1 S0: legs, arms, right side, left side) and on SEL (body or R5).
// Sliders: leg fluid and chest fluid (+10 % fluid lowers the 5 kHz reading 8.7 % legs / 9.1 % chest, from LTspice),
// a lifted foot (floating 10 Mohm input saturates), and mains hum. Monitoring, not diagnosis.
#include "wokwi-api.h"
#include <math.h>
#include <stdlib.h>

typedef struct {
  pin_t sel, s0, s1, out;
  uint32_t leg, chest, lifted, hum;
} chip_t;

static const double ONE_LEG = 289.25, ONE_ARM = 329.2, TRUNK = 27.95, R5 = 220.0, GAIN_I = 10 * 100e-6;

static void tick(void *data) {
  chip_t *c = data;
  double t = get_sim_nanos() / 1e9;
  double leg = ONE_LEG * (1 - 0.87 * attr_read_float(c->leg) / 100);
  double tr = TRUNK * (1 - 0.91 * attr_read_float(c->chest) / 100);
  int path = pin_read(c->s0) | (pin_read(c->s1) << 1);
  double z[4] = {2 * leg, 2 * ONE_ARM, ONE_ARM + tr + leg, ONE_ARM + tr + leg};
  bool ref = pin_read(c->sel);
  double v = 1.65 + attr_read_float(c->hum) / 1000 * 10 * sin(2 * M_PI * 50 * t);
  v += GAIN_I * (ref ? R5 : z[path]) * cos(2 * M_PI * 5000 * t);
  if (!ref && path == 0 && attr_read(c->lifted)) v = 1.65 + 3.0 * sin(2 * M_PI * 50 * t);   // foot off a plate
  pin_dac_write(c->out, v < 0 ? 0 : (v > 3.3 ? 3.3 : v));
}

void chip_init(void) {
  chip_t *c = malloc(sizeof(chip_t));
  c->sel = pin_init("SEL", INPUT); c->s0 = pin_init("S0", INPUT); c->s1 = pin_init("S1", INPUT);
  c->out = pin_init("OUT", ANALOG);
  c->leg = attr_init_float("legFluid", 0); c->chest = attr_init_float("chestFluid", 0);
  c->lifted = attr_init("footLifted", 0); c->hum = attr_init_float("humMv", 20);
  const timer_config_t cfg = {.user_data = c, .callback = tick};
  timer_start(timer_init(&cfg), 20, true);            // 50 kHz: 10 points per 5 kHz cycle
}
