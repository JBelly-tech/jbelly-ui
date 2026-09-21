#!/usr/bin/env python3
"""Smoke test: the whole pipeline works from a clean checkout.

  spec -> build-screen.py -> page ; verify_page.py (render + console + lint + pre-flight) ; grade.py
Exit 0 on PASS. Run before a pull request:  python tests/smoke.py
Rendering needs Playwright (pip install playwright && playwright install chromium) or a local Chrome/Chromium/Edge;
without either, the render step is skipped and reported.
"""
import glob, os, re, subprocess, sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills", "jbelly-ui")
OUT = os.path.join(ROOT, "tests", "out"); os.makedirs(OUT, exist_ok=True)
PY = sys.executable

def run(label, args, must=True):
    r = subprocess.run([PY] + args, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
    tail = "\n".join(r.stdout.strip().splitlines()[-4:])
    print(f"[{'OK' if r.returncode == 0 else 'FAIL'}] {label}\n    " + tail.replace("\n", "\n    "))
    if r.returncode != 0 and r.stderr.strip(): print("    stderr: " + r.stderr.strip().splitlines()[-1])
    return r.returncode == 0 or not must

ok = True
page = os.path.join(OUT, "dashboard.html")
ok &= run("build-screen.py (spec -> page)", [os.path.join(SK, "scripts", "build-screen.py"), os.path.join(SK, "assets", "spec.example.json"), page])
# The generator fills the page two ways and both fail quietly: literal wording is swapped through the
# SHELL table in build-screen.py (a reworded shell stops the swaps matching), and whole regions -- nav,
# toolbar, KPIs, activity -- are rebuilt between <!-- @region --> markers (a renamed marker only warns,
# and the region silently keeps the shell's demo content). So this builds from a spec that shares no
# wording with the shell and insists every slot of both kinds reaches the page.
import json
from html import escape as _esc
distinct = json.loads(open(os.path.join(SK, "assets", "spec.example.json"), encoding="utf-8").read())
distinct["product"] = "ZephyrLogistics"; distinct["title"] = "Fleet overview"
distinct["chart"]["title"] = "Deliveries per week"
distinct["chart"]["series"][0]["name"] = "Delivered"; distinct["chart"]["series"][1]["name"] = "Returned"
distinct["highlights"]["title"] = "Route mix"; distinct["highlights"]["total_label"] = "Trips completed"
distinct["highlights"]["items"] = [{"label": "Express lane", "value": 98}, {"label": "Standard lane", "value": 58},
                                   {"label": "Bulk freight", "value": 36}, {"label": "Cold chain", "value": 22}]
distinct["table"]["title"] = "Live shipments"; distinct["table"]["columns"] = ["Driver", "Route", "State", "ETA"]
distinct["table"]["rows"] = [{"name": "Hala Nimri", "plan": "Line A", "status": "On time", "time": "07:20"},
                             {"name": "Bilal Sweiss", "plan": "Line B", "status": "Delayed", "time": "08:05"},
                             {"name": "Tareq Zoubi", "plan": "Line C", "status": "Held", "time": "09:40"}]
distinct["nav"] = [{"heading": "On the road"}, {"label": "Fleet map", "icon": "map", "active": True},
                   {"label": "Waybills", "icon": "truck", "badge": "42"},
                   {"label": "Depots", "icon": "warehouse", "children": ["Northern depot", "Coastal depot"]},
                   {"heading": "Back office"}, {"label": "Fuel cards", "icon": "credit-card"}]
distinct["toolbar"] = {"periods": ["This shift", "This week", "This season"], "secondary": "Download manifest", "primary": "Dispatch run"}
distinct["kpis"] = [{"label": "Vans on road", "value": "37", "delta": "+5%", "trend": "up", "icon": "truck"},
                    {"label": "Parcels scanned", "value": "9,140", "delta": "+11%", "trend": "up", "icon": "scan-line"},
                    {"label": "Late drops", "value": "6", "delta": "-3%", "trend": "down", "icon": "clock"},
                    {"label": "Fuel spend", "value": "JD 4,120", "delta": "+2%", "trend": "up", "icon": "wallet"}]
distinct["activity"] = [{"who": "Hala Nimri", "text": "closed run R-77", "when": "4 min ago", "primary": True},
                        {"who": "Dispatch desk", "text": "rerouted two vans around the bridge", "when": "1 h ago"}]
spec_path = os.path.join(OUT, "spec-distinct.json"); page_distinct = os.path.join(OUT, "distinct.html")
open(spec_path, "w", encoding="utf-8").write(json.dumps(distinct, indent=2))
ok &= run("build-screen.py (a spec that shares no wording with the shell)",
          [os.path.join(SK, "scripts", "build-screen.py"), spec_path, page_distinct])
_html = open(page_distinct, encoding="utf-8").read() if os.path.isfile(page_distinct) else ""
_ch, _hl, _tb, _nav, _tbar = distinct["chart"], distinct["highlights"], distinct["table"], distinct["nav"], distinct["toolbar"]
_want = [("brand", distinct["product"]), ("chart", _ch["title"])] + [("chart", s["name"]) for s in _ch["series"]]
_want += [("highlights", _hl["title"]), ("highlights", _hl["total_label"])] + [("highlights", i["label"]) for i in _hl["items"]]
_want += [("table", _tb["title"])] + [("table", c) for c in _tb["columns"]] + [("table", r["name"]) for r in _tb["rows"]]
_want += [("nav", n.get("label", n.get("heading"))) for n in _nav] + [("nav", c) for n in _nav for c in n.get("children", [])]
_want += [("toolbar", distinct["title"]), ("toolbar", _tbar["secondary"]), ("toolbar", _tbar["primary"])] + [("toolbar", p) for p in _tbar["periods"]]
_want += [("kpis", v) for k in distinct["kpis"] for v in (k["label"], k["value"])]
_want += [("activity", v) for a in distinct["activity"] for v in (a["who"], a["text"])]
_missing = [f"{slot}: {w}" for slot, w in _want if w not in _html and _esc(w, quote=True) not in _html]
# One marker per slot that only the shell says: still on the page means that slot was never rebuilt.
_stale = [f"{slot}: {w}" for slot, w in [("brand", "Acme Ops"), ("chart", "Orders per week"), ("highlights", "Orders completed"),
          ("table", "Recent orders"), ("table rows", "Dana Qasem"), ("nav", "Insights"), ("toolbar", "Order created"),
          ("kpis", 'data-count="1284"'), ("activity", "Ramadan 14-day")] if w in _html]
_thin = len(_want) < 40    # a gutted list would pass vacuously, so the count is asserted too
_label = "OK" if not _missing and not _stale and not _thin else "FAIL"
print("[" + _label + "] every spec label reaches the page")
if _thin: print(f"    only {len(_want)} labels asserted - this check has been gutted")
if _missing: print("    missing: " + ", ".join(_missing))
if _stale: print("    shell wording left behind: " + ", ".join(_stale))
if _label == "OK": print(f"    {len(_want)}/{len(_want)} labels applied, no demo wording left")
ok &= _label == "OK"

# The landing and pricing kinds work the other way round from the app: instead of swapping the
# shell's words for the spec's, they rebuild each region whole. So the failure that hides is the
# mirror image -- a region that was never rebuilt keeps the demo page and still looks built -- and
# both directions have to be asserted. Each kind is built from its own example, which is written to
# share no wording with its template: every string the spec supplies must be on the page, and no
# sentence that only the shell says may be left anywhere on it.
MARKERS = {
    "landing": ["Mishwar", "مشوار", "Beirut depot", "Barakat Dairy", "orders-2025-10-11.csv",
                "Tomorrow's routes, planned before the depot opens.", "Dispatch supervisor",
                "Asked by every dispatcher we meet", "Route planning for wholesale delivery fleets."],
    "pricing": ["Acme Ops", "الطلبات والمتاجر", "Pricing that follows your order volume", "1,500 orders a month",
                "For one shop and a team that fits around one table.", "What counts as an order?",
                "Everything in Starter, plus", "Start on the plan you need this month"],
}
# Keys that steer the build rather than reach the page, and the dictionary, which is Arabic by design.
SPEC_CHROME = {"kind", "theme", "density", "icon", "dir", "lang", "href", "tone", "i18n", "keep_demo_controls"}

def spec_strings(node, key=""):
    """Every string the spec asks the page to say, at whatever depth it sits."""
    if isinstance(node, dict):
        return [x for k, v in node.items() if k not in SPEC_CHROME for x in spec_strings(v, k)]
    if isinstance(node, list):
        return [x for v in node for x in spec_strings(v, key)]
    return [(key, node)] if isinstance(node, str) and node.strip() else []

for _kind, _marks in MARKERS.items():
    _spec_path = os.path.join(SK, "assets", f"spec.{_kind}.example.json")
    _built = os.path.join(OUT, _kind + ".html")
    ok &= run(f"build-screen.py ({_kind} spec -> page)", [os.path.join(SK, "scripts", "build-screen.py"), _spec_path, _built])
    _page = open(_built, encoding="utf-8").read() if os.path.isfile(_built) else ""
    _shell = open(os.path.join(SK, "assets", f"{_kind}-shell.html"), encoding="utf-8").read()
    _want = spec_strings(json.loads(open(_spec_path, encoding="utf-8").read()))
    _missing = [f"{k}: {v[:44]}" for k, v in _want if v not in _page and _esc(v, quote=True) not in _page]
    _stale = [m for m in _marks if m in _page]
    _blunt = [m for m in _marks if m not in _shell]   # a marker its own shell no longer says asserts nothing
    _thin = len(_want) < 60
    _label = "OK" if not (_missing or _stale or _blunt or _thin) else "FAIL"
    print("[" + _label + f"] every {_kind} spec label reaches the page")
    if _thin: print(f"    only {len(_want)} labels asserted - this check has been gutted")
    if _missing: print("    missing: " + ", ".join(_missing))
    if _stale: print("    shell wording left behind: " + ", ".join(_stale))
    if _blunt: print(f"    {_kind}-shell.html no longer says: " + ", ".join(_blunt))
    if _label == "OK": print(f"    {len(_want)}/{len(_want)} labels applied, no demo wording left")
    ok &= _label == "OK"
    ok &= run(f"preflight.py ({_kind})", [os.path.join(SK, "scripts", "preflight.py"), _built])

ok &= run("new_screen.py (scaffold)", [os.path.join(SK, "scripts", "new_screen.py"), os.path.join(OUT, "blank.html"), "--theme", "theme-graphite", "--dir", "rtl", "--strip-demo-controls"])
ok &= run("personality_init.py", [os.path.join(SK, "scripts", "personality_init.py"), "--product", "Smoke", "--kind", "dashboard", "--audience", "ops, daily, keyboard", "--vibe", "precise, calm, plain", "--preset", "theme-clinic", "--change", "density compact", "--change", "radius 0.5rem", "--out", os.path.join(OUT, "personality.md")])
ok &= run("lint_tokens.py", [os.path.join(SK, "scripts", "lint_tokens.py"), OUT])
ok &= run("preflight.py", [os.path.join(SK, "scripts", "preflight.py"), page])
have_renderer = False
try:
    import playwright  # noqa
    have_renderer = True
except ImportError:
    sys.path.insert(0, os.path.join(SK, "scripts"))
    try:
        import verify_page as vp
        have_renderer = bool(vp.find_browser())
    except Exception:
        pass
if have_renderer:
    ok &= run("verify_page.py (render 1440/375, dark, rtl)", [os.path.join(SK, "scripts", "verify_page.py"), page, "--variants", ",#dark=1,#dir=rtl", "--widths", "1440,375", "--out", OUT, "--json"])
else:
    print("[SKIP] verify_page.py: no renderer (install Playwright or Chrome)")
ok &= run("export_tokens.py", [os.path.join(SK, "scripts", "export_tokens.py"), os.path.join(SK, "references", "tokens.css"), os.path.join(OUT, "tokens.json")])
ok &= run("build_dist.py", [os.path.join(SK, "scripts", "build_dist.py")])
# grade the built page with the comparison grader
GRADE = os.path.join(OUT, "grade")
os.makedirs(os.path.join(GRADE, "outputs", "smoke"), exist_ok=True)
import shutil; shutil.copy(page, os.path.join(GRADE, "outputs", "smoke", "dashboard-smoke.html"))
# tests/out survives between runs, so last run's scores would otherwise be read back as this run's
for _g in glob.glob(os.path.join(GRADE, "**", "grading.json"), recursive=True): os.remove(_g)
ok &= run("grade.py (8 heuristics)", [os.path.join(ROOT, "evals", "tools", "grade.py"), GRADE])
# grade.py reports a score and exits 0 whatever it is -- even when it graded nothing at all -- so the
# score it wrote is read back and enforced here; otherwise this step passes on a page that fails all 8.
_scores = [(os.path.basename(os.path.dirname(g)), e) for g in sorted(glob.glob(os.path.join(GRADE, "**", "grading.json"), recursive=True))
           for e in json.loads(open(g, encoding="utf-8").read())["expectations"]]
_lost = [f"{d}: {e['text']} - {e['evidence']}" for d, e in _scores if not e["passed"]]
_graded = "OK" if len(_scores) >= 8 and not _lost else "FAIL"
print("[" + _graded + "] the graded page meets every heuristic")
if len(_scores) < 8: print(f"    only {len(_scores)} heuristic(s) graded, expected 8 - grade.py found no page to grade under {GRADE}")
for _l in _lost: print("    " + _l)
if _graded == "OK": print(f"    {len(_scores)}/{len(_scores)} heuristics passed")
ok &= _graded == "OK"
# The reference is what people copy, so its examples have to obey its own prose. `## Link colour`
# tells the reader every preset declares --primary-accent; for a while none of the six did, and
# anyone copying a preset out of that file reproduced the defect the rule exists to prevent.
sys.path.insert(0, os.path.join(SK, "scripts"))
from preflight import to_srgb as _srgb, contrast as _cr
_pers = open(os.path.join(SK, "references", "personalities.md"), encoding="utf-8").read()
_WHITE = "oklch(100% 0 0)"
_bad = []
_blocks = re.findall(r"(\.theme-[\w.-]+)\s*\{([^}]*)\}", _pers)
for _sel, _body in _blocks:
    if "--primary:" not in _body: continue
    _acc = re.search(r"--primary-accent:\s*([^;]+);", _body)
    if not _acc:
        _bad.append(f"{_sel}: no --primary-accent, so its links keep the default blue"); continue
    _card = (re.search(r"--card:\s*([^;]+);", _body) or [None, _WHITE])[1].strip()
    _bg = (re.search(r"--background:\s*([^;]+);", _body) or [None, _WHITE])[1].strip()
    _r = min(_cr(_srgb(_acc.group(1).strip()), _srgb(_card)), _cr(_srgb(_acc.group(1).strip()), _srgb(_bg)))
    if _r < 4.5: _bad.append(f"{_sel}: link colour {_r:.2f}:1 against its own surfaces (need 4.5)")
_okp = len(_blocks) >= 6 and not _bad
print("[" + ("OK" if _okp else "FAIL") + "] personalities.md presets declare a readable link colour")
if len(_blocks) < 6: print(f"    only {len(_blocks)} preset block(s) found, expected 6")
for _b in _bad: print("    " + _b)
ok &= _okp

# A check that cannot fail is not a check. The contrast pass now reads the roles the markup paints
# text with, because the three shells passed for months while their links sat under 4.5:1 -- the
# pair was never declared, so nothing was ever compared. Put the old colour back on a copy and the
# pre-flight must refuse it.
_shell = os.path.join(SK, "assets", "landing-shell.html")
_src = open(_shell, encoding="utf-8").read()
_broken = _src.replace(".link { @apply text-primary-accent underline-offset-4 hover:underline; }",
                       ".link { @apply text-primary underline-offset-4 hover:underline; }")
if _broken == _src:
    print("[FAIL] pre-flight regression: the link recipe moved, so this test no longer tests anything")
    ok = False
else:
    _tmp = os.path.join(OUT, "contrast-regression.html")
    open(_tmp, "w", encoding="utf-8").write(_broken)
    _r = subprocess.run([sys.executable, os.path.join(SK, "scripts", "preflight.py"), _tmp],
                        capture_output=True, text=True)
    _caught = _r.returncode == 1 and "--primary on --" in _r.stdout
    print("[" + ("OK" if _caught else "FAIL") + "] pre-flight fails a page that paints links with an unreadable role")
    if not _caught: print("    it passed a page whose links are 3.96:1 in dark mode")
    ok &= _caught

print("\nSMOKE:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
