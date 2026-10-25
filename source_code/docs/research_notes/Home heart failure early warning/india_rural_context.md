# Indian / Rural Low-Resource Context for a Sub-INR 5,000 Home Heart-Failure Early-Warning Device

Research date: 2026-10-24. Method: ~21 web searches/fetches. Robu.in blocked automated fetch (HTTP 403), so Robu prices are only from search snippets; other Indian retailers used instead. All retail prices are snapshots and change often; GST (18%) inclusion is noted where known.

## 1. Indian HF burden and outcomes (prevalence, readmission, rural vs urban; THFR, NHFR)

### Takeaway
Indian HF patients are about 10 years younger than Western patients (mean age ~60). About 1 in 4 (NHFR) to 1 in 3 (Trivandrum) die within a year of a hospital admission, and ~30% are readmitted within a year. Only ~25% get guideline-directed therapy, and outcomes are worse with less education. There is no robust community prevalence figure; estimates range from 1.3–4.6 million to 8–10 million people.

### Cited Findings
- **National Heart Failure Registry (NHFR, ICMR-supported), Nature Communications, Jan 2025:** one-year outcomes for 10,850 HF patients, mean age 59.9, 31% women, from 53 hospitals in 24 states and 2 UTs. — [IDEAS/RePEc listing of Nat Commun 2025, doi 10.1038/s41467-024-55362-z](https://ideas.repec.org/a/nat/natcom/v16y2025i1d10.1038_s41467-024-55362-z.html); [DOAJ](https://doaj.org/article/fdea43adebdb4558ad5196ac27bbee25)
- NHFR: about 1 in 4 HF patients in India die within one year. Mortality varied by cause and was highest for rheumatic heart disease (~27.5%). News coverage says Indian HF patients die about 10 years earlier than Western patients. — [Science Chronicle summary](https://sciencechronicle.in/2025/05/07/heart-failure-patients-in-india-die-10-years-earlier/) (secondary news source)
- The NHFR protocol collected in-hospital, 3-, 6- and 12-month mortality and rehospitalisation. — [PMC7136335 (NHFR design paper)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7136335)
- **Trivandrum Heart Failure Registry (THFR, Kerala; enrolment 2013; Am Heart J 2017):**
  - Cohort: n = 1,205, mean age 61.2. Ischaemic heart disease ~72%, dilated cardiomyopathy ~13%, rheumatic heart disease ~8% (11.6% in women), HFpEF 25.8%.
  - Mortality: 1-year all-cause 30.8%, with 18.1% dying in the first 3 months. 61% of deaths were in people under 70.
  - Readmission: 30.2% readmitted within 1 year (24.3% for worsening HF; 5.8% more than once).
  - Treatment: GDMT at discharge for only 24.6% of HFrEF patients, and lower in less-educated patients.
  - Education: graduates had a mortality HR of 0.52 vs no formal education. 18.2% of women and 9.0% of men had no formal education.
  - Source: [PMC10424635](https://pmc.ncbi.nlm.nih.gov/articles/PMC10424635)
- **Prevalence:** Huffman and Prabhakaran (2010) estimated 1.3–4.6 million HF cases, with annual incidence ~0.49–1.8 million. This is a projection from 2000-era data and Western mortality data. — [NMJI review PDF](https://nmji.in/nmji/archives/Volume-23/Issue-5/Review-Article.pdf). **OUTDATED (2010).**
- **INDUS rural North-India community survey:** measured prevalence was only 1.2 per 1,000, but the authors project ~1% of the population (8–10 million). Commentators call the measured figure a gross underestimate caused by poor case-finding. — [INDUS study](https://repository.ias.ac.in/114560); [PMC6097178](https://pmc.ncbi.nlm.nih.gov/articles/PMC6097178)
- No robust Indian HF incidence or prevalence data exists. — [PMC3913650](https://pmc.ncbi.nlm.nih.gov/articles/PMC3913650/)

### Inferences
- The highest-risk window is the first ~90 days after discharge (18% died in that period in THFR). A device sold or given at discharge targets exactly this window.
- Patients are younger (~60), and many are still working or are household heads. The "elderly" framing should include 50–70-year-olds, often with low formal education, especially women.
- Rheumatic heart disease is a bigger cause in India than in the West, and its patients are younger and often female. This affects body weight ranges and literacy assumptions.
- Low education is linked both to lower GDMT use and to higher mortality. Voice- and colour-based UX is therefore a clinical need, not just a nicety.

### Gaps
- I did not retrieve NHFR readmission rates or rural-vs-urban outcome splits from the full text. Check doi 10.1038/s41467-024-55362-z.
- I found no Indian study that directly compares rural and urban HF access or outcomes.
- The ijmr.org.in NHFR age-group analysis (2025) was found but not read: [IJMR](https://ijmr.org.in/clinical-characteristics-treatment-patterns-outcomes-of-heart-failure-a-comparative-analysis-across-age-groups-from-the-heart-failure-registry-in-india/).

## 2. Existing Indian solutions and government programmes

### Takeaway
Dozee is the main Indian contactless (under-mattress) monitor. It is mostly sold to hospitals, with a US-priced home plan (~$345 plus $25–50/month). No Indian player offers a sub-INR 5,000 home HF weight/vitals alert device. The public system now has large rails a device could plug into: eSanjeevani (50 crore consultations, ~1.42 lakh Ayushman Arogya Mandir spokes), ASHA-led CBAC NCD screening, and follow-up of hypertension and diabetes patients. However, HF is not an explicit target in the NCD programme materials found.

### Cited Findings
**Dozee (Turtle Shell Technologies, Bengaluru)**
- Contactless ballistocardiography sensor placed under the mattress. Claimed deployments:
  - 2021: >5,000 hospital beds.
  - Later: 380+ hospitals in 50+ districts.
  - Has US FDA 510(k) clearance.
  - Source: [Prime VP release](https://www.primevp.in/news-and-announcement/dozee-raises-inr-44-croreusd-6-million-series-set-transform-critical-care-infrastructure-across-india-through-contactless-remote-patient-monitoring-platform)
- Connected-bed product built with Midmark India. — [MobiHealthNews](https://www.mobihealthnews.com/news/asia/indian-medical-device-maker-dozee-launches-smart-connected-bed-midmark-india)
- Dozee says ~95% of India's ~2 million hospital beds and 125,000 ICU beds are poorly monitored. — [MobiHealthNews](https://www.mobihealthnews.com/news/asia/indian-medical-device-maker-dozee-launches-smart-connected-bed-midmark-india)
- **Home pricing (US, pre-order late 2024):**
  - "Home ONE with Connect": $345 one-time (introductory, down from $425) plus $25/month.
  - "Home ONE with Telehealth": $345 plus $50/month, adding a 24x7 care coach.
  - Source: [FitGap listing citing Dozee page](https://us.fitgap.com/products/034460/dozee). This is a third-party aggregator and may be outdated. No Indian home price was found.
- **Funding and markets:** raised ~$8.3M in March 2025 for global expansion. US commercial operations began Q1 FY26, and revenue is reportedly ~50/50 India and US. — [Techleap](https://finder.techleap.nl/news/feed/dozee-raises-8m-for-global-expansion); [MobiHealthNews](https://cloudgate.mobihealthnews.com/news/asia/indian-rpm-startup-dozee-gets-6m-kickstart-global-expansion)

**Tricog (Bengaluru)**
- AI-assisted ECG interpretation service.
- Raised $8.5M Series B2 from Omron Healthcare and Sony Innovation Fund, for ~$30M total.
- Awaiting USFDA approval for its DeepRhythm real-time monitoring platform.
- Sources: [MedTech Innovator](https://medtechinnovator.org/tricog-raises-8-5-million-in-series-b2-funding/); [Indian Pharma Post](https://www.indianpharmapost.com/news/lite/tricog-raises-us-85-million-in-series-b2-funding-14042)

**Cardiotrack (Bengaluru, founded 2014)**
- Portable Bluetooth 12-lead ECG unit and cardiac risk assessment. No price found. — [GlobalLinker](https://www.globallinker.com/brand/tricog)

**eSanjeevani**
- 50,00,92,730 consultations as of 15 Sep 2026.
- Network: >1.42 lakh Ayushman Arogya Mandir spokes, 19,473 hubs, 901 online OPDs, 2,41,923 registered providers.
- Volume: ~2.5–3 lakh consultations per day.
- Source: [NewsOnAir](https://newsonair.gov.in/esanjeevani-achieves-milestone-of-50-cr-teleconsultations-from-across-the-country/); [Digital Health News](https://www.digitalhealthnews.com/esanjeevani-crosses-50-crore-teleconsultations-expands-into-specialist-care)
- Early 2025 figures: 34 crore consultations, operational at 1,31,133 Ayushman Arogya Mandirs. — [Rajya Sabha PQ, Feb 2025](https://rsdebate.nic.in/bitstream/123456789/758635/1/PQ_267_11022025_S79_p34_p42.pdf)

**ASHA workers, CBAC and NP-NCD**
- ASHAs fill the Community Based Assessment Checklist (CBAC) to flag high-risk people for ANM screening.
- They also follow up people diagnosed with hypertension or diabetes for medication adherence and lifestyle change.
- A government smartphone app now handles enrolment and CBAC entry.
- Source: [NHSRC ASHA-NCD evaluation](https://nhsrcindia.org/sites/default/files/IRHSS_%20A%20Training%2C%20Process%2C%20and%20Impact%20Evaluation%20of%20Utilizing%20ASHAs%20for%20NCD%20Screening.pdf); [BMC Health Serv Res](https://bmchealthservres.biomedcentral.com/articles/10.1186/s12913-018-3140-8/tables/1)
- Referral threshold: a CBAC score above 4 leads to referral to the Health and Wellness Centre (now Ayushman Arogya Mandir). — [Piramal FLW app Jira ticket](https://support.piramalfoundation.org/jira/browse/FLW-522). This is not official guidance; verify against MoHFW CBAC documents (e.g., [AAM document](https://aam.mohfw.gov.in/download/document/263f3ca26df87dc44b7687c1b9cf0c15.pdf)).

### Inferences
- **Price gap:** Dozee's home offer costs ~INR 29,000 up front plus ~INR 2,000–4,000/month at US prices. That leaves a clear gap below INR 5,000.
- **Positioning:** Dozee is ward- and ICU-focused in India and does not track weight. A device that combines daily weight trend, symptoms and a simple vital is differentiated.
- **Integration routes:** the natural paths are (a) alerts to the ASHA or ANM at the local Ayushman Arogya Mandir, and (b) an escalation link to an eSanjeevani teleconsult. Both need state or NHM partnership.
- **Hypertension follow-up:** ASHAs already do it, so adding a "daily weight plus breathlessness" check for discharged HF patients fits an existing workflow.

### Gaps
- I found no Indian home price for Dozee and no current Indian deployment count beyond 380+ hospitals.
- I found nothing on Sensesemi or AgVa in this search. Ultrahuman is a consumer wearables company and was not verified as doing HF monitoring.
- I found no NP-NCD or Ayushman Arogya Mandir document naming heart failure as a screened or followed-up condition. The programme materials found cover hypertension, diabetes and common cancers.
- ABDM / ABHA health-ID integration requirements for devices were not researched (search budget).

## 3. mHealth for low-literacy users: IVR, SMS, phones, 2G, power cuts

### Takeaway
- **Voice over text:** IVR or voice calls in local languages reach low-literacy feature-phone users at scale (Kilkari ~56 million women), but listenership drops off.
- **SMS:** Indian-language SMS is capped at 70 characters per segment (67 when concatenated), and every template must be pre-registered on TRAI DLT.
- **Cellular:** 2G is still alive on Airtel, Vi and BSNL. Jio is 4G-only. There is a ~250 million 2G feature-phone base. A 4G Cat-1 modem (A7670C) is the safer design choice, with 2G as a risk.
- **Power:** official rural supply is ~22 h/day, but independent monitoring shows several interruptions a day, so a battery backup is required.

### Cited Findings
**Kilkari (MoHFW maternal IVR programme)**
- Free weekly pre-recorded calls; runs in 23 states and 10 languages.
- IVR capacity of 12 million concurrent subscribers; cumulative reach ~55.9 million women.
- Source: [ARMMAN Q3 FY25 impact deck](https://armman.org/wp-content/uploads/2025/03/Q3_24-25_Impact-Deck.pdf) (programme self-report)
- Audio was chosen because nearly 50% of women in target states are illiterate and most use basic feature phones. — [GSMA case study](https://www.gsma.com/mobilefordevelopment/wp-content/uploads/2016/10/mHealth-Kilkari-a-maternal-and-child-health-service-in-India.pdf) (2016, older)
- **Coverage and retention:** coverage was 21% of pregnant women across 13 states in 2018, with low retention. Main reasons for drop-off were low listenership and unanswered calls. — [Mohan et al., BMJ Global Health 2022, via search summary](https://clinicaltrials.gov/study/NCT03576157)
- **RCT (Madhya Pradesh, n = 5,095):** no significant effect on exclusive breastfeeding (RR 1.04). — [ClinicalTrials.gov NCT03576157](https://clinicaltrials.gov/study/NCT03576157)

**SMS rules**
- Unicode (Hindi and other Indic scripts) SMS: 70 characters for a single segment, 67 per part when concatenated. One Indic character switches the whole message to UCS-2.
- Billing is per segment.
- Every template and sender ID must be registered on TRAI DLT.
- Sources: [Exotel Unicode SMS](https://developer.exotel.com/docs/sms-support/unicode-sms); [WebEngage TRAI DLT](https://docs.webengage.com/docs/trai-sms-dlt-regulations-india); [Fyno DLT templates](https://fyno.io/docs/dlt-sms-templates)
- An older Zoho page says 60/53 characters. This conflicts with the above; the 70/67 figure is the GSM-standard value. — [Zoho](https://help.zoho.com/portal/en/kb/crm-v2-1/connect-with-customers/notification-sms/articles/crm-v2-notification-sms-sender-id-requirements-for-india)

**2G and 4G status**
- Airtel has said it will keep 2G for feature-phone users, partly because older phones lack VoLTE. — [91mobiles](https://www.91mobiles.com/hub/?p=291528)
- Vi told TRAI that a forced 2G shutdown would cut off low-income users and 2G-dependent POS and IoT devices, and proposed handset subsidies. — [Voice&Data](https://www.voicendata.com/news/jios-stance-on-the-shutdown-of-2g-and-3g-challenged-by-vodafone-idea-3651302); [tele.net](https://tele.net.in/vi-opposes-jios-suggestion-to-phase-out-2g-networks/)
- Vi planned to fully shut 3G in FY25. — [TelecomTalk](https://telecomtalk.info/vodafone-idea-to-shut-down-3g-completely-in-fy25/915663/)
- Jio, which is 4G/5G-only, lobbies for a national 2G/3G phase-out and targets the "~250 million" 2G feature-phone users with JioBharat 4G phones. A JioBharat K1 sells for ~INR 699. — [Light Reading](https://www.lightreading.com/business-management/jio-s-dream-of-a-2g-free-india-is-a-nightmare-for-telcos); [TechCrunch Oct 2024](https://techcrunch.com/2024/10/15/india-reliance-targets-2g-users-with-13-4g-phones-offering-streaming-payments); [NavBharat Live](https://navbharatlive.com/technology/jio-bharat-phone-4g-phone-for-just-rs-699-know-features-and-plans-1156790.html)
- Airtel had ~130 million 2G users in 2023 (dated). — [Communications Today](https://www.communicationstoday.co.in/?p=258989)
- **2026 TRAI subscriber trends:** Vi's rural base fell from 93.23M to 93.08M in May 2026. Airtel and Jio are gaining, and Jio passed 500M mobile users. — [TelecomTalk](https://telecomtalk.info/vodafone-idea-lost-rural-mobile-jio-gained-trai/1009218/); [TelecomTalk](https://telecomtalk.info/airtel-top-wireless-gainer-in-may2026-trai/1009097/)
- An Indian retailer blog says 2G is being phased out rapidly and SIM800L may not work on current networks. This is a vendor claim and overstated: no operator has announced a shutdown. — [Zbotic](https://zbotic.in/sim800l-vs-a6-mini-gsm-module-low-cost-comparison-for-india/)

**Phone ownership among older adults**
- About 60% of India's ~104 million older adults own a smartphone, but up to 85% find it hard to use (small 2020 feasibility study). — [PMC7740952](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7740952/)
- Rural Mysore study (n = 150 older adults, 2022): 50% owned a mobile phone, very few a smartphone; digital literacy was 11%. — [Geriatrics 2022 (DOAJ)](https://doaj.org/article/84c3b157657d43428b43f94bc238b9f1)
- Rural Punjab (2025, qualitative): households typically have a dedicated feature phone for the elder plus a shared smartphone, and rely on younger family members. — [SAGE Mobile Media & Communication 2025](https://journals.sagepub.com/doi/10.1177/20501579251378548)

**Power supply**
- Official national average rural supply was ~22 h/day in FY2023-24. Nagaland, J&K, UP and Haryana were below 20 h. — [Rajya Sabha PQ, Feb 2025](https://rsdebate.nic.in/bitstream/123456789/758173/1/PQ_267_03022025_U153_p494_p495.pdf)
- Prayas monitoring: in half of rural locations, outages exceeded 15 h/month, with 2–4 interruptions per day. — [Prayas Energy Group](https://energy.prayaspune.org/images/pdf/100-rural-electrification-is-not-enough.pdf) (older study)
- Brookings: many rural areas have up to ~4 outages per day and power only 60–70% of the time. — [Brookings](https://www.brookings.edu/electrified-but-without-electricity)
- Feeder-level outage data is mostly not public; Karnataka is an exception. — [LEAP Journal, Sep 2025](https://blog.theleapjournal.org/2025/09/a-review-of-outage-reporting-by-indian.html)

### Inferences
- **Alert channel:** an outbound voice call (pre-recorded, local language) to the patient's own phone and to a caregiver's phone is the most inclusive alert. SMS should be secondary: 70 Indic characters is enough for "Weight up 2 kg in 3 days — call ASHA/doctor", but not for nuance.
- **Retention:** Kilkari's drop-off shows that frequent, low-value calls get ignored. Alerts should be rare and actionable.
- **Cellular hardware:**
  - SIM800L (2G) is cheaper but carries regulatory/longevity risk and does not work with Jio SIMs.
  - A7670C (4G Cat-1, with 2G fallback on the "C" variant per SIMCom) works on Jio, Airtel and Vi.
  - Use Wi-Fi via the ESP32 where a home has a smartphone hotspot or broadband, mainly in urban homes.
- **Power and storage:** an 18650 battery backup and store-and-forward of readings are required. Morning weighing can coincide with power outages.

### Gaps
- No 2025–26 official 2G shutdown dates or 2G subscriber counts by operator were found. TRAI does not publish a 2G/4G split in monthly press releases.
- mMitra (ARMMAN) results were not separately retrieved.
- No NSS or LASI figure on feature-phone vs smartphone ownership among rural people aged 60+ was retrieved.
- No official per-SMS price was found; it depends on the aggregator.

## 4. Design lessons for elderly / low-literacy users and cultural habits

### Takeaway
The evidence supports:
- voice output in the local language
- very few controls
- colour-coded status
- treating family members, often children living in cities, as the real users of the data

Indian sleep and bathing habits (charpai, floor mats, shared beds) are relevant to sensor placement, but I found no rigorous sources on them in this search. Those points are listed as inferences and gaps.

### Cited Findings
- Older Indian smartphone owners struggle with daily use (up to 85%). — [PMC7740952](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7740952/)
- Rural elderly have low digital literacy (11%) and low health literacy. — [Geriatrics 2022](https://doaj.org/article/84c3b157657d43428b43f94bc238b9f1)
- Rural elders rely on younger family members for phone use and share smartphones. — [SAGE 2025](https://journals.sagepub.com/doi/10.1177/20501579251378548)
- Kilkari used audio because of ~50% female illiteracy, and IVR suits feature phones. — [GSMA](https://www.gsma.com/mobilefordevelopment/programme/mhealth/an-overview-of-kilkari-a-maternal-and-child-health-service-in-india)
- In THFR, 18.2% of women and 9.0% of men with HF had no formal education. — [PMC10424635](https://pmc.ncbi.nlm.nih.gov/articles/PMC10424635)

### Inferences
**Hardware UX**
- One big button or no buttons: auto-wake when someone steps on the scale.
- Three-colour LED: green / amber / red.
- Recorded voice in the user's language (MAX98357A or DFPlayer plus speaker).
- Numbers on the display are optional; many users will not read them.

**Caregiver loop**
- Send alerts to a son or daughter in the city via a voice call or WhatsApp, and to the ASHA.
- Collecting the caregiver's number at setup is essential.

**Weighing habits (to validate in user research)**
- Weighing may happen barefoot after the morning bath or toilet, but footwear and clothing vary.
- Use a fixed daily routine and voice prompts such as "remove slippers".
- Use trend algorithms (e.g., 3-day change) rather than absolute weight.

**Sleep habits (to validate in user research)**
- Many rural elders sleep on charpais (rope cots), floor mats or shared beds, and often outdoors in summer.
- Under-mattress or bed-frame load sensing (Dozee-style) is therefore unreliable or impossible for many homes.
- A floor-standing scale is more universal than a bed sensor.
- Shared beds also confound bed-based respiration sensing.

**Physical design**
- A sturdy, non-slip, wide platform for frail users (fall risk).
- Water and dust tolerance, because it may sit in or near a bathroom.

### Gaps
- No peer-reviewed or survey source was found on how common charpai, floor-mat or shared-bed sleeping is among Indian elderly HF patients. This needs primary user research or NFHS/LASI housing data.
- No Indian-specific study on icon or colour comprehension for elderly device users was retrieved.

## 5. Indian component prices (INR)

### Takeaway
Hobby-grade parts for a scale-based HF monitor with ESP32-S3, HX711 with 4 load cells, voice output, a 4G modem, a battery and a small display come to roughly INR 3,000–4,500 at single-unit Indian retail prices. That fits under INR 5,000, but with little margin if you add ECG, impedance or a TFT. Bulk prices from IndiaMART or wholesale are often 30–50% lower.

### Cited Findings
| Part | INR price found | Source |
|---|---|---|
| ESP32-S3 DevKitC-1 (N8R2 / N16R8) | 1,299 (Probots); 885 + GST (Compoindia, N16R8); ~799 (Amazon.in generic) | [Probots](https://probots.co.in/esp32-s3-devkitc-1-development-board-wireless-module-wifi-bluetooth.html); [Compoindia](https://compoindia.com/product/esp32-s3-devkitc-1-n16r8-esp32-s3-development-board-wi-fi-ble-mcu-module-integrates-complete-wi-fi-and-ble-functions-for-arduino/); [Amazon.in](https://www.amazon.in/esp32-s3/s?k=esp32-s3) |
| HX711 board alone | ~40–59 (some ex-GST); IndiaMART 44 | [Probots](https://probots.co.in/hx711-load-cell-amplifier-board-adc-converter-weight-module.html); [SmartXpro](https://smartxprokits.in/hx711-load-cell-amplifier-module/); [IndiaMART](https://www.indiamart.com/proddetail/hx711-load-cell-module-2854190100930.html) |
| 50 kg half-bridge load cell + HX711 (single) | 136 (Robocraze); 220 (Engineer Store); 124 (IndiaMART); 734 (Flipkart combo) | [Robocraze](https://robocraze.com/products/50kg-load-cell-hx711); [Engineer Store](https://www.theengineerstore.in/products/50kg-load-cell-with-hx711-weight-sensor); [IndiaMART](https://www.indiamart.com/proddetail/50kg-load-cell-with-hx711-weight-sensor-2853903648930.html) |
| 4x 50 kg load cells + HX711 kit (DIYmalls) | ~1,205–1,467 on Amazon.in (varies by snapshot) | [Amazon.in](https://www.amazon.in/load-cell-with-hx711/s?k=load+cell+with+hx711) |
| AD8232 ECG module | 375 + GST (MRP 442.5, ElectronicsComp); 486–528 (Zbotic / Probots / Engineer Store); 695 + GST (ElectroPi); IndiaMART 298–1,800 | [ElectronicsComp](https://www.electronicscomp.com/ad8232-ecg-monitor-sensor-module-india); [Engineer Store](https://www.theengineerstore.in/products/ad8232-ecg-module); [Probots](https://probots.co.in/ad8232-ecg-sensor-module-heart-rate-pulse.html); [IndiaMART](https://www.indiamart.com/proddetail/ad8232-ecg-sensor-module-21591026388.html) |
| MAX30102 | ~96 (Zbotic; GST status unclear) | [Zbotic (search snippet)](https://zbotic.in/product/ad8232-ecg-monitor-sensor-module/) — weak; verify |
| MAX98357A I2S amp | ~249 (Amazon.in) | [Amazon.in search](https://www.amazon.in/esp32-s3-devkit/s?k=esp32+s3+devkit) |
| OLED + INMP441 + MAX98357 combo kit | ~799 (Amazon.in) | same as above |
| DFPlayer Mini | 260–349 (Amazon.in) | [Amazon.in](https://www.amazon.in/dfplayer-mini/s?k=dfplayer+mini) |
| SIM800L (2G) | 150–350 (Zbotic); 448 (IndiaMART Mini) | [Zbotic](https://zbotic.in/sim800l-vs-a6-mini-gsm-module-low-cost-comparison-for-india/) |
| A7670C (4G Cat-1) bare module | 450–900 (IndiaMART); 700 (A7670C-LASS); ~1,900 for a TTL breakout board | [IndiaMART](https://m.indiamart.com/proddetail/simcom-a7670c-chip-module-2856272006788.html); [IndiaMART LASS](https://m.indiamart.com/proddetail/simcom-a7670c-lass-lte-4g-module-cat-1-2850427127248.html); [IndiaMART board](https://m.indiamart.com/proddetail/wireless-simcom-7670c-4g-lte-gsm-module-with-ttl-output-for-electrical-industry-2856484594655.html) |
| 1.3" I2C OLED (SH1106) | 179 (1.29" CH1115, Robu); 299–319 (Rytronics / Robu); 499 (Amazon.in) | [Robu OLED category](https://robu.in/product-category/oled-display/); [Rytronics](https://www.rytronics.in/product-category/all-porducts/sensor-and-modules/modules/display-module/) |
| 2.4" TFT touch shield | ~428 (Rytronics, discounted from 699) | [Rytronics](https://www.rytronics.in/product-category/all-porducts/sensor-and-modules/modules/display-module/) |
| AD5933 (bio-impedance) | Chip $11.45 @1k (ADI); module ~$41.53 (AliExpress); no INR retail found | [Analog Devices](https://www.analog.com/en/products/ad5933/sample-buy.html); [AliExpress](https://www.aliexpress.com/w/wholesale-ad5933.html) |

### Inferences
**Illustrative BOM, retail single unit, mid-range prices, scale-based design**

| Part | INR |
|---|---|
| ESP32-S3 board | ~900 |
| 4-load-cell + HX711 kit | ~1,300 |
| A7670C module plus breakout and antenna | ~900–1,900 |
| MAX98357A + speaker | ~350 |
| 1.3" OLED or 3 LEDs | ~50–300 |
| 18650 cell + BMS/charger | not sourced; typically a few hundred |
| Enclosure / platform | not sourced |
| **Total** | **~3,500–4,800** |

- The 4G modem is the biggest swing cost. A cheaper alternative is Wi-Fi only plus Bluetooth to a family smartphone (urban). Rural homes need cellular.
- Hacking a cheap digital bathroom scale would replace the 4-load-cell kit and platform (often the cheapest platform plus load cells available). Its price was not retrieved, so verify on Amazon.in.
- AD5933 has no INR retail listing, and the ~$41 module price (~INR 3,500) would break the budget alone. Thoracic or body impedance is likely out of scope at INR 5,000 unless done with a discrete AD9833-based design.

### Gaps
- No INR prices were found for: 18650 cells and BMS, ESP32 (non-S3) boards, INMP441 standalone, DS3231, AD9833 module, piezo film sensors, or a cheap digital bathroom or body-composition scale.
- Robu.in product pages were blocked (403), so Robu prices are missing apart from OLED.
- Amazon prices are search-page snapshots.

## 6. Regulatory: CDSCO classification for vitals monitors and SaMD

### Takeaway
- **Framework:** India regulates devices under the Medical Devices Rules 2017, with risk classes A–D. All medical devices have needed licensing since Oct 2023 per secondary sources (not verified here).
- **SaMD guidance:** CDSCO issued a draft Guidance on Medical Device Software on 21 Oct 2025. It separates SaMD from SiMD. SiMD inherits the class of its hardware, and SaMD is classed A–D by risk. I found no evidence it has been finalised.
- **Classification of this device:** consultancy blogs disagree on patient and cardiac monitor classes (B vs C vs D). A home HF alert device would most likely be Class B, or Class C if it makes diagnostic or alarm claims. Confirm against official notifications.

### Cited Findings
- CDSCO draft guidance on medical device software, dated 21 Oct 2025:
  - Distinguishes SaMD (standalone) from SiMD (embedded).
  - Uses risk-based classes aligned with the MDR 2017 First Schedule.
  - Covers technical documentation, QMS, ISO/IEC standards, clinical or performance evaluation, and post-market vigilance.
  - Source: [India Briefing](https://india-briefing.com/news/cdsco-draft-guidance-medical-software-40691.html); [Nishith Desai](https://www.nishithdesai.com/research-and-articles/hotline/pharma-healthcare-update/the-next-frontier-in-medtech-regulation-dissecting-cdscos-draft-guidance-on-medical-device-software-15465)
- Law firms disagree on whether the draft creates new obligations or only interprets MDR 2017. — [Cyril Amarchand Mangaldas, Jan 2026](https://corporate.cyrilamarchandblogs.com/2026/01/medical-device-as-software-has-cdsco-guidance-changed-the-rules/); [Nishith Desai regulatory wrap 2025](https://nishithdesai.com/research-and-articles/hotline/pharma-healthcare-update/regulatory-wrap-2025-medical-devices-industry-in-india-15486)
- **Classes and licence forms:**
  - Classes: A low; B low–moderate; C moderate–high; D high.
  - Manufacturing licences: MD-3/MD-5 for Class A/B (state licensing authority) and MD-7/MD-9 for Class C/D (central licensing authority).
  - Import: MD-14/MD-15.
  - Source: [Corpseed](https://corpseed.com/knowledge-centre/classification-of-medical-devices-by-cdsco-in-india); [Operon Strategist](https://operonstrategist.com/examples-of-medical-device-classifications/)
- **Conflicting secondary classifications (consultancy blogs, not official):**
  - Diagnostic ECG: Class B; ambulatory ECG: Class C.
  - "Multiparameter monitor with critical parameters": Class C.
  - Cardiac monitor: listed as C in one source and D in another.
  - Spot-check pulse oximeter: Class A in one source.
  - Sources: [Operon Strategist](https://operonstrategist.com/examples-of-medical-device-classifications/); [Seyecs blog](https://blogs.seyecs.com/?p=5562); [Corpseed non-notified](https://www.corpseed.com/knowledge-centre/classification-of-non-notified-medical-devices-by-cdsco)
- CDSCO periodically publishes risk classifications of newly notified devices. — [Medical Dialogues](https://business.medicaldialogues.in/amp/cdsco-releases-risk-classification-of-newly-notified-medical-devices-ivds-details)

### Inferences
- **Wellness framing:** a startup can lower its burden by framing the product as a weighing scale plus symptom reminder that notifies a clinician, rather than as a diagnostic. Personal weighing scales are generally not medical devices.
- **Medical claims:** once it claims "early warning of HF decompensation", the software is likely SaMD or SiMD, plausibly Class B (or C if it is treated as a monitor with alarms). That requires an ISO 13485 QMS and a manufacturing licence.
- **Plan for:** state-level MD-5 licensing (if Class B), ISO 13485, IEC 60601-1 / -1-2 / -1-11 (home-use electrical safety and EMC), and possibly a clinical performance study.
- **Telecom:** a 4G module in the product may also trigger BIS/TEC (MTCTE) certification. Not researched.

### Gaps
- The official CDSCO classification list entry for "patient monitor", "weighing scale (medical)" and "ECG" was not retrieved; blogs conflict.
- No information on whether the Oct 2025 SaMD draft was finalised in 2026.
- MTCTE/TEC and BIS rules for IoT modules and Wi-Fi were not researched.
