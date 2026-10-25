# Low-cost wearable sensing for night/day monitoring of elderly heart-failure patients (companion to a home check-in station)

Research date: 2026-10-24. Sources are mostly search-result abstracts/snippets; full texts were not read except where stated. "PR" = peer-reviewed; "Co." = company/vendor claim; "Patent" = patent text (design claim, not evidence).

## 1. Chest-worn accelerometer accuracy (respiratory rate, effort, posture, sit-up/PND, cough, activity, falls)

### Takeaway
A chest accelerometer (pod in vest pocket, chest band, or pendant resting on the sternum) can give resting/sleep respiratory rate within about 2 breaths/min and good lying-vs-upright posture classification in small studies, but there is almost no validation specifically in older adults or heart-failure patients, and none for orthopnea/PND event detection. Audio-free cough detection reaches ~90% sens/spec only in small controlled studies; fall detection is much worse in real-world falls (~57% sensitivity for simple thresholds) than in lab tests.

### Cited Findings
**Respiratory rate during sleep/rest**
- PR: Chest-worn accelerometer, full overnight PSG, 13 healthy subjects: respiratory rate mean difference 1.8 breaths/min vs respiratory inductance plethysmography (RIP). Authors note that very few validation efforts exist for RR during sleep. — [Biomed Signal Process Control 2022 (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S1746809422004888)
- PR: Chest accelerometer RR and respiratory effort via constrained/recursive PCA, 20 subjects aged 46–65, tested under variable sensor positions and body postures, impedance-plethysmography reference; results not split by age. — [ResearchGate: Estimation of respiratory rate and effort from a chest-worn accelerometer](https://www.researchgate.net/publication/350183443_Estimation_of_respiratory_rate_and_effort_from_a_chest-worn_accelerometer_using_constrained_and_recursive_principal_component_analysis)
- PR: Estimation of respiration rate and sleeping position with a single wearable accelerometer (same research line; RR plus sleeping position from one chest sensor). — [ResearchGate](https://www.researchgate.net/publication/343940038_Estimation_of_respiration_rate_and_sleeping_position_using_a_wearable_accelerometer)
- PR: Chest-worn accelerometry sleep staging, 323 participants aged 13–83: 4-class epoch agreement kappa 0.68, accuracy 80.8% (staging, not RR accuracy, but shows the chest accelerometer captures usable cardiorespiratory signal across a wide age range). — [PMC11398147](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11398147/)
- PR (2026): "Clinical validation of a novel accelerometer-based respiratory rate monitor", J Clin Monit Comput 2026 — exists, but paywalled; numbers not retrieved. — [Springer](https://link.springer.com/article/10.1007/s10877-026-01419-x)
- No study found validating chest-accelerometer RR specifically in older adults or HF patients during sleep (search result explicitly found none). — [search summary; closest evidence above]

**Breathing depth/effort**
- PR: The PCA method above estimates "respiratory effort" (relative amplitude), not calibrated tidal volume. — [ResearchGate](https://www.researchgate.net/publication/350183443_Estimation_of_respiratory_rate_and_effort_from_a_chest-worn_accelerometer_using_constrained_and_recursive_principal_component_analysis)
- For comparison, impedance-based flow estimation from a 55 mm patch reached only r=0.81 with 38% relative error vs pneumotachometer (see Section 3), indicating absolute depth/volume from small wearables is weak. — [ResearchGate: Wearable Impedance Pneumography](https://www.researchgate.net/publication/342282690_Wearable_Impedance_Pneumography)

**Posture / trunk angle (lying flat, propped, sitting)**
- PR: Single chest-mounted tri-axial accelerometer detected daily postures, postural transitions and walking modes "with high sensitivity and specificity" (abstract; figures not in snippet). — [PubMed 29691130](https://pubmed.ncbi.nlm.nih.gov/29691130/)
- PR (EPFL, Najafi et al., older adults): chest-worn kinematic sensor, 11 elderly subjects vs optical motion capture: sit-to-stand sens 93%/spec 82%, stand-to-sit 82%/94%; sitting/standing posture classification errors 6% and 8% in two 1-hour monitored participants. — [EPFL Infoscience 97072](https://infoscience.epfl.ch/record/97072?ln=fr); [EPFL Infoscience 97055](https://infoscience.epfl.ch/record/97055?ln=en)
- PR: one study reported lying sens 98.4%/spec 99.7%, sitting 90.2%/93.4%, standing+walking 92.2%/92.1% (sensor placement/population not confirmed from snippet). — [EPFL Graphsearch](https://graphsearch.epfl.ch/publication/97072)
- PR (2023): single lower-back accelerometer+gyro, 18 community-dwelling older adults, video reference: scripted sitting sens/spec/PPV/NPV 76.9–94.8%, scripted lying 70.4–95.7%; authors note a single wearable struggles to distinguish sitting from lying. (Lower back, not chest — the chest gives a cleaner trunk-tilt vector.) — [PMC10223684](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10223684/)
- Patent: chest posture is computed from the accelerometer DC (gravity) vector vs a calibrated reference; example rules: torso angle ≤35° = supine, ≥135° = prone, else lateral; another uses 45° to split upright vs lying. Posture sensing is described as a way to monitor orthopnea and PND. — [US 10328267 (posture calibration matrices)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10328267); [US 12076127 (body-worn pulse oximeter)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12076127); [US 8956294](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8956294)

**Sit-up / PND events**
- No peer-reviewed validation of accelerometer-detected orthopnea or PND events in HF patients was found; only patents describe it. — [US 10328267](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10328267)

**Cough without audio**
- PR: Triaxial accelerometer + stretchable strain sensor, 21 participants: combined sens 92%/spec 96%; accelerometer alone sens 91%/spec 95%. — [Sci Rep 2021 / PMC8113562](https://pmc.ncbi.nlm.nih.gov/articles/PMC8113562/)
- PR (2025): multi-sensor smart garment (acceleration + strain), ML: AUC 95.2%, sens 98.5%, spec 91.9%. — [Comput Biol Med 2025](https://www.sciencedirect.com/science/article/pii/S0010482525005438)
- PR/preprint: neck-worn accelerometer cough vs swallow/speech/head movement sens 91%/spec 89%. — [arXiv 2001.00537](https://arxiv.org/pdf/2001.00537)
- Preprint: non-audio template matching averaged only 56% sensitivity. — [arXiv 2109.00630](https://arxiv.org/pdf/2109.00630)
- Non-peer-reviewed GitHub project (chest IMU): sens 0.907, spec 0.514, AUC 0.832; author flags label leakage — unreliable. — [GitHub](https://github.com/sumeyye-agac/chest-imu-cough-detection)

**Falls**
- PR: Threshold accelerometer algorithms on 29 real-world falls: mean sensitivity 57%; false alarms 3–85 per day across algorithms. — [Bagalà et al., PLoS One 2012](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0037062)
- PR: SVM on waist/sternum accelerometer, real-world falls in older adults: 8 of 10 falls detected, 0–0.3 false alarms/hour across individuals. — [PLoS One 2017 / PMC5498034](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5498034/)
- PR: Embedded fall algorithm, 272 simulated falls: waist and chest gave best sensitivity/false-alarm trade-off; ~90% detection with ~6 false alarms/day at high sensitivity. — [Sensors 2019 / PMC6603555](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6603555/)
- PR (2025): wearable fall system, 97.9% sensitivity in 15-person lab study (not real-world elderly). — [Sensors 2025](https://www.mdpi.com/1424-8220/25/12/3632)
- PR: user characteristics affect wearable fall-detection performance. — [Sci Rep 2021](https://www.nature.com/articles/s41598-021-02537-z)

**Activity/steps**
- No chest-specific step-count validation in elderly was retrieved in this pass (see Gaps).

### Inferences
- For the companion, the highest-confidence chest-accelerometer outputs are (a) nightly trunk angle/time spent supine vs propped vs upright and (b) resting/sleep RR trend; both depend on the pod being held firmly against the sternum (chest band or snug vest pocket) — a loose pendant swinging on a cord will degrade RR and cough detection, and can misreport posture.
- Trunk-angle bins (flat ≤~30°, propped ~30–60°, upright ≥~60°) map naturally onto orthopnea tracking ("pillows needed"); patents use 35°/45° cut-offs, but no clinical validation of these thresholds in HF exists, so present as trend, not diagnosis.
- PND event = transition from lying to sitting at night, possibly with elevated RR/cough burst afterward; the posture-transition sens/spec (~80–93%) from EPFL suggests feasibility but this is untested in HF.
- Fall detection should be treated as a secondary, best-effort feature with expected false alarms; it should not be marketed as a safety alarm.

### Gaps
- No chest-accelerometer RR validation in adults >70 or HF patients; no data on Cheyne-Stokes/central apnea patterns typical in HF.
- No validated sensitivity/specificity for orthopnea or PND detection.
- Chest-worn step-count accuracy in elderly not retrieved (wrist/hip literature exists but not searched here).
- 2026 Springer accelerometer RR monitor paper numbers not retrieved (paywall).

## 2. Chest/sternal PPG and wrist/ring PPG: night HR, SpO2, RR; older adults and darker skin

### Takeaway
Nocturnal heart rate from good wrist/ring PPG is accurate (Oura vs ECG r ≈ 1.0, including older participants), but HRV degrades in older adults and SpO2 from reflectance PPG at any site has ~2–4% errors with pigmentation-related bias and almost no validation in elderly sleepers. Sternal reflectance SpO2 is feasible (RMSE ~2.3–2.6% in 20 subjects with breath-holds) but immature; a bare MAX30102 is not a validated oximeter.

### Cited Findings
- PR (2024, Sensors): Oura ring nocturnal HR vs ECG, including older age groups: correlations ≥0.9 for all metrics and age groups, HR ≈1.00; but >50% of older participants had HRV MdAPE >10%. — [PMC11644394](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11644394/)
- PR (2025): 13 adults, 536 nights: Oura Gen 3/Gen 4 most accurate for nocturnal resting HR vs Polar, WHOOP. Small, healthy sample. — [PMC12367097](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12367097/)
- PR (2022): six wearables vs PSG in healthy adults: sleep/wake agreement Apple Watch S6 88%, Oura Gen2 89%; 4-stage agreement 53% vs 61%. — [PMC9412437](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9412437/)
- No PSG-validated wrist/ring SpO2 or RR data in older adults was found for Oura or Apple Watch. — [search result summary of above sources]
- PR (2024 meta-analysis, JMIR): 23 pulse-oximetry studies: SpO2 errors around 4% across light/medium/dark pigmentation groups; largest pooled bias for dark pigmentation (~1.27%); authors conclude readings may be inaccurate across all groups. — [JMIR 2024;e62769](https://www.jmir.org/2024/1/e62769/citations)
- PR (2023): Empatica EmbracePlus wrist SpO2, 30% dark-skinned participants, accuracy (Arms) 2.4%, within FDA 3.5% limit (company-sponsored device study). — [Frontiers Digital Health 2023](https://www.frontiersin.org/journals/digital-health/articles/10.3389/fdgth.2023.1258915/full)
- Secondary (blog, verify): 2025 test of 34 fingertip/wrist oximeters found 11 with significantly more positive bias in darker skin; only one met FDA proposed criteria. FDA January 2025 draft guidance calls for ~150+ participants, Monk 10-shade scale plus objective pigmentation measure. — [Sahha blog](https://sahha.ai/blog/wearables-darker-skin-accuracy/); FDA panel background: [FDA executive summary](https://www.fda.gov/media/175828/download)
- Preprint (2026): PPG HR accuracy inequities across body composition and skin tone. — [arXiv 2601.22377](https://arxiv.org/pdf/2601.22377)
- PR (2021, Biosensors): sternum reflectance SpO2 patch, 20 subjects, breath-hold protocol: RMSE 2.64 ± 1.14%, r=0.89 (subject-independent); 2.27 ± 0.76% with subject-specific calibration. Authors state clinical use needs a large diverse cohort, wide SpO2 range, RMSE <3.5%. — [PMC8699050](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8699050/)
- PR (2026, Sensors): real-time chest reflectance SpO2 validated against arterial SaO2; authors say performance during free daily activity still needs evaluation. — [Sensors 2026, doi 10.3390/s26175676](https://doi.org/10.3390/s26175676)
- PR (2024): chest-based PPG system; chest PPG signal quality depends on body location, wavelength, LED/photodiode geometry, posture and breathing pattern. — [PMC11573410](https://pmc.ncbi.nlm.nih.gov/articles/PMC11573410/)
- Preprint (2025): wrist and upper-arm reflectance SpO2 vs fingertip during overnight PSG in sleep-apnea patients. — [arXiv 2505.20846](https://arxiv.org/pdf/2505.20846)
- Retail: MAX30102 module (generic) sold as "heart rate and pulse oximeter sensor" — this is a hobby breakout, not a calibrated oximeter. — [Robu.in MAX30102](https://robu.in/product/max30102-heart-rate-and-pulse-oximeter-sensor-module-black/)

### Inferences
- For a ₹700–1,500 companion, night HR (and possibly PPG-derived RR) is realistic; claiming SpO2 is not, unless calibrated against a reference and disclosed as non-diagnostic. A fingertip pulse oximeter at the home station is a safer SpO2 source.
- Older skin (thinner, lower perfusion, more peripheral vasoconstriction in HF) and darker skin common in Indian users both work against reflectance PPG; sternum has better perfusion stability during sleep than wrist but needs firm contact (band, not pendant).
- Combining chest accelerometer (RR, posture) with a cheap PPG for HR only is the lowest-risk sensor set.

### Gaps
- No found validation of wrist/ring/chest SpO2 or RR specifically in adults >70 or in HF patients during sleep.
- No data on Fitzpatrick V–VI / Indian skin tones for MAX30102-class sensors.
- No validation of PPG-derived RR during sleep in elderly.

## 3. Impedance pneumography (chest band or two-electrode pod): respiration accuracy, lung-fluid value, electrode spacing

### Takeaway
Wearable impedance pneumography gives respiratory rate within ~1–2.5 breaths/min at rest (−0.6 ± 2.5 bpm vs capnography in 36 ward patients), but is motion-sensitive and loses signal as electrode spacing shrinks; tidal volume estimates are poor (38% error). Evidence that a small wearable tracks thoracic fluid in HF is essentially absent outside patents; it also needs gel/dry electrodes on skin, which raises irritation and adherence issues for elderly users.

### Cited Findings
- PR (2022): wearable with two thoracic + one abdominal electrode vs capnography, 36 hospital ward patients: mean difference −0.6 ± 2.5 breaths/min; tachypnea (>20/min) sens 81%, spec 93%. — [PMC8894146](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8894146/)
- PR: 55 mm patch configuration, 10 healthy subjects: RR error <1 bpm in almost all cases across supine/lateral/prone; flow estimation r=0.81, relative error 38% vs pneumotachometer. — [ResearchGate: Wearable Impedance Pneumography](https://www.researchgate.net/publication/342282690_Wearable_Impedance_Pneumography)
- PR: short-distance IP: very close electrodes give small respiration-induced impedance changes, prone to error; experiments with spacing down to 8 cm on frontal thorax. — [Short Distance Impedance Pneumography](https://www.researchgate.net/publication/327819521_Short_Distance_Impedance_Pneumography); [Optimal short-distance electrode locations](https://www.researchgate.net/publication/300114140_Optimal_Short_Distance_Electrode_Locations_for_Impedance_Pneumography_Measurement_from_the_Frontal_Thoracic_Area)
- PR: comparison of simple RR algorithms for wearable IP. — [ResearchGate](https://www.researchgate.net/publication/311500586_Comparison_of_simple_algorithms_for_estimating_respiration_rate_from_electrical_impedance_pneumography_signals_in_wearable_devices)
- PR: surgical patients — IP less accurate than capnography; IP susceptible to motion artifact and imprecise in several studies. — [ScienceDirect (Chest)](https://www.sciencedirect.com/science/article/abs/pii/S001236921533539X)
- PR (viewpoint): wearable bioimpedance applications overview. — [JMIR Biomed Eng 2021](https://biomedeng.jmir.org/2021/2/e22911/PDF)
- Patent: respiration (8–60 cycles/min) and congestion (minutes–days) impedance changes are separable by timescale; claims congestion changes are larger than breathing changes. Design claim only. — [US 9775520](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9775520)

### Inferences
- A two-electrode pod with <5 cm spacing is at the weak end of the evidence; a chest band with electrodes ~8+ cm apart is needed for reliable RR, which adds cost (AFE such as an impedance front-end, electrodes) beyond the ₹700–1,500 budget and adds skin-contact burden.
- For RR alone, the chest accelerometer gives similar accuracy without skin electrodes; IP's unique value would be thoracic fluid trend, which is unproven for wearables — not worth it for this companion.

### Gaps
- No peer-reviewed wearable study showing thoracic-impedance fluid tracking predicts HF decompensation found in this pass (implant-based and vest-based systems were not searched).
- No IP validation in elderly/HF at home.

## 4. Adherence / wear compliance in elderly and HF patients; skin, heat, sweat; charging; what improves wear

### Takeaway
Older adults can wear devices well when the device is comfortable and routines are simple (Fitbit ~95% of days worn; LINK-HF chest patch median ~23 h/day), but adhesive chest patches show frequent mild skin reactions (9–53%) and adhesive failure, and full 14-day completion can be as low as 41%. Charging/syncing burden and memory affect adherence; no head-to-head wrist vs chest vs pendant vs garment adherence trial in elderly HF was found.

### Cited Findings
- PR (2022): Paolillo et al., older adults (general, not confirmed HF), Fitbit: worn ~95% of study days, ~85% adherent to daily syncing; wearing adherence higher in women; syncing adherence associated with better memory; age and education not significant. — [Frontiers Digital Health 2022](https://www.frontiersin.org/journals/digital-health/articles/10.3389/fdgth.2022.884208/full)
- Conflict: Svensson et al. 2025 describe Paolillo et al. as a CHF population study; the primary abstract frames it as general older adults. — [PMC12515331](https://pmc.ncbi.nlm.nih.gov/articles/PMC12515331/)
- PR review (2025): LINK-HF trial median wear time ~23 h/day (chest-worn multisensor patch). — [PMC12744564](https://pmc.ncbi.nlm.nih.gov/articles/PMC12744564)
- PR (2024): SafeHeart, 303 ICD patients, wrist-worn accelerometer for 6 months; adherence defined as valid days with ≥22 h wear; "optimal" >95% long-term & 90% daily, "low" <75%. Useful template for defining adherence. — [PMC11417489](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11417489/)
- PR (2020): rural China elderly hypertensive, BP wristband: only about half became regular users; higher overall hypertension compliance predicted use. — [PMC7303401](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7303401/)
- PR (2025): JMIR secondary analysis of accelerometer adherence in older adults in mHealth cardiac rehab (exists; numbers not retrieved). — [JMIR 2025, doi 10.2196/80522](https://doi.org/10.2196/80522)
- PR (2025): single-lead ECG patch, median wear 13.2 days of 14; ~41% (n=88) completed all 14 days; manufacturer claims 98% compliance (Co.); BMI affects compliance mainly via adhesive failure. — [Dzikowicz 2025, Ann Noninvasive Electrocardiol / PMC12050362](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12050362/)
- PR: Korean 7-day patch cohort, 147 patients: 42.9% dermatologic adverse events (temporary); 4 stopped early for skin problems. — [PMC10264726](https://pmc.ncbi.nlm.nih.gov/articles/PMC10264726/)
- PR: 14-day patch, 32 patients: 53% had some dermal response, mean score 0.64 (minimal erythema). — [JKMS 2025](https://jkms.org/DOIx.php?id=10.3346%2Fjkms.2025.40.e168)
- PR: 7/14-day patch: 9% (5/58) had adverse skin reactions, mostly mild itch/redness. — [PMC10918718](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10918718/)
- HTA (Scotland 2024/2025): FDA adverse-event reports for ECG patches mostly non-serious contact dermatitis (113 cases). — [SHTG ECG patch assessment](https://shtg.scot/media/ad3bkw2u/2025-07-03-ecg-patches-assessment-v10.pdf)
- PR (smart garment): Hexoskin acceptability in smokers' daily life: varied — 2 would wear <3 h, 2 up to 7 h, 3 a day or more (not elderly). — [PMC8297348](https://pmc.ncbi.nlm.nih.gov/articles/PMC8297348/)
- PR (2025): HF patients' views on integrating wearables; mixed-methods/persona study. — [PMC12515331](https://pmc.ncbi.nlm.nih.gov/articles/PMC12515331/)

### Inferences
- Avoid adhesive electrodes/patches for an indefinite-use home companion: skin reactions in up to ~half of users over 1–2 weeks and adhesive failure would undermine nightly use in thin, fragile elderly skin.
- Highest likely adherence: a device that docks/charges at the check-in station each morning (charging tied to an existing routine), with multi-day battery, no app syncing required by the patient, and a familiar form (vest pocket / soft band). Paolillo's memory-sync link supports making sync automatic.
- Define adherence up front using SafeHeart-style thresholds (e.g., valid night = ≥6 h wear) so the hackathon demo can report it.

### Gaps
- No direct comparison of wrist vs chest band vs pendant vs garment adherence in elderly HF.
- No data on heat/sweat tolerance in hot-humid climates (India) for chest bands.
- No age-stratified patch skin-reaction data retrieved.

## 5. Safety: magnets near CIEDs, BLE near implants (ISO 14117), battery safety, neck-cord strangulation

### Takeaway
The documented implant risk from consumer wearables is static magnets (wristband clasps, MagSafe-style chargers) triggering magnet mode; FDA (2021) advises keeping such devices ≥15 cm (6 in) from a pacemaker/ICD, and ISO 14117 labelling uses the same 15 cm for portable RF transmitters. A chest-worn pod sits directly over a typical left-pectoral implant, so it must contain no magnets and ideally be worn on the opposite side or low-sternal; neck cords need a breakaway clasp; LiPo cells need protection circuits and thermal monitoring.

### Cited Findings
- FDA (2021, via secondary reporting): keep phones/smartwatches with magnets ~6 in (15 cm) from implanted pacemakers/defibrillators; do not carry in a pocket over the device; FDA believes risk is low and was unaware of adverse events at that time. — [HRS summary of FDA communications](https://www.hrsonline.org/resource/FDA-communications-cieds-consumer-devices); [Patient Safety Solutions copy of FDA notice](https://www.patientsafetysolutions.com/docs/July_20_2021_FDA_Warning_Magnets_in_Consumer_Electronics_May_Affect_Medical_Devices.htm); [PhoneArena](https://www.phonearena.com/news/fda-says-the-risk-is-low-that-a-magsafe-accessory-will-negatively-impact-implanted-medical-gear_id132128)
- Industry standard ISO 14117 calls for CIED labelling to warn of a minimum 15 cm (6 in) separation from portable electromagnetic transmitters (per HRS/secondary summary; standard text not read). — [HRS](https://www.hrsonline.org/resource/FDA-communications-cieds-consumer-devices)
- Co.: Apple advises >15 cm, and >30 cm while wirelessly charging. — [MacTrast](https://www.mactrast.com/2021/05/fda-risk-of-magsafe-interference-with-pacemakers-is-low/)
- PR (case report): fitness-watch wristband magnets put an ICD into magnet mode; authors advise not wearing such bands to sleep and keeping them away. — [Heart Rhythm Case Reports 2020](https://www.sciencedirect.com/science/article/pii/S2214027120302748)
- PR: static magnetic field measurements of phones/watches support the ≥6 in FDA advice; smartwatch magnetic bands can elicit magnet mode within ~2.0–2.4 cm. — [Heart Rhythm 2021 / PubMed 34600610](https://pubmed.ncbi.nlm.nih.gov/34600610/)
- PR: Apple Watch (1st gen) over device: no magnet effect in 148 patients; Series 6 field strong enough to induce magnet mode. — [PMC8979866](https://pmc.ncbi.nlm.nih.gov/articles/PMC8979866/)
- PR editorial: "Smartphones, smartwatches, and CIED patient safety: so far, so good." — [JACC EP 2020](https://www.jacc.org/doi/10.1016/j.jacep.2020.05.016)
- Henry Ford test: iPhone near left-chest ICD immediately suspended therapies. — [Physics World](https://physicsworld.com/a/electronic-gadgets-can-interfere-with-pacemakers-and-defibrillators-study-reveals/)
- Bluetooth/BLE radio itself: no clinical evidence of interference found; only a non-clinical buying guide claims it. — [Alibaba product insights (low quality)](https://www.alibaba.com/product-insights/how-to-choose-a-fitness-tracker-that-works-reliably-with-pacemakers-or-ecg-sensitive-devices.html)
- Battery: Fitbit Ionic recall (CPSC, March 2022): ~1.7 M units; 174 global overheating reports; 78 US burn injuries incl. 2 third-degree and 4 second-degree; Fitbit says <0.01% of units. — [CNBC](https://www.cnbc.com/2022/03/02/fitbit-recalls-smartwatches-over-burn-hazard.html); [BGR](https://bgr.com/tech/fitbit-recalls-1-69-million-ionic-smartwatches-after-118-burn-injuries/)
- Strangulation: Co. ADT fall-detection pendant manual warns of strangulation/choking hazard and that serious injury or death can occur if the cord entangles; lanyard is designed to break away with a tug. MobileHelp uses a magnetic breakaway lanyard. — [ADT pendant guide](https://www.adt.com/content/dam/adt/downloads/manuals/ADT_MedAlert_Fall_Detection_Pendant_User_Guide.pdf); [SeniorLiving MobileHelp review](https://www.seniorliving.org/medical-alert-systems/mobilehelp/)
- Patent: breakaway lanyards can drop the transmitter out of reach; proposes a secondary retention cord. — [US 9386829](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9386829)

### Inferences
- Design rules for the companion: no magnets in the pod, clasp, or charging (use pogo pins/USB-C, not magnetic connectors — note that magnetic breakaway lanyards conflict with CIED advice if worn over the implant); place the pod right-of-midline or mid-sternum away from a left-pectoral implant and keep ≥15 cm where possible; BLE at low transmit power is unlikely to be a problem but keep the ISO 14117 15 cm label guidance.
- Use a protected LiPo (cell with PCM, or TP4056 variant with DW01 protection), current-limited charging, an NTC on the cell to cut charging above ~45 °C, and charge only at the dock — never while worn.
- If a pendant is used, a non-magnetic mechanical breakaway clasp is mandatory; a chest band or vest-pocket clip avoids neck-cord risk altogether.

### Gaps
- ISO 14117 full text (RF test levels, 15 cm wording) not read; relying on HRS summary.
- No FDA MAUDE/CPSC strangulation statistics for medical-alert pendants found.
- IEC 62133 / BIS IS 16046 requirements for small wearable cells not retrieved.

## 6. Indian prices for components

### Takeaway
Core parts are cheap: ESP32-C3 SuperMini ~₹200–400, MAX30102 ~₹100–215, LIS3DH breakout ~₹150–265 (Adafruit ~₹742), TP4056 ~₹19. A chest pod with accelerometer + PPG + MCU + charger fits well under ₹1,000 in parts before battery, enclosure and band; LiPo, vibration motor, NTC and MPU6050 prices were not verified in this pass.

### Cited Findings
- ESP32-C3 SuperMini: Probots ₹242 incl. GST (₹237 at 5+) and ₹299 for another listing; Robosap ₹238; Techtonics ₹250; FlyRobo ₹329 (out of stock); Amazon.in (Roboduino) ₹399. — [Probots](https://probots.co.in/esp32-c3-supermini-wifi-bluetooth-development-board-32-bit-risc-v-uart-i2c-spi.html); [Probots alt](https://probots.co.in/esp32-c3-supermini-development-board-risc-v-wifi-bt-type-c.html); [Robosap](https://robosap.in/product/esp32-c3-super-mini-usb-c-type-development-board/); [Techtonics](https://techtonics.in/product/esp32-c3-super-mini-development-board-soldered-headers/); [FlyRobo](https://www.flyrobo.in/esp32-c3-supermini-development-board-wifi-bluetooth-usb-c-soldered); [Amazon.in](https://www.amazon.in/ROBODUINO-ESP32-C3-Super-Mini-Development/dp/B0G671727L)
- MAX30102: Robu.in ₹214 incl. GST (older listing ₹179); Roboway ₹85 + GST; DFRobot Fermion ₹1,449, Gravity ₹1,899 on Robu. — [Robu.in](https://robu.in/product/max30102-heart-rate-and-pulse-oximeter-sensor-module-black/); [Roboway](https://roboway.in/shop/max30102-pulse-oximeter-heart-rate-sensor-module/); [Robu DFRobot](https://stg.robu.in/product/dfrobot-fermion-max30102-heart-rate-and-oximeter-sensor-breakout/?add-to-cart=31464)
- LIS3DH: Evelta 7Semi ₹265.50 incl. GST; Robocraze 7Semi ₹265; ThinkRobotics ₹149.99; Indian Hobby Center ₹199 (sold out); Zbotic Adafruit ₹742; Zbotic guide range ₹200–450. DigiKey lists LIS3DH as obsolete (consider LIS2DH12/LIS2DW12-class successors). — [Evelta](https://evelta.com/evelta-lis3dh-triple-axis-mems-accelerometer-breakout-i2c-spi/); [Robocraze](https://robocraze.com/products/7semi-lis3dh-triple-axis-mems-accelerometer-breakout-module-i2c-spi); [ThinkRobotics](https://thinkrobotics.com/products/lis3dh-triple-axis-accelerometer); [Indian Hobby Center](https://www.indianhobbycenter.com/products/lis3dh-high-resolution-3-axis-accelerometer-module); [Zbotic Adafruit](https://zbotic.in/product/adafruit-lis3dh-triple-axis-accelerometer-2g-4g-8g-16g/); [Zbotic guide](https://zbotic.in/accelerometer-buying-guide-india-adxl345-vs-mpu6050-vs-lis3dh/); [DigiKey](https://www.digikey.in/en/products/detail/stmicroelectronics/LIS3DH/2334335)
- TP4056: Robu.in Type-C 1A with protection ₹19; Type-C without protection ₹19; Micro-USB ₹19; Micro-B ₹49. — [Robu Type-C w/ protection](https://robu.in/product/tp4056-1a-li-ion-lithium-battery-charging-module-with-current-protection-type-c/); [Robu Type-C](https://robu.in/product/tp4056-1a-li-ion-battery-charging-board-micro-usb-with-current-protection-type-c-connector/); [Robu Micro-B](https://robu.in/product/tp4056-1a-li-ion-lithium-battery-charging-module-micro-b-usb/)
- ESP32-C3 SuperMini expansion board on Robu: ₹134. — [Robu](https://aws.robu.in/product/esp32-c3-supermini-expansion-board/)

### Inferences
- Parts BOM sketch (verified items only): ESP32-C3 SuperMini ~₹240 + LIS3DH ~₹150–265 + MAX30102 ~₹100–215 + TP4056 ₹19 ≈ ₹510–740, leaving ~₹200–750 of a ₹700–1,500 budget for LiPo, vibration motor, NTC, enclosure, band/clip.
- An accelerometer-only pod (no PPG) cuts cost and power and removes the SpO2 claim temptation; LIS3DH (low-power, FIFO, wake-on-motion) suits overnight battery life better than MPU6050 (gyro draws more current) — power figures not verified here.
- TP4056 alone is a 1 A linear charger; for a small (200–500 mAh) cell the charge-current programming resistor should be changed to ~0.5C, otherwise overheating/aging risk — standard practice, not verified in a source here.

### Gaps
- Not retrieved/verified: MPU6050 (GY-521) price, small LiPo (e.g., 3.7 V 300–500 mAh) price, coin vibration motor price, 10k NTC thermistor price. From prior (unverified) knowledge, these are typically about ₹100–200, ₹150–350, ₹20–60 and ₹5–20 respectively on Robu/ElectronicsComp/Amazon.in — the report should label these as estimates or re-check retailer pages.
- MPU6050 production status (reportedly EOL) not verified.
- Prices from search-index snapshots; stock/GST status may have changed.
