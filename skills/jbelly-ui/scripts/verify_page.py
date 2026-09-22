#!/usr/bin/env python3
"""One-call page verification (cross-platform): render variants headlessly, collect console errors,
run the token lint, print PASS/FAIL. Replaces multi-step verify loops.

Usage: python scripts/verify_page.py <page.html> [--variants ",#dark=1,#dir=rtl"] [--widths 1440,768,375] [--out shots/] [--height 1000] [--json]

Exit 1 on any of: a console or page error, a blank render, horizontal overflow (Playwright only),
a variant that renders byte-identical to the first one, a missing screenshot, a lint or pre-flight
failure. Exit 2 when the page or a renderer is missing - nothing was verified.

Renderer, in order of preference:
  1. Playwright for Python if installed  (pip install playwright && playwright install chromium)  - full console capture
  2. A local Chrome / Chromium / Edge binary in headless mode                                    - console via --enable-logging
"""
import hashlib, os, re, shutil, subprocess, sys, tempfile, time, uuid
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

# Chrome writes every console severity to chrome_debug.log as plain INFO, so the binary renderer
# cannot tell console.error from console.log. It therefore collects every console line and drops only
# these two, which the browser itself emits on launch and which no page can cause.
BROWSER_NOISE = ("Tracking Prevention blocked access to storage", "ProtocolLaunch")
# A 1440x1000 PNG of one flat colour measures ~6-9 KB; the smallest page with real content measured
# 26 KB. Used only when there is no Playwright and therefore no way to ask the page what it rendered.
BLANK_PNG_BYTES = 12000
PAGE_METRICS = """() => {
  const d = document.documentElement, b = document.body;
  let painted = 0;
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.width > 2 && r.height > 2 && getComputedStyle(el).visibility !== 'hidden') painted++;
  }
  return {text: b ? b.innerText.trim().length : 0, media: document.querySelectorAll('img,svg,canvas,video').length,
          painted: painted, scroll_w: d.scrollWidth, client_w: d.clientWidth};
}"""

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
        metrics = page.evaluate(PAGE_METRICS)
        page.screenshot(path=png)
        b.close()
    return errors, metrics

def render_binary(browser, url, png, w, h, budget_ms=20000):
    prof = os.path.join(tempfile.gettempdir(), "verify-" + uuid.uuid4().hex[:8])
    args = [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars", f"--window-size={w},{h}",
            f"--timeout={budget_ms}", f"--virtual-time-budget={budget_ms}", "--enable-logging", "--log-level=0",
            f"--user-data-dir={prof}", f"--screenshot={png}", url]
    errors = []
    try:
        subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=budget_ms / 1000 + 60)
    except (OSError, subprocess.SubprocessError) as e:
        errors.append(f"renderer failed: {e.__class__.__name__}: {e}")
    for d, _, fs in os.walk(prof):
        if "chrome_debug.log" in fs:
            with open(os.path.join(d, "chrome_debug.log"), encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if "CONSOLE" in line and not any(n in line for n in BROWSER_NOISE):
                        errors.append(re.sub(r"^.*CONSOLE:\d+\] ", "", line.strip()))
    shutil.rmtree(prof, ignore_errors=True)
    return errors, {}

def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return 2
    path = os.path.abspath(a[0])
    if not os.path.isfile(path):
        print(f"[FAIL] no such page: {path}"); return 2
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
    if renderer != "playwright":
        print("note: no Playwright - layout is not measured and console severity is unavailable; install it for the full check.")
    fail = False
    report = []
    base = {}  # width -> digest of the first variant, so a variant that changes nothing is visible
    for v in variants:
      for w in widths:
        tag = (re.sub(r"[^a-z0-9]+", "-", v).strip("-") or "default") + (f"-{w}" if len(widths) > 1 else "")
        png = os.path.join(out, f"{name}-{tag}.png")
        # an earlier run's screenshot would otherwise be measured and reported as this run's evidence
        if os.path.exists(png): os.remove(png)
        try:
            errors, m = render_playwright(url + v, png, w, h) if renderer == "playwright" else render_binary(renderer, url + v, png, w, h)
        except Exception as e:
            errors, m = [f"renderer failed: {e.__class__.__name__}: {str(e).splitlines()[0]}"], {}
        size = os.path.getsize(png) if os.path.exists(png) else 0
        why = []
        if errors: why.append(f"{len(errors)} console/page error(s)")
        if not size: why.append("the renderer wrote no screenshot, so nothing was verified")
        elif m and m["text"] == 0 and m["media"] == 0 and m["painted"] <= 2: why.append(f"page rendered blank: no text, no image and {m['painted']} painted element(s)")
        elif not m and size < BLANK_PNG_BYTES: why.append(f"page looks blank: screenshot is only {size:,} bytes")
        if m and m["scroll_w"] > m["client_w"] + 1:  # +1: scrollWidth is rounded up from sub-pixel layout
            why.append(f"horizontal overflow: content is {m['scroll_w']}px wide in a {m['client_w']}px viewport")
        digest = hashlib.sha256(open(png, "rb").read()).hexdigest() if size else ""
        if v == variants[0]: base.setdefault(w, digest)
        elif digest and digest == base.get(w): why.append(f"renders byte-identical to variant '{variants[0] or '(default)'}': this variant changes nothing")
        status = "FAIL" if why else "OK"
        fail |= status == "FAIL"
        report.append({"variant": v or "(default)", "width": w, "status": status, "screenshot": png, "errors": errors[:5], "metrics": m, "failures": why})
        print(f"[{status}] variant '{v or '(default)'}' @ {w}px: screenshot {size:,} bytes -> {png}")
        for r in why: print("    " + r)
        for e in errors[:3]: print("    " + e)
    lint = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "lint_tokens.py"), path, "--quiet"], capture_output=True, text=True)
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
