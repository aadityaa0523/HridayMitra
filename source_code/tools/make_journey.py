"""USER JOURNEY STORYBOARD (PS deliverable 1): one A3 page. Eight illustrated moments from one month of a real
synthetic patient (P0189, held-out test set): his actual lights, reasons and missed tablets from the frozen v3 engine,
plus who uses it, when, for how long and why they keep using it for months.
Run:  python tools/make_journey.py     Out: docs/HridayMitra user journey.pdf / .png (+ docs/journey/ sources)
"""
import json, pathlib, subprocess, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "journey"
sys.path.insert(0, str(ROOT / "engine"))
import alert_engine as A

PID = "P0189"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def patient():
    f = pd.read_csv(ROOT / "data/processed/daily_features.csv")
    p = pd.read_csv(ROOT / "data/processed/patients.csv").set_index("patient_id").loc[PID]
    g = f[f.patient_id == PID].reset_index(drop=True)
    T = json.loads((ROOT / "engine/frozen_params_v3.json").read_text())["T"]
    sc = A.scores(g); L = A.lights(sc, T)
    amber = int(np.flatnonzero((L >= 1) & (np.arange(len(L)) >= 14))[0]); red = int(np.flatnonzero(L == 2)[0])
    why = {d: A.explain(g, sc[d]) for d in (amber, red)}
    return g, sc, L, T, amber, red, int(p.admit_day), why


def chart(g, sc, L, T, amber, red, admit):
    d = g.day.to_numpy(); n = len(d)
    w0, z0 = np.nanmedian(g.weight_kg[7:28]), np.nanmedian(g.leg_z_ohm[7:28])
    fig = plt.figure(figsize=(15.2, 2.15), dpi=150)
    ax = fig.add_axes([0.045, 0.2, 0.9, 0.58]); ax2 = ax.twinx()
    S = np.array([r["S"] for r in sc])
    ax.fill_between(d, 0, S, color="#cfe2ff", lw=0, zorder=1)
    ax.plot(d, S, color="#1c64f2", lw=2, zorder=3, label="warning score (engine)")
    ax.axhline(T, color="#d1242f", lw=1.2, ls="--", zorder=2); ax.text(1, T + 0.5, f"red threshold T = {T:g} (frozen before testing)", color="#d1242f", fontsize=8.5)
    ax.axhline(0.6 * T, color="#bf8700", lw=1, ls=":", zorder=2); ax.text(1, 0.6 * T + 0.4, "amber", color="#bf8700", fontsize=8.5)
    fill = lambda s: s.interpolate(limit_area="inside")      # days without a reading: draw the line straight across
    ax2.plot(d, fill(g.weight_kg) - w0, color="#e16f24", lw=1.6, label="weight change (kg)")
    ax2.plot(d, (fill(g.leg_z_ohm) / z0 - 1) * 100 / 2.5, color="#8250df", lw=1.6, label="leg reading change (% / 2.5)")
    ax.set_ylim(0, max(S.max() * 1.15, T * 1.6)); ax2.set_ylim(-3.2, 3.6)
    ax.set_xlim(-0.5, admit + 0.5); ax.set_xticks([0, 7, 14, 21, 28, 30, amber, red, admit])
    ax.set_xticklabels(["day 0", "7", "14", "21", "28", "30", str(amber), str(red), str(admit)], fontsize=8.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax.set_ylabel("score", fontsize=8.5); ax2.set_ylabel("kg  /  %÷2.5", fontsize=8.5)
    ax.tick_params(labelsize=8); ax2.tick_params(labelsize=8)
    # light strip on top = the stool's actual light each day
    lx = fig.add_axes([0.045, 0.82, 0.9, 0.07]); lx.set_xlim(-0.5, admit + 0.5); lx.axis("off")
    col = {0: "#2da44e", 1: "#d4a72c", 2: "#cf222e"}
    for i in range(min(n, admit + 1)):
        lx.add_patch(plt.Rectangle((i - 0.45, 0), 0.9, 1, color=col[int(L[i])] if i < n else "#ccc"))
    lx.set_ylim(0, 1)
    fig.text(0.045, 0.93, "What HridayMitra actually saw: its light every day (top), its warning score and two of its signals", fontsize=9.5, weight="bold")
    top = ax.get_ylim()[1]
    ax.axvspan(31.5, 34.5, color="#eaeef2", zorder=0)
    for x, txt, c in ((33, "tablets missed\n(drawer shut)", "#57606a"), (amber, "amber", "#bf8700"), (red, "RED: SMS", "#cf222e"),
                      (admit, "would need\nhospital", "#57606a")):
        ax.axvline(x, color=c, lw=1, alpha=0.6)
        left = txt.startswith("tablets")
        ax.text(x - 1.7 if left else x, top * 0.98, txt, color=c, fontsize=8.3, ha="right" if left else "center", va="top", weight="bold",
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.4))
    ax.annotate("", xy=(red, top * 0.55), xytext=(admit, top * 0.55), arrowprops=dict(arrowstyle="<->", color="#cf222e", lw=1.6))
    ax.text((red + admit) / 2, top * 0.58, f"{admit - red} days of warning", fontsize=9, color="#cf222e", weight="bold", ha="center", va="bottom")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8, frameon=False, ncol=3, bbox_to_anchor=(0.12, 0.99))
    fig.savefig(OUT / "chart.png", dpi=150, transparent=False, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    g, sc, L, T, amber, red, admit, why = patient()
    chart(g, sc, L, T, amber, red, admit)
    facts = dict(amber=amber, red=red, admit=admit, lead=admit - red, amber_why=why[amber][1], red_why=why[red][1],
                 amber_cause=why[amber][0], red_cause=why[red][0], missed=[int(x) for x in g.day[g.took_pills == 0]])
    (OUT / "facts.json").write_text(json.dumps(facts, indent=1))
    print(facts)
    html = OUT / "user_journey.html"
    if html.exists():
        pdf, png = ROOT / "docs" / "HridayMitra user journey.pdf", ROOT / "docs" / "HridayMitra user journey.png"
        prof = rf"--user-data-dir={pathlib.Path.home() / 'AppData/Local/Temp/hmpdf/prof_journey'}"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", prof, f"--print-to-pdf={pdf}", html.as_uri()],
                       check=True, capture_output=True, timeout=180)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", prof, f"--screenshot={png}", "--window-size=1587,1123",
                        "--force-device-scale-factor=2", html.as_uri()], check=True, capture_output=True, timeout=180)
        print("wrote", pdf, png)
