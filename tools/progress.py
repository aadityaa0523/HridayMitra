"""Progress tracker: reads progress.json, prints bars, writes docs/progress.html.   Run: python tools/progress.py"""
import json, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "progress.json").read_text(encoding="utf-8"))


def frac(tasks):
    return sum(t["done"] for t in tasks) / len(tasks)


ws = [(w["name"], w["weight"], frac(w["tasks"]), w["tasks"]) for w in data["workstreams"]]
overall = sum(w * f for _, w, f, _ in ws) / sum(w for _, w, _, _ in ws)
phys = frac(data["physical"]["tasks"])


def bar(f, n=30):
    k = round(f * n)
    return "█" * k + "░" * (n - k)


print(f"OVERALL (laptop work)  [{bar(overall)}] {overall:6.1%}")
for name, w, f, _ in ws:
    print(f"{name:<36} [{bar(f)}] {f:6.1%}  (weight {w})")
print(f"{'Physical build (team-reported)':<36} [{bar(phys)}] {phys:6.1%}")

rows = ""
for name, w, f, tasks in ws + [(data["physical"]["name"], 0, phys, data["physical"]["tasks"])]:
    items = "".join(f'<li class="{"d" if t["done"] >= 1 else "p" if t["done"] > 0 else ""}">{html.escape(t["name"])}'
                    f'<span>{t["done"]:.0%}</span></li>' for t in tasks)
    rows += (f'<section><div class="h"><b>{html.escape(name)}</b><span>{f:.0%}</span></div>'
             f'<div class="bar"><i style="width:{f*100:.1f}%"></i></div><ul>{items}</ul></section>')
page = f"""<!doctype html><html><head><meta charset="utf-8"><title>HridayMitra progress</title>
<style>
:root{{--bg:#f7f8f8;--fg:#1b2427;--mut:#5b6a6f;--line:#dde3e4;--acc:#0d6b6e;--ok:#2a6f42;--warn:#8a5300}}
@media(prefers-color-scheme:dark){{:root{{--bg:#111618;--fg:#e4ebec;--mut:#9aaaae;--line:#2a3539;--acc:#5cc3c6;--ok:#6cc58a;--warn:#e7a74a}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;max-width:760px;margin:0 auto;padding:24px 16px}}
h1{{font-size:22px;margin:0 0 4px}} .sub{{color:var(--mut);margin:0 0 18px}}
.total{{border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:18px}}
.h{{display:flex;justify-content:space-between;margin:14px 0 4px}} .bar{{height:12px;background:var(--line);border-radius:6px;overflow:hidden}}
.bar i{{display:block;height:100%;background:var(--acc)}} .total .bar{{height:20px}}
ul{{list-style:none;margin:6px 0 0;padding:0;font-size:13px;color:var(--mut)}} li{{display:flex;justify-content:space-between;padding:1px 0}}
li.d{{color:var(--ok)}} li.p{{color:var(--warn)}}
</style></head><body><h1>HridayMitra: progress</h1><p class="sub">Updated {html.escape(data["updated"])}. Edit progress.json and rerun tools/progress.py.</p>
<div class="total"><div class="h"><b>Overall (laptop work)</b><span>{overall:.0%}</span></div><div class="bar"><i style="width:{overall*100:.1f}%"></i></div></div>
{rows}</body></html>"""
(ROOT / "docs" / "progress.html").write_text(page, encoding="utf-8")
print("wrote docs/progress.html")
