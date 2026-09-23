#!/usr/bin/env python3
"""Motion lint (cross-platform, Class D): source rules M01-M14 for the jbelly-ui motion system.

Motion here reports a state change and nothing else. That is only a claim until a script can
refuse the opposite, so every principle in references/motion.md is one rule below, and each rule
is decidable from source alone - no browser, no render, no model.

The rules key off sentinels and exact token names rather than heuristics, which is what keeps the
false-positive rate near zero: the region between the MOTION TOKENS sentinels in tokens.css is the
one place a literal duration, curve or distance is legal, so every other literal is a finding by
construction rather than by guess.

  M01 RAW-TEMPO      a duration, easing or delay written as a literal outside the token region
  M02 TW-MOTION      a Tailwind motion utility in a class attribute or an @apply string
  M03 PROPERTY-TIER  an animated property outside compositor/discrete/paint tiers, a paint-tier
                     transition slower than --t-tint, or an animated focus ring
  M04 DISCRETE-TRIO  a display transition without allow-discrete, without a later @starting-style
                     for its open state, or a top-layer element that forgets overlay
  M05 REDUCE         a missing per-token reduce contract, or the blanket `* { !important }` block
  M06 SIGNED-INLINE  an authored inline-axis length or origin keyword that does not carry --flow-x
  M07 DOUBLE-MIRROR  measured geometry multiplied by the direction sign - it is already mirrored
  M08 NO-FRAME-LOOP  JavaScript drawing frames, or a banned animation dependency
  M09 NO-INFINITE    a loop where the system allows only a finite elapsed duration
  M10 NO-SCROLL      scroll-triggered reveal, scroll hijack, parallax, pointer-driven motion
  M11 FIRST-PAINT    an entrance at first paint, or a delay that is not 0 or --t-grace
  M12 NO-STAGGER     a delay derived from an index, in CSS or in JavaScript
  M13 TOKEN-BUDGET   a token outside the 80-450ms budget, a preset out of range, an out token
                     that is not faster than its enter sibling, an overreaching .theme-* block
  M14 ANIMATED-VALUE a count-up, an odometer, or per-character text splitting

Usage: python scripts/lint_motion.py <file-or-dir> [--json] [--quiet]
Exit 1 on any FAIL, 2 when there was nothing to check. Every finding prints file:line evidence.
Silence one line with a 'motion-lint-ignore' comment on it.

Markdown is not scanned. The refusal list, motion.md and this docstring all have to name the
things they refuse, and a linter that fails its own documentation teaches people to ignore it.
"""
import json, os, re, sys

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

EXT = {".html", ".htm", ".css", ".js", ".mjs", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".astro",
       ".razor", ".cshtml", ".php"}
SKIP_DIRS = {"node_modules", "dist", "build", ".git", ".next", "bin", "obj", "vendor", "__pycache__",
             "out", "evals"}
IGNORE = "motion-lint-ignore"

# The one file allowed to hand the engine a delta. Compared by basename so an inlined copy inside a
# single-file shell is recognised the same way (the shell declares it with the same id).
MOTION_JS = "motion.js"
SENTINEL_START, SENTINEL_END = "MOTION TOKENS START", "MOTION TOKENS END"

# ---- property tiers (P3) --------------------------------------------------------------------
COMPOSITE = {"transform", "translate", "rotate", "scale", "opacity", "clip-path", "filter",
             "backdrop-filter"}
DISCRETE = {"display", "overlay", "content-visibility"}
PAINT = ({"color", "background-color", "outline-color", "fill", "stroke", "border-color",
          "text-decoration-color", "caret-color", "accent-color", "column-rule-color"} |
         {f"border-{s}-color" for s in ("top", "right", "bottom", "left", "block", "inline",
                                        "block-start", "block-end", "inline-start", "inline-end")})
# Paint-tier transitions are capped at the paint token. Any longer and a colour change reads as an
# animation of its own rather than as the state it reports.
PAINT_DURATIONS = {"var(--t-tint)", "var(--t-press)", "var(--d-tint)", "var(--d-press)",
                   "var(--d-0)", "0s", "0ms", "0"}
# The focus ring is the one surface that must never lag the keyboard: a transitioned ring reads as
# input latency, not as feedback.
FOCUS_RING = {"outline", "outline-color", "outline-offset", "outline-width", "box-shadow", "all"}

TIME_LITERAL = re.compile(r"(?<![\w.#-])(\d+(?:\.\d+)?)(ms|s)(?![\w-])")
# A var() whose name says what it holds. The naming convention is the whole reason a shorthand can
# be read without resolving custom properties.
TIME_VAR = re.compile(r"var\(\s*--(?:t|d)-[\w-]+")
EASE_VAR = re.compile(r"var\(\s*--(?:ease|spring)-[\w-]+")
EASE_FN = re.compile(r"\b(?:cubic-bezier|linear|steps)\s*\(")
EASE_WORD = re.compile(r"(?<![\w-])(?:ease|ease-in|ease-out|ease-in-out|linear|step-start|step-end)(?![\w-])")
ZERO_TIME = {"0", "0s", "0ms"}
OPEN_MARKERS = ("[data-open]", ":popover-open", "[open]", "::backdrop", "[aria-expanded=\"true\"]",
                "[data-ready]", ":open")

BANNED_LIBS = ("gsap", "framer-motion", "motion-one", "@motionone", "aos", "lenis",
               "locomotive-scroll", "canvas-confetti", "tsparticles", "tw-animate-css",
               "tailwindcss-animate")
STYLE_PROPS = r"(?:transform|translate|rotate|scale|opacity|height|width|top|left|right|bottom|inset|margin|padding|animationDelay|transitionDelay)"
STYLE_WRITE = re.compile(r"\.style\s*\.\s*" + STYLE_PROPS + r"\s*=|"
                         r"\.style\s*\.\s*setProperty\s*\(\s*['\"](?!--)" + STYLE_PROPS)
ANIM_TIMELINE_OK = {".read-progress", ".app-seam::after"}


# ---- text plumbing ---------------------------------------------------------------------------

def line_index(text):
    """Offsets of every line start, so an offset becomes a 1-based line number by bisection."""
    out, i = [0], text.find("\n")
    while i != -1:
        out.append(i + 1); i = text.find("\n", i + 1)
    return out


def line_of(starts, off):
    lo, hi = 0, len(starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if starts[mid] <= off: lo = mid
        else: hi = mid - 1
    return lo + 1


def blank(text, a, b):
    """Replace [a,b) with spaces but keep every newline, so offsets and line numbers survive."""
    return text[:a] + "".join(c if c == "\n" else " " for c in text[a:b]) + text[b:]


def mask(text, kind):
    """Comments blanked out, offsets preserved. Every rule reads code, never a comment about code.

    String bodies are stepped over rather than blanked: a rule has to be able to see
    `import 'gsap'` and `addEventListener('wheel')`. Stepping over them is still necessary, because
    a URL inside a string contains //, and masking from there to the end of the line would hide
    real code behind a comment that was never there.
    """
    out = list(text); i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c in "\"'`" and kind in ("js", "css"):
            q, j = c, i + 1
            while j < n and text[j] != q:
                if text[j] == "\\": j += 1
                elif text[j] == "\n" and q != "`": break
                j += 1
            i = j + 1; continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2); j = n if j < 0 else j + 2
            for k in range(i, j):
                if text[k] != "\n": out[k] = " "
            i = j; continue
        if kind == "js" and c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i); j = n if j < 0 else j
            for k in range(i, j): out[k] = " "
            i = j; continue
        if kind == "html" and text.startswith("<!--", i):
            j = text.find("-->", i); j = n if j < 0 else j + 3
            for k in range(i, j):
                if text[k] != "\n": out[k] = " "
            i = j; continue
        i += 1
    return "".join(out)


def segments(path, text):
    """[(kind, start, masked_text_of_the_whole_file_with_everything_else_blanked)].

    Every segment keeps the file's own offsets, so one line index serves all of them and a finding
    inside an inlined <style> block reports the line a person would open.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".css": return [("css", 0, mask(text, "css"))]
    if ext in (".js", ".mjs", ".jsx", ".ts", ".tsx"): return [("js", 0, mask(text, "js"))]
    segs, css_spans, js_spans = [], [], []
    for m in re.finditer(r"<style\b[^>]*>", text, re.I):
        end = text.lower().find("</style>", m.end())
        css_spans.append((m.end(), len(text) if end < 0 else end))
    for m in re.finditer(r"<script\b([^>]*)>", text, re.I):
        end = text.lower().find("</script>", m.end())
        end = len(text) if end < 0 else end
        if not re.search(r"\bsrc\s*=", m.group(1), re.I): js_spans.append((m.end(), end))
    css = text
    for a, b in [s for s in js_spans]: css = blank(css, a, b)
    keep = css
    css = "".join(" " if c != "\n" else c for c in css)
    for a, b in css_spans: css = css[:a] + keep[a:b] + css[b:]
    if css_spans: segs.append(("css", 0, mask(css, "css")))
    js = text
    for a, b in css_spans: js = blank(js, a, b)
    keepj = js
    js = "".join(" " if c != "\n" else c for c in js)
    for a, b in js_spans: js = js[:a] + keepj[a:b] + js[b:]
    if js_spans: segs.append(("js", 0, mask(js, "js")))
    html = text
    for a, b in css_spans + js_spans: html = blank(html, a, b)
    segs.append(("html", 0, mask(html, "html")))
    return segs


# ---- a small CSS reader ------------------------------------------------------------------------

def parse_css(css):
    """[{prelude, ancestors, start, end, decls:[(prop, value, offset)]}] in source order.

    Small on purpose: braces, strings and parens, nothing else. It exists so a rule can ask "what
    does THIS selector transition" instead of matching a regex against a whole file, which is the
    difference between M03 having a false-positive rate and not having one.
    """
    rules, stack, i, n, buf = [], [], 0, len(css), 0
    def flush(a, b, node):
        txt = css[a:b].strip()
        if not txt or ":" not in txt: return
        prop, _, value = txt.partition(":")
        prop = prop.strip()
        if not re.fullmatch(r"-{0,2}[\w-]+", prop): return
        node["decls"].append((prop.lower(), value.strip(), a + (len(css[a:b]) - len(css[a:b].lstrip()))))
    while i < n:
        c = css[i]
        if c in "\"'":
            q, j = c, i + 1
            while j < n and css[j] != q:
                j += 2 if css[j] == "\\" else 1
            i = j + 1; continue
        if c == "(":
            depth, j = 1, i + 1
            while j < n and depth:
                if css[j] == "(": depth += 1
                elif css[j] == ")": depth -= 1
                j += 1
            i = j; continue
        if c == "{":
            stack.append({"prelude": " ".join(css[buf:i].split()), "start": buf,
                          "ancestors": tuple(s["prelude"] for s in stack), "decls": []})
            i += 1; buf = i; continue
        if c == "}":
            if stack:
                node = stack.pop(); flush(buf, i, node); node["end"] = i; rules.append(node)
            i += 1; buf = i; continue
        if c == ";":
            if stack: flush(buf, i, stack[-1])
            i += 1; buf = i; continue
        i += 1
    while stack:
        node = stack.pop(); node["end"] = n; rules.append(node)
    rules.sort(key=lambda r: r["start"])
    return rules


def strip_values(value):
    """A declaration value with quoted strings and url() bodies blanked - they are data, not CSS."""
    value = re.sub(r"\"[^\"]*\"|'[^']*'", '""', value)
    return re.sub(r"url\([^)]*\)", "url()", value)


def top_split(value, sep=","):
    """Split a value on a separator that is not inside parens."""
    out, depth, cur = [], 0, ""
    for ch in value:
        if ch == "(": depth += 1
        elif ch == ")": depth -= 1
        if ch == sep and depth == 0: out.append(cur); cur = ""
        else: cur += ch
    out.append(cur)
    return [p.strip() for p in out if p.strip()]


def tokens_of(part):
    """Whitespace split that keeps a function call whole: var(--a, 1) is one token."""
    out, depth, cur = [], 0, ""
    for ch in part:
        if ch == "(": depth += 1
        elif ch == ")": depth -= 1
        if ch.isspace() and depth == 0:
            if cur: out.append(cur); cur = ""
        else: cur += ch
    if cur: out.append(cur)
    return out


def is_time(tok):
    t = tok.strip()
    return bool(TIME_LITERAL.fullmatch(t) or TIME_VAR.match(t) or t in ZERO_TIME)


def is_ease(tok):
    t = tok.strip()
    return bool(EASE_VAR.match(t) or EASE_FN.match(t) or EASE_WORD.fullmatch(t))


def transition_parts(rule):
    """[(property, duration, delay, behaviour, offset)] for every transition this rule declares.

    Handles the shorthand and the longhands together, because a rule may narrow with
    transition-property and time it with transition-duration in the next declaration.
    """
    parts, props, dur = [], None, None
    for prop, value, off in rule["decls"]:
        v = strip_values(value)
        if prop == "transition":
            for part in top_split(v):
                times = [t for t in tokens_of(part) if is_time(t)]
                name = next((t for t in tokens_of(part)
                             if not is_time(t) and not is_ease(t) and t != "allow-discrete"), "")
                parts.append((name.lower(), times[0] if times else None,
                              times[1] if len(times) > 1 else None,
                              "allow-discrete" if "allow-discrete" in part else "", off))
        elif prop == "transition-property": props, props_off = [p.lower() for p in top_split(v)], off
        elif prop == "transition-duration": dur = top_split(v)[0] if top_split(v) else None
        elif prop == "transition-behavior": pass
    if props is not None:
        for p in props:
            parts.append((p, dur, None, "allow-discrete" if
                          any(d[0] == "transition-behavior" and "allow-discrete" in d[1]
                              for d in rule["decls"]) else "", props_off))
    return parts


def animation_times(rule):
    """[(kind, [time tokens], offset)] for every animation shorthand or delay longhand."""
    out = []
    for prop, value, off in rule["decls"]:
        v = strip_values(value)
        if prop == "animation":
            for part in top_split(v):
                out.append(("animation", [t for t in tokens_of(part) if is_time(t)], off))
        elif prop in ("animation-delay", "transition-delay"):
            out.append((prop, top_split(v), off))
    return out


# ---- findings --------------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.rows = []
    def add(self, path, starts, off, rule, evidence, text):
        ln = line_of(starts, off)
        src = text[starts[ln - 1]:(starts[ln] if ln < len(starts) else len(text))]
        if IGNORE in src: return
        self.rows.append({"file": path.replace("\\", "/"), "line": ln, "rule": rule,
                          "evidence": " ".join(str(evidence).split())[:160]})


# ---- the rules --------------------------------------------------------------------------------

def check_file(path, text, rep):
    starts = line_index(text)
    base = os.path.basename(path).lower()
    in_motion_js = base == MOTION_JS
    identity = identity_spans(path, text)
    segs = segments(path, text)
    css_text = next((s[2] for s in segs if s[0] == "css"), None)
    js_text = next((s[2] for s in segs if s[0] == "js"), None)
    html_text = next((s[2] for s in segs if s[0] == "html"), None)
    region = token_region(text)
    add = lambda off, rule, ev: rep.add(path, starts, off, rule, ev, text)

    if css_text is not None:
        rules = parse_css(css_text)
        exceptions = declared_exceptions(text)
        m01_css(css_text, region, rules, add)
        m03(rules, exceptions, add)
        m04(rules, add)
        m05(text, css_text, rules, add)
        m06(rules, add)
        m09_css(rules, add)
        m10_css(text, css_text, rules, add)
        m11(rules, add)
        m12_css(rules, add)
        m13(text, region, add)
        m13_overshoot(rules, add)
        m08_css(rules, in_motion_js, add)
    if js_text is not None:
        m01_js(js_text, in_motion_js, identity, add)
        m07(js_text, add)
        m08_js(js_text, in_motion_js, identity, add)
        m09_js(js_text, add)
        m10_js(js_text, add)
        m12_js(js_text, add)
        m14_js(js_text, add)
    if html_text is not None:
        m02(html_text, add)
        m08_html(html_text, add)
        m09_html(html_text, add)
        m10_html(html_text, add)
        m12_html(html_text, add)
        m14_html(html_text, add)
    if css_text is not None:
        m02_apply(css_text, add)


def identity_spans(path, text):
    """Where the identity module lives: the whole of assets/motion.js, or the <script id="jb-motion">
    block a single-file shell inlines it into. Inlining a file must not turn it into a violation,
    and the id is as explicit a declaration as the filename was."""
    if os.path.basename(path).lower() == MOTION_JS: return [(0, len(text))]
    spans = []
    for m in re.finditer(r"<script\b([^>]*)>", text, re.I):
        if re.search(r"""id\s*=\s*['\"]jb-motion['\"]""", m.group(1), re.I):
            end = text.lower().find("</script>", m.end())
            spans.append((m.end(), len(text) if end < 0 else end))
    return spans


def _inside(spans, off):
    return any(a <= off < b for a, b in spans)


def token_region(text):
    """(start, end) of the one region where a literal is legal, or None."""
    a = text.find(SENTINEL_START)
    b = text.find(SENTINEL_END, a + 1) if a >= 0 else -1
    return (a, b + len(SENTINEL_END)) if a >= 0 and b > a else None


def in_region(region, off):
    return bool(region) and region[0] <= off <= region[1]


def declared_exceptions(text):
    """{selector: reason} from every '/* motion-exception: <selector> - <reason> */' line.

    The reason is required. An exception with no written reason is a silent permission, and the
    whole point of naming them is that someone had to write down why.
    """
    out = {}
    for m in re.finditer(r"motion-exception:\s*(.+)", text):
        body = m.group(1).split("*/")[0].strip()
        parts = re.split(r"\s+[—–-]{1,2}\s+", body, maxsplit=1)
        if len(parts) == 2 and parts[1].strip():
            out[" ".join(parts[0].split())] = parts[1].strip()
    return out


# M01 -------------------------------------------------------------------------------------------

def m01_css(css, region, rules, add):
    """A literal duration, curve or bare easing keyword outside the sentinel-marked token region."""
    for r in rules:
        if r["prelude"].startswith("@") and not r["ancestors"]: pass
        for prop, value, off in r["decls"]:
            if in_region(region, off): continue
            v = strip_values(value)
            for m in TIME_LITERAL.finditer(v):
                if m.group(0) in ZERO_TIME: continue      # a zero is not a tempo choice
                add(off, "M01 RAW-TEMPO", f"{prop}: {value} - literal {m.group(0)}, use a var(--t-*) token")
            for fn in ("cubic-bezier(", "steps("):
                if fn in v.replace(" ", ""):
                    add(off, "M01 RAW-TEMPO", f"{prop}: {value} - literal easing {fn}), use a var(--ease-*) token")
            if re.search(r"linear\(\s*0", v):
                add(off, "M01 RAW-TEMPO", f"{prop}: {value} - literal linear() spring, use a var(--spring-*) token")
            slots = []
            if prop.endswith("timing-function"): slots = top_split(v)
            elif prop in ("transition", "animation"):
                slots = [t for part in top_split(v) for t in tokens_of(part)]
            for t in slots:
                if EASE_WORD.fullmatch(t.strip()):
                    add(off, "M01 RAW-TEMPO", f"{prop}: {value} - bare '{t.strip()}' in a timing slot, use a var(--ease-*) token")


def m01_js(js, in_motion_js, identity, add):
    if in_motion_js: return
    # A chart library's own entrance is motion nobody in this system approved, at the one moment
    # the rules forbid it: first paint.
    for m in re.finditer(r"animations\s*:\s*\{[^{}]*enabled\s*:\s*(?:true|!)", js):
        add(m.start(), "M01 RAW-TEMPO", "animations: { enabled: true } - a chart drawing itself in is motion at first paint; render with enabled: false")
    for m in re.finditer(r"(?<![\w$.])(speed|duration)\s*:\s*(\d+(?:\.\d+)?)\b", js):
        if m.group(2) in ("0", "0.0") or _inside(identity, m.start()): continue
        add(m.start(), "M01 RAW-TEMPO", f"{m.group(0)} - a literal tempo in JavaScript; read the token instead")


# M02 -------------------------------------------------------------------------------------------

VARIANT = re.compile(r"^(?:[\w-]+(?:\[[^\]]*\])?:)+")
TW_MOTION = (re.compile(r"^transition(?:-.+)?$"), re.compile(r"^duration-(?:\d+|\[.*\])$"),
             re.compile(r"^ease-(?:linear|in|out|in-out|\[.*\])$"),
             re.compile(r"^delay-(?:\d+|\[.*\])$"), re.compile(r"^animate-.+$"))


def _tw_hits(value):
    """Tailwind motion utilities in one class list, variants stripped first.

    `group-open:rotate-180` and `rtl:rotate-180` are END STATES, not motion, and must not match:
    stripping the variant prefix and testing the bare utility is what separates them.
    """
    hits = []
    for tok in value.split():
        base = VARIANT.sub("", tok).lstrip("!-")
        if any(p.match(base) for p in TW_MOTION): hits.append(tok)
    return hits


def m02(html, add):
    for m in re.finditer(r"\bclass(?:Name)?\s*=\s*(\"([^\"]*)\"|'([^']*)')", html):
        value = m.group(2) if m.group(2) is not None else m.group(3)
        for hit in _tw_hits(value):
            add(m.start(), "M02 TW-MOTION", f"class=\"...{hit}...\" - motion belongs in motion.css, not in a class attribute")


def m02_apply(css, add):
    for m in re.finditer(r"@apply\s+([^;}]+)", css):
        for hit in _tw_hits(m.group(1)):
            add(m.start(), "M02 TW-MOTION", f"@apply ...{hit}... - motion belongs in motion.css, not in an @apply string")


# M03 -------------------------------------------------------------------------------------------

def _covered(selector, exceptions):
    sel = " ".join(selector.split())
    return any(ex and ex in sel for ex in exceptions)


def m03(rules, exceptions, add):
    """Every animated property is compositor, declared-discrete, capped paint, or a named exception."""
    for r in rules:
        sel = r["prelude"]
        if sel.startswith("@"): continue
        focus = ":focus-visible" in sel or ":focus-within" in sel
        for prop, dur, _delay, behaviour, off in transition_parts(r):
            if prop in ("", "none"): continue
            if prop == "all":
                add(off, "M03 PROPERTY-TIER", f"{sel} transitions 'all' - name the properties; 'all' animates layout the moment a class adds padding")
                continue
            if focus:
                # A bare transition-property list NARROWS what may animate and cannot by itself make
                # the ring move, so border-color is only a finding in the timed shorthand form.
                ring = FOCUS_RING | ({"border-color"} if dur else set())
                if prop in ring:
                    add(off, "M03 PROPERTY-TIER", f"{sel} transitions {prop} - the focus ring is never animated; a transitioned ring reads as input latency")
                    continue
            if prop == "filter" and any("blur(" in v.replace(" ", "")
                                        for p2, v, _ in r["decls"] if p2 == "filter"):
                add(off, "M03 PROPERTY-TIER", f"{sel} transitions a filter containing blur() - blurring text is illegible for the whole duration, not stylish")
                continue
            if prop in COMPOSITE: continue
            if prop in DISCRETE:
                if "allow-discrete" not in behaviour:
                    add(off, "M03 PROPERTY-TIER", f"{sel} transitions {prop} without allow-discrete - the discrete step never runs")
                continue
            if prop in PAINT:
                if dur and dur not in PAINT_DURATIONS:
                    add(off, "M03 PROPERTY-TIER", f"{sel} transitions {prop} for {dur} - paint tier is capped at var(--t-tint)")
                continue
            if not _covered(sel, exceptions):
                add(off, "M03 PROPERTY-TIER", f"{sel} transitions {prop} - outside every tier and with no '/* motion-exception: {sel} - <reason> */' line")
        if "@keyframes" in " ".join(r["ancestors"]):
            for prop, value, off in r["decls"]:
                if prop.startswith("--") or prop in ("animation-timing-function",): continue
                if prop in COMPOSITE or prop in DISCRETE: continue
                frames = next((a for a in r["ancestors"] if a.startswith("@keyframes")), "@keyframes")
                if prop in PAINT: continue
                if not _covered(frames, exceptions):
                    add(off, "M03 PROPERTY-TIER", f"{frames} animates {prop} - outside every tier and with no motion-exception line")


# M04 -------------------------------------------------------------------------------------------

def m04(rules, add):
    """display transitions need allow-discrete, a LATER @starting-style, and overlay in the top layer."""
    starting = [(r["prelude"], r["start"]) for r in rules
                if any(a == "@starting-style" for a in r["ancestors"]) and not r["prelude"].startswith("@")]
    for r in rules:
        sel = r["prelude"]
        if sel.startswith("@"): continue
        parts = transition_parts(r)
        disp = [p for p in parts if p[0] == "display"]
        if not disp: continue
        if "allow-discrete" not in disp[0][3]:
            add(disp[0][4], "M04 DISCRETE-TRIO", f"{sel} transitions display without allow-discrete")
        for one in top_split(sel):
            flat = one.replace(" ", "")
            ok = False
            for st_sel, st_off in starting:
                if st_off <= r["start"]: continue          # equal specificity: source order decides
                for st_one in top_split(st_sel):
                    tail = st_one.replace(" ", "")
                    if tail.startswith(flat) and tail[len(flat):len(flat) + 1] in ("[", ":"):
                        ok = True
            if not ok:
                add(disp[0][4], "M04 DISCRETE-TRIO", f"{sel} transitions display but no @starting-style for its open state appears LATER in the file - the entrance silently does nothing")
        if "[popover]" in sel or re.search(r"(?<![\w-])dialog(?![\w-])", sel):
            if not any(p[0] == "overlay" for p in parts):
                add(disp[0][4], "M04 DISCRETE-TRIO", f"{sel} is in the top layer and does not transition overlay - it disappears before it fades")


# M05 -------------------------------------------------------------------------------------------

BLANKET = re.compile(r"^\*(?:\s*,\s*\*(?:::?(?:before|after))?)*$")


def m05(text, css, rules, add):
    """The reduce contract is two tokens, never a blanket override."""
    region = token_region(text)
    if region:
        body = text[region[0]:region[1]]
        reduce_blocks = [r for r in rules if any("prefers-reduced-motion" in a for a in r["ancestors"])
                         or "prefers-reduced-motion" in r["prelude"]]
        declared = {p for r in reduce_blocks for p, _, off in r["decls"] if in_region(region, off)}
        if "--travel-on" not in declared or "--motion-reduce" not in declared:
            add(region[0], "M05 REDUCE", "the MOTION TOKENS region has no @media (prefers-reduced-motion: reduce) block setting --travel-on: 0 and --motion-reduce")
        elif not re.search(r"--travel-on\s*:\s*0\b", body[body.find("prefers-reduced-motion"):] if "prefers-reduced-motion" in body else ""):
            add(region[0], "M05 REDUCE", "the reduce block does not set --travel-on: 0")
    for r in rules:
        if not (any("prefers-reduced-motion" in a for a in r["ancestors"])): continue
        if not BLANKET.match(r["prelude"].replace(" ", "").replace("*,", "*, ").replace(", ", ",").replace(",", ", ").strip() or "x"):
            flat = "".join(r["prelude"].split())
            if not BLANKET.match(flat): continue
        for prop, value, off in r["decls"]:
            if prop.endswith("-duration") and "!important" in value:
                add(off, "M05 REDUCE", f"blanket reduce override {r['prelude']} {{ {prop}: {value} }} - it freezes loading indicators and never reaches ::view-transition-*; set --travel-on and --motion-reduce instead")


# M06 -------------------------------------------------------------------------------------------

INLINE_PROPS = {"translate", "transform", "left", "right", "margin-inline-start",
                "margin-inline-end", "inset-inline-start", "inset-inline-end"}
ZERO_LEN = re.compile(r"^-?0(?:\.0+)?(?:px|%|em|rem|vw|vh|ch)?$")


def _first_inline(prop, value):
    """The inline-axis component of an authored displacement, or None when there is not one."""
    v = strip_values(value).strip()
    if prop == "translate":
        toks = tokens_of(v)
        return toks[0] if toks else None
    if prop == "transform":
        m = re.search(r"translateX\s*\(([^)]*)\)", v)
        if m: return m.group(1).strip()
        m = re.search(r"translate3?d?\s*\(([^)]*)\)", v)
        if m: return top_split(m.group(1))[0] if top_split(m.group(1)) else None
        return None
    return v


def m06(rules, add):
    """Authored inline-axis motion carries --flow-x; an origin keyword is var(--origin-inline)."""
    for r in rules:
        sel = r["prelude"]
        anc = " ".join(r["ancestors"])
        animated = {p[0] for p in transition_parts(r)}
        in_frames = "@keyframes" in anc
        in_start = "@starting-style" in anc or sel == "@starting-style"
        moves = {p[0] for p in transition_parts(r)} | ({"translate", "transform"} if in_frames or in_start else set())
        for prop, value, off in r["decls"]:
            if prop == "transform-origin":
                v = strip_values(value)
                if re.search(r"(?<![\w-])(left|right)(?![\w-])", v):
                    add(off, "M06 SIGNED-INLINE", f"{sel} transform-origin: {value} - a hard-coded inline origin; use var(--origin-inline)")
                elif re.fullmatch(r"(center|50%)(\s+(center|50%))?", v.strip()) and \
                        "panel-centre" not in sel and (moves & {"translate", "transform", "scale", "rotate"}):
                    add(off, "M06 SIGNED-INLINE", f"{sel} transform-origin: {value} - a centred origin says nothing about where the surface came from")
                continue
            if prop not in INLINE_PROPS: continue
            if not (in_frames or in_start or prop in animated): continue
            x = _first_inline(prop, value)
            if x is None or ZERO_LEN.match(x) or x in ("none", "auto", "0"): continue
            if "var(--flow-x)" in x.replace(" ", ""): continue
            add(off, "M06 SIGNED-INLINE", f"{sel} {prop}: {value} - an authored inline-axis length with no var(--flow-x); it points the wrong way in RTL")


# M07 -------------------------------------------------------------------------------------------

DIRECTION = re.compile(r"--flow-x|(?<![\w$])flow_?X(?![\w$])|(?<![\w$])(?:isRtl|isRTL|rtl)(?![\w$])"
                       r"|dir\s*===?\s*['\"]rtl['\"]|direction\s*===?\s*['\"]rtl['\"]")


def m07(js, add):
    """Measured geometry multiplied by the direction sign - the double-mirror bug.

    Scoped to one statement, not one function: a file may legitimately read --flow-x for something
    that is not a measurement, and failing that would make the rule unusable in the one file where
    measurement happens.
    """
    rects = set()
    for m in re.finditer(r"(?:const|let|var)\s+(?:\{([^}]*)\}|([\w$]+))\s*=\s*[^;\n]*getBoundingClientRect\s*\(", js):
        if m.group(1): rects |= {p.split(":")[-1].strip() for p in m.group(1).split(",") if p.strip()}
        else: rects.add(m.group(2))
    if not rects: return
    # A rect is only geometry through its fields. Requiring `r.left` rather than a bare `r` is what
    # keeps the rule usable: rect variables are routinely one letter, and a bare `r` also names the
    # second parameter of every little query helper on the page.
    field = r"\s*\.\s*(?:left|right|top|bottom|width|height|x|y)(?![\w$])"
    access = re.compile("|".join(rf"(?<![\w$]){re.escape(v)}{field}" for v in sorted(rects)))
    derived = set()
    for m in re.finditer(r"(?:const|let|var)\s+([\w$]+)\s*=\s*([^;\n]+)", js):
        if access.search(m.group(2)): derived.add(m.group(1))
    for stmt in re.finditer(r"[^;\n{}]+", js):
        s = stmt.group(0)
        if not DIRECTION.search(s): continue
        if access.search(s) or any(re.search(rf"(?<![\w$]){re.escape(v)}(?![\w$])", s) for v in derived):
            add(stmt.start(), "M07 DOUBLE-MIRROR", f"{s.strip()} - measured geometry is already mirrored; multiplying it by the direction sign sends the element the wrong way")


# M08 -------------------------------------------------------------------------------------------

def _block_around(text, idx, levels=2):
    """The enclosing brace block, widened by `levels` ancestors - an approximation of 'this function'."""
    opens, stack = [], []
    for i, c in enumerate(text):
        if c == "{": stack.append(i)
        elif c == "}" and stack:
            a = stack.pop()
            if a <= idx <= i: opens.append((a, i))
    opens.sort(key=lambda p: p[1] - p[0])
    if not opens: return text
    a, b = opens[min(levels, len(opens) - 1)]
    return text[a:b]


def m08_js(js, in_motion_js, identity, add):
    """JavaScript may flip a state attribute and hand over a measured delta. It may not draw."""
    for m in re.finditer(r"(?<![\w$.])requestAnimationFrame\s*\(", js):
        if STYLE_WRITE.search(_block_around(js, m.start())):
            add(m.start(), "M08 NO-FRAME-LOOP", "requestAnimationFrame in a function that writes a motion style - declare the change in CSS and let the engine draw it")
    for m in re.finditer(r"(?<![\w$.])(setInterval|setTimeout)\s*\(", js):
        j, depth = m.end(), 1
        while j < len(js) and depth:
            if js[j] == "(": depth += 1
            elif js[j] == ")": depth -= 1
            j += 1
        if STYLE_WRITE.search(js[m.end():j]):
            add(m.start(), "M08 NO-FRAME-LOOP", f"{m.group(1)} callback writes a motion style - a timer is not a timeline")
    if not in_motion_js:
        for pat, why in ((r"\.animate\s*\(", "element.animate("),
                         (r"(?<![\w$.])startViewTransition\s*\(", "startViewTransition("),
                         (r"(?<![\w$])viewTransitionName(?![\w$])", "viewTransitionName")):
            for m in re.finditer(pat, js):
                if _inside(identity, m.start()): continue
                add(m.start(), "M08 NO-FRAME-LOOP", f"{why} outside assets/motion.js - the identity module is the one sanctioned place for it")
    # A magnetic button, a tilt card and a cursor follower are one mechanism: the pointer writes a
    # transform. None of them reports a state change, and none of them exists on a keyboard.
    for m in re.finditer(r"""addEventListener\s*\(\s*['"](?:mousemove|pointermove)['"]""", js):
        window = js[m.start():m.start() + 600]
        if re.search(r"""\.style\s*\.\s*(?:transform|translate|rotate|scale)\s*=""", window) or \
           re.search(r"""setProperty\s*\(\s*['"]--(?:mouse|cursor|tilt|pointer)""", window):
            add(m.start(), "M08 NO-FRAME-LOOP", "a pointermove handler writing a transform - pointer-driven motion reports the pointer, not a state change, and does not exist on a keyboard")
    for m in re.finditer(r"""(?:import[^;\n]*from\s*|require\s*\(\s*)['"]([^'"]+)['"]""", js):
        spec = m.group(1).split("/")[0] if not m.group(1).startswith("@") else "/".join(m.group(1).split("/")[:2])
        if spec in BANNED_LIBS or m.group(1) in BANNED_LIBS or (spec == "motion" and not m.group(1).startswith(".")):
            add(m.start(), "M08 NO-FRAME-LOOP", f"import '{m.group(1)}' - a banned animation dependency; this system ships platform CSS and the Web Animations API only")


def m08_css(rules, in_motion_js, add):
    for r in rules:
        for prop, value, off in r["decls"]:
            if prop == "view-transition-name" and strip_values(value).strip() not in ("none", ""):
                add(off, "M08 NO-FRAME-LOOP", f"view-transition-name: {value} - names are leased at runtime from data-vt-key by motion.js, never authored")
            if prop == "cursor" and strip_values(value).strip() == "none":
                add(off, "M08 NO-FRAME-LOOP", "cursor: none - a cursor follower replaces the pointer the operating system already drew")
            if prop == "will-change":
                add(off, "M08 NO-FRAME-LOOP", f"will-change: {value} - a static stylesheet cannot know when the hint stops being a lie")


def m08_html(html, add):
    for m in re.finditer(r"<script\b[^>]*\bsrc\s*=\s*[\"']([^\"']+)[\"']", html, re.I):
        url = m.group(1)
        if "//" not in url and "node_modules" not in url: continue   # a local file is this repo's own
        for lib in BANNED_LIBS + ("motion",):
            if re.search(rf"(?<![\w-]){re.escape(lib)}(?:[@./-]|\.min|$)", url):
                add(m.start(), "M08 NO-FRAME-LOOP", f"<script src=\"{url}\"> - a banned animation dependency")
                break


# M09 -------------------------------------------------------------------------------------------

INFINITE = re.compile(r"(?<![\w-])infinite(?![\w-])")


def m09_css(rules, add):
    for r in rules:
        for prop, value, off in r["decls"]:
            if prop == "animation-iteration-count":
                add(off, "M09 NO-INFINITE", f"animation-iteration-count: {value} - waiting is an elapsed duration, not a loop")
            elif INFINITE.search(strip_values(value)):
                add(off, "M09 NO-INFINITE", f"{prop}: {value} - 'infinite' appears nowhere in this system")


def m09_js(js, add):
    for m in re.finditer(r"iterations\s*:\s*Infinity|(?<![\w$.])Infinity\s*(?=\})", js):
        add(m.start(), "M09 NO-INFINITE", f"{m.group(0)} - an endless Web Animations loop")


TW_ANIMATE = re.compile(r"(?<![\w-])animate-(?:spin|ping|pulse|bounce|marquee)(?![\w-])")


def m09_html(html, add):
    for m in TW_ANIMATE.finditer(html):
        add(m.start(), "M09 NO-INFINITE", f"{m.group(0)} - an infinite loop with no role; use the finite elapsed bar (.pends)")


# M10 -------------------------------------------------------------------------------------------

SCROLL_JS = [(r"(?<![\w$])AOS\s*\.\s*init\s*\(", "AOS.init("), (r"(?<![\w$])whileInView(?![\w$])", "whileInView"),
             (r"(?<![\w$])useInView\s*\(", "useInView("), (r"(?<![\w$])(?:Lenis|LocomotiveScroll|ScrollSmoother)(?![\w$])", "a scroll-hijack library"),
             (r"ScrollTrigger[\s\S]{0,200}?(?:pin\s*:|scrub\s*:)", "ScrollTrigger with pin/scrub")]


def m10_js(js, add):
    for pat, why in SCROLL_JS:
        for m in re.finditer(pat, js):
            add(m.start(), "M10 NO-SCROLL", f"{why} - scroll position reports the viewport moving, not anything changing")
    for m in re.finditer(r"(?<![\w$.])IntersectionObserver\s*\(", js):
        block = _block_around(js, m.start(), levels=1)
        if re.search(r"\.style\s*\.\s*(?:opacity|transform|translate|scale)\s*=", block):
            add(m.start(), "M10 NO-SCROLL", "IntersectionObserver writing opacity or a transform - a scroll-triggered reveal")
    for m in re.finditer(r"addEventListener\s*\(\s*['\"]wheel['\"]", js):
        j = js.find(")", m.start())
        if "preventDefault" in js[m.start():m.start() + 400]:
            add(m.start(), "M10 NO-SCROLL", "a wheel listener calling preventDefault() - scroll hijack")


def m10_css(text, css, rules, add):
    smooth, reduce_scroll = None, False
    for r in rules:
        sel, anc = r["prelude"], " ".join(r["ancestors"])
        for prop, value, off in r["decls"]:
            v = strip_values(value).strip()
            if prop == "animation-timeline" and "".join(sel.split()) not in ANIM_TIMELINE_OK:
                add(off, "M10 NO-SCROLL", f"{sel} {{ animation-timeline: {value} }} - only .read-progress and .app-seam::after may be driven by scroll")
            if prop == "background-attachment" and "fixed" in v:
                add(off, "M10 NO-SCROLL", f"background-attachment: {value} - parallax")
            if prop == "scroll-behavior":
                if "smooth" in v and "prefers-reduced-motion" not in anc: smooth = off
                if "prefers-reduced-motion" in anc: reduce_scroll = True
        if sel.startswith("@"): continue
        props = {p for p, _, _ in r["decls"]}
        if "pointer-events" in props and "opacity" in props:
            pe = next(v for p, v, _ in r["decls"] if p == "pointer-events")
            op = next(v for p, v, _ in r["decls"] if p == "opacity")
            gate = ("::before" in sel or "::after" in sel or ":before" in sel or ":after" in sel or
                    "[data-leaving]" in sel or "[hidden]" in sel or "aria-hidden" in sel or "[inert]" in sel)
            if "none" in pe and op.strip() in ("0", "0.0") and not gate:
                off = next(o for p, _, o in r["decls"] if p == "pointer-events")
                add(off, "M10 NO-SCROLL", f"{sel} {{ opacity: 0; pointer-events: none }} - a reveal gate: the content is hidden until something scrolls it in")
    if smooth is not None and not reduce_scroll:
        add(smooth, "M10 NO-SCROLL", "scroll-behavior: smooth with no prefers-reduced-motion override in the same file")


def m10_html(html, add):
    for m in re.finditer(r"\bdata-(?:aos|speed|parallax)(?![\w-])", html):
        add(m.start(), "M10 NO-SCROLL", f"{m.group(0)} - a scroll-triggered reveal or a parallax hook")
    for m in re.finditer(r"cursor\s*:\s*none(?![\w-])", html):
        add(m.start(), "M10 NO-SCROLL", "cursor: none - a cursor follower replaces the pointer the OS drew")


# M11 -------------------------------------------------------------------------------------------

def m11(rules, add):
    """No entrance at first paint, and every delay is 0 or var(--t-grace)."""
    for r in rules:
        sel, anc = r["prelude"], " ".join(r["ancestors"])
        if "@starting-style" in anc and not sel.startswith("@"):
            if not any(mk in sel for mk in OPEN_MARKERS):
                add(r["start"], "M11 FIRST-PAINT", f"@starting-style {{ {sel} }} - no post-load or open-state gate, so it animates the page's own arrival")
        for kind, times, off in animation_times(r):
            if kind == "animation":
                delay = times[1] if len(times) > 1 else None
            else:
                delay = times[0] if times else None
            if delay is None: continue
            d = delay.strip()
            if d in ZERO_TIME or d.replace(" ", "") == "var(--t-grace)": continue
            add(off, "M11 FIRST-PAINT", f"{kind} delay {d} - every delay is 0s or var(--t-grace); a set arriving is one report, not N")


# M12 -------------------------------------------------------------------------------------------

INDEX_MUL = re.compile(r"(?:var\(\s*--(?:i|idx|index|n)\s*\)|(?<![\w$])(?:i|idx|index)(?![\w$]))\s*[*]|"
                       r"[*]\s*(?:var\(\s*--(?:i|idx|index|n)\s*\)|(?<![\w$])(?:i|idx|index)(?![\w$]))")


def m12_css(rules, add):
    for r in rules:
        for prop, value, off in r["decls"]:
            if "delay" not in prop: continue
            v = strip_values(value)
            if INDEX_MUL.search(v) or "sibling-index()" in v.replace(" ", ""):
                add(off, "M12 NO-STAGGER", f"{prop}: {value} - a delay derived from a position; a set arriving is one report, not N")


def m12_js(js, add):
    for m in re.finditer(r"(?<![\w$.])stagger\s*\(|(?<![\w$.])staggerChildren(?![\w$])", js):
        add(m.start(), "M12 NO-STAGGER", f"{m.group(0)} - stagger is cut from this system in every form")
    for m in re.finditer(r"(?:delay|animationDelay|transitionDelay)\s*[:=]\s*([^,;\n)]+)", js):
        if INDEX_MUL.search(m.group(1)):
            add(m.start(), "M12 NO-STAGGER", f"{m.group(0).strip()} - a delay derived from a loop index")


def m12_html(html, add):
    ladder = []
    for m in re.finditer(r"style\s*=\s*[\"'][^\"']*?(?:animation-delay|transition-delay)\s*:\s*([\d.]+)(m?s)", html, re.I):
        ladder.append((m.start(), float(m.group(1)) * (1 if m.group(2) == "ms" else 1000)))
    for i in range(len(ladder) - 2):
        a, b, c = ladder[i][1], ladder[i + 1][1], ladder[i + 2][1]
        if 0 <= a < b < c:
            add(ladder[i][0], "M12 NO-STAGGER", f"inline delays {a:g}ms, {b:g}ms, {c:g}ms on consecutive elements - a hand-written stagger ladder")
            break


# M13 -------------------------------------------------------------------------------------------

THEME_KEYS = {"--motion-preset", "--ease-enter", "--press-depth", "--pop-depth"}
BUDGET_EXEMPT = {"--d-0", "--t-grace", "--t-elapsed", "--t-linger"}


def _ms(v):
    m = TIME_LITERAL.fullmatch(v.strip())
    if not m: return None
    return float(m.group(1)) * (1 if m.group(2) == "ms" else 1000)


OVERSHOOT_NOTE = ("an overshoot on a clamped value - opacity, a colour, a scale at its limit - "
                  "is a visible dead hold, not a bounce")


def m13_overshoot(rules, add):
    """No curve in this system has a stop above 1. Checked wherever a curve is written."""
    for r in rules:
        for prop, value, off in r["decls"]:
            v = strip_values(value)
            for m in re.finditer(r"linear\(([^()]*)\)", v):
                for part in m.group(1).split(","):
                    n = part.strip().split()
                    if n and re.fullmatch(r"-?\d*\.?\d+", n[0]) and float(n[0]) > 1:
                        add(off, "M13 TOKEN-BUDGET", f"{prop}: linear() stop {n[0]} is above 1 - {OVERSHOOT_NOTE}")
            for m in re.finditer(r"cubic-bezier\(([^()]*)\)", v):
                nums = [x.strip() for x in m.group(1).split(",")]
                if len(nums) == 4:
                    try: ys = [float(nums[1]), float(nums[3])]
                    except ValueError: continue
                    if max(ys) > 1 or min(ys) < 0:
                        add(off, "M13 TOKEN-BUDGET", f"{prop}: cubic-bezier control point y={max(ys, key=abs)} leaves 0..1 - {OVERSHOOT_NOTE}")


def m13(text, region, add):
    """The token region has to stay inside the budget it claims to enforce."""
    if not region: return
    body = text[region[0]:region[1]]
    rules = parse_css(mask(body, "css"))
    off0 = region[0]
    bases, presets, densities = {}, [], []
    for r in rules:
        if any("prefers-reduced-motion" in a for a in r["ancestors"]): continue
        for prop, value, off in r["decls"]:
            if prop.startswith("--d-") and prop not in BUDGET_EXEMPT:
                v = _ms(value)
                if v is not None: bases[prop] = (v, off0 + off)
            elif prop == "--motion-preset":
                try: presets.append((float(value.strip()), off0 + off))
                except ValueError: pass
            elif prop == "--travel-density":
                try: densities.append((float(value.strip()), off0 + off))
                except ValueError: pass
    for p, off in presets:
        if not (0.85 <= p <= 1.15):
            add(off, "M13 TOKEN-BUDGET", f"--motion-preset: {p} - a personality may set 0.85 to 1.15 and nothing else")
    for d, off in densities:
        if not (0.75 <= d <= 1.25):
            add(off, "M13 TOKEN-BUDGET", f"--travel-density: {d} - a density may set 0.75 to 1.25 and nothing else")
    scale = [p for p, _ in presets if 0.85 <= p <= 1.15] or [1.0]
    for name, (base, off) in bases.items():
        for p in (min(scale), max(scale)):
            r = base * p
            if not (80 <= r <= 450):
                add(off, "M13 TOKEN-BUDGET", f"{name}: {base:g}ms resolves to {r:g}ms at --motion-preset {p:g} - the budget is 80ms to 450ms")
                break
    for name, (base, off) in bases.items():
        if not name.endswith("-out"): continue
        enter = name[:-4]
        if enter in bases and not base < bases[enter][0]:
            add(off, "M13 TOKEN-BUDGET", f"{name}: {base:g}ms is not faster than {enter}: {bases[enter][0]:g}ms - exit accelerates, enter decelerates")
    for r in rules:
        sel = r["prelude"]
        if not sel.startswith(".theme-"): continue
        keys = [p for p, _, _ in r["decls"] if p.startswith("--")]
        bad = [k for k in keys if k not in THEME_KEYS]
        if bad:
            add(off0 + r["start"], "M13 TOKEN-BUDGET", f"{sel} sets {', '.join(bad)} - a personality may touch only {', '.join(sorted(THEME_KEYS))}")
        if len(keys) > 3:
            add(off0 + r["start"], "M13 TOKEN-BUDGET", f"{sel} overrides {len(keys)} motion keys - at most three")


# M14 -------------------------------------------------------------------------------------------

TEXT_WRITE = re.compile(r"\.(?:textContent|innerText|innerHTML)\s*=")
TICKERS = re.compile(r"(?<![\w$])(?:countUp|CountUp|odometer|Odometer|NumberTicker|SplitText|Splitting)(?![\w$])")


def m14_js(js, add):
    for m in re.finditer(r"(?<![\w$.])(requestAnimationFrame|setInterval|setTimeout)\s*\(", js):
        j, depth = m.end(), 1
        while j < len(js) and depth:
            if js[j] == "(": depth += 1
            elif js[j] == ")": depth -= 1
            j += 1
        body = js[m.end():j] if m.group(1) != "requestAnimationFrame" else _block_around(js, m.start())
        # A single deferred setTimeout that writes text is a late update, not an animation. Only a
        # repeating timer - setInterval, rAF, or a setTimeout that reschedules itself - interpolates
        # a value, so only that form puts a number in the DOM that was never true.
        if m.group(1) == "setTimeout" and not re.search(r"setTimeout|requestAnimationFrame", body):
            continue
        if TEXT_WRITE.search(body) and re.search(r"[+\-*/]|Math\.|toFixed|Number\(|parseFloat", body):
            add(m.start(), "M14 ANIMATED-VALUE", f"{m.group(1)} callback writes textContent from a computed value - a count-up puts a false number in the DOM that assistive tech announces")
    for m in TICKERS.finditer(js):
        add(m.start(), "M14 ANIMATED-VALUE", f"{m.group(0)} - an animated value or a per-character text split")
    for m in re.finditer(r"\.split\s*\(\s*['\"]{2}\s*\)", js):
        if re.search(r"createElement|innerHTML|<span|\.map\s*\(", js[m.end():m.end() + 240]):
            add(m.start(), "M14 ANIMATED-VALUE", ".split('') feeding element creation - per-character splitting breaks Arabic letter joining")


def m14_html(html, add):
    for m in re.finditer(r"(?<![\w-])data-count(?![\w-])", html):
        add(m.start(), "M14 ANIMATED-VALUE", "data-count - the true value belongs in the markup before anything moves")


# ---- driver -----------------------------------------------------------------------------------

def collect(root):
    if os.path.isfile(root): return [root]
    files = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        files += [os.path.join(d, f) for f in fs if os.path.splitext(f)[1].lower() in EXT]
    return sorted(files)


def die(msg):
    print(f"lint_motion: {msg}", file=sys.stderr)
    return 2


def main():
    a = sys.argv[1:]
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print(__doc__.strip()); return 0
    targets = [x for x in a if not x.startswith("--")]
    for flag in a:
        if flag.startswith("--") and flag not in ("--json", "--quiet"): return die(f"unknown option {flag}")
    if not targets: print(__doc__); return 2
    if len(targets) > 1: return die(f"expected one target, got {len(targets)}: {' '.join(targets)}")
    root = targets[0] or "."
    if not os.path.exists(root): return die(f"target not found: {root}")
    files = collect(root)
    # Scanning nothing is not a pass: it is a wrong path, and reporting OK there is how an
    # unmigrated page slips through a green build.
    if not files: return die(f"no motion-lintable files under {root} (looking for {' '.join(sorted(EXT))})")
    rep = Report()
    for f in files:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh: text = fh.read()
        except OSError as e: return die(f"cannot read {f}: {e}")
        try: check_file(f, text, rep)
        except Exception as e:                      # a parser that dies silently is a linter that lies
            return die(f"{f}: {e.__class__.__name__}: {e}")
    rows = sorted(rep.rows, key=lambda r: (r["file"], r["line"], r["rule"]))
    if "--json" in a:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    elif not ("--quiet" in a and not rows):
        for r in rows: print(f"{r['file']}:{r['line']}: {r['rule']} — {r['evidence']}")
        by_rule = {}
        for r in rows: by_rule[r["rule"].split()[0]] = by_rule.get(r["rule"].split()[0], 0) + 1
        tail = ", ".join(f"{k}x{v}" for k, v in sorted(by_rule.items()))
        print(f"\nlint_motion: {len(files)} file(s), {len(rows)} finding(s)"
              f"{' - ' + tail if tail else ''} -> {'FAIL' if rows else 'PASS'}")
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())
