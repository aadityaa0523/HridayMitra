// Software-in-the-loop run of the REAL stool firmware (firmware/hridaymitra_stool/*.ino, unchanged) through a scripted
// month in the emulated world of mock/arduino_mock.h. Prints PASS/FAIL per claim and writes every check-in report to
// reports/sil_checkins.jsonl so tests/test_firmware_sil.py can also compare the stool's lights with the Python engine.
#include "mock/arduino_mock.h"
#include "../../firmware/hridaymitra_stool/hridaymitra_stool.ino"

static const uint64_t S = 1000000ULL, MIN_ = 60 * S, H = 3600 * S, DAY = 86400 * S;
static int fails = 0;
static std::vector<std::pair<int, std::string>> checkins;   // (day, JSON line)
static int curDay = 0;
static FILE* logFile;

void check(bool ok, const std::string& what) { printf("%s  %s\n", ok ? "PASS" : "FAIL", what.c_str()); fprintf(logFile, "%s  %s\n", ok ? "PASS" : "FAIL", what.c_str()); fails += !ok; }
double jnum(const std::string& j, const char* k) {
  auto p = j.find(std::string("\"") + k + "\":"); if (p == std::string::npos) return NAN;
  const char* s = j.c_str() + p + strlen(k) + 3; return (strncmp(s, "nan", 3) == 0 || strncmp(s, "-nan", 4) == 0) ? NAN : atof(s);
}
std::string jstr(const std::string& j, const char* k) {
  auto p = j.find(std::string("\"") + k + "\":\""); if (p == std::string::npos) return "";
  auto a = p + strlen(k) + 4; return j.substr(a, j.find('"', a) - a);
}
void runUntil(uint64_t t) { while (W.us < t) { loop(); W.us += S; } }      // idle steps of 1 s between loop passes
std::vector<SentSms> smsTo(const char* who, uint64_t from, uint64_t to, const char* contains = "") {
  std::vector<SentSms> r;
  for (auto& m : W.sms) if (m.to == who && m.at_us >= from && m.at_us < to && m.text.find(contains) != std::string::npos) r.push_back(m);
  return r;
}

struct Body { double L = 289.25, A = 329.2, Tr = 27.95; };   // one leg, one arm, trunk (5 kHz |Z|, LTspice body model)
void setBody(const Body& b) { W.z[0] = 2 * b.L; W.z[1] = 2 * b.A; W.z[2] = W.z[3] = b.A + b.Tr + b.L; }

std::string doCheckin(double kg, const Body& b, std::vector<int> answers, double extraStand = 0) {
  setBody(b); W.weight = kg; W.sitting = true; W.standAt = 0;
  W.answers = answers; W.nextAnswer = 0; W.questionOpen = false;
  size_t before = W.usbOut.size();
  W.pressStart = true; loop();
  if (extraStand > 0) {}                                    // stand-up delay is set when the last answer is given
  W.sitting = false;
  for (size_t i = before; i < W.usbOut.size(); i++)
    if (W.usbOut[i].find("\"checkin\"") != std::string::npos) { checkins.push_back({curDay, W.usbOut[i]}); return W.usbOut[i]; }
  return "";
}

int main() {
  logFile = fopen("../../reports/sil_run.log", "w");
  W.day0 = 20727;                                           // 2026-10-01 (a Thursday): days since 1970
  W.us = 7 * H;
  setup();
  W.usbIn.clear();
  std::mt19937 r(3); std::normal_distribution<double> n(0, 1);
  double maxLegErr = 0, maxTrunkErr = 0, maxPulseErr = 0, maxSpo2Err = 0, maxWErr = 0; int firstRed = -1; uint64_t redAt = 0;

  for (curDay = 0; curDay <= 22; curDay++) {               // 14 stable days, then 8 days of worsening, then 1 more
    runUntil(curDay * DAY + 8 * H);
    int k = curDay >= 14 ? curDay - 13 : 0;
    Body b; b.L *= (1 + 0.004 * n(r)) * (1 - 0.013 * k); b.A *= 1 + 0.004 * n(r); b.Tr *= (1 + 0.01 * n(r)) * (1 - 0.015 * k);
    double kg = 62 + 0.25 * n(r) + 0.45 * k;
    W.bpm = 70 + 1.2 * n(r) + 1.2 * k; W.spo2 = 96.5 + 0.3 * n(r) - 0.15 * k;
    W.rr = 16 + 0.4 * n(r) + 0.35 * k; W.situps = std::round(0.4 * k); W.activity = 200 * (1 - 0.03 * k) + 6 * n(r);
    W.drawerOpen = true;                                   // tablets taken: the tablet question is skipped
    uint64_t startedAt = W.us;
    std::string j = doCheckin(kg, b, {k >= 4 ? 1 : 0, k >= 5 ? 1 : 0});
    if (j.empty()) { check(false, "check-in report on day " + std::to_string(curDay)); continue; }
    maxWErr = std::max(maxWErr, fabs(jnum(j, "weight_kg") - kg));
    maxLegErr = std::max(maxLegErr, fabs(jnum(j, "leg_z_ohm") / (2 * b.L) - 1));
    maxTrunkErr = std::max(maxTrunkErr, fabs(jnum(j, "trunk_z_ohm") - b.Tr));
    maxPulseErr = std::max(maxPulseErr, fabs(jnum(j, "pulse_bpm") - W.bpm));
    maxSpo2Err = std::max(maxSpo2Err, fabs(jnum(j, "spo2") - W.spo2));
    if (jnum(j, "light") == 2 && firstRed < 0) { firstRed = curDay; redAt = startedAt; }
    if (firstRed == curDay) {                               // the care loop: nobody answers, then the ASHA replies at 2.5 h
      W.inbox.push_back({redAt + 150 * MIN_, "\r\n+CMT: \"" + std::string(ASHA) + "\",,\"26/10/16,10:30:00+22\"\r\n1\r\n"});
    }
  }
  printf("first red on day %d (worsening started day 14)\n", firstRed);
  check(firstRed >= 15 && firstRed <= 21, "red alert comes during the worsening, not before it");
  check(smsTo(FAMILY1, 0, 14 * DAY).empty() && smsTo(ASHA, 0, 14 * DAY, "RED").empty(), "no alert SMS during the 14 stable days");
  check(maxWErr < 0.15, "weight within 0.15 kg (worst " + std::to_string(maxWErr) + ")");
  check(maxLegErr < 0.01, "leg impedance within 1 % through ADC + Goertzel (worst " + std::to_string(100 * maxLegErr) + " %)");
  check(maxTrunkErr < 1.5, "chest value within 1.5 ohm from 4 paths (worst " + std::to_string(maxTrunkErr) + ")");
  check(maxPulseErr < 2.5, "pulse within 2.5 bpm from the PPG waveform (worst " + std::to_string(maxPulseErr) + ")");
  check(maxSpo2Err < 2.0, "SpO2 within 2 points (worst " + std::to_string(maxSpo2Err) + ")");
  check(!smsTo(FAMILY1, redAt, redAt + 5 * MIN_, "Why:").empty(), "red: family 1 gets an SMS with the reasons");
  check(!smsTo(FAMILY1, redAt, redAt + 5 * MIN_, "doctor's plan").empty(), "red: family 1 also gets the doctor's plan");
  check(!smsTo(FAMILY2, redAt + 29 * MIN_, redAt + 45 * MIN_).empty(), "no reply: family 2 messaged at 30 min");
  check(!smsTo(ASHA, redAt + 119 * MIN_, redAt + 135 * MIN_, "please visit").empty(), "still no reply: ASHA messaged at 2 h");
  check(smsTo(DOCTOR, redAt, redAt + 12 * H).empty(), "ASHA replied 1: the doctor is not disturbed");
  check(W.pin[LED_R] == 1, "red LED on");

  // day 23: nobody checks in -> family reminder at 11:00
  curDay = 23; runUntil(23 * DAY + 12 * H);
  check(!smsTo(FAMILY1, 23 * DAY + 11 * H, 23 * DAY + 12 * H, "no check-in yet").empty(), "missed check-in: family reminded at 11:00");
  // day 24 (Sunday): recovered values; weekly summary to the ASHA at 18:00
  curDay = 24; runUntil(24 * DAY + 8 * H);
  W.bpm = 70; W.spo2 = 96.5; W.rr = 16; W.situps = 0; W.activity = 200;
  doCheckin(62, Body(), {0, 0});
  runUntil(24 * DAY + 19 * H);
  check(!smsTo(ASHA, 24 * DAY + 18 * H, 24 * DAY + 19 * H, "weekly").empty(), "Sunday 18:00: weekly summary to the ASHA");
  // day 25: a guest sits down in the afternoon
  curDay = 25; runUntil(25 * DAY + 8 * H); doCheckin(62.1, Body(), {0, 0});
  runUntil(25 * DAY + 15 * H);
  std::string g = doCheckin(85, Body(), {0, 0});
  check(jnum(g, "guest") == 1, "guest (85 kg) recognised: readings ignored by the engine");
  // day 26: a foot lifted off a plate -> "no reading" for the legs, not a wrong number
  curDay = 26; runUntil(26 * DAY + 8 * H); W.plateOpen = true;
  std::string o = doCheckin(62, Body(), {0, 0}); W.plateOpen = false;
  check(std::isnan(jnum(o, "leg_z_ohm")) && std::isnan(jnum(o, "trunk_z_ohm")), "lifted foot: leg and chest reported as no reading");
  // day 27: low battery found by the 07:00 self-test; SOS at 10:00
  curDay = 27; W.batteryMv = 3300; runUntil(27 * DAY + 7 * H + 30 * MIN_);
  check(!smsTo(ASHA, 27 * DAY + 7 * H, 27 * DAY + 8 * H, "battery low").empty(), "self-test: low battery -> service SMS to the ASHA");
  W.batteryMv = 3950; runUntil(27 * DAY + 8 * H); doCheckin(62, Body(), {0, 0});
  runUntil(27 * DAY + 10 * H); W.pressSos = true; runUntil(27 * DAY + 10 * H + 10 * MIN_);
  int sos = (int)(smsTo(FAMILY1, 27 * DAY + 10 * H, 27 * DAY + 11 * H, "SOS").size() + smsTo(FAMILY2, 27 * DAY + 10 * H, 27 * DAY + 11 * H, "SOS").size()
                  + smsTo(ASHA, 27 * DAY + 10 * H, 27 * DAY + 11 * H, "SOS").size());
  check(sos == 3, "SOS button: family 1, family 2 and ASHA messaged");
  // day 28: power cut -> the engine's memory comes back from flash
  curDay = 28; runUntil(28 * DAY + 7 * H + 30 * MIN_);
  std::vector<uint8_t> before((uint8_t*)&users[0], (uint8_t*)&users[0] + sizeof(User));
  FLASH = prefs.kv; users[0] = User(); users[1] = User(); loopSt = Loop(); for (auto& m : q) m.used = false;
  prefs.kv = FLASH; setup();
  check(memcmp(before.data(), &users[0], sizeof(User)) == 0, "power cut: personal baseline and alert state restored from flash");
  runUntil(28 * DAY + 8 * H); check(!doCheckin(62, Body(), {0, 0}).empty(), "check-in works after the power cut");
  // day 29: network down 07:55-08:45, SOS at 08:00 -> messages wait and go out when the network returns
  curDay = 29; runUntil(29 * DAY + 7 * H + 55 * MIN_); W.networkDown = true;
  runUntil(29 * DAY + 8 * H); W.pressSos = true; runUntil(29 * DAY + 8 * H + 45 * MIN_);
  check(smsTo(FAMILY1, 29 * DAY + 8 * H, 29 * DAY + 8 * H + 45 * MIN_, "SOS").empty(), "network down: nothing is lost, messages wait");
  W.networkDown = false; runUntil(29 * DAY + 9 * H + 30 * MIN_);
  check(smsTo(FAMILY1, 29 * DAY + 8 * H + 45 * MIN_, 29 * DAY + 10 * H, "SOS").size() == 1 &&
        smsTo(ASHA, 29 * DAY + 8 * H + 45 * MIN_, 29 * DAY + 10 * H, "SOS").size() == 1, "network back: queued SOS delivered within 10 min retry");
  doCheckin(62, Body(), {0, 0});
  // day 30: a second person is enrolled; the stool tells them apart and ignores a stranger
  curDay = 30; runUntil(30 * DAY + 8 * H);
  W.usbIn.push_back("enroll 2"); loop();
  Body b2; b2.L = 360; b2.A = 380; b2.Tr = 30;
  W.bpm = 76; std::string p2 = doCheckin(48, b2, {0, 0});
  check(jstr(p2, "id") == PATIENT_ID2, "second user enrolled and recognised");
  W.bpm = 70; std::string p1 = doCheckin(62, Body(), {0, 0});
  check(jstr(p1, "id") == PATIENT_ID, "first user still recognised");
  size_t nBefore = checkins.size(); doCheckin(85, Body(), {0, 0});
  check(checkins.size() == nBefore, "stranger on a two-user stool: nothing saved");

  FILE* f = fopen("../../reports/sil_checkins.jsonl", "w");
  for (auto& c : checkins) fprintf(f, "{\"day\":%d,\"report\":%s}\n", c.first, c.second.c_str());
  fclose(f);
  printf("%zu check-ins, %zu SMS sent, %d failures\n", checkins.size(), W.sms.size(), fails);
  fprintf(logFile, "%zu check-ins, %zu SMS sent, %d failures\n", checkins.size(), W.sms.size(), fails);
  for (auto& m : W.sms) fprintf(logFile, "SMS day %llu %02llu:%02llu to %s: %s\n", (unsigned long long)(m.at_us / DAY),
                                (unsigned long long)(m.at_us % DAY / H), (unsigned long long)(m.at_us % H / MIN_), m.to.c_str(), m.text.c_str());
  fclose(logFile);
  return fails;
}
