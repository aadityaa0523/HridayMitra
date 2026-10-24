"""Schematic checks: generated netlist routes every path as the build guide says, values equal LTspice. Run: python -m pytest tests -q"""
import copy, pathlib, subprocess, sys
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
if not pathlib.Path("C:/Program Files/KiCad/9.0/bin/kicad-cli.exe").exists():
    pytest.skip("KiCad 9 not installed", allow_module_level=True)
import make_schematic as M

NET = M.OUT / "hridaymitra.net"


@pytest.fixture(scope="module")
def nets():
    subprocess.run([sys.executable, str(ROOT / "tools/make_schematic.py")], check=True, capture_output=True)
    return M.netlist_nets(NET)


def test_paths_match_guide(nets):
    assert M.check_paths(nets) == []


def test_path_check_catches_a_swapped_wire(nets):
    bad = copy.deepcopy(nets)
    bad["RF_HEEL"].remove("U5.1"); bad["LF_HEEL"].add("U5.1")      # sense- of path 00 wired to the wrong heel
    assert M.check_paths(bad)


def test_values_match_ltspice():
    assert M.check_against_ltspice() == []


def test_erc_clean(nets):
    import json
    erc = json.loads((M.OUT / "erc.json").read_text())
    assert sum(len(s.get("violations", [])) for s in erc["sheets"]) == 0
