"""STOOL BRIDGE: joins the real stool to the laptop dashboard. The stool decides on its own (offline engine);
the bridge only logs its check-ins to data/live/<patient>.csv, which the demo shows live.

  python tools/stool_bridge.py --port COM5                 # log real check-ins (press the green button on the stool)
  python tools/stool_bridge.py --port COM5 --replay P0022  # hardware-in-the-loop: send a synthetic patient's days to
                                                           # the stool and check its lights equal the Python engine
  python tools/stool_bridge.py --simulate P0022            # no hardware: write that patient's days as if they came live
"""
import argparse, json, pathlib, sys, time
import numpy as np
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import alert_engine as A

LIVE = ROOT / "data" / "live"
COLS = ["weight_kg", "leg_z_ohm", "trunk_z_ohm", "pulse_bpm", "night_rr", "spo2", "activity_min", "standup_s", "leg_ewi",
        "breathless", "orthopnea", "night_situps"]                 # the stool's "day" command order (engine_core.h)
OUT_COLS = ["patient_id", "day", "weight_kg", "leg_z_ohm", "trunk_z_ohm", "leg_ewi", "pulse_bpm", "spo2", "standup_s", "breathless",
            "orthopnea", "took_pills", "quality", "amulet_worn", "night_rr", "night_situps", "activity_min", "light", "why"]
T = json.loads((ROOT / "engine/frozen_params_v3.json").read_text())["T"]


def append(row):
    """Add one check-in to the patient's live log (creates it on the first day)."""
    LIVE.mkdir(parents=True, exist_ok=True)
    f = LIVE / f"{row['patient_id']}.csv"
    day = len(pd.read_csv(f)) if f.exists() else 0
    rec = {c: row.get(c, np.nan) for c in OUT_COLS} | {"day": day, "took_pills": row.get("took_pills", 1),
                                                      "quality": row.get("quality", 1), "amulet_worn": 1}
    pd.DataFrame([rec])[OUT_COLS].to_csv(f, mode="a", header=not f.exists(), index=False)
    return day


def synthetic(pid):
    for folder in ("data/processed/realworld", "data/processed"):
        f = pd.read_csv(ROOT / folder / "daily_features.csv")
        g = f[f.patient_id == pid]
        if len(g):
            return g.reset_index(drop=True)
    sys.exit(f"{pid} not found in the synthetic cohorts")


def parse(line):
    """The stool prints C's 'nan' for a missing number; JSON wants NaN."""
    return json.loads(line.replace(":nan", ":NaN").replace(":-nan", ":NaN"))


def fmt(v):
    return "nan" if pd.isna(v) else f"{v:.4g}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port"); ap.add_argument("--replay"); ap.add_argument("--simulate")
    ap.add_argument("--delay", type=float, default=0.3, help="seconds between simulated days")
    a = ap.parse_args()

    if a.simulate:                                         # laptop only: replay a patient as a live feed
        g = synthetic(a.simulate)
        (LIVE / f"{a.simulate}.csv").unlink(missing_ok=True)
        lights = A.lights(A.scores(g), T)
        for t in range(len(g)):
            sc = A.scores(g.iloc[:t + 1])[-1]
            why = "; ".join(A.explain(g, sc)[1])
            append(g.iloc[t].to_dict() | {"patient_id": a.simulate, "light": int(lights[t]), "why": why})
            print(f"day {t:3d}  light {['green', 'amber', 'RED'][lights[t]]:5s}  {why}", flush=True)
            time.sleep(a.delay)
        return

    import serial                                          # pyserial
    port = serial.Serial(a.port, 115200, timeout=2)
    time.sleep(2)
    if a.replay:                                           # hardware-in-the-loop parity check
        g = synthetic(a.replay)
        want = A.lights(A.scores(g), T)
        port.write(b"reset\n"); port.readline()
        got = []
        for t in range(len(g)):
            port.write(("day " + ",".join(fmt(g.iloc[t][c]) for c in COLS) + "\n").encode())
            while True:
                line = port.readline().decode(errors="ignore").strip()
                if line.startswith("{") and '"checkin"' in line:
                    got.append(parse(line)["light"]); break
                if not line:
                    sys.exit(f"no answer from the stool on day {t}")
        agree = float(np.mean(np.array(got) == want))
        print(f"stool vs Python engine: {agree:.1%} of {len(got)} days agree")
        sys.exit(0 if agree == 1 else 1)

    print(f"listening on {a.port}; press the green button on the stool (Ctrl+C to stop)")
    while True:                                            # log real check-ins
        line = port.readline().decode(errors="ignore").strip()
        if not line.startswith("{"):
            continue
        msg = parse(line)
        if msg.get("t") == "checkin":
            day = append({k: (np.nan if v is None else v) for k, v in msg.items()} | {"patient_id": msg["id"]})
            print(f"day {day}: light {msg['light']}  {msg.get('why', '')}")
        elif msg.get("t") == "reply":
            print(f"care loop: reply {msg['digit']} from {msg['from']}")


if __name__ == "__main__":
    main()
