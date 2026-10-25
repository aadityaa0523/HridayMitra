# Night-time and daily-life signals that predict worsening heart failure (evidence for a low-cost companion device)

Research notes, 2026-10-24. Access limits: PMC/PubMed pages returned a CAPTCHA, and Healio and DOAJ returned 403/VPN blocks. Many numbers below therefore come from abstracts, institutional repository pages, sponsor material or news summaries rather than full texts. Each item says which. **Sponsor flag:** MultiSENSE and HeartLogic are Boston Scientific (BSci). LINK-HF was run with PhysIQ/VitalConnect, so its press-release numbers are sponsor-reported. EarlySense data are company-associated. Oura and Fitbit COVID claims are company-reported.

## Evidence-ranked summary (for the report writer)

| Rank | Signal | Best evidence (size, year) | Magnitude / lead time | Cost-feasible at home? |
|---|---|---|---|---|
| 1 | Night (resting) heart rate trend + flattened day/night HR rhythm | WEARIT-France, n=1,013, Europace 2023 (peer-reviewed, ZOLL WCD data); van Es et al., n=65, ESC HF 2025; HeartLogic NHR component (BSci) | >5 bpm week-on-week rise in night HR: adjusted HR 2.51 for CV death/HFH. Mesor ~70.6 to 73.6 bpm and amplitude 8.3 to 4.9 bpm across the ~21 days before events | Yes: wrist PPG or bed sensor |
| 2 | Night respiratory rate (and RSBI) | MultiSENSE n=900, JACC HF 2017 (BSci); Gardner ESC HF 2021 (BSci); EarlySense home study n≈30, J Telemed Telecare | RR and RSBI significantly higher pre-event. Daily mean RR only about +2.2% before HF events in a BSci CRT-D study. Vendor guide: 30-day mean RR >20/min means higher 30-day risk | Yes: bed/under-mattress sensor, chest accelerometer, or PPG-derived RR |
| 3 | Daily activity decline | Kelly et al., JACC HF 2020, Medicare-linked ALTITUDE data (BSci data); ICD accelerometer systematic review | About 85 to 75 active min/day over 8 weeks: HR 4.02 for HFH/death | Yes: wrist accelerometer |
| 4 | Multi-sensor fusion (HeartLogic-like) | MultiSENSE (BSci) | Sensitivity 70% at 1.47 unexplained alerts/patient-year (test cohort). Median lead time 34 days (IQR 19 to 66) | The architecture can be copied. S3 heart sounds and impedance are the main drivers and need implants or chest contact |
| 5 | Sleep-disordered breathing / Cheyne-Stokes | Oldenburg 2007, n=700 (prevalence); DASAP-HF (ApneaScan RDI vs PSG; outcomes) | 76% have SDB (40% CSA). Severe device-detected SA (RDI ≥30/h) predicts death and CV hospitalisation. **No data found on CSR worsening in the days before decompensation** | Partly: bed sensor or SpO2 pattern detection is feasible. Short-term predictive value is unproven |
| 6 | Orthopnea/PND, objectively measured trunk angle | Cardiovascular Health Study (symptom accuracy) | Orthopnea/PND sensitivity 52%, specificity 83% for HF diagnosis. **No validated sensor-based trunk-angle study in HF found** | Cheap (one accelerometer) but unvalidated, so research-grade only |
| 7 | Nocturnal cough | Trials registered or ongoing only (NCT06555757; AHF-Voice preprint) | No effect sizes published | Cheap (microphone). Unvalidated, with privacy cost |
| 8 | HRV alone | Reviews only | No effect sizes found for short-term prediction | Easy to capture but confounded by AF and ectopy |

---

## Key Question 1: Night respiratory rate and rapid-shallow-breathing index before HF events (HeartLogic/MultiSENSE, NOTICE-HF, EarlySense): magnitude and lead time

### Takeaway
Night or daily respiratory rate (RR) and RSBI (RR divided by tidal volume) rise before HF events and fall during recovery. The rise is small in absolute terms (a few percent, or about 1 to 2 breaths/min), and in HeartLogic these respiratory sensors contribute less often to alerts than heart sounds (S3) and impedance. Lead time belongs to the fused index (median 34 days), not to RR alone. The only home non-contact data (EarlySense, n≈30) found average nightly RR to be the strongest readmission predictor.

### Cited Findings
- MultiSENSE (Boehmer et al., JACC HF 2017;5(3):216-225; BSci-sponsored): 900 patients (development n=500, test n=400; one summary says 443 sequestered, a discrepancy that remains unresolved). Pre-specified endpoints were sensitivity >40% and unexplained alert rate <2/patient-year. Results: test-cohort sensitivity 70% and unexplained alert rate 1.47/pt-yr; development cohort 82% and 1.33/pt-yr — [Penn State Pure record](https://pure.psu.edu/en/publications/a-multisensor-algorithm-predicts-heartfailure-events-in-patients-/); [HMP EP Lab Digest summary](https://www.hmpgloballearningnetwork.com/site/eplab/multisensor-device-based-monitoring-patients-systolic-heart-failure)
- Median lead time before HF event: 34.0 days (IQR 19.0 to 66.3) — [Boston Scientific MultiSENSE page (sponsor)](https://bostonscientific.com/en-US/medical-specialties/electrophysiology/heartlogic-heart-failure-diagnostic/clinical-data/multisense.html)
- HeartLogic index = weighted combination of heart sounds (S3, S1), respiration (rate, tidal volume via RSBI), thoracic impedance and night HR (midnight to 6 a.m.). Nominal alert threshold 16, recovery threshold 6. The index needs 30 to 37 days of data before it is available. Event rate was 0.80 vs 0.08 events/pt-yr in vs out of alert — [BSci HeartLogic Alert Management Guide (sponsor)](https://bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heartfailure-diagnostic-ep/HeartLogic.Alert%20Management_Guide_FINAL.pdf); [EP Lab Digest](https://www.hmpgloballearningnetwork.com/site/eplab/multisensor-approach-heart-failure-monitoring)
- BSci guidance: worsening HF may be associated with a worse rapid-shallow-breathing pattern, raised RR, an increase in RR, or higher day-to-day RR variability — [BSci multi-sensor technology page](https://bostonscientific.com/en-US/medical-specialties/electrophysiology/heartlogic-heart-failure-diagnostic/multi-sensor-technology.html)
- Sensors worsening on the day the alert threshold was crossed: S3 84%, S3/S1 88%, night HR 60%, thoracic impedance 44%, RR 36%, RSBI 36%. Heart sounds and impedance were the main contributors — [EP Lab Digest, multisensor approach](https://www.hmpgloballearningnetwork.com/site/eplab/multisensor-approach-heart-failure-monitoring)
- Gardner et al., ESC Heart Failure 2021 (MultiSENSE secondary analysis, BSci): 1,667 stable periods in 676 patients vs 192 HF events in 106 patients. Before events, RR, RSBI, HR and S3 were significantly higher, and S1, impedance and activity were significantly lower. All except S1 improved during recovery. Numeric values appear only in a figure — [BSci HeartLogic newsletter 2021/3 (sponsor)](https://www.bostonscientific.com/en-EU/medical-specialties/heart-failure/heartlogic-heart-failure-diagnostic-hfc/newsletter/2021/3.html)
- A sensor table (OUP-hosted, likely from Gardner 2021 or a related HeartLogic paper) shows RR, daytime RSBI and night HR above baseline in the 7 days before events, with the HeartLogic index rising from about 12 to about 23. This was seen via search snippet only; the full table was not verified — [OUP view-large table](https://academic.oup.com/view-large/544450657)
- In a 568-patient real-world HeartLogic ICD cohort, most alerts were driven by heart sounds, but alerts linked to hospitalisation or death were more often driven by RR, RSBI or night HR (search-snippet level) — [Uniba repository](https://ricerca.uniba.it/handle/11586/519110)
- BSci-sponsored CRT-D study (Healio 2014, "HF events preceded by worsening rapid shallow breathing"): daily mean RR was significantly higher before HF events, by only 2.2% (P=.03). Full article blocked; figure from search snippet — [Healio 2014](https://cm.healio.com/news/cardiology/20141002/hf-events-preceded-by-worsening-rapid-shallow-breathing)
- BSci alert guide cites research linking a 30-day average RR >20 breaths/min to higher risk of HF events in the next 30 days (snippet; PDF could not be parsed) — [BSci HeartLogic Alert Guide CRM-499506](https://www.bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heartfailure-diagnostic-ep/CRM-499506-AC-HeartLogic-Alert-Guide.pdf); related: [Boehmer HRS 2013 presentation, "Variation in daily median respiratory rate identifies patients at higher risk of worsening HF in 30 days" (BSci)](https://www.bostonscientific.com/content/dam/bostonscientific/Rhythm%20Management/general/Presentation%20Resources/CRM-159703-HRS2013-Dr-Boehmer-pres.pdf)
- MULTITUDE-HF (Forleo et al., J Interv Card Electrophysiol 2015) analysed ICD-measured RR against clinical status and HF events. Results (HR, cutoffs) were not retrieved — [SpringerMedicine](https://www.springermedicine.com/long-term-monitoring-of-respiratory-rate-in-patients-with-heart-/21640190)
- Device patents describe a rise in night RR, and a damped day/night RR difference, as indicators of worsening HF, arguing that night RR is less affected by conscious and environmental influences. These are claims, not trial evidence — [US8394029B2](https://patents.google.com/patent/US8394029)
- EarlySense home study (J Telemed Telecare; about 30 patients discharged after HF admission; 29 patients over 640 nights in another report): readmitted patients had higher HR, higher RR and more respiratory variability, and average nightly RR was the most predictive of readmission. The sensor was well tolerated (1 dropout) — [Respiratory Therapy summary](https://respiratory-therapy.com/department-management/clinical/earlysense-home-monitoring-predicts-hospital-readmissions-hf/); [FierceBiotech (Cleveland Clinic)](https://www.fiercebiotech.com/medical-devices/cleveland-clinic-under-mattress-home-vitals-monitor-predicts-hospital-readmission)
- LINK-HF (Stehlik et al., Circ HF 2020;13:e006513): n=100, age 68±10, 98% male (VA), disposable chest multisensor patch for up to 3 months, ML personal-baseline model. Median 6.5 days between alert and readmission — [TCTMD](https://www.tctmd.com/news/stick-sensor-predicts-heart-failure-hospitalizations-pilot-study); [MD Anderson Pure record](https://mdanderson.elsevierpure.com/en/publications/continuous-wearable-monitoring-analytics-predict-heart-failure-ho). A sponsor press release reports up to 88% sensitivity, 86% specificity and a mean lead time of up to 10.4 days in a post hoc analysis — [BusinessWire (sponsor)](https://www.businesswire.com/news/home/20200225005593/en)

### Inferences
- For a companion device, night RR is worth capturing (rank 2), but an absolute change of about 2% means that one night's RR is noise. Use a 7-day rolling median compared with a 30-day personal baseline, and add day-to-day RR variability as a second feature.
- RSBI needs tidal volume. Without impedance or chest-wall excursion, a bed or chest accelerometer gives only relative amplitude. A "relative RSBI" (RR divided by normalised breath amplitude) is a plausible proxy but unvalidated.
- The 34-day HeartLogic lead time comes from S3 and impedance. With wrist PPG plus bed RR, a lead time closer to LINK-HF's (about 1 to 2 weeks) is realistic.

### Gaps
- NOTICE-HF (HeartLogic in the US, BSci) results were not retrieved. No sensor-level numbers from it were found.
- No source gave per-sensor absolute pre-event deltas in breaths/min or RSBI units from MultiSENSE. They exist only in figures I could not access.
- Recollection, not verified this session: LINK-HF abstract reports 76% to 88% sensitivity at 85% specificity. Verify before citing.

## Key Question 2: Periodic breathing / Cheyne-Stokes / central sleep apnea in HF: prevalence, change before decompensation, home detection

### Takeaway
Sleep-disordered breathing is very common in HFrEF (76%, with 40% central), and a device-detected severe level is a long-term risk marker. I found no peer-reviewed evidence that CSR or CSA burden rises in the days before a decompensation, so it serves as a risk stratifier and a plausible early-warning signal, not a proven one. Home detection with wireless or bed sensors and ICD algorithms is feasible.

### Cited Findings
- Oldenburg et al. 2007 (Eur J Heart Fail): 700 patients with HFrEF (NYHA ≥II, LVEF ≤40%) screened by polygraphy. SDB (AHI ≥5/h) in 76%: 40% CSA, 36% OSA — [PubMed 17027333](https://pubmed.ncbi.nlm.nih.gov/17027333/)
- A later German registry (>1,000 patients, ESC 2015) found that, among patients with SDB, 64% had OSA, 22% CSA and 14% mixed or unclassified. The two figure sets should not be mixed — [MDedge / The Hospitalist](https://mdedge.com/content/esc-obstructive-sleep-apnea-often-complicates-heart-failure)
- DASAP-HF: the ICD ApneaScan respiratory disturbance index (RDI) was validated against polysomnography for severe SA. Patients were stratified at 1 month by RDI ≥30/h, and higher RDI was associated with death and CV hospitalisation over 24 months. The analysis was baseline-stratified, not a pre-event trend — [IRIS Sant'Anna](https://www.iris.sssup.it/handle/11382/537296); [ARTS Trieste](https://arts.units.it/handle/11368/2992317)
- A week-averaged ICD RDI identified severe SDB on later polygraphy with 87% sensitivity and 56% specificity — [BSci HeartLogic newsletter 2021/6 (sponsor)](https://bostonscientific.com/en-EU/medical-specialties/heart-failure/heartlogic-heart-failure-diagnostic-hfc/newsletter/2021/6.html)
- Periodic breathing is described as a risk factor for worsening HF and reduced survival, and CSR as an independent predictor of mortality. A wireless cardiorespiratory system compared well with respiratory inductance plethysmography for CSR detection — [Imperial thesis](https://spiral.imperial.ac.uk/handle/10044/1/24577); [Oxford RDM publication](https://rdm.ox.ac.uk/publications/244885)

### Inferences
- In an HF population, a bed or chest sensor will see periodic breathing on many nights, so a baseline periodic-breathing burden per person is needed. Treat a rise in the share of the night with periodic breathing (cycle length about 40 to 90 s typical of CSR in HF) as a supporting feature, not a primary alarm.
- Because CSR worsens with higher filling pressure and lower cardiac output (physiology, not shown here as pre-event data), it is reasonable to include as an exploratory feature in synthetic data. Label it as hypothesis.

### Gaps
- No study found showing a change in CSR/CSA index before HF hospitalisation. A HeartLogic plus RDI combination study (Italian group, ESC HF Oct 2024) appeared in search, but the page was 403-blocked and its results are unverified.
- CSR cycle-length figures above are from general clinical knowledge, not a source retrieved this session.

## Key Question 3: Orthopnea and paroxysmal nocturnal dyspnea: predictive value; sensor-based measures of nocturnal sitting up or trunk angle

### Takeaway
Orthopnea and PND are specific-leaning but insensitive symptoms. Clinically, orthopnea is one of the best bedside congestion signs, but I found no peer-reviewed study that objectively measures trunk angle or nocturnal sitting-up with a sensor and validates it against HF congestion or events. A chest or pillow accelerometer is cheap, so this is a novel, unvalidated feature.

### Cited Findings
- Cardiovascular Health Study (adults ≥65): orthopnea or PND had 52% sensitivity, 83% specificity, 13% PPV and 97% NPV for definite HF. Fewer than 20% of those reporting either had HF — [U Kentucky Scholars](https://scholars.uky.edu/es/publications/value-of-orthopnea-paroxysmal-nocturnal-dyspnea-and-medications-i/)
- A 2026 HFA abstract proposes a "jugular-orthopnea index" to detect raised LV filling pressure in ambulatory HF. No accuracy numbers were retrieved — [CiteDrive (EJHF abstract)](https://www.citedrive.com/en/discovery/clinical-value-and-a-new-jugular-orthopnea-index-to-detect-increased-lv-filling-pressures-in-heart-failure/)
- Trunk angle can be computed from a 3-axis accelerometer, but only patent descriptions were found — [US7766841 sleep diagnosis device](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7766841); [ZOLL WCD motion/position patent family](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8676313)
- Accelerometer sleep-posture classification is accurate in non-HF populations: about 91% for 4 postures (wrist/body), and 99% for supine/prone/lateral with a neck-worn sensor — [BEEI 2026](https://www.beei.org/index.php/EEI/article/view/10105); [Imperial, neck accelerometer](https://spiral.imperial.ac.uk/entities/publication/b334ce8c-6cb2-4d67-a927-0c3f4643e3fc)
- Dual chest-mounted tri-axial accelerometers can extract respiration, heartbeat and posture from one sensor set (no HF cohort) — [IEEE 7808735](https://ieeexplore.ieee.org/document/7808735/authors)

### Inferences
- A chest-clip or pillow-tilt accelerometer could log "minutes asleep with trunk >30 to 45 degrees upright" and "number of sit-up episodes from 00:00 to 06:00" (an objective PND proxy). The cost is negligible, but treat it as an exploratory feature with a personal baseline. A wrist sensor alone cannot measure trunk angle.
- An evening check-in question asking about pillows or sleeping upright is a validated-concept, zero-cost alternative.

### Gaps
- No peer-reviewed sensor-validated orthopnea/PND study in HF found. Whether implant accelerometers (e.g., HeartLogic) record posture-at-night as a feature was not confirmed.
- No sensitivity/specificity of orthopnea against invasive filling pressure retrieved.

## Key Question 4: Night heart rate and HRV before decompensation; activity decline before admission; nocturnal cough

### Takeaway
Night HR trend is the best-supported cheap signal. A >5 bpm week-on-week rise roughly doubles to triples short-term risk, and a flattened circadian HR amplitude appears about 3 weeks before events. Activity decline of about 10 min/day over 8 weeks is associated with 4-fold risk. HRV and nocturnal cough lack published pre-event effect sizes.

### Cited Findings
- WEARIT-France (Garcia et al., EP Europace 2023;25(5); DOI 10.1093/europace/euad062; NCT03319160): 1,013 HF patients wearing a wearable cardioverter-defibrillator (median 68 days), median age 61, 16% women, median LVEF 26%. Night defined as 00:00 to 07:00. 58 patients (6%) had 69 events. Results:
  - Week-1 high night HR with a week-2 rise vs low and falling: adjusted HR 6.08 (2.56 to 14.45) for CV death/HFH.
  - A >5 bpm weekly rise in mean night HR: adjusted HR 2.51 (1.22 to 5.18) for the composite, 2.70 (1.51 to 4.82) for CV hospitalisation and 11.21 (3.55 to 35.37) for total mortality.
  - Source: [Region H research portal](https://research.regionh.dk/da/publications/dynamic-changes-in-nocturnal-heart-rate-predict-short-term-cardio/)
- van Es et al., ESC Heart Failure 2025;12(6):4095-4107: 65 post-ADHF patients wearing a wrist HR device for 6 months. Over the 21 days before an HF event, mesor rose (70.6 vs 73.6 bpm, P<0.001) and amplitude fell (8.3 vs 4.9 bpm, P=0.046). Amplitude carried 62% of feature importance, and the model reached AUC 0.74 (sensitivity 74%, specificity 73%). Acrophase did not change. Event count and sponsor were not on the page — [TU/e research portal](https://research.tue.nl/en/publications/predicting-acute-decompensated-heart-failure-using-circadian-mark/); [IRIS IMT Lucca PDF](https://iris.imtlucca.it/bitstream/20.500.11771/35878/1/ESC%20Heart%20Failure%20-%202025%20-%20Es%20-%20Predicting%20acute%20decompensated%20heart%20failure%20using%20circadian%20markers%20from%20heart%20rate%20time.pdf)
- HeartLogic night HR is averaged over 00:00 to 06:00 and approximates resting HR. An increase may reflect worsening HF or autonomic dysfunction — [BSci Alert Management Guide](https://bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heartfailure-diagnostic-ep/HeartLogic.Alert%20Management_Guide_FINAL.pdf)
- Kelly et al., JACC HF 2020 (BSci ALTITUDE device data linked to Medicare): a decline in daily activity from about 85 to about 75 min over 8 weeks was associated with HR 4.02 (3.82 to 4.22) for HFH or death. The authors say activity trends may flag imminent HFH or death several weeks ahead. Figures are from a news summary — [Healio 2020](https://www.healio.com/news/cardiology/20200214/monitoring-physical-activity-via-implantable-device-may-predict-hf-hospitalization-death)
- Systematic review of accelerometer activity in ICD recipients: both low post-implant activity and decline in activity were associated with mortality, HFH and appropriate shocks. Activity was also affected by AF onset, shocks, season and social factors — [PMC8890329](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8890329/)
- Low baseline device-measured activity was associated with atrial arrhythmias and with death/HFH in ICD patients with HF (JAHA 2018) — [Unimore JAHA PDF](https://iris.unimore.it/bitstream/11380/1168115/2/JAHA.117.008146.pdf)
- Gardner 2021 (BSci): device activity was significantly lower before HF events and recovered afterwards — [BSci newsletter 2021/3](https://www.bostonscientific.com/en-EU/medical-specialties/heart-failure/heartlogic-heart-failure-diagnostic-hfc/newsletter/2021/3.html)
- Smartwatch study (Toronto, n=217): a drop of ≥10% in a smartwatch-derived cardiopulmonary fitness estimate (from HR, activity and SpO2) was linked to more than 3 times the risk of unplanned hospitalisation or urgent treatment. This is a news report; the primary paper was not retrieved — [HospiMedica](https://www.hospimedica.com/latest-news/articles/294809517/wearable-ai-tool-predicts-hospitalization-risk-in-heart-failure.html)
- HRV: a registered wearable HR/RR remote-monitoring trial lists HRV as an autonomic marker, but no results were found — [NCT04455828](https://clinicaltrials.gov/study/NCT04455828)
- Nocturnal cough: a clinician interview argues that lying-down cough is a possible early decompensation sign (expert opinion, Hyfe, a cough-AI company) — [Hyfe Q&A with Dr Nadia Giannetti](https://hyfe.ai/insights/q-a-with-dr-nadia-giannetti). The AHF-Voice study (131 post-discharge patients, daily smartphone voice for 6 months) collects nocturnal cough frequency as a secondary endpoint, using a detector trained on asthma patients — [medRxiv 2023.03.06.23286682](https://medrxiv.org/content/10.1101/2023.03.06.23286682.full.pdf). An AI-sound decompensation trial is registered — [NCT06555757](https://clinicaltrials.gov/study/NCT06555757)

### Inferences
- Night HR is the best value signal for a wrist band: easy, robust, and backed by an n=1,013 peer-reviewed cohort plus a wrist-device circadian study. Use the mean or lowest 30-minute HR from 00:00 to 06:00, and track both the 7-day mean against a 4-week baseline (flag ≥5 bpm) and the 24-h HR amplitude (flag a substantial drop, such as from about 8 to about 5 bpm).
- Activity is a slow signal (weeks). Use weekly totals of active minutes or steps against personal baseline. A 10 to 15% sustained fall is a reasonable contributor threshold, scaled from 85 to 75 min.
- Leave HRV out of the alerting core. It is unreliable with AF and ectopy, which are common in HF, and lacks effect sizes. Log it only.

### Gaps
- No peer-reviewed effect size for nocturnal HRV or for nocturnal cough frequency before HF events.
- Kelly 2020 numbers are from a news summary; the full paper was not checked.
- No step-count-specific thresholds found (studies use device "active minutes").

## Key Question 5: Confounders (infection/fever, AF, poor sleep, heat, medication changes) and how to tell them apart

### Takeaway
Infection, AF onset and poor sleep move the same signals as HF (HR up, RR up, activity down). Temperature (skin or wrist trend) is the most useful differentiator for infection: wearable temperature flagged fever in 93% of cases about 3 days before symptoms. But only about half of infections produce fever, and infection itself is a common HF trigger, so it should prompt a check, not be discarded. AF onset is the other big confounder: detect it from PPG irregularity and treat it as a co-alert.

### Cited Findings
- Oura/TemPredict proof-of-concept (Scientific Reports, n=50): ring temperature detected fever onset in 93% of cases, about 3 days before symptoms. HR, HRV and RR also shifted but not always in step. Fever was present in only about 52 to 59% of infected participants. Oura's 76% claim (changes before COVID symptoms) is company-reported — [MobiHealthNews](https://mobihealthnews.com/news/oura-ring-detects-onset-fever-common-covid-19-symptom); [Oura blog (company)](https://ouraring.com/blog/he/tempredict_covid19_research/)
- Fitbit reported breathing- and heart-rate changes around COVID infection, but the results were not peer-reviewed in the sources found — [TBS News](https://www.tbsnews.net/node/110890)
- Device activity is affected by AF onset, ICD shocks, season and social factors — [PMC8890329](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8890329/)
- HeartLogic: a night HR rise may reflect worsening HF or autonomic dysfunction (i.e., non-specific) — [BSci Alert Management Guide](https://bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heartfailure-diagnostic-ep/HeartLogic.Alert%20Management_Guide_FINAL.pdf)
- Patent claims (not peer-reviewed): combined CSR plus arrhythmia detection predicted survival better than CSR alone — [US7803119](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7803119)

### Inferences
- Rule set for a low-cost device:
  - Night skin-temperature rise of about 0.5 °C or more above personal baseline, with an HR and RR rise, means "possible infection". Escalate anyway, because infection precipitates HF.
  - Irregular PPG RR intervals (AF screen) with an HR jump means "possible AF". Report separately; it is also an HF trigger.
  - HR and RR up with no temperature rise, plus activity down, plus a weight or impedance trend means "congestion pattern". This is the highest-priority alert.
- Heat: in India, room temperature affects night HR, RR and skin temperature. Logging dock ambient temperature and humidity (cheap sensor) allows adjustment.
- Medication changes (beta-blocker titration lowers night HR; diuretic changes move weight): add a one-tap "meds changed" log that resets or pauses the baseline for 7 to 14 days.
- Poor sleep: use sleep duration and wake bouts from the accelerometer to down-weight nights with less than 4 h of sleep.

### Gaps
- No HF-specific study found that uses skin or core temperature to separate infection-driven from congestion-driven alerts.
- No evidence retrieved on heat or ambient temperature effects on HF device sensors. The 0.5 °C threshold is an inference, not sourced.
- Medication-change effects on HeartLogic sensors were not retrieved.

## Key Question 6: How implant multi-sensor indices combine signals, and lessons for a low-cost personal-baseline algorithm

### Takeaway
HeartLogic computes each sensor's deviation from the patient's own rolling baseline, combines them into a weighted composite index, alerts when the index crosses a threshold (16), and holds the alert until it falls below a lower recovery threshold (6). It needs about a month of baseline. LINK-HF used a similar personal-baseline ML model on a chest patch, with a median 6.5-day lead. Lesson: personal baseline plus multi-signal agreement plus hysteresis matter more than any single threshold.

### Cited Findings
- HeartLogic structure, thresholds (16 alert / 6 recovery) and 30 to 37 day warm-up — [BSci Alert Management Guide](https://bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heartfailure-diagnostic-ep/HeartLogic.Alert%20Management_Guide_FINAL.pdf)
- Performance: 70% sensitivity, 1.47 unexplained alerts/pt-yr, median 34-day lead — [Penn State Pure](https://pure.psu.edu/en/publications/a-multisensor-algorithm-predicts-heartfailure-events-in-patients-/); [BSci MultiSENSE page](https://bostonscientific.com/en-US/medical-specialties/electrophysiology/heartlogic-heart-failure-diagnostic/clinical-data/multisense.html)
- Heart sounds and impedance dominate alert crossings. RR, RSBI and night HR worsen in 36 to 60% of crossings — [EP Lab Digest](https://www.hmpgloballearningnetwork.com/site/eplab/multisensor-approach-heart-failure-monitoring)
- LINK-HF: chest patch with ML personal baseline, median 6.5 days alert-to-readmission — [TCTMD](https://www.tctmd.com/news/stick-sensor-predicts-heart-failure-hospitalizations-pilot-study)
- The PARTNERS-HF-style combined device diagnostic score put high-risk months at adjusted HR 10.0 (6.4 to 15.7) for HFH in the next 30 days. This is a different study (Medtronic-era), found via search — [WUSTL journal club](https://journalclub.wustl.edu/2010/04/24/combined-heart-failure-device-diagnostics-identify-patients-at-higher-risk-of-subsequent-heart-failure-hospitalizations-results-from-partners-hf-program-to-access-and-review-trending-information-and/)
- Circadian HR amplitude alone gave AUC 0.74 in a wrist-device study — [TU/e](https://research.tue.nl/en/publications/predicting-acute-decompensated-heart-failure-using-circadian-mark/)

### Inferences
- Minimal algorithm for a ₹5,000 home unit:
  1. Use a 28-day warm-up baseline (median and MAD per signal).
  2. Compute a nightly robust z-score for each signal: night HR, night RR, RR variability, circadian HR amplitude (inverted), activity (inverted), morning weight, impedance (inverted), with optional periodic-breathing share and upright-sleep minutes.
  3. Smooth each z-score with a 7-day EWMA.
  4. Combine into a weighted sum, with weights favouring weight/impedance and night HR (the strongest evidence), and RR next.
  5. Alert above an entry threshold, clear below a lower exit threshold, and require 2 or more signal groups to agree.
  6. Gate the alert with temperature (infection), AF and "meds changed" flags.
- Target operating point: HeartLogic-like performance, i.e. at most about 1.5 to 2 unexplained alerts/patient-year at a sensitivity of about 60 to 70%. Without S3 and impedance, expect lower sensitivity and a shorter lead time (about 1 to 3 weeks).

### Gaps
- Exact HeartLogic sensor weights are proprietary and were not found.
- No published low-cost (non-implant, non-patch) multi-signal HF index with prospective validation was found.

## Key Question 7: Realistic magnitudes for synthetic night-signal patient data

### Takeaway
Sourced anchors for synthetic data:
- Night HR: about +3 to 5 bpm over the weeks before an event; >5 bpm/week defines high risk.
- Circadian HR amplitude: falls from about 8 to about 5 bpm over about 21 days.
- Activity: falls about 12% (85 to 75 min/day) over about 8 weeks.
- Daily RR: rises only about 2% on average (cohort mean); a mean above 20/min defines a risk state.
- Index ramp: about 2 to 5 weeks of lead (HeartLogic median 34 days; LINK-HF 6.5 days).

### Cited Findings
- Night HR: >5 bpm weekly rise means about 2.5-fold risk — [Region H / WEARIT-France](https://research.regionh.dk/da/publications/dynamic-changes-in-nocturnal-heart-rate-predict-short-term-cardio/)
- Mesor 70.6 to 73.6 bpm and amplitude 8.3 to 4.9 bpm across the 21-day pre-event window — [TU/e](https://research.tue.nl/en/publications/predicting-acute-decompensated-heart-failure-using-circadian-mark/)
- Activity 85 to 75 min/day over 8 weeks — [Healio 2020](https://www.healio.com/news/cardiology/20200214/monitoring-physical-activity-via-implantable-device-may-predict-hf-hospitalization-death)
- Daily mean RR +2.2% before events — [Healio 2014](https://cm.healio.com/news/cardiology/20141002/hf-events-preceded-by-worsening-rapid-shallow-breathing); 30-day mean RR >20/min means higher risk — [BSci Alert Guide](https://www.bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heartfailure-diagnostic-ep/CRM-499506-AC-HeartLogic-Alert-Guide.pdf)
- HeartLogic index about 12 to about 23 in the week before events (snippet) — [OUP table](https://academic.oup.com/view-large/544450657)
- Lead times: median 34 days (IQR 19 to 66) — [BSci](https://bostonscientific.com/en-US/medical-specialties/electrophysiology/heartlogic-heart-failure-diagnostic/clinical-data/multisense.html); 6.5 days — [TCTMD](https://www.tctmd.com/news/stick-sensor-predicts-heart-failure-hospitalizations-pilot-study)
- Baseline prevalence for synthetic cohorts: SDB 76%, CSA 40% in HFrEF — [PubMed 17027333](https://pubmed.ncbi.nlm.nih.gov/17027333/)
- Event rate context: about 0.08 events/pt-yr out of alert vs 0.80 in alert — [EP Lab Digest](https://www.hmpgloballearningnetwork.com/site/eplab/multisensor-approach-heart-failure-monitoring); in WEARIT-France, 6% of patients had an event over a median of 68 days — [Region H](https://research.regionh.dk/da/publications/dynamic-changes-in-nocturnal-heart-rate-predict-short-term-cardio/)

### Inferences
Suggested synthetic generator parameters. These are inferred from the sources above; noise levels are my assumptions and not sourced.
- **Night HR:** stable baseline 60 to 75 bpm with night-to-night SD about 2 to 3 bpm. Pre-event ramp of +4 to 8 bpm over 14 to 28 days (beta-blocked patients toward the low end). Add AF episodes as a step change of +15 to 30 bpm with high irregularity.
- **24-h HR amplitude:** baseline about 8 bpm, ramping linearly to about 5 bpm over 21 days.
- **Night RR:** baseline 14 to 18/min with SD about 0.7 to 1/min. Pre-event ramp of +1 to 3/min over 7 to 21 days, with RR day-to-day SD doubling. Infection episode: +2 to 4/min together with skin temperature +0.5 to 1.5 °C and HR +8 to 15 bpm over 2 to 5 days.
- **Periodic breathing share of night:** baseline 0 to 30% (bimodal: about 40% of patients have CSA). Exploratory pre-event rise of +10 to 20 percentage points. Label this as hypothetical.
- **Activity:** baseline 60 to 120 active min/day. Pre-event decline of 10 to 25% over 3 to 8 weeks, with weekday/weekend noise.
- **Upright-sleep minutes:** baseline near 0 to 30 min. Pre-event rise to over 60 to 120 min in the final 3 to 7 days (hypothetical).
- **Event mix:** about 70% of events show a ramp detectable at least 7 days ahead and about 30% are abrupt (fewer than 3 days). This is consistent with about 70% sensitivity, but the split is my assumption.
- **False-alert sources to inject:** infection, AF onset, medication titration, heat waves, and bad-sleep nights, at roughly 1 to 2 confounder episodes per patient-year (anchored on 1.47 unexplained alerts/pt-yr).

### Gaps
- Night-to-night variability (SD) of RR and night HR in stable HF was not found in sources. The noise parameters above are assumptions.
- No source gave the share of HF events that are "abrupt" vs "gradual".
- MultiSENSE per-sensor absolute deltas exist only in figures (Gardner 2021) that I could not access; they would be the best calibration source.
