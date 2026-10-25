# Phase 3 — elder routines and voice

Phase 2's 43 unit checks were rerun before implementation. Its software acceptance criteria are met; physical Android validation and optional C++ parity remain unperformed. This phase retains the single-phone synthetic hackathon scope.

## Delivered workflows

- Practice medicine card with explicit illustration/non-prescription wording. No drug name, dosage or treatment instruction is invented. Taken is stored encrypted with patient, replay date, timestamp and tap/voice provenance. Repeated confirmation is idempotent.
- A foreground reminder demonstration, full-screen alarm, repeated spoken prompt when a local TTS voice exists, vibration, up to three ten-minute snoozes and a local pending caregiver notice when the final snooze expires. The notice is not represented as delivered. Reload recovers persisted dose state when the vault is unlocked.
- Two daily questions, large Yes/No buttons, voice answers, encrypted persistence and confirmation. Answers belong to the selected synthetic replay day and are intentionally stored separately from the recorded simulated device result; they do not silently rewrite engine history.
- Encrypted family1/family2/ASHA contacts entered by a caregiver in Settings. Explicit dialler links require user action and cellular service; no placeholder number is seeded or called.
- SOS requires a two-second hold (pointer or keyboard) or an exact voice intent. It then offers a cancellable five-second countdown, followed by contact choices. No automatic dialling, unattended escalation, GPS collection or SMS sending is claimed. The emergency dialler link remains available.
- English and Hindi push-to-talk with Vosk. One optional model pack is installed per language, then recognition stays local. English-India and Hindi archives come from Alpha Cephei's official model catalogue, are repackaged for vosk-browser and verified against the local manifest hash on installation.
- Explicit optional online browser speech fallback, with notice that the browser provider may receive audio. It is never silently selected.
- Intent lists include six or more phrasings per supported intent/language. Exact matching is required for dose changes, yes/no, calls and SOS. Fuzzy matching is limited to navigation/read actions, with negation rejection and an ambiguity margin. Voice dose completion additionally requires contextual confirmation.

## Offline assets

Run `python app/tools/prepare_voice_models.py` from the repository root before building a distributable that serves voice packs. It downloads official zip files and emits `app/public/models/en.bin`, `hi.bin` and `manifest.json`. The `.bin` extension prevents HTTP auto-decompression of the gzip archive. Explicit directory entries preserve extraction permissions. Model files are excluded from git; the preparation script and manifest are versioned. Source: https://alphacephei.com/vosk/models . Model licenses: Apache-2.0. Runtime source: https://github.com/ccoreilly/vosk-browser .

English-India archive: about 37.5 MB. Hindi archive: about 44.4 MB. The optional Vosk runtime is about 5.8 MB uncompressed. Neither model nor runtime is part of the initial shell precache. The UI downloads a model on request and caches the runtime separately. The base application remains under 1 MB of precached resources. Speech assets add to device storage, and browser eviction remains possible.

Read-aloud uses matching local Web Speech synthesis voices. English/Hindi speech playback therefore needs an installed device voice; model packs provide recognition, not synthesis. Human-recorded fallbacks remain Phase 9 work. No guarantee of voice quality on rural accents or a specific Android phone is implied by software tests.

## Privacy and lifecycle

The microphone is user-initiated and stopped on close, language change, page exit, session lock or after a bounded listening session. Model-loading cancellation prevents delayed activation after close. Models run in a worker. Runtime logging is restricted. Transcripts are temporary UI state and are not written to the patient database. Installed language packs contain public model weights, not patient data.

Routine writes share the encrypted vault and audit mechanism. No treatment decisions or changes to the frozen alert engine are introduced. Caregiver roles remain demo views rather than verified identities. The contacts form is the first optional user-entered contact data; it is encrypted locally and never uploaded by the app.

## Acceptance and limits

Unit coverage includes both phrase dictionaries, negation, consequential-command rejection, snooze boundaries, dose idempotency, wrong-patient rejection and encrypted routine/contact persistence. Browser checks cover routine persistence after offline reload, SOS short-press rejection/countdown cancellation, reminder snoozing, and loading both Vosk models without network access using a simulated microphone. These do not replace actual speech accuracy and usability testing on the user's Android device.

The PWA cannot guarantee alarms while closed or asleep. It cannot detect unanswered calls and automatically dial the next person. Family/ASHA/doctor workflow completion, real prescriptions and tablet photos, full reporting, hardware pairing, educational media and reviewed recordings belong to later phases.

Verified in this session: production build passes; 74 unit tests pass; all 8 browser tests pass. The strengthened voice test also passes after a fully offline page reload for both languages. Chrome uses a simulated microphone; actual spoken-word accuracy, Android install, and background behavior have not been validated on a physical phone.
