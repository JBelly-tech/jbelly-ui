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
_stale = [f"{slot}: {w}" for slot, w in [("brand", "Bayan Ops"), ("chart", "Orders per week"), ("highlights", "Orders completed"),
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
    "pricing": ["Sijil", "الطلبات والمتاجر", "Pricing that follows your order volume", "1,500 orders a month",
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
# Named pages, not the whole output folder: tests/out is not cleaned between runs and holds
# deliberately broken copies this suite writes on purpose, so scanning all of it proves nothing.
ok &= run("lint_motion.py (the generated page)", [os.path.join(SK, "scripts", "lint_motion.py"), page])
for _kind2 in ("app", "landing", "pricing"):
    _p = os.path.join(OUT, _kind2 + ".html")
    if os.path.exists(_p):
        ok &= run(f"lint_motion.py (built {_kind2})", [os.path.join(SK, "scripts", "lint_motion.py"), _p])
ok &= run("lint_motion.py (the system itself)", [os.path.join(SK, "scripts", "lint_motion.py"), os.path.join(SK, "references")])
for _shellname in ("app-shell", "commerce-shell", "landing-shell", "pricing-shell"):
    ok &= run(f"lint_motion.py ({_shellname})", [os.path.join(SK, "scripts", "lint_motion.py"), os.path.join(SK, "assets", _shellname + ".html")])
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
# "Every button works" is the claim a demo lives or dies on, and it is not decidable by reading the
# source: a handler can be attached and still do nothing. The page the generator just built is
# driven, control by control, in a real browser.
_cc = subprocess.run([sys.executable, os.path.join(SK, "scripts", "check_controls.py"), page],
                     capture_output=True, text=True)
if _cc.returncode == 2:
    print("[SKIP] check_controls.py: no renderer (install Playwright or Chrome)")
    print("    " + (_cc.stderr or "").strip().splitlines()[-1][:120] if _cc.stderr.strip() else "")
else:
    print("[" + ("OK" if _cc.returncode == 0 else "FAIL") + "] every control in the built page does something")
    for _l in (_cc.stdout or "").strip().splitlines()[-6:]:
        print("    " + _l)
    ok &= _cc.returncode == 0

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

# A rule that cannot fail reads as a guarantee. Four deliberately bad sources, each the smallest
# thing that should trip its rule, and each has to fail for THAT reason -- so the rule id is
# asserted, not only the exit code.
_MOTION_NEGATIVES = [
    ("transition-all",             '<button class="btn transition-all duration-300">Save</button>', "M02"),
    ("a raw 300ms",                ".a { transition: opacity 300ms var(--ease-enter); }",            "M01"),
    ("animate-pulse",              '<div class="skeleton animate-pulse"></div>',                    "M09"),
    ("an ungated @starting-style", "@starting-style { .card { opacity: 0; } }",                      "M11"),
]
for _name, _body, _rule in _MOTION_NEGATIVES:
    _ext = ".html" if _body.lstrip().startswith("<") else ".css"
    _bad = os.path.join(OUT, "motion-negative-" + _rule + _ext)
    open(_bad, "w", encoding="utf-8").write(_body + "\n")
    _r = subprocess.run([PY, os.path.join(SK, "scripts", "lint_motion.py"), _bad],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    _hit = _r.returncode == 1 and _rule in _r.stdout
    print("[" + ("OK" if _hit else "FAIL") + f"] lint_motion.py fails {_name} with {_rule}")
    if not _hit: print(f"    exit {_r.returncode}: " + " | ".join(_r.stdout.strip().splitlines()[:2]))
    ok &= _hit
    os.remove(_bad)

# Scanning nothing is not a pass: a wrong path has to exit 2, never report OK.
_empty = os.path.join(OUT, "motion-empty"); os.makedirs(_empty, exist_ok=True)
_r = subprocess.run([PY, os.path.join(SK, "scripts", "lint_motion.py"), _empty],
                    capture_output=True, text=True, encoding="utf-8", errors="replace")
print("[" + ("OK" if _r.returncode == 2 else "FAIL") + "] lint_motion.py exits 2 when there was nothing to check")
ok &= _r.returncode == 2

# The runtime probe has one job source analysis cannot do: notice that the page renders correctly
# and does not animate. Break the sheet on a copy and V01 must refuse it.
if have_renderer:
    _src = open(os.path.join(SK, "assets", "pricing-shell.html"), encoding="utf-8").read()
    _dead = _src.replace('<style id="jb-motion">', '<style id="jb-motion-off">', 1)
    if _dead == _src:
        print("[FAIL] verify_motion regression: the shell no longer inlines a jb-motion block")
        ok = False
    else:
        _tmp = os.path.join(OUT, "motion-canary.html")
        open(_tmp, "w", encoding="utf-8").write(_dead)
        _r = subprocess.run([PY, os.path.join(SK, "scripts", "verify_motion.py"), _tmp],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        _caught = _r.returncode == 1 and "V01" in _r.stdout
        print("[" + ("OK" if _caught else "FAIL") + "] verify_motion.py refuses a page whose motion sheet never reached the document")
        if not _caught: print(f"    exit {_r.returncode}: " + " | ".join(_r.stdout.strip().splitlines()[-2:]))
        ok &= _caught

# The site claims the demos ship AR/EN with full RTL, and now the site itself does. That claim is
# worth what checks it: every element that asks to be translated has an entry, every entry is asked
# for by some element, and switching back restores the markup that was SERVED rather than a
# re-rendering of it -- an i18n layer that rebuilds English from its own table drifts silently.
try:
    from playwright.sync_api import sync_playwright as _spw
except ImportError:
    _spw = None
if _spw is None:
    print("[SKIP] the site's Arabic edition: needs Playwright")
else:
    _url = "file:///" + os.path.join(ROOT, "index.html").replace("\\", "/")
    with _spw() as _p:
        _b = _p.chromium.launch(); _pg = _b.new_page(viewport={"width": 1440, "height": 1000})
        _pg.goto(_url, wait_until="load"); _pg.wait_for_timeout(400)
        _before = _pg.evaluate("document.getElementById('main').innerHTML")
        _t0 = _pg.title()
        _pg.click("#lang-toggle"); _pg.wait_for_timeout(200)
        _ar = (_pg.get_attribute("html", "dir"), _pg.get_attribute("html", "lang"))
        _t1 = _pg.title()
        _gaps = _pg.evaluate("""() => {
          const t = document.getElementById('ar');
          const has = new Set([...t.content.querySelectorAll('[data-for]')].map(n => n.getAttribute('data-for')));
          const used = new Set([...document.querySelectorAll('[data-i18n]')].map(e => e.getAttribute('data-i18n')));
          const loose = new Set(['doc-title','doc-desc','dark','light','copy-done','copy-manual']);
          return { missing: [...used].filter(k => !has.has(k)),
                   unused: [...has].filter(k => !used.has(k) && !loose.has(k)) };
        }""")
        _pg.click("#lang-toggle"); _pg.wait_for_timeout(200)
        _after = _pg.evaluate("document.getElementById('main').innerHTML")
        _t2 = _pg.title()
        # The rail re-themes this page; the still beside it is the demo as it ships and cannot
        # follow. What can follow is the way in: every link to a demo carries the personality, the
        # mode and the language the reader is in -- except the one whose whole job is to open the
        # demo in the direction they are NOT in.
        _pg.click('button[data-theme="theme-mint"]'); _pg.wait_for_timeout(200)
        _pg.click("#dark-toggle"); _pg.wait_for_timeout(200)
        _links = _pg.evaluate("""() => Array.from(document.querySelectorAll('a[href*="-shell.html"]'))
              .map(a => a.getAttribute('href'))""")
        _carry = [l for l in _links if "dir=" not in l]
        _flip = [l for l in _links if "dir=" in l]
        _state_ok = bool(_carry) and all("theme=theme-mint" in l and "dark=1" in l for l in _carry)
        _flip_ok = all("theme=" not in l for l in _flip)
        _b.close()
    for _name, _cond, _why in [
        ("the language button switches the document to Arabic and RTL", _ar == ("rtl", "ar"), str(_ar)),
        ("the document title is translated with the page", _t1 != _t0, _t1),
        ("every element that asks for a translation has one", not _gaps["missing"], ", ".join(_gaps["missing"])),
        ("every translation is asked for by some element", not _gaps["unused"], ", ".join(_gaps["unused"])),
        ("switching back restores the served markup exactly", _before == _after,
         f"{len(_before)} -> {len(_after)} characters"),
        ("switching back restores the title", _t2 == _t0, _t2),
        ("every demo link carries the personality and the mode the reader picked", _state_ok,
         ", ".join(_carry)),
        ("the link that flips direction keeps its own fragment", _flip_ok, ", ".join(_flip)),
    ]:
        print("[" + ("OK" if _cond else "FAIL") + "] " + _name + ("" if _cond else "\n    " + _why))
        ok &= _cond


# A state nobody declared is still a state the page can be in. Five of six personalities on this
# project's own site painted white text on a white card in dark mode and the pre-flight said PASS,
# because no `.theme-x.dark` rule existed and so no environment was ever built for it. The smallest
# page that should trip the new check is one personality, a dark mode, and no block joining them.
_bare = os.path.join(OUT, "preset-without-dark.html")
open(_bare, "w", encoding="utf-8").write("""<!doctype html><html><head><style>
:root { --background: oklch(100% 0 0); --foreground: oklch(14.5% 0.005 285); }
.dark { --background: oklch(14.5% 0.005 285); --foreground: oklch(98.5% 0 0); }
.theme-x { --background: oklch(98% 0.01 160); }
</style></head><body><main><h1>a personality with no dark half</h1></main></body></html>""")
_r = subprocess.run([PY, os.path.join(SK, "scripts", "preflight.py"), _bare],
                    capture_output=True, text=True, encoding="utf-8", errors="replace")
_caught = _r.returncode == 1 and "reachable, undeclared" in _r.stdout
print("[" + ("OK" if _caught else "FAIL") + "] pre-flight fails a personality that has no dark half")
if not _caught: print(f"    exit {_r.returncode}: " + " | ".join(_r.stdout.strip().splitlines()[-2:]))
ok &= _caught

# The same run must not invent the failure where the dark half IS declared, or every correct
# personality in the system starts reporting a fault.
_paired = os.path.join(OUT, "preset-with-dark.html")
open(_paired, "w", encoding="utf-8").write("""<!doctype html><html><head><style>
:root { --background: oklch(100% 0 0); --foreground: oklch(14.5% 0.005 285); }
.dark { --background: oklch(14.5% 0.005 285); --foreground: oklch(98.5% 0 0); }
.theme-x { --background: oklch(98% 0.01 160); }
.theme-x.dark { --background: oklch(14% 0.01 160); }
</style></head><body><main><h1>a personality with both halves</h1></main></body></html>""")
_r2 = subprocess.run([PY, os.path.join(SK, "scripts", "preflight.py"), _paired],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
print("[" + ("OK" if _r2.returncode == 0 else "FAIL") + "] pre-flight passes a personality that has one")
if _r2.returncode != 0: print("    " + " | ".join(_r2.stdout.strip().splitlines()[-3:]))
ok &= _r2.returncode == 0

# And a file type it cannot parse is refused rather than mis-read as CSS.
_md = os.path.join(OUT, "not-reviewable.md")
open(_md, "w", encoding="utf-8").write("# notes\n\n```css\n.theme-x { --background: oklch(98% 0.01 160); }\n```\n")
_r3 = subprocess.run([PY, os.path.join(SK, "scripts", "preflight.py"), _md],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
print("[" + ("OK" if _r3.returncode == 2 else "FAIL") + "] pre-flight refuses a file type it cannot parse")
if _r3.returncode != 2: print(f"    exit {_r3.returncode}")
ok &= _r3.returncode == 2


# A personality is written after dark mode and is, like it, a single class, so every role it
# declares is handed to it in BOTH modes. Five of the six shipped personalities kept a light value
# in the dark page that way -- a 53% grey second line on a 13% ground, warm paper shadows on black.
# The contrast pass sees that only where it happens to compare that exact pair, and never at all for
# a role like --shadow-md, so the rule names the cause instead of waiting for a symptom.
_leak = os.path.join(OUT, "preset-leaks-into-dark.html")
open(_leak, "w", encoding="utf-8").write("""<!doctype html><html><head><style>
:root { --background: oklch(100% 0 0); --foreground: oklch(14.5% 0.005 285); --shadow-md: 0 1px 2px rgb(0 0 0 / 0.05); }
.dark { --background: oklch(14.5% 0.005 285); --foreground: oklch(98.5% 0 0); --shadow-md: 0 1px 2px rgb(0 0 0 / 0.5); }
.theme-x { --background: oklch(97% 0.01 160); --shadow-md: 0 6px 16px rgb(60 30 10 / 0.18); }
.theme-x.dark { --background: oklch(14% 0.01 160); }
</style></head><body><main><h1>a personality that keeps its light shadow in the dark</h1></main></body></html>""")
_r4 = subprocess.run([PY, os.path.join(SK, "scripts", "preflight.py"), _leak],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
_named = _r4.returncode == 1 and "keeps --shadow-md in .dark" in _r4.stdout
print("[" + ("OK" if _named else "FAIL") + "] pre-flight names a role a personality keeps in dark mode")
if not _named: print(f"    exit {_r4.returncode}: " + " | ".join(_r4.stdout.strip().splitlines()[-2:]))
ok &= _named

# preflight reads the declared roles. It cannot read what the markup does with them: `text-success`
# names no role pair -- it paints a fill as text, and on a tint of itself that is 1.97:1. Only a
# rendered page answers that, so verify_theme.py has to be able to fail on one.
_fill = os.path.join(OUT, "fill-as-text.html")
open(_fill, "w", encoding="utf-8").write("""<!doctype html><html><head><style>
:root { --background: oklch(100% 0 0); --foreground: oklch(14.5% 0.005 285); --success: oklch(72% 0.19 150); }
body { background: var(--background); color: var(--foreground); }
.badge { background: color-mix(in oklab, var(--success) 15%, transparent); color: var(--success);
         padding: 2px 8px; border-radius: 6px; font-size: 13px; }
</style></head><body><main><h1>the fill, painted as text</h1>
<p><span class="badge">Confirmed</span></p></main></body></html>""")
_r5 = subprocess.run([PY, os.path.join(SK, "scripts", "verify_theme.py"), _fill],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
_skipped = "[SKIP]" in _r5.stdout
_caught5 = _r5.returncode == 1 and "C01 TEXT" in _r5.stdout
print("[" + ("SKIP" if _skipped else ("OK" if _caught5 else "FAIL")) +
      "] verify_theme.py fails a fill painted as text on a tint of itself")
if not _skipped and not _caught5: print(f"    exit {_r5.returncode}: " + " | ".join(_r5.stdout.strip().splitlines()[-2:]))
ok &= _skipped or _caught5

# ...and must not invent one where the page reads, or every correct page reports a fault.
_ok_page = os.path.join(OUT, "accent-as-text.html")
open(_ok_page, "w", encoding="utf-8").write("""<!doctype html><html><head><style>
:root { --background: oklch(100% 0 0); --foreground: oklch(14.5% 0.005 285); --success: oklch(72% 0.19 150);
        --success-accent: oklch(45% 0.15 150); }
body { background: var(--background); color: var(--foreground); }
.badge { background: color-mix(in oklab, var(--success) 15%, transparent); color: var(--success-accent);
         padding: 2px 8px; border-radius: 6px; font-size: 13px; }
</style></head><body><main><h1>the text value, painted as text</h1>
<p><span class="badge">Confirmed</span></p></main></body></html>""")
_r6 = subprocess.run([PY, os.path.join(SK, "scripts", "verify_theme.py"), _ok_page],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
print("[" + ("OK" if _r6.returncode == 0 else "FAIL") + "] verify_theme.py passes the same page with the text role")
if _r6.returncode != 0: print("    " + " | ".join(_r6.stdout.strip().splitlines()[-3:]))
ok &= _r6.returncode == 0

# A control's edge and its focus ring are the only thing saying where the control is and which one
# you are on; WCAG 1.4.11 and 2.4.11 ask 3:1 of both. Three of the four shells shipped --input at
# 1.27:1 against the page it sits on -- a form field with no visible boundary -- and --ring at
# 1.91:1 in dark mode. Those are the values in this fixture.
_edge = os.path.join(OUT, "invisible-field-edge.html")
open(_edge, "w", encoding="utf-8").write("""<!doctype html><html><head><style>
:root { --background: oklch(100% 0 0); --foreground: oklch(14.5% 0.005 285); --card: oklch(100% 0 0);
        --input: oklch(92% 0.004 286); --ring: oklch(71% 0.01 286); }
</style></head><body><main><h1>a field whose edge you cannot see</h1>
<input aria-label="Name"></main></body></html>""")
_r7 = subprocess.run([PY, os.path.join(SK, "scripts", "preflight.py"), _edge],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
_caught7 = _r7.returncode == 1 and "--input on --background" in _r7.stdout and "--ring on" in _r7.stdout
print("[" + ("OK" if _caught7 else "FAIL") + "] pre-flight fails a control boundary and a focus ring under 3:1")
if not _caught7: print(f"    exit {_r7.returncode}: " + " | ".join(_r7.stdout.strip().splitlines()[-2:]))
ok &= _caught7

# A workflow that does not parse is not a failing build, it is no build: GitHub answers a YAML error
# by running no jobs at all, so the run is red with an empty job list and no log to read. That cost
# a push to learn, from an unquoted step name containing "gate: " -- a colon-space starts a nested
# mapping. CI cannot catch this, because CI is the thing that did not start.
try:
    import yaml as _yaml
except ImportError:
    print("[SKIP] the workflows parse: needs pyyaml")
else:
    _wf = sorted(glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml")) +
                 glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yaml")))
    _bad = []
    for _f in _wf:
        try:
            _d = _yaml.safe_load(open(_f, encoding="utf-8"))
            if not _d or not _d.get("jobs"):
                _bad.append(os.path.basename(_f) + ": no jobs")
            else:
                for _j, _spec in _d["jobs"].items():
                    if not _spec.get("steps"):
                        _bad.append(f"{os.path.basename(_f)}: job {_j} has no steps")
        except Exception as _e:
            _bad.append(f"{os.path.basename(_f)}: {type(_e).__name__}: {str(_e).splitlines()[0]}")
    print("[" + ("OK" if not _bad else "FAIL") +
          f"] every workflow parses and has jobs with steps ({len(_wf)} file(s))")
    for _m in _bad:
        print("    " + _m)
    ok &= not _bad

# An installed skill must not depend on anything this project hosts. That is the whole reason the
# move to an organisation broke nothing for anyone using it: the folder people copy never calls
# home, so the site could vanish and the skill would still work. One "see the live demo at ..." in
# a reference file would end that quietly, and the damage would surface at the NEXT move, to
# someone else. The demos' CDN links are a separate question and stay: they are third-party.
_OURS = ("jbelly-tech.github.io", "mohammadjohar.github.io",
         "github.com/JBelly-tech", "github.com/mohammadJohar")
_calls_home = []
for _root, _dirs, _files in os.walk(SK):
    _dirs[:] = [d for d in _dirs if d != "__pycache__"]
    for _n in _files:
        _f = os.path.join(_root, _n)
        try:
            _t = open(_f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for _h in _OURS:
            if _h in _t:
                _calls_home.append(os.path.relpath(_f, ROOT).replace("\\", "/") + " -> " + _h)
print("[" + ("OK" if not _calls_home else "FAIL") +
      "] the installed skill depends on nothing this project hosts")
for _m in _calls_home:
    print("    " + _m)
ok &= not _calls_home

# The four shells are one system with four products in it. A role that carries no brand -- the line
# around a card, a field's edge, the focus ring, the radius, the grey of a second line -- has no
# reason to differ between them, and three times in one release it did, always the same way: the
# storefront was revised and the other three were not. Nobody sees a border at 94% next to one at
# 88% in different files; you see it as "the demos look uneven" months later.
# Surfaces and brand are excluded on purpose: the storefront's off-white page is a decision about
# product photographs, and each demo is a different product with a different colour.
_STRUCTURAL = ("border", "input", "ring", "radius", "muted-foreground")
_shells = ["app", "commerce", "landing", "pricing"]


def _scope(name, sel):
    _css = open(os.path.join(SK, "assets", name + "-shell.html"), encoding="utf-8").read()
    _m = re.search(r"(^|\n)" + re.escape(sel) + r"[^{]*\{([^{}]*)\}", _css, re.S)
    return dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", _m.group(2))) if _m else {}


_drift = []
for _sel in (":root", ".dark"):
    _envs = {n: _scope(n, _sel) for n in _shells}
    for _role in _STRUCTURAL:
        _vals = {n: (_envs[n].get(_role) or "").strip() for n in _shells}
        _seen = {v for v in _vals.values() if v}
        if len(_seen) > 1:
            _drift.append("%s --%s: %s" % (_sel, _role,
                          ", ".join("%s=%s" % (n, v or "(unset)") for n, v in _vals.items())))
print("[" + ("OK" if not _drift else "FAIL") +
      "] the shells agree on every role that carries no brand")
for _m2 in _drift:
    print("    " + _m2)
ok &= not _drift

print("\nSMOKE:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
