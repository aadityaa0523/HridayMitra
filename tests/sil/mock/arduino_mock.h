// SOFTWARE-IN-THE-LOOP: an emulated world for the real stool firmware, compiled on a laptop.
// Every chip the firmware talks to is emulated at the level the firmware sees it: ADC samples of a body with known
// impedance (5 kHz excitation, 50 Hz hum, noise), HX711 bit-by-bit, MAX30102 registers and FIFO with a real pulse
// waveform, SIM800L AT commands (SMS, replies, clock, battery, signal, outages), buttons, drawer, BLE adverts, flash.
// Time is virtual: every call advances a clock, so a month runs in seconds.
#pragma once
#include <cmath>
#include <climits>
#include <cstdint>
#include <cstdio>
#include <cstdarg>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <map>
#include <random>
#include <algorithm>
#include <functional>
#include <complex>
#include <initializer_list>
using std::min; using std::max;

#define PI 3.14159265358979323846
#define HIGH 1
#define LOW 0
#define INPUT 0
#define OUTPUT 1
#define INPUT_PULLUP 2
#define SERIAL_8N1 0
#define PROGMEM
#define pgm_read_byte(p) (*(const uint8_t*)(p))
template <class T, class L, class H> T constrain(T x, L lo, H hi) { return x < lo ? (T)lo : (x > hi ? (T)hi : x); }
inline size_t strlcpy(char* d, const char* s, size_t n) { size_t l = strlen(s); if (n) { size_t c = l < n - 1 ? l : n - 1; memcpy(d, s, c); d[c] = 0; } return l; }

// ---------------- Arduino String (the subset the firmware uses) ----------------
class String {
 public:
  std::string s;
  String() {}
  String(const char* c) : s(c ? c : "") {}
  String(const std::string& x) : s(x) {}
  String(const char* c, unsigned n) : s(c, n) {}
  explicit String(char c) : s(1, c) {}
  unsigned length() const { return (unsigned)s.size(); }
  const char* c_str() const { return s.c_str(); }
  char operator[](unsigned i) const { return i < s.size() ? s[i] : 0; }
  String& operator+=(const String& o) { s += o.s; return *this; }
  String& operator+=(const char* o) { s += o; return *this; }
  String& operator+=(char c) { s += c; return *this; }
  bool operator==(const char* o) const { return s == o; }
  int indexOf(const char* t, unsigned from = 0) const { auto p = s.find(t, from); return p == std::string::npos ? -1 : (int)p; }
  int indexOf(char c, unsigned from = 0) const { auto p = s.find(c, from); return p == std::string::npos ? -1 : (int)p; }
  int lastIndexOf(char c) const { auto p = s.rfind(c); return p == std::string::npos ? -1 : (int)p; }
  String substring(unsigned a) const { return a >= s.size() ? String() : String(s.substr(a)); }
  String substring(unsigned a, unsigned b) const { return a >= s.size() ? String() : String(s.substr(a, b > a ? b - a : 0)); }
  long toInt() const { return atol(s.c_str()); }
  float toFloat() const { return (float)atof(s.c_str()); }
  bool startsWith(const char* p) const { return s.rfind(p, 0) == 0; }
  bool endsWith(const String& e) const { return s.size() >= e.s.size() && s.compare(s.size() - e.s.size(), e.s.size(), e.s) == 0; }
  void trim() { auto a = s.find_first_not_of(" \t\r\n"); auto b = s.find_last_not_of(" \t\r\n"); s = a == std::string::npos ? "" : s.substr(a, b - a + 1); }
};

// ---------------- the world ----------------
struct SentSms { uint64_t at_us; std::string to, text; };
struct World {
  uint64_t us = 0;                       // virtual time since day 0, 00:00
  long day0 = 0;                         // days since 1970 of day 0
  std::mt19937 rng{7};
  // body and sensors
  double weight = 0; bool plateOpen = false;
  double seg[3][3] = {{289.25, 650, 3.39e-9}, {330, 750, 2.9e-9}, {28, 60, 30e-9}};   // leg, arm, trunk: Re, Ri, Cm
  double excHz = 5000, refScale = 1.0;                      // refScale != 1: a damaged reference chain
  double bpm = 70, spo2 = 96; bool finger = true;
  double hum_mv = 20;
  uint64_t standAt = 0; bool sitting = false;
  // buttons and drawer
  std::vector<int> answers; size_t nextAnswer = 0; bool questionOpen = false; uint64_t questionAt = 0, lastRPoll = 0;
  bool pressStart = false, pressSos = false, drawerOpen = false;
  // amulet advert: rr*10, situps, activity/4, sos
  bool amuletNear = true; double rr = 16, situps = 0, activity = 200; bool amuletSos = false;
  // modem
  int batteryMv = 3950, signal = 18; bool networkDown = false;
  std::vector<SentSms> sms; std::string toModem, fromModem; std::vector<std::pair<uint64_t, std::string>> inbox;
  // pins
  int pin[40] = {0}; int hxBits = 0; long hxValue = 0; bool dacOn = false;
  std::vector<std::string> usbOut; std::string usbLine; std::vector<std::string> usbIn;
  std::function<void(const std::string&)> onUsbLine;
} W;

inline uint32_t millis() { W.us += 50; return (uint32_t)(W.us / 1000); }
inline uint32_t micros() { W.us += 1; return (uint32_t)W.us; }
inline void delay(uint32_t ms) { W.us += (uint64_t)ms * 1000; }
inline void delayMicroseconds(uint32_t u) { W.us += u; }
inline double now_s() { return W.us / 1e6; }
inline double gauss(double sd) { std::normal_distribution<double> n(0, sd); return n(W.rng); }

// ---------------- GPIO: buttons, drawer, HX711 ----------------
const int P_HX_DT = 32, P_HX_SCK = 14, P_SEL = 18, P_S0 = 33, P_S1 = 27, P_BTN_G = 4, P_BTN_R = 5, P_SOS = 15, P_DRAWER = 36;
inline void pinMode(int, int) {}
inline int scaleCounts() {
  double kg = (W.sitting && (W.standAt == 0 || W.us < W.standAt)) ? W.weight : 0.0;
  return (int)lround(kg * 21000.0 + gauss(800));          // DEFAULT_COUNTS_PER_KG, about 0.04 kg noise
}
inline void digitalWrite(int p, int v) {
  if (p == P_HX_SCK && v && !W.pin[p]) {                  // HX711: each rising clock shifts the next bit out
    if (W.hxBits == 0) W.hxValue = scaleCounts() & 0xFFFFFF;
    W.hxBits++;
    W.pin[P_HX_DT] = W.hxBits <= 24 ? (W.hxValue >> (24 - W.hxBits)) & 1 : 1;
    if (W.hxBits == 25) W.hxBits = 0;
  }
  W.pin[p] = v;
}
inline int digitalRead(int p) {
  if (p == P_HX_DT) return W.hxBits == 0 ? 0 : W.pin[P_HX_DT];   // always ready between words
  if (p == P_BTN_R || p == P_BTN_G) {                      // the patient answers a question 1 s after it is asked
    if (p == P_BTN_R) {
      if (!W.questionOpen && W.us - W.lastRPoll > 200000 && W.nextAnswer < W.answers.size()) { W.questionOpen = true; W.questionAt = W.us; }
      W.lastRPoll = W.us;
    }
    if (W.questionOpen && W.us - W.questionAt > 1000000) {
      int a = W.answers[W.nextAnswer];
      if ((p == P_BTN_R && a == 1) || (p == P_BTN_G && a == 0)) {
        W.questionOpen = false; W.nextAnswer++;
        if (W.nextAnswer == W.answers.size()) W.standAt = W.us + 6000000;   // stands up 6 s later (after the prompt)
        return 0;
      }
      if (a < 0) { W.questionOpen = false; W.nextAnswer++; }
    }
    if (p == P_BTN_G && W.pressStart) { W.pressStart = false; return 0; }
    return 1;
  }
  if (p == P_SOS) { if (W.pressSos) { W.pressSos = false; return 0; } return 1; }
  if (p == P_DRAWER) return W.drawerOpen ? 0 : 1;
  return W.pin[p];
}

// ---------------- ADC: the impedance front end ----------------
inline std::complex<double> segZ(int k, double f) {       // one Cole segment Re || (Ri + Cm)
  std::complex<double> zc(0, -1 / (2 * PI * f * W.seg[k][2]));
  return W.seg[k][0] * (W.seg[k][1] + zc) / (W.seg[k][0] + W.seg[k][1] + zc);
}
inline double zPath(int path, double f) {                  // legs, arms, right side, left side
  std::complex<double> L = segZ(0, f), A = segZ(1, f), T = segZ(2, f);
  return std::abs(path == 0 ? 2. * L : path == 1 ? 2. * A : A + T + L);
}
inline void analogReadResolution(int) {}
inline int analogRead(int) {
  W.us += 4;                                               // about 5 us per sample: the stool streams the ADC by DMA at 200 kS/s
  double t = now_s(), v = 1.65 + W.hum_mv / 1000 * 10 * sin(2 * PI * 50 * t);
  int path = W.pin[P_S0] | (W.pin[P_S1] << 1);
  if (W.dacOn) {
    double z = W.pin[P_SEL] ? (W.pin[12] ? 100.0 : 220.0 * W.refScale) : zPath(path, W.excHz);   // Rcal or R5 + Rcal
    v += 10 * 100e-6 * z * cos(2 * PI * W.excHz * t);         // 100 uA through the body, INA gain 10
    if (!W.pin[P_SEL] && W.plateOpen && path == 0) v = 1.65 + 3.0 * sin(2 * PI * 50 * t);   // floating input saturates
  }
  return (int)constrain(lround(v / 3.3 * 4095 + gauss(2)), 0L, 4095L);
}
inline void dacWrite(int, int) {}

// ---------------- DAC cosine generator ----------------
typedef struct dac_cos* dac_cosine_handle_t;
enum { DAC_CHAN_0 = 0, DAC_COSINE_CLK_SRC_DEFAULT = 0, DAC_COSINE_ATTEN_DB_6 = 1, DAC_COSINE_PHASE_0 = 0 };
struct dac_cosine_config_t { int chan_id, freq_hz, clk_src, atten, phase, offset; };
inline int dac_cosine_new_channel(const dac_cosine_config_t* c, dac_cosine_handle_t* h) { W.excHz = c->freq_hz; *h = (dac_cosine_handle_t)1; return 0; }
inline int dac_cosine_del_channel(dac_cosine_handle_t) { return 0; }
inline int dac_cosine_start(dac_cosine_handle_t) { W.dacOn = true; return 0; }
inline int dac_cosine_stop(dac_cosine_handle_t) { W.dacOn = false; return 0; }

// ---------------- I2C: MAX30102 ----------------
class TwoWire {
  uint8_t reg = 0; std::vector<uint8_t> rx; size_t rp = 0; bool writing = false; int nw = 0;
  uint64_t lastSampleUs = 0; int rdPtr = 0;
  int pending() { return (int)std::min<uint64_t>(31, (W.us - lastSampleUs) / 10000); }   // 100 samples/s
 public:
  void begin(int, int) {}
  void beginTransmission(uint8_t) { writing = true; nw = 0; }
  size_t write(uint8_t b) { if (nw++ == 0) reg = b; else if (reg == 0x09 && b == 0x03) lastSampleUs = W.us; return 1; }
  uint8_t endTransmission(bool = true) { writing = false; return 0; }
  uint8_t requestFrom(int, int n) {
    rx.clear(); rp = 0;
    for (int k = 0; k < n; k++) {
      if (reg == 0xFF) rx.push_back(0x15);
      else if (reg == 0x06) rx.push_back(rdPtr & 31);
      else if (reg == 0x04) rx.push_back((rdPtr + pending()) & 31);
      else if (reg == 0x07 && k % 6 == 0) {                // one FIFO sample: red then IR, 18-bit
        double t = lastSampleUs / 1e6, f = W.bpm / 60, beat = sin(2 * PI * f * t) + 0.3 * sin(4 * PI * f * t);
        double r = (110 - W.spo2) / 25, ir = W.finger ? 100000 * (1 + 0.01 * beat) + gauss(30) : 500;
        double red = W.finger ? 80000 * (1 + 0.01 * r * beat) + gauss(30) : 400;
        uint32_t R = (uint32_t)red, I = (uint32_t)ir;
        uint8_t b[6] = {uint8_t(R >> 16), uint8_t(R >> 8), uint8_t(R), uint8_t(I >> 16), uint8_t(I >> 8), uint8_t(I)};
        rx.insert(rx.end(), b, b + 6);
        lastSampleUs += 10000; rdPtr++;
      }
      else if (reg != 0x07) rx.push_back(0);
    }
    return (uint8_t)n;
  }
  int read() { return rp < rx.size() ? rx[rp++] : 0; }
} Wire;

// ---------------- flash ----------------
class Preferences {
 public:
  std::map<std::string, std::vector<uint8_t>> kv;
  bool begin(const char*) { return true; }
  template <class T> T get(const char* k, T d) { auto it = kv.find(k); if (it == kv.end()) return d; T v; memcpy(&v, it->second.data(), sizeof v); return v; }
  template <class T> void put(const char* k, T v) { kv[k] = std::vector<uint8_t>((uint8_t*)&v, (uint8_t*)&v + sizeof v); }
  float getFloat(const char* k, float d) { return get(k, d); } void putFloat(const char* k, float v) { put(k, v); }
  long getLong(const char* k, long d) { return get(k, d); } void putLong(const char* k, long v) { put(k, v); }
  int getInt(const char* k, int d) { return get(k, d); } void putInt(const char* k, int v) { put(k, v); }
  size_t getBytesLength(const char* k) { auto it = kv.find(k); return it == kv.end() ? 0 : it->second.size(); }
  size_t getBytes(const char* k, void* b, size_t n) { auto& v = kv[k]; memcpy(b, v.data(), std::min(n, v.size())); return n; }
  size_t putBytes(const char* k, const void* b, size_t n) { kv[k] = std::vector<uint8_t>((const uint8_t*)b, (const uint8_t*)b + n); return n; }
};
std::map<std::string, std::vector<uint8_t>> FLASH;          // survives a simulated power cut

// ---------------- BLE: the amulet advert ----------------
struct BLEAdvertisedDevice {
  std::string md;
  bool haveManufacturerData() { return !md.empty(); }
  String getManufacturerData() { return String(md.data(), (unsigned)md.size()); }
};
struct BLEScanResults {
  std::vector<BLEAdvertisedDevice> d;
  int getCount() { return (int)d.size(); }
  BLEAdvertisedDevice getDevice(int i) { return d[i]; }
};
struct BLEScan {
  BLEScanResults r;
  void setActiveScan(bool) {}
  BLEScanResults* start(int sec, bool) {
    delay(sec * 1000); r.d.clear();
    if (W.amuletNear) {
      uint16_t rr10 = (uint16_t)lround(W.rr * 10);
      uint8_t b[9] = {0xFF, 0xFF, 'H', 'M', uint8_t(rr10 & 0xFF), uint8_t(rr10 >> 8), uint8_t(W.situps), uint8_t(W.activity / 4), uint8_t(W.amuletSos)};
      r.d.push_back({std::string((char*)b, 9)});
    }
    return &r;
  }
  void clearResults() {}
};
struct BLEDevice {
  static void init(const char*) {}
  static BLEScan* getScan() { static BLEScan s; return &s; }
};

// ---------------- clock helpers for the modem ----------------
inline void civil(long z, int& y, int& m, int& d) {         // days since 1970 -> date (Howard Hinnant)
  z += 719468; long era = (z >= 0 ? z : z - 146096) / 146097; unsigned doe = (unsigned)(z - era * 146097);
  unsigned yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365; y = (int)(yoe + era * 400);
  unsigned doy = doe - (365 * yoe + yoe / 4 - yoe / 100), mp = (5 * doy + 2) / 153;
  d = (int)(doy - (153 * mp + 2) / 5 + 1); m = (int)(mp < 10 ? mp + 3 : mp - 9); y += m <= 2;
}

// ---------------- serial ports: USB (to the laptop) and UART2 (SIM800L) ----------------
class HardwareSerial {
  bool modem;
  std::string cmd; bool inCmgs = false; std::string cmgsTo, cmgsText;
  void modemSays(const std::string& s) { W.fromModem += s; }
  void modemLine(const std::string& l) {
    if (l.rfind("AT+CMGS=", 0) == 0) { inCmgs = true; cmgsTo = l.substr(9, l.find('"', 9) - 9); cmgsText.clear(); modemSays("\r\n> "); return; }
    if (l == "AT+CCLK?") {
      int y, m, d; civil(W.day0 + (long)(W.us / 86400000000ULL), y, m, d);
      uint64_t sod = (W.us / 1000000) % 86400; char b[64];
      snprintf(b, sizeof b, "\r\n+CCLK: \"%02d/%02d/%02d,%02d:%02d:%02d+22\"\r\n\r\nOK\r\n", y % 100, m, d, int(sod / 3600), int(sod / 60 % 60), int(sod % 60));
      modemSays(b); return;
    }
    if (l == "AT+CBC") { modemSays("\r\n+CBC: 0,80," + std::to_string(W.batteryMv) + "\r\n\r\nOK\r\n"); return; }
    if (l == "AT+CSQ") { modemSays("\r\n+CSQ: " + std::to_string(W.signal) + ",0\r\n\r\nOK\r\n"); return; }
    if (!l.empty()) modemSays("\r\nOK\r\n");
  }
 public:
  explicit HardwareSerial(bool m) : modem(m) {}
  void begin(long, int = 0, int = 0, int = 0) {}
  void raw(const std::string& s) {
    if (!modem) {
      for (char c : s) { if (c == '\n') { if (W.onUsbLine) W.onUsbLine(W.usbLine); W.usbOut.push_back(W.usbLine); W.usbLine.clear(); } else if (c != '\r') W.usbLine += c; }
      return;
    }
    for (char c : s) {
      if (inCmgs) {
        if (c == 26) {                                    // Ctrl+Z: send
          inCmgs = false;
          if (W.networkDown) modemSays("\r\n+CMS ERROR: 500\r\n");
          else { W.sms.push_back({W.us, cmgsTo, cmgsText}); modemSays("\r\n+CMGS: 1\r\n\r\nOK\r\n"); }
        } else cmgsText += c;
        continue;
      }
      if (c == '\r' || c == '\n') { if (!cmd.empty()) modemLine(cmd); cmd.clear(); } else cmd += c;
    }
  }
  void print(const char* s) { raw(s); }
  void print(const String& s) { raw(s.s); }
  void println(const char* s = "") { raw(std::string(s) + "\r\n"); }
  void println(const String& s) { raw(s.s + "\r\n"); }
  size_t write(uint8_t b) { raw(std::string(1, (char)b)); return 1; }
  int printf(const char* f, ...) { char b[1024]; va_list a; va_start(a, f); int n = vsnprintf(b, sizeof b, f, a); va_end(a); raw(b); return n; }
  int available() {
    if (!modem) return (int)!W.usbIn.empty();
    for (auto it = W.inbox.begin(); it != W.inbox.end();)  // incoming SMS / calls arrive at their time
      if (it->first <= W.us) { W.fromModem += it->second; it = W.inbox.erase(it); } else ++it;
    return (int)W.fromModem.size();
  }
  int read() { if (W.fromModem.empty()) return -1; char c = W.fromModem[0]; W.fromModem.erase(0, 1); W.us += 1000; return (uint8_t)c; }
  String readStringUntil(char) { String s = W.usbIn.front(); W.usbIn.erase(W.usbIn.begin()); return s; }
};
HardwareSerial Serial(false), Serial2(true);
