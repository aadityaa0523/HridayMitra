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
