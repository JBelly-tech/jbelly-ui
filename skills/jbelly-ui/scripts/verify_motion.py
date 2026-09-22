#!/usr/bin/env python3
"""Runtime motion probe V01-V08: what source analysis cannot reach, checked in a real engine.

lint_motion.py reads what was written. This reads what the browser actually did with it, which is a
different question in exactly one way that matters: a page can pass every source rule and still not
animate at all, because the stylesheet was swallowed by a compiler, a selector never matched, or an
@starting-style landed in the wrong source order. V01 is that check, and it is the reason this file
exists.

Animations are sampled WHILE RUNNING - each control is driven, then probed 30ms later. The absence
of an Animation object is never evidence of compliance, so a rule that finds nothing reports how
many animations it saw.

  V01 CANARY         the tokens resolve, allow-discrete is supported, and the #jb-motion sheet is live
  V02 DECLARED-CAUSE every animating element resolves data-motion to one of the six causes
  V03 PROPERTY-TIER  every animated property is compositor, discrete, paint, or a declared exception
  V04 BUDGET         every duration is <= --motion-max and equals a resolved --t-* token
  V05 ONE-SUBJECT    at most one element animates a positional property per state change
  V06 SUBSTITUTE     a state that animated but carries no non-motion delta under reduce   (WARN)
  V07 RTL-MIRROR     inline-axis keyframe offsets are exact negatives between LTR and RTL
  V08 FIRST-PAINT    nothing animates in the 200ms after load, and nothing rests at opacity 0

Usage: python scripts/verify_motion.py <page.html> [--json] [--quiet]
Exit 1 on any FAIL, 2 when the page is missing or could not be driven.
Without Playwright it prints [SKIP] and returns 0 WITHOUT claiming a pass - an unverified page is
not a verified one, and saying so is the whole difference.
"""
import argparse, json, os, pathlib, re, sys

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

CAUSES = {"feedback", "state", "spatial", "continuity", "status", "position"}
COMPOSITE = {"transform", "translate", "rotate", "scale", "opacity", "clipPath", "filter",
             "backdropFilter", "offset", "offsetDistance"}
DISCRETE = {"display", "overlay", "contentVisibility", "visibility"}
PAINT = {"color", "backgroundColor", "borderColor", "borderTopColor", "borderRightColor",
         "borderBottomColor", "borderLeftColor", "borderBlockColor", "borderInlineColor",
         "outlineColor", "fill", "stroke", "boxShadow"}
POSITIONAL = {"transform", "translate", "scale", "rotate"}
MAX_CONTROLS = 60
# What a logical property becomes once the writing mode is known. getKeyframes() reports the
# resolved physical longhand, never the logical name the stylesheet was written in.
PHYSICAL = {"inlineSize": {"width"}, "blockSize": {"height"},
            "minInlineSize": {"minWidth"}, "minBlockSize": {"minHeight"},
            "maxInlineSize": {"maxWidth"}, "maxBlockSize": {"maxHeight"},
            "insetInlineStart": {"left", "right"}, "insetInlineEnd": {"left", "right"},
            "insetBlockStart": {"top", "bottom"}, "insetBlockEnd": {"top", "bottom"},
            "marginInlineStart": {"marginLeft", "marginRight"},
            "marginInlineEnd": {"marginLeft", "marginRight"},
            "paddingInlineStart": {"paddingLeft", "paddingRight"},
            "paddingInlineEnd": {"paddingLeft", "paddingRight"}}

# Collected 30ms after each action: what is running, on what, and why.
PROBE = r"""
() => {
  const skip = new Set(['offset', 'composite', 'computedOffset', 'easing']);
  const path = el => {
    const bits = [];
    for (let n = el; n && n.nodeType === 1 && bits.length < 4; n = n.parentElement) {
      let s = n.tagName.toLowerCase();
      if (n.id) { bits.unshift(s + '#' + n.id); break; }
      if (n.classList.length) s += '.' + [...n.classList].slice(0, 2).join('.');
      bits.unshift(s);
    }
    return bits.join(' > ');
  };
  // A panel travels by 100%, not by pixels: `translate` keeps percentages in its computed value,
  // so a px-only reader sees no inline-axis motion anywhere and reports a vacuous pass.
  const firstLen = v => {
    if (typeof v !== 'string') return null;
    const m = v.match(/translate(?:X|3d)?\(\s*(-?[\d.]+)(?:px|%)|^\s*(-?[\d.]+)(?:px|%)/);
    return m ? parseFloat(m[1] !== undefined ? m[1] : m[2]) : null;
  };
  const out = [];
  for (const a of document.getAnimations()) {
    const eff = a.effect, t = eff && eff.target;
    let frames = [];
    try { frames = eff.getKeyframes(); } catch (e) { frames = []; }
    const props = [...new Set(frames.flatMap(Object.keys))].filter(k => !skip.has(k));
    let dur = null;
    try { const d = eff.getTiming().duration; dur = typeof d === 'number' ? d : null; } catch (e) {}
    const xs = [];
    for (const f of frames) {
      for (const k of ['translate', 'transform']) {
        const n = firstLen(f[k]);
        if (n !== null) xs.push(n);
      }
    }
    const cause = t && t.closest('[data-motion]');
    out.push({
      id: a.id || '', pseudo: (eff && eff.pseudoElement) || '',
      kind: (a.constructor && a.constructor.name) || '',
      name: a.animationName || (a.constructor && a.constructor.name) || '',
      props, duration: dur, target: t ? path(t) : null,
      cause: cause ? cause.getAttribute('data-motion') : null,
      chart: t ? !!t.closest('.apexcharts-canvas') : false,
      group: t ? !!t.closest('[data-motion-group]') : false,
      x: xs
    });
  }
  return out;
}
"""

TOKENS = r"""
() => {
  const cs = getComputedStyle(document.documentElement);
  const v = n => cs.getPropertyValue(n).trim();
  // A custom property is not computed to a time - getPropertyValue returns the calc() as authored.
  // Feeding it to a real transition-duration is the only way to read what the engine resolved.
  const probe = document.createElement('div');
  probe.style.cssText = 'position:absolute;left:-9999px;top:0;width:1px;height:1px';
  document.body.appendChild(probe);
  const ms = n => {
    probe.style.transitionDuration = 'var(' + n + ')';
    const r = getComputedStyle(probe).transitionDuration;
    return r ? parseFloat(r) * 1000 : null;
  };
  const names = ['--t-press','--t-tint','--t-pop','--t-pop-out','--t-menu','--t-menu-out','--t-move',
                 '--t-panel','--t-panel-out','--t-heavy','--d-0','--t-grace','--t-elapsed','--t-linger'];
  const t = {};
  for (const n of names) t[n] = ms(n);
  const max = ms('--motion-max');
  probe.remove();
  let sheetRules = 0, sheetError = '';
  for (const s of document.styleSheets) {
    try { if (s.ownerNode && s.ownerNode.id === 'jb-motion') sheetRules += s.cssRules.length; }
    catch (e) { sheetError = e.name; }
  }
  return {
    tokens: t, max, reduced: v('--reduced'), travelOn: v('--travel-on'),
    discrete: CSS.supports('transition-behavior', 'allow-discrete'),
    startingStyle: CSS.supports('selector(:popover-open)'),
    sheetRules, sheetError, flowX: v('--flow-x')
  };
}
"""

# Everything the page can say without moving: the markup with transform and style noise removed,
# what is focused, and what any live region is announcing.
MEANING = r"""
  el => {
    const hash = t => { let h = 5381; for (let i = 0; i < t.length; i++) h = (h * 33 ^ t.charCodeAt(i)) >>> 0; return h.toString(36); };
    const scope = (el && (el.closest('section, main, [role=region], form, table') || document.body))
                  || document.body;
    const html = scope.outerHTML
      .replace(/\sstyle="[^"]*"/g, '')
      .replace(/\stranslate="[^"]*"/g, '')
      .replace(/\sdata-(?:open|leaving|refused)="[^"]*"/g, m => m);
    const live = [...document.querySelectorAll('[aria-live], [role=status], [role=alert]')]
      .map(n => n.textContent.trim()).join('|');
    const cs = el ? getComputedStyle(el) : null;
    return {
      // Hashed, not truncated: in an exclusive accordion the only difference between two
      // states is which sibling carries `open`, and a truncated snapshot of a long section
      // reports that as no difference at all.
      html: html.length + ':' + hash(html.replace(/\s+/g, ' ')),
      focus: document.activeElement ? document.activeElement.outerHTML.slice(0, 120) : '',
      live,
      paint: cs ? [cs.opacity, cs.backgroundColor, cs.borderColor, cs.boxShadow, cs.color].join('|') : '',
      text: el ? el.textContent.trim().slice(0, 200) : ''
    };
  }
"""

FIRST_PAINT = r"""
() => {
  const hidden = ['[hidden]', '[popover]', '[inert]', '[data-open]', '[data-reveal]',
                  '.panel', '.scrim', '.menu', '.apexcharts-canvas', '[class*="apexcharts"]'];
  const bad = [];
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.bottom < 0 || r.top > innerHeight || !r.width || !r.height) continue;
    if (hidden.some(s => el.closest(s))) continue;
    if (el.closest('[aria-hidden="true"]')) continue;
    if (!el.checkVisibility({ contentVisibilityAuto: true, opacityProperty: false })) continue;
    if (getComputedStyle(el).opacity === '0') {
      bad.push(el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
               (el.classList.length ? '.' + [...el.classList].slice(0, 2).join('.') : ''));
    }
    if (bad.length > 4) break;
  }
  return bad;
}
"""

# Everything that opens or changes something, including the triggers that are not buttons: a
# surface that only a data attribute opens is exactly the one whose entrance nobody re-checks.

PATH_ONE = r"""
  e => {
    const bits = [];
    for (let n = e; n && n.nodeType === 1 && bits.length < 4; n = n.parentElement) {
      let s = n.tagName.toLowerCase();
      if (n.id) { bits.unshift(s + '#' + n.id); break; }
      if (n.classList.length) s += '.' + [...n.classList].slice(0, 2).join('.');
      bits.unshift(s);
    }
    return bits.join(' > ');
  }
"""

DRIVE = ("button:not([disabled]), summary, [popovertarget], [role=tab], [role=switch], "
         "label:has(input[type=radio]), [data-open-drawer], [data-toggle-group]")


def selectors_with_exceptions(page_path):
    """[(selector token, {camelCase properties})] from every motion-exception comment in the page.

    The reason half of the comment names the properties the exception is for, so the exemption is
    scoped to those and not to everything that element ever animates. A rendered element path
    cannot carry a pseudo-element, so `.disclosure::details-content` reduces to `.disclosure` -
    which would excuse the whole subtree if the property set did not narrow it back.
    """
    try:
        text = pathlib.Path(page_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    out = {}
    for m in re.finditer(r"motion-exception:\s*(.+)", text):
        body = m.group(1).split("*/")[0].strip()
        parts = re.split(r"\s+[—–-]{1,2}\s+", body, maxsplit=1)
        if len(parts) != 2: continue
        sel = parts[0].split("::")[0].split(":")[0]
        token = re.findall(r"[#.][\w-]+", sel)
        if not token: continue
        props = set()
        for w in re.findall(r"[a-z]+(?:-[a-z]+)+", parts[1].split(":")[0]):
            camel = re.sub(r"-(\w)", lambda g: g.group(1).upper(), w)
            # The engine reports the physical longhand a logical property resolved to, so an
            # exception written in logical terms has to name both or it never matches.
            props |= {camel} | PHYSICAL.get(camel, set())
        out.setdefault(token[-1], set()).update(props)
    return sorted(out.items())


def drive(page, results, reduced=False):
    """Every control is activated, then probed 30ms later. Returns [(label, [animation records])]."""
    seen = []
    handles = page.query_selector_all(DRIVE)[:MAX_CONTROLS]
    for el in handles:
        try:
            if not el.is_visible(): continue
        except Exception:
            continue
        label = el.evaluate("e => (e.getAttribute('aria-label') || e.innerText || e.tagName)"
                            ".toString().trim().replace(/\\s+/g,' ').slice(0,32)")
        before = el.evaluate(MEANING)
        try:
            el.hover(timeout=800)
            el.click(timeout=1200)
        except Exception:
            continue
        page.wait_for_timeout(30)
        anims = page.evaluate(PROBE)
        after = el.evaluate(MEANING)
        seen.append({"i": len(seen), "label": label, "anims": anims, "before": before, "after": after,
                     "path": el.evaluate(PATH_ONE),
                     "target": el.evaluate("e => e.tagName.toLowerCase() + (e.id ? '#'+e.id : '')")})
        page.wait_for_timeout(120)
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        page.wait_for_timeout(60)
    return seen


def probe(target, exceptions):
    from playwright.sync_api import sync_playwright
    out = {"console": [], "results": [], "counts": {}}

    def add(status, rule, detail):
        out["results"].append({"status": status, "rule": rule, "detail": detail})

    with sync_playwright() as p:
        b = p.chromium.launch()
        viewport = {"width": 1440, "height": 1000}
        ctx = b.new_context(viewport=viewport)
        page = ctx.new_page()
        page.on("console", lambda m: out["console"].append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: out["console"].append(str(e)))
        page.goto(target, wait_until="networkidle", timeout=60000)

        # V08 first: it is the only rule whose evidence is destroyed by driving the page.
        page.wait_for_timeout(200)
        idle = [a for a in page.evaluate(PROBE)
                if not a["chart"] and a["duration"] not in (0, None)]
        if idle:
            add("FAIL", "V08 FIRST-PAINT",
                f"{len(idle)} animation(s) running 200ms after load with no input: "
                + ", ".join(sorted({a['target'] or a['pseudo'] or a['name'] for a in idle})[:4]))
        else:
            add("OK", "V08 FIRST-PAINT", "nothing animates after load")
        invisible = page.evaluate(FIRST_PAINT)
        if invisible:
            add("FAIL", "V08 FIRST-PAINT",
                f"{len(invisible)} visible element(s) rest at opacity 0: {', '.join(invisible[:4])}")

        env = page.evaluate(TOKENS)
        out["env"] = env
        why = []
        if not env["tokens"].get("--t-panel"): why.append("--t-panel does not resolve to a time")
        if not env["discrete"]: why.append("the engine has no transition-behavior: allow-discrete")
        if env["sheetError"]: why.append(f"the #jb-motion sheet could not be read ({env['sheetError']}) - unverifiable, not a pass")
        elif not env["sheetRules"]: why.append("no <style id=\"jb-motion\"> rules are live: the motion sheet never reached the document")
        add("FAIL" if why else "OK", "V01 CANARY", "; ".join(why) or
            f"--t-panel {env['tokens']['--t-panel']}ms, allow-discrete yes, {env['sheetRules']} motion rules live")

        runs = drive(page, out)
        all_anims = [a for r in runs for a in r["anims"]]
        out["counts"]["animations"] = len(all_anims)
        out["counts"]["controls"] = len(runs)

        # V02
        real = [a for a in all_anims if not a["chart"]
                and not a["pseudo"].startswith("::view-transition")]
        bad = [a for a in real if a["target"] is not None and a["cause"] not in CAUSES]
        add("FAIL" if bad else "OK", "V02 DECLARED-CAUSE",
            (f"{len(bad)} animation(s) with no data-motion cause: "
             + ", ".join(sorted({f"{a['target']} [{', '.join(a['props'])}]" for a in bad})[:4]))
            if bad else f"{len(all_anims)} animation(s) sampled, every one declares a cause")

        # V03
        allowed = COMPOSITE | DISCRETE | PAINT
        v3 = []
        for a in real:
            stray = [k for k in a["props"] if k not in allowed]
            if not stray: continue
            if a["target"] and any(tok in a["target"] and set(stray) <= props
                                   for tok, props in exceptions): continue
            v3.append(f"{a['target'] or a['pseudo']} animates {', '.join(stray)}")
        add("FAIL" if v3 else "OK", "V03 PROPERTY-TIER",
            "; ".join(sorted(set(v3))[:4]) if v3 else
            f"every animated property is compositor, discrete, paint or one of {len(exceptions)} declared exception(s): "
            + "; ".join(f"{t} {sorted(p)}" for t, p in exceptions))

        # V04
        budget = [v for k, v in env["tokens"].items() if v] + [0.0, 1.0]
        # --t-elapsed and --t-linger are not UI tempo: one is how long a wait has lasted, the other
        # how long a report stays readable. Neither belongs inside the 80-450ms budget.
        unscaled = [env["tokens"].get(n) for n in ("--t-elapsed", "--t-linger") if env["tokens"].get(n)]
        over = []
        for a in real:
            d = a["duration"]
            if d is None or d == 0: continue
            if any(abs(d - u) <= 1 for u in unscaled): continue
            if env["max"] and d > env["max"] + 1:
                over.append(f"{a['target'] or a['pseudo']} runs {d:.0f}ms (--motion-max {env['max']:.0f}ms)")
            elif a["kind"] == "CSSTransition":
                # A transition reversed before it finished is shortened by the engine, by design, so
                # its duration is a fraction of the token it was declared with. The ceiling still
                # applies; the exact-token check is what M03 already proves from source.
                continue
            elif not any(abs(d - t) <= 1 for t in budget) and d < 5000:
                over.append(f"{a['target'] or a['pseudo']} runs {d:.0f}ms, which is not a --t-* token")
        add("FAIL" if over else "OK", "V04 BUDGET",
            "; ".join(sorted(set(over))[:4]) if over else "every duration resolves to a token inside the budget")

        # V05 - the pressed control's own feedback is the same report, so it is not a second subject.
        v5 = []
        for r in runs:
            subjects = {a["target"] for a in r["anims"]
                        if not a["chart"] and a["target"]
                        and not a["pseudo"].startswith("::view-transition") and set(a["props"]) & POSITIONAL
                        and a["cause"] not in ("status", "position") and not a["group"]
                        and a["target"] != r["path"]}
            if len(subjects) > 1:
                v5.append(f"'{r['label']}' moved {len(subjects)}: {', '.join(sorted(subjects)[:3])}")
        add("FAIL" if v5 else "OK", "V05 ONE-SUBJECT",
            "; ".join(v5[:3]) if v5 else f"{len(runs)} state change(s), at most one positional subject each")

        # V07 - the same page in RTL, compared selector by selector.
        rtl = b.new_context(viewport=viewport).new_page()
        rtl.goto(target, wait_until="networkidle", timeout=60000)
        rtl.evaluate("() => { document.documentElement.setAttribute('dir', 'rtl'); }")
        rtl.wait_for_timeout(200)
        rtl_runs = drive(rtl, out)
        def by_sel(rs):
            m = {}
            for a in (x for r in rs for x in r["anims"]):
                if a["chart"] or a["id"] == "jb-flip" or a["pseudo"].startswith("::view-transition"): continue
                if not a["target"] or not a["x"]: continue
                xs = {x for x in a["x"] if x}
                if xs: m.setdefault(a["target"], set()).update(xs)
            return m
        l, r2 = by_sel(runs), by_sel(rtl_runs)
        v7 = []
        for sel, xs in l.items():
            if sel not in r2: continue
            if not any(any(abs(x + y) < 0.6 for y in r2[sel]) for x in xs):
                v7.append(f"{sel}: LTR {sorted(xs)} vs RTL {sorted(r2[sel])} are not negatives")
        add("FAIL" if v7 else "OK", "V07 RTL-MIRROR",
            "; ".join(v7[:3]) if v7 else
            f"{len(l)} selector(s) with inline-axis motion, every one mirrored (vertical-only motion is exempt)")
        rtl.close()

        # V06 - the same drive under reduce. WARN in v1: the highest false-positive risk of any rule.
        red = b.new_context(viewport=viewport).new_page()
        red.emulate_media(reduced_motion="reduce")
        red.goto(target, wait_until="networkidle", timeout=60000)
        red.wait_for_timeout(200)
        red_runs = drive(red, out, reduced=True)
        red_by = {r["i"]: r for r in red_runs}
        v6 = []
        for r in runs:
            moved = [a for a in r["anims"] if not a["chart"] and a["cause"] in
                     ("state", "spatial", "continuity") and set(a["props"]) & POSITIONAL]
            if not moved: continue
            rr = red_by.get(r["i"])
            if rr and rr["target"] != r["target"]: continue   # the passes diverged; pairing is not safe
            if not rr: continue
            was, af = rr["before"], rr["after"]
            same = (was["html"] == af["html"] and was["focus"] == af["focus"] and was["live"] == af["live"]
                    and was["paint"] == af["paint"] and was["text"] == af["text"])
            if same:
                v6.append(f"'{r['label']}' moved but reports nothing under reduce: no markup, focus, live-region or paint delta")
        add("WARN" if v6 else "OK", "V06 SUBSTITUTE",
            "; ".join(v6[:3]) if v6 else
            f"every positional state change carries a non-motion delta under reduce ({len(red_runs)} driven)")
        red_env = red.evaluate(TOKENS)
        if red_env["travelOn"] not in ("0", "0 "):
            add("FAIL", "V06 SUBSTITUTE",
                f"--travel-on is '{red_env['travelOn']}' under prefers-reduced-motion, expected 0 - the reduce contract is not wired")
        red.close()
        b.close()
    return out


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("page", help="an HTML file or a URL")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    try:
        import playwright  # noqa: F401
    except ImportError:
        # Not a pass. The page is simply unverified, and the verdict line has to say so.
        print("[SKIP] motion runtime: no Playwright - not verified "
              "(pip install playwright && playwright install chromium)")
        return 0

    target = a.page
    if "://" not in target:
        f = pathlib.Path(target)
        if not f.is_file():
            print(f"verify_motion: not a file: {target}", file=sys.stderr)
            return 2
        target = f.resolve().as_uri()

    exceptions = selectors_with_exceptions(a.page)
    try:
        out = probe(target, exceptions)
    except Exception as exc:
        print(f"verify_motion: could not drive the page: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 2

    fails = [r for r in out["results"] if r["status"] == "FAIL"]
    warns = [r for r in out["results"] if r["status"] == "WARN"]
    if out["console"]:
        fails.append({"status": "FAIL", "rule": "V00 CONSOLE", "detail": out["console"][0][:160]})
        out["results"].append(fails[-1])
    if a.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    elif not a.quiet:
        for r in out["results"]:
            print(f"[{r['status']}] {r['rule']:<20} {r['detail']}")
        print(f"\nverify_motion: {out['counts'].get('controls', 0)} control(s) driven, "
              f"{out['counts'].get('animations', 0)} animation(s) sampled, "
              f"{len(fails)} FAIL, {len(warns)} WARN -> {'FAIL' if fails else 'PASS'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
