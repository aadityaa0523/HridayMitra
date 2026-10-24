# Build a 90-second check-in, not a wearable

**Bottom line:** Build a seated, 90-second daily "check-in station". It is a hacked bathroom scale with steel foot plates, a grab handle that also works as ECG electrodes, a finger pulse sensor, voice prompts in the local language, two big answer buttons and an SMS/voice-call modem. This is the best fit for the Transfinitte problem statement and for elderly rural and urban Indian users. The best published evidence for *low-effort, non-invasive* home warning comes from multi-sensor systems. Weight alone catches only **23–35% of heart failure (HF) events with about 4 false alerts per patient-year**. A scale that adds foot bioimpedance caught **70% of events with 2.58 alerts per patient-year** in one observational study ([TCTMD](https://www.tctmd.com/news/smart-scale-better-predicting-hf-events-weight-based-monitoring)). Implanted multi-sensor systems such as HeartLogic set the ceiling: **70% sensitivity, 1.47 unexplained alerts per patient-year and 34 days of warning** ([PSU Pure](https://pure.psu.edu/en/publications/a-multisensor-algorithm-predicts-heartfailure-events-in-patients-/)). Patches score well but need wear compliance. Bed sensors have almost no HF data and do not suit charpais, floor mats or shared beds. The coordinator's design is sound in direction. This report adopts most of it, with six changes: measure seated with everything on the platform; use four-electrode (tetrapolar) impedance; make standing BCG a stretch goal only; add a bendopnea question; use a cold-start prior; run voice analysis in "shadow mode" only. The main risks are the cost ceiling (the recommended 4G + ECG build is near or above ₹5,000 at conservative retail prices) and the fact that none of this combination has been tested on real Indian patients. Present it as **monitoring, not diagnosis**.

---

## 1. Executive summary: one station, many signals, few alerts

- **Recommendation:** Build the **seated 90-second check-in station**. Weight, foot bioimpedance (fluid in legs), resting heart rate and rhythm from handle ECG, SpO2 and pulse from a finger sensor, breathing rate, and two voice-answered symptom questions cover all six problem-statement (PS) targets in under 2 minutes a day. No patch is needed.
- **Why this beats the alternatives:** Adding foot impedance to a scale **doubled sensitivity versus weight rules (70% vs 35%) and cut alerts (2.58 vs 4.13 per patient-year)** ([TCTMD](https://www.tctmd.com/news/smart-scale-better-predicting-hf-events-weight-based-monitoring)). Wearables lose about half their users to non-wear ([Review PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)). Bed sensors have no validated HF sensitivity at all.
- **The custom part** for the hardware score is a **DIY tetrapolar bioimpedance front end** driven by the classic ESP32's built-in DAC. It costs an estimated ₹150–400, against about ₹3,500 for an AD5933 module ([AliExpress](https://www.aliexpress.com/w/wholesale-ad5933.html)). Simulate it in LTspice and show that wet or dry feet do not change the reading.
- **Alert engine (software score):** Copy proven patterns. Use worsening-only personal baselines (rolling median/MAD), trend detectors with published starting parameters (weight MACD 9/20 days > 0.62 kg; CUSUM; [Gyllensten 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)), HeartLogic-style hysteresis (alert at 16, clear below 6; [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)), a 2-of-3-day persistence rule, an amber "repeat check" step, and "probable cause" tags (infection-like, AF-like, salty meal, medicine change). Every alert comes with a spoken reason.
- **Edge cases:** Use an identity gate (weight and impedance band) plus guest mode for shared use, contact and stillness checks for shoes and wet feet, a fixed morning window for time-of-day effects, battery-first power and store-and-forward for power and internet cuts, and voice plus colour lights for users who cannot read. Silence never counts as "all fine": a missed check-in escalates.
- **Escalation ladder:** Device light and voice, then family voice call and SMS, then ASHA worker, then doctor. Rural homes use a 4G Cat-1 modem (A7670C works on Jio, Airtel and Vi; SIM800L 2G does not work with Jio). Urban homes add Wi-Fi, WhatsApp and a web dashboard.
- **Validation:** Use at least 200 synthetic patients (the PS minimum is 20), each with a 30-day warm-up and a 30-day test window. Model weight-silent episodes and confounders explicitly. Test the HR code on BIDMC CHF. Split by patient. **Beat the weight-rule baseline (23–35% sensitivity, about 0.35 false alerts per patient-month) at no more than 0.21 false alerts per patient-month.**
- **Cost reality:** The lean 2G build costs about **₹2,600–5,000**. The recommended 4G + ECG build costs about **₹3,600–6,500**, depending on prices that are not yet verified. Get real quotes this week. Use the cost-down levers in Section 7 (hacked scale, bare modules, one battery cell, no OLED) to present a sourced BOM under ₹5,000.

---

## 2. Existing solutions: multi-sensor fusion wins, weight alone fails

The landscape splits into four groups: implants (best numbers, not usable here), wearables and patches (good numbers, high effort), zero-effort bed and radar sensors (almost no HF data), and low-effort daily "step-on" or "speak-in" checks (moderate numbers, the best fit for the PS). A note on the false-alert column: studies count these differently. Some report all alerts, some only "unexplained" ones, and many report none.

**Evidence key:** **A** = randomised trial or peer-reviewed validation with a held-out test set. **B** = peer-reviewed observational or pilot study. **C** = conference or press data, or company-linked. **D** = protocol, proof-of-concept or no HF outcome data.

| Approach | Example | Patient effort | Sensitivity | Specificity / false alerts | Lead time | Cost class | India fit | Evidence |
|---|---|---|---|---|---|---|---|---|
| Daily weight rules | FAST trial ([MDedge](https://mdedge.com/content/impedance-beats-weight-predicting-hf-events)) | Daily step-on; only 76% did it daily | **23%** | **4.3 unexplained / pt-yr** | not reported | Very low | Good (if barefoot routine) | B |
| Weight rules (comparator) | SCALE-HF 1 ([TCTMD](https://www.tctmd.com/news/smart-scale-better-predicting-hf-events-weight-based-monitoring)) | Daily step-on | **35%** | 4.13 alerts / pt-yr | not reported | Very low | Good | C |
| Weight + foot impedance scale | Bodyport, SCALE-HF 1 ([TCTMD](https://www.tctmd.com/news/smart-scale-better-predicting-hf-events-weight-based-monitoring)) | Daily barefoot step-on | **70%** | **2.58 alerts / pt-yr** | ~14 days **[company/press claim]** ([CLP](https://clpmag.com/disease-states/cardiovascular/heart-failure-monitoring-tech-doubles-sensitivity-for-predicting-events-versus-standard-of-care/)) | Medium (US) | Good form factor | C (observational; presenter consults for company) |
| BCG + ECG scale | Inan, Georgia Tech ([GT news](https://ece.gatech.edu/news/2023/12/bathroom-scale-could-monitor-millions-heart-failure)) | ~1 min standing | Classification only (43 patients) | not reported | not shown | Low | Good | D |
| Trend algorithms on non-invasive vest impedance | Gyllensten 2016 ([PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)) | Daily vest + weight | **60%** (impedance CUSUM); 33% (weight MACD) | Spec 96%; **~0.48 false / pt-yr**; weight spec 91% | 2-week window | Medium | Vest not practical | B (cross-validated) |
| Multi-sensor chest patch | LINK-HF ([TCTMD](https://www.tctmd.com/news/stick-sensor-predicts-heart-failure-hospitalizations-pilot-study)) | Continuous adhesive patch | **76–88%** | Spec 85%; false alerts not reported | **median 6.5 days** | High | Poor (PS: patch "may not be ideal") | B (n=100 pilot) |
| Multi-sensor patch | MUSIC ([Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)) | Continuous patch | 63% | Spec 92%; **0.9 false / pt-yr** | not reported | High | Poor | B |
| RF lung-fluid patch | ZOLL µCor, BMAD ([TCTMD](https://www.tctmd.com/news/wearable-device-helps-hf-patients-avoid-coming-back-hospital-bmad)) | Continuous patch | not reported | not reported | "days–weeks" | High | Poor | B (outcome −38% readmissions, not randomised) |
| Wearable defibrillator vest | ZOLL LifeVest ([Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)) | Vest ~24 h | 69% | Spec 60%; "high" false positives | median 32 days | Very high | Not applicable | B |
| Lung-fluid vest (spot check) | ReDS ([Region H](https://research.regionh.dk/en/publications/remote-dielectric-sensing-to-detect-acute-heart-failure-in-patien/)) | 1.5–3 min seated | 46% (ED diagnosis) | Spec 88% | n/a | High | Poor (cost) | B; outcome trials mixed |
| Under-mattress piezo | EarlySense ([PMC5221726](https://pmc.ncbi.nlm.nih.gov/articles/PMC5221726)) | Zero | Not reported; night breathing rate was the top predictor | not reported | not reported | Medium–high | Weak (charpai, floor mat, shared bed) | D (29 patients) |
| Indian under-mattress BCG | Dozee ([Prime VP](https://www.primevp.in/news-and-announcement/dozee-raises-inr-44-croreusd-6-million-series-set-transform-critical-care-infrastructure-across-india-through-contactless-remote-patient-monitoring-platform)) | Zero | No HF prediction data found | — | — | Home: ~$345 + $25–50/month (US) ([FitGap](https://us.fitgap.com/products/034460/dozee)) | Hospital-focused | D for HF |
| Bedside radar | Sleepiz One+ ([AASM](https://aasm.org/sleepiz-one-bedside-monitoring-device-receives-fda-clearance/)) | Zero | FDA-cleared for HR/RR only; no HF data | — | — | Medium | Weak | D for HF |
| Smartwatch / ring | Apple Watch HF study ([ClinicalTrials.gov](https://clinicaltrials.gov/study/NCT06819618)) | Wear + charge daily | No prediction data; circadian PPG AUC ~0.74 ([Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)) | — | — | Medium | Urban only | D |
| Voice analysis app | Cordio HearO, COMMUNITY-HF ([TCTMD](https://www.tctmd.com/news/voice-analysis-picks-patients-risk-hf-hospitalization-community-hf)) | ~30 s/day on smartphone; **83.5% adherence over ~4 years** | **71–85%** | **2.4–3 false / pt-yr** | **24–26 days** (retrospective) | Software | Needs a smartphone; language-independent claim | C (company-linked, conference) |
| Counting test | Roth score ([PMC6490799](https://pmc.ncbi.nlm.nih.gov/articles/PMC6490799)) | 10 s | 78% for SpO2 < 95% (not HF events) | Spec 73% | — | Free | Good | D; over the phone it can give false reassurance ([CEBM](https://cebm.net/?p=15546)) |
| Daily symptom questions / IVR | Various ([Frontiers 2025](https://www.frontiersin.org/articles/10.3389/fcvm.2025.1659830/full)) | 30 s | No published sensitivity found; bendopnea adjusted HR 1.6 for events | — | Symptoms come late | Free | Good with voice | B (bendopnea, hospital cohort) |
| Implant reference: HeartLogic | MultiSENSE ([PSU Pure](https://pure.psu.edu/en/publications/a-multisensor-algorithm-predicts-heartfailure-events-in-patients-/)) | None (implant) | **70%** | **1.47 unexplained / pt-yr** | **median 34 days** | Very high | Not applicable | A (held-out test cohort; sponsor-funded) |
| Implant reference: OptiVol | FAST ([Cardiac Rhythm News](https://cardiacrhythmnews.com/?p=4954)) | None | 76% | 1.9 unexplained / pt-yr | — | Very high | Not applicable | B |
| Implant reference: CardioMEMS | CHAMPION ([ACC](https://www.acc.org/Latest-in-Cardiology/Clinical-Trials/2015/12/29/12/44/CHAMPION)) | Daily pillow reading | Outcome only: −28% HF admissions at 6 months | — | — | Very high | Not applicable | A |

Three facts from this table drive the design. First, **weight alone is the weakest signal**. In one cohort, weight in the two weeks before decompensation was not different from baseline at all (83 vs 84 kg) ([Gyllensten](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)). In a rural trial, a 5 lb weekly gain was linked to emergency visits but not to readmission, while breathlessness predicted both ([Flinders](https://researchnow.flinders.edu.au/en/publications/rapid-5lb-weight-gain-is-not-associated-with-readmission-in-patie/)). Second, **impedance and multi-signal fusion lift sensitivity**, but impedance alone gives "high false positives" ([Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)). Third, **the lowest-effort daily task with long-term data (a 30-second voice recording) kept 83.5% adherence for years**. Weekly-or-more telemonitoring use fell to 55% in large trials. Effort, not sensor accuracy, decides whether a system works in practice.

Gaps in the evidence: no peer-reviewed study gives HF sensitivity for consumer body-composition scales, Dozee, Withings Sleep, rings or watches. The full SCALE-HF 1 paper (lead time, adherence) was not retrieved, so its 14-day lead time is a press figure only.

---

## 3. Lessons: programs fail on adherence and response, not on sensors

### Adherence decays within weeks, and the response loop decides outcomes

Large telemonitoring trials show the same pattern. **TIM-HF2** cut all-cause mortality by about 30% (7.86 vs 11.34 per 100 person-years). It sent daily weight, blood pressure, ECG and self-rated health to a **24/7 physician-staffed telemedical centre** that acted on the data ([The Hospitalist](https://blogs.the-hospitalist.org/content/home-telemonitoring-heart-failure-cuts-mortality)). Trials with weak response loops were neutral. In **Tele-HF**, only 55% of patients still used the IVR system at least three times a week by the end ([NEJM CardioExchange](https://blogs.nejm.org/cardioexchange/wp-json/wp/v2/posts/4565)). In **BEAT-HF**, adherence to telemonitoring was 55% at just 30 days, and readmission was about 50% in both arms ([PMC4827701](https://pmc.ncbi.nlm.nih.gov/articles/PMC4827701)). TEN-HMS found that structured human contact (nurse phone calls) cut mortality as much as telemonitoring did ([ACC](https://www.acc.org/Latest-in-Cardiology/Clinical-Trials/2013/05/30/16/25/TENHMS)). Benefit is largest in sicker, adherent patients, and depression reduces it ([Frontiers 2022](https://www.frontiersin.org/journals/cardiovascular-medicine/articles/10.3389/fcvm.2022.943778/pdf)).

Detection alone does not help patients. Implanted impedance alerts alone (OptiVol) did not reduce admissions or deaths in trials ([Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)). In a real-world HeartLogic study, clinicians acted on only 43% of alerts, and acting was linked to fewer HF events ([Boston Scientific newsletter](https://www.bostonscientific.com/en-EU/medical-specialties/electrophysiology/clinical-evidence-newsletter/2023/3.html)). When the response loop works, it is usually simple: in MANAGE-HF, 74% of alert cases led to a medicine change, and 89% of those were diuretics ([Duke Scholars](https://scholars.duke.edu/publication/1519187)).

**For India**, this means the alert must reach a person who can act, which in most homes is a family member and the ASHA worker. Only about 25% of Indian HFrEF patients leave hospital on full guideline therapy ([THFR, PMC10424635](https://pmc.ncbi.nlm.nih.gov/articles/PMC10424635)). The response loop therefore also needs a path to a doctor, for example through eSanjeevani, which has more than 1.42 lakh Ayushman Arogya Mandir spokes ([NewsOnAir](https://newsonair.gov.in/esanjeevani-achieves-milestone-of-50-cr-teleconsultations-from-across-the-country/)). One gap: HF is not named in the national NCD programme documents found, so ASHA integration needs a state or NHM partnership. Alerts must also be rare. The Kilkari voice programme lost listeners because of low-value calls and unanswered calls ([NCT03576157](https://clinicaltrials.gov/study/NCT03576157)).

### What reduces false alerts (with evidence)

| Technique | Evidence | Effect |
|---|---|---|
| Fuse several signals | MUSIC: single-parameter algorithms had high false-positive rates; the multi-sensor version had 0.9 per pt-yr ([Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)) | Fewer false alerts at the same sensitivity |
| Trend detectors on a personal baseline instead of "+2 kg" rules | Gyllensten: MACD/CUSUM beat rule-of-thumb (weight 33% vs 20%; impedance 60% vs 33%) ([PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)); simple sudden-change rules gave many alerts with poor sensitivity ([PMC5240411](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5240411/)) | Higher sensitivity and fewer alerts |
| Hysteresis (alert high, clear low) | HeartLogic alerts at 16 and clears below 6 ([PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)) | Stops on/off "flicker" alerts |
| Check measurement quality before alerting | TwoCan: **45% of incorrect alerts came from inaccurate measurement, 27% from supraventricular arrhythmia**; HR > 110 was linked to *incorrect* alerts ([JMIR Cardio 2024](https://cardio.jmir.org/2024/1/e52648)) | Repeat-check and rhythm path remove the biggest causes |
| Label "explained" alerts | MultiSENSE counts only unexplained alerts as false; causes include new AF, therapy stopped, changes in activity or sleep habits ([PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)) | Clinician can dismiss quickly |
| Recognise the infection pattern | In COVID-19, night HR rose 3–4× more than in HF events, and activity fell more ([Gardner 2021, sponsor](https://www.bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heart-failure-diagnostic/heartlogic-newsletter/issue-7-2021/Gardner_ESC-HF_2021.pdf)) | "Infection-like" tag instead of an HF alert |
| Avoid self-typed values | End-digit preference in self-entered values causes false alerts ([JMIR Cardio 2024](https://cardio.jmir.org/2024/1/e52648)) | Automatic capture only |

---

## 4. Edge cases and false detections: each one gets a specific fix

Most failure modes below come from engineering reasoning, not from studies. The notes found **no study that measures failure from shoes, blankets, bed partners or meal timing**. Items with a published basis are marked [cited]. All countermeasures are **design proposals** to be tested.

| # | Edge case | How it corrupts the data | Countermeasure in our design |
|---|---|---|---|
| 1 | **Another person uses the station** (spouse, child, guest) | Wrong weight, impedance and HR enter the patient's baseline; false alert or masked worsening | Identity gate: accept only if weight is within ±(3 × 14-day MAD + 1.5 kg) of the recent median **and** impedance is within the patient's band ([notes based on Fitbit Aria / patent practice](https://fda.innolitics.com/device/K133872)). Otherwise the voice asks "Is this Ramesh?" (green/red button). If the answer is no or there is no answer, log it as a guest and never feed it to the baseline. ECG identity is only a tie-breaker, because real-world error is 9–22% ([arXiv](https://ar5iv.labs.arxiv.org/html/2003.03273)). Offer guest mode as a family benefit. |
| 2 | **Two people with similar weight** | Identity gate passes the wrong person | Add the impedance signature, the ECG tie-breaker and the "Is this…?" prompt on every borderline reading |
| 3 | **Someone sleeping in the same bed; blankets or extra pillows change data** | Ruins bed-sensor breathing and HR signals | **Avoided by design:** no bed sensor. Orthopnea is asked as a *change* ("more pillows than usual / had to sit up?"), because habitual pillow use confounds pillow counts ([UMaryland](https://blogs.pharmacy.umaryland.edu/atrium/?p=424)) |
| 4 | **Sudden problem during the day** | A daily check misses it | SOS button on the station (optional pendant); "breathless at rest" can be reported at any time by pressing red; any extra check-in runs the red-flag rules at once; SOS triggers a family voice call and SMS |
| 5 | **Power cut** | Missed check-in; lost data; modem resets | Runs on 18650 cells and sleeps between check-ins; readings saved in flash; queued SMS sent later (store-and-forward); charges when mains returns. Rural supply often has 2–4 interruptions a day ([Prayas](https://energy.prayaspune.org/images/pdf/100-rural-electrification-is-not-enough.pdf)) [cited] |
| 6 | **Weak or no internet** | Cloud-based logic fails | Engine runs on the ESP32. Alerts go by SMS and voice call over 2G/4G, which need no data. Cloud sync only when available. If there is no network at all, local voice and light tell the family and the ASHA hears a summary on her visit |
| 7 | **Illiterate users / local language** | Text screens and typed answers fail | Voice prompts in the local language; 3 coloured lights; 2 large buttons with shape and colour (green ✓ circle, red ✗ square); nothing to read. Many older rural adults have about 11% digital literacy ([Geriatrics 2022](https://doaj.org/article/84c3b157657d43428b43f94bc238b9f1)) [cited] |
| 8 | **Rural vs urban homes** | One channel does not fit both | Rural: 4G Cat-1 SMS + voice call, ASHA in the loop. Urban: same, plus Wi-Fi sync, WhatsApp and a web dashboard for children living elsewhere |
| 9 | **Atrial fibrillation (AF)** | HR jumps; irregular beats break HR baselines; a common cause of false HF alerts [cited: [TwoCan](https://cardio.jmir.org/2024/1/e52648), [Bertini](https://ricerca.uniba.it/retrieve/4a283bc7-cf07-4baf-952e-18de9d9fa29e/Bertini_HRJ2022_Proof.pdf)] | Measure RR-interval irregularity from handle ECG. New irregular rhythm goes to a separate "rhythm check" alert (doctor review, not an HF alert). Freeze the HR baseline while AF persists. PPG-only AF calls have low PPV in older people ([PMC7125433](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7125433/)), so confirm with ECG |
| 10 | **Infection / fever** | HR and breathing rise; looks like HF | "Infection-like" tag when HR rises sharply (e.g., +10–20 bpm within 1–3 days) with fast breathing and flat weight/impedance (simulation assumption; pattern from [Gardner](https://www.bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heart-failure-diagnostic/heartlogic-newsletter/issue-7-2021/Gardner_ESC-HF_2021.pdf)). An adaptive extra question asks "Do you have fever or cough?" Still notify family (infection can trigger HF), but with a different message |
| 11 | **Salty meal / festival food** | Weight +0.5–1.5 kg that reverses in 1–3 days (assumption) | Persistence rule (2 of 3 days) plus MACD trend; a single-day jump is ignored unless impedance or symptoms agree |
| 12 | **Medicine change (diuretic up, down or stopped)** | Weight steps down 1–2 kg, or real worsening after stopping therapy (a documented alert cause, [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)) | ASHA or family sends an SMS keyword (e.g., "DAWA") or presses a 3-second button combination to mark the change. Freeze or reset the baseline for about 7 days and widen the identity band. Do not suppress alerts after a dose is *stopped* |
| 13 | **Scale misuse** (standing on the edge, holding a child or bucket, leaning on a rail) | Wrong weight | **Everything the user touches (stool and handle) is mounted on the platform**, so leaning does not change total weight. Stand-still check (load variance), centre-of-pressure check from the 4 load cells, and a >1.5 kg single-day jump that does not persist is discarded |
| 14 | **Shoes, socks, slippers** | Foot impedance becomes open-circuit; weight offset | The contact check sees a very high or no current path. Voice: "Please remove slippers." Retry, then log as "no impedance" without blocking weight |
| 15 | **Wet feet after bath; dusty or cracked heels** | Skin-contact resistance changes and can mimic a fluid change | **Tetrapolar (4-electrode) measurement**: two plates inject current, two sense voltage, which largely cancels contact resistance. Prove it in LTspice by sweeping contact resistance. Contact-quality limits trigger a voice prompt: "Please dry your feet" |
| 16 | **Time of day, meals, toilet** | Weight changes during the day; impedance-type readings shift with posture and time (ReDS reads higher in the morning, [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)) [cited] | Fixed window (after toilet, before breakfast), always seated, same posture. Readings outside the window are stored but down-weighted |
| 17 | **Heavy winter clothes or shawl** | +0.5–1.5 kg step (assumption) | Seasonal step change caught as a non-persistent jump; optional voice tip "same light clothes each day" |
| 18 | **Missing data** (forgot, travelling, ill) | Gaps break baselines; missing days may themselves mean worsening (low compliance tracked worse BNP, [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)) [cited] | Missing days do not reset the baseline. Causal interpolation with a gap cap. Exclude weeks with fewer than 3 readings from trend scoring (as Gyllensten did). Missed check-in by late morning gives a reminder, then a family SMS. 2+ missed days count as a weak risk feature |
| 19 | **Device fault** (load-cell drift, broken wire, low battery, modem dead) | Silent failure looks like "all fine" | Self-test each check-in: an on-board reference resistor for the impedance channel, load-cell zero check, battery voltage. Weekly "device OK" SMS. Monthly weight check with a known load (e.g., a filled 5-litre water can). Fault SMS to family |
| 20 | **Cold start / first weeks after discharge** | No personal baseline yet, during the riskiest period (18% of Indian HF patients in THFR died within 3 months, [PMC10424635](https://pmc.ncbi.nlm.nih.gov/articles/PMC10424635)) [cited] | Seed the baseline with the hospital "dry weight" entered at setup. Blend population priors with personal data (shrinkage weight n/(n+7) after n days). Red-flag rules work from day 1 |
| 21 | **Muscle and fat loss hiding fluid gain** | Weight flat while fluid rises | Impedance, HR, breathing and symptoms carry the signal; 30–40% of synthetic episodes are "weight-silent" |
| 22 | **Dehydration / summer heat** | Weight down, HR up | "Dehydration-like" tag (weight ↓ with HR ↑): HR alert only, not an HF fluid alert |
| 23 | **Tremor, cold fingers, poor perfusion** | PPG fails (no age-specific data found) | PPG quality index; retry with "hold still, warm your hands"; fall back to ECG HR; SpO2 marked "not available" rather than guessed |
| 24 | **Wrong button press / memory problems** | False symptom "yes" | Repeat the question once; keep button meanings the same every day; a symptom "yes" alone raises amber, never red, unless "breathless at rest" is confirmed twice |
| 25 | **Implanted pacemaker or ICD** | Safety question for injected current (many HF patients have devices) | **Not covered in our sources; verify.** Use very low current and an "impedance-off" mode set by the doctor at setup |
| 26 | **Fall risk on the platform** | Injury | Seated use, low and wide non-slip platform, the handle as a rail |
| 27 | **Family phone unanswered or number changed** | Alert lost (a main Kilkari drop-off cause, [NCT03576157](https://clinicaltrials.gov/study/NCT03576157)) [cited] | Retry the call, then call a second contact, then SMS the ASHA. Phone numbers can be updated by SMS keyword from a registered number |
| 28 | **Sudden death or arrhythmic events** | Not predictable by trend monitoring (LINK-HF predicted none of 12 deaths, [TCTMD](https://www.tctmd.com/news/stick-sensor-predicts-heart-failure-hospitalizations-pilot-study)) [cited] | State it clearly in the disclaimer: monitoring, not diagnosis, and not an emergency device |

---

## 5. Ranked ideas: ten options, eight make the core build

Ideas are ranked by fit to the PS and the judging weights (creativity 20, ease and long-term use 20, software 20, hardware 15, science 15, cost/India 10), then by evidence strength. "Extra cost" means cost on top of the core station.

| Rank | Idea | PS targets covered | Evidence strength | Extra cost (₹) | Main edge-case risk |
|---|---|---|---|---|---|
| 1 | **Seated 90-s "closed-loop" check-in station** (stool and handle on the platform) | All six | Each part has evidence; the combination is untested | Base unit (Section 7) | Adherence in India unknown |
| 2 | **DIY tetrapolar foot bioimpedance from the ESP32 DAC** (custom part) | Fluid in legs; weight-silent episodes | Moderate: Bodyport 70% vs 35% (C-grade); DIY accuracy unknown | 250–600 (plates + front end, estimate) | Wet feet, implants, calibration |
| 3 | **Confounder-aware, explainable alert engine** | "One signal is rarely enough"; explanations | Strong design pattern (HeartLogic, Gyllensten) | 0 | Parameters come from implant/vest data |
| 4 | **Two-step confirmation + immediate red flags** | False alerts; sudden problems | Good rationale: 45% of wrong alerts were measurement errors (TwoCan) | 0 | Delay of one day for amber |
| 5 | **Identity gate + guest mode** | Shared use | Commercial practice; no accuracy data | 0 | Similar-weight family members |
| 6 | **Bendopnea built into the barefoot routine + change-based orthopnea + adaptive questions** | Trouble breathing lying flat; breathlessness | Bendopnea adj. HR 1.6 (hospital cohort); no home cut-offs | 0 | Wrong presses, late symptoms |
| 7 | **"Silence is never green"**: missed check-in escalation, weekly device-OK, missingness as a feature | Adherence, device faults, less activity (proxy) | Low compliance tracks worse outcomes (wearable data) | SMS cost only | Alert fatigue if over-used |
| 8 | **Local-language voice-call escalation ladder into ASHA / eSanjeevani** | Real home use; response loop | TIM-HF2 shows the response loop matters; Kilkari shows voice reach | Modem (in base) | Module voice support; ASHA workload |
| 9 | **Mother-tongue voice biomarker in shadow mode** | Fluid in lungs (proxy), breathing | Cordio 71–85% sens, 2.4–3 FA/yr (C-grade); DIY features unvalidated | 100–250 (mic, not verified) | Colds, dentures, accents; no public HF voice data |
| 10 | **Sit-to-stand force curve from the load cells** | Less activity (function proxy) | None for HF in our sources (novel, weak) | 0 | Noisy at HX711 sample rates |
| Opt. | **SOS + activity pendant** (BLE accelerometer; night trunk angle) | Less activity; orthopnea (sleeping propped up); daytime SOS | Activity drop after decompensation (non-sedentary time 9% vs 27%, [Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)); wear compliance ~50% | Not priced (estimate 300–600) | Not worn or not charged |
| Stretch | **Two-frequency impedance ratio** (e.g., ~5 kHz vs ~50 kHz) | Fluid vs tissue change | None in our sources | 0 | Extra calibration work |

### What each idea is and why it is unique

**1. Seated closed-loop check-in station.** The patient sits on a stool that stands *on* the scale platform, puts bare feet on four steel plates and holds a steel handle that is also mounted on the platform. For 60 seconds the station records ECG (hands), finger PPG, foot impedance and weight together. Then it asks two questions. The unique point is the closed force loop: the stool and rail are part of the weighed system, so a frail person can sit and lean without spoiling the weight, and posture is the same every day. Bodyport and Inan both use standing scales. Seated use is safer for frail elderly users and gives a truer resting HR than standing.

**2. DIY tetrapolar foot bioimpedance (the custom part).** The classic ESP32 has a DAC with a cosine generator. The coordinator cites ESP-IDF documentation for a range of about 130 Hz–55 kHz; this is not verified in our notes. The DAC drives a band-pass filter and an op-amp current source (Howland type, with DC-blocking capacitors and a series resistor that limits current). The current goes through two outer foot plates. An instrumentation amplifier reads the voltage on two inner plates, and a precision rectifier and low-pass filter feed the ESP32 ADC. An on-board reference resistor is measured at every check-in for calibration and fault detection. This targets Bodyport's evidence (foot impedance plethysmography lifted sensitivity from 35% to 70%) at a fraction of the cost of an AD5933 module (about $41, roughly ₹3,500; [AliExpress](https://www.aliexpress.com/w/wholesale-ad5933.html)). **Caveat:** Bodyport's index is proprietary and our circuit is not the same measurement. Its accuracy is unknown until bench-tested. Keep the injected current within IEC 60601-1 patient-current limits and never measure while the charger is connected.

**3. Confounder-aware, explainable alert engine.** Personal baselines, worsening-only scores, trend detectors, hysteresis, persistence and "probable cause" tags (Section 6). It is unique because published home systems either use fixed weight rules or closed proprietary indices. Ours is open, runs offline on a ₹500-class chip and says *why* it fired in the patient's language.

**4. Two-step confirmation and red flags.** Amber never goes straight to the doctor. It triggers a repeat check (that evening or next morning) with a longer 90-second recording. Red needs two signal families or three days of persistence. A small set of safety rules bypasses this (Section 6). The rationale is TwoCan, where almost half of wrong alerts came from bad measurements ([JMIR Cardio](https://cardio.jmir.org/2024/1/e52648)).

**5. Identity gate and guest mode.** Weight-band plus impedance matching, with a spoken "Is this…?" prompt. Turning guests into a feature ("anyone can weigh themselves, it won't count for Papa") makes the device welcome in a shared Indian home instead of something to guard.

**6. Bendopnea in the routine.** The patient must bend to remove slippers anyway, so the device asks: "When you bent to take off your slippers, did you get breathless?" Bendopnea is the best-validated single bedside symptom (HF rehospitalisation 35.1% vs 22.3%; adjusted HR 1.6; [Frontiers 2025](https://www.frontiersin.org/articles/10.3389/fcvm.2025.1659830/full)). Orthopnea is asked as a change from usual. Adaptive questions (fever? swollen feet? walked less?) are asked only when signals move, so the daily load stays at two questions.

**7. "Silence is never green."** A missed check-in, a dead battery or a failed sensor is never shown as safe. The family gets a reminder SMS, the device sends a weekly "device OK" SMS, and missed days count as a weak risk feature. This copies the finding that low wear compliance tracked higher BNP and rehospitalisation ([Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)).

**8. Voice-call escalation into existing public rails.** The device itself places a call over the modem and plays a recorded message in the family's language. SMS backs it up within the 70-character Indic limit ([Exotel](https://developer.exotel.com/docs/sms-support/unicode-sms)). Alerts route to the ASHA, who already follows up hypertension and diabetes patients ([NHSRC](https://nhsrcindia.org/sites/default/files/IRHSS_%20A%20Training%2C%20Process%2C%20and%20Impact%20Evaluation%20of%20Utilizing%20ASHAs%20for%20NCD%20Screening.pdf)), and to an eSanjeevani consult. Check that your exact modem variant supports voice calls and audio input before you rely on this.

**9. Voice biomarker in shadow mode.** The patient says the same short sentence in their mother tongue each day (about 10 s, INMP441 mic). The device stores simple features (duration, pauses, pitch stability, maximum "aaah" time) against a personal baseline. Cordio reports language-independent performance because each patient is their own baseline ([TCTMD](https://www.tctmd.com/news/voice-analysis-picks-patients-risk-hf-hospitalization-community-hf)), but the data are company-linked and no language-stratified accuracy was reported. **Log the features and show them in the demo, but keep them out of the alert score** until validated. Do not use the Roth counting test as an alert input.

**10. Sit-to-stand force curve.** When the patient stands up at the end, the load cells see a force spike whose timing and size reflect leg strength and effort. A slower rise over days could be a cheap "less activity / weaker" proxy. This is novel, with no HF evidence in our sources. The HX711 runs at only about 10 or 80 samples per second (datasheet; verify), so test feasibility first.

**Rejected or downgraded:** Standing BCG on a hacked scale becomes a stretch goal. The only evidence is a 43-patient classification study ([GT](https://ece.gatech.edu/news/2023/12/bathroom-scale-could-monitor-millions-heart-failure)), and HX711 bandwidth is likely too low; use ECG and PPG for HR. A pure bed or cot sensor is rejected (no HF sensitivity data; charpai, floor-mat and shared-bed problems). A pure wrist band is rejected as the primary device (about 50% full wear compliance; PPG motion artefact). Phone-photo edema has no accuracy data ([UCLan](https://clok.uclan.ac.uk/43736)) and is skipped.

### Recommended combination

Build ideas **1–8 as the core**. Run **9 and 10 in shadow mode** (recorded and plotted, not scored), because they add creativity points without risking false alerts. Offer the **pendant as an optional add-on** for high-risk urban patients who want activity tracking. Keep **two-frequency impedance** as a stretch goal if the LTspice work goes well.

---

## 6. Recommended system: architecture, alert logic and escalation

### Block diagram

```
          [Mains 5V adapter] --> [Charger + protection] --> [2x 18650] --> [Boost/LDO rails]
                                                         (measure only when charger is off)
 PATIENT SIDE (all mounted on the weighed platform)
  4 load cells --> HX711 ---------------------------\
  4 steel foot plates <--> DIY tetrapolar BIA        \
     (ESP32 DAC -> filter -> current source;          \
      INA -> rectifier -> ADC; ref. resistor)          >--> ESP32 (classic, has DAC)
  Steel handle (2 hand plates) --> AD8232 (ECG) ------/      - quality gates, identity gate
  Finger clip on handle --> MAX30102 (PPG, SpO2) ----/       - baseline + alert engine
  Green / Red buttons, SOS button ------------------/        - flash log, store-and-forward
  (optional) INMP441 mic -----------------------------/      - deep sleep between check-ins
                                                                 |            |         |
                          3 LEDs (G/A/R) + MAX98357A speaker <---+            |         |
                          (optional) 1.3" OLED icons <------------------------+         |
                          A7670C 4G modem: SMS + voice call to family / ASHA / doctor <-+
                          Wi-Fi (urban): sync to cloud dashboard / WhatsApp gateway
```

### Signals, sensors and quality gates

| Signal | Sensor and method | PS target | Quality gate (reject or retry if failed) | Evidence that the signal matters |
|---|---|---|---|---|
| Weight (kg) | 4 load cells + HX711, seated, stool tared | Weight gain | Stillness (low variance for 5 s), centre of pressure inside the plate, identity gate, time window | Weight rises from ~1 week before admission; ORs 2.77–7.65 by size of gain ([PMC2892745](https://pmc.ncbi.nlm.nih.gov/articles/PMC2892745)) |
| Foot impedance (log Ω) | DIY tetrapolar BIA at ~50 kHz | Fluid in legs | Contact impedance within limits, reference-resistor check, no charger connected | Bodyport 70% vs 35% ([TCTMD](https://www.tctmd.com/news/smart-scale-better-predicting-hf-events-weight-based-monitoring)); vest impedance CUSUM 60% at spec 96% ([PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)) |
| Resting HR (bpm) | Handle ECG (AD8232, lead I), median of last 30 s of 60 s seated | Faster resting HR | ECG quality index (e.g., NeuroKit2 quality functions); PPG backup | Night HR rise > 5 bpm more than doubled risk ([Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)). Note: ours is a morning seated HR, not a night HR |
| Rhythm irregularity | RR-interval irregularity from ECG | AF confounder / trigger | ≥ 30 clean beats | AF causes false HF alerts and predicts alerts ([PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)) |
| Breathing rate (/min) | ECG-derived and PPG-derived respiration over 60–90 s | Faster breathing | Agreement between the two estimates; use 7-day averages | Rises ~1.5–2.1/min before events; 30-day SD > 1.0 gave HR 12.3 ([NOTICE-HF](https://www.link.springer.com/article/10.1007/s10840-015-9983-6)). **Weak:** a 60-s spot count is noisy against a 2/min change |
| SpO2 (%) | MAX30102 finger clip | Fluid in lungs (proxy), red flag | PPG quality index; repeat once if low | SpO2 < 90% used as an alert trigger in TwoCan ([JMIR Cardio](https://cardio.jmir.org/2024/1/e52648)) |
| Orthopnea (yes/no) | Voice question, button answer: "more pillows or sat up to breathe last night?" | Trouble breathing lying flat | Repeat if no answer | Pillow count is weak; ask about change |
| Bendopnea / breathless (yes/no) | Voice question after removing slippers | Breathlessness | Repeat if no answer | Adj. HR 1.6 ([Frontiers 2025](https://www.frontiersin.org/articles/10.3389/fcvm.2025.1659830/full)) |
| Activity proxy | Check-in time, missed days, adaptive question "walked less?", sit-to-stand curve (shadow), optional pendant | Less activity | — | Activity falls after decompensation ([Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)). **Our proxies are weak; the pendant is the only direct measure** |
| Voice features | Mic, 10-s fixed sentence | Lungs / breathing (proxy) | Loudness and noise check | Company-linked only; **shadow mode** |

The **"fluid in lungs"** target has no direct cheap sensor in this design. It is covered by proxies (breathing rate, SpO2, orthopnea and bendopnea, and voice in shadow mode). Say this openly in the pitch.

### User journey (about 90 seconds, once each morning)

| Step | Time | What happens |
|---|---|---|
| 1 | 0 s | Patient sits on the stool. Load on the platform wakes the device. Voice: "Namaste Ramesh-ji. Please take off your slippers." |
| 2 | 5 s | "When you bent down, did you feel breathless? Green for no, red for yes." |
| 3 | 15 s | "Put both feet on the steel plates and hold the handle gently. Put your finger in the clip. Sit still and breathe normally." |
| 4 | 15–75 s | 60 s of ECG, PPG, impedance and weight. If contact is poor: "Please press your feet down" or "dry your feet". Retry up to 2 times |
| 5 | 75 s | "Last night, did you need more pillows or have to sit up to breathe?" |
| 6 | 85 s | Result: green light + "All fine today, thank you." Or amber + "Some readings changed. Please check again this evening." Or red + "Your weight and breathing have changed. We are calling Sunita and ASHA didi." |
| 7 | 90 s | (Optional, shadow) "Please say: *Aaj mausam accha hai*." The device sleeps |

Family members can weigh themselves too. The device says "Guest reading" and does not store it as the patient's reading.

### Alert logic with starting parameters

All parameters below are **starting points**. They come from implant and vest studies, not from foot-impedance scales. Retune them on the synthetic training set only.

**Step 1: Clean.** Drop readings that fail quality gates or the identity gate. Discard a weight jump of more than 1.5 kg in one day that does not persist the next day. Mark medicine-change days.

**Step 2: Baseline.** For each signal, use the rolling median of days −35 to −7 (the window lag keeps slow worsening from pulling the baseline toward the event) and spread = 1.4826 × MAD ([design from notes, after Gyllensten windows of 20–35 days](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)). Cold start: blend with population priors and the discharge dry weight. HeartLogic does not alert for its first 30–37 days ([PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)); we alert from day 1 for red flags only, and trend alerts start once at least 7 personal readings exist.

**Step 3: Per-signal worsening scores.** Robust z = (7-day mean − baseline median) / spread, signed so that worsening is positive (weight ↑, impedance ↓, HR ↑, breathing ↑, SpO2 ↓, activity proxy ↓). Clip at 0, so an improvement in one signal cannot cancel worsening in another. Add the published trend detectors:

| Detector | Starting parameters | Source performance |
|---|---|---|
| Weight MACD | short 9-day mean − long 20-day mean > **0.62 kg** | 33% sens, 91% spec ([Gyllensten](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)) |
| Weight CUSUM | 10-day window, depreciation c = 0.75, threshold **8.7** | — |
| Impedance CUSUM (log Ω) | 20-day window, c = 0.75, threshold **−7.8** | 60% sens, 96% spec, ~0.48 false/pt-yr (thoracic vest, not feet) |
| Impedance MACD (log Ω) | 9 vs 35 days, < **−0.059** | — |
| Breathing variability | 30-day SD of daily breathing rate > **1.0/min** | HR 12.3 for an event within 30 days ([NOTICE-HF](https://www.link.springer.com/article/10.1007/s10840-015-9983-6)) |
| HR rise | sustained 3-day rise > **5 bpm** above baseline | LifeVest night-HR finding ([Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)) |

**Step 4: Composite index.** S = Σ wᵢ · min(zᵢ, 4) over signal families, plus +2 for each confirmed symptom "yes". Signal families are: fluid (weight, impedance), cardio-respiratory (HR, breathing, SpO2) and symptoms. Start with equal weights; tune on training data.

**Step 5: Alert states with hysteresis and persistence.**
- **Amber** when S ≥ T_high on 1 day. The device asks for a repeat check that evening or the next morning (90-s recording).
- **Red** when S ≥ T_high on **2 of the last 3 days** *and* at least **2 signal families** contribute; or one family stays above threshold for 3 days.
- **Clear** only when S < 0.4 × T_high, mirroring HeartLogic's 16 → 6 ([PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)). No new alert for the same episode until it clears.
- Choose T_high on the training set so that false alerts are ≤ 0.21 per patient-month (2.5 per patient-year).

**Step 6: Immediate red-flag rules** (bypass the baseline; confirm with one repeat reading within minutes):
- SpO2 < 90% (as used in [TwoCan](https://cardio.jmir.org/2024/1/e52648)).
- HR > 110 bpm. Route to the "rhythm/urgent check" message, since high HR was linked to *incorrect* HF alerts.
- HR < 40 bpm (design proposal; not from sources).
- New irregular rhythm.
- "Breathless at rest" confirmed twice.
- SOS press.

**Step 7: Probable-cause tags and explanation.** Each alert gets a tag:

| Tag | Pattern |
|---|---|
| HF-like | Fluid family plus another family, gradual |
| Infection-like | Abrupt HR and breathing rise, weight flat |
| AF-like | Irregularity high, HR step |
| Salty-meal-like | Weight up and reversing |
| After medicine change | Change marker present |
| Dehydration-like | Weight ↓ with HR ↑ |

The explanation names the top 2–3 contributing signals in plain words. Example voice and SMS: "Weight up 1.8 kg in 6 days. Foot water reading up. Breathing faster. Call ASHA." In Indic script, an SMS must fit 70 characters, or 67 per part if split ([Exotel](https://developer.exotel.com/docs/sms-support/unicode-sms)).

### Display and escalation ladder

| Level | Trigger | Patient (device) | Family | ASHA | Doctor |
|---|---|---|---|---|---|
| 0 Green | Normal check-in | Green light + "All fine" | Nothing daily; weekly "device OK + trend" SMS | Weekly summary SMS (optional) | Monthly summary (urban dashboard) |
| 1 Missed | No check-in by ~10:30 | Voice reminder at next button press | SMS at ~11:00; voice call if missed 2 days | SMS after 2 missed days | — |
| 2 Amber | S ≥ T_high once, or one symptom "yes" | Amber light + "check again this evening" | SMS "repeat check asked" (urban: WhatsApp) | — | — |
| 3 Red | Persistent multi-signal alert | Red light + voice explanation + "call ASHA/doctor" | **Automatic voice call in local language** + SMS with reason | SMS with reason + patient name | SMS summary; urban: dashboard plot + eSanjeevani link |
| 4 Urgent | Red-flag rule or SOS | Red flashing + "Call 108 / go to hospital now" | Repeated voice call to 2 contacts | SMS | SMS |
| F Fault | Sensor or battery fault | Voice: "Device needs help" | SMS "device fault" | — | — |

| Feature | Rural home | Urban home |
|---|---|---|
| Network | 4G Cat-1 (A7670C) SMS + voice; 2G SIM800L only on Airtel/Vi/BSNL SIMs | Same modem, or Wi-Fi only (cheaper tier) |
| Main alert channel | Voice call to family + SMS to ASHA | Voice call + WhatsApp/web dashboard for children elsewhere |
| Doctor link | ASHA → Ayushman Arogya Mandir → eSanjeevani | Private cardiologist dashboard; eSanjeevani |
| Power | Battery-first; several cuts a day expected | Battery as backup |
| Language | Pre-recorded local language and dialect voice files | Same, plus optional OLED icons |

Older Indian adults often own a feature phone and share a smartphone with younger family members ([SAGE 2025](https://journals.sagepub.com/doi/10.1177/20501579251378548)), so the family member is the real user of the remote alerts. Collect two family numbers and the ASHA's number at setup.

---

## 7. Cost options: four tiers, and only the lean one is safely under ₹5,000

Prices are single-unit Indian retail snapshots from the notes. "Estimate" means **not verified**; these are team placeholders. Get real quotes before the pitch. Bulk or IndiaMART prices are often 30–50% lower (notes), but that is not used below.

### Parts list (₹)

| # | Part | Low | Conservative | Price status / source |
|---|---|---|---|---|
| 1 | ESP32 classic DevKit (WROOM-32, has DAC) | 450 | 900 | **Not verified.** Only ESP32-S3 boards were priced: 799–1,299 ([Probots](https://probots.co.in/esp32-s3-devkitc-1-development-board-wireless-module-wifi-bluetooth.html), [Amazon.in](https://www.amazon.in/esp32-s3/s?k=esp32-s3)) |
| 2 | 4 × 50 kg load cell + HX711 (bought as 4 single sets) | 544 | 880 | Verified: 136 each ([Robocraze](https://robocraze.com/products/50kg-load-cell-hx711)) to 220 each ([Engineer Store](https://www.theengineerstore.in/products/50kg-load-cell-with-hx711-weight-sensor)) |
| 2a | *Alternative:* 4-cell + HX711 kit | 1,205 | 1,467 | Verified ([Amazon.in](https://www.amazon.in/load-cell-with-hx711/s?k=load+cell+with+hx711)) |
| 2b | *Alternative:* hacked cheap digital bathroom scale (replaces 2 and most of 3) | ? | ? | **Not verified.** Check Amazon.in |
| 3 | Platform board, non-slip mat, low stool, enclosure | 300 | 600 | Estimate |
| 4 | 4 stainless-steel foot plates | 100 | 200 | Estimate |
| 5 | DIY bioimpedance front end (op-amps, instrumentation amp, rectifier, passives, reference resistor) | 150 | 400 | Estimate |
| 6 | MAX30102 finger sensor | 96 | 250 | Weak listing, 96 ([Zbotic snippet](https://zbotic.in/product/ad8232-ecg-monitor-sensor-module/)); upper is an estimate |
| 7 | MAX98357A amp + small speaker | 300 | 350 | Amp 249 verified ([Amazon.in](https://www.amazon.in/esp32-s3-devkit/s?k=esp32+s3+devkit)); speaker estimate |
| 8 | 2 big buttons + SOS button + 3 LEDs | 100 | 200 | Estimate |
| 9 | 2 × 18650 + holder + charger/protection + boost | 300 | 500 | Estimate (not sourced) |
| 10 | Wires, perfboard/PCB, connectors | 150 | 300 | Estimate |
| 11a | SIM800L (2G; no Jio) | 150 | 448 | Verified ([Zbotic](https://zbotic.in/sim800l-vs-a6-mini-gsm-module-low-cost-comparison-for-india/); IndiaMART) |
| 11b | A7670C 4G Cat-1 bare module + antenna/breakout parts | 550 | 1,100 | Module 450–900 verified ([IndiaMART](https://m.indiamart.com/proddetail/simcom-a7670c-chip-module-2856272006788.html)); extras estimate |
| 11c | *Alternative:* A7670C ready TTL board | 1,900 | 1,900 | Verified ([IndiaMART](https://m.indiamart.com/proddetail/wireless-simcom-7670c-4g-lte-gsm-module-with-ttl-output-for-electrical-industry-2856484594655.html)) |
| 12 | AD8232 ECG module | 443 | 528 | Verified (375 + GST, [ElectronicsComp](https://www.electronicscomp.com/ad8232-ecg-monitor-sensor-module-india); 528, [Engineer Store](https://www.theengineerstore.in/products/ad8232-ecg-module)) |
| 13 | Steel handle / rail with 2 hand electrodes | 150 | 250 | Estimate |
| 14 | 1.3" I2C OLED | 179 | 499 | Verified ([Robu](https://robu.in/product-category/oled-display/); Amazon.in) |
| 15 | INMP441 microphone | 100 | 250 | **Not verified** (only in a ~799 OLED + mic + amp combo) |

Core (items 1–10) = **₹2,490 low / ₹4,580 conservative**.

### Tiers

| Tier | What is in it | Low total | Conservative total | Under ₹5,000? | Trade-offs |
|---|---|---|---|---|---|
| **A. Lean rural (2G)** | Core + SIM800L | **₹2,640** | **₹5,028** | Yes at low prices; ~₹30 over at conservative | No ECG, so no AF check and HR comes from PPG only. SIM800L does not work with Jio SIMs, and 2G has long-term risk ([Light Reading](https://www.lightreading.com/business-management/jio-s-dream-of-a-2g-free-india-is-a-nightmare-for-telcos)), though Airtel says it will keep 2G ([91mobiles](https://www.91mobiles.com/hub/?p=291528)) |
| **B. Recommended (4G + ECG handle)** | Core + A7670C bare + AD8232 + handle | **₹3,633** | **₹6,458** | Only at low-to-mid prices | Works on all networks; AF/rhythm path. **Needs the cost-down levers below** |
| **C. Full demo** | Tier B + OLED + mic | **₹3,912** | **₹7,207** | Only at low prices | Icons for urban users; voice biomarker data. Use this for the hackathon demo, but price the pitch BOM as Tier B |
| **D. Urban Wi-Fi** | Core + AD8232 + handle + mic, no modem | **₹3,183** | **₹5,608** | Yes at low-to-mid prices | No SMS or call without home Wi-Fi; not for rural homes |

**Cost-down levers to bring Tier B under ₹5,000** (mostly unverified; check each):
- Use a hacked bathroom scale instead of separate load cells and a platform. This could save several hundred rupees if the scale costs less than about ₹900; price not verified.
- Buy the bare A7670C at the lower IndiaMART price and design your own carrier board, instead of the ₹1,900 TTL board.
- Use one 18650 cell instead of two. The device sleeps except for about 2 minutes a day, but size the cell for modem peak current.
- Drop the OLED. Voice and three LEDs are enough.
- Put a bare ESP32-WROOM module on your own PCB instead of a DevKit.
- Note in the pitch that volume pricing is often 30–50% lower.

A sensible pitch line: **"Tier B parts: ₹3,600 at the listed prices we sourced, ₹5,000 target ceiling, with every price linked."**

### Alternative architectures compared

| Architecture | Effort | PS fit | Edge-case fit | Cost | Verdict |
|---|---|---|---|---|---|
| **Check-in station (this report)** | ~90 s/day | All six targets (lungs and activity by proxy) | Good: identity gate; no bed interference; fixed posture | ₹2,600–6,500 | **Adopt** |
| Wrist band + bedside dock + SMS | Wear all day, charge daily | HR, activity, sleep HR; no weight or impedance | Weak: full wear compliance ~50%; PPG motion artefact; daytime gaps ([Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)) | Similar parts cost; band enclosure is hard | Use only as the optional pendant |
| Bed or cot sensor (load cells or piezo) | Zero | Night HR, breathing, restlessness | Poor: shared beds, charpais, floor mats, blankets, sleeping in a chair when orthopneic; no HF sensitivity data | Similar parts; Dozee home ~$345 + monthly (US) | Reject (the team already rejected it) |
| Adhesive patch | Continuous | Best published numbers (LINK-HF) | Skin, battery, replacement; PS says "may not be ideal" | High | Reject |
| Smartphone voice app only | 30 s/day | Lungs (proxy) only | Many rural elders do not own or cannot use smartphones ([PMC7740952](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7740952/)) | Software | Fold into the station in shadow mode |

---

## 8. PS and judging checklist: every requirement has an owner

| Requirement | How the design meets it | Status / risk |
|---|---|---|
| Effortless capture (< 2 min/day; no all-day patch) | One 90-s seated check-in; no wearable needed | Meets. Amber days add one repeat check |
| Real home use: little reading, local language | Voice prompts, 3 lights, 2 coloured buttons; no text needed | Meets. Record voice files with native speakers |
| Power cuts | Battery-first, deep sleep, flash log, store-and-forward | Meets. Size the battery for modem peaks |
| Weak internet | On-device engine; SMS and voice call need no data | Meets. Verify modem voice support |
| Home unit parts < ₹5,000 | Tier A ₹2,640–5,028; Tier B ₹3,633–6,458 | **Risk:** Tier B needs low prices and verified estimates |
| Weight gain | Load cells, MACD/CUSUM | Meets |
| Faster resting HR | Handle ECG + PPG, seated rest | Meets (morning seated HR, not night HR) |
| Faster breathing | ECG/PPG-derived breathing rate | Partial: a 60-s spot estimate is noisy; use 7-day trends |
| Less activity | Missed check-ins, adaptive question, sit-to-stand (shadow), optional pendant | **Partial:** weak proxies unless the pendant is used |
| Fluid in lungs or legs | Legs: foot impedance. Lungs: SpO2, breathing, symptoms, voice (shadow) | Legs meets; lungs by proxy only |
| Trouble breathing lying flat | Change-based orthopnea question; optional pendant trunk angle | Meets (self-report) |
| "One signal is rarely enough" | Red needs ≥ 2 signal families or persistence | Meets |
| User journey | Section 6 table | Meets |
| Block diagram + schematic of ≥ 1 custom part with sensor circuit + MCU | Tetrapolar BIA front end + ESP32 (also AD8232 + HX711) | To build in KiCad/EasyEDA |
| Parts list in ₹ | Section 7, with links | Replace estimates with quotes |
| Simulation proof (free tool) | LTspice: current source + body model + contact-resistance sweep (wet vs dry feet). Wokwi: ESP32 check-in state machine (check part availability). Python: NeuroKit2 signal pipeline | To build |
| Raw signals → alert | Quality gates → features → baseline → scores → composite → states | To build |
| Learns a personal baseline | Rolling median/MAD with lag; cold-start prior | Meets by design |
| Explains why each alert fired | Top contributing signals + probable-cause tag in voice and SMS | Meets by design |
| Simple screen for patient / family / doctor | Lights + voice; SMS/voice call; web dashboard with trend plots | Build a minimal dashboard |
| Validation: ≥ 20 virtual patients × 30 days; worsening 3–10 days before visit; sensitivity, specificity, median lead time, false alerts per patient-month; patient-level split | Section 9 | To run |
| BIDMC CHF ECG for HR code | HR + irregularity pipeline tested on BIDMC CHF records | To run |
| Public GitHub, 2-page report, 5-min pitch | Repo with firmware, LTspice files, simulator, notebook | To do |
| "Monitoring, not diagnosis" disclaimer | On device voice at setup, SMS footer, dashboard, report | Meets |
| **Judging: creativity of sensing (20)** | Closed-loop seated station; DIY tetrapolar BIA; bendopnea-in-routine; sit-to-stand and voice shadow features | Strong |
| **Ease and long-term use (20)** | 90 s, voice-guided, guest mode, family loop, "silence is never green" | Strong; adherence unproven |
| **Software and analytics (20)** | Explainable fusion engine with cited parameters, confounder tags, ablations | Strong |
| **Hardware and simulation (15)** | Custom BIA circuit with LTspice proof; Wokwi firmware | Medium–strong; bench accuracy unknown |
| **Scientific basis and honest testing (15)** | Benchmarks against published weight rules; patient-level split; honest caveats | Strong if you report failures too |
| **Cost / India fit / pitch (10)** | ₹ BOM with links, 4G/2G choice, ASHA/eSanjeevani path | Medium: tight budget |

---

## 9. Validation plan: beat the weight rule on held-out patients

### Synthetic cohort design

No public generator of HF decompensation trajectories exists, so build a parametric simulator. Use daily aggregates for the alert engine. Use waveforms only to demonstrate the signal-processing pipeline.

**Size:** at least 200 virtual patients (well above the PS minimum of 20), each with a **30-day warm-up history plus a 30-day test window**. Also report a strict "30 days only, cold start" run, so judges see both. About 40–50% of patients get one HF event in the test window. This enrichment is needed because real event rates of about 0.2–0.5 per patient-year ([PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)) would give almost no events in 30 days. Report false alerts from both event-free and event patients.

| Parameter | Value | Basis |
|---|---|---|
| Baseline weight | 40–100 kg (Indian patients; younger RHD patients are often lighter women); day-to-day SD 0.3–0.5 kg | Assumption |
| Resting HR | 60–80 bpm, SD ~2 | Assumption |
| Breathing rate | 14–18/min, SD 0.5–1.0 | NOTICE-HF ([Springer](https://www.link.springer.com/article/10.1007/s10840-015-9983-6)) |
| Foot impedance | Per-patient baseline; day noise ~2–3% | Assumption |
| SpO2 | 94–98% | Assumption |
| Missing days | 5–15% random, plus some 2–3-day gaps | Notes |
| **Worsening episode** | Onset **3–10 days before the visit** (per PS), accelerating near the end. Weight +1–4.5 kg; breathing +1.5–2.1/min; HR +3–8 bpm; impedance −5–15%; activity proxy −15–30%; symptom "yes" probability rises in the last 2–4 days | Weight bands: [Chaudhry](https://pmc.ncbi.nlm.nih.gov/articles/PMC2892745); breathing: [NOTICE-HF](https://www.link.springer.com/article/10.1007/s10840-015-9983-6); HR, impedance, activity magnitudes are assumptions |
| **Weight-silent episodes** | 30–40% of episodes with < 0.5 kg gain | Reflects FAST and Gyllensten ([PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)) |
| Infection | Abrupt; HR +10–20, breathing +3–5, weight flat; 3–7 days | Assumption; pattern from Gardner |
| AF | HR step +15–30 with irregular beats | Assumption |
| Salty meal | Weight +0.5–1.5 kg, gone in 2 days | Assumption |
| Diuretic change | Weight −1–2 kg step, with a marker | Assumption |
| Measurement faults | Guest user (other weight band), shoes (no impedance), wet feet (contact change), heavy clothes (+1 kg), single-day spikes | Assumption |

**Waveform layer:** Generate ECG, PPG and respiration with NeuroKit2 (`ecg_simulate`, `ppg_simulate`, `rsp_simulate`; [docs](https://neuropsychology.github.io/NeuroKit/functions/ecg.html)). Add motion and noise, and show that the quality gate rejects bad segments. Check `ppg_simulate` defaults with `inspect.signature`, because the docs conflict. **Real data:** run the HR and irregularity code on the PhysioNet BIDMC CHF database (long ECG recordings from people with severe CHF; check record details on PhysioNet) and report HR error against the database's beat annotations.

### Metrics (report all together, so no single one can be gamed)

| Metric | Definition |
|---|---|
| Sensitivity (per event) | Event counted as detected if a red alert starts between worsening onset and the visit day (also report with a 14-day window) |
| Specificity | Share of non-event patient-days (or 7-day windows) without an active red alert |
| Median lead time (IQR) | Visit day minus first red-alert day. Note the cap: with 3–10-day onsets, lead time can never exceed 10 days |
| False alerts per patient per month | Red alert episodes not overlapping an event window, divided by patient-months. Also convert to per patient-year to compare with the literature |
| Time in alert, PPV | As in MultiSENSE ([PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441)) |
| Amber burden | Repeat checks requested per patient-month (an effort cost) |

**Split:** patient-level only. Use 70/30 train/test with GroupKFold (5-fold) on the training part for tuning. Gyllensten used 8-fold leave-patient-out ([PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/)). Tune all thresholds on training patients, then run the test set **once**. Give 95% confidence intervals by bootstrapping over patients.

**Baselines and targets:**

| System | Sensitivity | False alerts / patient-month | Source |
|---|---|---|---|
| Weight rule (> 1.4 kg in 1 day or > 2.3 kg in 7 days) | ~35% | ~0.34 | SCALE-HF comparator ([TCTMD](https://www.tctmd.com/news/smart-scale-better-predicting-hf-events-weight-based-monitoring)) |
| Weight rule (FAST) | 23% | 0.36 | [MDedge](https://mdedge.com/content/impedance-beats-weight-predicting-hf-events) |
| Weight + foot impedance (Bodyport) | 70% | 0.22 | [TCTMD](https://www.tctmd.com/news/smart-scale-better-predicting-hf-events-weight-based-monitoring) |
| HeartLogic (implant ceiling) | 70% | 0.12 | [PSU Pure](https://pure.psu.edu/en/publications/a-multisensor-algorithm-predicts-heartfailure-events-in-patients-/) |
| **Our target** | **> 35%, aim ≥ 60%** | **≤ 0.21** | Target from notes |
| **Lead-time target** | median ≥ 4–5 days (≥ 7 impossible for late-onset episodes) | — | — |

Implement the two weight rules in the same code and run them on the same test patients. **Ablations** to report: weight only → + impedance → + HR/breathing/SpO2 → + symptoms → + two-step confirmation → + identity gate. **Stress tests:** 30% missing days, 20% guest readings, wet-feet artefacts, AF and infection episodes, and the cold-start run.

**Honesty rule:** synthetic results only show that the engine finds the patterns you put in. They do not prove clinical accuracy. Say this on the results slide.

---

## 10. Limits, risks and the regulatory path

### Honest caveats

- **The core evidence is thin.** Foot impedance on a scale has one observational, company-linked study (SCALE-HF 1). Its 14-day lead time is a press figure, and the index is proprietary. Our DIY circuit is a different, unvalidated measurement.
- **Most parameters are borrowed from implants or vests** (HeartLogic, Gyllensten's thoracic vest). They are starting points, not proof that the same numbers fit foot impedance or seated morning HR.
- **Spot measurements are weaker than overnight ones.** A 60-s breathing rate cannot reliably see a 1.5–2/min change on a single day; only multi-day trends can. Night HR, used in the literature, is not what we measure.
- **Lungs and activity are covered only by proxies** unless the optional pendant is used.
- **Voice features are company-validated only**, in mostly Israeli cohorts, with no language-stratified results ([TCTMD](https://www.tctmd.com/news/voice-analysis-picks-patients-risk-hf-hospitalization-community-hf)). The pivotal DETECT-HF results were not found.
- **Adherence in India is unknown.** HearO's 83.5% came from stable volunteers. Tele-HF and BEAT-HF fell to 55%.
- **The response loop is outside our control.** Benefit needs someone who can change medicines. Only ~25% of Indian HFrEF patients get full guideline therapy at discharge ([PMC10424635](https://pmc.ncbi.nlm.nih.gov/articles/PMC10424635)), and HF is not yet an ASHA programme condition.
- **Safety unknowns:** injected current with pacemakers/ICDs (not researched; provide an impedance-off mode), electrical safety (measure on battery only), fall risk, and false reassurance from green lights.
- **It cannot predict sudden death** (LINK-HF predicted none of 12 deaths).
- **Budget:** Tier B is above ₹5,000 at conservative prices, and about a third of the BOM is unverified estimates.
- **Telecom:** 2G longevity is uncertain. A2P SMS at scale needs TRAI DLT template registration ([WebEngage](https://docs.webengage.com/docs/trai-sms-dlt-regulations-india)). Modem voice-call support depends on the variant.

### Regulatory note (CDSCO) and startup path

India regulates devices under the **Medical Devices Rules 2017**, with risk classes A–D. Class A/B manufacturing licences (MD-3/MD-5) come from the state authority and Class C/D licences (MD-7/MD-9) from the central authority ([Corpseed](https://corpseed.com/knowledge-centre/classification-of-medical-devices-by-cdsco-in-india)). CDSCO issued a **draft Guidance on Medical Device Software on 21 Oct 2025**, separating standalone software (SaMD) from embedded software (SiMD) ([India Briefing](https://india-briefing.com/news/cdsco-draft-guidance-medical-software-40691.html)). We found no evidence that it has been finalised. Consultancy sources disagree on monitor classes (B vs C vs D) ([Operon Strategist](https://operonstrategist.com/examples-of-medical-device-classifications/)). A home HF early-warning device is most likely **Class B, or Class C if it makes alarm or diagnostic claims**. Confirm with official notifications.

A realistic startup path has four steps:
1. Sell or pilot as a weighing scale with reminders and family notification, with no diagnostic claim.
2. Run a district pilot with a cardiology department and ASHAs through NHM, linked to eSanjeevani. Collect real data to validate the algorithm, starting with a "shadow" period in which alerts go only to the study team.
3. Build ISO 13485 quality systems and test to IEC 60601-1, -1-2 and -1-11 (home use). MTCTE/BIS rules for the 4G module were not researched.
4. Apply for the licence once claims of "early warning" are backed by a clinical performance study.

---

## Conclusion

The research changes the question from "which sensor detects heart failure?" to "which daily habit survives for months and produces alerts that someone acts on?" Weight was the default for twenty years and catches only a quarter to a third of events. The systems that do better either fuse several signals or ask so little of the patient that they keep using it. A seated, voice-guided check-in that measures several signals at once, refuses to count bad or borrowed readings, and escalates through family and ASHA workers is the one design that serves both needs within an Indian home budget. That makes it the right bet for this hackathon, but it is still a hypothesis.

The team's strongest competitive move is honesty in testing, not more sensors. Few published home systems report false alerts consistently, and none handle shared use, wet feet or weight-silent episodes explicitly. A project that adopts the HeartLogic and Gyllensten logic, models these confounders in an open simulator, shows on held-out virtual patients that it beats the weight rule, and states clearly where its proxies are weak (lungs, activity, voice) will stand out on the 35 points for software and science. It also lays the groundwork for the real-patient pilot that no amount of synthetic data can replace.

---

## 11. Sources

**Home sensing, scales, wearables, bed sensors**
- FAST trial (weight vs impedance): [MDedge](https://mdedge.com/content/impedance-beats-weight-predicting-hf-events); [Cardiac Rhythm News](https://cardiacrhythmnews.com/?p=4954)
- Chaudhry 2007, weight before admission: [PMC2892745](https://pmc.ncbi.nlm.nih.gov/articles/PMC2892745)
- SCALE-HF 1 (Bodyport): [TCTMD](https://www.tctmd.com/news/smart-scale-better-predicting-hf-events-weight-based-monitoring); [Healio](https://www.healio.com/news/cardiology/20240313/scale-using-biosensor-technology-detects-hf-events-more-often-than-standard-of-care); [CLP Mag press](https://clpmag.com/disease-states/cardiovascular/heart-failure-monitoring-tech-doubles-sensitivity-for-predicting-events-versus-standard-of-care/)
- Inan BCG scale: [Georgia Tech ECE](https://ece.gatech.edu/news/2023/12/bathroom-scale-could-monitor-millions-heart-failure)
- EarlySense: [PMC5221726](https://pmc.ncbi.nlm.nih.gov/articles/PMC5221726); NICE MIB49: [NICE](https://www.nice.org.uk/advice/MIB49/chapter/Summary)
- Emfit protocol: [DOAJ](https://doaj.org/article/8e0dc6e287b7424b9082e7713beeaf3b); Sleepiz: [AASM](https://aasm.org/sleepiz-one-bedside-monitoring-device-receives-fda-clearance/)
- LINK-HF: [TCTMD](https://www.tctmd.com/news/stick-sensor-predicts-heart-failure-hospitalizations-pilot-study); BMAD: [TCTMD](https://www.tctmd.com/news/wearable-device-helps-hf-patients-avoid-coming-back-hospital-bmad)
- 2025 narrative review (MUSIC, LifeVest, wearables, ReDS, bioimpedance): [PMC12565691](https://pmc.ncbi.nlm.nih.gov/articles/PMC12565691/)
- ReDS: [PMC8745965](https://pmc.ncbi.nlm.nih.gov/articles/PMC8745965/); [Region H](https://research.regionh.dk/en/publications/remote-dielectric-sensing-to-detect-acute-heart-failure-in-patien/); SMILE-HF [Medthority](https://www.medthority.com/news/2019/10/smile-hf-trial-of-reds-shows-reduction-in-readmission-for-heart-failure---medicure/)
- Apple Watch HF study: [ClinicalTrials.gov NCT06819618](https://clinicaltrials.gov/study/NCT06819618)

**Implant benchmarks and alert algorithms**
- HeartLogic MultiSENSE: [PSU Pure](https://pure.psu.edu/en/publications/a-multisensor-algorithm-predicts-heartfailure-events-in-patients-/); cohort and hysteresis: [PMC6437441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6437441); MANAGE-HF: [Duke Scholars](https://scholars.duke.edu/publication/1519187); real-world: [Boston Scientific newsletter](https://www.bostonscientific.com/en-EU/medical-specialties/electrophysiology/clinical-evidence-newsletter/2023/3.html); Bertini AF/CKD: [HRJ 2022 proof](https://ricerca.uniba.it/retrieve/4a283bc7-cf07-4baf-952e-18de9d9fa29e/Bertini_HRJ2022_Proof.pdf)
- TriageHF: [NICE MIB298](https://www.nice.org.uk/advice/mib298/chapter/Clinical-and-technical-evidence); SELENE HF: [ESC365](https://esc365.escardio.org/journal/53445)
- CardioMEMS: [ACC CHAMPION](https://www.acc.org/Latest-in-Cardiology/Clinical-Trials/2015/12/29/12/44/CHAMPION); [ACC GUIDE-HF](https://www.acc.org/Latest-in-Cardiology/Clinical-Trials/2021/08/25/23/01/GUIDE-HF)
- Gyllensten 2016 algorithms: [PMC4777885](https://pmc.ncbi.nlm.nih.gov/articles/PMC4777885/); simulated case management: [PMC5240411](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5240411/)
- NOTICE-HF breathing rate: [Springer](https://www.link.springer.com/article/10.1007/s10840-015-9983-6); MultiSENSE breathing: [Healio](https://cm.healio.com/news/cardiology/20141002/hf-events-preceded-by-worsening-rapid-shallow-breathing)
- Infection pattern (Gardner 2021, sponsor): [PDF](https://www.bostonscientific.com/content/dam/bostonscientific/ep/portfolio-group/heartlogic-heart-failure-diagnostic/heartlogic-newsletter/issue-7-2021/Gardner_ESC-HF_2021.pdf)
- Rural 5 lb weight gain: [Flinders](https://researchnow.flinders.edu.au/en/publications/rapid-5lb-weight-gain-is-not-associated-with-readmission-in-patie/)
- User identification: [Fitbit Aria FDA K133872](https://fda.innolitics.com/device/K133872); [EPO EP4137045](https://data.epo.org/publication-server/rest/v1.2/patents/EP4137045NWA1/document.html); ECG biometrics field study: [arXiv 2003.03273](https://ar5iv.labs.arxiv.org/html/2003.03273)
- TRACER: [arXiv 2609.29742](https://arxiv.org/abs/2609.29742); NeuroKit2: [ECG docs](https://neuropsychology.github.io/NeuroKit/functions/ecg.html), [PPG docs](https://neuropsychology.github.io/NeuroKit/functions/ppg.html)

**Voice, symptoms, telemonitoring trials**
- Cordio HearO: [TCTMD COMMUNITY-HF](https://www.tctmd.com/news/voice-analysis-picks-patients-risk-hf-hospitalization-community-hf); [MDedge 2022](https://mdedge.com/ecardiologynews/article/254876/heart-failure/voice-analysis-app-promising-early-warning-system-heart); [MDedge 2023](https://mdedge.com/content/smartphone-app-detects-voice-quality-changes-indicating-worsening-heart-failure); [TCTMD JACC HF 2022](https://www.tctmd.com/news/smartphone-app-hears-speech-changes-indicating-fluid-buildup-hf); DETECT-HF: [CenterWatch](https://www.centerwatch.com/clinical-trials/listings/NCT06378632/an-international-observational-blinded-study-to-assess-the-performance-of-the-cordio-hearo-system)
- Roth score: [PMC6490799](https://pmc.ncbi.nlm.nih.gov/articles/PMC6490799); [CEBM](https://cebm.net/?p=15546)
- Camera PPG for AF: [PMC7125433](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7125433/); [Heart 2022](https://heart.bmj.com/content/108/20/1600); edema imaging: [GlobalSpec](https://insights.globalspec.com/article/22237/), [UCLan](https://clok.uclan.ac.uk/43736)
- Bendopnea: [Frontiers 2025](https://www.frontiersin.org/articles/10.3389/fcvm.2025.1659830/full); pillow count: [UMaryland blog](https://blogs.pharmacy.umaryland.edu/atrium/?p=424); TwoCan alerts: [JMIR Cardio 2024](https://cardio.jmir.org/2024/1/e52648)
- TIM-HF2: [The Hospitalist](https://blogs.the-hospitalist.org/content/home-telemonitoring-heart-failure-cuts-mortality); [ESC365](https://esc365.escardio.org/journal/53058); TIM-HF adherence: [Thieme](https://thieme-connect.de/products/ejournals/abstract/10.1055/s-0034-1369849)
- Tele-HF: [NEJM CardioExchange](https://blogs.nejm.org/cardioexchange/wp-json/wp/v2/posts/4565); BEAT-HF: [PMC4827701](https://pmc.ncbi.nlm.nih.gov/articles/PMC4827701); TEN-HMS: [ACC](https://www.acc.org/Latest-in-Cardiology/Clinical-Trials/2013/05/30/16/25/TENHMS); OSICAT and context: [Frontiers 2022](https://www.frontiersin.org/journals/cardiovascular-medicine/articles/10.3389/fcvm.2022.943778/pdf)

**India context, parts, regulation**
- NHFR: [Nat Commun 2025 listing](https://ideas.repec.org/a/nat/natcom/v16y2025i1d10.1038_s41467-024-55362-z.html); THFR: [PMC10424635](https://pmc.ncbi.nlm.nih.gov/articles/PMC10424635)
- Dozee: [Prime VP](https://www.primevp.in/news-and-announcement/dozee-raises-inr-44-croreusd-6-million-series-set-transform-critical-care-infrastructure-across-india-through-contactless-remote-patient-monitoring-platform); [FitGap pricing](https://us.fitgap.com/products/034460/dozee)
- eSanjeevani: [NewsOnAir](https://newsonair.gov.in/esanjeevani-achieves-milestone-of-50-cr-teleconsultations-from-across-the-country/); ASHA NCD role: [NHSRC](https://nhsrcindia.org/sites/default/files/IRHSS_%20A%20Training%2C%20Process%2C%20and%20Impact%20Evaluation%20of%20Utilizing%20ASHAs%20for%20NCD%20Screening.pdf)
- Kilkari: [NCT03576157](https://clinicaltrials.gov/study/NCT03576157); [ARMMAN deck](https://armman.org/wp-content/uploads/2025/03/Q3_24-25_Impact-Deck.pdf)
- SMS rules: [Exotel](https://developer.exotel.com/docs/sms-support/unicode-sms); [WebEngage DLT](https://docs.webengage.com/docs/trai-sms-dlt-regulations-india)
- 2G/4G: [91mobiles](https://www.91mobiles.com/hub/?p=291528); [Light Reading](https://www.lightreading.com/business-management/jio-s-dream-of-a-2g-free-india-is-a-nightmare-for-telcos); [Zbotic vendor claim](https://zbotic.in/sim800l-vs-a6-mini-gsm-module-low-cost-comparison-for-india/)
- Older adults and phones: [PMC7740952](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7740952/); [Geriatrics 2022](https://doaj.org/article/84c3b157657d43428b43f94bc238b9f1); [SAGE 2025](https://journals.sagepub.com/doi/10.1177/20501579251378548)
- Power supply: [Rajya Sabha PQ](https://rsdebate.nic.in/bitstream/123456789/758173/1/PQ_267_03022025_U153_p494_p495.pdf); [Prayas](https://energy.prayaspune.org/images/pdf/100-rural-electrification-is-not-enough.pdf); [Brookings](https://www.brookings.edu/electrified-but-without-electricity)
- Component prices: [Probots ESP32-S3](https://probots.co.in/esp32-s3-devkitc-1-development-board-wireless-module-wifi-bluetooth.html); [Robocraze load cell](https://robocraze.com/products/50kg-load-cell-hx711); [Engineer Store load cell](https://www.theengineerstore.in/products/50kg-load-cell-with-hx711-weight-sensor); [Amazon.in load-cell kits](https://www.amazon.in/load-cell-with-hx711/s?k=load+cell+with+hx711); [ElectronicsComp AD8232](https://www.electronicscomp.com/ad8232-ecg-monitor-sensor-module-india); [Engineer Store AD8232](https://www.theengineerstore.in/products/ad8232-ecg-module); [IndiaMART A7670C](https://m.indiamart.com/proddetail/simcom-a7670c-chip-module-2856272006788.html); [IndiaMART A7670C board](https://m.indiamart.com/proddetail/wireless-simcom-7670c-4g-lte-gsm-module-with-ttl-output-for-electrical-industry-2856484594655.html); [Robu OLED](https://robu.in/product-category/oled-display/); [Analog Devices AD5933](https://www.analog.com/en/products/ad5933/sample-buy.html); [AliExpress AD5933 module](https://www.aliexpress.com/w/wholesale-ad5933.html)
- CDSCO: [India Briefing](https://india-briefing.com/news/cdsco-draft-guidance-medical-software-40691.html); [Corpseed](https://corpseed.com/knowledge-centre/classification-of-medical-devices-by-cdsco-in-india); [Operon Strategist](https://operonstrategist.com/examples-of-medical-device-classifications/); [Cyril Amarchand](https://corporate.cyrilamarchandblogs.com/2026/01/medical-device-as-software-has-cdsco-guidance-changed-the-rules/)

*This system is for monitoring, not diagnosis. It does not replace a doctor or emergency care.*
