#!/usr/bin/env python3
"""Re-capture the screenshots the README and the landing page show (Class D).

The captures are the first thing a visitor sees, and until now they were taken by hand. That meant
they could fall behind the shells without anyone noticing: the set shipped for five days showing
link colours that the shells no longer use. This script takes them from the shells themselves, so a
capture is a build step rather than a memory.

Each entry names the demo state it wants through the URL fragment the shells already understand,
so nothing here knows anything about the pages beyond their controls.

Usage:  python scripts/capture_showcase.py [--out docs/showcase] [--width 1440] [--height 1000]
Exit 1 if any capture fails, 2 if there is no renderer.
"""
import argparse
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "skills" / "jbelly-ui" / "assets"

# name -> (shell, fragment, scroll target). The fragment drives the shell's own demo controls. A
# shot that is about the table has to scroll to it: the table sits below the fold at 1440x1000, so
# capturing the top of the page would show everything except the thing the caption promises.
SHOTS = {
    "default-light":                   ("app-shell.html", "", None),
    "default-dark":                    ("app-shell.html", "#dark=1", None),
    "demo-clinic-dark":                ("app-shell.html", "#theme=theme-clinic&dark=1", None),
    "demo-graphite-compact-loading":   ("app-shell.html", "#theme=theme-graphite&density=density-compact&state=loading", "#table-toolbar"),
    "demo-neo-empty":                  ("app-shell.html", "#theme=theme-neo&state=empty", "#table-toolbar"),
    "demo-sidebar-dark":               ("app-shell.html", "#sidebar=dark", None),
    "demo-slate-rtl":                  ("app-shell.html", "#theme=theme-slate&dir=rtl", None),
    "landing-light":                   ("landing-shell.html", "", None),
    "landing-dark":                    ("landing-shell.html", "#dark=1", None),
    "pricing-light":                   ("pricing-shell.html", "", None),
}


def capture(url, png, w, h, scroll=None):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(1200)          # charts and icons mount after the network settles
        if scroll:
            el = page.query_selector(scroll)
            if el is None:                   # a caption promising a state the shot cannot show
                raise RuntimeError(f"scroll target {scroll} is not in the page")
            # scroll_into_view_if_needed does nothing when the element is already technically
            # visible, which it is when it sits in the last few pixels of the viewport -- exactly the
            # case this is here to fix. Centre it explicitly.
            page.eval_on_selector(scroll, "e => e.scrollIntoView({block: 'center'})")
            page.wait_for_timeout(500)
        page.screenshot(path=str(png))
        browser.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "showcase"))
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=1000)
    ap.add_argument("--only", help="capture just this one name")
    a = ap.parse_args()

    try:
        import playwright  # noqa: F401
    except ImportError:
        print("No renderer: pip install playwright && playwright install chromium", file=sys.stderr)
        return 2

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    failed = []
    for name, (shell, frag, scroll) in SHOTS.items():
        if a.only and name != a.only:
            continue
        src = ASSETS / shell
        if not src.is_file():
            print(f"[SKIP] {name}: {shell} not present")
            continue
        png = out / f"{name}.png"
        url = src.as_uri() + frag
        try:
            capture(url, png, a.width, a.height, scroll)
            print(f"[OK]   {name}.png  {os.path.getsize(png):,} bytes  <- {shell}{frag}")
        except Exception as exc:                                  # a failed capture must not pass
            failed.append(f"{name}: {exc}")
            print(f"[FAIL] {name}: {exc}", file=sys.stderr)
    if failed:
        print(f"\n{len(failed)} capture(s) failed", file=sys.stderr)
        return 1
    print("\ncaptures written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
