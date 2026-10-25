# Bedside contactless sensing (mmWave/FMCW radar and bedside acoustic) for night monitoring of elderly heart failure patients at home

Research date: 2026-10-24. About 20 search and fetch calls. Many numbers below come from search-engine summaries of pages, not full-text reads. Where only a summary was seen, that is flagged.

## Q1. How accurate are low-cost radar vital-sign modules, and is there validation in elderly or heart failure patients? What is the basis of Sleepiz One+ clearance?

### Takeaway
No peer-reviewed validation of hobby-grade 60 GHz modules (Seeed MR60BHA1/MR60BHA2) for HR or RR against a clinical reference turned up. The few small independent tests disagree, and Seeed's own accuracy percentages don't even match each other. Regulated or research-grade bedside radars do reach about 1 breath/min respiratory-rate error in older adults and patients. Heart rate is harder, and none of them has been validated in heart failure patients at home specifically.

### Cited Findings
**Seeed MR60BHA1 / MR60BHA2 (company claims)**
- The Seeed wiki says heartbeat accuracy "up to 85%" and breathing "up to 90%". Its own spec table says 95% / 90%, and the product page says HR ≥95% / RR ≥90%. No reference method or test conditions are given, so these are company claims with inconsistent numbers. Breath and heart detection range is 0.4–1.5 m. — [Seeed wiki MR60BHA1](https://wiki.seeedstudio.com/Radar_MR60BHA1/)
- The MR60BHA1 is now marked discontinued by The Pi Hut (£43.90). The MR60BHA2 replaces it. — [The Pi Hut MR60BHA1](https://thepihut.com/products/mr60bha1-60ghz-mmwave-module-respiratory-heartbeat-detection)
- MR60BHA2 is a 60 GHz module on a XIAO ESP32C6 with ESPHome / Home Assistant firmware. Breathing and heartbeat are rated to about 1.5 m for a single stationary person in a controlled empty room. Presence is rated to about 6 m. — [OpenELAB MR60BHA2 listing](https://openelab.io/de/products/seeed-studio-xiao-60ghz-mmwave-human-breathing-heartbeat-sensor-mr60bha2); [Mouser MR60BHA2 kit](https://www.mouser.ca/new/seeed-studio/seeed-studio-mr60bha2-sensor-kit)
- Seeed's own datasheet describes the MR60BHA2 kit as an early-build beta product. — [Seeed datasheet 114993387](https://files.seeedstudio.com/Bazaar/product_pdf/114993387.pdf)

**Independent tests of the MR60BHA1 (small, conflicting)**
- A Metropolia UAS thesis compared the MR60BHA1 with an Apple Watch. It found "significant discrepancies" in HR and difficulty with RR accuracy, and said it is not recommended for medical device use. This is a student thesis with a non-clinical reference. — [Theseus: Analytical Comparison of 24GHz and 60GHz mmWave Radar Sensors](https://www.theseus.fi/handle/10024/886300)
- A Thai conference paper ("Breath & Beat") tested n=5 at 0.4–3 m against smartwatches and manual counting. It reported HR error under 2.5% on average and RR within 1 breath/min. The sample is tiny and the reference is weak. — [RMUTL e-research](https://e-research.rmutl.ac.th/conference/76c39d5c-f7c8-11f0-a1c2-506b8da904ed)
- A WashU NeuroTech Hub evaluated the module for non-human use. Detailed results were not seen. — [WashU neurotechhub](https://neurotechhub.wustl.edu/evaluating-a-60ghz-mmwave-radar-system)

**Bedside radar in older adults (peer-reviewed)**
- JMIR mHealth uHealth (Aug 2024, Surrey Sleep Research Centre) studied 35 community-dwelling adults aged 65–83 (mean 70.8). 57% had comorbidities, 49% had moderate-to-severe sleep apnea and 51% had some arrhythmia. Somnofy, a bedside Doppler radar, was compared with lab PSG on 17 nights. Breathing rate at 1-minute resolution: MAE 1.06 breaths/min, bias −0.47, 95% LoA −4.38 to 3.43, ICC 0.58. Whole-night average MAPE was 4.64% (ICC 0.82). Somnofy reports no heart rate. RR data were missing for about 32% of in-bed time, mostly during wake and body movement. Outliers came from participants with severe breathing disturbance or arrhythmia. — [PMC11387924](https://pmc.ncbi.nlm.nih.gov/articles/PMC11387924/)
- In the same study, the under-mattress comparators (not radar) did better on HR: Withings Sleep Analyzer MAE 2.08 bpm (LoA −9.27 to 8.54), Emfit 2.12 bpm. — [PMC11387924](https://pmc.ncbi.nlm.nih.gov/articles/PMC11387924/)

**Heart failure patients**
- UTS study with 50 systolic heart failure patients during overnight PSG. A bedside non-contact Doppler biomotion sensor tracked breathing rate closely. Comparing two rate-scoring schemes flagged central sleep apnea / Cheyne-Stokes sections with 71% sensitivity, 88% specificity and 86% accuracy. Only the abstract summary was seen. — [UTS OPUS 10453/125882](https://opus.lib.uts.edu.au/handle/10453/125882)
- No radar study that predicts HF decompensation at home was found. The closest are: a single-case report (a 91-year-old followed for a year with an ambient sensor; rising RR and HR before decompensation, analyzed retrospectively) ([PMC7884343](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7884343/)); a 2017 under-mattress piezo study where RR was the strongest risk-adjusted associate of HF readmission ([Bennett et al. 2017, J Telemed Telecare](https://doi.org/10.1177/1357633X15618810)); and a 2025 wrist-device study with 97.2% specificity but only 5.3% sensitivity for decompensation, with sleep data missing 99% of the time ([PMC12507380](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12507380/)).

**Sleepiz One+ (FDA 510(k) K223163, Class II, announced Oct 2023)**
- Intended use: contactless HR and RR in adults at rest or during sleep, in non-motion conditions. It also detects presence and movement. Home use by patients or caregivers is allowed. It is NOT for active monitoring and has no alarms. — [Innolitics K223163 summary](https://fda.innolitics.com/device/K223163)
- Technology: continuous-wave radar (frequency not stated in the summary seen). Predicate: Xandar Kardian XK300 UWB radar (K202464). Output ranges: RR 5–40/min, HR 40–120 bpm. — [Innolitics K223163](https://fda.innolitics.com/device/K223163)
- Clinical basis: two studies, n=199 in total. The cohorts were neurorehabilitation ward patients (59+32) and patients suspected of sleep apnea (73/105). References were ECG, pulse oximetry, respiratory effort belt, nasal cannula and etCO2.
  - HR: within ±5 bpm in 94% of readings (rehab ward), LoA −2.64 to 5.82 bpm vs ECG; 96% in the sleep-apnea group.
  - RR: within ±3/min in 99% vs belt, LoA −1.42 to 0.97. Against etCO2 (n=35): within ±2/min in 93.7%, LoA −2.51 to 2.04, MAE 0.79/min.
  — [Innolitics K223163](https://fda.innolitics.com/device/K223163)
- Contraindications in the summary: pregnant women and patients with active implantable devices. This matters for HF patients with pacemakers, ICDs or CRT. — [Innolitics K223163](https://fda.innolitics.com/device/K223163)
- Later clearances K251364 (2025-07-29) and K253388 (2026-01-28) appear to rely on the predicate's testing and add no new accuracy criteria. Only database summaries were seen. — [Innolitics K251364](https://510k.innolitics.com/device/K251364); [Innolitics K253388](https://510k.innolitics.com/device/K253388)
- Press coverage rounds the results to "99% RR / 96% HR accuracy". That is a headline derived from the ±3/min and ±5 bpm thresholds, not error figures. — [Sleep Review](https://sleepreviewmag.com/practice-management/laws-regulations/fda/fda-clears-contactless-remote-sleep-monitoring-device/)

### Inferences
- RR at about ±1–2 breaths/min overnight is achievable with bedside radar in elderly and comorbid people, but only with mature, validated signal processing (Somnofy, Sleepiz). The MR60BHA2's onboard firmware has no such validation, so its RR and HR outputs should be treated as unvalidated until the team benchmarks them against a reference (a chest belt or pulse oximeter) on a few volunteers.
- Night HR from radar is weaker than RR, and arrhythmia is common in HF (AF in particular), which makes it worse. Radar HR should be reported as a trend at best. It should not be used as a clinical value.
- A whole-night average RR trend (where the error is about 5%) is a more defensible output than minute-level RR. A rising nightly RR is also the signal the HF literature links to readmission.
- The Sleepiz contraindication for "active implantable devices" is a regulatory and labeling problem for an HF population, many of whom have CRT or ICDs, even though interference evidence at mmWave is reassuring (see Q5).

### Gaps
- No peer-reviewed validation of the MR60BHA2, Infineon BGT60 (TR13C/LTR11) or TI IWR6843 vital-sign demos in elderly or HF patients was found. The TI and Infineon datasheet accuracy claims were not retrieved.
- The Sleepiz radar frequency and its home-use accuracy outside the clinic were not found.
- The UTS HF study full text (year, device model, likely ResMed SleepMinder) was not verified.

## Q2. Can radar detect posture, sit-up events, apnea or periodic breathing, cough, and falls?

### Takeaway
Detecting periodic or Cheyne-Stokes breathing from bedside radar has the best HF-specific evidence: 50 HF patients, 86% accuracy. Fall detection works well in lab trials but degrades on fall-like everyday movements. Posture (flat vs propped vs sitting) and night cough from radar have no usable validated evidence at low cost.

### Cited Findings
- Periodic breathing / CSA in HF: bedside Doppler, n=50 systolic HF patients vs PSG, 71% sensitivity, 88% specificity, 86% accuracy for CSA/Cheyne-Stokes sections. — [UTS OPUS](https://opus.lib.uts.edu.au/handle/10453/125882)
- Microwave channel-state-information sensing using a software-defined radio (USRP) classified normal vs Cheyne-Stokes breathing in HF patients with 97% accuracy (SVM). This is the authors' own figure from a lab setup, not low-cost radar. — [Glasgow eprints 267764](https://eprints.gla.ac.uk/267764/1/267764.pdf)
- A three-UWB-radar plus depth-camera proof-of-concept classified breathing patterns including Cheyne-Stokes, with RR MAE about 0.6/min. It was not tested on patients. — [PMC8959759](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8959759/)
- AHI from a contactless (under-mattress) device in older adults: r² = 0.59 vs PSG, MAE 6.49 events/h. Somnofy radar gave no breathing-disturbance index in that study. — [PMC11387924](https://pmc.ncbi.nlm.nih.gov/articles/PMC11387924/)
- Falls, multi-person mmWave (Sci Rep 2026): 97.9% accuracy across 1–10 subjects in a 12×12 m room. Accuracy dropped to 76.8% on fall-like activities of daily living such as sitting down abruptly or lying on a bed. — [PMC12988233](https://pmc.ncbi.nlm.nih.gov/articles/PMC12988233/)
- An FMCW radar LSTM study for seniors living alone classified sitting correctly 95% of the time but lying only 50%. — [MDPI Appl Sci 15(15):8381](https://www.mdpi.com/2076-3417/15/15/8381)
- Post-fall floor occupancy (lying face up, lying sideways, sitting on the floor) from low-cost mmWave point clouds accumulated over 30 s. Accuracy figures were not seen. — [arXiv 2601.17710](https://arxiv.org/pdf/2601.17710)
- A vendor 60 GHz fall sensor claims "99%" fall accuracy. This is a marketing claim with no study. — [Milesight VS373](https://www.milesight.com/iot/product/lorawan-sensor/vs373)
- Seeed sells a separate fall-detection module, the MR60FDA2 kit. So fall detection and breathing/heartbeat are different SKUs, not one module. — [Fabtolab MR60FDA2](https://www.fabtolab.com/seeed-mr60fda-60ghz-mmwave-fall-detection-sensor-kit-xiao-esp32c6)
- Bed entry and exit with thermal plus ultrasonic sensors (not radar): 98.66% / 96.73%. — [PMC5492489](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5492489/)

### Inferences
- A plausible sit-up or orthopnea proxy: with range gating, a 60 GHz or LD2410-class radar can see the distance to the torso and the height of motion energy change when someone sits up. That makes a coarse "sat up / left bed" event plausible. Telling "lying flat" from "propped on 2–3 pillows" is unlikely to be reliable from a single bedside radar. No source validated this.
- Night cough from radar alone has no evidence. Cough looks like a short burst of body movement, so radar could flag "movement burst" events but not label them as cough. Acoustic sensing is the right tool for cough (see Q4).
- Periodic breathing detection needs a stable raw breathing waveform. The MR60BHA2 firmware outputs rates. Whether its raw phase or waveform data is exposed for custom cycle analysis was not confirmed.

### Gaps
- No study validates posture classes (flat vs propped vs upright in bed) with bedside radar.
- No radar cough-detection validation was found.
- The MR60BHA2 raw-data or API exposure for waveform analysis was not checked.

## Q3. Edge cases: two people, fans, blankets, pets, floor sleeping, distance and angle, movement, power cuts

### Takeaway
Two people in the same bed and moving objects such as ceiling fans are the main unsolved problems for cheap single-module radar. Movement causes data loss of about a third of in-bed time even in good devices. Floor sleeping and power cuts are installation and design problems that have no literature at all.

### Cited Findings
- Same-bed couples are not reliably separable with most methods. Separation of vital signs works only when targets are far apart in range or angle. A TI demo had 4 cm range and 15° angle resolution. One FMCW study separated two people a minimum of 40 cm apart using beamforming. — [Electronics 12(12):2732, CEEMDAN-ICA](https://doi.org/10.3390/electronics12122732); [TI multi-person vital signs white paper](https://e2echina.ti.com/cfs-file/__key/communityserver-discussions-components-files/60/Vital-Signs-Monitoring-of-Multiple-People-using-a.pdf)
- Blind source separation (FastICA) reportedly separated two targets in the same resolution cell, but only in controlled tests. — [Electronics 12(12):2732](https://doi.org/10.3390/electronics12122732)
- Accuracy drops when other people are nearby, and bed-frame multipath adds noise. Two radars on one bed interfere with each other unless managed (patent). — [MDPI Sensors 22(21):8167](https://www.mdpi.com/1424-8220/22/21/8167); [US patent 12447305](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12447305)
- Fans, curtains and pets produce returns that look human, and fan motion injects energy into the detection zone. This is a non-peer-reviewed blog with no measurements. — [DEV Community: Ghost targets and glass walls](https://dev.to/249263431/ghost-targets-and-glass-walls-multipath-interference-in-home-radar-care-kk5)
- The MR60BHA2's 1.5 m vital-sign range is specified for a single stationary person in a controlled empty room. — [OpenELAB MR60BHA2](https://openelab.io/de/products/seeed-studio-xiao-60ghz-mmwave-human-breathing-heartbeat-sensor-mr60bha2)
- Body movement: Somnofy lost RR data for about 32% of in-bed time, mostly wake and movement. Accuracy was worse during wake than during sleep. Sleepiz's clearance is limited to "non-motion conditions". — [PMC11387924](https://pmc.ncbi.nlm.nih.gov/articles/PMC11387924/); [Innolitics K223163](https://fda.innolitics.com/device/K223163)
- Home data loss in the older-adult study was mostly from Wi-Fi dropouts (3.3–4.2%). — [PMC11387924](https://pmc.ncbi.nlm.nih.gov/articles/PMC11387924/)
- Power: the MR60BHA2 kit draws about 0.5 W in standby and 0.8 W active, from 5 V / 1 A. That is roughly 0.8 W × 10 h ≈ 8 Wh per night. — [Mouser MR60BHA2](https://www.mouser.ca/new/seeed-studio/seeed-studio-mr60bha2-sensor-kit)

### Inferences
- Ceiling fans are near-universal in Indian bedrooms. The blades sit above the bed and rotate at a steady rate. A bedside unit aimed horizontally or slightly downward at chest height, with range gating set to the bed distance (0.5–1.2 m), should keep most fan returns out of the beam. Fan-induced flutter of bedsheets and mosquito nets will still add Doppler noise. This is untested and should be tested in the team's pilot.
- Sharing a bed with a spouse is common for elderly Indian couples. A single cheap module will often mix two breathing signals. Mitigations: place the unit on the patient's side with a narrow range gate, record "second person present" as a data-quality flag, and accept that nights with low-quality signal get discarded.
- Floor sleeping (mattress on the floor) changes geometry. The unit must sit low and close (within 1–1.5 m), so the mount should be adjustable or placed on the floor.
- Power cuts: about 1 W means a small Li-ion cell or a USB power bank can bridge outages. A 2,000 mAh 3.7 V cell (≈7.4 Wh) covers most of a night. Buffering data locally avoids gaps.
- Thin blankets are not expected to block 24/60 GHz much. This was not verified in sources. Thick quilts, metal bed frames and water are likely to attenuate or reflect the signal.

### Gaps
- No quantitative study of ceiling-fan Doppler clutter on bedside vital-sign accuracy was found.
- No study on blankets or quilts, pets, or floor sleeping was found.
- No data were found on LD2410 or MR60BHA2 behavior with two occupants of one bed.

## Q4. Bedside acoustic sensing (microphone) for cough counting and breathing

### Takeaway
Validated nocturnal cough detection with non-contact microphones reaches about 72–90% sensitivity with high specificity. False positives run at about 1 per hour in the field. Running a small classifier on-device keeps audio from leaving the unit, which is the main privacy safeguard. No study tested Indian home noise or HF patients.

### Cited Findings
- Hyfe multicenter validation (Sci Rep, Jan 2025; NCT05723159): wrist-worn device, 546 monitored hours, 4,454 coughs. Sensitivity 90.4% (95% CI 88.3–92.2). False positives 1.03/h (0.84–1.24). Hourly counts vs human annotation r ≈ 0.99. Participants were monitored for 24 h during usual activities. An ERS 2024 abstract reported n=23. — [DOAJ Sci Rep 2025](https://doaj.org/article/a19cc385064a4c1ebd5d233c5095ce85); [ClinicalTrials NCT05723159](https://clinicaltrials.gov/study/NCT05723159); [ERS 2024 abstract](https://publications.ersnet.org/content/erj/64/suppl68/pa788)
- Nighttime smartphone cough monitoring in the ward (JMIR Form Res 2023): n=9 pneumonia patients, 72 h of recordings. Sensitivity/specificity was 72%/99% on-device and 82%/99% on a computer. The authors note there is "no adequately validated generic cough monitor" commercially available. — [PMC9989914](https://pmc.ncbi.nlm.nih.gov/articles/PMC9989914/)
- Non-contact microphone, nocturnal, DNN-based: sensitivity 86.1%, specificity 99.9%, PPV 78.4%. — [PMC8769326](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8769326/)
- Asthma field study (JMIR 2020): automated nocturnal cough counts vs human annotation had a mean difference of −0.1 coughs (95% CI −12.11 to 11.91). — [JMIR 2020;22(7):e18082](https://www.jmir.org/2020/7/e18082/citations)
- A UW ubicomp lab paper presents a low-cost, privacy-preserving microphone cough sensor, with 92% TPR and 0.5% FPR in the wild. Only the search summary was seen. — [UW ubicomplab PDF](https://ubicomplab.cs.washington.edu/pdfs/accurate-and.pdf)
- Across nocturnal cough monitors, reported sensitivity ranges from 26% to 99.9%, and many validations were not peer-reviewed or were done on recordings rather than on-device. — [PMC9989914](https://pmc.ncbi.nlm.nih.gov/articles/PMC9989914/)

### Inferences
- An INMP441 I2S MEMS mic on an ESP32-S3 can run a small cough/non-cough classifier, for example a TinyML model trained on public cough datasets. It can store only timestamps and counts, never raw audio. That addresses privacy for an elderly household and keeps bandwidth near zero.
- Indian home noise (ceiling fans as broadband steady noise, TV, traffic, dogs, religious loudspeakers, other family members coughing) will raise false positives. Fan noise is stationary and can be spectrally subtracted. TV and another person's cough cannot be fully removed. Expect at least the 1 FP/hour seen in field studies, so report a nightly cough-count trend rather than single events.
- The microphone can also give snoring and gasping cues. Acoustic breathing rate at bedside distance is less reliable than radar RR. No source was found for acoustic RR accuracy at 1 m.
- Bedside acoustic does not tell whose cough it is (patient vs spouse). This is the same attribution problem radar has.

### Gaps
- No validation of acoustic cough counting in HF patients was found. Cough is a known HF congestion symptom, but this is not quantified here.
- No study of cough detection in Indian home acoustic environments was found.
- No accuracy figure for bedside acoustic breathing rate was found.

## Q5. Prices in India and power; safety and regulatory (RF exposure, WPC/ETA for 60 GHz, pacemakers and ICDs)

### Takeaway
A 24 GHz presence radar (LD2410 family, ₹300–650) plus a MEMS microphone (₹180–250) plus an ESP32 fits easily within ₹700–1,500. A 60 GHz vital-sign module (MR60BHA2 kit, about ₹2,500–3,300 if available in India) breaks that budget by itself. 60 GHz (57–64 GHz) does not appear to be delicensed in India as of the latest results found, which is a real regulatory risk. mmWave interference with pacemakers and ICDs looks negligible in body-scanner studies, but Sleepiz is still labeled contraindicated for active implants.

### Cited Findings
**Prices (India, single unit unless noted)**
- HLK-LD2410 (24 GHz presence, includes stationary/breathing-level presence): ElectronicsComp ₹369 + 18% GST (out of stock when indexed). Indian Hobby Center ₹499. Probots LD2410C ₹399–495. Robu LD2410S ₹639 (via aggregator). Amazon.in LD2410C ₹999. — [ElectronicsComp](https://www.electronicscomp.com/hlk-ld2410-24ghz-human-presence-body-induction-distance-detection-radar-sensor-module-support-gpio-and-uart-ports); [Indian Hobby Center](https://www.indianhobbycenter.com/products/hi-link-hlk-ld2410-24ghz-human-presence-body-induction-distance-detection-radar-sensor-module-support-gpio-and-uart-ports); [Amazon.in](https://www.amazon.in/EC-Buying-HLK-LD2410-Presence-Millimeter/dp/B0BXDLHHH2)
- HLK-LD2410B + BLE on IndiaMART at ₹292–313/piece (wholesale). — [IndiaMART](https://www.indiamart.com/proddetail/hlk-ld2410b-ble-24ghz-human-presence-radar-sensor-2851273796555.html); [Rajguru Electronics](https://www.rajguruelectronics.in/lidar-radar-sensor.html)
- Hi-Link factory listing for LD2410 is about US$3.20. — [Hi-Link](https://www.hlktech.net/index.php?id=988)
- An HLK-LD2410B test kit is sold in India marketed as "respiration and heartbeat monitoring", per the product title. Treat this as a seller claim. The LD2410 is a presence sensor. — [Quartz Components](https://quartzcomponents.com/products/hi-link-new-24g-human-presence-radar-module-kit-ld2410-respiration-and-heartbeat-monitoring-non-contact-induction-smart-sensor)
- HLK-LD2450 (24 GHz, tracks up to 3 people) is sold by Probots. The price was not captured. — [Probots LD2450](https://probots.co.in/hlk-ld2450-24ghz-mmwave-tracking-radar-sensor.html)
- MR60BHA2 kit: Amazon.in listing "currently unavailable". Fabtolab shows about ₹3,332, but the price is ambiguous between MR60BHA2 and MR60FDA2. Seeed lists US$26.99 at 10+ units. The Pi Hut lists £28.80. — [Amazon.in MR60BHA2](https://www.amazon.in/MR60BHA2-Breathing-Heartbeat-Assistant-Compatible/dp/B0F3CCM5P6); [Fabtolab](https://www.fabtolab.com/seeed-mr60fda-60ghz-mmwave-fall-detection-sensor-kit-xiao-esp32c6); [Seeed](https://www.seeedstudio.com/MR60BHA2-60GHz-mmWave-Sensor-Breathing-and-Heartbeat-Module-p-5945.html); [The Pi Hut](https://thepihut.com/products/60ghz-mmwave-breathing-and-heartbeat-detection-sensor-mr60bha2)
- INMP441 I2S MEMS microphone: Probots ₹245 including GST. Hubtronics ₹177 including GST. IndiaMART ₹188–239 excluding tax. Robu has a listing, but the price was not captured. — [Probots INMP441](https://probots.co.in/inmp441-mems-high-precision-omnidirectional-microphone-module-i2s.html); [Hubtronics](https://hubtronics.in/generic/inmp441-omnidirectional-microphone-module?page=46); [IndiaMART](https://m.indiamart.com/proddetail/inmp441-mems-high-precision-omnidirectional-microphone-module-i2s-interface-supp-fr-01-274-2852645893348.html); [Robu](https://robu.in/product/inmp441-mems-high-precision-omnidirectional-microphone-module-i2s)
- MR60BHA2 power: 0.5 W standby, 0.8 W active, 5 V / 1 A. — [Mouser](https://www.mouser.ca/new/seeed-studio/seeed-studio-mr60bha2-sensor-kit)

**Regulatory (India)**
- TRAI consulted on V-band (57–64 GHz and 64–71 GHz) in Sep 2023. Molex submitted (Dec 2023) asking for unlicensed short-range-device use of 57–64 GHz. That is advocacy, not a rule. — [TRAI Molex submission](https://trai.gov.in/sites/default/files/Molex_14122023.pdf)
- TRAI had earlier recommended delicensing 60 GHz, but DoT had not decided at the time of that article (an old article). — [Communications Today](https://www.communicationstoday.co.in/delicensed-v-band-to-be-or-not-to-be/)
- Recent DoT delicensing covers the lower 6 GHz band (Jan 2026, 5925–6425 MHz) and 5.9 GHz plus 77–81 GHz (June 2026, automotive). No 57–64 GHz exemption was found. — [MediaNama Jan 2026](https://www.medianama.com/2026/01/223-india-delicenses-6ghz-wifi-spectrum/); [ETV Bharat June 2026](https://www.etvbharat.com/en/technology/dot-delicenses-mid-high-frequency-bands-to-boost-passenger-safety-autonomous-car-devt-enn26061206965)
- The 2015 WPC delicensing (GSR 696–699(E)) included 76–77 GHz short-range radar, not 60 GHz. — [Kiwa regulatory update Oct 2015](https://careers.kiwa.com/globalassets/uk/pcs/regulatory-updates-2015/regulatory_update_india-wpc_21-oct-15.pdf)
- All wireless products in delicensed bands still need WPC Equipment Type Approval (ETA). — [UL India WPC](https://india.ul.com/download-resources/wireless-planning-and-coordination-wing-wpc/)
- A 2026 consolidated guide to WPC delicensed bands exists, but its table was not readable in the results. — [PCN Global India 2026 guide](https://pcnindiaglobal.com/2026/07/06/wpc-de-licensed-frequency-bands-india-complete-guide/)

**Cardiac implants**
- ESC 2018 (German Heart Center Munich): 300 patients with pacemakers, ICDs or CRT went through a mmWave security body scanner with ECG monitoring. There was no EMI or device malfunction. This was a conference presentation. — [ACC summary](https://www.acc.org/Latest-in-Cardiology/Articles/2018/08/20/17/59/sun-830am-security-bodyscanners-esc-2018)
- 2021 study (J Interv Card Electrophysiol): 73 patients with leadless pacemakers or S-ICDs, scanned including at close range. There was no pacing inhibition, oversensing or reprogramming. — [Springer s10840-020-00830-x](https://link.springer.com/article/10.1007/s10840-020-00830-x)
- The authors' proposed explanation: implants filter high-frequency signals, mmWave barely penetrates the body, and exposure is short. This is a hypothesis. Note that bedside radar exposure lasts all night, unlike a scanner. — [DZHK news](https://old.dzhk.de/en/news/latest-news/article/security-millimetre-wave-body-scanner-safe-for-patients-with-pacemakers-and-defibrillators/)
- Sleepiz One+ lists "patients with active implantable devices" as a contraindication. — [Innolitics K223163](https://fda.innolitics.com/device/K223163)

### Inferences
- Indicative budget build inside ₹700–1,500 (prices from the listings above; ESP32 board price not sourced):
  - HLK-LD2410B/C: about ₹300–500
  - INMP441: about ₹180–250
  - ESP32-S3 or ESP32-C3 dev board: not sourced, typically a few hundred rupees
  - Cell/charger, enclosure and cable: extra
  - A total of about ₹900–1,400 looks feasible.

  This build gives presence, bed occupancy and exit, coarse sit-up, movement and restlessness, and acoustic cough counts. It does NOT give validated RR, HR or periodic-breathing detection. LD2410 firmware reports presence and energy per range gate, not breathing rate.
- The 60 GHz route (MR60BHA2, about ₹2,500–3,300 + import) is the only cheap option that outputs RR and HR. But it busts the ₹1,500 cap, is a beta product, is unvalidated, and may not be type-approvable in India if 57–64 GHz stays licensed.
- Raw-data 24 GHz FMCW modules could in principle give a breathing waveform from range-gate phase, with custom DSP. Whether the LD2410 exposes enough raw data for this was not verified, and it would be a research project in itself.
- Per Hi-Link documentation, the 24 GHz LD2410 runs in the 24.0–24.25 GHz ISM band. India's delicensing of a 24 GHz low-power band was not confirmed in this search (see Gaps). ETA approval is needed either way.
- Compared with the ₹5,000 home-unit budget (from the project's memory notes): a 60 GHz module could fit the overall home budget but not the ₹700–1,500 companion line item.

### Gaps
- India's 24 GHz delicensing status (exact GSR notification and band limits) was not confirmed in these searches.
- No current Robu, ElectronicsComp or Probots rupee price was found for the MR60BHA2. No Indian prices were found for Infineon BGT60 or TI IWR6843 boards. These are known to be far more expensive, but that was not sourced here.
- ICNIRP / India RF exposure limits for 24 and 60 GHz consumer devices were not retrieved. The output power of these modules (typically in the mW range) was not sourced.
- The 2026 PCN consolidated WPC band table was not readable, so a 57–64 GHz exemption since mid-2026 cannot be fully ruled out.
- No study covered all-night mmWave exposure in patients with implanted cardiac devices.
