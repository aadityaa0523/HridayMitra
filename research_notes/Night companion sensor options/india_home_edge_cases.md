# Indian Home Conditions and Elderly-User Factors for Night / Wearable Heart Failure Monitoring

Scope note: about 20 search/fetch calls. Two primary PDFs (MoHFW LASI Brief, BMJ Open Suhriday pilot via DOAJ) returned HTTP 403 and could not be read, so several LASI figures below come from peer-reviewed secondary analyses or credible news summaries of LASI rather than the LASI report tables. Anything marked "ASSUMPTION" has no source found and is designer judgement only.

## 1. Sleeping arrangements (bed/room sharing, floor/mat, charpai, outdoor/rooftop sleeping, rural vs urban)

### Takeaway
Almost no older Indian adult lives or sleeps truly alone: only about 5.7% of people 60+ live alone. No national dataset quantifies bed-sharing, floor or mat sleeping, charpai use or rooftop sleeping among the elderly. That is a real evidence gap, and designers should treat a shared room or shared bed and a movable sleeping surface as the default case.

### Cited Findings
- About 5.7% of people aged 60+ in LASI Wave 1 live alone (1.4% at 45–59). Living alone is more common among women and in rural areas. — [Down To Earth summary of LASI](https://www.downtoearth.org.in/blog/health/how-is-india-s-population-ageing-evidence-from-lasi-81770)
- LASI Wave 1 analysis of people aged 45+: 3.85% live alone in rural areas and 2.32% in urban areas, and the share rises with age. — [IPC 2021 abstract (IIPS)](https://ipc2021.popconf.org/abstracts/211497)
- In a Tamil Nadu (Salem district) study of 278 married adults (not elderly-specific), 47.8% co-slept with their spouse and 52.2% slept apart ("sleep divorce"). Reasons for sleeping apart included preference, childcare and comfort. — [Frontiers in Sleep, 2026](https://www.frontiersin.org/journals/sleep/articles/10.3389/frsle.2026.1745546/full)
- 97.8% of Indian children aged 5–12 in a pediatric sample co-slept, which shows how normal shared sleeping spaces are in Indian homes. — [Indian Pediatrics, 2022](https://indianpediatrics.net/mar2022/250.pdf)
- NFHS records a "rooms used for sleeping" variable (HV216): a room is a space with a permanent partition used regularly for sleeping, and state-level "mean persons per sleeping room" is published. The values were not retrievable in this pass. — [World Bank microdata, NFHS variable](https://microdata.worldbank.org/catalog/2949/variable/F3/V85?name=hv216); [Indiastat NFHS-4 housing table](https://www.indiastat.com/table/template/india-state/health/region-state-wise-percentage-selected-housing-char/1284966)
- Outdoor and rooftop sleeping in heat is documented in reporting, not surveys. A Delhi rickshaw driver sleeps on his roof for cooler air. In Bhubaneswar, a poor family slept on straw mats outside their huts. Tin and asbestos roofs trap heat in slum housing. — [Eco-Business / Thomson Reuters Foundation](https://www.eco-business.com/news/armed-with-wet-sacks-indias-poorest-try-to-beat-extreme-heat/)
- A memoir account of a 1970s–80s Delhi family describes charpoys moved to the balcony in summer, with a ceiling fan running. This is anecdotal and historical. — [The Quint](https://thequint.com/voices/blogs/how-i-remember-my-balcony-charpoys-coolers-and-anti-sikh-riots)

### Inferences
- With fewer than 6% of people 60+ living alone, a bedside radar, microphone or bed sensor will usually see more than one body. It needs person-separation or range-gating, or it should be paired with a wearable worn by the patient so the signal can be attributed to them.
- ASSUMPTION (no data found): floor mattresses, mats, charpais (rope cots) and seasonal relocation to the courtyard, verandah or roof are common, especially in rural north and central India in April–June. An under-mattress pressure or BCG sensor and a fixed bedside unit that needs mains power will both fail when the sleeper moves. A body-worn sensor, or a bedside unit that runs on battery and can be carried, handles relocation better.
- A charpai's woven rope surface sags and transmits motion differently from a mattress on a wooden bed. Any bed-mounted sensor needs calibration per surface type.

### Gaps
- No national figure found for the share of elderly people who share a bed or room, sleep on the floor or a mat, or use a charpai. NFHS and LASI do not appear to ask this directly. The NFHS "persons per sleeping room" mean is the best proxy but was not retrieved.
- No quantitative data on seasonal outdoor or rooftop sleeping by age or region.

## 2. Night environment (fans, heat/humidity, mosquito nets, power cuts, noise, family members and pets)

### Takeaway
Fans are near-universal (NFHS-5: 96.4% of urban and 84.3% of rural households). Night heat stresses older hearts. Rural power is officially about 22 hours a day but unreliable in practice, and independent surveys show far worse supply in some states. Mosquito nets are present in roughly a third of households. A night device must survive power cuts, airflow noise and movement, and multiple sleepers.

### Cited Findings
- NFHS-5 (2019–21): 96.4% of urban and 84.3% of rural households own an electric fan (any type, not only ceiling fans). — [Swarajya, citing NFHS-5](https://swarajyamag.com/amp/story/commentary/an-ujala-moment-for-the-humble-ceiling-fan-a-massive-leap-for-indias-residential-energy-consumption)
- Prayas survey: about 94% (Uttar Pradesh) and 95% (Maharashtra) of surveyed households own ceiling fans. — [Prayas Energy Group](https://energy.prayaspune.org/our-work/article-and-blog/space-conditioning-focus-on-fans-and-air-coolers-for-efficiency)
- The Ministry of Power told the Rajya Sabha (Feb 2025) that average rural supply was about 22 hours a day in 2023-24. Nagaland, J&K, Uttar Pradesh and Haryana were below 20 hours. — [Rajya Sabha PQ 267, 03-02-2025](https://rsdebate.nic.in/bitstream/123456789/758173/1/PQ_267_03022025_U153_p494_p495.pdf)
- States including Bihar, Madhya Pradesh, Telangana and Himachal Pradesh have seen significant cuts in rural supply hours. — [Policy Circle](https://www.policycircle.org/policy/india-eyes-24x7-electricity)
- Older independent data (2015, 714 villages in 6 states): 50% of electrified rural households got less than 12 hours of supply a day. A Prayas monitoring network found half its locations had more than 15 hours of outages per month. — [Prayas, "100% rural electrification is not enough"](https://energy.prayaspune.org/images/pdf/100-rural-electrification-is-not-enough.pdf)
- Yale survey, Dec 2025–Feb 2026: about two-thirds of Indians experience electricity disruptions on a typical day. — [Yale Program on Climate Change Communication](https://climatecommunication.yale.edu/?p=31611)
- Mosquito nets: a DHS user-forum post quotes "36% of households have at least one mosquito net, 8% an ITN" for India's 2019 survey. The poster could not reproduce the ITN figure, and the link to NFHS-5 is unverified. — [DHS user forum](https://userforum.dhsprogram.com/pdf.php?msg=24675). A town study in Odisha found 94.2% household net coverage but only 45.7% regular use. — [PMC11229663](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11229663/)
- Night heat: older adults show higher heart rates and more physiological stress when sleeping warm. Higher night temperatures reduce deep and REM sleep. — [Eco-Business](https://www.eco-business.com/news/armed-with-wet-sacks-indias-poorest-try-to-beat-extreme-heat/)
- Sleep problems are common among Indians 60+ (LASI-1), with estimates depending on definition: 9.9% insomnia (symptoms at least 5 times a week) — [European Psychiatry 2024](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11863040/); 14.8% sleep problems, linked to multimorbidity, pain and depression — [PLOS ONE 2023](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9910705/); 37% insomnia — [PMC11960366](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11960366/).

### Inferences
- Power: a dock or bedside unit needs a battery to cover multi-hour outages, and the wearable must keep logging when the dock is unpowered. Alerts should go out over cellular/SMS, not home Wi-Fi, because Wi-Fi routers also lose power.
- Fans: ceiling-fan airflow and vibration create motion and acoustic noise that will affect radar, microphone (cough or breathing sounds) and bed-vibration sensors. Validate with a fan running at high speed.
- Heat and sweat: in pre-monsoon and monsoon humidity, a strap or adhesive worn all night on the chest or wrist will cause sweat, rash and slippage. Optical PPG and skin-contact electrodes will drift.
- Mosquito nets: a net (polyester mesh) between the bedside unit and the sleeper is mostly radar-transparent, but it blocks line-of-sight for cameras or IR and physically blocks reaching for a button. ASSUMPTION: needs a bench test.
- Rising night temperatures are themselves a cardiac stressor for HF patients. Logging room temperature is cheap and useful context.
- Night-time waking from insomnia, nocturia and HF orthopnoea means the patient may get up repeatedly. Expect frequent "out of bed" periods, which are not device faults.

### Gaps
- No verified NFHS-5 mosquito-net figure was retrieved. The national tables need checking.
- No India data found on night-time noise levels in homes, or on pets or livestock in sleeping areas. Livestock sharing living space is common in some rural homes (ASSUMPTION, unverified).
- No data found specifically on how often outages happen at night, as opposed to daily averages.

## 3. Clothing and cultural acceptability of body-worn devices

### Takeaway
Evidence is thin. One Delhi study found more than 80% of women aged 65–80 wear a sari day and night. The nightie is widely reported as the default homewear and nightwear for older women. No study was found on acceptance of chest-worn devices, or on interaction with mangalsutra, sacred threads or bangles. These need user testing.

### Cited Findings
- Study of 160 women aged 65–80 (Delhi and satellite towns): more than 80% wore the traditional sari during the day and at night. The study reported fit and comfort problems with sari blouses and found that market clothing was designed for younger people. — [Research Journal of Textile and Apparel, "Design of Ergonomic Garment for Elderly Indian Women"](https://emerald.com/insight/content/doi/10.1108/RJTA-17-03-2013-B012/full/html)
- The nightie is described as the garment of choice for many Indian grandmothers (cultural commentary, not a survey). — [Homegrown](https://homegrown.co.in/homegrown-voices/the-history-of-the-indian-nightie-from-colonial-sleepwear-to-iconic-cultural-staple). In Kerala, women report wearing nighties for comfort, especially in summer, including an 88-year-old. — [The News Minute](https://www.thenewsminute.com/kerala/keralas-showstopper-women-nighties-30354)
- A web survey of Indian adults (n=495, aged 16+, not elderly-specific) found 62.2% use some wearable for health management. Elderly representation is likely low. — [PMC9740494](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9740494/)
- An India-authored qualitative study followed 12 seniors aged 60–69 using smartwatches for 6–12 months, focused on usability, accessibility and social support (CRC Press chapter, 2025; full text paywalled). — [Christ University archive](https://archives.christuniversity.in/items/show/27879)

### Inferences
- ASSUMPTION (not sourced): common nightwear among older men is a cotton vest (baniyan) with a lungi, dhoti or pyjama, and many men sleep shirtless in summer. Older women commonly sleep in a sari with blouse and petticoat, or a nightie. Women's blouses are tight-fitting and many women wear no bra at night. A chest strap would have to go under the blouse or sari pallu, and wearing it may need help. A wrist or upper-arm device avoids undressing.
- ASSUMPTION: the wrist is already crowded for many women (glass or metal bangles, sometimes worn permanently) and for many men and women (sacred red/black threads such as kalava or raksha sutra, copper bracelets). A wrist device may need to go on the other arm, or be designed to sit alongside bangles. Metal bangles near a PPG or BLE antenna could also cause interference.
- ASSUMPTION: married Hindu women wear a mangalsutra (a gold and black-bead necklace) continuously and are culturally reluctant to remove it. A pendant-style chest sensor ("locket") may be acceptable because lockets and taveez (amulet) pendants are familiar, but it must not need the mangalsutra removed and must not be confused with one. This is a hypothesis to test with users, not a finding.
- Modesty: any device needing placement on bare skin over the chest, especially for women and with a male family member or ASHA helping, risks rejection. Prefer placements that need no undressing (wrist, upper arm over clothing, finger) or no contact at all (bedside).

### Gaps
- No peer-reviewed data found on elderly Indian men's nightwear.
- No study found on cultural acceptability of chest-worn medical devices, pendants or patches in India, or on conflicts with mangalsutra, threads or bangles.
- The JMIR Aging 2026 smartwatch acceptance study in adults 60+ (https://aging.jmir.org/2026/1/e76404/PDF) could not be read, and its country is unconfirmed.

## 4. Elderly user factors in India (sensory loss, dementia, literacy, frailty, helpers, phones and charging)

### Takeaway
Vision impairment is very common, hearing loss is underdiagnosed and rarely aided, and dementia affects about 7.4% of people 60+. Basic phone access is high (over 84% of households), but smartphone access among people 60+ is only about 42–45%, and many find technology confusing and depend on children or grandchildren. The device must work with zero literacy, no smartphone and a family helper.

### Cited Findings
- Vision: measured visual acuity worse than 20/80 in about 33.8% of men and 40% of women aged 45+ (LASI 2017–18), with state variation up to 77% for women in Arunachal Pradesh. — [BMC Ophthalmology 2023](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10240694/). Another LASI analysis (45+) gives vision impairment 48.0%, hearing impairment 6.9% and dual sensory impairment about 5%. — [Aging and Health Research 2022](https://doaj.org/article/3ac37c227d8c44c2b6e63af4eb24f272). Among people 60+: 13.7% impaired vision, 9.6% impaired hearing (different definition). — [PMC11907313](https://pmc.ncbi.nlm.nih.gov/articles/PMC11907313). These estimates differ by definition, so the definition must be quoted alongside any figure.
- Only about 5% of older adults with hearing difficulty use hearing aids, and use is lower among the poor, Scheduled Castes and rural residents. — [PMC9646738](https://pmc.ncbi.nlm.nih.gov/articles/PMC9646738)
- People in a South Indian cohort (55+) waited about 3.5 years from noticing hearing difficulty before getting tested. — [IJCMPH](https://www.ijcmph.com/index.php/ijcmph/article/view/16352)
- Dementia: 7.4% prevalence among people 60+ (LASI-DAD, 2018–20), about 8.8 million people, with strong age and education gradients and urban/rural and state differences. — [NIH Fogarty](https://www.fic.nih.gov/News/GlobalHealthMatters/march-april-2023/Pages/new-estimate-dementia-prevalence-magnitude-india-challenge.aspx). Under DSM-5 criteria, mild neurocognitive disorder is 17.6% and major is 7.2%. — [PLoS ONE 2024, PMC10849236](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10849236/)
- Phones: LASI found mobile phone access in 93.6% of urban and 84.1% of rural households of people 45+. — [ORF](https://www.orfonline.org/expert-speak/screen-time-may-be-rising-steadily-among-older-indians). Smartphone access is 44.7% at ages 60–69 and 42% at 70+, compared with 88.6% at 18–49. About 2 in 5 people 60+ say they can use the internet. — [Communications Today, CMS:T data](https://www.communicationstoday.co.in/?p=357574). Only 13% of Indians 60+ have ever used the internet (NITI Aayog). — [ORF](https://orfonline.org/research/screen-time-may-be-rising-steadily-among-older-indians)
- HelpAge India (n=5,798, 10 cities, urban): 71% find basic feature phones easy, 41% use smartphones, and 66% find technology confusing. Children (54%) and grandchildren (52%) act as their digital guides. — [Outlook Money](https://www.outlookmoney.com/amp/story/news/digital-divide-among-elderly-66-find-digital-tools-too-confusing)
- Rural Karnataka (DAHLIA, n=150): 50% owned a mobile phone, very few had a smartphone, and digital literacy was 11%. Low exposure and low confidence drove low tech use. — [PMC8938771](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8938771/)
- Insomnia predictors among older Indians include illiteracy, living without a spouse, female sex and chronic conditions. Illiteracy is therefore common enough to be a predictor in its own right. — [PMC11960366](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11960366/)
- Self-reported disability (45+, LASI): locomotor 5%, visual 3%, mental 2%, hearing 2%. — [Down To Earth](https://www.downtoearth.org.in/news/health/every-fourth-senior-citizen-in-india-rates-health-as-poor-lasi-75193)
- ASHAs have been trained to run smartphone-based CVD risk screening for people 40+ in rural Andhra Pradesh. They screened about 86% of the target population, doctors followed up 70% of high-risk referrals, and the system sent IVR (voice) reminders to patients. — [Down To Earth](https://www.downtoearth.org.in/health/new-mobile-app-may-help-in-addressing-heart-disease-in-rural-areas-63888)

### Inferences
- Alerts and feedback: avoid relying on small text or on one alert channel alone. Use high-contrast LEDs plus loud, low-frequency tones (age-related hearing loss affects high frequencies first; general audiology knowledge, not India-sourced), plus vibration. Escalate by SMS or voice call to a family member's phone, since the patient may not hear or see the alert.
- Literacy: use icons, colours and recorded voice prompts in the local language rather than text. SMS to the caregiver can be text, but voice/IVR is safer for the patient.
- Phones: design for a feature phone at the receiving end. SMS or voice must be the baseline, with any app optional. This matches the HF-hackathon SMS design.
- Charging: ASSUMPTION (no India data found on elderly device-charging habits). Given dementia and vision loss, and that people already charge feature phones every few days, make charging require no thought: a drop-in dock, at least a week of battery, and a visible or audible low-battery warning that also reaches the caregiver.
- Helpers: plan for a named family caregiver (often a son, daughter-in-law or grandchild) as the main user for setup, charging and alert response, with the ASHA as the community escalation point. With dementia at about 7% and mild cognitive disorder at about 18%, assume the patient cannot be relied on to put the device on or take it off correctly every night.
- Tremor and frailty: ASSUMPTION (no India prevalence found). Use large, single-action controls and no small clasps or buckles. A magnetic or slip-on band is preferable.

### Gaps
- No LASI literacy or "never attended school" figure for people 60+ was retrieved. The LASI national report should have it.
- No India data found on tremor or Parkinson's prevalence, grip strength or frailty indices relevant to device handling.
- No data on how often older Indians charge phones, or on who in the household does it.
- No official NPHCE document was retrieved on ASHA roles in elderly or heart failure home care.

## 5. Lessons from Indian health-tech and assistive-device deployments with older adults

### Takeaway
The best Indian evidence on adoption comes from hearing aids, and it says attitude, stigma and denial, not cost or device faults, drive non-use. Heart failure remote monitoring in India is barely studied. Community-health-worker-mediated models (ASHA plus app plus IVR) show high reach.

### Cited Findings
- Punjab study (n=74 elderly): 54% of people who had hearing aids did not use them. Non-users scored higher on stigma, denial and emotional impact of hearing loss. — [Journal of the Indian Academy of Geriatrics 2019](https://doaj.org/article/a73f16bfd7d545e6a1d29e407c65e89b)
- Karnataka study (n=100): attitude-related reasons for not accepting hearing aids ranked above device-related, personal and financial reasons. — [Manipal researcher portal](https://researcher.manipal.edu/en/publications/reasons-for-nonacceptance-of-hearing-aid-in-older-adults/)
- National: only 5% of older adults with hearing difficulty use hearing aids. — [PMC9646738](https://pmc.ncbi.nlm.nih.gov/articles/PMC9646738)
- Suhriday, a smartphone app for heart failure self-care and remote monitoring, was piloted at a tertiary hospital in Bengaluru (St John's). The authors note there is little evidence on mobile-app-facilitated remote HF monitoring in India. — [BMJ Open 2022 via DOAJ](https://doaj.org/article/09be39f8ae9d478a93e748128f6984ab); [St John's publication page](https://www.stjohns.in/publications/usability-and-feasibility-assessment-of-a-smartphone-application-suhriday-for-heart-failure-self-care-remote-monitoring-in-an-indian-tertiary-health-care-setting-a-pilot-mixed-methods-study). The full results (sample, attrition) were not retrieved because of a 403 error.
- The ASHA-delivered mHealth CVD screening in Andhra Pradesh reached about 86% of the target population, with IVR reminders for patients. — [Down To Earth](https://www.downtoearth.org.in/health/new-mobile-app-may-help-in-addressing-heart-disease-in-rural-areas-63888)
- Children and grandchildren are the main digital helpers for older urban Indians. — [Outlook Money / HelpAge](https://www.outlookmoney.com/amp/story/news/digital-divide-among-elderly-66-find-digital-tools-too-confusing)

### Inferences
- Stigma is the main adoption risk. A device that looks medical or signals illness ("I'm a heart patient") may be rejected the way hearing aids are. A bedside unit that looks like an ordinary household object, or a wearable that looks like a watch or locket, is likely more acceptable. This is a hypothesis drawn from the hearing-aid evidence.
- Route engagement through people the patient already trusts (family members, the ASHA, the treating doctor) rather than expecting the patient to engage with the device on their own.
- Voice/IVR is a proven channel for low-literacy patients in Indian deployments.

### Gaps
- No Indian study found that reports abandonment rates for wearables or remote-monitoring devices among the elderly.
- No outcome data found from Indian HF telemonitoring at home in rural settings.

## 6. Wearable abandonment in older adults (general evidence)

### Takeaway
Abandonment is fast and common. About 1 in 3 tracker users of all ages stop within 6 months, and one report suggests adults aged 70+ may stop within about 2 weeks. Continued use depends on seeing lasting value, having social support and motivation. Abandonment follows technology limitations and "awareness without change".

### Cited Findings
- About 1 in 3 activity-tracker users of all adult ages stop within 6 months of purchase. Length of use correlates with age, and adults 70+ were reported to quit in about 2 weeks. — [Kononova et al., JMIR mHealth uHealth 2019](https://mhealth.jmir.org/2019/4/e9832)
- Continued use depends on recognising the long-term benefits, social support and internal motivation. Non-adoption or relapse follows technology limitations, or gaining awareness of activity without changing behaviour. — [Kononova et al., 2019](https://mhealth.jmir.org/2019/4/e9832)
- In a one-year follow-up case study, criticisms raised at the start of use persisted over the long term. Objective data and reminders supported continued use, and everyday use was mostly passive. — [Schlomann, Gerontechnology](https://journal.gerontechnology.org/currentIssueContent.aspx?aid=2501)
- Long-term older users were more likely to wear the device daily, use more of its functions, exercise more, have more education and have no chronic conditions. — [MSU study](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Factors-Associated-with-Older-Adults-Long-Term-Use-of-Wearable-Activity-Trackers.pdf)

### Inferences
- An HF patient is the opposite of the "long-term user" profile: chronic illness, often low education, older. Expect abandonment risk to be higher than the general figures.
- Problems at first contact (discomfort, confusing charging) persist, so the first-night experience must be painless.
- Mostly passive use is the realistic target. The device should need no daily interaction beyond wearing or docking. A contactless bedside sensor removes the wear-compliance problem entirely but brings back the shared-bed and relocation problems from Section 1. A hybrid (bedside primary, wearable optional) is worth considering.
- Caregiver-facing value (the family gets reassurance and an SMS) may sustain use better than patient-facing value, because it creates social support.

### Gaps
- Most abandonment evidence comes from fitness trackers in high-income countries. No evidence found for medical wearables worn at night by HF patients in LMICs.
- The cited "70+ quit in about 2 weeks" figure is a secondary citation inside Kononova et al. The primary source was not checked.
