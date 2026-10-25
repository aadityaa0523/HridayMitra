# HridayMitra Saathi: app build specification

> **To the AI or developer building this app:** this file is the complete brief. Build exactly what it describes, in the order of section 14. Don't invent medical logic: the alert rules are in section 8, with test vectors. Repo: https://github.com/aadityaa0523/HridayMitra. **Monitoring, not diagnosis**: this sentence must appear on every screen that shows a health status.

---

## 1. Product in one paragraph
HridayMitra is a home early-warning system for **worsening heart failure** in elderly patients in rural and urban India.
- **The check-in stool** measures, in a 90-second daily check-in:
  - weight;
  - leg and chest fluid (8-electrode bioimpedance);
  - pulse and SpO₂;
  - stand-up speed;
  - answers to spoken questions.
- **The worn amulet** adds night breathing, night sit-ups, activity, falls and SOS.
- **An alert engine on the stool** turns each day green, amber or red, explains why, and sends SMS to family, then the ASHA worker, then the PHC doctor.

**Saathi** is the companion app. It shows all of this in 10 Indian languages with voice commands, keeps every medical record, generates medical reports, coordinates the care team, and works **completely offline**. It never needs internet, but uses it when available.

## 2. Users and modes (one app, role chosen at setup, switchable with a PIN)
| Mode | User | Main jobs |
|---|---|---|
| **Saathi (elder)** | The patient | See today's light, hear it explained, take medicines on time, answer daily questions by voice, SOS, call family |
| **Family** | Son, daughter, spouse (may live far away) | Watch 1–4 elders, act on alerts, manage medicines, reports |
| **ASHA** | Community health worker, 30–50 patients | Today's visit list, offline visit form, referral, close the care loop, weekly report |
| **Doctor** | PHC or cardiology doctor | Patient timeline, set the sick-day plan and targets, review reports, add notes |

The setup wizard creates the household: elder profile(s), family phone numbers, ASHA number, doctor number, language, the stool pairing, and the voice choice.

## 3. Non-negotiable principles
1. **Offline first:** every feature works in airplane mode. Data lives on the device. Sync is opportunistic.
2. **Voice first for elders:** every screen can be read aloud. Every elder action can be done by voice or one big tap. **No typing in Saathi mode.**
3. **Plain language:** no medical jargon on patient or family screens. "Fluid building up in the legs", not "decreased bioimpedance".
4. **Never decides treatment:** the app only shows the plan the doctor typed in. It never suggests medicine changes on its own.
5. **Always explains:** every amber or red shows its reasons and what to do next.
6. **Accessible:** WCAG 2.2 AA at minimum, and AAA contrast in Saathi mode.
7. **Private:** encrypted at rest, consent recorded, role-based visibility. Follows India's DPDP Act 2023.

## 4. Tech stack (hackathon build = installable PWA; product = the same code wrapped later)
| Concern | Choice | Why |
|---|---|---|
| Framework | **React 18 + TypeScript + Vite** | Fast, typed, small |
| PWA / offline | **vite-plugin-pwa (Workbox)**, precache everything, `display: standalone` | Installs from a link, runs offline |
| Storage | **Dexie (IndexedDB)**; sensitive fields encrypted with **Web Crypto AES-GCM**, key derived from the app PIN (PBKDF2) | Offline, fast queries |
| Styling | **Tailwind CSS** + **Radix UI** primitives + the design tokens in section 11 | Accessible components |
| i18n | **i18next + react-i18next**, ICU plurals, one JSON file per language | 10 languages |
| Text-to-speech | **Web Speech `speechSynthesis`** (on-device voices on Android work offline once the language pack is installed); **fallback: pre-recorded MP3 clips** for the 40 core phrases in each language (`/public/audio/<lang>/<key>.mp3`) | Must speak with no network |
| Speech recognition (voice commands) | **Offline: `vosk-browser`** (WebAssembly) with small models (Hindi, English-IN; others downloadable). **Online: Web Speech `SpeechRecognition`** when available. Both go through the same intent matcher (section 7) | Offline voice commands |
| Charts | **uPlot** (tiny, fast) | Trends on cheap phones |
| PDF | **pdf-lib** + embedded **Noto Sans** and **Noto Sans Devanagari / Tamil / Telugu / Bengali / Gujarati / Kannada / Malayalam / Oriya** subset fonts | Indian-script reports offline |
| QR | `qrcode` (make) + `@zxing/browser` (scan) | Phone-to-phone transfer with no internet |
| Stool link | **Web Bluetooth** (GATT, section 9); **Web Serial** over USB-OTG as a fallback | Talk to the stool directly |
| Notifications | Service-worker notifications + in-app alarm screen; Periodic Background Sync where supported | Medicine reminders |
| Tests | **Vitest** (unit, engine vectors), **Playwright** (end-to-end incl. offline mode), **axe-core** (accessibility), Lighthouse PWA ≥ 95 | Production quality |
| Later | **Capacitor** wrapper for the Play Store (same code; native BLE, notifications, SMS read permission) | No rewrite |

Target devices: Android 9+ Chrome, 2 GB RAM, 720×1280 screens. First load under 3 s on a mid-range phone. App size without voice models under 5 MB. Voice model packs are downloaded once, about 40 MB per language.

## 5. Features by mode

### 5.1 Saathi (elder) mode
**Home: one screen, nothing else needed**
- **Today's light:**
  - a 200 px circle in the light's colour, with a shape inside (✓ green, ! amber, ✕ red) for colour-blind users;
  - one sentence in the elder's language, read aloud automatically on open ("Aaj sab theek hai").
- **Big buttons (at least 72 px tall), with icon + word + spoken label:**
  - **Check-in now** (starts the stool over Bluetooth, or guides a manual check-in if there's no stool);
  - **My medicines**;
  - **Call family**;
  - **SOS**.
- **A row of 3 small cards:** water left today (glass icons), next medicine (pill photo + time), the check-in done today ✓.
- **Microphone button** (bottom centre, 96 px): "Ask me anything" (section 7).

**Medicines**
- One card per dose: a **photo of the actual tablet** (taken by family or ASHA), name in large text, "after breakfast" with an icon, and a **Taken** button.
- Reminder alarm: full-screen, spoken repeatedly, with a gentle vibration pattern. Snooze 10 min, up to 3 times. After the 3rd missed snooze, family is notified (in-app, plus SMS through the stool when there's no internet).
- If the stool's tablet drawer reports "opened today", the dose is marked automatically.

**Daily questions (if not done on the stool)**
- "Were you more breathless today?" and "Did you need extra pillows last night?" Answer by voice ("haan" / "nahi" and equivalents in every language) or huge Yes/No buttons.

**SOS**
- Hold for 2 s (no accidental taps), or say "help" / "bachao" / "madad".
- Then: calls family 1; if there's no answer in 30 s, calls family 2, then the ASHA, then shows **"Call 108"**. It sends SMS with the location (GPS works offline) to all of them.

**Call family**
- Photo tiles of 2–4 contacts; one tap dials.

**Learn**
- 8 short offline videos or cartoon slideshows: what heart failure is, salt, fluid, daily weight, warning signs, medicines, sleeping propped up, when to call 108. Narrated in the selected language.

**Elder accessibility rules**
- Base font 22 sp, headings 32 sp, never below 18 sp.
- Contrast ≥ 7:1.
- Tap targets ≥ 64 px.
- No gestures except tap and long-press. No swipes, carousels, or timeouts shorter than 30 s.
- Every action is confirmed by voice and a vibration.
- Animations ≤ 200 ms, and "reduce motion" is respected.
- Settings are hidden behind the family PIN.

### 5.2 Family mode
- **Elders list:** each with light, last check-in time, medicine status, and an alert badge.
- **Elder detail:**
  - today's card (light, reasons, readings);
  - 7- and 30-day trends (weight, leg reading, pulse, SpO₂, night breathing);
  - medicine adherence calendar;
  - check-in streak.
- **Alert screen (amber or red):**
  - the reasons in plain words, plus a "Why this matters" explainer;
  - **the doctor's sick-day plan** as a checklist;
  - actions **I'm checking (1)**, **Need help (2)**, **Patient is fine (3)**: the same meaning as the SMS replies; the response is sent to the stool and the ASHA when possible;
  - a call-elder button.
- **Medicine manager:**
  - add medicines from a prescription photo (manual entry in the MVP; text-reading on the phone in phase 2);
  - schedule, refill countdown, upload a tablet photo.
- **Reminders:** a missed check-in by 11:00 notifies family.
- **Nearby help:** downloaded list of the nearest PHC, CHC and hospital with phone numbers; 108.
- **Reports:** generate and share (section 10).

### 5.3 ASHA mode
- **Today:**
  - patients sorted **red → amber → missed check-in (>1 day) → green**;
  - each row shows name, village and house, light, reason, and days since the last visit;
  - a filter by village.
- **Visit form** (offline, about 2 minutes):
  - BP (systolic and diastolic);
  - weight (if no stool);
  - **ankle swelling grade 0–3** with photo examples;
  - breathlessness at rest (yes/no), extra pillows (yes/no);
  - medicines seen (yes/no per drug);
  - a photo of the ankles (optional);
  - notes by voice-to-text;
  - outcome: *fine / advised / referred / called 108*.
- **Referral slip:** a one-tap PDF with the last 30 days summarised and the reason for referral. Share it, or show it as a QR code.
- **Close the loop:** saving a visit marks the alert "Seen by ASHA" and stops the escalation.
- **Weekly report** to the PHC: counts of visits, reds and referrals. Sent by SMS text if offline; as a PDF if online.

### 5.4 Doctor mode
- **Patient list** (by PHC) and a **timeline**:
  - every check-in, alert, reason and escalation step;
  - who responded and when;
  - ASHA visits, medicine adherence, and lab values.
- **Set the patient's plan:**
  - the amber plan text and the red plan text (spoken to the patient and sent to the family);
  - target dry weight;
  - daily fluid limit (litres);
  - salt advice;
  - follow-up date.
- **Sensitivity:** standard or more sensitive. More sensitive lowers the red threshold T from 7.0 to 6.0; the default is standard. Every change is written to the audit log with the doctor's name.
- **Lab results:** manual entry of sodium, potassium, creatinine, eGFR, NT-proBNP and haemoglobin, with dates (photo text-reading in phase 2).
- **Notes:** consult notes that the family and ASHA can see.

## 6. Multilingual
- **Languages (MVP: Hindi + English, with all keys present in all files):** English, हिन्दी, தமிழ், తెలుగు, ಕನ್ನಡ, मराठी, বাংলা, ગુજરાતી, മലയാളം, ଓଡ଼ିଆ.
- **Choosing:** the language is picked on first launch by tapping a **spoken** list. Each language name is read aloud in that language.
- **Per user:** each user can have a different language (the elder in Tamil, the son in English).
- **Numbers and units:** numerals follow the locale. Units are always shown with words ("62.4 kilo").
- **Copy rules:** sentences under 12 words, second person ("your weight"), no fear words ("danger", "failure"); use "needs attention" or "see the doctor today".
- **Translation files:** `src/i18n/<lang>.json`, with keys grouped by screen. Include the 40 core spoken phrases (section 7.4) and record MP3 fallbacks for them.

## 7. Voice commands
### 7.1 How it works
**Mic button**, or the optional wake phrase "Saathi" in elder mode only (on-device keyword spotting with a Vosk grammar).
1. Speech is converted to text: Vosk offline, or Web Speech when online.
2. The text is normalised: lower-case, Devanagari and other scripts kept, common romanised spellings mapped.
3. The **intent matcher** checks each intent's phrase list (fuzzy match, ratio ≥ 0.8), per language.
4. The action runs and is confirmed aloud.
5. If no intent matches: "Sorry, I didn't understand. You can say: medicine, check-in, help." Show 3 suggestion chips.

### 7.2 Intents (MVP set)
| Intent | Example phrases (English / Hindi / Tamil) | Action |
|---|---|---|
| `status_today` | "how am I today" / "aaj main kaisa hoon" / "inniku eppadi irukken" | Read out today's light and reasons |
| `start_checkin` | "start check-in" / "jaanch shuru karo" / "check-in thodangu" | Start the stool check-in |
| `medicine_next` | "which medicine now" / "abhi kaunsi dawai" / "ippo endha maathirai" | Read the next dose and show its photo |
| `medicine_taken` | "I took my medicine" / "dawai le li" / "maathirai saapitten" | Mark the current dose taken |
| `call_family` | "call my son" / "bete ko phone karo" / "magan-ukku call pannu" | Call contact 1 (or the named relation) |
| `call_asha` | "call ASHA" / "asha didi ko bulao" / "ASHA-vai koopidu" | Call the ASHA |
| `sos` | "help" / "bachao" / "madad" / "udhavi" | SOS flow (asks "Calling family now" and gives 5 s to cancel) |
| `answer_yes` / `answer_no` | "yes" / "haan" / "aamaa"; "no" / "nahi" / "illai" | Answer the current question |
| `water_left` | "how much water" / "kitna paani" / "evvalavu thanneer" | Read the remaining fluid allowance |
| `repeat` | "say again" / "phir se bolo" / "thirumba sollu" | Repeat the last spoken message |
| `read_screen` | "read this" / "padh ke sunao" / "padichi kaattu" | Read the current screen |
| `go_home` | "home" / "ghar" / "mudhal page" | Go to the home screen |
| `report_week` | (family/doctor) "weekly report" / "hafte ki report" | Generate the weekly PDF |

Phrase lists live in `src/voice/intents.<lang>.json`. Each intent has at least 6 phrasings per language. Tests check every phrase maps to its intent.

### 7.3 Voice safety
- SOS by voice always gives a **5-second spoken countdown with cancel** ("bolo 'ruk jao' to cancel").
- Voice never confirms a medical decision; it only reads status and plans.

### 7.4 Core spoken phrases (pre-record per language)
Greeting, the three lights, the two daily questions, medicine reminder, medicine taken, check-in start, check-in steps (sit, feet on plates, hold handles, finger on sensor, stand up), the amber plan, the red plan, SOS calling, the SOS cancel countdown, "family has been told", "ASHA is coming", "still learning your normal", "please place your feet again", "didn't understand", and water allowance (number words 0–10 in each language).

## 8. The alert engine (only for manual entry; the stool decides on its own)
When readings come **from the stool**, **show the stool's light; never recompute it.** When the family or ASHA enters readings by hand (no stool), the app runs the **same engine**, ported from `firmware/hridaymitra_stool/engine_core.h` / `engine/alert_engine.py`. It **must reproduce `docs/app/engine_test_vectors.json` exactly**: 5 patients, about 820 days, with the expected light and score S for each day.

**Inputs per day** (null = not measured): `weight_kg, leg_z_ohm, trunk_z_ohm, leg_ewi` (leg water-outside-cells index from 5/20/50 kHz spectroscopy), `pulse_bpm, night_rr, spo2, activity_min, standup_s, breathless (0/1), orthopnea (0/1), night_situps`.

**Signals:**

| Signal | Family | Bad direction | Minimum spread | Spread relative to the normal? | Weight in family |
|---|---|---|---|---|---|
| weight_kg | fluid | up | 0.30 | no | 1.0 |
| leg_z_ohm | fluid | down | 0.010 | yes (× normal) | 1.0 |
| trunk_z_ohm | fluid | down | 3.0 | no | 0.5 |
| leg_ewi | fluid | up | 0.003 | yes | 1.0 |
| pulse_bpm | heart_lungs | up | 2.0 | no | 1.0 |
| night_rr | heart_lungs | up | 0.7 | no | 1.0 |
| spo2 | heart_lungs | down | 0.7 | no | 0.5 |
| activity_min | daily_life | down | 0.08 | yes | 1.0 |
| standup_s | daily_life | up | 0.04 | yes | 1.0 |

**Algorithm**, for day t, using only days ≤ t:
1. **Guest gate:** take the last 7 earlier non-null weights. If there are at least 3 and |w_t − their median| > 2.5 kg, the day is a guest. Set weight, leg, trunk, leg_ewi, pulse, spo2 and standup to null for that day, and keep it stored null (the history stays gated).
2. **Plate gate:** take the last 7 earlier non-null leg readings. If there are at least 3 and |leg_t / median − 1| > 0.25, set leg, trunk and leg_ewi to null for that day.
3. **For each signal:**
   - **baseline** = non-null values from days max(0, t−35) up to max(0, t−6), exclusive end (i.e. days t−35 … t−7);
   - **level** = mean of the non-null values from days t−2 … t;
   - skip the signal if there are fewer than 6 baseline values or no level values;
   - med = median(base); spread = max(1.4826 × median(|base − med|), min_spread × (|med| if relative else 1));
   - z = clip((level − med) / spread × direction, 0, 5) × weight.
4. **Symptoms:** z_sym = 1.2 × max(0, (breathless + orthopnea summed over days t−2 … t, null counts as 0) − 1).
   **Sit-ups:** if any non-null sit-up value in t−2 … t, z_sit = max(0, their sum − 1). Both belong to daily_life.
5. **Family score** = largest z + 0.5 × second largest (0 if none). **S** = fluid + heart_lungs + daily_life. n_fam = number of families ≥ 1.5. maxFam = the largest family score.
6. **danger** = the raw SpO₂ today < 90 and not a guest day.
7. **Light**, with T = 7.0 (engine v3, `engine/frozen_params_v3.json`). The state carries `red` (bool) and flags for the last 3 days: high = S ≥ T, famHigh = maxFam ≥ T.
   - Append today's flags first.
   - If today has no data at all (every signal null and both answers null), the light = yesterday's light.
   - Else if danger: red = true.
   - Else if red already: red = S ≥ 0.4 T (stays red until well below).
   - Else: red = (at least 2 of the last 3 days high and n_fam ≥ 2) or (at least 3 days recorded and all of the last 3 famHigh).
   - Light = 2 if red, else 1 if S ≥ 0.6 T, else 0.
8. **learning** = no signal had a baseline. Show "Still learning your normal (about 10 days)".
9. **Reasons:** the top 3 signals with z ≥ 1, worded as "weight +1.8 kg vs normal", "leg reading −6 % vs normal", "resting pulse +7 bpm", "breathless or extra pillows reported", "sitting up at night".

## 9. Talking to the stool
**A. Bluetooth Low Energy (primary).** The stool is a GATT server. *Firmware task: add this service to `firmware/hridaymitra_stool`; it isn't implemented yet.*
| Item | UUID | Properties | Content |
|---|---|---|---|
| Service "HridayMitra Stool" | `6e8a0001-4b5a-4c3e-9a51-6d697472a001` | – | – |
| Check-in reports | `…a002` | notify, read | One JSON line per check-in (format B below), sent in ≤ 180-byte chunks ending with `\n` |
| History request | `…a003` | write | `{"since":"2026-10-01"}` → the stool replays its stored reports as notifications |
| Commands | `…a004` | write | `checkin`, `selftest`, `{"reply":1\|2\|3}` (care-loop answer), `{"plan":{"amber":"…","red":"…"}}` (doctor's plan), `{"time":"2026-10-25T08:00:00+05:30"}` |
| Status | `…a005` | read, notify | `{"battery_mv":3950,"signal":18,"selftest":"","light":0,"learning":false}` |

**B. Messages the stool already sends** (USB serial today, 115200 baud, one JSON per line; same over BLE):
```json
{"t":"checkin","id":"P001","weight_kg":62.0037,"leg_z_ohm":578.4963,"trunk_z_ohm":27.8620,"pulse_bpm":70.5882,"spo2":96.4632,"standup_s":3.4670,"night_rr":16.0,"night_situps":0,"activity_min":200,"leg_ewi":0.69107,"breathless":0,"orthopnea":0,"took_pills":1,"light":0,"S":1.2817,"learning":0,"guest":0,"why":"weight +0.8 kg; resting pulse +3.6 bpm"}
{"t":"sms","to":"+910000000001","text":"HridayMitra RED for P001. Why: ..."}
{"t":"reply","from":"+910000000003","digit":"1"}
{"t":"selftest","battery_mv":3950,"signal":18,"problems":""}
```
Missing values are printed as `nan`: replace `:nan` with `:null` before `JSON.parse`.

**C. No Bluetooth: SMS.** The family's phone already receives the stool's SMS (format in `firmware/hridaymitra_stool/hridaymitra_stool.ino`, `startCareLoop`). In the Capacitor build, parse incoming SMS from the stool's number into alerts. In the PWA, let the user paste or share the SMS into the app (share target).

**D. Serial fallback:** Web Serial over a USB-OTG cable (Android Chrome), same JSON lines.

## 10. Medical reports (PDF, generated on the phone, offline)
**Every report includes:**
- a header with the patient name, age, ABHA number (if any), dates, the generating user and a QR code of the report ID;
- the footer "HridayMitra: monitoring, not diagnosis. Page x of y";
- the selected language plus an English column for clinical values.

| Report | Pages | Contents |
|---|---|---|
| Daily card | 1 | Light, reasons, readings vs normal, medicines taken |
| Weekly summary | 1 | Check-ins 6/7, light strip, weight trend, adherence %, alerts and responses |
| **Monthly clinical report** | 2 | Charts: weight, leg reading, chest reading, pulse, SpO₂, night breathing, with the personal normal band; alert episodes table; ASHA visits; labs |
| **OPD visit summary** | 1 | What the doctor needs in 30 s: current light, 30-day trend thumbnails, recent alerts, medicines and adherence, symptoms, labs, the ASHA's last findings |
| Alert episode report | 1 | Trigger, reasons, escalation timeline (who was messaged when, who replied), outcome |
| Medication adherence | 1 | Calendar heat map per drug, missed-dose list |
| Lab history | 1 | Table and sparklines per lab value |
| Referral slip (ASHA) | 1 | Reason, findings, last 30 days, contact |
| Device health | 1 | Self-test history, battery, signal, service actions |
| **FHIR R4 bundle** | JSON | Observations with LOINC codes: weight 29463-7, heart rate 8867-4, SpO₂ 59408-5, respiratory rate 9279-1; impedance as text-coded observations. Same mapping as `engine/product.py fhir_bundle()` |

**Sharing:** the Android share sheet (WhatsApp etc.) when online; **QR transfer** offline (compressed data split across animated QR frames for big files, or the report ID if a PHC server exists); print.

## 11. UI/UX design system
**Feel:** warm, calm and trustworthy, like a caring family doctor's clinic. Not a "tech gadget". Rounded shapes, soft shadows, generous space.

**Colour tokens** (light theme; also provide a dark theme and a high-contrast theme, auto-on in Saathi mode):
| Token | Hex | Use |
|---|---|---|
| `--brand` | #0D6B6E | Headers, primary buttons (deep teal) |
| `--brand-soft` | #E6F2F2 | Surfaces |
| `--ok` | #1E8E4F | Green state (with ✓ icon) |
| `--watch` | #C77700 | Amber state (with ! icon). Text on amber is #1A1A1A |
| `--alert` | #C0392B | Red state (with ✕ icon) |
| `--fluid` | #2C7BE0 | Fluid charts and indicators |
| `--ink` | #17202A | Body text |
| `--muted` | #5D6D7E | Secondary text |
| `--bg` | #FAFBFB | Background |

Colours always pair with an icon and a word; never use colour alone.

**Type:**
- Noto Sans plus the script-matching Noto fonts.
- Scale (sp): 14 / 16 / 18 / 22 / 28 / 32 / 40. Saathi mode starts at 22.
- Line height 1.4.

**Spacing and shape:**
- 4 px grid.
- Cards: 16 px padding, 16 px radius, soft shadow.
- Buttons: 56 px tall (64–96 px in Saathi mode), 14 px radius.

**Components:**
- StatusOrb (big light + shape + spoken label);
- ReasonList;
- TrendChart (with the personal normal band shaded);
- MedicineCard (photo, time icon, Taken button);
- BigActionButton;
- MicButton (pulsing ring while listening, a live transcript bubble);
- AlertBanner;
- PlanChecklist;
- VisitForm sections;
- ReportPreview;
- LanguagePicker (spoken);
- PinPad;
- OfflineBadge (shows "Saved on phone ✓", never an error);
- SyncStatus.

**Motion:**
- 150–200 ms ease-out; the light orb "breathes" gently (scale 1.00–1.03, 4 s) when green.
- Respect reduce-motion.

**Empty and error states:**
- Always friendly and actionable: "No check-in yet today. Sit on the stool or tap Check-in."
- **Never show a stack trace or the word "error"** to elders.

**Key screens to design and build** (mobile-first, 360×800):
1. Language picker (spoken)
2. Role and household setup wizard (5 steps, with a progress bar)
3. Saathi home
4. Medicine alarm (full-screen)
5. Daily questions
6. SOS countdown
7. Learn player
8. Family elders list
9. Elder detail with trends
10. Alert screen with plan and actions
11. Medicine manager
12. ASHA today list
13. ASHA visit form
14. Referral slip preview
15. Doctor timeline
16. Plan editor
17. Lab entry
18. Reports hub
19. Report preview and share
20. Settings (language, voice, contacts, stool pairing, data export, delete data)
21. Stool pairing (Bluetooth scan → pair → test check-in)

## 12. Data model (Dexie tables)
```ts
patients(id, name, ageYears, sex, photo, language, abhaId?, village?, house?, phone?, doctorPlan:{amber:string, red:string, dryWeightKg?, fluidLimitL?}, sensitivity:'standard'|'high', createdAt)
contacts(id, patientId, role:'family1'|'family2'|'asha'|'doctor', name, phone, photo?)
checkins(id, patientId, date, source:'stool'|'manual'|'asha', weight_kg?, leg_z_ohm?, trunk_z_ohm?, pulse_bpm?, spo2?, standup_s?, night_rr?, night_situps?, activity_min?, breathless?, orthopnea?, took_pills?, light, S, reasons:string[], guest:boolean, learning:boolean)
alerts(id, patientId, checkinId, light, startedAt, reasons, steps:[{at, to, role, channel:'sms'|'app', status}], responses:[{at, by, digit:1|2|3}], closedAt?, outcome?)
medicines(id, patientId, name, strength, photo?, schedule:[{time:'08:00', withFood:'before'|'after'}], stockCount?, active)
doses(id, medicineId, patientId, dueAt, takenAt?, source:'tap'|'voice'|'drawer', missed:boolean)
visits(id, patientId, ashaId, at, bpSys?, bpDia?, weight?, edemaGrade?, breathlessRest?, pillows?, medsSeen:{[medId]:boolean}, photo?, notes, outcome)
labs(id, patientId, at, test:'Na'|'K'|'Creatinine'|'eGFR'|'NTproBNP'|'Hb', value, unit)
notes(id, patientId, by, at, text)
reports(id, patientId, type, period, createdAt, fileBlob, sha256)
audit(id, at, user, action, details)          // every plan or threshold change, every export
settings(key, value)
```

## 13. Security, privacy, safety
- **PIN** per role. Saathi mode needs no PIN; switching out of it does. Biometric unlock where available.
- **Encryption:** health fields encrypted with AES-GCM; the key comes from the PIN (PBKDF2, 310k iterations) and is cached in memory only.
- **Consent screen** at setup, recorded in the audit log. **Export all data** (JSON + PDFs) and **delete all data**, both in settings.
- **Logging:** no third-party analytics; no data leaves the phone except by explicit share or sync.
- **Disclaimer** "Monitoring, not diagnosis. In an emergency call 108." on the status, alert and report screens.
- **The red alert UI** always shows the doctor's plan and the 108 button; it never auto-dismisses.

## 14. Build order (milestones with acceptance criteria)
1. **Skeleton:**
   - Vite + React + TS + Tailwind + PWA; works offline after the first load (Playwright test with network blocked);
   - i18n with English and Hindi;
   - design tokens; StatusOrb, BigActionButton and MicButton components.
2. **Data and engine:**
   - Dexie schema;
   - the engine port in `src/engine/` passes **all** `docs/app/engine_test_vectors.json` cases (light and S within 1e-3);
   - a seed loader that imports one synthetic patient's history from the vectors file, so the demo has 5 months of data.
3. **Saathi mode:** home, medicines and alarm, daily questions, SOS with countdown, read-aloud; voice intents for English + Hindi with Vosk offline (falling back to Web Speech).
4. **Family mode:** elders list, elder detail with trends, alert screen with plan and actions, medicine manager, reminders.
5. **ASHA mode:** today list, visit form, referral slip, close the loop, weekly report.
6. **Doctor mode:** timeline, plan editor, sensitivity with audit, labs, notes.
7. **Reports:** all PDFs in section 10, including Devanagari rendering, plus the FHIR export and QR share.
8. **Stool link:** Web Bluetooth with the section 9 UUIDs, plus a **simulator mode** (built-in fake stool that replays the vectors) so the demo works with no hardware; Web Serial fallback.
9. **Polish:**
   - accessibility (axe: 0 serious issues);
   - Lighthouse PWA ≥ 95, Performance ≥ 90 on a mid-range phone profile;
   - all 10 language files (machine-translated, marked "needs review");
   - pre-recorded clips for Hindi.

**Definition of done:**
- all unit and end-to-end tests pass;
- works in airplane mode;
- installs on Android;
- an elder can do the morning routine (hear status, take medicine, answer the questions) **without reading**, using voice or 3 taps;
- the family receives and acts on a red alert;
- the ASHA records a visit offline;
- the doctor generates the OPD summary PDF in Hindi.

## 15. Demo script (3 minutes)
1. Install from a link on a phone. Pick हिन्दी by voice.
2. Saathi mode: the app greets the elder and reads today's green status aloud. Say "dawai le li" and the dose is marked.
3. Switch the simulator stool to "worsening" (or use the real stool over Bluetooth). The light turns red and the reasons are read aloud.
4. Family mode: open the alert, show the doctor's plan, tap "I'm checking".
5. ASHA mode: the patient tops the list; fill the visit form offline; generate a referral slip.
6. Doctor mode: generate the OPD summary PDF in Hindi; show the FHIR export.
7. Turn on airplane mode, repeat a step, and show that everything still works.

## 16. Files in this repo the builder should use
- `docs/app/engine_test_vectors.json`: engine ground truth (section 8).
- `engine/alert_engine.py`, `firmware/hridaymitra_stool/engine_core.h`: the reference engine.
- `engine/product.py`: doctor's plan, coaching tips, two-user matching, weekly summary, FHIR mapping (same rules).
- `firmware/hridaymitra_stool/hridaymitra_stool.ino`: the stool's JSON messages and SMS formats.
- `tools/make_voice_clips.py`: the core prompt texts (English and Hindi) to reuse for voice.
- `docs/block_diagram.png`, `README.md`, `docs/EVIDENCE.md`: product context.

Put the app in a new folder **`app/`** in this repo, with its own `README.md` (setup: `npm i`, `npm run dev`, `npm test`, `npm run build`). Keep it independent from the Python code.
