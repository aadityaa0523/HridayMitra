# Implant-based HF early-warning benchmarks and alert-algorithm design (low false detections)

Research notes, compiled 2026-10-24. About 15 tool calls. Several figures come from search-engine summaries of abstracts or sponsor pages rather than full texts. Each item says so where that applies.

## Benchmarks: HeartLogic, OptiVol/CareLink, TriageHF, CardioMEMS (sensors, index construction, numbers)

### Takeaway
The reference numbers to beat come from HeartLogic, validated in MultiSENSE (Boehmer et al., JACC HF, 2017): 70% sensitivity, 1.47 unexplained alerts per patient-year, and a median lead time of 34 days. It fuses five sensor groups against a moving personal baseline and uses hysteresis: it alerts when the index reaches 16 and re-arms when it falls to 6. OptiVol (impedance alone) achieves about 76% sensitivity with about 1.9 unexplained detections per patient-year. Weight alone reaches about 23% sensitivity with 4.3 unexplained detections per patient-year. CardioMEMS is an outcome benchmark (fewer hospitalisations), not an alert-accuracy benchmark.

### Cited Findings
**HeartLogic, MultiSENSE (Boehmer et al., JACC: Heart Failure, March 2017; funded by Boston Scientific)**
- The study had a development cohort and a held-out test cohort. The pre-specified coprimary endpoints were sensitivity above 40% for HF events and an unexplained alert rate below 2 per patient-year. — [PSU Pure record](https://pure.psu.edu/en/publications/a-multisensor-algorithm-predicts-heartfailure-events-in-patients-/); [Boston Scientific MultiSENSE page](https://www.bostonscientific.com/en-US/medical-specialties/electrophysiology/heartlogic-heart-failure-diagnostic/clinical-data/multisense.html)
- Test-cohort results: sensitivity 70% (95% CI 55.4–82.1%); unexplained alert rate 1.47 per patient-year (95% CI 1.32–1.65); median lead time 34.0 days (IQR 19.0–66.3). The test cohort had 320 patient-years of follow-up and 50 HF events. — [PSU Pure](https://pure.psu.edu/en/publications/a-multisensor-algorithm-predicts-heartfailure-events-in-patients-/); [HeartLogic Clinical Compendium (sponsor)](https://www.bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heartfailure-diagnostic-ep/HeartLogic-Clinical-Compendium.pdf)
- Development cohort (secondary summary): 82% sensitivity and 1.33 unexplained alerts per patient-year. This was not verified in the full text. — [EP Lab Digest / HMP](https://www.hmpgloballearningnetwork.com/site/eplab/multisensor-device-based-monitoring-patients-systolic-heart-failure)
- MultiSENSE also reported 17% of time in alert and a PPV of 11.3%. These figures are cited in a later HeartLogic cohort paper. — [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)
- MultiSENSE event-accounting rules: an alert counts as a true positive if it began before the event and did not reset more than 30 days before the event. HF events count only if they occur at least 45 days after sensor data collection starts. — [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)

**HeartLogic index construction**
- Inputs:
  - accelerometer heart sounds: S3 (filling pressure), S1 (contractility)
  - intrathoracic impedance (RV lead to can)
  - respiratory rate, and RSBI (respiratory rate divided by tidal volume)
  - night heart rate (midnight to 6 am)
  - activity (hours active per day)

  Heart sounds are sampled every 20 minutes at rest and impedance every 2 minutes, then aggregated daily. — [Boston Scientific multi-sensor page](https://www.bostonscientific.com/en-EU/medical-specialties/electrophysiology/heartlogic-heart-failure-diagnostic/multi-sensor-technology.html); [HeartLogic IPDF (sponsor PDF)](https://www.bostonscientific.com/content/dam/bostonscientific/corporate/cardiovascular-resources/CRM-1143002-AB_HeartLogicIPDF_MAY22FINAL.pdf)
- Each day, each sensor is compared with a moving personal baseline to score its worsening, and the scores are combined into a composite index on a 0–100 scale. The index is unavailable for the first 30–37 days, which is the baseline-learning period. — [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)
- An alert fires when the index crosses a programmable threshold (nominal 16). Once in alert, the threshold automatically drops to a recovery value (nominal 6). This is hysteresis: the alert clears only after the index falls below 6, and only then can a new alert fire. — [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441); [HeartLogic Alert Guide (sponsor)](https://www.bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heartfailure-diagnostic-ep/CRM-499506-AC-HeartLogic-Alert-Guide.pdf)
- The manufacturer says the index responds slowly to rapid changes because of long-term averaging, and should not be used for day-to-day management. — [HeartLogic IPDF](https://www.bostonscientific.com/content/dam/bostonscientific/corporate/cardiovascular-resources/CRM-1143002-AB_HeartLogicIPDF_MAY22FINAL.pdf)
- The exact sensor weights, baseline window lengths and per-sensor thresholds are not public in the sources found.

**HeartLogic, later cohorts**
- Single-centre early-experience cohort (PMC6437441):
  - 58 patients, about 24 patient-years.
  - 24 threshold crossings, which is 0.99 per patient-year.
  - Unexplained alerts: 0.41 per patient-year. PPV 58%. Time in alert 12%.
  - Median warning before HF hospitalisation 38 days (IQR 15–61); before minor HF events 12 days (IQR 1–19).
  - Median peak index: 40 for hospitalisations, 24 for minor events.

  — [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)
- In that cohort, every alert case showed a rise in S3 and a fall in S1. Night heart rate rose in 15 alerts, respiratory rate or RSBI worsened in 12, and impedance fell in 11; impedance was a low-sensitivity signal. — [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)
- MANAGE-HF Phase I (Hernandez et al., J Card Fail, 2022):
  - 200 patients; 585 alert cases over 333 patient-years, which is 1.76 alert cases per patient-year.
  - HF medications were augmented in 74% of alert cases; 89% of those augmentations were diuretics.
  - Serious adverse events from alert-prompted changes: 0.015 per patient-year.
  - HF hospitalisations fell compared with the 12 months before enrolment (rate ratio 0.33, 95% CI 0.23–0.47). This is a pre/post comparison, not a randomised one.

  — [Duke Scholars](https://scholars.duke.edu/publication/1519187); [Boston Scientific MANAGE-HF page](https://www.bostonscientific.com/en-EU/medical-specialties/heart-failure/heartlogic-heart-failure-diagnostic-hfc/clinical-data/manage-hf.html)
- Italian real-world study (366 patients, 22 centres): 273 alerts (0.76 per patient-year) in 150 patients. Clinical action followed 43% of alerts, and taking action was associated with fewer HF events. — [Boston Scientific clinical-evidence newsletter (secondary)](https://www.bostonscientific.com/en-EU/medical-specialties/electrophysiology/clinical-evidence-newsletter/2023/3.html)
- An eight-centre study reported 242 alerts (0.8 per patient-year) in 123 patients. — [PMC9175259](https://pmc.ncbi.nlm.nih.gov/articles/PMC9175259)

**OptiVol (Medtronic intrathoracic impedance fluid index) and FAST**
- FAST trial: OptiVol had 76% per-patient sensitivity versus 23% for weight monitoring. Unexplained detection rate was 1.9 per patient-year for OptiVol versus 4.3 for weight. — [Cardiac Rhythm News](https://cardiacrhythmnews.com/?p=4954)
- A secondary citation reports 77% sensitivity for HF hospitalisation with 1.5 false-positive alerts per patient-year. It is unclear whether this is from SENSE-HF. — [PMC3796699](https://pmc.ncbi.nlm.nih.gov/articles/PMC3796699)
- A real-world single-centre study found that 79.6% of alerts were unexplained, a rate of 1.27 per person-year. — [Kansas J Med](https://journals.ku.edu/kjm/article/download/11418/10825)
- The SENSE-HF registry entry (NCT00400985) describes a blinded phase to estimate sensitivity and PPV. No results are posted there. — [ClinicalTrials.gov NCT00400985](https://clinicaltrials.gov/study/NCT00400985)

**TriageHF / TriageHF Plus (Medtronic HF Risk Score)**
- Inputs come from ICD and CRT-D devices: intrathoracic impedance, intracardiac electrogram data, and accelerometer activity. The score estimates the risk of a worsening-HF hospitalisation in the next 30 days. A high score triggers a structured phone triage call. — [NICE MIB298, 2022](https://www.nice.org.uk/advice/mib298/chapter/Clinical-and-technical-evidence)
- Single-centre pathway results:
  - Phone contact was made in 127 of 157 high-score cases (80.9%); 70.9% of those had worsening HF or another acute problem.
  - Admission rates per person-year versus historical controls:

    | Admission type | TriageHF Plus | Historical controls | p |
    |---|---|---|---|
    | All-cause | 0.41 | 0.57 | 0.001 |
    | Cardiovascular | 0.14 | 0.29 | 0.037 |
    | HF | 0.02 | 0.07 | 0.003 |

  — [NICE MIB298](https://www.nice.org.uk/advice/mib298/chapter/Clinical-and-technical-evidence)
- Optum/CareLink analysis (n = 22,901): risk tiers for an HF event within 6 months were low (<5.4%), medium (5.4% to <20%) and high (≥20%). — [NICE MIB298](https://www.nice.org.uk/advice/mib298/chapter/Clinical-and-technical-evidence)
- One summary reports a specificity of 63.4% and PPV of 55.9%; the score is tuned to accept false positives in order to avoid false negatives. NICE notes that all evidence is observational, mostly from one group, with company-linked authors. — [NICE MIB298](https://www.nice.org.uk/advice/mib298/chapter/Clinical-and-technical-evidence)

**SELENE HF (Biotronik, Europace 2021)**
- Inputs: day and night heart rate, activity, HRV and thoracic impedance, combined with baseline risk.
- C-statistic 0.89 in the derivation group.
- Validation: sensitivity 65.5% with a median alert time of 42 days; false or unexplained alerts were common.

— [search summary of ESC365 / Europace abstract](https://esc365.escardio.org/journal/53445). Not verified in full text.

**CardioMEMS (pulmonary artery pressure; outcome benchmark, not an alert algorithm)**
- CHAMPION (Abraham et al., Lancet, 2011):
  - 550 NYHA III patients at 64 US centres.
  - 6-month HF hospitalisation rate 0.32 versus 0.44; HR 0.72 (95% CI 0.60–0.85), p = 0.0002. That is about a 28% reduction, with 84 versus 120 events (some summaries report 83).
  - Over a mean 15 months: 37% reduction (158 versus 254 events, HR 0.63).

  — [Lancet PDF mirror](https://s.mriquestions.com/uploads/3/4/5/7/34572113/cardiomems_piis0140673611601013.pdf); [ACC CHAMPION summary](https://www.acc.org/Latest-in-Cardiology/Clinical-Trials/2015/12/29/12/44/CHAMPION)
- GUIDE-HF (Lancet, 2021):
  - 1,000 patients randomised (497 to haemodynamic-guided care, 503 to standard care).
  - The primary composite of mortality and HF events was not met overall.
  - Pre-COVID-19 analysis: 28% reduction in HF hospitalisations.

  — [ACC GUIDE-HF](https://www.acc.org/Latest-in-Cardiology/Clinical-Trials/2021/08/25/23/01/GUIDE-HF); [TCTMD](https://www.tctmd.com/news/guide-hf-pulmonary-artery-sensor-may-help-mild-hf-covid-19-muddies-water)

### Inferences
- Benchmark table for the team:

  | System | Sensitivity | Unexplained alerts | Lead time |
  |---|---|---|---|
  | HeartLogic | 70% | 1.47 per patient-year | 34 days |
  | OptiVol | 76% | 1.9 per patient-year | — |
  | Weight-only telemonitoring | 23% | 4.3 per patient-year | — |
  | SELENE HF | 65.5% | — | 42 days |

  A non-invasive home system that matches HeartLogic's 70% sensitivity at fewer than 2 false alerts per patient-year would be very strong. A realistic hackathon target is to beat the weight-only rule.
- HeartLogic's design pattern is worth copying directly: a per-sensor deviation from a moving personal baseline, summed into a composite, with a warm-up period of about 30 days and a high/low hysteresis pair (16 and 6).

### Gaps
- The exact HeartLogic sensor weights and baseline windows were not found in public sources; they are proprietary.
- The primary SENSE-HF results paper was not retrieved.
- TriageHF lead time and false alerts per patient-year were not found.

## Alert-logic best practice: personal baselines, fusion, persistence, re-arming, SQI, missing data, explainability

### Takeaway
The strongest published comparison of home-telemonitoring algorithms is Cuba Gyllensten et al. (JMIR Med Inform, 2016). Trend detectors (MACD, CUSUM) on a personal baseline beat simple "+2 kg" rules, and impedance beat weight. The paper gives exact optimal parameters that the team can reuse. HeartLogic supplies the hysteresis and re-arming model, and NOTICE-HF suggests variability (SD) features in addition to mean shifts.

### Cited Findings
- Gyllensten 2016 setup:
  - 91 HF patients (of 108 with the system installed), mean 10 months of monitoring.
  - Daily weight and a non-invasive transthoracic bio-impedance (NITTI) vest.
  - 24 adjudicated HF hospitalisations in 19 patients.

  — [PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)
- Optimal parameters found:

  | Algorithm | Weight | NITTI (log ohm) |
  |---|---|---|
  | Rule of thumb (current value minus value d days earlier) | >2.7 kg over 17 days | < −0.27 over 21 days |
  | MACD (short-window mean minus long-window mean) | >0.62 kg (Ns = 9, Nl = 20) | < −0.059 (Ns = 9, Nl = 35) |
  | CUSUM (running mean/SD window d, depreciation c) | >8.7 (10-day window, c = 0.75) | < −7.8 (20-day window, c = 0.75) |

  — [PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)
- Cross-validated performance:

  | Algorithm | Sensitivity | Specificity | PPV | NPV |
  |---|---|---|---|---|
  | Weight-MACD | 33% | 91% | 3.2% | 99.3% |
  | NITTI-CUSUM | 60% | 96% | 10.9% | 99.6% |
  | Weight-RoT | 20% | — | — | — |
  | NITTI-RoT | 33% | — | — | — |

  NITTI-CUSUM gave about 0.48 false alarms per patient-year. Parameters were chosen to maximise AUC at specificity above 95%, with thresholds at the Youden point under the constraint of specificity above 90%. — [PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)
- Missing-data handling in Gyllensten 2016:
  - Periods with fewer than 3 measurements per week were excluded.
  - Gaps were filled by linear interpolation using only data that would have been available in real time (no look-ahead).
  - Start-up periods, end periods and post-discharge periods were removed.
  - Impedance was log-transformed for skew.

  — [PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)
- In a simulated case-management study using the same data, clinicians reviewed caseloads under different rules: a simple "+2 kg in 3 days" rule, a weight moving-average (MACD) rule and a bio-impedance CUSUM rule. Simple sudden-change rules produced many alerts with poor sensitivity. — [PMC5240411](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5240411/)
- Hysteresis and re-arming: HeartLogic alerts at 16 and drops to a recovery threshold of 6 once in alert. — [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)
- MultiSENSE reports only "unexplained" alerts as false alerts, which requires adjudicating each alert against clinical events. — [PSU Pure](https://pure.psu.edu/en/publications/a-multisensor-algorithm-predicts-heartfailure-events-in-patients-/)
- NOTICE-HF (respiratory rate from ICD and CRT-D devices):
  - Daily maximum, median and minimum respiratory rate rose by about 1.5–2.1 breaths per minute before HF events.
  - A 1-month SD of median respiratory rate above 1.0 breath per minute gave a hazard ratio of 12.3 for an HF event within 30 days.

  — [Springer, J Interv Card Electrophysiol (search summary)](https://www.link.springer.com/article/10.1007/s10840-015-9983-6)
- Explainability: HeartLogic reports present which sensor contributed (for example, rising S3 or falling impedance), and clinicians act on the contributing sensors. — [Boston Scientific multi-sensor page](https://www.bostonscientific.com/en-EU/medical-specialties/electrophysiology/heartlogic-heart-failure-diagnostic/multi-sensor-technology.html); [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)

### Inferences
These are design recommendations synthesised from the findings above. They are not individually validated in a study.
- Personal baseline: for each signal, compute a robust baseline as the rolling median over 20–35 days (cf. the MACD long windows of 20–35 days). Measure spread with MAD × 1.4826, which approximates SD. Exclude the current suspected-event window from the baseline (a lag of about 7 days) so that slow drift does not pull the baseline toward the event. Require about 30 days of warm-up before alerting, as HeartLogic does.
- Per-signal score: robust z = (short EWMA or 7–9-day mean − baseline median) / (1.4826 × MAD), signed by the direction of worsening:
  - weight ↑
  - night HR ↑
  - RR ↑
  - activity ↓
  - impedance ↓
  - HRV ↓

  Clip each z at 0 so that improvement cannot cancel out worsening, then sum the signals (optionally weighted) to form a HeartLogic-like composite. A CUSUM on the composite captures slow, persistent drift.
- Persistence and hysteresis: fire only when the composite stays above the high threshold for at least N of the last M days (for example, 2 of 3). Clear only when it falls below a low threshold (about 40% of the high threshold, mirroring 16 and 6). Suppress a new alert for the same episode until the alert has cleared.
- Signal quality (SQI) gating: drop or down-weight days where:
  - the signal quality index is low (ECG/PPG from NeuroKit2 quality functions)
  - fewer than X valid minutes were captured
  - the weight was taken by a different user
  - the reading is a physiologically implausible jump (for example, weight changing by more than 3 kg/day without a corroborating trend)

  Missing days should not reset the baseline. Use last-available, causal interpolation as Gyllensten did, but cap the length of gap that is imputed.
- Variability feature: add a rolling 30-day SD of respiratory rate and heart rate (NOTICE-HF).

### Gaps
- No published head-to-head comparison of rolling median/MAD versus EWMA versus CUSUM specifically for wearable HR/RR was found.
- No published SQI-gating method specific to HF telemonitoring was found.

## Confounders and false-alert causes, and how studies handled them

### Takeaway
Device studies classify alerts as "explained" (by a clinical event) or "unexplained" and report only unexplained alerts as false. Documented causes of alerts not due to HF include new atrial fibrillation, stopping or reducing HF therapy, changes in activity or sleep habits, and device or lead problems. AF and chronic kidney disease predict more alerts. Infection (COVID-19) produces a distinct pattern: a much larger rise in night HR and a larger fall in activity.

### Cited Findings
- Alert causes in a HeartLogic cohort:
  - 10 "unexplained" alerts followed HF therapy being stopped or reduced (n = 5), or other events affecting clinical status or sensor data.
  - Other listed causes: new-onset AF, changes in activity or sleep habits, stopping multisite pacing because of phrenic stimulation, Twiddler's syndrome, and RV lead dislodgement.

  — [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)
- In an Italian multicentre analysis (568 ICD patients), AF at implant and CKD independently predicted HeartLogic alerts. Alerts remained associated with cardiovascular hospitalisation or death regardless of AF or CKD status. — [Boston Scientific newsletter (secondary)](https://www.bostonscientific.com/en-EU/medical-specialties/electrophysiology/clinical-evidence-newsletter/2023/3.html); [Bertini et al., HRJ 2022 proof](https://ricerca.uniba.it/retrieve/4a283bc7-cf07-4baf-952e-18de9d9fa29e/Bertini_HRJ2022_Proof.pdf)
- Gardner et al. (ESC Heart Failure, 2021) used data from MultiSENSE, PREEMPT-HF and MANAGE-HF. In COVID-19, night HR rose about 3–4 times more than in HF or pneumonia events, and activity fell more. This means infection can be partly separated from HF by its sensor pattern. — [Gardner ESC-HF 2021 (sponsor PDF)](https://www.bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heart-failure-diagnostic/heartlogic-newsletter/issue-7-2021/Gardner_ESC-HF_2021.pdf); [PSU Pure](https://pure.psu.edu/en/publications/multiparameter-diagnostic-sensor-measurements-in-heart-failure-pa/)
- Weight-based rules have a high unexplained-detection rate (4.3 per patient-year in FAST). Gyllensten found no significant weight difference in the 2 weeks before decompensation (83 versus 84 kg, p = 0.97). — [Cardiac Rhythm News](https://cardiacrhythmnews.com/?p=4954); [PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)
- In a secondary analysis of a rural RCT, a 5 lb gain over 7 days was associated with ED visits but not with readmission; dyspnoea predicted both better. — [Flinders (search summary)](https://researchnow.flinders.edu.au/en/publications/rapid-5lb-weight-gain-is-not-associated-with-readmission-in-patie/)

### Inferences
- Model confounders explicitly in the synthetic data and the engine:
  - Fever or infection: HR ↑ and RR ↑ with an abrupt onset (1–3 days), temperature ↑, little weight change, activity ↓. A large night-HR jump without weight or impedance drift suggests infection rather than HF.
  - Salty meal: weight ↑ 0.5–1.5 kg that reverses within 1–3 days. A persistence rule plus MACD should ignore it.
  - AF onset: an abrupt HR step with high RR-interval irregularity. Flag it as a separate "rhythm" alert rather than an HF alert, and pause the HR baseline update.
  - Diuretic or medication change: log it as an event marker. Reset or freeze the baseline for about 7 days.
  - Dehydration: weight ↓ with HR ↑.
  - Scale misuse or a clothing change: a single-day jump of more than 1.5 kg that does not persist.
  - Another person on the device: weight outside the user's band, caught by an identity check.
- Expose a "probable explanation" field (infection-like, AF-like, transient sodium load) so that clinicians can dismiss explained alerts. This mirrors the MultiSENSE explained/unexplained adjudication.

### Gaps
- No quantitative studies were found on menstrual, weather or seasonal effects on HF telemonitoring false alerts. The search was not deep on this.
- Infection as a cause of HeartLogic false alerts is documented only for COVID-19, in sponsor-linked data.

## Patient identification on shared home devices

### Takeaway
Commercial multi-user scales identify users by matching the current weight to each user's recent weight history, then use impedance or body-fat to break ties. When confidence is low they ask the user or skip logging. ECG biometrics is feasible, but real-world single-lead equal error rates (EER, the operating point where false accepts equal false rejects) are about 9–22%. It should therefore be a secondary check, not a primary one.

### Cited Findings
- Fitbit Aria recognised up to 8 users from weight and fat readings, according to its FDA summary. — [FDA K133872 via Innolitics](https://fda.innolitics.com/device/K133872)
- Aria prompted people with similar weights to identify themselves by initials. — [search summary of manufacturer descriptions](https://revmedconnect.com/device/fitbit-inc/fb201b/00898628002045)
- An EPO patent describes staged filtering: first a candidate set from the measured weight against each user's weight history, then impedance, body-fat history and user attributes to refine the match. — [EPO EP4137045](https://data.epo.org/publication-server/rest/v1.2/patents/EP4137045NWA1/document.html)
- A user-identifying toilet patent (foot scale plus bioimpedance) skips logging when classification confidence is low. — [USPTO 9595185](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9595185)
- ECG biometrics:
  - A one-week field study (20 people, chest belt) reported EER of 9.15–21.91%. The best result came from fusing up to 15 heartbeats per decision. — [arXiv 2003.03273](https://ar5iv.labs.arxiv.org/html/2003.03273)
  - Lab benchmarks on the PTB database: 0.14% single-session and 2.06% multi-session EER. — [arXiv 2204.03992](https://www.arxiv.org/abs/2204.03992)
  - Accuracy drops across days. — [Buffalo survey PDF](https://cse.buffalo.edu/~wenyaoxu/courses/fall2017/Paper/ECG_Biometrics2.pdf)
  - A palm-electrode study reported 94.3% identification and 10.1% EER. — [SciTePress 2013](https://scitepress.org/Papers/2013/42432/pdf/index.html)

### Inferences
- Recommended identity gate:
  - Accept a reading as the patient's only if the weight is within ±(3 × the patient's 14-day MAD + 1.5 kg) of their recent median, with a wider band in the days after a diuretic change.
  - If impedance is available, it should also lie within the patient's band.
  - Otherwise mark the reading "unattributed". Never feed it to the baseline; prompt for confirmation in the app.
- A trend that is a true decompensation (+2 kg over a week) stays inside a band defined this way, while another adult's weight usually does not. Very similar weights between household members remain a failure mode.

### Gaps
- No peer-reviewed accuracy figures for weight-history user matching on consumer scales were found.

## Evaluation methodology

### Takeaway
Use event-based metrics, as MultiSENSE and Gyllensten did:
- sensitivity per event within a fixed pre-event window (14–30 days)
- unexplained or false alerts per patient-year
- median lead time
- time in alert
- PPV

Always split by patient. Gyllensten used stratified 8-fold leave-patient-out cross-validation, and MultiSENSE used separate development and test cohorts.

### Cited Findings
- MultiSENSE endpoints were sensitivity above 40% and unexplained alert rate below 2 per patient-year, assessed in an independent test cohort after development. — [PSU Pure](https://pure.psu.edu/en/publications/a-multisensor-algorithm-predicts-heartfailure-events-in-patients-/)
- MultiSENSE true-positive rule: the alert started before the event and did not reset more than 30 days before it. Events in the first 45 days were excluded. Time in alert and PPV were also reported. — [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)
- Gyllensten scheme:
  - The data are split into 2-week periods, each ending at a hospitalisation where one occurs.
  - Any alarm within 2 weeks before a hospitalisation is a true positive; an alarm in another period is a false positive; a period without an alarm is a true negative.
  - Cross-validation was stratified, leave-patient-out, with 8 folds and events balanced across folds.
  - The authors warn that this period framing makes PPV look worse than the false-alarms-per-patient-year metric does.

  — [PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)
- TRACER (Aerts et al., arXiv, Sept 2026):
  - A transformer with contrastive pre-training, applied to low-resolution, irregular telemonitoring data from 276 Swedish HF patients.
  - Windows are labelled by whether an HF hospitalisation occurs at the window's later edge.
  - It correctly predicted 66.7% of timelines leading to hospitalisation, with 7.9% "overestimation".
  - Framing training as event detection beat training directly on forecasting windows.

  — [arXiv 2609.29742](https://arxiv.org/abs/2609.29742)

### Inferences
- Report all of these together, so that no single metric can be gamed:
  - sensitivity per event (alert 1–30 days before admission)
  - false alerts per patient-year, and per patient-month for the demo
  - specificity on non-event days or windows
  - median and IQR of lead time
  - time in alert
  - PPV
- Exclude the first 30 days, the warm-up period, from evaluation. Never let the same synthetic patient appear in both training and test sets.

### Gaps
- No standard definition of "lead time" exists across studies. MultiSENSE uses the first alert date relative to the event.

## Synthetic HF data: trajectories and realistic magnitudes; NeuroKit2

### Takeaway
No public generator of synthetic HF decompensation trajectories was found. The team should build a parametric simulator calibrated to these published figures:
- weight begins rising about 30 days before admission and diverges clearly in the final week
- respiratory rate rises about 1.5–2.1 breaths per minute (about 2% for mean daily RR in the final 7 days)
- RSBI rises about 6%
- night HR rises, and activity falls

Waveform-level signals can come from NeuroKit2: `ecg_simulate`, `ppg_simulate` and `rsp_simulate`.

### Cited Findings
- Weight (Chaudhry et al., Circulation 2007;116:1549–1554):
  - A nested case-control study within a home-monitoring programme of more than 10,000 patients; 393 had an HF admission.
  - Weight began rising gradually about 30 days before admission, and the case and control trajectories diverged significantly in the final week.
  - Odds ratios for admission: 2.34 for a 2–5 lb gain, 3.69 for 5–10 lb, and 4.98 for more than 10 lb.

  — [PMC2892745](https://pmc.ncbi.nlm.nih.gov/articles/PMC2892745); [Relias Media](https://www.reliasmedia.com/articles/8984-weight-gain-predictor-of-heart-failure-hospitalization)
- Contrary evidence on weight: in Gyllensten 2016, weight was not significantly different in the 2 weeks before events. The weight CUSUM statistic was 1.9 ± 2.7 versus 0.8 ± 1.3 (p = 0.58). Impedance was significant (log ohm 3.0 ± 0.3 versus 3.4 ± 0.3, p < .001). — [PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)
- Respiration:
  - NOTICE-HF: daily RR rose about 1.5–2.1 breaths per minute before HF events. A 30-day SD of median RR above 1.0 breath per minute gave HR 12.3. — [Springer (search summary)](https://www.link.springer.com/article/10.1007/s10840-015-9983-6)
  - MultiSENSE: mean daily RR was about 2.2% higher and RSBI about 6% higher in the 7 days before events; tidal volume did not change significantly. — [Healio 2014](https://cm.healio.com/news/cardiology/20141002/hf-events-preceded-by-worsening-rapid-shallow-breathing)
- Night HR and activity:
  - Night HR rose in 15 of the HeartLogic alerts in the PMC6437441 cohort.
  - Night HR rose 3–4 times more in COVID-19 than in HF events, so the HR rise in HF is modest.
  - No standalone published magnitude of activity decline in HF was found.

  — [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441); [Gardner 2021](https://www.bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heart-failure-diagnostic/heartlogic-newsletter/issue-7-2021/Gardner_ESC-HF_2021.pdf)
- Alert-episode shape (useful for simulation), from PMC6437441:
  - Median HeartLogic alert duration: 70 days for hospitalisations, 36 days for minor events.
  - Peak index: 40 versus 24.
  - Warning time: 38 days versus 12 days.

  — [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)
- NeuroKit2 `ecg_simulate(duration=10, length=None, sampling_rate=1000, noise=0.01, heart_rate=70, heart_rate_std=1, method='ecgsyn', random_state=None, random_state_distort='spawn', **kwargs)`:
  - Methods: `'simple'`, `'ecgsyn'` (McSharry 2003 dynamical model) and `'multileads'` (12 leads).
  - Supports ECGSYN kwargs such as `lfhfratio`.

  — [NeuroKit2 ECG docs](https://neuropsychology.github.io/NeuroKit/functions/ecg.html)
- NeuroKit2 `ppg_simulate(duration=120, sampling_rate=1000, heart_rate=70, frequency_modulation=0.2, ibi_randomness=0.1, drift=0, motion_amplitude=0.1, powerline_amplitude=0.01, burst_number=0, burst_amplitude=1, random_state=None, ...)`:
  - The docs' parameter descriptions conflict with the signature on some defaults, so check with `inspect.signature`.
  - `powerline_amplitude` needs `sampling_rate` of at least 500.

  — [NeuroKit2 PPG docs](https://neuropsychology.github.io/NeuroKit/functions/ppg.html)
- `rsp_simulate(duration=..., respiratory_rate=15, sampling_rate=...)` exists in NeuroKit2. Usage example: `nk.rsp_simulate(duration=10, respiratory_rate=15)`. — [NeuroKit2 docs (intro)](https://rpanderson-neurokit2.readthedocs.io/en/latest/introduction.html)

### Inferences
Proposed simulator, calibrated to the cited magnitudes. Parameters not directly cited are marked as assumptions.
- Stable baseline for each patient:
  - weight 60–110 kg, day-to-day SD about 0.3–0.5 kg (assumption)
  - night HR 60–80 bpm, SD about 2 bpm (assumption)
  - RR 14–18 breaths per minute, SD about 0.5–1.0 (NOTICE-HF: an SD above 1.0 signals risk)
  - activity 3–6 h per day (assumption)
  - weekly seasonality, and 5–15% random missing days
- Decompensation episode, a ramp from day −30 to day 0 that accelerates over the final 7 days (Chaudhry):
  - weight +1–4.5 kg (2–10 lb, matching the OR bands)
  - RR +1.5–2.1 breaths per minute
  - night HR +3–8 bpm (assumption; direction cited, magnitude not)
  - activity −15–30% (assumption)
  - impedance −5–15% (assumption; direction cited)

  Make about 30–40% of episodes "weight-silent" to reflect Gyllensten and FAST, where weight was insensitive.
- Confounder episodes:

  | Episode | Shape |
  |---|---|
  | Infection | Abrupt; HR +10–20 bpm, RR +3–5, activity ↓↓, weight flat; 3–7 days |
  | AF | HR step +15–30 bpm with irregular RR intervals |
  | Salty meal | Weight +0.5–1.5 kg, resolving in 2 days |
  | Diuretic change | Weight −1–2 kg step |
  | Scale misuse / guest user | Single-day spikes |

  All magnitudes in this table are assumptions to tune.
- Event rate: about 0.2–0.5 HF hospitalisations per patient-year (PMC6437441 cohort: 0.21 per patient-year). Generate at least 100 patients × 1 year so that false alerts per patient-year can be estimated.
- Derive daily HR and RR from NeuroKit2 waveforms only when demonstrating the signal-processing and SQI pipeline. For the alert engine itself, simulate the daily aggregates directly, which is cheaper and fully controlled.

### Gaps
- No published open-source generator of HF decompensation trajectories was found.
- Absolute magnitudes of the night-HR rise and activity decline before HF admission were not found in the retrieved sources.
- The full text of TRACER (arXiv 2609.29742) could not be parsed, so its features and baselines are unknown.
