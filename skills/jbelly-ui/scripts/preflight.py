#!/usr/bin/env python3
"""Mechanical pre-flight for a UI page or folder (Class D): AI-tells, structure thresholds, token contrast.

Usage: python scripts/preflight.py <file-or-dir> [--json]
Exit 1 on any FAIL, 2 when there was nothing to check. Every check prints file:line evidence so a fix is one edit away.

Checks
  tells      — signatures of default-AI UI (a region marked data-preflight="quote" is exempt from
               this pass only, and the exemption is printed so it cannot hide quietly): purple/indigo gradient hexes, gradient text, glass-by-reflex,
               `uppercase tracking-` eyebrows over budget, Sparkles/Zap icons, marketing filler words, emoji icons,
               DiceBear avatars, `transition: all`, pure #000 text, rounded-2xl+shadow-lg on everything
  structure  — one primary action per view, h1 count, skip link present when a nav exists, icon-only buttons labelled
  contrast   — WCAG ratio of the token pairs in every scope that declares them - :root, .dark, a theme class,
               a wrapped @layer/@media block (foreground/background, primary-foreground/primary,
               muted-foreground/background) computed from oklch()/hex; text pairs must reach 4.5, muted 4.5,
               large 3. A declared pair whose value cannot be read is a FAIL, never a skip.
               Any role the markup uses as text is checked against the surface behind it too, so a
               page cannot pass by never declaring the pair it needed
"""
import json, math, os, re, sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

EXTS = (".html", ".htm", ".css", ".jsx", ".tsx", ".vue", ".svelte", ".razor", ".cshtml")
CLASS_ATTR = r"class(?:Name)?\s*=\s*[\"'{]"  # .jsx/.tsx are collected too, and React spells it className

TELLS = [
    ("purple-indigo-gradient", r"(?:from|via|to)-(?:purple|indigo|violet|fuchsia)-\d{3}|#(?:6366f1|8b5cf6|a855f7|7c3aed|4f46e5|c084fc)\b", "purple/indigo gradient palette", 0),
    ("gradient-text", r"bg-clip-text\s+text-transparent|text-transparent\s+bg-clip-text", "gradient text", 0),
    ("glass-by-reflex", r"backdrop-blur-(?:md|lg|xl|2xl)\b(?![^\"]*(?:header|nav|sticky))", "glassmorphism outside a sticky header", 2),
    ("sparkle-icons", r"data-lucide=\"(?:sparkles|zap|rocket|wand-2)\"|lucide-(?:sparkles|zap|rocket)|<Sparkles|<Zap|<Rocket", "Sparkles/Zap/Rocket icons", 0),
    ("filler-copy", r"\b(?:Elevate|Seamless(?:ly)?|Unleash|Supercharge|Effortless(?:ly)?|Next-gen|Revolutioni[sz]e|Empower)\b", "marketing filler words", 0),
    ("emoji-icons", r"[>\w\"']\s*[\U0001F300-\U0001FAFF☀-➿]|[\U0001F300-\U0001FAFF☀-➿]\s*[<\w\"']", "emoji used as icons", 0),
    ("dicebear", r"dicebear\.com|api\.dicebear", "DiceBear avatars", 0),
    ("transition-all", r"transition:\s*all\b|\btransition-all\b", "transition: all", 0),
    ("pure-black-text", r"(?:color|--foreground)\s*:\s*(?:#000(?:000)?\b|rgba?\(\s*0\s*,\s*0\s*,\s*0\b)|text-\[#000(?:000)?\]|text-black\b", "pure black text", 0),
    ("rounded-2xl-shadow-lg", r"rounded-2xl[^\"]*shadow-(?:lg|xl|2xl)|shadow-(?:lg|xl|2xl)[^\"]*rounded-2xl", "rounded-2xl + shadow-lg cards", 2),
    # allowed 0: one hit IS the layout this names, so the first match has to report
    ("hero-three-cards", r"grid-cols-3[^>]*>\s*(?:<div[^>]*" + CLASS_ATTR + r"[^>]*(?:card|rounded)[\s\S]{0,400}){3}", "hero + three identical feature cards", 0),
]
EYEBROW = r"uppercase[^\"]*tracking-(?:wide|wider|widest|\[)"

def to_srgb(c):
    """oklch(L% C H) | oklch(L C H) | #hex -> (r,g,b) 0..1 or None."""
    c = c.strip().lower()
    m = re.match(r"oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)", c)
    if m:
        L = float(m.group(1)) / (100 if m.group(2) or float(m.group(1)) > 1 else 1); C = float(m.group(3)); H = math.radians(float(m.group(4)))
        a, b = C * math.cos(H), C * math.sin(H)
        l_ = L + 0.3963377774 * a + 0.2158037573 * b; m_ = L - 0.1055613458 * a - 0.0638541728 * b; s_ = L - 0.0894841775 * a - 1.2914855480 * b
        l, m2, s = l_ ** 3, m_ ** 3, s_ ** 3
        r = 4.0767416621 * l - 3.3077115913 * m2 + 0.2309699292 * s
        g = -1.2684380046 * l + 2.6097574011 * m2 - 0.3413193965 * s
        bb = -0.0041960863 * l - 0.7034186147 * m2 + 1.7076147010 * s
        def gamma(v):  # linear -> sRGB, so lum() can linearise like it does for hex
            v = min(1, max(0, v)); return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
        return tuple(gamma(x) for x in (r, g, bb))
    m = re.match(r"#([0-9a-f]{6})\b", c)
    if m:
        h = m.group(1); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    if c in ("white", "#fff"): return (1, 1, 1)
    if c in ("black",): return (0, 0, 0)
    return None

def lum(rgb):
    def ch(v): return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb); return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(a, b):
    la, lb = lum(a), lum(b); hi, lo = max(la, lb), min(la, lb); return (hi + 0.05) / (lo + 0.05)

def token_scopes(css):
    """[(selector, narrowing-set, tokens)] for every block that declares custom properties, in source order.

    Palettes live under @layer, @media, a theme class or a data-attribute as often as under a bare
    :root; a scope that is never collected is a palette that is never contrast-checked, which reads
    as a clean PASS. The narrowing-set is what makes a scope more specific than another (its classes
    and attribute selectors), so `.theme-mint.dark` can inherit `:root`, `.dark` and `.theme-mint`.
    """
    scopes = []
    css = re.sub(r"/\*[\s\S]*?\*/", " ", css)  # a comment is neither a selector nor a live declaration
    end = 0
    for m in re.finditer(r"\{([^{}]*)\}", css):  # innermost blocks only, so @layer/@media wrappers are stepped over
        pre, end = css[end:m.start()], m.end()  # anchor on the brace and slice the selector out, or a 200KB page costs O(n^2)
        decls = re.findall(r"--([\w-]+)\s*:\s*([^;\n}]+)", m.group(1))
        if not decls: continue
        sel = " ".join(re.split(r"[{};>]", pre)[-1].split())[:60] or ":root"  # tail only: drop the rule or tag before it
        scopes.append((sel, frozenset(re.findall(r"\.[\w-]+|\[[^\]]*\]", sel)), {k: v.strip() for k, v in decls}))
    return scopes

def resolve(tokens, name, depth=0):
    v = tokens.get(name)
    if v is None or depth > 5: return None
    m = re.match(r"var\(--([\w-]+)\)", v.strip())
    return resolve(tokens, m.group(1), depth + 1) if m else v

ICON_TAG = re.compile(r"<\s*(?:i|svg|path|use)\b|data-lucide\s*=", re.I)
ICON_SELECTOR = re.compile(r"(?:^|[\s,>+~])(?:svg|i|path|use)(?:[\s,:.]|$)")


def text_role_pairs(txt, declared):
    """The roles this page paints text with, paired against the surface that is actually behind them.

    The fixed pair list can only check what a page declares. A page that writes `text-primary` on
    its links and never declares `--primary-accent` was therefore checked for nothing at all --
    which is how three shells shipped links below the floor. What the markup does is the better
    question, so every `text-<role>` utility is read out of the class lists and checked.

    What is deliberately left out, because the surface behind it is not the page:

    - an icon, whether written as an element (`<i data-lucide="check" class="text-success">`), as a
      variant (`[&_svg]:text-primary`) or as a rule whose selector targets one (`.feature svg`).
      All three become an svg; a graphic is judged at 3:1, and holding icons to 4.5 would dull every
      feature list for no accessibility gain.
    - a `text-x` sitting in the same class list as `bg-x/NN`: it is on its own tint, and that pair is
      a different question from this one.
    - a `-foreground` role, which is the text half of a pair already in the list. Checking it against
      the page would compare white with white.

    Sidebar roles are checked against `--sidebar`, since that is the surface they sit on. Everything
    else is checked against both the page and the card.
    """
    roles = set()
    for m in re.finditer(r"""(?:class(?:Name)?\s*=\s*["'{]|@apply\s)([^"'}\n;]+)""", txt):
        chunk = m.group(1)
        head = txt[max(0, m.start() - 400):m.start()]
        tag = head.rfind("<")
        if tag != -1 and ICON_TAG.search(head[tag:]):
            continue                                            # an icon element
        brace = head.rfind("{")
        if brace != -1:                                         # inside a rule: what does it select?
            sel = head[:brace]
            sel = sel[max(sel.rfind("}"), sel.rfind(";")) + 1:]
            if ICON_SELECTOR.search(sel):
                continue                                        # a rule that styles icons
        for util in chunk.split():                              # whitespace only: brackets are syntax
            if "svg" in util and ":" in util:
                continue                                        # an arbitrary variant scoped to an svg
            base = util.split(":")[-1].strip("[]")
            if not base.startswith("text-"):
                continue
            role = base[5:].split("/")[0]
            if not role or role.endswith("-foreground") or role not in declared:
                continue                                        # a size or an alignment utility
            if re.search(r"(?<![\w-])bg-" + re.escape(role) + r"/", chunk):
                continue                                        # sits on its own tint
            roles.add(role)
    out = []
    for role in sorted(roles):
        if role.startswith("sidebar"):
            if "sidebar" in declared:
                out.append((role, "sidebar", 4.5))
            continue
        out += [(role, "background", 4.5), (role, "card", 4.5)]
    return out


def quoted_spans(txt):
    """The spans of every element marked data-preflight="quote", nesting included.

    A non-greedy regex stops at the first closing tag, which on a list of divs exempts the first item
    and nothing else. Depth has to be counted, so it is counted here.
    """
    spans = []
    for m in re.finditer(r"<(\w+)(?=[^>]*\sdata-preflight=[\"']quote[\"'])[^>]*>", txt, re.I):
        tag = m.group(1)
        depth, i = 1, m.end()
        step = re.compile(rf"</?{re.escape(tag)}\b[^>]*>", re.I)
        while depth and i < len(txt):
            nxt = step.search(txt, i)
            if not nxt:
                break
            depth += -1 if nxt.group(0).startswith("</") else 1
            i = nxt.end()
        spans.append((m.start(), i))
    return spans


def check_file(path, results):
    txt = open(path, encoding="utf-8", errors="replace").read()
    lines = txt.split("\n")
    def where(pos):
        return txt.count("\n", 0, pos) + 1
    # A page that documents these rules has to be able to name what they ban, so a region marked
    # data-preflight="quote" is exempt from the tells pass -- and only from that pass. A quotation
    # cannot hide a contrast failure or an unlabelled button, because those are facts about the
    # rendered page rather than about its words.
    quoted = quoted_spans(txt)
    tell_txt = txt
    for a, b in reversed(quoted):
        tell_txt = tell_txt[:a] + (" " * (b - a)) + tell_txt[b:]
    if quoted:
        results.append(("OK", "exempt", f"{path}:{where(quoted[0][0])}",
                        f"{len(quoted)} quoted region(s) exempt from the tells pass -- check they are quotations"))
    # tells
    for key, pat, label, allowed in TELLS:
        hits = [m for m in re.finditer(pat, tell_txt, re.I)]
        if len(hits) > allowed:
            results.append(("FAIL", "tells", f"{path}:{where(hits[0].start())}", f"{label} ({len(hits)} hit{'s' if len(hits) != 1 else ''}, allowed {allowed})"))
    sections = max(1, len(re.findall(r"<section\b|<div[^>]*" + CLASS_ATTR + r"[^>]*\bcard\b", txt)))
    eyebrows = len(re.findall(EYEBROW, txt))
    budget = math.ceil(sections / 3)
    if eyebrows > max(3, budget):
        results.append(("FAIL", "tells", f"{path}", f"{eyebrows} uppercase-tracking eyebrows for {sections} sections (budget {max(3, budget)})"))
    # structure
    body = re.sub(r"<(nav|aside)\b[\s\S]*?</\1>", "", re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", txt))
    prim = len(re.findall(r"<(?:button|a)\b[^>]*" + CLASS_ATTR + r"[^>]*(?:btn-primary|bg-primary\s+text-primary-foreground)", body))
    if prim > 2: results.append(("WARN", "structure", path, f"{prim} primary controls outside nav (aim for 1, max 2)"))
    h1 = len(re.findall(r"<h1\b", txt))
    if h1 != 1 and "<main" in txt: results.append(("WARN", "structure", path, f"{h1} <h1> elements (expected exactly 1)"))
    if re.search(r"<nav\b", txt) and not re.search(r"skip to (?:main )?content", txt, re.I):
        results.append(("WARN", "structure", path, "nav present but no skip link"))
    icon_only = []
    for m in re.finditer(r"<button\b([^>]*)>([\s\S]*?)</button>", txt, re.I):
        if re.search(r"aria-label(?:ledby)?\s*=", m.group(1), re.I): continue  # title= is a tooltip, not a name
        # the accessible name comes from text, not from markup: empty text = icon-only, whatever the icon is made of
        if re.sub(r"<[^>]*>|&[a-z]+;|&#\d+;|\s", "", m.group(2)): continue
        icon_only.append(m)
    if icon_only: results.append(("FAIL", "structure", f"{path}:{where(icon_only[0].start())}", f"{len(icon_only)} icon-only button(s) without aria-label"))
    # contrast on tokens (css or html with <style>)
    scopes = token_scopes(txt)
    declared = {t.lstrip("-") for _, _, toks in scopes for t in toks}
    pairs = [("foreground", "background", 4.5), ("primary-foreground", "primary", 4.5), ("muted-foreground", "background", 4.5), ("secondary-foreground", "secondary", 4.5), ("card-foreground", "card", 4.5), ("primary-accent", "card", 4.5), ("primary-accent", "background", 4.5)]
    # and whatever the markup itself paints text with, which a fixed list cannot know
    pairs += [q for q in text_role_pairs(txt, declared) if q not in pairs]
    envs = {}  # keyed by narrowing-set: a page repeats few distinct scopes but can repeat them often
    for sel, sig, toks in scopes:
        if sig not in envs:
            envs[sig] = env = {}
            # Specificity decides, and source order only breaks a tie -- which is what the engine
            # does. Walking the file top to bottom instead let a `.theme-x` block written below a
            # `.theme-x.dark` block override it, and reported the light value as the dark one's.
            applies = [(len(sig2), i, toks2) for i, (_, sig2, toks2) in enumerate(scopes) if sig2 <= sig]
            for _, _, toks2 in sorted(applies, key=lambda x: (x[0], x[1])):
                env.update(toks2)
        env = envs[sig]
        for fg, bg, need in pairs:
            if fg not in toks and bg not in toks: continue  # scope leaves the pair alone; whoever set it reports it
            if fg not in env or bg not in env: continue  # half a pair: there is nothing to compare against
            a, b = resolve(env, fg), resolve(env, bg)
            ra, rb = (to_srgb(a) if a else None), (to_srgb(b) if b else None)
            if ra is None or rb is None:
                for name, rgb in ((fg, ra), (bg, rb)):  # an unreadable value is an unchecked pair, so say so and fail
                    if rgb is None: results.append(("FAIL", "contrast", f"{path} {sel}", f"--{name}: cannot read {env[name]!r}, pair --{fg} on --{bg} left unchecked"))
                continue
            cr = contrast(ra, rb)
            results.append(("FAIL" if cr < need else "OK", "contrast", f"{path} {sel}", f"--{fg} on --{bg}: {cr:.2f}:1 (need {need})"))

def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return 2
    target = a[0]; files = []
    if not os.path.exists(target):
        print(f"preflight: target not found: {target}", file=sys.stderr); return 2
    if os.path.isfile(target): files = [target]
    else:
        for d, dirs, fs in os.walk(target):
            dirs[:] = [x for x in dirs if x not in ("node_modules", "dist", ".git", "vendor", "__pycache__")]
            files += [os.path.join(d, f) for f in fs if os.path.splitext(f)[1] in EXTS]
    if not files:  # scanning nothing is not a pass, it is a typo in the path or the wrong folder
        print(f"preflight: no reviewable files under {target} (looking for {' '.join(EXTS)})", file=sys.stderr); return 2
    results = []
    for f in files: check_file(f, results)
    fails = [r for r in results if r[0] == "FAIL"]
    if "--json" in a:
        print(json.dumps([dict(status=s, group=g, where=w, detail=d) for s, g, w, d in results], indent=2))
    else:
        for s, g, w, d in results:
            if s != "OK" or g in ("contrast", "exempt"): print(f"[{s}] {g:9} {w}: {d}")   # an exemption nobody can see is one that gets abused
        print(f"\npreflight: {len(files)} file(s), {len(fails)} FAIL, {sum(1 for r in results if r[0]=='WARN')} WARN -> {'FAIL' if fails else 'PASS'}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
