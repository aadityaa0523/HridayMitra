# Phase 5 - ASHA mode

Implements the ASHA milestone for the accepted synthetic, single-phone hackathon PWA.

## Visit list

Settings -> unlock/load demo -> ASHA. The selected historical replay date is explicit. Latest usable readings at or before that date determine priority: red, amber, missed check-in over one calendar day, then green/learning. Future rows and guest readings are excluded. Cards show village/house, reasons and days since the last recorded ASHA visit. A village filter includes an explicit unknown-location choice. Location, house and PHC phone can be recorded from the visit screen, encrypted locally.

## Offline visits

The form records optional paired BP values and weight, required swelling grade 0-3, breathlessness at rest, extra pillows, yes/no for each applicable medicine, optional resized ankle photo, editable typed/dictated notes, outcome and referral reason. A referral reason is required for referred outcomes. No symptom or outcome is defaulted. BP plausibility checks are input validation, not clinical interpretation. Visit measurements remain separate observations; the frozen check-in result is preserved.

Voice notes reuse the existing English/Hindi Vosk packs, work locally after installation and stop on close/page exit, language change or a bounded one-minute session. Notes remain editable and are saved only on visit submission. Photos use the same 5 MB input limit and 640px local resize as medicine photos; metadata is not retained. Unsaved form drafts are not persisted.

Grade options use labeled schematic illustrations. Clinically validated swelling-photo examples were not supplied and are not fabricated; the UI directs trained workers to use their training. Reviewed training-photo assets remain a content task. The form records a grade and does not assess or diagnose from an image.

A visit UUID makes repeated submission idempotent. Visit, linked alert seen marker, local stop metadata and a pending outbox instruction are written in one encrypted transaction with audit. Existing Family response/checklist data is retained, including when Family later records another response. The device's red light remains unchanged.

## Close the loop

Saving marks the linked latest amber/red alert Seen by ASHA and records escalation stopped locally. Family alert detail exposes this acknowledgement. A stop-escalation instruction is queued locally for future hardware/sync integration. Nothing is claimed to have reached the stool/PHC; this PWA cannot stop an unconnected device's escalation. Selecting Called 108 only records an outcome, while an explicit dialler link initiates calling.

## Referral and weekly reports

Referral preview includes visit observations, medicine checks, referral reason, notes and a 30-day summary of available gated readings, ranges, amber/red counts and latest reasons. The summary ends at the visit date, even when viewing an older visit. Weekly reports use exactly seven calendar days ending on the replay date and respect the village filter. Counts distinguish visits, unique visited elders, red check-in days, unique red elders, referrals and recorded 108 calls.

A consent checkbox gates export. PDF generation and QR encoding run in the browser, including after an offline reload. Hindi pages use browser-shaped canvas text embedded into A4 PDFs. This preserves conjuncts but produces image-based, non-searchable PDFs; they are not signed clinician documents. PDF and QR exports record their SHA-256 and channel in encrypted report metadata/audit. Exported files are outside the vault; deleting local records cannot remove copies already downloaded/shared.

QR contains a short plaintext referral summary, not the PDF or a hosted link. Its privacy implications are shown before revealing it. Native file sharing is offered where supported, with download as fallback. A weekly SMS link opens an explicit composer draft to a reviewed PHC number and records an audit entry; cellular SMS may work without internet. Sending and delivery cannot be confirmed by this app. No third-party message is sent by the implementation tools.

Libraries: jsPDF https://github.com/parallax/jsPDF and node-qrcode https://github.com/soldair/node-qrcode . The report runtime is precached for offline export; the shell precache is now about 1.6 MB, with voice models still optional.

## Verification and remaining scope

Unit tests cover encrypted/idempotent saving, validation, medicine ownership/completeness, priority and village filtering, future-data exclusion, seven-day counts, referral/QR content and export metadata. Browser coverage includes offline persistence and Family acknowledgement, Hindi PDF/QR after offline reload, weekly PDF/SMS draft, village filtering and axe accessibility. PDFs are rendered with Poppler and visually inspected.

Physical Android usability, native share/SMS behavior and real-speaker dictation accuracy remain unverified. No public deployment, actual hardware escalation control or remote messaging is provided. Full clinical report formats and FHIR remain Phase 7; Doctor mode is Phase 6. The repository's pre-existing dependency advisories (Vitest tooling and Vosk's bundled uuid) remain; new PDF/QR dependencies did not add the audit findings.

Final verification: 87 unit tests and all 15 browser tests pass; production build passes. The visit form and Hindi referral screen have zero axe violations in the tested WCAG A/AA checks. The final Hindi referral and English weekly PDFs each render as one A4 page and were visually checked with Poppler. Mobile English/Hindi list and form screenshots were inspected.

## Completion addendum with Phase 6

The ASHA form now has explicit encrypted draft save/recovery and a reviewed-photo upload library managed in Doctor mode. Reviewed images replace the relevant grade illustration and include source/reviewer attribution. Final visit saving clears its draft in the same transaction. Offline ASHA microphone startup and stop-on-navigation are tested. Actual clinical photo approval, phone validation and hardware delivery still require external inputs; see PHASE_6.md.
