// Renders a HridayMitra Wokwi chip's screen on a laptop (no Wokwi): a host stand-in for the Wokwi chip API runs the
// chip's real drawing code and saves screens as PPM images. Build once per chip: -DBODY or -DMONITOR.
// Usage: chip_preview <out_dir>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define __attribute__(x)
#include "../../wokwi/chips/wokwi-api.h"
#undef __attribute__

static float ATTR[32]; static const char *ANAME[32]; static int nattr;
static uint32_t PIN[32]; static const char *PNAME[32]; static int npin;
static uint32_t *FB; static uint32_t FBW, FBH;
static void (*UART_RX)(void *, uint8_t); static void *UART_USER;
static timer_config_t TIMERS[8]; static int ntimer;

uint32_t attr_init(const char *n, uint32_t d) { ANAME[nattr] = n; ATTR[nattr] = d; return nattr++; }
uint32_t attr_init_float(const char *n, float d) { ANAME[nattr] = n; ATTR[nattr] = d; return nattr++; }
uint32_t attr_read(uint32_t a) { return (uint32_t)ATTR[a]; }
float attr_read_float(uint32_t a) { return ATTR[a]; }
pin_t pin_init(const char *n, uint32_t m) { PNAME[npin] = n; PIN[npin] = 0; return npin++; }
uint32_t pin_read(pin_t p) { return PIN[p]; }
float pin_dac_write(pin_t p, float v) { return v; }
bool pin_watch(pin_t p, const pin_watch_config_t *c) { return true; }
timer_t timer_init(const timer_config_t *c) { TIMERS[ntimer] = *c; return ntimer++; }
void timer_start(const timer_t t, uint32_t us, bool r) {}
void timer_stop(const timer_t t) {}
double get_sim_nanos_d(void) { return 0; }
uart_dev_t uart_init(const uart_config_t *c) { UART_RX = c->rx_data; UART_USER = c->user_data; return 1; }
bool uart_write(uart_dev_t u, uint8_t *b, uint32_t n) { return true; }
i2c_dev_t i2c_init(const i2c_config_t *c) { return 1; }
buffer_t framebuffer_init(uint32_t *w, uint32_t *h) { *w = FBW; *h = FBH; FB = calloc(FBW * FBH, 4); return 1; }
void buffer_write(buffer_t b, uint32_t off, void *d, uint32_t n) { memcpy((char *)FB + off, d, n); }

static void set_attr(const char *n, float v) { for (int i = 0; i < nattr; i++) if (!strcmp(ANAME[i], n)) ATTR[i] = v; }
static void set_pin(const char *n, uint32_t v) { for (int i = 0; i < npin; i++) if (!strcmp(PNAME[i], n)) PIN[i] = v; }
static void save(const char *dir, const char *name) {
  char p[256]; snprintf(p, sizeof p, "%s/%s.ppm", dir, name);
  FILE *f = fopen(p, "wb"); fprintf(f, "P6 %u %u 255\n", FBW, FBH);
  for (uint32_t i = 0; i < FBW * FBH; i++) { uint32_t c = FB[i]; fputc(c & 255, f); fputc((c >> 8) & 255, f); fputc((c >> 16) & 255, f); }
  fclose(f);
}

#ifdef BODY
#include "../../wokwi/chips/hm-body.chip.c"
int main(int argc, char **argv) {
  const char *dir = argc > 1 ? argv[1] : ".";
  FBW = 180; FBH = 230; chip_init();
  save(dir, "twin_idle");
  void (*redraw)(void *) = TIMERS[1].callback; void *chip = TIMERS[1].user_data;   // the 100 ms refresh timer
  set_attr("legFluid", 18); set_attr("chestFluid", 12); set_pin("EXC", 1); set_pin("S1", 1); redraw(chip);
  save(dir, "twin_measuring_right_side_fluid");
  set_pin("S1", 0); set_pin("S0", 0); set_attr("footLifted", 1); redraw(chip);
  save(dir, "twin_foot_lifted");
  return 0;
}
#endif

#ifdef MONITOR
#include "../../wokwi/chips/hm-monitor.chip.c"
static void feed(const char *s) { for (; *s; s++) UART_RX(UART_USER, (uint8_t)*s); }
int main(int argc, char **argv) {
  const char *dir = argc > 1 ? argv[1] : ".";
  FBW = 220; FBH = 170; chip_init();
  char b[600];
  float S[] = {0.4f, 0.9f, 0.3f, 1.2f, 0.6f, 0.8f, 0.5f, 1.4f, 2.1f, 4.4f, 7.7f, 16.0f};
  int L[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2};
  for (int i = 0; i < 12; i++) {
    snprintf(b, sizeof b, "{\"t\":\"checkin\",\"id\":\"P001\",\"weight_kg\":%.2f,\"leg_z_ohm\":%.1f,\"pulse_bpm\":%.1f,\"spo2\":96.0,"
             "\"light\":%d,\"S\":%.2f,\"learning\":0,\"guest\":0,\"why\":\"%s\"}\n", 62 + 0.2 * i, 578 - 3.0 * i, 72 + i * 0.8, L[i], S[i],
             i == 11 ? "weight +1.7 kg; breathless or extra pillows; leg reading -4 %" : (i == 10 ? "weight +0.8 kg; resting pulse +3.6 bpm" : ""));
    feed(b);
    if (i == 8) save(dir, "monitor_green");
  }
  feed("{\"t\":\"sms\",\"to\":\"+910000000001\",\"text\":\"x\"}\n{\"t\":\"sms\",\"to\":\"+910000000001\",\"text\":\"y\"}\n");
  save(dir, "monitor_red");
  return 0;
}
#endif
