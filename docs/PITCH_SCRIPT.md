# 5-minute pitch script (numbers match the deck; regenerate with python tools/make_docs.py)

| Time | Slide | Say |
|---|---|---|
| 0:00 | 1 | "Every heart-failure admission starts days earlier, silently. HridayMitra is a 90-second daily check-in that warns the family 3 days before the hospital, offline, for ₹4,330." |
| 0:30 | 2 | The weight-scale rule catches about a third and cries wolf; elders don't wear patches; rural homes have power cuts and 2G. |
| 1:00 | 3 | Stool + amulet + care loop. Point at the block diagram: 8 electrodes, legs and chest fluid. |
| 1:45 | 4 | Personal normal, two witnesses, reasons. Read the SMS aloud. |
| 2:15 | 5 | Results: 66% vs 40%, 0.06 vs 0.53 false alerts. ML catches more but with 3-5x the false alarms. |
| 2:50 | Demo | `python run.py demo`: patient P0022, slide to the red day, tick "guest" and "toe ring": the light does not lie. |
| 3:30 | 6 | We tried to break it: 52/52 wrong-assumption worlds still beat the rule; care loop 92%. |
| 4:00 | 7 | Engineering: the Monte Carlo found our own bug (1 MΩ → 10 MΩ); C++ engine 100% identical on the ESP32. |
| 4:30 | 8-9 | Cost, model, honest limits, the ask. |

Questions to expect: lungs? (chest segment = weak, trend over a week; the stronger lung signals are night breathing and orthopnea). Pacemaker? (impedance off by setting, no magnets). Why not ML? (alarm fatigue; hybrid is the next step). Real data? (synthetic by PS rule; BIDMC real ECG for heart rate).
