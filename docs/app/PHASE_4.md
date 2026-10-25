# Phase 4 — Family mode

The accepted scope remains a hackathon PWA on one Android phone with role switching, synthetic history and the amulet included. Phase 4 implements milestone 4: elders list, detail and trends, alert checklist/actions, medicine manager and reminders.

## Family workflows

Unlock and load the demo in Settings, then select Family. The household supports up to four synthetic elders. Added elders intentionally reuse the same public fixture; medicines, contacts, dose records and alert responses are patient-scoped. Selection persists encrypted and keeps the shared replay position.

Each card shows the selected historical day's light, check-in availability, scheduled/taken doses and alert response. Elder detail includes gated readings, five 7/30-day charts (weight, leg reading, pulse, oxygen and night breathing), a 30-day adherence calendar and a check-in streak. Charts exclude future dates, preserve missing days, and offer accessible value tables. No schedule is displayed as unknown rather than perfect adherence.

Amber/red alert detail uses the recorded engine result, plain-language reasons and a contextual explainer. Responses 1/2/3 preserve the device light and never dismiss a red alert. Checklist selections, response and pending outbox entry are saved with an audit entry. Patient-is-fine is a caregiver response, not a clinical clearance.

No clinician plan is fabricated. A caregiver may transcribe an existing plan and elder phone number; the UI explicitly labels the text unverified and awaiting clinician review. The checkboxes save with the alert response. Plan authoring/review by a doctor remains Phase 6. Dialling always requires an explicit link tap.

## Medicines and reminders

Manual prescription entry includes name, strength, 1–6 unique daily times, prescribed tablets per dose, food instructions, stock, optional tablet and prescription images. Photos are resized to a 640px maximum dimension and stored encrypted locally; supported input is JPEG/PNG/WebP up to 5 MB. There is no OCR or upload.

Schedules begin on the selected replay day and do not backfill earlier doses. Saathi mode displays the recorded name, photo, strength, time and food instruction. With several doses, the elder chooses one. Tap/voice confirmation is stored per scheduled dose; marking it taken again is idempotent. Dose completion and stock decrement are one encrypted transaction. Insufficient stock blocks confirmation until reconciled through the manager.

Refill days mean whole days at the recorded schedule. Refill adds counted tablets, without inferring actual consumption. Archive stops that schedule from the selected day; already-taken doses remain visible. Correct a schedule by archiving and adding the corrected prescription.

The selected historical day has a clearly labeled demo clock. The Family reminder button evaluates due doses and check-ins at a chosen time. A missing/guest-only check-in at or after 11:00 queues one local notice. While the app remains visible, a minute timer also evaluates the selected day using India time. This intentionally simulates the clock against replay history; it is not today's real patient monitoring.

Due medicine alarms open in Saathi mode. They support 10-minute snoozes up to three times; expiry records a missed dose and local pending notice. Practice medicine remains available when no actual schedule is recorded. Reminders are not guaranteed when the app is closed, asleep or suspended.

## Delivery and limits

All records and audit entries use the existing encrypted vault. Reload requires the vault PIN. Roles are demo views rather than verified identities. Responses and reminder notices stay in the local outbox, explicitly not sent. Device/ASHA delivery awaits hardware/sync integration; no SMS or remote notification service is claimed.

A nearby facility directory is explicitly unconfigured because no village/location and verified facility data were supplied. ASHA/family contacts and 108 dialler links remain available. Full PDF/report sharing is Phase 7. Physical Android testing remains outstanding.

## Verification

Unit tests cover household limits and isolation, replay position, calendar windows and streak gaps, idempotent stock changes, archive history, invalid inputs/photos, patient ownership, alert checklist/response persistence, unchanged device results, reminder boundaries and missed-dose snoozes. Browser tests cover Family-to-Saathi medicines, reminders, stock, offline reload, plan/checklist responses, red alert retention, a second elder, Hindi and accessibility.

Verified: production build passes; 80 unit tests pass; full 12-test browser suite passes. After the final plan-display correction, the seven affected Family/Saathi browser tests were rerun. Mobile English/Hindi screenshots were visually inspected; Family detail and alert screens have zero axe violations in the tested WCAG A/AA checks. These are Chrome simulations, not physical Android validation.
