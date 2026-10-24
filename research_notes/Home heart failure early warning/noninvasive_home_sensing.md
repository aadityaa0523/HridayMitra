# Non-invasive, low-effort home sensing for early warning of worsening heart failure

Scope note: 15 search and fetch calls. Figures come from peer-reviewed abstracts where possible, but often via secondary news coverage (TCTMD, Healio, MDedge) or a 2025 narrative review (PMC12565691). Company-sourced numbers are flagged **[company claim]**. Items I know from background knowledge but could not verify this session are listed under Gaps, not Findings.

## Smart scales: daily weight telemonitoring, BCG scales, foot-impedance and body-composition scales

### Takeaway
Daily weight alone is a weak early-warning signal. In FAST (2011), weight rules caught about 23% of HF events and produced 4.3 unexplained alerts per patient-year. Only 76% of patients weighed themselves daily. Adding foot-to-foot impedance plethysmography to a scale (Bodyport, SCALE-HF 1, 2024) roughly doubled sensitivity to 70% and cut alerts to 2.58 per patient-year. BCG-on-a-scale (Inan, Georgia Tech) can tell compensated from decompensated HF in a small proof-of-concept, but nobody has shown prospective lead time.

### Cited Findings
- **Chaudhry et al., Circulation 2007 (nested case-control, n=268 daily-weighing patients in a disease-management program):** Weight gain predicted HF hospitalization, compared with gain of 2 lb or less. Adjusted OR was 2.77 for 2–5 lb, 4.46 for 5–10 lb and 7.65 for >10 lb. Weight increases "begin at least 1 week before admission." The paper reports odds ratios, not sensitivity or specificity. — [PMC2892745](https://pmc.ncbi.nlm.nih.gov/articles/PMC2892745); [HealthDay](https://www.healthday.com/health-news/nutrition/weight-gain-may-spell-trouble-for-heart-failure-patients-608083.html); [clinician.com](https://www.clinician.com/articles/108420-weight-gain-predictor-of-heart-failure-hospitalization)
- **FAST, Abraham et al., Congest Heart Fail 2011;17(2):51–55 (n=156, ICD/CRT-D patients, 537±312 days):** This is the cleanest head-to-head number for weight rules. Adjusted sensitivity was 23% for daily weight vs 76% for implanted intrathoracic impedance. Weight predicted 13 of 65 HF events; impedance predicted 48 of 65. Unexplained detections were **4.3 per patient-year for weight** vs 1.9 for impedance. There were 890 weight threshold crossings vs 417 impedance crossings. Only **76% of patients complied with daily weighing**. — [MDedge](https://mdedge.com/content/impedance-beats-weight-predicting-hf-events); [HealthImaging](https://healthimaging.com/node/35542)
- A review summarizing FAST says "most studies demonstrate low sensitivity of daily weight monitoring," and that 62% of 65 adjudicated events were detected by impedance but not by weight. — [HealthImaging/HFSA](https://healthimaging.com/node/35542)
- **Bodyport Cardiac Scale, SCALE-HF 1 (Fudim, Duke; presented at THT 2024; prospective observational; 329 enrolled in 2021–2022 across 8 sites; 238 patient-years; 69 analyzable HF events):**
  - The scale fuses weight with foot impedance plethysmography (IPG) into a proprietary "congestion index."
  - Sensitivity for HF hospitalization or unplanned IV diuretic was **0.70 vs 0.35 for weight rules**. The weight rules were >3 lb in 1 day or >5 lb in 7 days.
  - **Alert rate was 2.58 vs 4.13 per patient-year.**
  - Lead time was not given at THT. Company and press reports later cite an average lead time of ~14 days and 38% fewer false alerts in J Card Fail **[company claim / press release]**.
  - Limitations: observational design; proprietary index; the presenter consults for Bodyport.
  - BCG was not part of SCALE-HF 1 and is planned for SCALE-HF 2.
  
  — [TCTMD 2024](https://www.tctmd.com/news/smart-scale-better-predicting-hf-events-weight-based-monitoring); [Healio 2024](https://www.healio.com/news/cardiology/20240313/scale-using-biosensor-technology-detects-hf-events-more-often-than-standard-of-care); [CLP Mag (press)](https://clpmag.com/disease-states/cardiovascular/heart-failure-monitoring-tech-doubles-sensitivity-for-predicting-events-versus-standard-of-care/); [Protocol NCT04882449](https://cdn.clinicaltrials.gov/large-docs/49/NCT04882449/Prot_000.pdf)
- **Inan group (Georgia Tech), IEEE TBME 2019, DOI 10.1109/TBME.2019.2935619 (n=43 HF patients):**
  - Proof-of-concept that ballistocardiogram (BCG) and ECG recorded on a modified bathroom scale can classify compensated vs decompensated HF with machine learning.
  - The key feature was beat-to-beat BCG variability across 20-second segments. The distinguishing information was in the mechanical BCG, not the ECG.
  - The exact classifier accuracy was not retrieved.
  
  — [Georgia Tech ECE news](https://ece.gatech.edu/news/2023/12/bathroom-scale-could-monitor-millions-heart-failure); [Newswise](https://www.newswise.com/articles/a-scale-could-monitor-millions-with-heart-failure)

### Inferences
- Weight rules (e.g., >2 kg in 3 days, or >3 lb/day or >5 lb/week) have a known performance envelope: sensitivity about 20–35%, about 4 or more unexplained alerts per patient-year, and about 76% daily adherence. Any new scale-based method should be benchmarked against this.
- Adding impedance or haemodynamic signals (IPG, BCG) to the scale step adds no patient effort, which is why scale-based multi-sensing looks attractive. The evidence is still one observational study (Bodyport) and one small classification study (Inan).
- Failure modes for scales, mostly from domain reasoning rather than cited data:
  - shoes or socks block foot-electrode impedance;
  - another household member steps on the scale, so the scale must identify the user;
  - weight shifts with time of day, meals and voiding;
  - weighing compliance falls off (76% in FAST);
  - changes in non-fluid weight (cachexia vs fluid) can hide fluid gain.

### Gaps
- I could not retrieve the full J Card Fail SCALE-HF 1 paper. Lead time, unexplained-alert rate and adherence are therefore press-reported only.
- "Zhang 2009" (often cited as weight-rule sensitivity of ~9% and specificity ~97%) could not be located or confirmed in this session. Treat it as unverified.
- The guideline wording for weight-gain rules (ESC "heartfailurematters" advice of >2 kg in 3 days) was not fetched. Cite it from the ESC 2021 guideline or its patient pages directly.
- No peer-reviewed accuracy data were found for consumer body-composition scales (Withings, Omron, Tanita segmental BIA) used to detect HF fluid.
- Tele-HF (Chaudhry NEJM 2010, a negative telemonitoring RCT) and BEAT-HF were not verified with numbers here. The 2025 review cites them only as "no added benefit."

## Bed, under-mattress and contact-free sensors (load cells, piezo/EMFi sheets, radar)

### Takeaway
Evidence that bed sensors predict HF decompensation at home is thin and small. The best-cited datum is EarlySense (piezo, under the mattress): nightly respiratory rate was the strongest risk-adjusted correlate of HF readmission (29 patients, 640 nights, 2015). Emfit QS is in a 24-patient prospective protocol (2024) with no results yet. Radar devices such as Sleepiz have FDA clearance for heart and respiratory rate measurement but no HF prediction data.

### Cited Findings
- **EarlySense, Bennett, Shao & Gorodeski, J Telemed Telecare 2015 (Cleveland Clinic, single-centre):**
  - A piezoelectric under-mattress sensor recorded respiration, heartbeat and movement after HF discharge (29 patients, 640 nights).
  - Average nightly respiratory rate was the most important risk-adjusted associate of HF readmission.
  - Sensitivity, specificity and lead time were not reported in the sources retrieved.
  
  — [PMC5221726](https://pmc.ncbi.nlm.nih.gov/articles/PMC5221726); [Fierce Biotech](https://www.fiercebiotech.com/medical-devices/cleveland-clinic-under-mattress-home-vitals-monitor-predicts-hospital-readmission); [Respiratory Therapy](https://respiratory-therapy.com/department-management/clinical/earlysense-home-monitoring-predicts-hospital-readmissions-hf/)
- **EarlySense in hospital (NICE MIB49, 2016):** Prediction of general ward deterioration, not HF, in one prospective study (n=113):
  - heart rate: sensitivity 82%, specificity 67%;
  - respiratory rate: sensitivity 64%, specificity 81%.
  
  Validation studies suggest heart and respiratory rate are measured accurately. — [NICE MIB49](https://www.nice.org.uk/advice/MIB49/chapter/Summary)
- **Emfit QS under-mattress sensor, JMIR Res Protoc 2024:**
  - Prospective protocol: 24 HF patients aged ≥70 who live alone, recruited after an HF decompensation admission.
  - Flagged changes in nocturnal heart rate, respiratory rate and motion trigger clinical review and NT-proBNP testing.
  - Sensitivity and specificity have yet to be calculated; no results were found.
  
  — [DOAJ / JMIR Res Protoc 2024](https://doaj.org/article/8e0dc6e287b7424b9082e7713beeaf3b)
- **Sleepiz One+ (radar, contact-free bedside):**
  - FDA 510(k) clearance (K223163) to measure heart rate and respiratory rate at rest or during sleep. It can be used at home by patients or caregivers.
  - It is "not indicated for active patient monitoring" and has no alarms.
  - No HF study was found.
  
  — [AASM](https://aasm.org/sleepiz-one-bedside-monitoring-device-receives-fda-clearance/); [510k summary](https://510k.innolitics.com/device/K223163)
- **ResMed SleepMinder (contactless RF, ESC 2014):** Used at home to diagnose sleep-disordered breathing in HF patients more accurately than a single hospital night **[company press release]**. It was not tested for decompensation prediction. — [ResMed IR](https://investor.resmed.com/news-events/press-releases/detail/246/esc-congress-2014-highlights-heart-failure-patients-with-sleep-disordered-breathing-more-accurately-diagnosed-through-at-home-contactless-sleepmindertm-device-than-single-hospital-based-assessment)

### Inferences
- Bed sensors cost the patient nothing in effort and capture the physiologically relevant overnight window: resting HR and RR, restlessness, orthopnoea and positional change. They are under-studied for HF decompensation, which is a clear gap a hackathon could target.
- Expected failure modes, from engineering reasoning and not cited:
  - a bed partner or pet adds signal;
  - thick mattress toppers or a sensor shifted under the mattress weaken the signal;
  - sleeping in a recliner or chair, common with orthopnoea, means the patient leaves the bed exactly when the HF signal appears;
  - nights away from home;
  - no reference standard for posture or orthopnoea.

### Gaps
- No peer-reviewed HF-decompensation sensitivity, specificity or lead time was found for these: Withings Sleep Analyzer, Dozee, Emfit, Sleepiz, load-cell bedpost systems (e.g., Beattie/Univ. Missouri TigerPlace hydraulic sensors), or UWB radar.
- Vivalink is a wearable patch, not a bed sensor. Its HF-specific data were not searched.

## Wearables: patches, vests, smartwatches and rings

### Takeaway
LINK-HF (2020) is the reference result for patches: a multisensor chest patch with ML gave 76–88% sensitivity, 85% specificity and a median 6.5-day lead time in 100 veterans. ZOLL HFMS (µCor, a radiofrequency lung-fluid patch) reduced 90-day HF readmissions by 38% in the non-randomized BMAD trial (2023). Consumer smartwatches and rings have no validated decompensation-prediction data yet; studies are feasibility-stage. Wear compliance is a recurring problem: about half of participants achieve full protocol compliance in activity-tracker studies.

### Cited Findings
- **LINK-HF, Stehlik et al., Circ Heart Fail 2020;13:e006513 (VitalConnect VitalPatch + PhysIQ ML; n=100 veterans, mean age 68, 4 VA sites, 90-day follow-up after HF discharge):**
  - Sensitivity was 76–88% and specificity 85%.
  - **Median lead time was 6.5 days (IQR 4.2–13.7).**
  - There were 35 unplanned non-trauma hospitalizations, 24 of them for worsening HF.
  - None of the 12 deaths was predicted.
  - Signals: ECG, bioimpedance, accelerometry/posture, temperature.
  - Limitation in the review: battery life, so patches need replacing. The false-alert rate was not reported.
  
  — [TCTMD](https://www.tctmd.com/news/stick-sensor-predicts-heart-failure-hospitalizations-pilot-study); [Cardiac Rhythm News](https://cardiacrhythmnews.com/wearable-sensor-analytics-platform-predicts-worsening-heart-failure-prior-to-hospitalisation/); [HCPLive](https://hcplive.com/view/wearable-patch-predicts-worsening-heart-failure); [Review PMC12565691, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)
- **ZOLL HFMS (µCor patch; radiofrequency lung fluid plus ECG, HR, RR, activity, posture). BMAD trial, presented ACC.23 (2023):**
  - Design: multicenter, prospective, concurrent-control, **not randomized**. Control arm BMAD-HF (n=245) wore the device with blinded data; intervention arm BMAD-TX (n=249) had data used in care.
  - Result: **38% reduction in 90-day HF readmission (p=0.03)**, and a 29% relative risk reduction at 1 year **[company page]**.
  - Only 70% of participants had ≥90-day follow-up.
  - No sensitivity or specificity figures were found.
  
  — [TCTMD](https://www.tctmd.com/news/wearable-device-helps-hf-patients-avoid-coming-back-hospital-bmad); [ZOLL clinical outcomes [company]](https://cardiac.zoll.com/medical-professionals/heart-failure-management-system/clinical-outcomes); [ZOLL press release 2023](https://www.zoll.com/news-releases/2023/03/06/results-from-bmad-heart-failure-trial-presented-as-acc23-wcc-late-breaking-clinical-trial)
- **ZOLL LifeVest (wearable defibrillator) HF prediction, Erath et al.:**
  - Sensitivity 69%, specificity 60%, NPV 94%.
  - **Median prediction window 32 days**, with a high false-positive rate.
  - A separate LifeVest analysis: a nocturnal resting HR rise of >5 bpm more than doubled the risk of CV hospitalization or mortality.
  
  — [Review PMC12565691, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)
- **MUSIC study (non-invasive multisensor adherent patch; a historical comparator):** Validation-cohort sensitivity 63%, specificity 92%, **0.9 false positives per patient-year**. Single-parameter algorithms reached >60% sensitivity but had high false-positive rates. — [Review PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)
- **Smartwatch, wrist PPG and ECG (from the 2025 review):**
  - Shah et al.: PPG pilot, AUC 0.92 for HFrEF vs non-HF and 0.85 for HFpEF vs non-HF. It could not separate acute from chronic HF. Limitations were motion artefact and daytime gaps.
  - Circadian PPG ML: AUC ~0.74 for predicting decompensation.
  - Hasumi et al.: Apple Watch-type single-lead ECG CNN, 91.6% accuracy for NYHA I–II vs III–IV. This classifies severity; it does not predict decompensation.
  
  — [Review PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)
- **Apple Watch HF study, Göttingen (NCT06819618):**
  - Feasibility study: n=32, started April 2024, estimated completion May 2025.
  - Inputs: ECG, SpO2, RR, steps, nocturnal temperature.
  - The group reports good acceptance, and that daily steps correlate with 6-minute walk distance. No predictive performance has been published.
  
  — [ClinicalTrials.gov](https://clinicaltrials.gov/study/NCT06819618); [Review PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)
- **Activity and accelerometry:**
  - Fewer than 4,889 steps/day indicated cardiac mortality risk (Izawa).
  - Non-sedentary awake time was 9% after decompensation vs 27% in stable HF and 34% in controls (Nelson).
  - **Wear compliance:** in Young et al., wear time was >15 h/day, but **only about half of participants achieved full protocol compliance**. Lower compliance was associated with higher BNP and rehospitalisation, so missing data is itself informative.
  - Step counts vary substantially between devices (ICC ~0.80).
  - In WATCHFUL, step counts rose without any change in NT-proBNP or 6MWT.
  
  — [Review PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)
- **Regulatory landscape:** Scholte et al. identified only 8 RCTs of HF wearables and found only two FDA-approved wearables designed specifically for HF remote monitoring. — [Review PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)
- **Expected window:** Congestion symptoms typically appear about 3–7 days before hospitalization. This is the window wearables aim to catch. — [Review PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)

### Inferences
- Patch and vest systems trade patient effort for sensitivity: replacing adhesive patches, battery life, skin irritation and wear compliance. LINK-HF lasted 90 days in motivated veterans; real-world adherence beyond 3 months is undocumented in these sources.
- Consumer watches and rings are everywhere, but nobody has shown prospective HF decompensation prediction with them. Combining nocturnal resting HR (rise >5 bpm), RR and activity decline is the most plausible signal set; it mirrors the LifeVest and LINK-HF features.
- A missing-data pattern (device not worn) may carry signal, because lower compliance correlates with worse BNP.

### Gaps
- No sensitivity, specificity or lead time was found for Oura or Samsung rings, Fitbit, Withings ScanWatch or Apple Watch in HF decompensation.
- Vivalink patch HF-specific data were not searched.
- Device costs were not found. The review describes cost only qualitatively.
- LINK-HF false alerts per patient-year and patch adherence percentage were not retrieved.

## Thoracic and whole-body bioimpedance and dielectric devices (ReDS, vests, Edema Guard)

### Takeaway
ReDS (remote dielectric sensing) measures lung fluid in about 90 seconds to 3 minutes with a vest. It correlates moderately with CT (r=0.65) and has low sensitivity (46%) but good specificity (88%) for detecting acute HF in the ED. Outcome trials are mixed: one small study found 87% fewer hospitalizations compared with before enrolment, and SMILE-HF reported 58% fewer readmissions **[company claim]**, but Bensimhon found no 30-day benefit. Non-invasive thoracic impedance vests (e.g., SENTINEL-HF) show associations with readmission but no validated alert performance. The review flags bioimpedance alone as producing "high false positives."

### Cited Findings
- **ReDS vs CT, Imamura et al., J Clin Med 2021 (n=46 inpatients):** Moderate correlation with CT high-attenuation area, r=0.65, regardless of HF status. Accuracy in small-bodied patients was uncertain. — [PMC8745965](https://pmc.ncbi.nlm.nih.gov/articles/PMC8745965/)
- **ReDS in ED dyspnoea (n=97; Region H Denmark):** At a cutoff >35%, sensitivity was 46%, specificity 88% and accuracy 71% for acute HF, similar to the Boston score and lung ultrasound. A negative reading does not rule out HF. — [Region H research](https://research.regionh.dk/en/publications/remote-dielectric-sensing-to-detect-acute-heart-failure-in-patien/)
- **SMILE-HF (RCT, 268 patients, 43 US centres, daily home ReDS after ADHF discharge):** Reported 58% of HF readmissions prevented **[company-linked announcement; full peer-reviewed numbers not verified]**. — [Medthority 2019](https://www.medthority.com/news/2019/10/smile-hf-trial-of-reds-shows-reduction-in-readmission-for-heart-failure---medicure/)
- **Amir et al. (continuous home ReDS):** HF hospitalizations fell 87% vs the pre-enrolment period and 79% vs the post-enrolment period. This is an observational before/after design. — [Review PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)
- **Mixed ReDS outcome evidence:**
  - Bensimhon et al.: ReDS-guided diuretics did **not** reduce 30-day rehospitalization.
  - Lala et al.: lower 30-day CV readmission.
  - ReDS-SAFE HF: discharge at ReDS ≤35% was associated with fewer HF events.
  - Sattar et al. meta-analysis: significant reduction in rehospitalization.
  - **ReDS failure modes:** the reading takes about 3 minutes, depends on posture, and is higher in the morning.
  
  — [Review PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)
- **SENTINEL-HF (non-invasive thoracic impedance vest; n=180; daily 45-second measurement for 45 days after discharge):** Declining or persistently low impedance was associated with higher 30-day readmission. Adherence was described as "good" without a percentage. — [Review PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)
- **Gastelurrutia et al.:** Discharge thoracic impedance <20 Ω was associated with worse outcomes and pump-failure death. — [Review PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)
- **Bioimpedance alone produces high false positives** (review Table 2). Implanted impedance alerts alone (OptiVol) did not reduce admissions or mortality in RCTs. In the SENSE-HF phase I, OptiVol sensitivity was only 20.7% (12 of 58 HF hospitalizations). — [Review PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/); [NCT00400985](https://clinicaltrials.gov/study/NCT00400985)
- **Non-invasive lung impedance device (Shochat-type), 2019 case series:** Prior studies with this device reduced HF hospitalizations. Only case-series-level evidence was retrieved. — [Univ. Porto repository](https://repositorio-aberto.up.pt/handle/10216/85148)
- A Philips wearable trans-thoracic bioimpedance feasibility study found bioimpedance was the most predictive measurement before HF admissions. No numbers were retrieved. — [PMC8135018](https://pmc.ncbi.nlm.nih.gov/articles/PMC8135018)

### Inferences
- Lung-fluid-specific sensing (ReDS, µCor RF) has outcome-trial support, while generic impedance mostly has association data. Specificity is the weak point of impedance alone, which argues for multi-parameter fusion (impedance plus HR, RR and activity), as in LINK-HF and MUSIC.
- Posture and time-of-day dependence (ReDS higher in the morning) mean any home protocol must fix the measurement time and posture.

### Gaps
- No primary peer-reviewed data were retrieved for the Edema Guard Monitor, the IMPEDANCE-HF trial (Shochat, Eur J Heart Fail 2016) or SENSIBLE-HF. Recall-based figures for these should be verified before use.
- ReDS device cost and per-patient reimbursement were not found.
- No peer-reviewed data were found for whole-body or segmental BIA (e.g., home BIA scales) in HF.

## Cross-cutting comparison: effort, performance and failure modes

### Takeaway
Across modalities, published non-invasive home HF predictors cluster at about 63–88% sensitivity, 60–92% specificity, a median lead time of about 6.5 days (LINK-HF) or longer for vests (32 days, LifeVest), and roughly 0.9–4.3 alerts per patient-year. Weight alone sits at the bottom (23–35% sensitivity, 4.1–4.3 alerts per patient-year). Wear and use compliance (about 50–76%) is the dominant real-world failure mode.

### Cited Findings
| Approach (year) | Patient effort | Sens. | Spec. | Lead time | False/unexplained alerts per pt-yr | Source |
|---|---|---|---|---|---|---|
| Daily weight rules, FAST (2011) | Daily step-on; 76% compliant | 23% | n/r | n/r | 4.3 | [MDedge](https://mdedge.com/content/impedance-beats-weight-predicting-hf-events) |
| Weight rules, SCALE-HF 1 comparator (2024) | Daily step-on | 35% | n/r | n/r | 4.13 (all alerts) | [TCTMD](https://www.tctmd.com/news/smart-scale-better-predicting-hf-events-weight-based-monitoring) |
| Bodyport scale (weight + foot IPG), SCALE-HF 1 (2024) | Daily barefoot step-on | 70% | n/r | ~14 d **[press]** | 2.58 (all alerts) | [TCTMD](https://www.tctmd.com/news/smart-scale-better-predicting-hf-events-weight-based-monitoring) |
| Inan BCG scale (2019) | Daily step-on, ~1 min | n/r (classification only) | n/r | n/r | n/r | [GT news](https://ece.gatech.edu/news/2023/12/bathroom-scale-could-monitor-millions-heart-failure) |
| LINK-HF patch (2020) | Continuous adhesive patch | 76–88% | 85% | median 6.5 d | n/r | [TCTMD](https://www.tctmd.com/news/stick-sensor-predicts-heart-failure-hospitalizations-pilot-study) |
| MUSIC patch | Continuous adhesive patch | 63% | 92% | n/r | 0.9 | [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/) |
| ZOLL LifeVest (Erath) | Wear vest ~24 h | 69% | 60% | median 32 d | "high" | [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/) |
| ZOLL HFMS µCor, BMAD (2023) | Continuous RF patch | n/r | n/r | "days–weeks" | n/r; outcome −38% 90-d readmission (non-randomized) | [TCTMD](https://www.tctmd.com/news/wearable-device-helps-hf-patients-avoid-coming-back-hospital-bmad) |
| ReDS vest (ED, 2021–22) | ~1.5–3 min seated, daily | 46% (diagnostic) | 88% | n/a | n/r | [Region H](https://research.regionh.dk/en/publications/remote-dielectric-sensing-to-detect-acute-heart-failure-in-patien/) |
| EarlySense under-mattress (2015) | Zero effort | n/r (RR was top predictor) | n/r | n/r | n/r | [PMC5221726](https://pmc.ncbi.nlm.nih.gov/articles/PMC5221726) |
| Implanted impedance, for reference (FAST 2011) | None (implant) | 76% | n/r | n/r | 1.9 | [MDedge](https://mdedge.com/content/impedance-beats-weight-predicting-hf-events) |

(n/r means not reported in the sources retrieved.)

- **Documented failure modes:**
  - LINK-HF missed all 12 deaths [TCTMD](https://www.tctmd.com/news/stick-sensor-predicts-heart-failure-hospitalizations-pilot-study).
  - Patch battery life [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/).
  - PPG motion artefact and daytime gaps [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/).
  - Stethoscope and PCG displacement with activity [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/).
  - ReDS depends on posture and time of day [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/).
  - Weight compliance of 76% [MDedge](https://mdedge.com/content/impedance-beats-weight-predicting-hf-events).
  - Activity-wearable full compliance of about 50%, worse in sicker patients [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/).
  - Bioimpedance alone produces high false positives [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/).
  - Step counts vary between devices [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/).
- **Telemonitoring outcomes context:** TIM-HF was neutral on mortality and HF hospitalization. TIM-HF2 reduced days lost to unplanned CV hospitalization and all-cause mortality. Detection alone does not guarantee benefit. — [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)

### Inferences
- **Gaps a hackathon could target:**
  1. Zero-effort bed or under-mattress and radar sensing has almost no HF-specific validation, yet it captures nocturnal HR, RR and orthopnoea.
  2. No study handles multi-occupant contamination (partner in bed, family on scale) explicitly.
  3. Fusing cheap consumer signals (scale weight, watch nocturnal HR, steps) has not been prospectively tested against the weight-rule baseline (sensitivity about 23–35%, about 4 alerts per patient-year).
  4. Missingness (non-wear, skipped weighing) as an early-warning feature is unexplored, although low compliance tracks worse BNP.
- A realistic target for a new system is to beat about 35% sensitivity at ≤2.5 alerts per patient-year with a lead time of ≥7 days. That would match or beat Bodyport and LINK-HF while requiring less patient effort than a patch.

### Gaps
- Few studies report false alerts per patient-year consistently: LINK-HF, LifeVest and BMAD do not report them in the sources retrieved.
- Real-world costs are largely unreported. Commonly quoted figures (e.g., Withings Sleep Analyzer about $100–130, ReDS service reimbursement) were not verified this session.
- No sources were found that quantify failure from blankets or pillows, partners in bed, shoes on scales, or meal and hydration timing for any of these devices. Those failure modes are inferred, not documented.
