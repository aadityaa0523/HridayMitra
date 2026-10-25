# HridayMitra phase plan (status on 24 Oct 2026)

| Phase | Work | Tier | Status |
|---|---|---|---|
| 1 | Alert brain, four PS measures, calibration, frozen-threshold testing | Must | ✅ Done. Engine v2 frozen (T = 6.5): held-out sensitivity 66%, specificity 99.8%, lead 2 days, 0.03 false alerts per patient-month |
| 2 | Stress tests, assumption sensitivity, care-loop simulator, ablations | Differentiator | ✅ Done (`reports/phase2_summary.md`) |
| 3 | Circuit random variation, KiCad schematic from code, cost simulation | Must + differentiator | ✅ Done. Trunk paths, Monte Carlo (R8/R9 → 10 MΩ), jewellery, mains hum; KiCad schematic from code (`tools/make_schematic.py`: ERC 0 violations, netlist path check, values = LTspice); block diagram (`docs/block_diagram.png`); cost Monte Carlo (`tools/cost_sim.py`: build cost ₹4,188–4,343, always under ₹5,000). Remaining circuit items belong to Phase 7 (Wokwi) and the team (bench vs simulation) |
| 4 | Demo with three views and fault injection | Must | ✅ Done: `demo/app.py` (patient light + voice in English/Hindi/Tamil, family SMS, ASHA/doctor trends, 4 break-it switches) and `engine/signals.py` (raw → numbers, 7 tests) |
| 5 | Traceability matrix, FMEA, assumption ledger, dataset/model cards | Differentiator, cheap | ⚠️ Dataset card only (`data/processed/DATA.md`) |
| 6 | Report, pitch, user journey, GitHub polish | Must | ⚠️ Public repo live: https://github.com/aadityaa0523/HridayMitra (CI green). Left: report, pitch, user journey |
| 7 | Wokwi, all 15 BIDMC records, ML comparator, multilingual audio, expert outreach | If time allows | ⚠️ BIDMC 3 of 15 records |

Not in the original phases, but needed:
- **Raw-signal module**: raw waveform → impedance (Goertzel), PPG → pulse and SpO₂, quality checks. The PS asks for "software that turns raw signals into alerts". Fits with Phase 4.
- **ESP32 firmware** for the physical build (team needs it).

Team-only tasks: real price quotes, physical build, bench-versus-simulation check, backup video.

Live progress bars: `python tools/progress.py` (writes `docs/progress.html`).
