# HridayMitra Saathi

Phase 6 of the hackathon PWA. React 18 + TypeScript + Vite, Tailwind CSS, Radix Dialog, i18next and Workbox. Runs independently of the Python project.

## Engine and stool link (merged into the main repo)

- **Engine v3**, the same as `engine/alert_engine.py`: adds the leg extracellular-water index (`leg_ewi`, spectroscopy); T 7.0 standard / 6.0 more sensitive. `tests/engine.test.ts` checks every day of `docs/app/engine_test_vectors.json`, which `tools/generate_vectors.py` makes from the Python engine.
- **Stool link** (`firmware/hridaymitra_stool/app_link.h`): BLE GATT service and the same JSON lines over USB. Check-ins carry `date`, `event_id`, `plate`, `leg_ewi`, `ref_ratio` (self-calibration) and `walk6_steps` (amulet walk test, shown in Doctor → readings).
- **Firmware ↔ app cross-check:** `tests/device.test.ts` parses every check-in the real stool firmware wrote in the month-long software-in-the-loop run (`reports/sil_checkins.jsonl`).
- **Voice models** (`public/models/*.bin`, 82 MB) are not in git: run `python tools/prepare_voice_models.py` (downloads and checks the sha256 in `public/models/manifest.json`).

## Run

Use Node.js 22.12+ (tested here with Node 24).

```sh
npm i
npm run dev
npm test
npm run build
npm run preview
npm run test:e2e
```

The E2E suite runs against the production build on port 4173. Install a Playwright browser with `npx playwright install chromium` if needed. Browser tests emulate a Pixel 5 viewport; they do not substitute for testing a physical Android phone.

## What is implemented

- Language welcome, English/Hindi translations and persistent language choice.
- Mobile-first elder home, StatusOrb, BigActionButton and MicButton.
- Explicit unknown/locked health states; a labeled 164-day synthetic history is available after vault setup.
- Check-in platform and included wearable amulet indicators.
- One-phone role navigation for Saathi, Family, ASHA and Doctor. Each can show the unlocked synthetic patient summary; Family mode now includes elders, trends, alerts and medicines; ASHA now includes visits and referrals; Doctor mode now includes plans, timeline, sensitivity, labs and notes.
- Accessible dialogs, keyboard focus handling, reduced-motion support.
- Read-aloud using an available matching device voice. No remote voice service is explicitly called; voice availability/offline support depends on the selected system voice. Offline English/Hindi command recognition is available after installing the optional Vosk pack. Recorded speech fallbacks remain Phase 9.
- Install manifest, PNG icons, cached production shell and opt-in update prompt.
- Emergency help opens a phone dialler only after the user explicitly selects 108. No automatic calls, alerts or SMS.

## Android demo

Build and serve `dist/` on an HTTPS origin. In Android Chrome, open the site, complete first load, wait for “App ready offline”, then choose Add to Home screen / Install app. Reopen it, turn off networking and confirm it reloads. A plain HTTP LAN URL is not a secure context and cannot prove PWA installation or service-worker behavior. Desktop localhost is a secure-context exception.

No public deployment has been made. The current UI is intentionally a foundation, not the whole application.

## Phase 2 demo

Settings → create and confirm a 6–12 digit PIN → agree to synthetic local storage → Create demo vault → Load five-month demo. Choose a replay date or Next red-alert day, then open Home. All results are historical simulations, not today's real health. The amulet's night breathing and activity are included. No doctor plan or medicine instructions are seeded.

Records are encrypted using AES-GCM and a PBKDF2-derived key held in memory. Reloading requires the PIN again. Wrong PINs cannot decrypt records. Lock records hides the patient state; explicit deletion clears the vault and its PIN metadata. Demo role switching is not identity verification. Numeric PINs are not a production authentication system. No recovery is available; forgotten PINs require clearing site data and recreating the synthetic demo.

Only language, role and welcome preferences remain in localStorage. Dexie stores encrypted patient records, check-ins, replay settings and audit events. Caregiver-entered contact names and phone numbers are encrypted locally. Real patient import is not exposed. The seed is public synthetic data bundled with the app.

## Engine and tests

The port uses the frozen Python reference. Generated vectors live in ../docs/app/engine_test_vectors.json. They cover 1,366 days at two thresholds (2,732 comparisons). Provenance includes reference hashes and synthetic seed. Regenerate from the repository root with Python: `python app/tools/generate_vectors.py`. The original brief's supplied fixture was absent; this is explicitly a locally generated replacement. C++ parity was not rerun because Zig is unavailable.

`npm test` covers parity, calendar gaps, duplicate/conflicting input, device result preservation, crypto, migrations and atomic seed/deletion. `npm run test:e2e` covers offline reload, wrong PIN, ciphertext inspection, replay, deletion and accessibility. Set PLAYWRIGHT_CHANNEL=chrome to use installed Chrome. Set PLAYWRIGHT_BASE_URL to an existing production preview URL to skip starting another server.

See ../docs/app/PHASE_2.md for the detailed data/security contract. This establishes software parity, not clinical validity.

## Remaining external acceptance

Phases 1-9 have software implementations for the synthetic hackathon demo. Draft translations/audio still need human review, and the intended Android phone needs installation and hardware checks. No public deployment or physical Android installation has been performed.

## Accepted scope

Hackathon PWA, one Android phone with role switching, amulet included. Existing-chair platform and lap bar are called “check-in device” in the UI. No deadline or specific Android model has been provided.

## Phase 3 demo

Unlock and load the synthetic demo, then Home → My medicines or Daily questions. The tablet is explicitly a practice illustration, not a prescription. Try reminder now opens a foreground alarm; snooze lasts ten minutes, at most three times. Get help requires a two-second hold followed by a cancellable five-second countdown. Calls require a separate tap. Settings accepts encrypted family/ASHA contacts.

Voice commands → Install offline language pack → Start microphone. Repeat installation after selecting Hindi to add that language. English takes about 37.5 MB and Hindi 44.4 MB plus a shared runtime. The production preview already includes the archives. On a fresh source checkout, run `python tools/prepare_voice_models.py` before `npm run build`; or extract the separate voice-model bundle into the repository root. The Vosk voice flow requires the production service worker; use build + preview to test it.

Alarms require the app to remain open and awake. A missed practice dose queues a local notice; it does not send SMS. Read-aloud requires an installed local system voice. Physical Android installation and real-speaker accuracy remain unverified. See ../docs/app/PHASE_3.md for scope and acceptance details.

## Phase 4 demo

Settings → unlock/load demo → Family → select Demo elder 01. Switch 7/30-day trends, view adherence and open an alert. Care contacts and plan accepts a caregiver transcription of an existing clinician plan and an elder phone number; the transcription is explicitly unverified. Responses 1/2/3 save locally with checklist steps and an audit entry. The device alert remains unchanged.

Medicine manager → Add medicine → manually copy a prescription, schedule and counted stock; optional tablet/prescription photos are encrypted locally. Switch to Saathi → My medicines → select a scheduled dose and Taken. Family mode then shows stock and adherence updates. Refill adds tablets; archive retains taken-dose history.

The selected historical day and demo clock are explicit. Foreground reminder checks run each visible minute using India time, or at the chosen Family demo time. Closed-app alarms and remote delivery are not available. Nearby facility data is unconfigured; reports arrive in Phase 7. See ../docs/app/PHASE_4.md.

## Phase 5 demo

Select ASHA after unlocking. The list prioritizes red/amber and overdue check-ins; village and house can be entered in a visit. Complete observations and medicine checks, choose an outcome, then Save visit and mark seen. The visit persists offline, and Family alert detail shows Seen by ASHA without changing the engine light.

Review the referral preview, consent, then Download PDF or Show referral QR. Both work offline; Hindi shaping is preserved in image-based PDFs. The list also includes a seven-day PHC summary with PDF and explicit SMS draft. Check the PHC number before opening the composer. Dictated notes use the existing optional offline language packs.

Local follow-up closure is recorded, while hardware delivery remains pending. Swelling options are illustrations rather than validated photo examples. See ../docs/app/PHASE_5.md for the full data/export contract.

## Phase 6 demo

Choose Doctor, enter a demo doctor name, and open a patient. Timeline filters recorded events, Family responses, ASHA visits, dose records, labs and notes. Assign a PHC from the patient record to enable PHC list filtering.

Care plan accepts manual amber/red instructions, target dry weight, daily fluid limit, salt advice and follow-up date. Confirm to save a dated version. Family/ASHA see the plan locally; Saathi can read it using installed local speech. More sensitive changes T from 6.5 to 5.5 with named audit; the what-if preview does not overwrite the recorded light.

Lab results and Consult notes are dated, attributed, encrypted and append-only. Notes are shared with Family/ASHA. Reviewed photo references accepts consented, human-reviewed grade examples; uploaded images appear in the ASHA form. Save encrypted visit draft now supports offline recovery before final submission. See ../docs/app/PHASE_6.md.

## Phase 7 demo

Choose Family, ASHA or Doctor and open Reports. Generate any of nine English/Hindi PDF formats, restore encrypted saved PDFs, export FHIR R4 JSON, share a file or open the print viewer. Offline QR transfer compresses report data and charts into animated frames; the receiver checks integrity and regenerates the PDF. Camera scanning has a paste fallback. See ../docs/app/PHASE_7.md for scope, security and verification.


## Phase 8 demo

Open Device connection after unlocking. Choose Built-in simulator, create a separate linked demo elder, connect and request history. Review the received IDs/dates before saving. Worsening and Recovery scenarios replay frozen-engine fixture messages. Bluetooth LE and 115200-baud Web Serial use the same validated protocol; availability and USB-OTG support depend on the browser/device. Health events persist encrypted and appear in device reports. See ../docs/app/PHASE_8.md for firmware build, transport limitations and tests.


## Phase 9 demo

Welcome and Settings offer all ten specified UI languages. Additional languages are marked machine-translated / needs review. Settings -> Display and audio provides light/dark/high-contrast themes, larger text and Hindi offline audio. Elder mode automatically uses high contrast. 48 pre-generated Hindi clips are bundled; unrecorded dynamic clinical text still needs an installed local voice. Recognition and PDFs remain English/Hindi.

Verified: 108 unit tests, 27 browser tests; mobile Lighthouse 13.5 performance 93 first launch / 99 returning Hindi home, accessibility 100. A separately labeled legacy Lighthouse 11.7.1 PWA audit scores 100. Core precache is about 3.32 MiB, excluding optional ASR runtime/models. See ../docs/app/PHASE_9.md for methodology and limits.

