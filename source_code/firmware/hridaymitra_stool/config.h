// Edit these before flashing. Phone numbers in international format.
#pragma once
#define PATIENT_ID   "P001"               // first user
#define PATIENT_ID2  "P002"               // second user on the same stool (enrol with "enroll 2" over USB)
#define FAMILY1      "+910000000001"
#define FAMILY2      "+910000000002"
#define ASHA         "+910000000003"
#define DOCTOR       "+910000000004"      // PHC doctor or helpline

// The doctor's own sick-day plan (spoken by the stool and sent to the family). Placeholders, not medical advice.
// After editing, run: python tools/make_voice_clips.py
#define PLAN_AMBER "Your doctor's plan: cut salt today, weigh again tomorrow, and call the ASHA if you feel worse."
#define PLAN_RED   "Your doctor's plan: take the extra water tablet your doctor prescribed for bad days, and visit the PHC today."

// care-loop timers (minutes), as simulated in sim/careloop/careloop.py
#define ESC_FAMILY2_MIN  30
#define ESC_ASHA_MIN     120
#define ESC_DOCTOR_MIN   360
#define SMS_RETRY_MIN    10
#define NUDGE_HOUR       11               // remind the family if nobody checked in by this hour
#define SELFTEST_HOUR    7                // daily self-test; problems go to the ASHA as "service" SMS
#define SUMMARY_HOUR     18               // Sunday summary to the ASHA
#define STEP_LENGTH_M    0.5f             // walk-test distance = steps x this. ASHA sets it once: 10 m / steps counted over 10 m

// HX711 scale: counts per kg. Calibrate with "cal <kg>" over USB serial with a known weight on the stool.
#ifdef HM_WOKWI                           // Wokwi simulation build (see wokwi/README.md)
#define DEFAULT_COUNTS_PER_KG  105.0f     // Wokwi load cell = one of the 4 corner cells (420 counts/kg / 4)
#define MINUTE_MS              1000UL     // 1 s of simulation = 1 minute (the SIM800L chip's clock runs 60x)
#else
#define DEFAULT_COUNTS_PER_KG  21000.0f
#define MINUTE_MS              60000UL
#endif
