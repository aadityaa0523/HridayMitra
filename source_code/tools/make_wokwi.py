"""WOKWI PROJECTS from the real firmware: wokwi/stool and wokwi/amulet.

The stool project wires an ESP32 DevKitC to Wokwi's HX711 + load cell, buttons, drawer switch, LEDs, and three custom
chips written for HridayMitra (wokwi/chips): the virtual patient with the 8-electrode impedance front end (sliders for
leg / chest fluid, lifted foot, mains hum), a MAX30102 (pulse, SpO2, finger) and a SIM800L with a phone screen (SMS
appear on it; sliders send replies, missed calls, outages). The sketch is the production firmware built with
-DHM_WOKWI (no Bluetooth, 1 s = 1 minute, 20 days of history preloaded, beeps instead of voice).
Run:  python tools/make_wokwi.py [--no-compile]      (also builds the chips to WebAssembly and both firmwares)
Out:  wokwi/stool/*, wokwi/amulet/* (open in wokwi.com or the Wokwi VS Code extension; see wokwi/README.md)
"""
import json, pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
WK, FW, CHIPS = ROOT / "wokwi", ROOT / "firmware", ROOT / "wokwi" / "chips"
ARDUINO = shutil.which("arduino-cli") or str(pathlib.Path.home() / "tools/arduino/arduino-cli.exe")
sys.path.insert(0, str(ROOT / "tools"))


def wire(a, b, color="green"):
    return [a, b, color, []]


def stool_diagram():
    parts = [                                          # laid out like the product: patient left, stool middle, care loop right
        {"type": "board-esp32-devkit-c-v4", "id": "esp", "top": 0, "left": 0, "attrs": {}},
        {"type": "chip-hm-body", "id": "body", "top": -150, "left": -360, "attrs": {}},
        {"type": "chip-hm-max30102", "id": "finger", "top": 230, "left": -330, "attrs": {}},
        {"type": "chip-hm-monitor", "id": "monitor", "top": -290, "left": 200, "attrs": {}},
        {"type": "chip-hm-sim800l", "id": "gsm", "top": -40, "left": 330, "attrs": {}},
        {"type": "wokwi-hx711", "id": "cell", "top": 240, "left": 220, "attrs": {"type": "50kg"}},
        {"type": "wokwi-pushbutton", "id": "btnG", "top": 330, "left": -140, "attrs": {"color": "green", "label": "GO / NO"}},
        {"type": "wokwi-pushbutton", "id": "btnR", "top": 330, "left": -40, "attrs": {"color": "red", "label": "YES"}},
        {"type": "wokwi-pushbutton", "id": "btnS", "top": 330, "left": 60, "attrs": {"color": "yellow", "label": "SOS"}},
        {"type": "wokwi-slide-switch", "id": "drawer", "top": 335, "left": 160, "attrs": {"label": "tablet drawer"}},
    ]
    conns = [wire("esp:TX", "$serialMonitor:RX", ""), wire("esp:RX", "$serialMonitor:TX", ""),
             wire("monitor:RX", "esp:TX", "gold"), wire("monitor:VCC", "esp:3V3", "red"), wire("monitor:GND", "esp:GND.1", "black"),
             wire("body:VCC", "esp:3V3", "red"), wire("body:GND", "esp:GND.1", "black"), wire("body:EXC", "esp:25", "orange"), wire("body:CAL", "esp:12", "violet"), wire("body:SEL", "esp:18"),
             wire("body:S0", "esp:33"), wire("body:S1", "esp:27"), wire("body:OUT", "esp:35", "orange"),
             wire("finger:VCC", "esp:3V3", "red"), wire("finger:GND", "esp:GND.1", "black"),
             wire("finger:SDA", "esp:21", "blue"), wire("finger:SCL", "esp:22", "purple"),
             wire("gsm:VCC", "esp:5V", "red"), wire("gsm:GND", "esp:GND.2", "black"),
             wire("gsm:RX", "esp:17", "blue"), wire("gsm:TX", "esp:16", "purple"),
             wire("cell:VCC", "esp:3V3", "red"), wire("cell:GND", "esp:GND.2", "black"),
             wire("cell:DT", "esp:32", "blue"), wire("cell:SCK", "esp:14", "purple"),
             wire("btnG:1.l", "esp:4"), wire("btnG:2.l", "esp:GND.1", "black"),
             wire("btnR:1.l", "esp:5"), wire("btnR:2.l", "esp:GND.1", "black"),
             wire("btnS:1.l", "esp:15"), wire("btnS:2.l", "esp:GND.1", "black"),
             wire("drawer:2", "esp:VP"), wire("drawer:1", "esp:GND.2", "black"), wire("drawer:3", "esp:3V3", "red")]
    for k, (pin, color, label) in enumerate([("13", "green", "OK"), ("23", "yellow", "CHECK AGAIN"), ("2", "red", "ALERT"),
                                             ("19", "blue", "seat vibration")]):
        led, res = f"led{k}", f"r{k}"
        parts += [{"type": "wokwi-led", "id": led, "top": 40 + 50 * k, "left": 200, "attrs": {"color": color, "label": label}},
                  {"type": "wokwi-resistor", "id": res, "top": 75 + 50 * k, "left": 150, "rotate": 90, "attrs": {"value": "220"}}]
        conns += [wire(f"esp:{pin}", f"{led}:A", color), wire(f"{led}:C", f"{res}:1", "black"), wire(f"{res}:2", "esp:GND.3", "black")]
    return {"version": 1, "author": "HridayMitra", "editor": "wokwi", "parts": parts, "connections": conns, "dependencies": {}}


def amulet_diagram():
    return {"version": 1, "author": "HridayMitra", "editor": "wokwi",
            "parts": [{"type": "board-esp32-c3-devkitm-1", "id": "esp", "top": 0, "left": 0, "attrs": {}},
                      {"type": "wokwi-mpu6050", "id": "imu", "top": -120, "left": 150, "attrs": {}},
                      {"type": "wokwi-pushbutton", "id": "sos", "top": 160, "left": 150, "attrs": {"color": "red", "label": "SOS"}}],
            "connections": [wire("esp:TX", "$serialMonitor:RX", ""), wire("esp:RX", "$serialMonitor:TX", ""),
                            wire("imu:VCC", "esp:3V3.1", "red"), wire("imu:GND", "esp:GND.1", "black"),
                            wire("imu:SDA", "esp:8", "blue"), wire("imu:SCL", "esp:9", "purple"),
                            wire("sos:1.l", "esp:3"), wire("sos:2.l", "esp:GND.2", "black")],
            "dependencies": {}}


def beep_clips():
    """Wokwi does not play the DAC: tiny 0.1 s beeps with the same names keep the sketch small."""
    from make_voice_clips import CLIPS
    import re
    cfg = (FW / "hridaymitra_stool/config.h").read_text(encoding="utf8")
    names = list(CLIPS) + [n for n in ("plan_amber", "plan_red") if n not in CLIPS and re.search(n.upper(), cfg)]
    beep = ",".join("200" if (i // 4) % 2 else "56" for i in range(800))
    out = ["// Wokwi build: 0.1 s beeps instead of voice clips (generated by tools/make_wokwi.py)", "#pragma once",
           "struct Clip { const uint8_t* data; uint32_t len; uint16_t rate; };", f"const uint8_t beep_data[] PROGMEM = {{{beep}}};"]
    out += [f"const Clip CLIP_{n.upper()} = {{beep_data, 800, 8000}};" for n in names]
    return "\n".join(out) + "\n"


def build_chips(dst):
    """Compile each chip to WebAssembly the way Wokwi does (needs zig: pip install ziglang)."""
    for c in sorted(CHIPS.glob("*.chip.c")):
        name = c.name.replace(".chip.c", "")
        subprocess.run([sys.executable, "-m", "ziglang", "cc", "--target=wasm32-wasi", "-O2", "-nostartfiles",
                        "-Wl,--import-memory", "-Wl,--export-table", "-Wl,--no-entry", "-Wl,--export-dynamic",
                        "-I", str(CHIPS), str(c), "-o", str(dst / f"{name}.chip.wasm")], check=True, capture_output=True)
        print("chip", name, "-> wasm", (dst / f"{name}.chip.wasm").stat().st_size, "bytes")


def compile_fw(project, fqbn):
    src = project / "build_src" / "sketch"
    src.mkdir(parents=True, exist_ok=True)
    for f in project.glob("*.[ih]*"):
        if f.suffix in (".ino", ".h"):
            shutil.copy(f, src / f.name)
    r = subprocess.run([ARDUINO, "compile", "--fqbn", fqbn, "--output-dir", str(project / "build"), str(src)],
                       capture_output=True, text=True)
    print(project.name, "firmware:", next((l for l in r.stdout.splitlines() if "Sketch uses" in l), r.stderr[-800:]))
    shutil.rmtree(project / "build_src")
    return r.returncode == 0


def main():
    stool, amulet = WK / "stool", WK / "amulet"
    for d in (stool, amulet, stool / "chips"):
        d.mkdir(parents=True, exist_ok=True)
    (stool / "sketch.ino").write_text("#define HM_WOKWI 1\n" + (FW / "hridaymitra_stool/hridaymitra_stool.ino").read_text(encoding="utf8"), encoding="utf8")
    for f in ("engine_core.h", "config.h", "app_link.h"):
        shutil.copy(FW / "hridaymitra_stool" / f, stool / f)
    (stool / "voice_clips.h").write_text(beep_clips(), encoding="utf8")
    gfx = (CHIPS / "gfx.inc").read_text(encoding="utf8")
    for f in CHIPS.glob("hm-*.chip.*"):                # the web editor compiles one file per chip: paste gfx.inc in
        if f.suffix == ".json":
            shutil.copy(f, stool / f.name)
        elif f.suffix == ".c":
            (stool / f.name).write_text(f.read_text(encoding="utf8").replace('#include "gfx.inc"', gfx), encoding="utf8")
    (stool / "diagram.json").write_text(json.dumps(stool_diagram(), indent=2), encoding="utf8")
    chips = "\n".join(f"[[chip]]\nname = '{n}'\nbinary = 'chips/{n}.chip.wasm'\n" for n in ("hm-body", "hm-max30102", "hm-sim800l", "hm-monitor"))
    (stool / "wokwi.toml").write_text(f"[wokwi]\nversion = 1\nfirmware = 'build/sketch.ino.merged.bin'\nelf = 'build/sketch.ino.elf'\n\n{chips}", encoding="utf8")
    shutil.copy(FW / "hridaymitra_amulet/walk_core.h", amulet / "walk_core.h")
    (amulet / "sketch.ino").write_text("#define HM_WOKWI 1\n" + (FW / "hridaymitra_amulet/hridaymitra_amulet.ino").read_text(encoding="utf8"), encoding="utf8")
    (amulet / "diagram.json").write_text(json.dumps(amulet_diagram(), indent=2), encoding="utf8")
    (amulet / "wokwi.toml").write_text("[wokwi]\nversion = 1\nfirmware = 'build/sketch.ino.merged.bin'\nelf = 'build/sketch.ino.elf'\n", encoding="utf8")
    if "--no-compile" in sys.argv:
        return
    build_chips(stool / "chips")
    ok = compile_fw(stool, "esp32:esp32:esp32") & compile_fw(amulet, "esp32:esp32:esp32c3:CDCOnBoot=default")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
