# Phase 9: hackathon polish

Scope remains the synthetic, offline PWA. This milestone does not turn demo roles into verified professional identities, clinically validate the engine, or certify a medical device.

## Languages

All ten specified JSON files are present: en, hi, ta, te, kn, mr, bn, gu, ml and or. Each contains the same 611 keys, intact interpolation placeholders and needs-review metadata. English/Hindi retain the authored MVP copy. The eight additional files were machine translated from public English UI copy and are visibly labeled Needs review. No patient records were sent for translation.

Welcome and Settings allow all ten languages, with persistence after offline reload. Script fonts are bundled locally. Language bundles are loaded on selection and precached with the shell. Advanced Reports and Device connection use the additional translated static-copy namespace; dynamic device/clinician text stays as originally recorded.

Speech recognition remains English/Hindi. Unsupported languages cannot silently select an English model or intent dictionary. Clinical PDF output remains English/Hindi and the draft-language notice says so. Machine translation is not a clinical language review. PDF support and voice models for the other scripts have not been added.

## Hindi audio

48 pre-generated synthetic Hindi MP3 clips are bundled under public/audio/hi, with a source/review manifest, exact text, byte lengths and SHA-256 hashes. They include greeting/status, daily questions, medicine/SOS prompts, monitoring disclaimer, historical-demo announcement, check-in instructions and number words 0-10. They are synthesized speech, not human recordings, and require listening review before public use.

The app prefers an installed local system voice. Without one, exact Hindi prompt text or a sequence of entirely known prompts can play the corresponding local clips. Unknown clinician instructions, drug names, numeric readings and delivery claims are never replaced with generic speech. The visible notice asks for a local voice or caregiver help when the exact message is unavailable. English still requires a local system voice; Hindi has the MP3 fallback.

Settings -> Display and audio offers a Hindi greeting test and Stop audio. Playback stops on navigation, language changes, dialog exit and page hide. Voice-command handling suppresses both native TTS and MP3 playback echoes, while retaining cancel. Opening Daily questions reads the first question; the second question and save confirmation use the existing audible workflow.

All 48 files were decoded with ffprobe (0.720-5.448 seconds each). Browser tests decode and play audio with networking blocked and no system voices. This does not establish human intelligibility or real-speaker recognition accuracy. Audio authoring and draft translation regeneration are in tools/prepare_polish_assets.py; runtime playback/translation never calls the generation service.

## Accessibility and display

Light, dark and high-contrast display choices persist locally, with high contrast automatic in elder mode. Larger text persists across reload. Focus indicators cover keyboard-operable controls; buttons have enlarged touch targets. Review notices remain readable in selected language buttons. Reduced-motion preference disables animation; green orb motion only runs when motion is allowed. Script text wraps at phone widths.

Tests run axe WCAG A/AA, including 2.2 tags, across all ten draft-language Settings screens, and check no serious/critical findings there. Existing care/device/report workflows retain their axe checks. Dark Settings passes the full tested AA set; elder home with enlarged text, including seeded red status, passes the enhanced contrast check. Automated checks do not establish complete WCAG conformance, screen-reader usability or successful unassisted elder use.

## Performance and PWA

Larger role screens and report/QR code load on demand. All are still available offline through precaching. Draft-language resources load on selection. The optional Vosk runtime and recognition model packs are kept separate from the core install cache.

The final core Workbox precache is 95 entries, about 3.32 MiB, including ten UI languages, script fonts and 48 Hindi clips. The optional ASR runtime is about 5.8 MB and the separate English/Hindi model archives are about 82 MB combined; these are not part of that core-cache measurement. This is not a claim that the complete optional voice distribution is below 5 MB.

Actual Lighthouse 13.5.0 results from local production preview:

| Scenario | Performance | Accessibility | Best practices | SEO |
|---|---:|---:|---:|---:|
| First-launch welcome | 93 | 100 | 100 | 91 |
| Returning Hindi elder home | 99 | 100 | 100 | 91 |

Mobile configuration uses simulated 150 ms RTT, 1638.4 Kbps throughput and 4x CPU slowdown. The returning-home run retains normal local preferences/cache after its setup visit; it is explicitly not a cold first load. These are laboratory measurements, not Android field performance.

Lighthouse removed its PWA category in version 12. To evaluate the brief's original PWA >=95 criterion, a separate isolated Lighthouse 11.7.1 audit was run: PWA 100, no failed PWA audits. The legacy dependency was not added to the application. Current scores and legacy PWA results are labeled separately. Reference: https://developers.google.com/speed/docs/insights/release_notes.

Run tools/audit_mobile.mjs against the production preview for the two modern reports. Browser tests cover manifest/icons, controlling service worker, full offline role switching, draft-language restore and Hindi audio. No Android device was attached when adb devices was checked; installation and operation on the intended physical phone remain unverified. Use HTTPS or an appropriate USB development connection for phone install/hardware tests.

## Validation and dependencies

108 unit tests pass, including full ten-language key/placeholder parity, clip hashes/matching and unsupported recognition-language rejection. Existing frozen engine fixtures continue to pass. The browser suite contains 27 scenarios, including three Phase 9 scenarios.

Vitest was upgraded to 5.0.5 to resolve the prior critical development-tooling advisories. The final npm audit reports no high/critical advisories and two moderate findings associated with the optional Vosk/UUID dependency chain. No broad forced dependency rewrite was applied to the working ASR runtime.

## Remaining external acceptance

- A speaker/clinical reviewer must check the eight translated drafts and synthetic Hindi recordings.
- A physical Android phone must verify installation, local voices/audio, real speech, battery/background limitations and hardware links.
- Native remote delivery, server synchronization, production authentication and clinical validation remain outside the accepted hackathon demo. The app still labels queued messages as not sent.
