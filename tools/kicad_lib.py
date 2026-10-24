"""Read symbols from the installed KiCad 9 libraries: raw text (to embed in a schematic) and pin positions."""
import pathlib, re

LIBDIR = pathlib.Path(r"C:\Program Files\KiCad\9.0\share\kicad\symbols")


def parse(text, i=0):
    """Tiny s-expression parser: returns (tree, next index). Strings keep their quotes stripped."""
    out = []
    while i < len(text):
        c = text[i]
        if c == "(":
            sub, i = parse(text, i + 1)
            out.append(sub)
        elif c == ")":
            return out, i + 1
        elif c == '"':
            j = i + 1
            while text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i + 1:j]); i = j + 1
        elif c.isspace():
            i += 1
        else:
            j = i
            while j < len(text) and text[j] not in '()" \t\r\n':
                j += 1
            out.append(text[i:j]); i = j
    return out, i


def block(text, name):
    """Raw text of the top-level (symbol "name" ...) in a library file."""
    i = text.index(f'\t(symbol "{name}"')
    depth, j = 0, i
    while True:
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                return text[i:j + 1].strip()
        elif text[j] == '"':
            j += 1
            while text[j] != '"':
                j += 2 if text[j] == "\\" else 1
        j += 1


class Symbol:
    def __init__(self, lib, name):
        text = (LIBDIR / f"{lib}.kicad_sym").read_text(encoding="utf8")
        raw = block(text, name)
        self.lib_id = f"{lib}:{name}"
        self.raw = raw.replace(f'(symbol "{name}"', f'(symbol "{self.lib_id}"', 1)
        tree = parse(raw)[0][0]
        assert not any(isinstance(x, list) and x[0] == "extends" for x in tree), f"{name} is derived"
        self.pins = []                                     # dict(unit, number, name, type, x, y, angle, hidden)
        for sub in tree:
            if isinstance(sub, list) and sub[0] == "symbol":
                unit = int(sub[1].rsplit("_", 2)[1])
                for p in sub:
                    if isinstance(p, list) and p[0] == "pin":
                        at = next(x for x in p if isinstance(x, list) and x[0] == "at")
                        nm = next(x for x in p if isinstance(x, list) and x[0] == "name")[1]
                        nu = next(x for x in p if isinstance(x, list) and x[0] == "number")[1]
                        hidden = "hide" in p or any(isinstance(x, list) and x[:2] == ["hide", "yes"] for x in p)
                        self.pins.append(dict(unit=unit, number=nu, name=nm, type=p[1], x=float(at[1]), y=float(at[2]),
                                              angle=float(at[3]) if len(at) > 3 else 0.0, hidden=hidden))
        self.units = sorted({p["unit"] for p in self.pins if p["unit"] > 0}) or [1]


if __name__ == "__main__":
    for lib, n in [("Analog_Switch", "CD4052B"), ("Analog_Switch", "CD4053B"), ("Amplifier_Instrumentation", "INA128"),
                   ("Amplifier_Operational", "LM2904"), ("Regulator_Linear", "AP1117-15"), ("RF_Module", "ESP32-WROOM-32")]:
        s = Symbol(lib, n)
        print(n, "units", s.units)
        print("   ", [(p["unit"], p["number"], p["name"], p["type"][:5], "H" if p["hidden"] else "") for p in s.pins])
