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

struct Body {                                             // Cole segments Re || (Ri + Cm), the LTspice body model
  double legRe = 289.25, legRi = 650, legCm = 3.39e-9, armRe = 330, armRi = 750, armCm = 2.9e-9, trRe = 28, trRi = 60, trCm = 30e-9;
  double ewi() const { return legRi / (legRe + legRi); }   // true extracellular-water index Rinf/R0
};
void setBody(const Body& b) {
  double v[3][3] = {{b.legRe, b.legRi, b.legCm}, {b.armRe, b.armRi, b.armCm}, {b.trRe, b.trRi, b.trCm}};
  memcpy(W.seg, v, sizeof v);
}
double legTrue(const Body& b) { setBody(b); return zPath(0, 5000); }
double trunkTrue(const Body& b) { setBody(b); return std::abs(segZ(2, 5000)); }

std::string doCheckin(double kg, const Body& b, std::vector<int> answers, double extraStand = 0) {
  setBody(b); W.weight = kg; W.sitting = true; W.standAt = 0; W.answersDone = false;
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
  double maxEwiErr = 0, ewiStable = NAN, ewiWorse = NAN;
  double maxLegErr = 0, maxTrunkErr = 0, maxPulseErr = 0, maxSpo2Err = 0, maxWErr = 0; int firstRed = -1; uint64_t redAt = 0;

  for (curDay = 0; curDay <= 22; curDay++) {               // 14 stable days, then 8 days of worsening, then 1 more
    runUntil(curDay * DAY + 8 * H);
    int k = curDay >= 14 ? curDay - 13 : 0;
    Body b; double gl = 1 + 0.004 * n(r), ga = 1 + 0.004 * n(r);          // day-to-day position / limb geometry
    b.legRe = b.legRe * gl / (1 + 0.015 * k); b.legRi *= gl; b.legCm /= gl;   // worsening: fluid outside the cells rises
    b.armRe *= ga; b.armRi *= ga; b.armCm /= ga; b.trRe = b.trRe * (1 + 0.01 * n(r)) / (1 + 0.015 * k);
    double kg = 62 + 0.25 * n(r) + 0.45 * k;
    W.bpm = 70 + 1.2 * n(r) + 1.2 * k; W.spo2 = 96.5 + 0.3 * n(r) - 0.15 * k;
    W.rr = 16 + 0.4 * n(r) + 0.35 * k; W.situps = std::round(0.4 * k); W.activity = 200 * (1 - 0.03 * k) + 6 * n(r);
    W.drawerOpen = true;                                   // tablets taken: the tablet question is skipped
    uint64_t startedAt = W.us;
    std::string j = doCheckin(kg, b, {k >= 4 ? 1 : 0, k >= 5 ? 1 : 0});
    if (j.empty()) { check(false, "check-in report on day " + std::to_string(curDay)); continue; }
    maxWErr = std::max(maxWErr, fabs(jnum(j, "weight_kg") - kg));
    maxLegErr = std::max(maxLegErr, fabs(jnum(j, "leg_z_ohm") / legTrue(b) - 1));
    maxTrunkErr = std::max(maxTrunkErr, fabs(jnum(j, "trunk_z_ohm") - trunkTrue(b)));
    maxEwiErr = std::max(maxEwiErr, fabs(jnum(j, "leg_ewi") / b.ewi() - 1));
    if (curDay == 13) ewiStable = jnum(j, "leg_ewi");
    if (curDay == 21) ewiWorse = jnum(j, "leg_ewi");
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
  check(maxEwiErr < 0.006, "spectroscopy (5/20/50 kHz): water-outside-cells index within 0.6 % (worst " + std::to_string(100 * maxEwiErr) + " %)");
  check(ewiWorse > ewiStable * 1.03, "spectroscopy index rises with the fluid build-up (" + std::to_string(ewiStable) + " -> " + std::to_string(ewiWorse) + ")");
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
  runUntil(24 * DAY + 10 * H); W.walk6 = 540;                // the Sunday walk test after the check-in: amulet reports 540 steps
  runUntil(24 * DAY + 19 * H);
  check(!smsTo(ASHA, 24 * DAY + 18 * H, 24 * DAY + 19 * H, "weekly").empty(), "Sunday 18:00: weekly summary to the ASHA");
  check(!smsTo(ASHA, 24 * DAY + 18 * H, 24 * DAY + 19 * H, "6-min walk 540 steps ~270 m").empty(), "6-minute walk test in the weekly summary (540 steps, ~270 m)");
  W.walk6 = 0;
  // day 25: a guest sits down in the afternoon
  curDay = 25; runUntil(25 * DAY + 7 * H); W.pin[39] = 1;   // CHARGE/USE switch left on CHARGE
  int starts = W.dacStarts;
  check(doCheckin(62.1, Body(), {0, 0}).empty() && W.dacStarts == starts, "switch on CHARGE: check-in refused, no current through the body");
  W.pin[39] = 0; runUntil(25 * DAY + 8 * H); doCheckin(62.1, Body(), {0, 0});
  runUntil(25 * DAY + 15 * H);
  std::string g = doCheckin(85, Body(), {0, 0});
  check(jnum(g, "guest") == 1, "guest (85 kg) recognised: readings ignored by the engine");
  // day 26: a foot lifted off a plate -> "no reading" for the legs, not a wrong number
  curDay = 26; runUntil(26 * DAY + 8 * H); W.openFoot = 1;   // left foot stays lifted through the retry
  std::string o = doCheckin(62, Body(), {0, 0}); W.openFoot = 0;
  check(std::isnan(jnum(o, "leg_z_ohm")) && std::isnan(jnum(o, "trunk_z_ohm")), "lifted foot: leg and chest reported as no reading");
  float zl[4] = {NAN, 600, 640, NAN}, zr[4] = {NAN, 600, NAN, 640}, zok[4] = {580, 600, 640, 640};
  check(hm::liftedFoot(zl) == 1 && hm::liftedFoot(zr) == 2 && hm::liftedFoot(zok) == 0, "lifted foot named from the failed paths (left / right)");
  runUntil(26 * DAY + 14 * H); W.openFoot = 2; W.openFor = 5000000;   // right foot lifted, put back after the voice prompt
  std::string back = doCheckin(62, Body(), {0, 0}); W.openFoot = 0; W.openFor = 0;
  check(!std::isnan(jnum(back, "leg_z_ohm")) && fabs(jnum(back, "leg_z_ohm") / legTrue(Body()) - 1) < 0.02,
        "foot put back after the prompt: re-measured, leg reading recovered (" + std::to_string(jnum(back, "leg_z_ohm")) + " ohm)");
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
  // day 29 afternoon: the reference resistor chain is damaged (solder joint) -> readings rejected, service SMS
  runUntil(29 * DAY + 15 * H); W.refScale = 1.25;
  std::string bad = doCheckin(62, Body(), {0, 0}); W.refScale = 1.0;
  check(std::isnan(jnum(bad, "leg_z_ohm")) && jnum(bad, "ref_ratio") > 2.6, "self-calibration: damaged reference detected, no numbers reported (ratio " + std::to_string(jnum(bad, "ref_ratio")) + ")");
  runUntil(29 * DAY + 16 * H);
  check(!smsTo(ASHA, 29 * DAY + 15 * H, 29 * DAY + 16 * H, "reference resistor").empty(), "self-calibration: service SMS to the ASHA");
  std::string good = doCheckin(62, Body(), {0, 0});
  check(fabs(jnum(good, "ref_ratio") - 2.2) < 0.02, "self-calibration: healthy reference ratio 2.2 (" + std::to_string(jnum(good, "ref_ratio")) + ")");
  // day 30: a second person is enrolled; the stool tells them apart and ignores a stranger
  curDay = 30; runUntil(30 * DAY + 8 * H);
  W.usbIn.push_back("enroll 2"); loop();
  Body b2; b2.legRe = 375; b2.legRi = 800; b2.armRe = 390; b2.armRi = 880; b2.trRe = 31;
  W.bpm = 76; std::string p2 = doCheckin(48, b2, {0, 0});
  check(jstr(p2, "id") == PATIENT_ID2, "second user enrolled and recognised");
  W.bpm = 70; std::string p1 = doCheckin(62, Body(), {0, 0});
  check(jstr(p1, "id") == PATIENT_ID, "first user still recognised");
  size_t nBefore = checkins.size(); doCheckin(85, Body(), {0, 0});
  check(checkins.size() == nBefore, "stranger on a two-user stool: nothing saved");
  { bool ok = true; for (auto& m : W.sms) if (m.text.rfind("HridayMitra RED", 0) == 0 && m.text.find("no reply") == std::string::npos)
      ok = ok && m.text.size() <= 160 && m.text.find("call 108") != std::string::npos;
    check(ok, "every red SMS fits one SMS (160 chars) and keeps the 'call 108' instruction"); }
  // sit-to-stand on the platform (the chair stands on it): rise time from the force swing, a slower rise reads slower
  check(fabs(jnum(p1, "standup_s") - W.stsD) < 0.3, "sit-to-stand from the platform force: " + std::to_string(jnum(p1, "standup_s")) + " s for a 2.2 s rise");
  W.stsD = 3.4; std::string slow = doCheckin(62, Body(), {0, 0}); W.stsD = 2.2;
  check(jnum(slow, "standup_s") - jnum(p1, "standup_s") > 0.8, "slower rise reads slower: " + std::to_string(jnum(slow, "standup_s")) + " s for a 3.4 s rise");
  // the app over BLE: dated reports with a unique event id, history replay, commands run from loop()
  const char* APP_CMD = "6e8a0001-4b5a-4c3e-9a51-6d697472a004";
  check(jstr(p1, "date") == "2026-10-31" && !jstr(p1, "event_id").empty() && !std::isnan(jnum(p1, "leg_ewi")),
        "app link: report dated " + jstr(p1, "date") + ", event " + jstr(p1, "event_id") + ", with spectroscopy and walk fields");
  bleRx.clear(); bleWrite(APP_CMD, "{\"since\":\"2026-10-30\"}"); loop();
  size_t replayed = 0; for (size_t q = 0; (q = bleRx.find("\"t\":\"checkin\"", q)) != std::string::npos; q++) replayed++;
  check(replayed >= 3 && bleRx.find("\"date\":\"2026-10-29\"") == std::string::npos && bleRx.find("\"command\":\"history\",\"ok\":true") != std::string::npos,
        "app link: history since 30 Oct replayed over BLE (" + std::to_string(replayed) + " reports), older ones not");
  bleRx.clear(); bleWrite(APP_CMD, "selftest"); loop();
  check(bleRx.find("\"t\":\"selftest\"") != std::string::npos && bleRx.find("\"command\":\"selftest\",\"ok\":true") != std::string::npos,
        "app link: self-test run on the app's command, result notified");

  FILE* f = fopen("../../reports/sil_checkins.jsonl", "w");
  for (auto& c : checkins) fprintf(f, "{\"day\":%d,\"report\":%s}\n", c.first, c.second.c_str());
  fclose(f);
  f = fopen("../../reports/sil_sms.jsonl", "w");                   // every SMS the firmware sent (for the demo video)
  for (auto& m : W.sms) {
    std::string t; for (char ch : m.text) { if (ch == '"' || ch == '\\') t += '\\'; t += ch; }
    fprintf(f, "{\"day\":%d,\"minute\":%d,\"to\":\"%s\",\"text\":\"%s\"}\n", (int)(m.at_us / DAY), (int)(m.at_us % DAY / MIN_), m.to.c_str(), t.c_str());
  }
  fclose(f);
  printf("%zu check-ins, %zu SMS sent, %d failures\n", checkins.size(), W.sms.size(), fails);
  fprintf(logFile, "%zu check-ins, %zu SMS sent, %d failures\n", checkins.size(), W.sms.size(), fails);
  for (auto& m : W.sms) fprintf(logFile, "SMS day %llu %02llu:%02llu to %s: %s\n", (unsigned long long)(m.at_us / DAY),
                                (unsigned long long)(m.at_us % DAY / H), (unsigned long long)(m.at_us % H / MIN_), m.to.c_str(), m.text.c_str());
  fclose(logFile);
  return fails;
}
