#!/usr/bin/env python3
"""Smoke test: the whole pipeline works from a clean checkout.

  spec -> build-screen.py -> page ; verify_page.py (render + console + lint + pre-flight) ; grade.py
Exit 0 on PASS. Run before a pull request:  python tests/smoke.py
Rendering needs Playwright (pip install playwright && playwright install chromium) or a local Chrome/Chromium/Edge;
without either, the render step is skipped and reported.
"""
import os, subprocess, sys
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
os.makedirs(os.path.join(OUT, "grade", "outputs", "smoke"), exist_ok=True)
import shutil; shutil.copy(page, os.path.join(OUT, "grade", "outputs", "smoke", "dashboard-smoke.html"))
ok &= run("grade.py (8 heuristics)", [os.path.join(ROOT, "comparison", "tools", "grade.py"), os.path.join(OUT, "grade")])
print("\nSMOKE:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
