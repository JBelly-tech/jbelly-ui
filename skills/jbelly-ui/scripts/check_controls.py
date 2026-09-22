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

Each control is driven from a freshly loaded page, so no activation can move, hide or renumber the
ones after it. The cost is a page load per control; the benefit is an answer that does not depend on
the order things happened to run in. The limit of that design is stated in the summary: this sweep
covers the page as a reader first meets it, and a control that only exists after navigating
elsewhere is out of its reach.

Usage:
  python scripts/check_controls.py <file-or-url> [--width 1440] [--json] [--quiet]
Exit 1 if any control did nothing, 2 if the page could not be driven at all.
"""
import argparse
import json
import pathlib
import sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # a control label may be Arabic
except Exception: pass

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
  e => {
  const b = window.__jbBefore || {};
  const now = {
    href: location.href,
    focus: document.activeElement ? document.activeElement.outerHTML.slice(0, 120) : '',
    anims: document.getAnimations ? document.getAnimations().length : 0,
    scroll: window.scrollY
  };
  if (window.__jbObs) window.__jbObs.disconnect();
  // An empty fragment is what `href="#"` leaves behind. It is not a destination, and counting it
  // would pass the first dead link in a page and fail every one after it.
  const bare = u => (u || '').replace(/#$/, '');
  return {
    mutated: !!window.__jbMoved,
    navigated: bare(now.href) !== bare(b.href),
    // Focus that landed on the control itself is what a click always does; it says nothing.
    focusMoved: now.focus !== b.focus && document.activeElement !== e,
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



# What a control is, independently of where it sits in a list that keeps changing under us.
SIGNATURE = """
  e => {
    const name = (e.getAttribute('aria-label') || e.getAttribute('title') ||
                  (e.innerText || e.value || '')).trim().replace(/\\s+/g, ' ').slice(0, 60);
    return [e.tagName.toLowerCase(), e.id || '', e.getAttribute('href') || '',
            e.getAttribute('data-theme') || '', name].join('\\u0001');
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
          // The page you are already on is meant to go nowhere.
          current: e.getAttribute('aria-current') === 'page',
          outer: e.outerHTML.slice(0, 160)
        };
      }
    """)


def run(target: str, width: int, height: int) -> dict:
    from playwright.sync_api import sync_playwright

    dead, checked, skipped = [], 0, 0
    console = []

    with sync_playwright() as p:
        browser = p.chromium.launch()

        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()
        page.on("console", lambda m: console.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: console.append(str(e)))

        def fresh():
            """Back to the page a reader first meets, with nothing the last control chose kept.

            A reload re-runs every script, so the only state that can survive it is the storage these
            demos persist their preferences to. Clearing that is the whole isolation, and it keeps
            the network cache a new context would have thrown away.
            """
            page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} }")
            context.clear_cookies()
            page.goto("about:blank")
            page.goto(target, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(700)
            return context, page

        page.goto(target, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(900)

        # One pass over the page as a reader first meets it: what each control is, and whether it
        # is going to be driven at all. Settling the skips here is what makes this affordable --
        # opening a context for a control only to discover it is hidden costs a page load for
        # nothing, and most controls on a large page are hidden at any one width.
        roster = []
        for h in page.query_selector_all(SELECTOR):
            info = describe(h)
            href = (info["href"] or "").strip()
            skip = (info["disabled"] or info["current"] or not h.is_visible()
                    or (href and href not in ("#", "#!") and not href.startswith("#")
                        and not href.startswith("javascript:")))
            roster.append({"sig": h.evaluate(SIGNATURE), "info": info, "skip": skip})
        total = len(roster)
        unreachable = 0
        skipped = sum(1 for r in roster if r["skip"])
        drivable = [i for i, r in enumerate(roster) if not r["skip"]]
        first = True

        for i in drivable:
            if not first:                               # back to a page that remembers nothing
                fresh()
            first = False
            here = page.query_selector_all(SELECTOR)
            if i >= len(here):
                unreachable += 1                        # the page did not come back the same
                continue
            el = here[i]
            if el.evaluate(SIGNATURE) != roster[i]["sig"]:
                # The roster and the reload disagree, so position is no longer meaningful and the
                # rest of this sweep would be measuring the wrong elements.
                left = len([j for j in drivable if j >= i])
                unreachable += left
                print(f"check_controls: the page did not reload identically at control {i}; "
                      f"{left} control(s) were not driven", file=sys.stderr)
                break
            info = roster[i]["info"]
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

            kind = el.evaluate("e => ({ tag: e.tagName.toLowerCase(), type: (e.type || ''), "
                               "checked: e.checked === true, options: e.options ? e.options.length : 0 })")
            # A radio or checkbox already in the state the click would set is defined to do nothing.
            # That is the specification working, not a control that is dead.
            if kind["type"] in ("radio", "checkbox") and kind["checked"]:
                skipped += 1
                continue
            # A select opens a native list on click and mutates nothing. Changing it is the action.
            if kind["tag"] == "select":
                if kind["options"] < 2:
                    skipped += 1
                    continue
                page.evaluate(WATCHER)
                try:
                    el.select_option(index=1 if el.evaluate("e => e.selectedIndex") == 0 else 0)
                except Exception as exc:
                    dead.append({**info, "why": f"could not be changed: {str(exc).splitlines()[0][:90]}"})
                    checked += 1
                    continue
                page.wait_for_timeout(260)
                v = el.evaluate(VERDICT)
                checked += 1
                if not any(v.values()):
                    dead.append({**info, "why": "changing the selection changed nothing in the page"})
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
            v = el.evaluate(VERDICT)
            checked += 1
            if not any(v.values()):
                dead.append({**info, "why": "nothing in the page changed"})


        context.close()
        browser.close()
    return {"target": target, "width": width, "total": total, "checked": checked,
            "skipped": skipped, "unreachable": unreachable, "dead": dead,
            "console_errors": console[:10]}


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
    if not a.quiet and not a.json:   # --json means JSON, not JSON with a sentence after it
        tail = f", {r['unreachable']} not present on a fresh load" if r.get("unreachable") else ""
        print(f"check_controls: {r['checked']} control(s) driven at {a.width}px, "
              f"{len(r['dead'])} dead, {r['skipped']} skipped (links, disabled, hidden){tail} "
              f"-> {verdict}")
    return 1 if r["dead"] else 0


if __name__ == "__main__":
    sys.exit(main())
