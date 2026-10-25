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
    ("meet", 9, ["Meet Ramesh.", "He is sixty-two. He lives with his daughter's family, and he has heart failure."]),
    ("silent", 15, ["Heart failure rarely strikes without warning.",
                    "For days before a hospital visit, fluid quietly builds up in his legs and lungs.",
                    "He gains a little weight. He breathes a little faster. He sleeps on extra pillows.",
                    "But nobody notices, until he cannot breathe, and it becomes an emergency."]),
    ("challenge", 15, ["That is the challenge Dare to Dream Ventures set at Transfinite.",
                       "Spot worsening heart failure at home, days early, with almost no effort from the patient.",
                       "Under two minutes a day. Easy for someone who may not read. Ready for power cuts and weak internet.",
                       "And under five thousand rupees."]),
    ("why", 10, ["A weighing scale alone catches only about one in three of these episodes.",
                 "Patches are uncomfortable to wear all day.",
                 "So we asked, what does Ramesh already do every day?", "He sits in his chair."]),
    ("logo", 7, ["This is Hriday Mitra.", "Your chair. One simple check-in."]),
    ("product", 18, ["A weighing platform slides under the chair he already owns.",
                     "Four load cells measure his weight, and four steel plates touch his bare feet.",
                     "On his lap rests a sensor bar, with hand strips, a fingertip cradle for pulse and oxygen, and three big buttons.",
                     "Around his neck, the Kavach amulet watches his breathing and sleep at night."]),
    ("demo", 30, ["Every morning after tea, Ramesh sits down, and the device greets him in Hindi.",
                  "Feet on the plates. Hands on the bar.",
                  "A tiny, safe current measures the fluid in his legs and chest, at three frequencies.",
                  "The fingertip sensor reads his pulse and oxygen.",
                  "Then three simple questions, answered with a tick or a cross.",
                  "Ninety seconds later, a light. Green means all is well."]),
    ("alert", 26, ["But one week, he misses his tablets.", "On day thirty-four, the light turns amber. Check again tomorrow.",
                   "By day forty-one, his weight, his leg fluid and his night breathing all point the same way.",
                   "The light turns red, and an S M S reaches his daughter, explaining why.",
                   "If nobody responds, it climbs to a second family member, then the Asha worker, then the doctor at the health centre.",
                   "His doctor's plan begins four days before he would have needed a hospital."]),
    ("built", 24, ["Every part of this is designed and simulated.",
                   "A full block diagram, and a Kai Cad schematic of our own sensor circuit.",
                   "L T spice shows the front end measuring within five hundredths of a percent.",
                   "A Monte Carlo of a hundred virtual devices caught our own design bug, before we built anything.",
                   "And the real firmware runs on an emulated E S P thirty-two in Wok-wee, with a virtual patient we can make sick."]),
    ("results", 17, ["On a thousand synthetic patients, Hriday Mitra catches eighty-six percent of worsening episodes.",
                     "That is more than twice the weight rule.",
                     "The engine on the chip raises about nine times fewer false alarms, and warns about three days early, with no internet at all."]),
    ("app", 13, ["The family, the Asha worker and the doctor share the Saathee app, in ten Indian languages.",
                 "And the whole home unit costs about four thousand four hundred rupees."]),
    ("close", 12, ["Hriday Mitra.", "Ninety seconds a day, so the family knows, days before the hospital.",
                   "A monitoring tool, not a diagnosis. Tested on synthetic data, and ready for its first bench build."]),
]
LEAD, GAP, TAIL = 0.7, 0.35, 1.1
GAPS = {"product": 0.9, "demo": 1.5, "alert": 0.8, "built": 0.9, "results": 0.7}   # room for the visuals to land


def synth(model, text, path):
    subprocess.run([sys.executable, "-m", "piper", "-m", model, "-f", str(path), "--length-scale", "1.1",
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
