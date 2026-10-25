# Phase 8: check-in device link

Accepted scope remains the synthetic hackathon PWA, one Android phone with role switching, and the amulet feeding the check-in device. This is a prototype transport implementation, not a production clinical pairing or device-authentication system.

## Open and demonstrate

Unlock the vault in Settings, load the five-month fixture if wanted, then open Device connection. Choose Built-in simulator, keep device patient ID P001 and Create linked demo elder. This creates an isolated profile within the existing four-elder household limit. Existing fixture histories are not overwritten.

Connect device -> Request device history imports no data automatically. The simulator replays dated fixture messages through the same line parser used for real devices. Review ID/dates, check the review box and Save reviewed device records. Stable replays through fixture index 30. Worsening uses the first recorded red day; Recovery uses the first subsequent green day. Start test check-in requests the selected scenario. Home -> Family -> linked elder shows the preserved recorded light and reasons.

Run device self-test produces clearly labeled synthetic telemetry. Save device health event stores it encrypted with receipt timestamp and audit. Saved health events appear on the device screen and in device health reports, whose telemetry receipt timestamps are explicitly independent of the historical replay date. Disconnect is explicit; changing patient, leaving the device page, reload or lock tears down the connection. Reconnecting requires another user action.

## BLE and serial

The app filters the chooser by service 6e8a0001-4b5a-4c3e-9a51-6d697472a001. Characteristic suffixes a002/a003/a004/a005 are reports, history, commands and status. Reports are fragmented UTF-8 newline messages; notifications may split multibyte Hindi characters. The status characteristic is subscribed/read. Commands use write-with-response, with an additional newline on serial.

Supported controls are checkin, selftest and a compact history request {"since":"YYYY-MM-DD"}. A successful write is not described as measurement completion. A later device report/ack is distinct. Care-loop reply, clinician-plan, threshold and clock updates are not sent by this screen; pending care instructions elsewhere remain pending, and this firmware explicitly rejects unsupported commands.

For real-board demonstration, create a separate profile with Bluetooth LE or USB / Serial and the exact firmware patient ID (P001 or P002 by default). IDs are case-sensitive. Authorize the browser chooser and review received records before saving. Existing same-day records cannot be silently corrected or replaced.

Web Serial requests a port and opens at 115200 baud. The UI feature-detects the APIs and handles cancellation, permission rejection, connection failure and disconnection. Use a secure browser context. Loopback on the laptop qualifies; accessing a laptop through a plain HTTP LAN IP on the phone does not establish a secure context. A deployed HTTPS origin or an appropriate USB development setup is required for the phone.

Android USB-OTG serial support depends on the Chrome/Android/device combination. Presence of navigator.serial alone does not establish USB support. BLE and the offline simulator are the primary phone paths; the serial adapter is available on supporting browsers. See https://developer.chrome.com/docs/capabilities/serial and https://developer.chrome.com/docs/capabilities/bluetooth.

## Protocol and persistence

The parser accepts the section 9 checkin/selftest formats and explicit status/ack messages. It repairs bare :nan value tokens without changing quoted text, validates finite nonnegative measurements, IDs, dates, light, score, flags and message bounds. Negative sentinel -1 telemetry becomes unknown; GSM signal 99 remains unknown. Lines are capped at 8192 bytes and the review buffer at 200 records. Legacy packets lacking dates require one explicitly confirmed date at a time; undated multi-record history is rejected.

Binding records and health events use the existing encrypted settings collection. Linked patient IDs are separate from hardware patient IDs. Imported check-ins are atomically written with audit and replay cursor. Exact duplicates are idempotent; conflicting date/event IDs, wrong identities, transport changes and invalid batches are rejected. Device-authored light and score are preserved and never recalculated against the phone's incomplete history. Raw measurements, gated values, source, device ID and original why text are retained. Guest/plate exclusions remain missing in clinical exports.

The wire protocol does not supply structured engine reasons or a threshold. Original why text is displayed; the Doctor timeline shows an unknown threshold for these records. The internal compatibility threshold field does not drive rescoring. Authentication of the transmitting device, professional signatures and real patient onboarding are outside this synthetic demo.

## Firmware

firmware/hridaymitra_stool/app_link.h adds an ESP32 GATT server alongside the existing amulet scan. Sensor operations run from a bounded FreeRTOS command queue in the main loop rather than BLE callbacks. Notifications use 20-byte chunks, within the required 180-byte maximum and compatible with minimum ATT MTU. UTF-8 bytes are reassembled by the app.

The newest eight reports are persisted in a dedicated NVS namespace and replayed in order on/after since. This is bounded recent history, not an indefinite archive. Reports with no valid clock date are excluded from date-filtered replay. Live reports include stable persisted sequence IDs and a date when the network clock is valid. USB and BLE share history/report formats. Self-test results update the status characteristic and the fragmented report stream. Advertising resumes after disconnect.

The only engine change is read-only access to the latest gated sample to report the plate gate; the frozen scoring algorithm is unchanged. The existing modem, sensor, amulet, SMS and audio logic remain in place. GATT is intended for a trusted synthetic laboratory demo; no authenticated/encrypted application pairing is implemented. Do not flash placeholder-contact firmware onto a clinical device.

Build with ESP32 Arduino core 3.3.12 and the Huge APP partition (no OTA): arduino-cli compile --fqbn esp32:esp32:esp32:PartitionScheme=huge_app firmware/hridaymitra_stool. No flashing is performed by this task.

## Verification

Production PWA build, 105 unit tests and all 24 browser tests pass. The check-in firmware compiles with ESP32 Arduino core 3.3.12, Huge APP: 1,906,900 bytes program storage (60% of 3,145,728), 73,980 bytes static RAM (22%). Static RAM accounting does not measure runtime BLE/audio heap usage.

Unit tests cover fragmented UTF-8/nan parsing, malformed/oversized data, unknown telemetry, explicit binding/date, preserved device results, atomic import/conflicts, simulator scenarios, GATT UUIDs/notifications/writes/cleanup, serial framing/cancellation and connection failures. Browser checks run the complete offline simulator/history/import/health workflow, reload/unlock recovery, wrong-ID and same-day conflict rejection, Hindi layout and accessibility.

Physical ESP32 pairing, sensor acquisition, amulet/server BLE coexistence, phone USB-OTG, radio interruption, NVS persistence under power loss and modem delivery still require the assembled devices. Simulator and adapter-mock checks cannot establish those hardware properties.
