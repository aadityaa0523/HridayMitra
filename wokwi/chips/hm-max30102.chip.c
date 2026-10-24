// MAX30102 finger pulse-oximeter (Wokwi custom chip, I2C 0x57): part ID, FIFO pointers and an 18-bit red/IR
// FIFO filled at 100 samples/s with a real pulse waveform. Sliders: pulse, SpO2, finger on/off.
// SpO2 is encoded with the same ratio-of-ratios the firmware decodes (SpO2 = 110 - 25 R).
#include "wokwi-api.h"
#include <math.h>
#include <stdlib.h>

typedef struct {
  uint32_t bpm, spo2, finger;
  uint8_t reg, sample[6], byteIdx; bool first;
  uint64_t nextNs; uint32_t rd; bool running;
  uint32_t seed;
} chip_t;

static double noise(chip_t *c) { c->seed = c->seed * 1103515245 + 12345; return ((c->seed >> 16) & 0x7FFF) / 32768.0 - 0.5; }

static uint32_t pending(chip_t *c) {
  if (!c->running) return 0;
  uint64_t now = get_sim_nanos();
  uint64_t n = now > c->nextNs ? (now - c->nextNs) / 10000000ULL : 0;
  return n > 31 ? 31 : (uint32_t)n;
}

static void makeSample(chip_t *c) {
  double t = c->nextNs / 1e9, f = attr_read_float(c->bpm) / 60;
  double beat = sin(2 * M_PI * f * t) + 0.3 * sin(4 * M_PI * f * t), r = (110 - attr_read_float(c->spo2)) / 25;
  bool on = attr_read(c->finger);
  uint32_t ir = on ? (uint32_t)(100000 * (1 + 0.01 * beat) + 60 * noise(c)) : 500;
  uint32_t red = on ? (uint32_t)(80000 * (1 + 0.01 * r * beat) + 60 * noise(c)) : 400;
  uint8_t s[6] = {red >> 16, red >> 8, red, ir >> 16, ir >> 8, ir};
  for (int i = 0; i < 6; i++) c->sample[i] = s[i];
}

static bool on_connect(void *d, uint32_t addr, bool read) { chip_t *c = d; if (!read) c->first = true; return true; }

static bool on_write(void *d, uint8_t b) {
  chip_t *c = d;
  if (c->first) { c->reg = b; c->first = false; c->byteIdx = 0; return true; }
  if (c->reg == 0x09 && b == 0x03) { c->running = true; c->nextNs = get_sim_nanos(); c->rd = 0; }   // SpO2 mode on
  return true;
}

static uint8_t on_read(void *d) {
  chip_t *c = d;
  switch (c->reg) {
    case 0xFF: return 0x15;                              // part ID
    case 0x06: return c->rd & 31;                        // FIFO read pointer
    case 0x04: return (c->rd + pending(c)) & 31;         // FIFO write pointer
    case 0x07:
      if (c->byteIdx == 0) makeSample(c);
      { uint8_t b = c->sample[c->byteIdx++];
        if (c->byteIdx == 6) { c->byteIdx = 0; c->nextNs += 10000000ULL; c->rd++; }
        return b; }
    default: return 0;
  }
}

static void on_disconnect(void *d) {}

void chip_init(void) {
  chip_t *c = calloc(1, sizeof(chip_t));
  c->bpm = attr_init_float("pulse", 72); c->spo2 = attr_init_float("spo2", 97); c->finger = attr_init("finger", 1);
  c->seed = 7;
  const i2c_config_t cfg = {.user_data = c, .address = 0x57, .scl = pin_init("SCL", INPUT), .sda = pin_init("SDA", INPUT),
                            .connect = on_connect, .read = on_read, .write = on_write, .disconnect = on_disconnect};
  i2c_init(&cfg);
}
