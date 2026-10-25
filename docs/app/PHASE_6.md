# Phase 6 - Doctor mode and Phase 5 completion

Accepted scope: synthetic hackathon PWA, one Android phone with demo role switching and the amulet included. No authenticated professional identity or real patient import is introduced.

## Doctor workspace

Unlock and load the demo, then choose Doctor. The patient list filters by current PHC assignment, including an unassigned group. Each patient opens a record with timeline, plan, labs, consult notes and reviewed-photo references. PHC name/phone are editable with the entered doctor's name and audit. Names are demo provenance; the app does not verify credentials.

The timeline includes recorded check-ins, alert reasons, historical Family responses with actor/timestamp, ASHA visits, scheduled medicine taken/missed events, lab values, consult notes, plan versions, sensitivity changes and queued delivery steps. It excludes dates beyond the selected replay day, filters by event type and loads 20 more events on request. Replay dates and actual phone recording timestamps are labeled separately. Pending delivery steps are never presented as delivered escalation messages.

## Care plans

The editor requires manually entered amber/red instructions and optionally records target dry weight, daily fluid limit, salt advice and follow-up date. Nothing is prefilled as a treatment recommendation. Saving requires an entered author and explicit review confirmation. A new immutable plan version and audit record are saved with the patient projection and pending device delivery entry in one encrypted transaction.

Plans take effect on the selected replay date. Earlier replay dates use the earlier version, preserving a legacy caregiver transcription when one existed. All roles use the same as-of projection. Family can change the contact number but cannot overwrite a Doctor-mode plan through the transcription form. Family/ASHA see the author, instructions and plan fields locally. Doctor notes are also shared locally.

Saathi read-aloud and the status voice intent include the applicable plan and recorded limits. The water intent can state the prescribed daily limit, while explicitly declining to infer remaining allowance because no intake log exists. Speech requires an installed matching local system voice. Original clinician-entered text is spoken as entered; it is not automatically medically translated.

## Sensitivity

Standard is the default, T=6.5. More sensitive stores T=5.5. The editor displays a separately labeled synthetic what-if result using the frozen calendar-aware engine and requires explicit confirmation. Each actual change records old/new setting, threshold, date and doctor name in audit; repeated saves of the same value are idempotent. Sensitivity versions also project as of the replay date.

No saved check-in result is recomputed or overwritten. In particular, a recorded device/simulator light remains authoritative. A pending outbox entry requests a future device threshold update. The app setting is available to future manual ingestion; live device application belongs to the hardware integration phase.

## Labs and notes

Manual lab entry supports Na, K, creatinine, eGFR, NT-proBNP and haemoglobin, with date, explicit test-specific unit, numeric value and author. Alternative supported units are stored as reported, with no automatic conversion, normal-range flags or treatment inference. Future dates relative to the replay cutoff are rejected. Lab results and notes are append-only, encrypted and audited. Corrections can be documented in a new entry; signed-record editing or deletion is not implemented. Notes are visible in Family/ASHA views and persist after offline reload/unlock.

## Phase 5 additions

- Explicit encrypted visit drafts can be saved with incomplete observations, restored after offline reload/unlock and cleared atomically when the final visit saves. Old medicine selections are reconciled with the applicable schedule on submission.
- A reviewed-photo library supports grade 0-3 images, source/permission reference, reviewer name and review/permission attestation. Uploaded photos replace schematic options for the relevant grade in ASHA mode and remain available offline. Removal is audited. Images use local resizing, MIME/size limits and vault encryption. No clinical grading photos are fabricated or seeded. Actual approved assets must be supplied by the training team; the app records the uploader's review assertion, not independent validation.
- ASHA dictation startup and stop-on-navigation are tested with networking disabled and a simulated microphone. Actual speaker accuracy remains unverified.
- A pending plan/response no longer produces a false practice-medicine missed notice. Only the corresponding missed-practice-dose event triggers that banner.

## Remaining external checks

No accessible ADB command or connected phone test session was available here. Physical Android installation, device TTS, actual dictation accuracy, native sharing and SMS compose/delivery require the user's phone. Existing local follow-up closure remains pending device delivery; an unconnected stool's escalation cannot be stopped by this PWA. Hardware integration is Phase 8. The clinical review of uploaded photos and instructions is a human content responsibility.

Full report types, Hindi clinical document formats and FHIR are Phase 7. Existing ASHA referral/weekly exports continue to work offline.

## Final verification

Production build, 94 unit tests and all 20 browser tests pass. Browser coverage includes Doctor plan/sensitivity persistence after offline reload, shared notes/plan visibility, PHC filters, labs and timelines, restored ASHA drafts, uploaded references, offline dictation lifecycle, complete ASHA observations in the Doctor timeline and a stubbed native file-share handoff. The existing ASHA offline Hindi PDF/QR and weekly export tests also pass. Doctor plan/timeline and Hindi lab screens were visually inspected at phone size. Axe checks report zero violations in the tested Doctor/ASHA/Family views. Actual speech accuracy and native Android behavior are not established by these simulations.
