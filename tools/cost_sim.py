"""COST SIMULATION: does the HridayMitra home unit stay under Rs 5,000 once real-life price noise is added?
Parses the parts list (section 3) of the build guide v3, checks the sums against the guide's own product totals
(Rs 3,837 low / Rs 4,695 plan), then runs a Monte Carlo (fixed seed, 20,000 draws).

Assumptions (all ours, not from the guide):
  * each item price ~ triangular(low, mode = (low+high)/2, high), where high = the guide's "Plan" price
  * build cost only: no shipping, no spare or replacement parts (team decision, 24 Oct 2026)
  * GST is already inside the listed prices (the guide uses retail listings), so none is added
  * volume line: at 100 units, bulk prices are 30-40% lower than the single-unit price (pure assumption)

Run:  python tools/cost_sim.py
Outputs: reports/cost_simulation.csv, reports/cost_simulation.png
"""
import pathlib, re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "src" / "HridayMitra build guide v3.html"
N, SEED, LIMIT = 20_000, 2026, 5000
NOT_PRODUCT = {"24", "26"}      # breadboards and solder: the guide marks them "demo only", not in the product total


def load_parts():
    """Product parts list as a DataFrame (name, low, high), plus the guide's stated product totals."""
    tabs = pd.read_html(GUIDE)
    parts = next(t for t in tabs if "Plan ₹" in t.columns)
    parts.columns = ["n", "part", "qty", "use", "tier", "low", "high", "src"]
    parts["low"] = pd.to_numeric(parts["low"], errors="coerce")      # section header rows repeat text -> NaN
    parts["high"] = pd.to_numeric(parts["high"], errors="coerce")
    parts["n"] = parts["n"].astype(str)
    buy = parts[parts.tier.isin(["Must", "Should", "Nice"]) & ~parts.n.isin(NOT_PRODUCT)].copy()
    # The charger is "skip if you own", low = 0, but the guide's product total counts it at its Plan price.
    buy.loc[buy.n == "27", "low"] = buy.loc[buy.n == "27", "high"]
    # Owned ESP32 and the amulet's ESP32-C3 are counted at market price, quoted in the Source column.
    price = lambda n, pat: float(re.search(pat, parts.loc[parts.n == n, "src"].iloc[0]).group(1))
    extra = pd.DataFrame({"part": ["ESP32 WROOM-32 DevKit (market price)", "ESP32-C3 SuperMini, amulet (market price)"],
                          "low": [price("1", r"Market ₹(\d+)"), price("3", r"SuperMini ₹(\d+)")]})
    extra["high"] = extra["low"]
    buy["part"] = buy["part"].str.split(r"[.,:(]").str[0].str.slice(0, 42).str.strip()
    items = pd.concat([buy[["part", "low", "high"]], extra], ignore_index=True)
    totals = next(t for t in tabs if t.columns[0] == "What")
    row = totals[totals.What.str.startswith("Product parts list")].iloc[0]
    guide = tuple(float(str(row[c]).replace(",", "")) for c in ("Low ₹", "Plan ₹"))
    return items, guide


def simulate(items, n=N, seed=SEED):
    rng = np.random.default_rng(seed)
    lo, hi = items.low.to_numpy(), items.high.to_numpy()
    price = np.tile(lo, (n, 1)).astype(float)
    var = hi > lo                                           # triangular() rejects low == high, so fixed prices skip it
    price[:, var] = rng.triangular(lo[var], (lo[var] + hi[var]) / 2, hi[var], size=(n, var.sum()))
    return price


def main():
    items, guide = load_parts()
    price = simulate(items)
    total = price.sum(axis=1)
    p5, med, p95 = np.percentile(total, [5, 50, 95])
    p_ok = float((total <= LIMIT).mean())
    # variance share = cov(source, total) / var(total); the shares add up to 1
    srcs, names = price, list(items.part)
    share = np.array([np.cov(srcs[:, i], total)[0, 1] for i in range(srcs.shape[1])]) / total.var(ddof=1)
    order = np.argsort(share)[::-1]
    top5 = list(order[:5])
    base = np.median(total)
    vol = (base * 0.6, base * 0.7)

    sums = (items.low.sum(), items.high.sum())
    rows = [("parsed_total_low", sums[0], "Rs, sum of parsed list"), ("guide_total_low", guide[0], "Rs, stated in guide"),
            ("parsed_total_plan", sums[1], "Rs, sum of parsed list"), ("guide_total_plan", guide[1], "Rs, stated in guide"),
            ("P(total<=5000)", p_ok, "build cost only (parts)"), ("median", med, "Rs"),
            ("p5", p5, "Rs"), ("p95", p95, "Rs"),
            ("volume_100_units_low", vol[0], "ASSUMPTION: bulk prices 40% lower, Rs per unit, no shipping"),
            ("volume_100_units_high", vol[1], "ASSUMPTION: bulk prices 30% lower, Rs per unit, no shipping")]
    rows += [(f"top{k+1}_variance", share[i], names[i]) for k, i in enumerate(top5)]
    out = ROOT / "reports"
    pd.DataFrame(rows, columns=["metric", "value", "note"]).round(4).to_csv(out / "cost_simulation.csv", index=False)

    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.5))
    a.hist(total, bins=60, color="#7fb6b8")
    a.axvline(LIMIT, color="#c0392b", lw=2); a.text(LIMIT + 15, a.get_ylim()[1] * 0.92, "Rs 5,000 limit", color="#c0392b")
    a.set(title=f"Home-unit build cost, {N:,} draws: P(<= Rs 5,000) = {p_ok:.0%}", xlabel="Rs", ylabel="draws")
    top = order[:8][::-1]
    b.barh([names[i] for i in top], share[top] * 100, color="#0d6b6e")
    b.set(title="Share of cost variance (%)", xlabel="% of variance")
    fig.tight_layout(); fig.savefig(out / "cost_simulation.png", dpi=150)

    print(f"Parsed {len(items)} product items: low Rs {sums[0]:,.0f} (guide {guide[0]:,.0f}), plan Rs {sums[1]:,.0f} (guide {guide[1]:,.0f})")
    print(f"P(total <= Rs 5,000) = {p_ok:.1%}; median Rs {med:,.0f}; 5th-95th Rs {p5:,.0f} - {p95:,.0f}")
    print("Top-5 variance items:", "; ".join(f"{names[i]} {share[i]:.0%}" for i in top5))
    print(f"ASSUMPTION, 100 units at 30-40% off: about Rs {vol[0]:,.0f} - {vol[1]:,.0f} per unit")


if __name__ == "__main__":
    main()
