"""TRUNK (CHEST) PATHS: 8-electrode segmental impedance in LTspice, and whether a small chest-fluid change is visible.

Body model (Cole segments): left/right arm (hand -> shoulder), trunk (shoulder -> pelvis), left/right leg (foot -> pelvis).
Each hand and foot has two electrodes (inject + sense), each with its own contact resistance Rc.
The 74HC4052 path mux (GPIO33/27) picks which pair injects and which pair senses:
    path 1  Z1 = left foot  -> right foot  = legs L + R
    path 2  Z2 = left hand  -> right hand  = arms L + R
    path 3  Z3 = left hand  -> left foot   = arm L + trunk + leg L
    path 4  Z4 = right hand -> right foot  = arm R + trunk + leg R
    trunk   = (Z3 + Z4 - Z1 - Z2) / 2
Ratiometric front end: Z = Rcal x V(body) / V(Rcal). Self-calibrating reference (C2): R5 (120 ohm, any tolerance) in series with
Rcal (100 ohm, 0.1 %); the spare 74HC4053 switch (CAL, GPIO12) taps across Rcal for every reference reading, or across both for
the integrity check (ratio 2.2).

Run:  python sim/circuit/trunk_paths.py           (writes .cir files, runs LTspice in batch, checks results)
Out:  trunk_paths_5khz.cir / _50khz.cir / trunk_open_me.cir, trunk_results.csv, trunk_results.png
"""
import cmath, csv, json, math, pathlib, re, subprocess
import numpy as np

D = pathlib.Path(__file__).parent
LTSPICE = r"C:\Users\Aadityaa\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
R5 = 100.0                                   # the reference is the 0.1 % precision Rcal (self-calibrating front end)
# segment Cole parameters: (Re extracellular, Ri intracellular, Cm membrane). ASSUMPTION, typical adult segment sizes.
SEG = {"arm": (330.0, 750.0, 2.9e-9), "leg": (290.0, 650.0, 3.39e-9), "trunk": (28.0, 60.0, 30e-9)}
FT, RC, PATHS = [1.0, 1.05, 1.10], [300, 3000], [1, 2, 3, 4]
# which electrode each of the four mux lines connects to, per path (inj+, inj-, sense+, sense-)
ROUTE = {1: ("LF", "RF"), 2: ("LH", "RH"), 3: ("LH", "LF"), 4: ("RH", "RF")}
LIMBS = ["LH", "RH", "LF", "RF"]


def cole(re_, ri, cm, w):
    zc = 1 / (1j * w * cm)
    return re_ * (ri + zc) / (re_ + ri + zc)


def true_z(path, ft, f, fl=1.0):
    w = 2 * math.pi * f
    arm, leg = cole(*SEG["arm"], w), cole(SEG["leg"][0] / fl, *SEG["leg"][1:], w)
    tr = cole(SEG["trunk"][0] / ft, *SEG["trunk"][1:], w)
    return abs({1: 2 * leg, 2: 2 * arm, 3: arm + tr + leg, 4: arm + tr + leg}[path])


def true_trunk(ft, f):
    return abs(cole(SEG["trunk"][0] / ft, *SEG["trunk"][1:], 2 * math.pi * f))


def netlist(f, steps, title, header=""):
    L = [f"* ===== HridayMitra: {title} =====", header,
         ".param f=" + f"{f:g}" + " Rc=1k ft=1 fl=1 path=1 selv=0 calv=3.3",
         "V1 vcc 0 3.3", "R1 vcc vrefin 10k", "R2 vrefin 0 10k", "C1 vrefin 0 10u",
         "Bu1a vref 0 V=limit(V(vrefin),0.05,3.25)",
         "Vdac dac 0 SIN(1.65 0.83 {f})", "C2 dac excin 1u", "R3 excin vref 100k",
         "Bu1b excout 0 V=limit(V(excin),0.05,3.25)",
         "C3 excout n1 1u", "R4 n1 injP 4.7k", "C4 injN ret 1u", "R5 ret ncal 120", "Rcal ncal vref 100",
         "* --- body: arms to shoulder node SH, trunk SH-PV, legs to pelvis node PV (Cole: Re || Ri+Cm) ---"]
    for limb, seg, end in [("LH", "arm", "SH"), ("RH", "arm", "SH"), ("LF", "leg", "PV"), ("RF", "leg", "PV")]:
        re_, ri, cm = SEG[seg]
        rex = f"{{{re_:g}/fl}}" if seg == "leg" else f"{re_:g}"
        L += [f"Re{limb} {limb} {end} {rex}", f"Ri{limb} {limb} m{limb} {ri:g}", f"Cm{limb} m{limb} {end} {cm:g}"]
    re_, ri, cm = SEG["trunk"]
    L += [f"ReT SH PV {{{re_:g}/ft}}", f"RiT SH mT {ri:g}", f"CmT mT PV {cm:g}",
          "* --- electrodes: every hand/foot has an inject (i) and a sense (s) plate, each with contact Rc ---"]
    for limb in LIMBS:
        L += [f"Rci{limb} i{limb} {limb} {{Rc}}", f"Rcs{limb} s{limb} {limb} {{Rc}}"]
    L += ["* --- path mux (74HC4052, Ron 100 ohm): picks inject pair and sense pair ---",
          ".model SW SW(Ron=100 Roff=1G Vt=1.65 Vh=0.1)"]
    k = 0
    for line, node, prefix in [(0, "injP", "i"), (1, "injN", "i"), (0, "sraw_p", "s"), (1, "sraw_n", "s")]:
        for limb in LIMBS:
            ps = [p for p in PATHS if ROUTE[p][line] == limb]
            if not ps:
                continue
            k += 1
            ctl = " + ".join(f"if(abs(path-{p})<0.5,3.3,0)" for p in ps)
            L += [f"Bm{k} c{k} 0 V={ctl}", f"Sm{k} {node} {prefix}{limb} c{k} 0 SW"]
    L += ["* --- sense lines: 1k protection, 1M bias to VREF ---",
          "R6 sraw_p sa 1k", "R7 sraw_n sb 1k", "R8 sa vref 10Meg", "R9 sb vref 10Meg",
          "* --- 74HC4053 selector: selv=0 body, selv=3.3 reference; switch C (calv): 3.3 = across Rcal, 0 = across R5+Rcal ---",
          "Vsel sel 0 {selv}", "Bch chi 0 V=V(sel)", "Bcl clo 0 V=3.3-V(sel)",
          "Vcal calsel 0 {calv}", "Bcc ccal 0 V=V(calsel)", "Bcn cnot 0 V=3.3-V(calsel)",
          "S5 rtap ncal ccal 0 SW", "S6 rtap ret cnot 0 SW",
          "S1 inp sa clo 0 SW", "S2 inp rtap chi 0 SW", "S3 inn sb clo 0 SW", "S4 inn vref chi 0 SW",
          "Bina ina 0 V=limit(V(vref)+10*(V(inp)-V(inn)),0.05,3.25)", "R11 ina adc 1.5k", "C5 adc 0 10n", "Radc adc 0 10Meg",
          "* --- DC definition of floating nodes ---"]
    nodes = ["n1", "injP", "injN", "SH", "PV", "mT", "sraw_p", "sraw_n", "ncal", "rtap"] + LIMBS + [f"m{x}" for x in LIMBS] + \
            [f"{p}{x}" for p in "is" for x in LIMBS]
    L += [f"Rd{i} {n} vref 1G" for i, n in enumerate(nodes)]
    per = 1 / f
    L += steps(per)
    L += [".save V(adc) I(R4)", ".end"]
    return "\n".join(x for x in L if x is not None) + "\n"


def batch_steps(per):
    t_end = max(0.02, 200 * per)
    return [f".tran 0 {t_end:g} 0 {per / 40:g}",
            ".step param selv list 0 3.3", ".step param path list 1 2 3 4", ".step param Rc list 300 3k",
            ".step param ft list 1 1.05 1.1",
            f".meas TRAN vpp PP V(adc) FROM={0.4 * t_end:g} TO={t_end:g}",
            f".meas TRAN ipk MAX abs(I(R4)) FROM={0.4 * t_end:g} TO={t_end:g}"]


def read_meas(log, name, n):
    txt = log.read_text(errors="ignore")
    block = txt.split(f"Measurement: {name}")[1].split("Measurement:")[0]
    vals = [float(m.group(2)) for m in re.finditer(r"^\s*(\d+)\s+([-\d.eE+]+)", block, re.M)]
    assert len(vals) == n, (name, len(vals), n)
    return vals


def run(cir):
    subprocess.run([LTSPICE, "-b", str(cir)], check=True, timeout=1800)
    return cir.with_suffix(".log")


def leg_noise_pct():
    t = json.loads((D.parents[1] / "data/processed/measurement_error_model.json").read_text())["table"]
    return float(np.mean([r["sd_pct_median3"] for r in t if r["noise_lsb"] == 4]))


def write_open_me():
    """One file a person can open in LTspice and press Run: 4 paths, answers in the log."""
    exp = {k: true_z(k, 1.0, 5e3) for k in PATHS}
    tr = (exp[3] + exp[4] - exp[1] - exp[2]) / 2
    head = chr(10).join([
        "* HOW TO USE: File > Open this file in LTspice, press Run (running man). It runs 4 times, once per path.",
        "*   Answer: View > SPICE Output Log, find 'zmeas' (one value per path, ohm). Expected (exact model, 5 kHz):",
        f"*     path 1 legs Z1 = {exp[1]:.1f}   path 2 arms Z2 = {exp[2]:.1f}   path 3 left Z3 = {exp[3]:.1f}   path 4 right Z4 = {exp[4]:.1f}",
        f"*     chest (trunk) = (Z3 + Z4 - Z1 - Z2) / 2 = {tr:.2f} ohm. Pass if every zmeas is within 1 % of these.",
        "*   Plot: right-click > Add Trace > V(adc). First 20 ms = body signal, next 20 ms = across the 100 ohm precision reference (Rcal).",
        "*   Try: set ft=1.1 (+10 % chest fluid) on the .param line: the chest number should fall about 9 %.",
        "*   Try: set Rc=10k (dry skin): the numbers should barely move (that is the point of 4-electrode sensing)."])
    def steps(per):
        return [".tran 0 0.04 0 5u", ".step param path list 1 2 3 4",
                ".meas TRAN vbody PP V(adc) FROM=0.008 TO=0.019",
                ".meas TRAN vsens PP V(adc) FROM=0.028 TO=0.039",
                ".meas TRAN zmeas PARAM 100*vbody/vsens"]
    txt = netlist(5e3, steps, "OPEN ME: chest (trunk) paths Z1-Z4, 5 kHz", head)
    txt = txt.replace("Vsel sel 0 {selv}", "Vsel sel 0 PULSE(0 3.3 0.02 1u 1u 0.02 0.1)   ; low = body, high = across Rcal")
    (D / "trunk_open_me.cir").write_text(txt)
    log = run(D / "trunk_open_me.cir")
    got = read_meas(log, "zmeas", 4)
    for k, g in zip(PATHS, got):
        print(f"open-me check path {k}: LTspice {g:.2f} vs exact {exp[k]:.2f} ({100 * (g - exp[k]) / exp[k]:+.2f} %)")
    print(f"open-me trunk: {(got[2] + got[3] - got[0] - got[1]) / 2:.2f} vs exact {tr:.2f}")


if __name__ == "__main__":
    write_open_me()
    rows, Z = [], {}
    for f in (5e3, 50e3):
        cir = D / f"trunk_paths_{f / 1e3:g}khz.cir"
        cir.write_text(netlist(f, batch_steps, f"trunk paths Z1-Z4 at {f / 1e3:g} kHz (batch: 48 runs)"))
        log = run(cir)
        n = 2 * 4 * 2 * 3
        vpp, ipk = read_meas(log, "vpp", n), read_meas(log, "ipk", n)
        for i in range(n):                                    # step order: selv fastest, then path, Rc, ft
            s, p, c, k = i % 2, (i // 2) % 4, (i // 8) % 2, i // 16
            Z.setdefault((f, FT[k], RC[c], PATHS[p]), [None, None, 0])
            Z[(f, FT[k], RC[c], PATHS[p])][s] = vpp[i]
            Z[(f, FT[k], RC[c], PATHS[p])][2] = max(Z[(f, FT[k], RC[c], PATHS[p])][2], ipk[i])
    for (f, ft, rc, p), (vb, vs, ip) in sorted(Z.items()):
        zm, zt = R5 * vb / vs, true_z(p, ft, f)
        rows.append(dict(f_hz=f, trunk_fluid=ft, contact_ohm=rc, path=p, z_meas=round(zm, 3), z_true=round(zt, 3),
                         err_pct=round(100 * (zm - zt) / zt, 3), body_pp_v=round(vb, 3), i_peak_uA=round(ip * 1e6, 1)))
    with open(D / "trunk_results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    zm = {(r["f_hz"], r["trunk_fluid"], r["contact_ohm"], r["path"]): r["z_meas"] for r in rows}
    trunk = lambda f, ft, rc: (zm[(f, ft, rc, 3)] + zm[(f, ft, rc, 4)] - zm[(f, ft, rc, 1)] - zm[(f, ft, rc, 2)]) / 2
    print(f"max |error| of Z1-Z4 over all cases: {max(abs(r['err_pct']) for r in rows):.2f} %  (criterion <= 1 %)")
    print(f"max body signal: {max(r['body_pp_v'] for r in rows) / 2:.2f} V peak around 1.65 V (clips at 1.6)")
    print(f"max injected current: {max(r['i_peak_uA'] for r in rows):.0f} uA peak")
    summary = {}
    for f in (5e3, 50e3):
        for rc in RC:
            t = [trunk(f, ft, rc) for ft in FT]
            tt = [true_trunk(ft, f) for ft in FT]
            print(f"{f / 1e3:>3.0f} kHz Rc={rc:>5}: trunk from 4 paths = {t[0]:.2f} / {t[1]:.2f} / {t[2]:.2f} ohm "
                  f"(true |Z| {tt[0]:.2f} / {tt[1]:.2f} / {tt[2]:.2f}); +10% chest fluid -> {100 * (t[2] - t[0]) / t[0]:+.1f} %")
        summary[f] = [trunk(f, ft, 300) for ft in FT]

    # small-change test: is a +5% / +10% chest-fluid change visible through real measurement noise?
    # each Z reading has noise sd = leg_noise_pct % of its value (from the circuit error model), independent per path
    sd_pct, rng, f = leg_noise_pct(), np.random.default_rng(0), 5e3
    zs = {p: zm[(f, 1.0, 300, p)] for p in PATHS}
    sd_trunk = 0.5 * math.sqrt(sum((sd_pct / 100 * zs[p]) ** 2 for p in PATHS))
    print(f"\nnoise: each path {sd_pct:.2f} % -> trunk sd {sd_trunk:.2f} ohm on a {summary[f][0]:.1f} ohm trunk "
          f"({100 * sd_trunk / summary[f][0]:.1f} %), one daily check-in (median of 3)")
    for ft_i, label in [(1, "+5%"), (2, "+10%")]:
        delta = summary[f][0] - summary[f][ft_i]
        for days in (1, 3, 7):
            z = delta / (sd_trunk / math.sqrt(days))
            print(f"  chest fluid {label}: change {delta:.2f} ohm, averaged over {days} day(s) -> {z:.1f} noise units")

    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for f, col in ((5e3, "#0d6b6e"), (50e3, "#b3261e")):
        for rc, mk in zip(RC, "os"):
            ax[0].plot([100 * (x - 1) for x in FT], [trunk(f, ft, rc) for ft in FT], marker=mk, color=col,
                       label=f"{f / 1e3:g} kHz, contact {rc} ohm")
        ax[0].plot([100 * (x - 1) for x in FT], [true_trunk(ft, f) for ft in FT], "k--", lw=.8)
    ax[0].set_xlabel("extra chest fluid (%)"); ax[0].set_ylabel("trunk from 4 paths (ohm)"); ax[0].legend(fontsize=7)
    ax[0].set_title("LTspice: trunk recovered from Z1-Z4 (dashed = exact)")
    e = [r["err_pct"] for r in rows]
    ax[1].hist(e, bins=20, color="#0d6b6e"); ax[1].set_xlabel("error of each Z1-Z4 reading (%)")
    ax[1].set_title(f"all {len(rows)} path readings")
    fig.tight_layout(); fig.savefig(D / "trunk_results.png", dpi=130)
