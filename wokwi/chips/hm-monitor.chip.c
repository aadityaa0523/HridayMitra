// HridayMitra STOOL MONITOR (Wokwi custom chip): listens to the stool's USB serial (115200) and draws what the
// on-chip alert engine decided: a big green / amber / red light, the warning score against the frozen threshold,
// the trend of the last 24 check-ins, the reasons in plain words, the readings, SMS count and self-test status.
// Nothing here decides anything: it only shows the firmware's own JSON reports.
#include "wokwi-api.h"
#include <stdio.h>
#include <stdlib.h>
#include "gfx.inc"

#define HIST 24
static const float T = 7.0f;                          // frozen threshold (engine/frozen_params_v3.json)
enum { BG = 0xFF261810, BAR = 0xFF4A2E1C, TXT = 0xFFEAEAEA, DIM = 0xFF9A9A9A, GRID = 0xFF3A3A3A,
       GREEN = 0xFF4CC24C, AMBER = 0xFF1AB4F5, RED = 0xFF3B3BE8, HEAD = 0xFFFFB04A, BLUE = 0xFFE07A2C };

typedef struct {
  char line[700]; int ll;
  float S[HIST]; int light[HIST]; int n;
  char why[120], id[12], selftest[60]; float weight, leg, spo2, pulse; int sms, guest, learning;
  gfx_t g;
} chip_t;

static float num(const char *j, const char *k) {
  char key[40]; snprintf(key, sizeof key, "\"%s\":", k);
  const char *p = strstr(j, key); return p ? (float)atof(p + strlen(key)) : -1;
}
static void str(const char *j, const char *k, char *out, int n) {
  char key[40]; snprintf(key, sizeof key, "\"%s\":\"", k);
  const char *p = strstr(j, key); out[0] = 0; if (!p) return;
  p += strlen(key); int i = 0; while (*p && *p != '"' && i < n - 1) out[i++] = *p++; out[i] = 0;
}

static void draw(chip_t *c) {
  gfx_t *g = &c->g; char b[80];
  uint32_t col[3] = {GREEN, AMBER, RED}; const char *word[3] = {"GREEN", "AMBER", "RED"};
  gfx_rect(g, 0, 0, g->w, g->h, BG);
  gfx_rect(g, 0, 0, g->w, 14, BAR);
  gfx_text(g, 4, 2, "HRIDAYMITRA STOOL MONITOR", 2, HEAD);
  int L = c->n ? c->light[(c->n - 1) % HIST] : -1;
  // big light
  gfx_circle(g, 32, 48, 26, L < 0 ? GRID : col[L]);
  gfx_text(g, L == 2 ? 20 : 12, 44, L < 0 ? "WAIT" : word[L], 2, 0xFF101010);
  // score gauge against the threshold
  float S = c->n ? c->S[(c->n - 1) % HIST] : 0;
  gfx_text(g, 66, 20, c->n ? c->id : "NO CHECK-IN YET", 2, TXT);
  snprintf(b, sizeof b, "SCORE %.1f / RED AT %.1f", S, T); gfx_text(g, 66, 36, b, 1, TXT);
  gfx_rect(g, 66, 44, 150, 8, GRID);
  int w = (int)(150 * (S / (2 * T) > 1 ? 1 : S / (2 * T))); gfx_rect(g, 66, 44, w, 8, S >= T ? RED : (S >= 0.6f * T ? AMBER : GREEN));
  gfx_rect(g, 66 + 75, 42, 2, 12, TXT);               // threshold mark at the middle of the bar
  if (c->learning) gfx_text(g, 66, 58, "STILL LEARNING THIS PERSON", 1, DIM);
  else if (c->guest) gfx_text(g, 66, 58, "GUEST: READING IGNORED", 1, AMBER);
  // trend of the last check-ins
  int x0 = 6, y0 = 82, gw = 210, gh = 40;
  gfx_text(g, x0, y0 - 8, "WARNING SCORE, LAST 24 CHECK-INS", 1, DIM);
  gfx_rect(g, x0, y0, gw, gh, 0xFF1C120C);
  int ty = y0 + gh - (int)(gh * T / (2 * T)); for (int i = x0; i < x0 + gw; i += 4) gfx_rect(g, i, ty, 2, 1, RED);
  int m = c->n < HIST ? c->n : HIST;
  for (int k = 0; k < m; k++) {
    int idx = (c->n - m + k) % HIST; float s = c->S[idx] > 2 * T ? 2 * T : c->S[idx];
    int h = (int)(gh * s / (2 * T)); gfx_rect(g, x0 + 2 + k * 9, y0 + gh - h, 7, h > 0 ? h : 1, col[c->light[idx]]);
  }
  // reasons and readings
  gfx_text(g, 4, 128, "WHY:", 1, DIM);
  char why[120]; snprintf(why, sizeof why, "%s", c->why[0] ? c->why : "-");
  for (int row = 0, i = 0; row < 2 && why[i]; row++) {          // wrap at spaces, 48 characters a row
    int end = i, last = -1;
    while (why[end] && end - i < 48) { if (why[end] == ' ') last = end; end++; }
    if (why[end] && last > i) end = last;
    char ln[52]; int k = 0; while (i < end) ln[k++] = why[i++]; ln[k] = 0;
    while (why[i] == ' ') i++;
    gfx_text(g, 22, 128 + row * 7, ln, 1, TXT);
  }
  if (c->weight > 0) { snprintf(b, sizeof b, "WEIGHT %.1f KG  LEG %d OHM  PULSE %d  SPO2 %d", c->weight, (int)c->leg, (int)c->pulse, (int)c->spo2); gfx_text(g, 4, 146, b, 1, BLUE); }
  snprintf(b, sizeof b, "SMS SENT %d   SELF-TEST %s", c->sms, c->selftest[0] ? c->selftest : "OK"); gfx_text(g, 4, 158, b, 1, c->selftest[0] ? AMBER : GREEN);
  gfx_flush(g);
}

static void rx(void *d, uint8_t ch) {
  chip_t *c = d;
  if (ch != '\n') { if (c->ll < (int)sizeof c->line - 1) c->line[c->ll++] = ch; return; }
  c->line[c->ll] = 0; c->ll = 0;
  const char *j = c->line;
  if (strstr(j, "\"t\":\"checkin\"")) {
    int k = c->n % HIST;
    c->S[k] = num(j, "S"); c->light[k] = (int)num(j, "light"); c->n++;
    str(j, "why", c->why, sizeof c->why); str(j, "id", c->id, sizeof c->id);
    c->weight = num(j, "weight_kg"); c->leg = num(j, "leg_z_ohm"); c->pulse = num(j, "pulse_bpm"); c->spo2 = num(j, "spo2");
    c->guest = num(j, "guest") > 0; c->learning = num(j, "learning") > 0;
    draw(c);
  } else if (strstr(j, "\"t\":\"sms\"")) { c->sms++; draw(c); }
  else if (strstr(j, "\"t\":\"selftest\"")) { str(j, "problems", c->selftest, sizeof c->selftest); draw(c); }
}

static void done(void *d) {}

void chip_init(void) {
  chip_t *c = calloc(1, sizeof(chip_t));
  const uart_config_t u = {.user_data = c, .rx = pin_init("RX", INPUT), .tx = pin_init("TX", INPUT_PULLUP), .baud_rate = 115200,
                           .rx_data = rx, .write_done = done};
  uart_init(&u);
  gfx_init(&c->g); draw(c);
}
