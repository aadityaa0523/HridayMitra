// HridayMitra check-in stool firmware (ESP32 DevKit, WROOM-32, Arduino core 3.x). Monitoring, not diagnosis.
// One 90 s check-in a day: weight, 4 impedance paths (legs, arms, both sides -> chest), finger pulse + SpO2,
// yes/no questions, stand-up time, amulet summary over BLE. The alert engine (engine_core.h, same lights as the
// tested Python engine) runs ON the stool, offline, with a separate personal baseline for each of two users.
// Product layer (same rules as engine/product.py): the doctor's sick-day plan, coaching tips, daily self-test,
// missed check-in reminder, Sunday summary for the ASHA, vibration prompts for hard-of-hearing users, tablet drawer.
// Red alerts start the SMS care loop over the SIM800L. Pins: docs/src/HridayMitra build guide v3.html, section 4.
// USB serial (115200): one JSON line per event for tools/stool_bridge.py; commands: checkin, tare, cal <kg>,
// enroll <1|2>, day <11 values>, selftest, reset.
#include <Wire.h>
#include <Preferences.h>
#include <BLEDevice.h>
#include <BLEScan.h>
#include <driver/dac_cosine.h>
#include "config.h"
#include "engine_core.h"
#include "voice_clips.h"

// ---- pins (build guide v3.1) ----
const int HX_DT = 32, HX_SCK = 14, VOICE = 26, Z_ADC = 35, SEL = 18, PATH_S0 = 33, PATH_S1 = 27;
const int LED_G = 13, LED_A = 23, LED_R = 2, BTN_G = 4, BTN_R = 5, BTN_SOS = 15, GSM_RX = 16, GSM_TX = 17;
const int VIBRA = 19, DRAWER = 36;                       // seat vibration motor (via NPN); tablet-drawer switch to GND
const float R5 = 220.0f;

struct User {                                            // everything kept per person, saved in flash
  hm::Engine eng;
  float w0 = 0, z0 = 0; bool enrolled = false;
  int lastDay = -1; uint8_t lights[7] = {255, 255, 255, 255, 255, 255, 255}; uint8_t took[5] = {1, 1, 1, 1, 1};
};
User users[2];
const char* IDS[2] = {PATIENT_ID, PATIENT_ID2};
int enrollNext = -1;

Preferences prefs;
dac_cosine_handle_t cosine = nullptr;
float countsPerKg = DEFAULT_COUNTS_PER_KG, excHz = 5000, lastRefAmp = -1;
long tareCounts = 0;
bool drawerToday = false; int drawerDay = -1;

// ======================= small helpers =======================
void leds(int light) {
  digitalWrite(LED_G, light == 0); digitalWrite(LED_A, light == 1); digitalWrite(LED_R, light == 2);
}

void buzz(int ms) { digitalWrite(VIBRA, 1); delay(ms); digitalWrite(VIBRA, 0); }

void say(const Clip& c) {                                // 8-bit clip from flash through DAC2 -> PAM8403
  buzz(150);                                             // feelable cue before every prompt (hard of hearing)
  const uint32_t us = 1000000UL / c.rate;
  uint32_t t = micros();
  for (uint32_t i = 0; i < c.len; i++) {
    dacWrite(VOICE, pgm_read_byte(c.data + i));
    t += us; while ((int32_t)(micros() - t) < 0) {}
  }
  dacWrite(VOICE, 128);
}

int button(uint32_t timeoutMs) {                         // 1 = red (yes), 0 = green (no), -1 = no answer
  uint32_t t0 = millis();
  while (millis() - t0 < timeoutMs) {
    if (!digitalRead(BTN_R)) { delay(300); return 1; }
    if (!digitalRead(BTN_G)) { delay(300); return 0; }
    delay(10);
  }
  return -1;
}

void unsolicited(const String& buf);                     // defined with the SIM800L code below

// ======================= clock from the SIM800L network =======================
long daysFromCivil(int y, unsigned m, unsigned d) {      // days since 1970-01-01 (Howard Hinnant's algorithm)
  y -= m <= 2; const long era = (y >= 0 ? y : y - 399) / 400; const unsigned yoe = (unsigned)(y - era * 400);
  const unsigned doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1, doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + (long)doe - 719468;
}

bool clockNow(long& day, int& hour, int& wday) {         // wday 0 = Sunday; false if the network has not set the clock
  Serial2.println("AT+CCLK?"); uint32_t t0 = millis(); String b;
  while (millis() - t0 < 1000) while (Serial2.available()) b += (char)Serial2.read();
  unsolicited(b);
  int i = b.indexOf("+CCLK: \""); if (i < 0) return false;
  int y = b.substring(i + 8, i + 10).toInt(), mo = b.substring(i + 11, i + 13).toInt(), d = b.substring(i + 14, i + 16).toInt();
  if (y < 24 || mo < 1 || mo > 12) return false;
  hour = b.substring(i + 17, i + 19).toInt();
  day = daysFromCivil(2000 + y, mo, d); wday = (int)((day + 4) % 7);
  return true;
}

// ======================= HX711 (bit-banged, gain 128) =======================
long hxRaw() {
  uint32_t t0 = millis();
  while (digitalRead(HX_DT)) { if (millis() - t0 > 200) return LONG_MIN; delay(1); }
  long v = 0;
  for (int i = 0; i < 24; i++) {
    digitalWrite(HX_SCK, 1); delayMicroseconds(1); v = (v << 1) | digitalRead(HX_DT);
    digitalWrite(HX_SCK, 0); delayMicroseconds(1);
  }
  digitalWrite(HX_SCK, 1); delayMicroseconds(1); digitalWrite(HX_SCK, 0);
  return (v & 0x800000) ? v - 0x1000000 : v;
}

float kg() { long r = hxRaw(); return r == LONG_MIN ? NAN : (r - tareCounts) / countsPerKg; }

float stableWeight(uint32_t timeoutMs) {                 // 10 readings within 0.2 kg of each other
  float buf[10]; int n = 0; uint32_t t0 = millis();
  while (millis() - t0 < timeoutMs) {
    float w = kg(); if (isnan(w)) continue;
    buf[n++ % 10] = w;
    if (n >= 10) {
      float lo = 1e9, hi = -1e9, s = 0;
      for (float x : buf) { lo = min(lo, x); hi = max(hi, x); s += x; }
      if (hi - lo < 0.2f && s / 10 > 20) return s / 10;
    }
  }
  return NAN;
}

// ======================= impedance: Goertzel on the ADC, ratiometric against R5 =======================
float goertzelAmp(float& clipFrac, uint32_t windowUs = 100000) {   // 100 ms = 5 whole mains cycles
  double sx = 0, sc = 0, ss = 0, xc = 0, xs = 0; uint32_t n = 0, clip = 0;
  const double w = 2 * PI * excHz / 1e6;
  uint32_t t0 = micros(), t;
  while ((t = micros() - t0) < windowUs) {
    int x = analogRead(Z_ADC);
    double c = cos(w * t), s = sin(w * t);           // real sample time: the ADC rate does not need to be exact
    sx += x; sc += c; ss += s; xc += x * c; xs += x * s; n++;
    clip += (x < 5 || x > 4090);
  }
  clipFrac = (float)clip / n;
  double m = sx / n, re = xc - m * sc, im = xs - m * ss;   // remove the 1.65 V level before the DFT
  return 2 * sqrt(re * re + im * im) / n;
}

float measurePath(int path) {                            // path 0..3 = Z1 legs, Z2 arms, Z3 right, Z4 left
  digitalWrite(PATH_S0, path & 1); digitalWrite(PATH_S1, (path >> 1) & 1);
  delay(200);
  float zs[3];
  for (int k = 0; k < 3; k++) {
    float clipB, clipR;
    digitalWrite(SEL, 0); delay(20); float body = goertzelAmp(clipB);
    digitalWrite(SEL, 1); delay(20); float ref = goertzelAmp(clipR);
    lastRefAmp = ref;
    if (clipB > 0.01f || ref < 5) return NAN;            // open plate / lifted foot / no current: "no reading"
    zs[k] = R5 * body / ref;
  }
  return hm::median(zs, 3);
}

// ======================= MAX30102 finger sensor (minimal driver) =======================
const uint8_t MAX = 0x57;
void maxW(uint8_t r, uint8_t v) { Wire.beginTransmission(MAX); Wire.write(r); Wire.write(v); Wire.endTransmission(); }
uint8_t maxR(uint8_t r) { Wire.beginTransmission(MAX); Wire.write(r); Wire.endTransmission(false); Wire.requestFrom(MAX, (uint8_t)1); return Wire.read(); }

void maxInit() {
  maxW(0x09, 0x40); delay(100);                          // reset
  maxW(0x08, 0x1F);                                      // no averaging, FIFO rollover
  maxW(0x0A, 0x27);                                      // 4096 nA range, 100 samples/s, 18-bit
  maxW(0x0C, 0x24); maxW(0x0D, 0x24);                    // red and IR LED current about 7 mA
  maxW(0x04, 0); maxW(0x05, 0); maxW(0x06, 0);
  maxW(0x09, 0x03);                                      // SpO2 mode
}

const int NPPG = 1500;                                   // 15 s at 100 samples/s
static float red_[NPPG], ir_[NPPG];

bool pulseSpo2(float& bpm, float& spo2) {                // same method as engine/signals.py pulse_spo2()
  int n = 0; uint32_t t0 = millis();
  while (n < NPPG && millis() - t0 < 20000) {
    int avail = (maxR(0x04) - maxR(0x06)) & 31;
    while (avail-- > 0 && n < NPPG) {
      Wire.beginTransmission(MAX); Wire.write(0x07); Wire.endTransmission(false);
      Wire.requestFrom(MAX, (uint8_t)6);
      uint32_t r = 0, i = 0;
      for (int b = 0; b < 3; b++) r = (r << 8) | Wire.read();
      for (int b = 0; b < 3; b++) i = (i << 8) | Wire.read();
      red_[n] = r & 0x3FFFF; ir_[n] = i & 0x3FFFF; n++;
    }
    delay(5);
  }
  bpm = spo2 = NAN;
  if (n < NPPG) return false;
  double mr = 0, mi = 0; for (int k = 0; k < n; k++) { mr += red_[k]; mi += ir_[k]; } mr /= n; mi /= n;
  if (mi < 20000) return false;                          // no finger
  static float acI[NPPG], acR[NPPG];                     // AC part: minus a 1 s moving average
  for (int k = 0; k < n; k++) {
    int a = max(0, k - 50), b = min(n - 1, k + 50); double si = 0, sr = 0;
    for (int j = a; j <= b; j++) { si += ir_[j]; sr += red_[j]; }
    acI[k] = ir_[k] - si / (b - a + 1); acR[k] = red_[k] - sr / (b - a + 1);
  }
  double vi = 0, vr = 0; for (int k = 0; k < n; k++) { vi += acI[k] * acI[k]; vr += acR[k] * acR[k]; }
  float sdI = sqrt(vi / n), sdR = sqrt(vr / n);
  if (sdI / mi < 0.0005f) return false;                  // pulse too weak
  int peaks[60], np = 0;
  for (int k = 2; k < n - 2 && np < 60; k++)
    if (acI[k] > 0.5f * sdI && acI[k] >= acI[k - 1] && acI[k] >= acI[k + 1] && acI[k] > acI[k - 2] && acI[k] > acI[k + 2]
        && (np == 0 || k - peaks[np - 1] >= 33)) peaks[np++] = k;
  if (np < 5) return false;
  float ibi[59]; double s = 0, s2 = 0;
  for (int k = 1; k < np; k++) { ibi[k - 1] = (peaks[k] - peaks[k - 1]) / 100.0f; s += ibi[k - 1]; s2 += ibi[k - 1] * ibi[k - 1]; }
  int m = np - 1; double mean = s / m;
  if (sqrt(s2 / m - mean * mean) / mean > 0.25) return false;    // irregular or moving
  bpm = 60 / hm::median(ibi, m);
  float R = (sdR / mr) / (sdI / mi);
  spo2 = constrain(110 - 25 * R, 70, 100);               // generic calibration: check against a pulse oximeter
  return true;
}

// ======================= amulet summary over BLE (manufacturer data, no pairing) =======================
struct Amulet { float rr = NAN, situps = NAN, activity = NAN; bool sos = false; } amulet;

void scanAmulet() {
  BLEScan* scan = BLEDevice::getScan();
  scan->setActiveScan(false);
  auto* res = scan->start(4, false);
  for (int i = 0; i < res->getCount(); i++) {
    BLEAdvertisedDevice d = res->getDevice(i);
    if (!d.haveManufacturerData()) continue;
    auto md = d.getManufacturerData();                   // 0xFFFF test company id, "HM", rr*10, situps, activity/4, flags
    if (md.length() >= 9 && (uint8_t)md[0] == 0xFF && (uint8_t)md[1] == 0xFF && md[2] == 'H' && md[3] == 'M') {
      uint16_t rr10 = (uint8_t)md[4] | ((uint8_t)md[5] << 8);
      amulet.rr = rr10 ? rr10 / 10.0f : NAN;
      amulet.situps = (uint8_t)md[6];
      amulet.activity = (uint8_t)md[7] * 4.0f;
      amulet.sos = md[8] & 1;
    }
  }
  scan->clearResults();
}

// ======================= SIM800L: SMS queue with retries, replies, missed calls =======================
struct Sms { char to[16]; char text[160]; uint32_t nextTry; bool used; } q[10];
struct Loop { bool active = false, fine = false, ashaSent = false, ashaReplied = false, docSent = false, fam2Sent = false;
              bool replied = false; uint32_t t0 = 0; char who[8] = ""; char why[100] = ""; } loopSt;

String gsmLine() {
  String s; uint32_t t0 = millis();
  while (millis() - t0 < 50) if (Serial2.available()) { char c = Serial2.read(); if (c == '\n') break; if (c != '\r') s += c; t0 = millis(); }
  return s;
}

void onReply(const String& from, char digit);

void unsolicited(const String& buf) {                    // replies or missed calls caught inside another command's answer
  for (int i = buf.indexOf("+CMT: \""); i >= 0; i = buf.indexOf("+CMT: \"", i + 1)) {
    String from = buf.substring(i + 7, buf.indexOf('"', i + 7));
    int nl = buf.indexOf('\n', i);
    if (nl >= 0 && nl + 1 < (int)buf.length() && strchr("123", buf[nl + 1])) onReply(from, buf[nl + 1]);
  }
  for (int i = buf.indexOf("+CLIP: \""); i >= 0; i = buf.indexOf("+CLIP: \"", i + 1)) {
    Serial2.println("ATH"); onReply(buf.substring(i + 8, buf.indexOf('"', i + 8)), '1');
  }
}

bool gsmCmd(const char* cmd, const char* ok, uint32_t ms, String* out = nullptr) {
  Serial2.println(cmd); uint32_t t0 = millis(); String buf;
  while (millis() - t0 < ms) { while (Serial2.available()) buf += (char)Serial2.read(); if (buf.indexOf(ok) >= 0) { unsolicited(buf); if (out) *out = buf; return true; } }
  unsolicited(buf);
  if (out) *out = buf;
  return false;
}

bool sendNow(const char* to, const char* text) {
  if (!gsmCmd("AT+CMGF=1", "OK", 1000)) return false;
  Serial2.printf("AT+CMGS=\"%s\"\r", to);
  delay(300); Serial2.print(text); Serial2.write(26);
  return gsmCmd("", "+CMGS", 15000);
}

void queueSms(const char* to, const char* text) {
  for (auto& m : q) if (!m.used) { strlcpy(m.to, to, 16); strlcpy(m.text, text, 160); m.nextTry = 0; m.used = true; return; }
}

void serviceSms() {
  for (auto& m : q) if (m.used && millis() >= m.nextTry) {
    if (sendNow(m.to, m.text)) m.used = false;
    else m.nextTry = millis() + SMS_RETRY_MIN * 60000UL;  // no network or power cut: try again later
  }
}

void onReply(const String& from, char digit) {
  if (from.endsWith(String(ASHA).substring(3))) loopSt.ashaReplied = true;
  loopSt.replied = true;
  if (digit == '3') loopSt.fine = true;
  if (digit == '2' && !loopSt.ashaSent) { queueSms(ASHA, "HridayMitra: family asks for help. Please visit today."); loopSt.ashaSent = true; }
  Serial.printf("{\"t\":\"reply\",\"from\":\"%s\",\"digit\":\"%c\"}\n", from.c_str(), digit);
}

void serviceGsm() {
  while (Serial2.available()) {
    String l = gsmLine();
    if (l.startsWith("+CMT:")) {                         // incoming SMS: next line is the text
      String from = l.substring(l.indexOf('"') + 1); from = from.substring(0, from.indexOf('"'));
      String body = gsmLine(); body.trim();
      if (body.length() && strchr("123", body[0])) onReply(from, body[0]);
    } else if (l.startsWith("+CLIP:")) {                 // missed call counts as reply 1
      String from = l.substring(l.indexOf('"') + 1); from = from.substring(0, from.indexOf('"'));
      Serial2.println("ATH"); onReply(from, '1');
    }
  }
  if (!loopSt.active) return;
  uint32_t mins = (millis() - loopSt.t0) / 60000;
  char msg[160];
  if (!loopSt.replied && !loopSt.fam2Sent && mins >= ESC_FAMILY2_MIN) {
    snprintf(msg, sizeof msg, "HridayMitra RED for %s, no reply yet. Why: %s. Reply 1 checking, 2 need help, 3 fine.", loopSt.who, loopSt.why);
    queueSms(FAMILY2, msg); loopSt.fam2Sent = true;
  }
  if (!loopSt.fine && !loopSt.ashaSent && mins >= ESC_ASHA_MIN) {
    snprintf(msg, sizeof msg, "HridayMitra: please visit %s today. Warning signs: %s. Reply 1 when seen.", loopSt.who, loopSt.why);
    queueSms(ASHA, msg); loopSt.ashaSent = true;
  }
  if (!loopSt.fine && !loopSt.ashaReplied && !loopSt.docSent && mins >= ESC_DOCTOR_MIN) {
    snprintf(msg, sizeof msg, "HridayMitra: %s has heart-failure warning signs (%s), not seen in 6 h. Please call.", loopSt.who, loopSt.why);
    queueSms(DOCTOR, msg); loopSt.docSent = true;
  }
  if (loopSt.fine || loopSt.docSent || mins > 24 * 60) loopSt.active = false;
}

void startCareLoop(const char* who, const char* why, bool danger) {
  loopSt = Loop(); loopSt.active = true; loopSt.t0 = millis();
  strlcpy(loopSt.who, who, sizeof loopSt.who); strlcpy(loopSt.why, why, sizeof loopSt.why);
  char msg[160];
  snprintf(msg, sizeof msg, "HridayMitra RED for %s. Why: %s. Reply 1 checking, 2 need help, 3 fine. Not a diagnosis; breathless at rest: call 108.", who, why);
  queueSms(FAMILY1, msg);
  queueSms(FAMILY1, PLAN_RED);                           // the doctor's plan as a second SMS
  if (danger) { queueSms(FAMILY2, msg); queueSms(ASHA, msg); loopSt.fam2Sent = loopSt.ashaSent = true; }
}

// ======================= self-test (daily + at boot) =======================
void selfTest() {
  String probs, r;
  long raw = hxRaw();
  if (raw == LONG_MIN) probs += "scale not answering; ";
  else if (fabsf((raw - tareCounts) / countsPerKg) > 2) probs += "scale zero drifted, run tare; ";
  if (maxR(0xFF) != 0x15) probs += "finger sensor not found; ";
  int mv = -1, csq = -1;
  if (gsmCmd("AT+CBC", "OK", 1000, &r) && r.indexOf("+CBC:") >= 0) mv = r.substring(r.lastIndexOf(',') + 1).toInt();
  if (gsmCmd("AT+CSQ", "OK", 1000, &r) && r.indexOf("+CSQ:") >= 0) csq = r.substring(r.indexOf(':') + 2).toInt();
  if (mv > 0 && mv < 3500) probs += "battery low, charge the stool; ";
  if (mv < 0) probs += "SIM module not answering; ";
  if (csq >= 0 && (csq < 5 || csq == 99)) probs += "weak mobile signal; ";
  if (lastRefAmp >= 0 && lastRefAmp < 20) probs += "impedance current too low, check plates and wiring; ";
  Serial.printf("{\"t\":\"selftest\",\"battery_mv\":%d,\"signal\":%d,\"problems\":\"%s\"}\n", mv, csq, probs.c_str());
  if (probs.length()) {
    char msg[160]; snprintf(msg, sizeof msg, "HridayMitra stool needs service: %s", probs.c_str());
    queueSms(ASHA, msg);
  }
}

// ======================= users and the engine =======================
void saveUser(int u) { char k[4] = {'u', char('0' + u), 0}; prefs.putBytes(k, &users[u], sizeof(User)); }

int whoIsThis(float w, float z) {                        // same rule as engine/product.py identify()
  if (enrollNext >= 0) { int u = enrollNext; users[u] = User(); users[u].enrolled = true; users[u].w0 = w; users[u].z0 = z; enrollNext = -1; return u; }
  if (!users[1].enrolled) return 0;                      // one-person stool: the engine's own guest check applies
  int best = -1; float bestD = 1e9;
  for (int u = 0; u < 2; u++) {
    if (!users[u].enrolled && !(u == 0 && users[0].w0 > 0)) continue;   // user 1 is the stool's first regular user
    float d = max(fabsf(w - users[u].w0) / 3.0f, isnan(z) || users[u].z0 <= 0 ? 0.0f : fabsf(z / users[u].z0 - 1) / 0.15f);
    if (d <= 1 && d < bestD) { best = u; bestD = d; }
  }
  return best;                                           // -1 = guest
}

const Clip* coachingTip(const User& u, const hm::Result& r) {   // same order as engine/product.py coaching()
  int missed = 0; for (uint8_t t : u.took) missed += (t == 0);
  if (missed >= 2) return &CLIP_TIP_TABLETS;
  if (r.fam[1] >= 2 && r.fam[0] < 1) return &CLIP_TIP_INFECTION;
  if (r.z[hm::WEIGHT] >= 1 && r.z[hm::LEG] < 1) return &CLIP_TIP_SALT;
  if (r.fam[0] >= 1.5f) return &CLIP_TIP_FLUID;
  return nullptr;
}

void runEngine(int u, const hm::DayIn& d, int tookPills) {
  User& U = users[u];
  long today; int hour, wday;
  bool clk = clockNow(today, hour, wday);
  if (clk && U.lastDay > 0)                              // missed days go in as "no check-in" so the history stays true
    for (long g = U.lastDay + 1; g < today && g - U.lastDay < 40; g++) {
      hm::DayIn e; for (float& v : e.v) v = NAN; e.breathless = e.orthopnea = e.situps = NAN; U.eng.add(e);
    }
  if (clk) U.lastDay = today;
  hm::Result r = U.eng.add(d);
  memmove(U.lights, U.lights + 1, 6); U.lights[6] = r.light;
  memmove(U.took, U.took + 1, 4); U.took[4] = tookPills < 0 ? 1 : tookPills;
  if (!isnan(d.v[hm::WEIGHT]) && !r.guest) {             // usual weight / leg reading for telling two users apart
    U.w0 = U.w0 <= 0 ? d.v[hm::WEIGHT] : U.w0 + 0.1f * (d.v[hm::WEIGHT] - U.w0);
    if (!isnan(d.v[hm::LEG])) U.z0 = U.z0 <= 0 ? d.v[hm::LEG] : U.z0 + 0.1f * (d.v[hm::LEG] - U.z0);
  }
  char why[100]; hm::Engine::reasons(r, why, sizeof why);
  leds(r.light);
  if (r.light == 2) buzz(1000);
  say(r.light == 2 ? CLIP_RED : r.light == 1 ? CLIP_AMBER : CLIP_GREEN);
  if (r.learning) say(CLIP_LEARNING);
  if (r.light == 2) say(CLIP_PLAN_RED);
  else if (r.light == 1 && U.lights[5] == 1) say(CLIP_PLAN_AMBER);   // amber two days running: the doctor's plan
  const Clip* tip = coachingTip(U, r);
  if (tip) say(*tip);
  if (r.light == 2 && (!loopSt.active || millis() - loopSt.t0 > 20UL * 3600000)) startCareLoop(IDS[u], why[0] ? why : "several signs together", r.danger);
  saveUser(u);
  Serial.printf("{\"t\":\"checkin\",\"id\":\"%s\",\"weight_kg\":%.4f,\"leg_z_ohm\":%.4f,\"trunk_z_ohm\":%.4f,\"pulse_bpm\":%.4f,"
                "\"spo2\":%.4f,\"standup_s\":%.4f,\"night_rr\":%.4f,\"night_situps\":%.4f,\"activity_min\":%.4f,"
                "\"breathless\":%.4f,\"orthopnea\":%.4f,\"took_pills\":%d,\"light\":%d,\"S\":%.4f,\"learning\":%d,\"guest\":%d,\"why\":\"%s\"}\n",
                IDS[u], d.v[hm::WEIGHT], d.v[hm::LEG], d.v[hm::TRUNK], d.v[hm::PULSE], d.v[hm::SPO2], d.v[hm::STANDUP],
                d.v[hm::NIGHT_RR], d.situps, d.v[hm::ACTIVITY], d.breathless, d.orthopnea, U.took[4], r.light, r.S, r.learning, r.guest, why);
}

// ======================= the 90-second check-in =======================
void checkin() {
  hm::DayIn d; for (float& v : d.v) v = NAN; d.breathless = d.orthopnea = d.situps = NAN;
  say(CLIP_WELCOME);
  d.v[hm::WEIGHT] = stableWeight(30000);
  if (isnan(d.v[hm::WEIGHT])) { say(CLIP_RETRY); return; }
  say(CLIP_FEET_HANDS);
  dac_cosine_start(cosine);
  float z[4];
  for (int p = 0; p < 4; p++) z[p] = measurePath(p);
  dac_cosine_stop(cosine);
  if (isnan(z[0])) say(CLIP_REPLACE_FEET);
  int u = whoIsThis(d.v[hm::WEIGHT], z[0]);
  if (u < 0) { say(CLIP_GUEST); return; }                // not a registered user: nothing saved
  d.v[hm::LEG] = z[0];
  d.v[hm::TRUNK] = (isnan(z[0]) || isnan(z[1]) || isnan(z[2]) || isnan(z[3])) ? NAN : (z[2] + z[3] - z[0] - z[1]) / 2;
  say(CLIP_FINGER);
  float bpm, spo2;
  if (pulseSpo2(bpm, spo2)) { d.v[hm::PULSE] = bpm; d.v[hm::SPO2] = spo2; }
  say(CLIP_Q_BREATH); int a = button(20000); d.breathless = a < 0 ? NAN : a;
  say(CLIP_Q_PILLOW); a = button(20000); d.orthopnea = a < 0 ? NAN : a;
  int took = -1;
  if (drawerToday) took = 1;                             // tablet drawer opened today: no need to ask
  else { say(CLIP_Q_TABLETS); a = button(20000); took = a < 0 ? -1 : (a == 1 ? 1 : 0); }
  say(CLIP_STAND);
  uint32_t t0 = millis();
  while (millis() - t0 < 15000) { float w = kg(); if (!isnan(w) && w < 5) { d.v[hm::STANDUP] = (millis() - t0) / 1000.0f; break; } }
  scanAmulet();
  d.v[hm::NIGHT_RR] = amulet.rr; d.situps = amulet.situps; d.v[hm::ACTIVITY] = amulet.activity;
  runEngine(u, d, took);
}

// ======================= background duties: drawer, nudges, self-test, weekly summary =======================
void duties() {
  static uint32_t lastClock = 0; static long nudged = -1, tested = -1, summarised = -1;
  if (!digitalRead(DRAWER)) drawerToday = true;          // drawer switch closes to GND when opened
  if (millis() - lastClock < 600000 && lastClock) return; // check the clock every 10 min
  lastClock = millis();
  long today; int hour, wday;
  if (!clockNow(today, hour, wday)) return;
  if (drawerDay != today) { drawerDay = today; drawerToday = !digitalRead(DRAWER); }
  char msg[160];
  if (hour >= NUDGE_HOUR && nudged != today) {           // same rule as engine/product.py nudge_due()
    for (int u = 0; u < 2; u++) if ((u == 0 || users[u].enrolled) && users[u].lastDay != today) {
      snprintf(msg, sizeof msg, "HridayMitra: no check-in yet today for %s. Please remind them to sit on the stool.", IDS[u]);
      queueSms(FAMILY1, msg);
    }
    nudged = today;
  }
  if (hour >= SELFTEST_HOUR && tested != today) { selfTest(); tested = today; }
  if (wday == 0 && hour >= SUMMARY_HOUR && summarised != today) {   // Sunday summary, same format as weekly_summary()
    for (int u = 0; u < 2; u++) if (u == 0 || users[u].enrolled) {
      char marks[8]; int done = 0;
      for (int k = 0; k < 7; k++) { uint8_t l = users[u].lights[k]; marks[k] = l > 2 ? '-' : "GAR"[l]; done += l <= 2; }
      marks[7] = 0;
      snprintf(msg, sizeof msg, "HridayMitra weekly %s: %d/7 check-ins, lights %s, usual weight %.1f kg. Monitoring, not diagnosis.",
               IDS[u], done, marks, users[u].w0);
      queueSms(ASHA, msg);
    }
    summarised = today;
  }
}

void handleUsb() {                                       // laptop commands
  if (!Serial.available()) return;
  String c = Serial.readStringUntil('\n'); c.trim();
  if (c == "checkin") checkin();
  else if (c == "selftest") selfTest();
  else if (c == "tare") { long s = 0; for (int i = 0; i < 10; i++) s += hxRaw(); tareCounts = s / 10; prefs.putLong("tare", tareCounts); Serial.println("{\"t\":\"ok\"}"); }
  else if (c.startsWith("cal ")) {
    float ref = c.substring(4).toFloat(); long s = 0; for (int i = 0; i < 10; i++) s += hxRaw();
    countsPerKg = (s / 10 - tareCounts) / ref; prefs.putFloat("cpk", countsPerKg); Serial.printf("{\"t\":\"ok\",\"counts_per_kg\":%.1f}\n", countsPerKg);
  } else if (c.startsWith("enroll ")) {                 // the next check-in becomes user 1 or 2
    enrollNext = constrain(c.substring(7).toInt(), 1, 2) - 1; Serial.println("{\"t\":\"ok\",\"enroll\":\"next check-in\"}");
  } else if (c.startsWith("day ")) {                    // feed numbers without sensors (hardware-in-the-loop test)
    hm::DayIn d; float f[11]; int k = 0; char buf[200]; strlcpy(buf, c.c_str() + 4, sizeof buf);
    for (char* tok = strtok(buf, ","); tok && k < 11; tok = strtok(nullptr, ",")) f[k++] = (tok[0] == 'n') ? NAN : atof(tok);
    if (k == 11) { for (int s = 0; s < hm::N_SIG; s++) d.v[s] = f[s]; d.breathless = f[8]; d.orthopnea = f[9]; d.situps = f[10]; runEngine(0, d, -1); }
  } else if (c == "reset") { for (int u = 0; u < 2; u++) { users[u] = User(); saveUser(u); } Serial.println("{\"t\":\"ok\"}"); }
}

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, GSM_RX, GSM_TX);
  for (int p : {LED_G, LED_A, LED_R, SEL, PATH_S0, PATH_S1, HX_SCK, VIBRA}) pinMode(p, OUTPUT);
  for (int p : {BTN_G, BTN_R, BTN_SOS}) pinMode(p, INPUT_PULLUP);
  pinMode(HX_DT, INPUT); pinMode(DRAWER, INPUT);         // GPIO36 has no internal pull-up: 10 k to 3.3 V on the board
  analogReadResolution(12);
  Wire.begin(21, 22); maxInit();
  dac_cosine_config_t cfg = {};
  cfg.chan_id = DAC_CHAN_0; cfg.freq_hz = 5000; cfg.clk_src = DAC_COSINE_CLK_SRC_DEFAULT;
  cfg.atten = DAC_COSINE_ATTEN_DB_6; cfg.phase = DAC_COSINE_PHASE_0; cfg.offset = 0;   // scale 1/2, about 0.83 V peak
  dac_cosine_new_channel(&cfg, &cosine);
  prefs.begin("hm");
  countsPerKg = prefs.getFloat("cpk", DEFAULT_COUNTS_PER_KG); tareCounts = prefs.getLong("tare", 0);
  for (int u = 0; u < 2; u++) {                          // engines and baselines survive power cuts
    char k[4] = {'u', char('0' + u), 0};
    if (prefs.getBytesLength(k) == sizeof(User)) prefs.getBytes(k, &users[u], sizeof(User));
  }
  BLEDevice::init("HridayMitra-stool");
  gsmCmd("AT", "OK", 1000); gsmCmd("AT+CLTS=1", "OK", 1000); gsmCmd("AT+CNMI=2,2,0,0,0", "OK", 1000); gsmCmd("AT+CLIP=1", "OK", 1000);
  leds(-1);
  selfTest();
  Serial.println("{\"t\":\"ready\"}");
}

void loop() {
  static uint32_t lastScan = 0;
  if (millis() - lastScan > 60000) { scanAmulet(); lastScan = millis(); }   // catches an amulet SOS between check-ins
  if (!digitalRead(BTN_G)) { delay(300); checkin(); }
  if (!digitalRead(BTN_SOS) || amulet.sos) {             // SOS: everyone at once
    amulet.sos = false; buzz(500); say(CLIP_SOS);
    char msg[120]; snprintf(msg, sizeof msg, "HridayMitra SOS from %s's home. Please call or visit now. If unresponsive call 108.", PATIENT_ID);
    queueSms(FAMILY1, msg); queueSms(FAMILY2, msg); queueSms(ASHA, msg); delay(1000);
  }
  handleUsb();
  duties();
  serviceGsm();
  serviceSms();
}
