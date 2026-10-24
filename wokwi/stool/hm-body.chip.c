// HridayMitra PATIENT DIGITAL TWIN + 8-electrode impedance front end (Wokwi custom chip).
// Electrically: drives the INA126 output node (ESP32 ADC) the way the LTspice-verified front end does,
//   v = 1.65 V + gain x current x Z x cos(2 pi 5 kHz t) + mains hum,
// for the path the 74HC4052s select (S1 S0: legs, arms, right side, left side) and SEL (body or R5 reference).
// Visually: a body with its 8 electrodes; while the stool measures, the current path lights up through the limbs;
// legs and chest fill with blue as fluid builds up; live impedances and warnings underneath.
// Sliders: leg / chest fluid (+10 % fluid -> -8.7 % legs, -9.1 % chest at 5 kHz, from LTspice), lifted foot, hum.
// The 50 kHz waveform only runs while EXC (GPIO25, excitation enable) is high, so the simulation stays fast.
#include "wokwi-api.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
// Tiny graphics for HridayMitra's Wokwi chips: pixels, rectangles, circles, lines and a 3x5 font (drawn 2x).
// Included by the chips (tools/make_wokwi.py pastes it in for the Wokwi web editor). Colours are 0xAABBGGRR.
#include <string.h>

typedef struct { buffer_t fb; uint32_t w, h; uint32_t *px; } gfx_t;

static void gfx_init(gfx_t *g) {
  g->fb = framebuffer_init(&g->w, &g->h);
  g->px = calloc(g->w * g->h, 4);
}
static void gfx_flush(gfx_t *g) { buffer_write(g->fb, 0, g->px, g->w * g->h * 4); }
static void gfx_put(gfx_t *g, int x, int y, uint32_t c) { if (x >= 0 && y >= 0 && x < (int)g->w && y < (int)g->h) g->px[y * g->w + x] = c; }
static void gfx_rect(gfx_t *g, int x, int y, int w, int h, uint32_t c) {
  for (int j = y; j < y + h; j++) for (int i = x; i < x + w; i++) gfx_put(g, i, j, c);
}
static void gfx_circle(gfx_t *g, int cx, int cy, int r, uint32_t c) {
  for (int j = -r; j <= r; j++) for (int i = -r; i <= r; i++) if (i * i + j * j <= r * r) gfx_put(g, cx + i, cy + j, c);
}
static void gfx_line(gfx_t *g, int x0, int y0, int x1, int y1, int thick, uint32_t c) {
  int dx = abs(x1 - x0), sx = x0 < x1 ? 1 : -1, dy = -abs(y1 - y0), sy = y0 < y1 ? 1 : -1, err = dx + dy;
  for (;;) {
    gfx_rect(g, x0 - thick / 2, y0 - thick / 2, thick, thick, c);
    if (x0 == x1 && y0 == y1) break;
    int e2 = 2 * err;
    if (e2 >= dy) { err += dy; x0 += sx; }
    if (e2 <= dx) { err += dx; y0 += sy; }
  }
}
static uint32_t gfx_mix(uint32_t a, uint32_t b, float t) {   // blend colour a -> b by t (0..1)
  if (t < 0) t = 0; if (t > 1) t = 1;
  uint32_t out = 0xFF000000;
  for (int s = 0; s < 24; s += 8) out |= (uint32_t)(((a >> s) & 255) * (1 - t) + ((b >> s) & 255) * t) << s;
  return out;
}

static const char *GFX_FONT = " 000000000000000A010101111101101B110101110101110C011100100100011D110101101101110E111100110100111"
  "F111100110100100G011100101101011H101101111101101I111010010010111J001001001101010K101101110101101L100100100100111"
  "M101111111101101N110101101101101O010101101101010P110101110100100Q010101101110011R110101110101101S011100010001110"
  "T111010010010010U101101101101111V101101101101010W101101111111101X101101010101101Y101101010010010Z111001010100111"
  "0111101101101111101011001001011121100010101001113110001010001110410110111100100151111001100011106011100111101111"
  "711100101001001081111011111011119111101111001110.000000000000010,000000000010100:000010000010000;000010000010100"
  "+000010111010000-000000111000000%101001010100101/001001010100100(001010010010001)100010010010100'010010000000000"
  "!010010010000010?110001010000010\"101101000000000=000111000111000<001010100010001>100010001010100";

static const char *gfx_glyph(char ch) {
  if (ch >= 'a' && ch <= 'z') ch -= 32;
  for (const char *f = GFX_FONT; *f; f += 16) if (*f == ch) return f + 1;
  return GFX_FONT + 1;
}

// text at pixel (x, y), scale s (1 = 4x6 cell, 2 = 8x12 cell); returns the x after the text
static int gfx_text(gfx_t *g, int x, int y, const char *s, int sc, uint32_t c) {
  for (; *s; s++, x += 4 * sc) {
    const char *gl = gfx_glyph(*s);
    for (int r = 0; r < 5; r++) for (int k = 0; k < 3; k++) if (gl[r * 3 + k] == '1') gfx_rect(g, x + k * sc, y + r * sc, sc, sc, c);
  }
  return x;
}


typedef struct {
  pin_t sel, s0, s1, out, exc; timer_t timer;
  uint32_t leg, chest, lifted, hum;
  gfx_t g; int lastKey;
} chip_t;

static const double ONE_LEG = 289.25, ONE_ARM = 329.2, TRUNK = 27.95, R5 = 220.0, GAIN_I = 10 * 100e-6;
enum { BG = 0xFF2A1A12, SKIN = 0xFF7FA6D9, WATER = 0xFFE07A2C, LINE = 0xFF505050, TXT = 0xFFEAEAEA, DIM = 0xFF9A9A9A,
       CURRENT = 0xFF33E6FF, ELEC = 0xFFC0C0C0, WARN = 0xFF3B3BFF, HEAD = 0xFFFFB04A, OK = 0xFF66D766 };

static double legZ(chip_t *c) { return ONE_LEG * (1 - 0.87 * attr_read_float(c->leg) / 100); }
static double trunkZ(chip_t *c) { return TRUNK * (1 - 0.91 * attr_read_float(c->chest) / 100); }

static void tick(void *data) {
  chip_t *c = data;
  double t = get_sim_nanos() / 1e9, leg = legZ(c), tr = trunkZ(c);
  int path = pin_read(c->s0) | (pin_read(c->s1) << 1);
  double z[4] = {2 * leg, 2 * ONE_ARM, ONE_ARM + tr + leg, ONE_ARM + tr + leg};
  bool ref = pin_read(c->sel);
  double v = 1.65 + attr_read_float(c->hum) / 1000 * 10 * sin(2 * M_PI * 50 * t);
  v += GAIN_I * (ref ? R5 : z[path]) * cos(2 * M_PI * 5000 * t);
  if (!ref && path == 0 && attr_read(c->lifted)) v = 1.65 + 3.0 * sin(2 * M_PI * 50 * t);   // foot off a plate
  pin_dac_write(c->out, v < 0 ? 0 : (v > 3.3 ? 3.3 : v));
}

// body geometry (display 180 x 230): limb end points used for the electrodes and the current path
#define SH_L 66, 64
#define SH_R 114, 64
#define PELVIS 90, 132
#define HAND_L 46, 120
#define HAND_R 134, 120
#define FOOT_L 74, 196
#define FOOT_R 106, 196

static void draw(chip_t *c) {
  gfx_t *g = &c->g;
  float lf = attr_read_float(c->leg) / 30, cf = attr_read_float(c->chest) / 30;
  bool exc = pin_read(c->exc), ref = pin_read(c->sel), lifted = attr_read(c->lifted);
  int path = pin_read(c->s0) | (pin_read(c->s1) << 1);
  gfx_rect(g, 0, 0, g->w, g->h, BG);
  gfx_rect(g, 0, 0, g->w, 14, 0xFF4A2E1C);
  gfx_text(g, 4, 2, "PATIENT DIGITAL TWIN", 2, HEAD);
  // body: legs and chest tinted by fluid
  uint32_t legC = gfx_mix(SKIN, WATER, lf), chestC = gfx_mix(SKIN, WATER, cf);
  gfx_circle(g, 90, 36, 13, SKIN);                                     // head
  gfx_rect(g, 84, 49, 12, 8, SKIN);                                    // neck
  gfx_rect(g, 66, 57, 48, 78, chestC);                                 // trunk
  gfx_line(g, SH_L, HAND_L, 11, SKIN); gfx_line(g, SH_R, HAND_R, 11, SKIN);   // arms
  gfx_line(g, 80, 134, FOOT_L, 15, legC); gfx_line(g, 100, 134, FOOT_R, 15, legC);   // legs
  if (cf > 0.02f) gfx_text(g, 72, 86, "LUNG", 1, TXT);
  // electrode plates: 2 per hand (strips), 2 per foot (forefoot + heel)
  int ex[8][2] = {{40, 114}, {40, 126}, {140, 114}, {140, 126}, {64, 204}, {80, 204}, {100, 204}, {116, 204}};
  for (int k = 0; k < 8; k++) gfx_rect(g, ex[k][0] - 6, ex[k][1] - 3, 12, 6, (lifted && (k == 4 || k == 5)) ? WARN : ELEC);
  // the current path being measured right now
  if (exc && !ref) {
    switch (path) {
      case 0: gfx_line(g, FOOT_L, PELVIS, 3, CURRENT); gfx_line(g, PELVIS, FOOT_R, 3, CURRENT); break;          // legs
      case 1: gfx_line(g, HAND_L, SH_L, 3, CURRENT); gfx_line(g, SH_L, SH_R, 3, CURRENT); gfx_line(g, SH_R, HAND_R, 3, CURRENT); break;
      case 2: gfx_line(g, HAND_R, SH_R, 3, CURRENT); gfx_line(g, SH_R, PELVIS, 3, CURRENT); gfx_line(g, PELVIS, FOOT_R, 3, CURRENT); break;
      case 3: gfx_line(g, HAND_L, SH_L, 3, CURRENT); gfx_line(g, SH_L, PELVIS, 3, CURRENT); gfx_line(g, PELVIS, FOOT_L, 3, CURRENT); break;
    }
    const char *names[4] = {"Z1 LEGS", "Z2 ARMS", "Z3 RIGHT SIDE", "Z4 LEFT SIDE"};
    gfx_text(g, 4, 18, "MEASURING", 1, CURRENT); gfx_text(g, 4, 25, names[path], 1, CURRENT);
  } else if (exc && ref) gfx_text(g, 4, 18, "R5 REFERENCE", 1, CURRENT);
  // live numbers
  char b[64];
  snprintf(b, sizeof b, "LEG FLUID +%d%%  Z %d OHM", (int)attr_read_float(c->leg), (int)(2 * legZ(c) + 0.5)); gfx_text(g, 4, 212, b, 1, lf > 0 ? WATER : TXT);
  snprintf(b, sizeof b, "CHEST FLUID +%d%%  Z %.1f OHM", (int)attr_read_float(c->chest), trunkZ(c)); gfx_text(g, 4, 219, b, 1, cf > 0 ? WATER : TXT);
  if (lifted) gfx_text(g, 104, 18, "FOOT LIFTED!", 1, WARN);
  else if (attr_read_float(c->hum) > 50) gfx_text(g, 110, 18, "MAINS HUM", 1, DIM);
  gfx_flush(g);
}

static void refresh(void *data) {                     // redraw only when something visible changed
  chip_t *c = data;
  int key = (int)attr_read_float(c->leg) * 131 + (int)attr_read_float(c->chest) * 7 + attr_read(c->lifted) * 3 +
            ((int)attr_read_float(c->hum) > 50) * 5 + pin_read(c->exc) * 1000 + pin_read(c->sel) * 2000 +
            (pin_read(c->s0) | (pin_read(c->s1) << 1)) * 4000;
  if (key != c->lastKey) { c->lastKey = key; draw(c); }
}

static void on_exc(void *data, pin_t pin, uint32_t value) {
  chip_t *c = data;
  if (value) timer_start(c->timer, 20, true);         // 50 kHz: 10 points per 5 kHz cycle
  else { timer_stop(c->timer); pin_dac_write(c->out, 1.65); }
}

void chip_init(void) {
  chip_t *c = calloc(1, sizeof(chip_t));
  c->sel = pin_init("SEL", INPUT); c->s0 = pin_init("S0", INPUT); c->s1 = pin_init("S1", INPUT);
  c->out = pin_init("OUT", ANALOG); c->exc = pin_init("EXC", INPUT);
  c->leg = attr_init_float("legFluid", 0); c->chest = attr_init_float("chestFluid", 0);
  c->lifted = attr_init("footLifted", 0); c->hum = attr_init_float("humMv", 20);
  const timer_config_t cfg = {.user_data = c, .callback = tick};
  c->timer = timer_init(&cfg);
  const pin_watch_config_t w = {.user_data = c, .edge = BOTH, .pin_change = on_exc};
  pin_watch(c->exc, &w);
  pin_dac_write(c->out, 1.65);
  gfx_init(&c->g); c->lastKey = -1; draw(c);
  const timer_config_t r = {.user_data = c, .callback = refresh};
  timer_start(timer_init(&r), 100000, true);          // 10 redraw checks per second
}
