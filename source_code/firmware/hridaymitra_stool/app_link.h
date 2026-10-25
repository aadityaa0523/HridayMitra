// App link (HridayMitra Saathi app): BLE GATT service + the same lines over USB. Synthetic records only, trusted lab.
// Reports: every check-in and self-test as one JSON line, notified in 20-byte fragments (works at the minimum MTU).
// Commands (written by the app): "checkin", "selftest", {"since":"YYYY-MM-DD"} = replay the last 8 dated reports.
// Commands are queued here and run by loop(), never inside the BLE callback. In Wokwi (no Bluetooth) only USB is used.
#pragma once
#ifndef HM_WOKWI
#include <BLEServer.h>
#include <BLE2902.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#endif

static Preferences hmLinkPrefs;
static String hmHistory[8];
static unsigned hmNext = 0, hmCount = 0;
#ifndef HM_WOKWI
static const char* HM_SERVICE = "6e8a0001-4b5a-4c3e-9a51-6d697472a001";
static BLECharacteristic *hmReports = nullptr, *hmStatus = nullptr;
static QueueHandle_t hmCommands = nullptr;
static volatile bool hmRestartAdvertising = false;
#endif

static String hmQuoted(const String& input) {
  String out = "\"";
  for (unsigned i = 0; i < input.length(); i++) {
    char c = input[i];
    if (c == '"' || c == '\\') { out += '\\'; out += c; }
    else if (c == '\n') out += "\\n";
    else if (c == '\r') out += "\\r";
    else if ((uint8_t)c >= 32) out += c;
  }
  out += "\"";
  return out;
}
static void hmNotifyLine(const String& line) {
#ifndef HM_WOKWI
  if (!hmReports) return;
  String bytes = line; bytes += "\n";
  for (unsigned offset = 0; offset < bytes.length(); offset += 20) {   // 20-byte fragments: minimum ATT MTU of 23
    unsigned count = min(20U, (unsigned)bytes.length() - offset);
    hmReports->setValue((uint8_t*)bytes.c_str() + offset, count);
    hmReports->notify(); delay(12);
  }
  hmReports->setValue(bytes.c_str());
#endif
}
static void hmAck(const char* command, bool ok) {
  String line = "{\"t\":\"ack\",\"command\":"; line += hmQuoted(command); line += ok ? ",\"ok\":true}" : ",\"ok\":false}";
  Serial.println(line); hmNotifyLine(line);
}
static void hmPublishReport(const String& line) {
  Serial.println(line);
  hmHistory[hmNext] = line;
  char key[8]; snprintf(key, sizeof key, "r%u", hmNext);
  hmLinkPrefs.putString(key, line);
  hmNext = (hmNext + 1) % 8; hmCount = min(hmCount + 1, 8U);
  hmLinkPrefs.putUInt("next", hmNext); hmLinkPrefs.putUInt("count", hmCount);
  hmNotifyLine(line);
}
static void hmPublishStatus(int battery, int signal, const String& problems) {
  char head[64]; snprintf(head, sizeof head, "{\"t\":\"selftest\",\"battery_mv\":%d,\"signal\":%d,\"problems\":", battery, signal);
  String line = head; line += hmQuoted(problems); line += "}";
  Serial.println(line);
#ifndef HM_WOKWI
  if (hmStatus) { hmStatus->setValue(line.c_str()); hmStatus->notify(); }
#endif
  hmNotifyLine(line);
}
#ifndef HM_WOKWI
class HmWrites : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic* characteristic) override {
    auto value = characteristic->getValue();
    if (!hmCommands || value.length() > 180) return;
    char command[181] = {};
    memcpy(command, value.c_str(), value.length());
    xQueueSend(hmCommands, command, 0);
  }
};
class HmConnections : public BLEServerCallbacks {
  void onDisconnect(BLEServer*) override { hmRestartAdvertising = true; }
};
#endif
static void hmBeginLink() {
  hmLinkPrefs.begin("hm-app");
  hmNext = hmLinkPrefs.getUInt("next", 0) % 8;
  hmCount = min((unsigned)hmLinkPrefs.getUInt("count", 0), 8U);
  for (unsigned i = 0; i < 8; i++) { char key[8]; snprintf(key, sizeof key, "r%u", i); hmHistory[i] = hmLinkPrefs.getString(key, ""); }
#ifndef HM_WOKWI
  hmCommands = xQueueCreate(8, 181);
  BLEDevice::setMTU(185);
  auto server = BLEDevice::createServer(); server->setCallbacks(new HmConnections());
  auto service = server->createService(HM_SERVICE);
  hmReports = service->createCharacteristic("6e8a0001-4b5a-4c3e-9a51-6d697472a002", BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  hmReports->addDescriptor(new BLE2902());
  for (const char* uuid : {"6e8a0001-4b5a-4c3e-9a51-6d697472a003", "6e8a0001-4b5a-4c3e-9a51-6d697472a004"}) {
    auto c = service->createCharacteristic(uuid, BLECharacteristic::PROPERTY_WRITE); c->setCallbacks(new HmWrites());
  }
  hmStatus = service->createCharacteristic("6e8a0001-4b5a-4c3e-9a51-6d697472a005", BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  hmStatus->addDescriptor(new BLE2902()); hmStatus->setValue("{\"t\":\"status\",\"battery_mv\":null,\"signal\":null,\"selftest\":\"Not run\"}");
  service->start(); auto advertising = BLEDevice::getAdvertising(); advertising->addServiceUUID(HM_SERVICE); advertising->setScanResponse(true); BLEDevice::startAdvertising();
#endif
}
// {"since":"YYYY-MM-DD"}: replay the persisted reports dated on or after it (undated legacy reports are skipped)
static bool hmHistoryRequest(const String& command) {
  if (!command.startsWith("{\"since\":\"") || !command.endsWith("\"}") || command.length() != 22) return false;
  String since = command.substring(10, 20);
  for (unsigned i = 0; i < 10; i++) if (i == 4 || i == 7) { if (since[i] != '-') return false; } else if (!isDigit(since[i])) return false;
  for (unsigned i = 0; i < hmCount; i++) {
    const String& line = hmHistory[(hmNext + 8 - hmCount + i) % 8];
    int pos = line.indexOf("\"date\":\"");
    if (pos >= 0 && strncmp(line.c_str() + pos + 8, since.c_str(), 10) >= 0) { Serial.println(line); hmNotifyLine(line); }
  }
  hmAck("history", true); return true;
}
// a command from the app, run from loop(): returns false if there was none
static bool hmPollCommand(String& c) {
#ifndef HM_WOKWI
  if (hmRestartAdvertising) { hmRestartAdvertising = false; BLEDevice::startAdvertising(); }
  char buf[181];
  if (hmCommands && xQueueReceive(hmCommands, buf, 0) == pdTRUE) { c = buf; c.trim(); return true; }
#endif
  return false;
}
