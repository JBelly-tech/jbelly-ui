#!/usr/bin/env python3
"""Runtime colour probe C01-C04: every painted pixel of text, in every personality the page ships.

preflight.py reads the declared tokens and checks the role pairs. That catches a palette nobody
could read. It cannot catch what the markup does with the palette, because a class like
`bg-success/15 text-success` names no role pair -- it names a fill and then paints that same fill as
text on a tint of itself. Whether that is readable depends on a composite the stylesheet never
states, and the answer changes with every preset.

So this drives the real engine: set the personality on <html>, let the tint transition settle, walk
every element that paints, composite the background the way the compositor does, and compare.

  C01 TEXT        every text run clears 4.5:1 against its own composited ground (3:1 when large)
  C02 ICON        every standalone icon clears 3:1
  C03 INVISIBLE   nothing paints a foreground equal to its own ground
  C04 REACHED     every personality declared in the page was actually applied and measured

The states are built here rather than requested through the page's own controls, for two reasons a
demo teaches quickly: a URL fragment is a same-document navigation, so a page that reads it once on
load never sees the second one; and a page that remembers dark mode will hand back the previous
state and read as a clean sweep.

Usage: python scripts/verify_theme.py <page.html> [--json] [--quiet] [--width 1440]
Exit 1 on any failure, 2 when the page is missing or could not be driven.
Without Playwright it prints [SKIP] and returns 0 WITHOUT claiming a pass.
"""
import argparse, json, math, os, pathlib, re, sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LARGE_PX = 24.0          # WCAG large text: 24px, or 18.66px at >=700
LARGE_BOLD_PX = 18.66
SETTLE_MS = 120          # layout only: the tint transition is switched off, see STILL


def srgb(c):
    """Any computed colour the engine hands back -> (r,g,b,a) in sRGB 0..1, or None."""
    c = (c or "").strip().lower()
    if not c or c == "transparent" or c == "none":
        return None
    m = re.match(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)\s*(?:[,/]\s*([\d.%]+))?\s*\)", c)
    if m:
        a = m.group(4)
        a = 1.0 if a is None else (float(a.rstrip("%")) / 100 if a.endswith("%") else float(a))
        return (float(m.group(1)) / 255, float(m.group(2)) / 255, float(m.group(3)) / 255, a)
    m = re.match(r"(oklch|oklab)\(\s*([\d.]+)(%?)\s+(-?[\d.]+)\s+(-?[\d.]+)\s*(?:/\s*([\d.%]+))?\s*\)", c)
    if m:
        L = float(m.group(2)) / (100 if m.group(3) else 1)
        if m.group(1) == "oklch":
            C, H = float(m.group(4)), math.radians(float(m.group(5)))
            a_, b_ = C * math.cos(H), C * math.sin(H)
        else:
            a_, b_ = float(m.group(4)), float(m.group(5))
        al = m.group(6)
        al = 1.0 if al is None else (float(al.rstrip("%")) / 100 if al.endswith("%") else float(al))
        l_ = L + 0.3963377774 * a_ + 0.2158037573 * b_
        m_ = L - 0.1055613458 * a_ - 0.0638541728 * b_
        s_ = L - 0.0894841775 * a_ - 1.2914855480 * b_
        l, m2, s = l_ ** 3, m_ ** 3, s_ ** 3
        r = 4.0767416621 * l - 3.3077115913 * m2 + 0.2309699292 * s
        g = -1.2684380046 * l + 2.6097574011 * m2 - 0.3413193965 * s
        bb = -0.0041960863 * l - 0.7034186147 * m2 + 1.7076147010 * s

        def gamma(v):
            v = min(1, max(0, v))
            return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
        return (gamma(r), gamma(g), gamma(bb), al)
    m = re.match(r"#([0-9a-f]{6})\b", c)
    if m:
        h = m.group(1)
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1.0,)
    if c in ("white", "#fff"):
        return (1, 1, 1, 1)
    if c == "black":
        return (0, 0, 0, 1)
    return None


def lum(rgb):
    def ch(v):
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def over(top, bottom):
    """src-over: a translucent colour composited onto an opaque one."""
    a = top[3]
    return tuple(top[i] * a + bottom[i] * (1 - a) for i in range(3)) + (1.0,)


def ground(stack):
    """stack is innermost-first; the page's own ground is last. Returns the opaque result."""
    base = None
    for c in reversed(stack):
        p = srgb(c)
        if p is None:
            continue
        base = p if (base is None or p[3] >= 1) else over(p, base)
    if base is None:
        return None
    return base if base[3] >= 1 else over(base, (1, 1, 1, 1))


# Collected per element: what it paints, what it paints on, and what would hide it anyway.
PROBE = r"""
(sel) => {
  const out = [];
  const seen = new Set();
  const path = el => {
    const b = [];
    for (let n = el; n && n.nodeType === 1 && b.length < 3; n = n.parentElement) {
      let s = n.tagName.toLowerCase();
      if (n.id) { b.unshift(s + '#' + n.id); break; }
      const c = (n.getAttribute('class') || '').split(/\s+/).filter(Boolean).slice(0, 3).join('.');
      b.unshift(c ? s + '.' + c : s);
    }
    return b.join(' > ');
  };
  document.querySelectorAll('*').forEach(el => {
    const tag = el.tagName.toLowerCase();
    if (tag === 'script' || tag === 'style' || tag === 'template' || tag === 'head' ||
        tag === 'title' || tag === 'meta' || tag === 'link') return;
    if (el.closest('[hidden]') || (sel && el.closest(sel))) return;
    let txt = '';
    for (const n of el.childNodes) if (n.nodeType === 3) txt += n.nodeValue;
    txt = txt.replace(/\s+/g, ' ').trim();
    const icon = tag === 'svg' || (tag === 'i' && el.hasAttribute('data-lucide'));
    if (!txt && !icon) return;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') return;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return;
    let op = 1, img = false;
    const bg = [];
    for (let n = el; n; n = n.parentElement) {
      const s = getComputedStyle(n);
      op *= parseFloat(s.opacity || '1');
      if (s.backgroundImage && s.backgroundImage !== 'none') img = true;
      bg.push(s.backgroundColor);
    }
    bg.push(getComputedStyle(document.documentElement).backgroundColor);
    if (op < 0.02) return;             // not painted at all; verify_motion.py owns that rule
    const key = path(el) + '|' + txt + '|' + cs.color + '|' + bg[0] + '|' + bg[1];
    if (seen.has(key)) return;         // a repeated row says the same thing as its first copy
    seen.add(key);
    out.push({
      icon: icon, path: path(el), text: txt.slice(0, 40),
      fg: icon ? ((cs.stroke && cs.stroke !== 'none') ? cs.stroke : cs.color) : cs.color,
      size: parseFloat(cs.fontSize) || 16, weight: String(cs.fontWeight),
      op: op, bg: bg, img: img,
      off: el.matches(':disabled') || el.closest('[disabled]') !== null ||
           el.closest('[aria-disabled="true"]') !== null
    });
  });
  return out;
}
"""

APPLY = r"""
([base, theme, dark]) => {
  const h = document.documentElement;
  h.className = [base, theme, dark ? 'dark' : ''].filter(Boolean).join(' ');
  return h.className;
}
"""

# Every surface in this system crossfades on a theme change. Sampled while that is running, the
# engine reports an interpolated oklab() -- the colour of the state being left, not the one being
# entered -- and a sweep then reports failures that describe a frame nobody sees, or misses real
# ones. Waiting it out is guesswork about a duration; switching it off is not. Resting colour is
# the only thing this file is about; verify_motion.py owns what moves.
STILL = r"""
() => {
  const s = document.createElement('style');
  s.id = 'jb-verify-theme-still';
  s.textContent = '*, *::before, *::after { transition: none !important; animation: none !important; }';
  document.head.appendChild(s);
}
"""


def states(src):
    """Every personality the page declares, light and dark. A page with none still has two."""
    themes = sorted(set(re.findall(r"\.(theme-[a-z][\w-]*)\s*(?:\.dark)?\s*\{", src)))
    return [("default", "")] + [(t, t) for t in themes]


def measure(rows, label, results):
    bad = []
    for r in rows:
        if r["off"] or r["img"]:
            continue                      # a disabled control may be dim; an image is not a colour
        fg = srgb(r["fg"])
        bg = ground(r["bg"])
        if fg is None or bg is None:
            continue
        if r["op"] < 0.999:
            fg = over((fg[0], fg[1], fg[2], fg[3] * r["op"]), bg)
        elif fg[3] < 1:
            fg = over(fg, bg)
        ratio = contrast(fg, bg)
        large = r["size"] >= LARGE_PX or (r["size"] >= LARGE_BOLD_PX and r["weight"] in ("700", "800", "900", "bold"))
        need = 3.0 if (r["icon"] or large) else 4.5
        rule = "C02 ICON" if r["icon"] else "C01 TEXT"
        if ratio < 1.15:
            rule = "C03 INVISIBLE"
        if ratio + 1e-9 >= need:
            continue
        bad.append({"rule": rule, "state": label, "path": r["path"], "text": r["text"],
                    "ratio": round(ratio, 2), "need": need, "fg": r["fg"]})
    results.extend(bad)
    return len(bad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=1000)
    ap.add_argument("--ignore", default="", help="CSS selector whose subtree is not part of the product")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    path = pathlib.Path(a.page)
    if not path.is_file():
        print("verify_theme: %s is not a file" % a.page, file=sys.stderr)
        return 2
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[SKIP] verify_theme: no renderer (pip install playwright && playwright install chromium)")
        print("       This is not a pass: the page was not measured.")
        return 0

    src = path.read_text(encoding="utf-8", errors="replace")
    plan = states(src)
    results, counted, reached = [], 0, []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": a.width, "height": a.height}, device_scale_factor=1)
        page = ctx.new_page()
        try:
            page.goto(path.resolve().as_uri(), wait_until="networkidle", timeout=60000)
        except Exception as e:
            browser.close()
            print("verify_theme: %s could not be driven: %s" % (path.name, e), file=sys.stderr)
            return 2
        page.wait_for_timeout(1200)            # charts and icons mount after the network settles
        page.evaluate(STILL)
        base = page.evaluate("() => document.documentElement.className")
        base = " ".join(c for c in base.split() if c != "dark" and not c.startswith("theme-"))
        for name, cls in plan:
            for dark in (False, True):
                got = page.evaluate(APPLY, [base, cls, dark])
                page.wait_for_timeout(SETTLE_MS)
                if (cls and cls not in got.split()) or (dark != ("dark" in got.split())):
                    results.append({"rule": "C04 REACHED", "state": "%s %s" % (name, "dark" if dark else "light"),
                                    "path": "html", "text": got, "ratio": 0, "need": 0, "fg": ""})
                    continue
                label = "%s %s" % (name, "dark" if dark else "light")
                reached.append(label)
                rows = page.evaluate(PROBE, a.ignore or None)
                counted += len(rows)
                measure(rows, label, results)
        browser.close()

    if a.json:
        print(json.dumps({"page": path.name, "states": reached, "painted": counted,
                          "findings": results}, indent=1))
    elif not a.quiet:
        by_rule = {}
        for f in results:
            by_rule.setdefault(f["rule"], []).append(f)
        for rule in ("C03 INVISIBLE", "C01 TEXT", "C02 ICON", "C04 REACHED"):
            hits = by_rule.get(rule, [])
            if not hits:
                continue
            print("[FAIL] %s  %d" % (rule, len(hits)))
            shown = {}
            for f in hits:
                k = (f["path"], f["text"])
                shown.setdefault(k, []).append(f)
            for (pth, txt), group in sorted(shown.items(), key=lambda kv: min(g["ratio"] for g in kv[1]))[:12]:
                worst = min(group, key=lambda g: g["ratio"])
                where = group[0]["state"] if len(group) == 1 else "%d states" % len(group)
                print("       %5.2f:1 (needs %.1f)  %s  %r  [%s]  fg %s"
                      % (worst["ratio"], worst["need"], pth[-54:], txt[:28], where, worst["fg"]))
            if len(shown) > 12:
                print("       ... and %d more" % (len(shown) - 12))
        if not results:
            print("[OK] C01-C04  %d painted element(s) across %d personality state(s), all readable"
                  % (counted, len(reached)))
        print("verify_theme: %s -> %s (%d state(s), %d painted, %d finding(s))"
              % (path.name, "PASS" if not results else "FAIL", len(reached), counted, len(results)))
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main())
