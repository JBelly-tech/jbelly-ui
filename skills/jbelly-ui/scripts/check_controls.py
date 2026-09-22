#!/usr/bin/env python3
"""Every control on the page does something, and this is what proves it (Class D).

A dead button is the most common defect in a demo and the hardest to see in review: it looks
finished, it has the right label, and nothing happens. Reading the source does not settle it either,
because a handler can be attached and still do nothing. So the page is driven.

Each control is activated in a fresh state and the page is watched for any evidence that the
activation landed: a DOM mutation, a changed attribute, a navigation, a moved focus, a new
animation. A control that produces none of those is reported with its label and its line.

What is deliberately not reported:
  - a link that leaves the page. Following it is navigation, which is its own check. A link to
    this same page is driven, and an anchor whose target is not in the document is reported: it
    looks identical to one that works.
  - a disabled control, which is doing exactly what it should by refusing.
  - a control the page hides at this width. It is not dead, it is not there.

Usage:
  python scripts/check_controls.py <file-or-url> [--width 1440] [--json] [--quiet]
Exit 1 if any control did nothing, 2 if the page could not be driven at all.
"""
import argparse
import json
import pathlib
import sys

# Anything a person can press, in the order a reader meets it.
SELECTOR = (
    "button, summary, [role=button], [role=tab], [role=radio], [role=switch], [role=menuitem], "
    "a[href], input:not([type=hidden]), select, textarea, [onclick], [tabindex]:not([tabindex='-1'])"
)

# Installed before each activation; reports whether anything at all moved.
WATCHER = """
() => {
  window.__jbMoved = false;
  if (window.__jbObs) window.__jbObs.disconnect();
  window.__jbObs = new MutationObserver(() => { window.__jbMoved = true; });
  window.__jbObs.observe(document.documentElement, {
    subtree: true, childList: true, attributes: true, characterData: true
  });
  window.__jbBefore = {
    href: location.href,
    focus: document.activeElement ? document.activeElement.outerHTML.slice(0, 120) : '',
    anims: document.getAnimations ? document.getAnimations().length : 0,
    scroll: window.scrollY
  };
}
"""

VERDICT = """
() => {
  const b = window.__jbBefore || {};
  const now = {
    href: location.href,
    focus: document.activeElement ? document.activeElement.outerHTML.slice(0, 120) : '',
    anims: document.getAnimations ? document.getAnimations().length : 0,
    scroll: window.scrollY
  };
  if (window.__jbObs) window.__jbObs.disconnect();
  return {
    mutated: !!window.__jbMoved,
    navigated: now.href !== b.href,
    focusMoved: now.focus !== b.focus,
    animated: now.anims > (b.anims || 0),
    scrolled: now.scroll !== b.scroll
  };
}
"""

# Whether this control is the thing a click at its own centre would reach. Guessing which overlay
# might be open needs a list of selectors that is wrong for every page nobody thought of; the
# browser already knows what is in front.
REACHABLE = """
  e => {
    const r = e.getBoundingClientRect();
    if (!r.width || !r.height) return { reachable: false, reason: 'zero size' };
    const cs = getComputedStyle(e);
    if (cs.pointerEvents === 'none') return { reachable: false, reason: 'pointer-events: none' };
    // A control hidden for sighted readers and paired with a visible label is the correct
    // segmented-control pattern: the input holds the semantics, the label holds the pixels. Drive
    // what a person drives.
    if (r.width <= 4 || r.height <= 4) {
      const lab = e.closest('label') ||
                  (e.id ? document.querySelector('label[for="' + CSS.escape(e.id) + '"]') : null);
      if (lab) {
        const lr = lab.getBoundingClientRect();
        if (lr.width > 4 && lr.height > 4) return { reachable: true, viaLabel: true };
      }
      return { reachable: false, reason: 'smaller than 4px with no visible label' };
    }
    const top = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
    if (!top) return { reachable: false, reason: 'outside the viewport' };
    if (top === e || e.contains(top) || top.contains(e)) return { reachable: true };
    return { reachable: false, reason: 'covered by ' + top.tagName.toLowerCase() +
             (top.id ? '#' + top.id : '') };
  }
"""


def describe(handle):
    """A label a person would recognise, and where to find it."""
    return handle.evaluate("""
      e => {
        const txt = (e.innerText || e.value || '').trim().replace(/\\s+/g, ' ').slice(0, 40);
        const name = e.getAttribute('aria-label') || e.getAttribute('title') || txt;
        const id = e.id ? '#' + e.id : '';
        return {
          tag: e.tagName.toLowerCase(), id: id,
          name: name || '(no accessible name)',
          href: e.getAttribute('href') || '',
          disabled: e.disabled === true || e.getAttribute('aria-disabled') === 'true',
          outer: e.outerHTML.slice(0, 160)
        };
      }
    """)


def run(target: str, width: int, height: int) -> dict:
    from playwright.sync_api import sync_playwright

    dead, checked, skipped = [], 0, 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        console = []
        page.on("console", lambda m: console.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: console.append(str(e)))
        page.goto(target, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(900)

        total = len(page.query_selector_all(SELECTOR))
        for i in range(total):
            handles = page.query_selector_all(SELECTOR)
            if i >= len(handles):
                break                                   # the page rebuilt itself; the rest re-index
            el = handles[i]
            info = describe(el)

            if info["disabled"]:
                skipped += 1
                continue
            if not el.is_visible():
                skipped += 1
                continue
            href = (info["href"] or "").strip()
            if href.startswith("#") and len(href) > 1:
                # A link to this same page is the one kind that can be driven without leaving, and
                # the one that most often points at nothing.
                target_id = href[1:]
                exists = page.evaluate(
                    "id => !!(document.getElementById(id) || document.getElementsByName(id).length)",
                    target_id)
                if not exists:
                    dead.append({**info, "why": f"points at #{target_id}, which is not in the page"})
                    checked += 1
                    continue
            elif href and href not in ("#", "#!") and not href.startswith("javascript:"):
                skipped += 1                            # leaves the page; following it is another check
                continue

            reach = el.evaluate(REACHABLE)
            if not reach["reachable"] and reach["reason"].startswith("covered by"):
                # Something the previous control opened is in the way. Start clean and re-find it.
                page.goto(target, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(700)
                handles = page.query_selector_all(SELECTOR)
                if i >= len(handles):
                    break
                el = handles[i]
                reach = el.evaluate(REACHABLE)
            if not reach["reachable"]:
                if reach.get("reason") == "pointer-events: none":
                    # Inert to a mouse, and still available to a keyboard and to assistive
                    # technology, which is a state no control should be in.
                    dead.append({**info, "why": "made inert with pointer-events: none but not "
                                                "marked disabled or aria-disabled"})
                    checked += 1
                else:
                    skipped += 1
                continue

            page.evaluate(WATCHER)
            try:
                if reach.get("viaLabel"):
                    el.evaluate("e => (e.closest('label') || "
                                "document.querySelector('label[for=\"' + CSS.escape(e.id) + '\"]')).click()")
                else:
                    el.click(timeout=2500)
            except Exception as exc:                    # moved or detached mid-click
                dead.append({**info, "why": f"could not be clicked: {str(exc).splitlines()[0][:90]}"})
                checked += 1
                continue
            page.wait_for_timeout(260)
            v = page.evaluate(VERDICT)
            checked += 1
            if not any(v.values()):
                dead.append({**info, "why": "nothing in the page changed"})

            # Put the page back into a state where the next control is reachable.
            page.keyboard.press("Escape")
            page.wait_for_timeout(90)

        browser.close()
    return {"target": target, "width": width, "total": total, "checked": checked,
            "skipped": skipped, "dead": dead, "console_errors": console[:10]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="an HTML file or a URL")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=1000)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    try:
        import playwright  # noqa: F401
    except ImportError:
        print("check_controls: needs Playwright (pip install playwright && playwright install chromium)",
              file=sys.stderr)
        return 2

    t = a.target
    if "://" not in t:
        f = pathlib.Path(t)
        if not f.is_file():
            print(f"check_controls: not a file: {t}", file=sys.stderr)
            return 2
        t = f.resolve().as_uri()

    try:
        r = run(t, a.width, a.height)
    except Exception as exc:
        print(f"check_controls: could not drive the page: {exc}", file=sys.stderr)
        return 2

    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    elif not a.quiet:
        for d in r["dead"]:
            print(f"[FAIL] {d['tag']}{d['id']} \"{d['name']}\" - {d['why']}")
            print(f"       {d['outer']}")
    if r["checked"] == 0:                               # driving nothing is not a pass
        print(f"check_controls: no drivable control found in {a.target} at {a.width}px "
              f"({r['total']} matched the selector, all skipped)", file=sys.stderr)
        return 2
    verdict = "PASS" if not r["dead"] else "FAIL"
    if not a.quiet:
        print(f"check_controls: {r['checked']} control(s) driven at {a.width}px, "
              f"{len(r['dead'])} dead, {r['skipped']} skipped (links, disabled, hidden) -> {verdict}")
    return 1 if r["dead"] else 0


if __name__ == "__main__":
    sys.exit(main())
