// SIM800L GSM modem + the family's phone (Wokwi custom chip, UART 9600).
// Answers the AT commands the stool uses (AT, CMGF, CMGS, CCLK, CBC, CSQ, CNMI, CLIP, CLTS, ATH) and shows every SMS
// the stool sends on a 160x120 phone screen. Sliders: the family's / ASHA's reply (1 checking, 2 need help, 3 fine),
// a missed call, network outage, battery and signal. The network clock runs 60x fast (1 s of simulation = 1 minute)
// so a whole care-loop ladder (30 min, 2 h, 6 h) plays out in a few minutes; build the stool with -DHM_WOKWI.
#include "wokwi-api.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define W 160
#define H 120
#define WARP 60.0
static const char *FAMILY1 = "+910000000001", *ASHA = "+910000000003";

typedef struct {
  uart_dev_t uart; buffer_t fb;
  char line[200]; int ll; bool cmgs; char to[20]; char text[200]; int tl;
  char tx[2048]; int txHead, txTail; bool busy;
  uint32_t famReply, ashaReply, call, down, battery, signal;
  uint32_t lastFam, lastAsha, lastCall;
  char shown[6][200]; int nShown;
  uint32_t px[W * H];
} chip_t;

// ---------- 3x5 font (rows of 3 bits), drawn 2x -> 8 x 12 pixel cells, 20 columns x 9 rows ----------
static const char *GLYPH = " 000000000000000A010101111101101B110101110101110C011100100100011D110101101101110E111100110100111"
  "F111100110100100G011100101101011H101101111101101I111010010010111J001001001101010K101101110101101L100100100100111"
  "M101111111101101N110101101101101O010101101101010P110101110100100Q010101101110011R110101110101101S011100010001110"
  "T111010010010010U101101101101111V101101101101010W101101111111101X101101010101101Y101101010010010Z111001010100111"
  "0111101101101111101011001001011121100010101001113110001010001110410110111100100151111001100011106011100111101111"
  "711100101001001081111011111011119111101111001110.000000000000010,000000000010100:000010000010000;000010000010100"
  "+000010111010000-000000111000000%101001010100101/001001010100100(001010010010001)100010010010100'010010000000000"
  "!010010010000010?110001010000010\"101101000000000=000111000111000<001010100010001>100010001010100";

static const char *glyph(char ch) {
  if (ch >= 'a' && ch <= 'z') ch -= 32;
  for (const char *g = GLYPH; *g; g += 16) if (*g == ch) return g + 1;
  return GLYPH + 1;
}

static void put(chip_t *c, int x, int y, uint32_t col) { if (x >= 0 && x < W && y >= 0 && y < H) c->px[y * W + x] = col; }

static void text(chip_t *c, int col, int row, const char *s, uint32_t colr) {
  for (; *s && col < 20; s++, col++) {
    const char *g = glyph(*s);
    for (int r = 0; r < 5; r++) for (int k = 0; k < 3; k++) if (g[r * 3 + k] == '1')
      for (int dy = 0; dy < 2; dy++) for (int dx = 0; dx < 2; dx++) put(c, col * 8 + 1 + k * 2 + dx, 4 + row * 12 + r * 2 + dy, colr);
  }
}

static void redraw(chip_t *c) {
  const uint32_t BG = 0xFF201810, HEAD = 0xFF30A0FF, MSG = 0xFFF0F0F0, WHO = 0xFF60D060;   // ABGR
  for (int i = 0; i < W * H; i++) c->px[i] = i < W * 12 ? 0xFF503018 : BG;
  text(c, 0, 0, "FAMILY PHONE  SMS", HEAD);
  int row = 1;
  for (int m = c->nShown - 1; m >= 0 && row < 9; m--) {                // newest first, wrapped at 20 characters
    const char *s = c->shown[m];
    char chunk[21];
    for (int first = 1; *s && row < 9; first = 0) {
      int n = (int)strlen(s) < 20 ? (int)strlen(s) : 20;
      memcpy(chunk, s, n); chunk[n] = 0; text(c, 0, row++, chunk, first ? WHO : MSG); s += n;
    }
  }
  buffer_write(c->fb, 0, c->px, sizeof c->px);
}

// ---------- UART with a small transmit queue ----------
static void pump(chip_t *c) {
  if (c->busy || c->txHead == c->txTail) return;
  int n = c->txTail > c->txHead ? c->txTail - c->txHead : (int)sizeof c->tx - c->txHead;
  if (uart_write(c->uart, (uint8_t *)c->tx + c->txHead, n)) { c->busy = true; c->txHead = (c->txHead + n) % (int)sizeof c->tx; }
}
static void say(chip_t *c, const char *s) { for (; *s; s++) { c->tx[c->txTail] = *s; c->txTail = (c->txTail + 1) % (int)sizeof c->tx; } pump(c); }
static void write_done(void *d) { chip_t *c = d; c->busy = false; pump(c); }

static void civil(long z, int *y, int *m, int *dd) {                   // days since 1970 -> date
  z += 719468; long era = (z >= 0 ? z : z - 146096) / 146097; unsigned doe = (unsigned)(z - era * 146097);
  unsigned yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365; *y = (int)(yoe + era * 400);
  unsigned doy = doe - (365 * yoe + yoe / 4 - yoe / 100), mp = (5 * doy + 2) / 153;
  *dd = (int)(doy - (153 * mp + 2) / 5 + 1); *m = (int)(mp < 10 ? mp + 3 : mp - 9); *y += *m <= 2;
}

static void command(chip_t *c, const char *l) {
  char b[200];
  if (!strncmp(l, "AT+CMGS=\"", 9)) {
    c->cmgs = true; c->tl = 0; snprintf(c->to, sizeof c->to, "%.*s", (int)(strchr(l + 9, '"') - (l + 9)), l + 9);
    say(c, "\r\n> "); return;
  }
  if (!strcmp(l, "AT+CCLK?")) {
    double mins = get_sim_nanos() / 1e9 * WARP / 60.0 + 8 * 60;      // starts 25 Oct 2026, 08:00
    long day = 20751 + (long)(mins / 1440); int sod = (int)((mins - 1440.0 * (long)(mins / 1440)) * 60), y, m, d;
    civil(day, &y, &m, &d);
    snprintf(b, sizeof b, "\r\n+CCLK: \"%02d/%02d/%02d,%02d:%02d:%02d+22\"\r\n\r\nOK\r\n", y % 100, m, d, sod / 3600, sod / 60 % 60, sod % 60);
    say(c, b); return;
  }
  if (!strcmp(l, "AT+CBC")) { snprintf(b, sizeof b, "\r\n+CBC: 0,80,%u\r\n\r\nOK\r\n", attr_read(c->battery)); say(c, b); return; }
  if (!strcmp(l, "AT+CSQ")) { snprintf(b, sizeof b, "\r\n+CSQ: %u,0\r\n\r\nOK\r\n", attr_read(c->signal)); say(c, b); return; }
  if (*l) say(c, "\r\nOK\r\n");
}

static void rx(void *d, uint8_t ch) {
  chip_t *c = d;
  if (c->cmgs) {
    if (ch == 26) {                                                   // Ctrl+Z: send the SMS
      c->cmgs = false; c->text[c->tl] = 0;
      if (attr_read(c->down)) { say(c, "\r\n+CMS ERROR: 500\r\n"); return; }
      if (c->nShown == 6) { memmove(c->shown, c->shown + 1, sizeof c->shown[0] * 5); c->nShown = 5; }
      snprintf(c->shown[c->nShown++], 200, "TO %s: %s", strcmp(c->to, FAMILY1) ? (strcmp(c->to, ASHA) ? "DOCTOR/FAM2" : "ASHA") : "FAMILY", c->text);
      printf("SMS to %s: %s\n", c->to, c->text);
      redraw(c); say(c, "\r\n+CMGS: 1\r\n\r\nOK\r\n");
    } else if (c->tl < 199) c->text[c->tl++] = ch;
    return;
  }
  if (ch == '\r' || ch == '\n') { c->line[c->ll] = 0; command(c, c->line); c->ll = 0; }
  else if (c->ll < 199) c->line[c->ll++] = ch;
}

static void incoming(void *d) {                                       // slider changes become replies / calls
  chip_t *c = d; char b[160];
  uint32_t f = attr_read(c->famReply), a = attr_read(c->ashaReply), k = attr_read(c->call);
  if (f && f != c->lastFam) { snprintf(b, sizeof b, "\r\n+CMT: \"%s\",,\"26/10/25,08:00:00+22\"\r\n%u\r\n", FAMILY1, f); say(c, b); }
  if (a && a != c->lastAsha) { snprintf(b, sizeof b, "\r\n+CMT: \"%s\",,\"26/10/25,08:00:00+22\"\r\n%u\r\n", ASHA, a); say(c, b); }
  if (k && !c->lastCall) { snprintf(b, sizeof b, "\r\nRING\r\n\r\n+CLIP: \"%s\",145\r\n", FAMILY1); say(c, b); }
  c->lastFam = f; c->lastAsha = a; c->lastCall = k;
}

void chip_init(void) {
  chip_t *c = calloc(1, sizeof(chip_t));
  c->famReply = attr_init("familyReply", 0); c->ashaReply = attr_init("ashaReply", 0); c->call = attr_init("missedCall", 0);
  c->down = attr_init("networkDown", 0); c->battery = attr_init("batteryMv", 3950); c->signal = attr_init("signal", 18);
  const uart_config_t u = {.user_data = c, .rx = pin_init("RX", INPUT), .tx = pin_init("TX", INPUT_PULLUP), .baud_rate = 9600,
                           .rx_data = rx, .write_done = write_done};
  c->uart = uart_init(&u);
  uint32_t w, h; c->fb = framebuffer_init(&w, &h);
  redraw(c);
  const timer_config_t t = {.user_data = c, .callback = incoming};
  timer_start(timer_init(&t), 200000, true);
}
