#!/usr/bin/env python3
"""One-call page verification (cross-platform): render variants headlessly, collect console errors,
run the token lint, print PASS/FAIL. Replaces multi-step verify loops.

Usage: python scripts/verify_page.py <page.html> [--variants ",#dark=1,#dir=rtl"] [--widths 1440,768,375] [--out shots/] [--height 1000] [--json]

Renderer, in order of preference:
  1. Playwright for Python if installed  (pip install playwright && playwright install chromium)  - full console capture
  2. A local Chrome / Chromium / Edge binary in headless mode                                    - console via --enable-logging
"""
import os, re, shutil, subprocess, sys, tempfile, time, uuid

def find_browser():
    cands = ["google-chrome", "chrome", "chromium", "chromium-browser", "msedge", "microsoft-edge",
             r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
             "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
             "/Applications/Chromium.app/Contents/MacOS/Chromium"]
    for c in cands:
        p = shutil.which(c) if not os.path.isabs(c) else (c if os.path.exists(c) else None)
        if p: return p
    return None

def render_playwright(url, png, w, h):
    from playwright.sync_api import sync_playwright
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": w, "height": h})
        page.on("console", lambda m: errors.append(m.text) if m.type in ("error",) else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(url, wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(1200)
        page.screenshot(path=png)
        b.close()
    return errors

def render_binary(browser, url, png, w, h, budget_ms=20000):
    prof = os.path.join(tempfile.gettempdir(), "verify-" + uuid.uuid4().hex[:8])
    args = [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars", f"--window-size={w},{h}",
            f"--timeout={budget_ms}", f"--virtual-time-budget={budget_ms}", "--enable-logging", "--log-level=0",
            f"--user-data-dir={prof}", f"--screenshot={png}", url]
    subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=budget_ms / 1000 + 60)
    errors = []
    for d, _, fs in os.walk(prof):
        if "chrome_debug.log" in fs:
            with open(os.path.join(d, "chrome_debug.log"), encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if "CONSOLE" in line and re.search(r"Uncaught|Error|error|Cannot apply|Failed to", line) and not re.search(r"Tracking Prevention|ProtocolLaunch", line):
                        errors.append(re.sub(r"^.*CONSOLE:\d+\] ", "", line.strip()))
    shutil.rmtree(prof, ignore_errors=True)
    return errors

def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return 2
    path = os.path.abspath(a[0])
    def opt(name, default):
        return a[a.index(name) + 1] if name in a else default
    variants = [v for v in opt("--variants", "").split(",")] if "--variants" in a else [""]
    out = opt("--out", os.path.join(tempfile.gettempdir(), "verify-page")); os.makedirs(out, exist_ok=True)
    widths = [int(x) for x in opt("--widths", opt("--width", "1440")).split(",")]; h = int(opt("--height", 1000))
    url = "file:///" + path.replace("\\", "/")
    name = os.path.splitext(os.path.basename(path))[0]
    try:
        import playwright  # noqa
        renderer = "playwright"
    except ImportError:
        renderer = find_browser()
        if not renderer:
            print("No renderer: install Playwright (pip install playwright && playwright install chromium) or Chrome/Chromium/Edge."); return 2
    fail = False
    report = []
    for v in variants:
      for w in widths:
        tag = (re.sub(r"[^a-z0-9]+", "-", v).strip("-") or "default") + (f"-{w}" if len(widths) > 1 else "")
        png = os.path.join(out, f"{name}-{tag}.png")
        errors = render_playwright(url + v, png, w, h) if renderer == "playwright" else render_binary(renderer, url + v, png, w, h)
        size = os.path.getsize(png) if os.path.exists(png) else 0
        status = "FAIL" if errors else ("SUSPECT" if size < (40000 if w >= 768 else 15000) else "OK")
        fail |= status == "FAIL"
        report.append({"variant": v or "(default)", "width": w, "status": status, "screenshot": png, "errors": errors[:5]})
        print(f"[{status}] variant '{v or '(default)'}' @ {w}px: screenshot {size:,} bytes -> {png}")
        for e in errors[:3]: print("    " + e)
        if status == "SUSPECT": print("    screenshot is very small: page may be unstyled or blank; open it and check")
    lint = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "lint_tokens.py"), os.path.dirname(path), "--quiet"], capture_output=True, text=True)
    print(f"[{'OK' if lint.returncode == 0 else 'FAIL'}] token lint: {'no raw palette classes' if lint.returncode == 0 else lint.stdout.strip().splitlines()[-2:]}")
    fail |= lint.returncode != 0
    pf = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "preflight.py"), path], capture_output=True, text=True, encoding="utf-8", errors="replace")
    pf_lines = [l for l in pf.stdout.splitlines() if l.startswith("[FAIL]") or l.startswith("[WARN]")]
    print(f"[{'OK' if pf.returncode == 0 else 'FAIL'}] pre-flight: {pf.stdout.strip().splitlines()[-1] if pf.stdout.strip() else 'no output'}")
    for l in pf_lines[:6]: print("    " + l)
    fail |= pf.returncode != 0
    if "--json" in a:
        import json
        json.dump({"page": path, "renders": report, "lint_ok": lint.returncode == 0, "preflight_ok": pf.returncode == 0, "verdict": "FAIL" if fail else "PASS"}, open(os.path.join(out, name + "-verify.json"), "w", encoding="utf-8"), indent=2)
        print(f"json -> {os.path.join(out, name + '-verify.json')}")
    print("VERDICT: FAIL - fix the items above, then run this script once more." if fail else "VERDICT: PASS - done; do not add further verification rounds.")
    return 1 if fail else 0

if __name__ == "__main__":
    sys.exit(main())
