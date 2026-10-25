# Phase 2 implementation contract

This phase supports a single-phone, synthetic-data hackathon demo. It is not a deployed clinical record system.

## Engine and fixtures

The TypeScript implementation in `app/src/engine/` ports `engine/alert_engine.py` with CUSUM disabled. Gates use valid readings in the preceding seven calendar rows, preserving reference behavior rather than interpreting the brief as seven non-null readings regardless of elapsed time. Thresholds 6.5 and 5.5 are supported by the pure engine; the demo uses 6.5.

`engine_test_vectors.json` is generated locally by `app/tools/generate_vectors.py`. It is not the missing author-supplied fixture. It records hashes of the reference source and source CSV, the deterministic synthetic seed, all inputs, scores and expected lights. The generator calls Python, never the TypeScript implementation. Regeneration requires the repository's Python dependencies.

Coverage: five generated histories of 164 days (820 days), five edge histories (275 days), and five original repository histories (271 days). Both thresholds are checked, totaling 2,732 patient-day/threshold comparisons. This establishes software parity, not clinical accuracy. C++ parity could not be rerun in this environment because the Zig compiler package is unavailable.

The app bundles only one generated history, without its expected outputs. It computes results using the port, encrypts the stored history, and replays selected dates. All views label these as historical simulated measurements, never today's real health. Missing raw fields remain null; device and amulet connections remain disconnected.

Calendar normalization inserts empty days, sorts dates, deduplicates byte-equivalent event replays and rejects conflicting same-day records or mixed patients. Corrections require an explicit future workflow. Device-authored results are preserved by the daily ingestion adapter; missing device results are rejected. Raw inputs and gated scoring values are kept separately.

## Encrypted storage

Dexie schema v1 includes metadata and encrypted collections for patients, contacts, check-ins, medicines, doses, visits, labs, notes, reports, audit and settings. Version 2 adds alerts and outbox. The migration is tested for preservation of existing ciphertext. Future feature schemas will add typed domain models to currently reserved collections.

AES-256-GCM uses a random 96-bit IV per write and authenticated data binding the envelope version, collection and record ID. PBKDF2-SHA-256 uses 310,000 iterations and a random 128-bit salt. Keys are non-exportable and held only in memory. PIN input is cleared after submission. Reload, explicit lock and pagehide end the unlocked session. Decryption/tamper failures lock the vault. Ciphertext and audit updates are committed atomically, after encryption completes outside the IndexedDB transaction.

Unencrypted metadata: database/table structure, schema/envelope version, IDs, IVs, ciphertext lengths, salt and key-derivation parameters. Demo IDs include dates; do not interpret this schema as hiding traffic or record-count metadata. PINs and keys are not stored. A short numeric PIN is vulnerable to offline guessing despite key stretching; this is not production-grade identity verification or account security. No PIN recovery or change workflow is implemented in this phase. Forgotten PINs require clearing site data and recreating the synthetic demo.

The bundled seed itself is public synthetic data. Encrypting its stored copy demonstrates storage behavior; it does not make the public sample secret. No real-patient entry or import is offered.

## Consent and audit

A caregiver records consent for synthetic local storage before creating the vault. Audit events cover consent, seed loading and replay changes. These are encrypted local activity records, not cryptographically append-only or server-backed audit trails. Role switching remains a demo; it does not verify clinician identity. No clinician plan is seeded, and no default medication instructions are imported from the Python product layer.

## UI flow

Settings → enter and confirm a 6–12 digit PIN → agree to synthetic storage → Create demo vault → Load five-month demo. Choose a date, step forward/back, or jump to the next actual engine-produced red day. Home shows the selected date, reasons, raw/gated distinction where relevant, amulet readings, score-derived status and absent-plan notice. The same patient summary is available in caregiver role previews.

Explicit Lock records clears the displayed record state. Reload shows records locked, not a healthy result. Unlock works offline after the PWA shell is cached. Delete demo data requires an explicit checkbox and clears all collections plus the vault metadata. Language/role preferences remain outside the vault.

## Remaining work

Phase 3 introduces elder medicine workflows, questions and offline command recognition. Later phases implement real caregiver flows, verified roles, plan editing, PDF/FHIR exports, actual hardware ingestion and durable remote communication. Physical Android validation, production security review and clinical validation remain outstanding.
