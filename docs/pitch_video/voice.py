"""Voice-over for the pitch video, and the timeline the visuals follow.

python voice.py VOICE.onnx OUT_DIR
  -> OUT_DIR/voice.wav (the whole narration, placed on the timeline)
  -> timing.js (segment start/end and the start of every sentence, read by index.html and music.py)

Voice: Piper (offline neural TTS), e.g. en-us-ryan-high from github.com/rhasspy/piper/releases (v0.0.2).
Spellings below are phonetic on purpose ("Hriday Mitra", "Asha", "Kai Cad") so the voice says them right.
"""
import json, pathlib, subprocess, sys, wave
import numpy as np

# (segment, minimum seconds on screen, sentences)
SCRIPT = [
    ("meet", 8, ["Meet Ramesh.", "He is sixty-two, he lives with his daughter's family, and he has heart failure."]),
    ("silent", 13, ["For days before a hospital visit, fluid quietly builds up in his legs and lungs.",
                    "He gains a little weight, breathes a little faster, and sleeps on extra pillows.",
                    "Nobody notices, until it becomes an emergency."]),
    ("challenge", 12, ["Dare to Dream Ventures asked us to catch this at home, days early, with almost no effort from the patient.",
                       "Under two minutes a day, for someone who may not read, through power cuts and weak internet, for under five thousand rupees."]),
    ("why", 9, ["A scale alone catches about one in three episodes, and patches are uncomfortable all day.",
                "But Ramesh already sits in his chair, every day."]),
    ("logo", 6, ["This is Hriday Mitra.", "Your chair. One simple check-in."]),
    ("product", 16, ["A weighing platform slides under the chair he already owns, with four load cells and four steel foot plates.",
                     "On his lap, a sensor bar with hand strips, a fingertip cradle for pulse and oxygen, and three big buttons.",
                     "Around his neck, the Kavach amulet watches his breathing and sleep at night."]),
    ("demo", 28, ["Every morning after tea, Ramesh sits down, and the device greets him in Hindi.",
                  "Feet on the plates. Hands on the bar.",
                  "A tiny, safe current measures the fluid in his legs and chest, at three frequencies.",
                  "The fingertip sensor reads his pulse and oxygen.",
                  "Then three simple questions, answered with a tick or a cross.",
                  "Ninety seconds later, a light. Green means all is well."]),
    ("proto", 12, ["And this is not just an animation.", "Here is our first breadboard prototype, on an ordinary plastic chair.",
                   "The sensor board rests on the lap, the status light glows green, and the amulet hangs on a cord around the neck."]),
    ("alert", 22, ["One week, Ramesh misses his tablets. On day thirty-four, the light turns amber.",
                   "By day forty-one, his weight, leg fluid and night breathing all agree. Red. An S M S reaches his daughter, explaining why.",
                   "If nobody responds, it climbs to family, the Asha worker, then the doctor. His care begins four days before the hospital."]),
    ("simintro", 6, ["We could not test on patients. So we simulated everything with free tools, and tried hard to break it."]),
    ("ltspice", 12, ["In L T spice, the full analog front end runs on a model of the human body.",
                     "At every test point it reads five hundred seventy-eight point four ohms, against five hundred seventy-eight point five exact. Every path is within five hundredths of a percent."]),
    ("mc", 12, ["Then a Monte Carlo of a hundred virtual devices, built from cheap five percent parts, on random bodies.",
                "Ninety-nine percent of readings land within two percent, and it caught our own bug. The bias resistors had to go from one, to ten mega-ohms."]),
    ("spectro", 7, ["Three frequencies and a Cole fit separate real fluid from foot position and skin temperature."]),
    ("safety", 12, ["Mains hum falls from eighteen percent error to under point two, with a Goertzel filter.",
                    "Every single circuit fault stays at least twelve times inside the I E C medical safety limit, and a charge-or-use switch cuts charger leakage to almost nothing."]),
    ("kicad", 8, ["The custom circuit is a Kai Cad schematic, generated from code with zero rule errors, beside a full block diagram and power budget."]),
    ("wokwi", 11, ["The real firmware runs on an emulated E S P thirty-two in Wok-wee, with a virtual patient we can make sick.",
                   "Over an emulated month, all twenty-six firmware checks pass."]),
    ("parity", 7, ["The same engine runs in Python, in C plus plus on the chip, and in the phone app, and they agree on every one of three thousand two hundred thirty-one days."]),
    ("data", 13, ["We built two hundred synthetic patients to the problem statement's rules, and a thousand messier ones, with every parameter sourced, or marked as an assumption.",
                  "On fifteen real heart-failure E C G recordings from PhysioNet, heart rate is off by a median of just point one five beats per minute."]),
    ("robust", 8, ["We pushed every assumption low and high. In all fifty-two worlds it still beats the weight rule, and it survives fourteen of fifteen stress tests."]),
    ("results", 12, ["On a thousand external patients, Hriday Mitra catches eighty-six percent of worsening episodes, against thirty-one for the weight rule.",
                     "The engine on the chip raises about nine times fewer false alarms, and warns about three days early, with no internet at all."]),
    ("app", 9, ["Family, Asha worker and doctor share the Saathee app in ten Indian languages. And the whole home unit costs about four thousand four hundred rupees."]),
    ("close", 11, ["Hriday Mitra.", "Ninety seconds a day, so the family knows, days before the hospital.",
                   "A monitoring tool, not a diagnosis. Tested on synthetic data, and now on its first breadboard prototype."]),
]
LEAD, GAP, TAIL = 0.6, 0.3, 0.8
GAPS = {"product": 0.6, "demo": 1.3, "alert": 0.6, "ltspice": 0.5, "mc": 0.5, "data": 0.5}   # room for the visuals to land


def synth(model, text, path):
    subprocess.run([sys.executable, "-m", "piper", "-m", model, "-f", str(path), "--length-scale", "1.06",
                    "--sentence-silence", "0"], input=text.encode(), check=True, capture_output=True)
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768, w.getframerate()


def main(model, out):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    clips, segs, cues, t = [], {}, {}, 0.0
    for seg, min_d, lines in SCRIPT:
        s, c = t, t + LEAD
        for i, line in enumerate(lines):
            a, sr = synth(model, line, out / f"{seg}_{i}.wav")
            g = GAPS.get(seg, GAP)
            cues[f"{seg}:{i}"] = round(c, 3); clips.append((c, a, sr)); c += len(a) / sr + g
        t = max(c - g + TAIL, s + min_d)
        segs[seg] = [round(s, 3), round(t, 3)]
    total = round(t, 3)
    sr = clips[0][2]; voice = np.zeros(int(total * sr) + sr)
    for c, a, _ in clips:
        i = int(c * sr); voice[i:i + len(a)] += a
    with wave.open(str(out / "voice.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(voice, -1, 1) * 32767).astype(np.int16).tobytes())
    T = {"total": total, "segs": segs, "cues": cues}
    pathlib.Path(__file__).with_name("timing.js").write_text("window.TIMING=" + json.dumps(T) + ";\n")
    print(json.dumps({k: v for k, v in segs.items()}), "total", total)


if __name__ == "__main__":
    main(*sys.argv[1:3])
