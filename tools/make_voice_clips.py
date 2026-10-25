"""VOICE CLIPS -> firmware/hridaymitra_stool/voice_clips.h (8-bit, 8 kHz mono, stored in flash, played on DAC2).

Recorded human clips win: put WAV files named <clip>.wav in firmware/voice/<lang>/ (e.g. hi/welcome.wav, a family
member or ASHA reading the Hindi lines below). Missing clips are made with Windows' offline speech engine (English).
Run:  python tools/make_voice_clips.py [--lang hi]
"""
import argparse, pathlib, subprocess, tempfile, wave
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
RATE = 8000
CLIPS = {  # name: (English, Hindi line for a human recording)
    "welcome": ("Namaste. Please sit on the stool and keep still.", "नमस्ते। स्टूल पर बैठिए और स्थिर रहिए।"),
    "retry": ("I could not read your weight. Please sit again.", "वज़न नहीं मिला। कृपया फिर से बैठिए।"),
    "feet_hands": ("Put both bare feet on the plates and hold both handles.", "दोनों नंगे पैर प्लेट पर रखिए और दोनों हैंडल पकड़िए।"),
    "replace_feet": ("Please place your feet flat on the plates again.", "कृपया पैर फिर से प्लेट पर सीधे रखिए।"),
    "finger": ("Now put your finger on the light and hold still.", "अब उंगली रोशनी पर रखिए और हिलिए मत।"),
    "q_breath": ("Were you more breathless today? Red for yes, green for no.", "क्या आज साँस ज़्यादा फूली? हाँ के लिए लाल, नहीं के लिए हरा।"),
    "q_pillow": ("Did you need extra pillows last night? Red for yes, green for no.", "क्या रात में ज़्यादा तकिए लगे? हाँ लाल, नहीं हरा।"),
    "q_tablets": ("Did you take your tablets today? Red for yes, green for no.", "क्या आज दवा ली? हाँ लाल, नहीं हरा।"),
    "walk": ("It is Sunday walk test day. When you are ready, walk at your usual pace for six minutes, wearing the amulet.",
             "आज रविवार, चलने की जाँच का दिन है। ताबीज़ पहनकर अपनी आम चाल से छह मिनट चलिए।"),
    "use_switch": ("The stool is on charge. Please move the switch to USE, then press green.",
                   "स्टूल चार्ज पर है। स्विच को यूज़ पर कीजिए, फिर हरा दबाइए।"),
    "lift_left": ("Your left foot is not touching its plate. Please put both feet flat.", "बायाँ पैर प्लेट पर नहीं है। दोनों पैर सीधे रखिए।"),
    "lift_right": ("Your right foot is not touching its plate. Please put both feet flat.", "दायाँ पैर प्लेट पर नहीं है। दोनों पैर सीधे रखिए।"),
    "stand": ("Now please stand up and step off.", "अब खड़े होकर उतर जाइए।"),
    "green": ("All fine today. Thank you.", "आज सब ठीक है। धन्यवाद।"),
    "amber": ("Some signs changed. Please check again tomorrow.", "कुछ बदलाव दिखे। कल फिर जाँच कीजिए।"),
    "red": ("Warning signs. A message is going to your family and ASHA.", "चेतावनी। परिवार और आशा दीदी को संदेश जा रहा है।"),
    "learning": ("I am still learning your normal.", "मैं अभी आपका सामान्य सीख रहा हूँ।"),
    "sos": ("Help message sent to your family and ASHA.", "मदद का संदेश परिवार और आशा को भेजा गया।"),
    "guest": ("I do not recognise you. Nothing was saved.", "मैं आपको नहीं पहचानता। कुछ सेव नहीं हुआ।"),
    "tip_tablets": ("Tablets were missed this week. Keep them in the drawer and take them after the check-in.",
                    "इस हफ्ते दवा छूटी। दवा दराज़ में रखिए और जाँच के बाद लीजिए।"),
    "tip_infection": ("Pulse and breathing are up but fluid is steady. This may be an infection. Please see the doctor.",
                      "नब्ज़ और साँस बढ़ी है पर पानी नहीं। यह संक्रमण हो सकता है। डॉक्टर को दिखाइए।"),
    "tip_salt": ("Weight went up but the legs look normal. Yesterday's food may have been salty.",
                 "वज़न बढ़ा पर पैर ठीक हैं। कल का खाना नमकीन रहा होगा।"),
    "tip_fluid": ("Fluid is building. Drink only what your doctor allows and avoid salty food.",
                  "पानी जमा हो रहा है। डॉक्टर जितना कहें उतना ही पिएँ, नमक कम करें।"),
}
import re as _re
_cfg = (ROOT / "firmware/hridaymitra_stool/config.h").read_text(encoding="utf8")
for _name, _key in (("plan_amber", "PLAN_AMBER"), ("plan_red", "PLAN_RED")):     # the doctor's plan, from config.h
    CLIPS[_name] = (_re.search(rf'#define {_key}\s+"([^"]+)"', _cfg).group(1), "(doctor records this line)")


def tts(text, path):
    ps = ("Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
          "$f = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(8000, [System.Speech.AudioFormat.AudioBitsPerSample]::Eight, "
          "[System.Speech.AudioFormat.AudioChannel]::Mono); $s.Rate = -1; "
          f"$s.SetOutputToWaveFile('{path}', $f); $s.Speak(\"{text}\"); $s.Dispose()")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True, capture_output=True)


def load(path):
    """Any WAV -> uint8 at 8 kHz (mono mix, linear resample, peak-normalised)."""
    with wave.open(str(path)) as w:
        n, ch, sw, fr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = np.frombuffer(w.readframes(n), {1: np.uint8, 2: np.int16}[sw]).astype(float)
    x = (raw - 128) / 128 if sw == 1 else raw / 32768
    x = x.reshape(-1, ch).mean(axis=1)
    x = np.interp(np.arange(0, len(x), fr / RATE), np.arange(len(x)), x)
    nz = np.flatnonzero(np.abs(x) > 0.02)                 # trim silence at both ends
    x = x[max(0, nz[0] - 400): nz[-1] + 400] if len(nz) else x
    x = 0.9 * x / max(1e-6, np.abs(x).max())
    return np.clip(np.round(x * 127 + 128), 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--lang", default="en"); a = ap.parse_args()
    rec = ROOT / "firmware" / "voice" / a.lang
    out = ["// Generated by tools/make_voice_clips.py. Do not edit.", "#pragma once", "#include <pgmspace.h>",
           "struct Clip { const uint8_t* data; uint32_t len; uint16_t rate; };"]
    total = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, (en, _) in CLIPS.items():
            src = rec / f"{name}.wav"
            if not src.exists():
                src = pathlib.Path(tmp) / f"{name}.wav"; tts(en, src)
            x = load(src); total += len(x)
            rows = ",".join(map(str, x))
            out += [f"const uint8_t {name}_data[] PROGMEM = {{{rows}}};",
                    f"const Clip CLIP_{name.upper()} = {{{name}_data, {len(x)}, {RATE}}};"]
    (ROOT / "firmware/hridaymitra_stool/voice_clips.h").write_text("\n".join(out) + "\n", encoding="utf8")
    print(f"{len(CLIPS)} clips, {total / RATE:.1f} s, {total / 1024:.0f} KB of flash")


if __name__ == "__main__":
    main()
