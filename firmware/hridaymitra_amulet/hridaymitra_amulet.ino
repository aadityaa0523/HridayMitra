// Kavach amulet firmware (ESP32-C3 SuperMini + MPU6050, worn on a breakaway cord). Monitoring, not diagnosis.
// Sends a small summary in its BLE advertisement (no pairing, works with any stool in range):
//   last night's breathing rate (median of quiet 60 s windows while lying), night sit-ups, active minutes in the
//   last 24 h, an SOS flag (button or a fall followed by lying still) and the 6-minute walk test: the most steps in
//   any 6 minutes of the last 24 h (walk_core.h; no button, the stool asks for a walk on Sundays).
//   Same methods as engine/signals.py.
// Wiring: MPU6050 SDA GPIO8, SCL GPIO9, 3.3 V, GND. SOS button GPIO3 to GND. No magnets (pacemaker safety).
#include <Wire.h>
#include "walk_core.h"
#ifndef HM_WOKWI
#include <BLEDevice.h>
#include <BLEAdvertising.h>
#endif

const int SDA_PIN = 8, SCL_PIN = 9, SOS_PIN = 3, MPU = 0x68, FS = 10;   // 10 samples per second
float uprightDeg = 0, mag = 1;
// breathing: 60 s windows while lying still
float hpPrev = 0, lpSlow = 0, lpFast = 0; int crossings = 0, winN = 0; float magSum = 0, magSq = 0;
float nightRR[60]; int nRR = 0; float lastNightRR = NAN;
// sit-ups: lying -> sitting -> lying again within 20 min
enum Pose { UNKNOWN, LYING, SITTING } pose = UNKNOWN; uint32_t poseSince = 0; int nightSitups = 0, lastNightSitups = 0;
bool night = false;
// activity: per-minute movement, rolling 24 h in hourly slots
uint16_t activeHour[24] = {0}; int hourSlot = 0; uint32_t hourStart = 0, minuteStart = 0; float minSq = 0, minSum = 0; int minN = 0;
// 6-minute walk test: steps counted at 20 Hz, best rolling 6 minutes per hour slot
hm::Walk walk; uint16_t walkHour[24] = {0};
// falls / SOS
bool sos = false; uint32_t fallAt = 0, sosSince = 0;
#ifndef HM_WOKWI
BLEAdvertising* adv;
#endif

void mpuWrite(uint8_t r, uint8_t v) { Wire.beginTransmission(MPU); Wire.write(r); Wire.write(v); Wire.endTransmission(); }

bool readAccel(float& x, float& y, float& z) {
  Wire.beginTransmission(MPU); Wire.write(0x3B); if (Wire.endTransmission(false)) return false;
  if (Wire.requestFrom(MPU, 6) != 6) return false;
  int16_t v[3]; for (auto& a : v) a = (Wire.read() << 8) | Wire.read();
  x = v[0] / 16384.0f; y = v[1] / 16384.0f; z = v[2] / 16384.0f;   // +-2 g range
  return true;
}

void advertise() {
  uint16_t rr10 = isnan(lastNightRR) ? 0 : (uint16_t)(lastNightRR * 10);
  uint32_t act = 0; for (auto m : activeHour) act += m;
  uint16_t w6 = 0; for (auto s : walkHour) w6 = max(w6, s);
  uint8_t d[11] = {0xFF, 0xFF, 'H', 'M', (uint8_t)(rr10 & 0xFF), (uint8_t)(rr10 >> 8), (uint8_t)min(lastNightSitups, 255),
                   (uint8_t)min<uint32_t>(act / 4, 255), (uint8_t)(sos ? 1 : 0), (uint8_t)(w6 & 0xFF), (uint8_t)(w6 >> 8)};
  Serial.printf("{\"t\":\"amulet\",\"night_rr\":%.1f,\"night_situps\":%d,\"activity_min\":%u,\"walk6_steps\":%u,\"sos\":%d,\"upright_deg\":%.0f}\n",
                lastNightRR, lastNightSitups, (unsigned)act, (unsigned)w6, sos ? 1 : 0, uprightDeg);
#ifndef HM_WOKWI
  BLEAdvertisementData ad; ad.setFlags(0x06); ad.setManufacturerData(String((const char*)d, sizeof d));
  adv->stop(); adv->setAdvertisementData(ad); adv->start();
#endif
}

float median(float* a, int n) {
  for (int i = 1; i < n; i++) for (int j = i; j > 0 && a[j] < a[j - 1]; j--) { float t = a[j]; a[j] = a[j - 1]; a[j - 1] = t; }
  return n % 2 ? a[n / 2] : 0.5f * (a[n / 2 - 1] + a[n / 2]);
}

void setup() {
  Serial.begin(115200);
  pinMode(SOS_PIN, INPUT_PULLUP);
  Wire.begin(SDA_PIN, SCL_PIN);
  mpuWrite(0x6B, 0);            // wake
  mpuWrite(0x1A, 0x05);         // 10 Hz digital low-pass (read at 20 Hz)
#ifndef HM_WOKWI
  BLEDevice::init("HridayMitra-amulet");
  adv = BLEDevice::getAdvertising();
  adv->setMinInterval(1600); adv->setMaxInterval(3200);   // 1-2 s: tiny battery use
#endif
  hourStart = minuteStart = millis();
  advertise();
}

void loop() {
  static uint32_t next = 0, lastAdv = 0; static bool odd = false;
  if (millis() < next) return;
  next = millis() + 1000 / hm::WALK_FS;
  float x, y, z;
  if (!readAccel(x, y, z)) return;
  mag = sqrtf(x * x + y * y + z * z);
  int w6 = walk.add(mag);                                // steps at 20 Hz; everything below runs at 10 Hz
  if (w6 > (int)walkHour[hourSlot]) walkHour[hourSlot] = w6;
  if ((odd = !odd)) return;
  uprightDeg = acosf(constrain(fabsf(y) / max(mag, 0.1f), 0.0f, 1.0f)) * 57.3f;   // cord hangs along y when upright

  // pose and night sit-ups (hysteresis: lying > 60 deg, sitting < 30 deg)
  Pose p = uprightDeg > 60 ? LYING : uprightDeg < 30 ? SITTING : pose;
  if (p != pose) {
    uint32_t held = millis() - poseSince;
    if (p == SITTING && pose == LYING && held > 20UL * 60000) night = true;          // lay down for 20 min: it is a night
    if (p == LYING && pose == SITTING && night && held < 20UL * 60000) nightSitups++; // sat up briefly and lay back down
    pose = p; poseSince = millis();
  }
  if (night && pose == SITTING && millis() - poseSince > 3UL * 3600000) {           // up for 3 h: the night is over
    night = false; lastNightSitups = nightSitups; nightSitups = 0;
    if (nRR) lastNightRR = median(nightRR, nRR);
    nRR = 0;
  }

  // breathing: chest rise moves the gravity vector slightly; band-pass with two moving averages, count zero crossings
  float g = z / max(mag, 0.1f);
  lpSlow += (g - lpSlow) * 0.01f; lpFast += (g - lpFast) * 0.3f;
  float hp = lpFast - lpSlow;
  if (pose == LYING) {
    if ((hp > 0) != (hpPrev > 0)) crossings++;
    magSum += mag; magSq += mag * mag; winN++;
    if (winN == 60 * FS) {
      float sd = sqrtf(max(0.0f, magSq / winN - (magSum / winN) * (magSum / winN)));
      float rpm = crossings / 2.0f;
      if (sd < 0.05f && rpm >= 6 && rpm <= 40 && nRR < 60) nightRR[nRR++] = rpm;   // quiet window only
      crossings = winN = 0; magSum = magSq = 0;
    }
  } else { crossings = winN = 0; magSum = magSq = 0; }
  hpPrev = hp;

  // activity minutes, rolling 24 h
  minSum += mag; minSq += mag * mag; minN++;
  if (millis() - minuteStart >= 60000) {
    float sd = sqrtf(max(0.0f, minSq / minN - (minSum / minN) * (minSum / minN)));
    if (sd > 0.05f) activeHour[hourSlot]++;
    minSum = minSq = 0; minN = 0; minuteStart = millis();
  }
  if (millis() - hourStart >= 3600000) { hourSlot = (hourSlot + 1) % 24; activeHour[hourSlot] = walkHour[hourSlot] = 0; hourStart = millis(); }

  // SOS: button, or a hard impact followed by 10 s lying still
  if (!digitalRead(SOS_PIN) && !sos) { sos = true; sosSince = millis(); }
  if (mag > 2.5f) fallAt = millis();
  if (fallAt && millis() - fallAt > 10000) { if (pose == LYING && fabsf(mag - 1) < 0.1f && !sos) { sos = true; sosSince = millis(); } fallAt = 0; }

  if (millis() - lastAdv > (sos ? 1000 : 10000)) { advertise(); lastAdv = millis(); }
  if (sos && millis() - sosSince > 60000) sos = false;  // the stool scans every minute, so it has heard it
}
