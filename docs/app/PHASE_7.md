# Phase 7: offline reports and transfer

Accepted scope: synthetic hackathon PWA, English/Hindi, one Android phone with role switching. No public deployment, clinical validation, authenticated clinician signature, PHC server or hardware telemetry is implied.

## Demo

1. Settings: unlock/load the synthetic demo and select a replay day. Choose Family, ASHA or Doctor. Use Reports above the page content. The globally selected elder and replay date are shown.
2. Select one of nine report formats and enter the generating person's name. Generate and save PDF stores the PDF and its structured source in the encrypted reports collection, with SHA-256 and a named audit entry.
3. Review the preview, enable export, then download, use native file sharing or open the PDF viewer to print. Android sharing/printing depends on installed apps. Load saved reports restores a previously generated PDF after unlock and verifies its hash.
4. FHIR R4 JSON exports the selected day for Daily, otherwise the previous 30 calendar days. It exports measurements rather than the PDF, dose history or clinical interpretation.
5. Offline QR transfer sends a gzip-compressed structured report including chart points, not the original PDF bytes. Scan all animated frames on a receiving phone, or paste individual frame texts. The receiver verifies SHA-256, previews the document and regenerates a PDF. Received documents are never merged into patient records. The original PDF's header QR is only an identifier, not a transfer frame or server download URL.
6. One-phone demonstration: pause frames, copy each frame text, open Receive offline QR report and paste each frame. Reordering and identical duplicates are supported. Reset receiver before a different transfer.

## Formats

- Daily card: light, reasons, six clinical measurements and baseline bands, scheduled/taken/pending/missed medicines.
- Weekly summary: check-in count, dated light strip, weight chart, adherence and alert responses.
- Monthly report: six trend charts (weight, leg/chest impedance, pulse, oxygen saturation, night respiratory rate), baseline legend, monitoring summary, alert episodes, ASHA findings and labs. Charts occupy the first page; details follow.
- OPD: current recorded light, reasons, 30-day trend thumbnails, medicines/adherence, symptoms, labs and ASHA observations.
- Alert episode: latest recorded alert within the window, trigger, reasons, response/checks, ASHA status, locally queued delivery timeline and recorded outcome. Pending/not-sent is never described as a delivered message.
- Medication adherence: per-drug colored daily dose cells, explicit taken/missed/pending/unscheduled legend and recorded missed-dose list.
- Lab history: reported values, author, original units and per-test/unit sparklines. Units are not silently converted or mixed.
- ASHA referral: reason, outcome, contact, observations and 30-day monitoring trends.
- Device health: explicit unavailable self-tests, battery, signal and service history until a real adapter supplies them.

Reports paginate rather than omit long observations, many medicines or long histories. Intended standard templates are one page, except the two-page monthly report; additional pages may be necessary for large records. Every page repeats the patient/date/author/report-ID header and identifier QR, with the required monitoring disclaimer and Page x of y footer. Age and ABHA remain not recorded because the synthetic profile does not contain them. PDFs are raster pages so browser shaping preserves Devanagari; they are not searchable or accessible tagged clinical documents. The in-app preview remains selectable text.

## Data contract

All builders filter by patient and replay cutoff. Clinical charts use engine-gated values; rejected guest/plate readings remain missing. Baseline uses calendar days t-35 through t-7, at least six values, median +/- max(1.4826 MAD, frozen engine floor). This is a descriptive final-day personal band, not a diagnostic normal range and not a rolling population reference. Null readings break lines rather than connecting over gaps. Pending doses are not counted as taken or automatically called missed.

FHIR uses a collection Bundle containing Patient and final Observation resources. LOINC 29463-7, 8867-4, 59408-5 and 9279-1 follow engine/product.py; leg/trunk 5 kHz impedance remains text-coded. UCUM units, date precision, patient references and synthetic provenance are included. Export omits null/rejected values and uses gated readings to avoid exporting guest data. This is a local R4 export, not ABDM certification or a validated receiving-system integration. References: https://hl7.org/fhir/R4/observation.html and https://hl7.org/fhir/R4/bundle.html.

QR protocol v1: JSON frames with report UUID, SHA-256 of compressed bytes, zero-based index, frame count and base64 chunk. Chunks are at most 650 characters, at most 120 frames. Expanded data is capped at 240 KB; malformed, mixed-session and conflicting duplicate frames are rejected. SHA-256 detects corruption, not sender authenticity. Transfer is unencrypted outside the vault; the UI makes this explicit. Camera decoding uses BarcodeDetector where available, with manual paste fallback. No network upload occurs.

## Verification and limits

Unit coverage includes nine formats, patient/date isolation, baseline window, missing/device data, LOINC mapping, null/guest filtering, compression roundtrip, duplicate/reordered frames and tamper rejection. Browser coverage exercises Hindi PDF downloads offline, native-share API stub, multipart paste roundtrip, encrypted PDF recovery, responsive layout and accessibility. Physical Android share sheets, camera optics, printing and interoperability with a live PHC remain device/integration checks.
