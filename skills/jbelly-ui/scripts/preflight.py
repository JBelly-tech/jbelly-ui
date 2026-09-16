#!/usr/bin/env python3
"""Mechanical pre-flight for a UI page or folder (Class D): AI-tells, structure thresholds, token contrast.

Usage: python scripts/preflight.py <file-or-dir> [--json]
Exit 1 on any FAIL. Every check prints file:line evidence so a fix is one edit away.

Checks
  tells      — signatures of default-AI UI: purple/indigo gradient hexes, gradient text, glass-by-reflex,
               `uppercase tracking-` eyebrows over budget, Sparkles/Zap icons, marketing filler words, emoji icons,
               DiceBear avatars, `transition: all`, pure #000 text, rounded-2xl+shadow-lg on everything
  structure  — one primary action per view, h1 count, skip link present when a nav exists, icon-only buttons labelled
  contrast   — WCAG ratio of the token pairs in :root and .dark (foreground/background, primary-foreground/primary,
               muted-foreground/background) computed from oklch()/hex; text pairs must reach 4.5, muted 4.5, large 3
"""
import json, math, os, re, sys

TELLS = [
    ("purple-indigo-gradient", r"(?:from|via|to)-(?:purple|indigo|violet|fuchsia)-\d{3}|#(?:6366f1|8b5cf6|a855f7|7c3aed|4f46e5|c084fc)\b", "purple/indigo gradient palette", 0),
    ("gradient-text", r"bg-clip-text\s+text-transparent|text-transparent\s+bg-clip-text", "gradient text", 0),
    ("glass-by-reflex", r"backdrop-blur-(?:md|lg|xl|2xl)\b(?![^\"]*(?:header|nav|sticky))", "glassmorphism outside a sticky header", 2),
    ("sparkle-icons", r"data-lucide=\"(?:sparkles|zap|rocket|wand-2)\"|lucide-(?:sparkles|zap|rocket)|<Sparkles|<Zap|<Rocket", "Sparkles/Zap/Rocket icons", 0),
    ("filler-copy", r"\b(?:Elevate|Seamless(?:ly)?|Unleash|Supercharge|Effortless(?:ly)?|Next-gen|Revolutioni[sz]e|Empower)\b", "marketing filler words", 0),
    ("emoji-icons", r"[\U0001F300-\U0001FAFF☀-➿](?=\s*(?:<|$))", "emoji used as icons", 0),
    ("dicebear", r"dicebear\.com|api\.dicebear", "DiceBear avatars", 0),
    ("transition-all", r"transition:\s*all\b|\btransition-all\b", "transition: all", 0),
    ("pure-black-text", r"(?:color|--foreground)\s*:\s*#000\b|text-\[#000\]|text-black\b", "pure black text", 0),
    ("rounded-2xl-shadow-lg", r"rounded-2xl[^\"]*shadow-(?:lg|xl|2xl)|shadow-(?:lg|xl|2xl)[^\"]*rounded-2xl", "rounded-2xl + shadow-lg cards", 2),
    ("hero-three-cards", r"grid-cols-3[^\"]*\"[^>]*>\s*(?:<div[^>]*class=\"[^\"]*(?:card|rounded)[^\"]*\"[\s\S]{0,400}){3}", "hero + three identical feature cards", 1),
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

def token_block(css, selector):
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    return dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", m.group(1))) if m else {}

def resolve(tokens, name, depth=0):
    v = tokens.get(name)
    if v is None or depth > 5: return None
    m = re.match(r"var\(--([\w-]+)\)", v.strip())
    return resolve(tokens, m.group(1), depth + 1) if m else v

def check_file(path, results):
    txt = open(path, encoding="utf-8", errors="replace").read()
    lines = txt.split("\n")
    def where(pos):
        return txt.count("\n", 0, pos) + 1
    # tells
    for key, pat, label, allowed in TELLS:
        hits = [m for m in re.finditer(pat, txt, re.I)]
        if len(hits) > allowed:
            results.append(("FAIL", "tells", f"{path}:{where(hits[0].start())}", f"{label} ({len(hits)} hit{'s' if len(hits) != 1 else ''}, allowed {allowed})"))
    sections = max(1, len(re.findall(r"<section\b|<div[^>]*class=\"[^\"]*\bcard\b", txt)))
    eyebrows = len(re.findall(EYEBROW, txt))
    budget = math.ceil(sections / 3)
    if eyebrows > max(3, budget):
        results.append(("FAIL", "tells", f"{path}", f"{eyebrows} uppercase-tracking eyebrows for {sections} sections (budget {max(3, budget)})"))
    # structure
    body = re.sub(r"<(nav|aside)\b[\s\S]*?</\1>", "", re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", txt))
    prim = len(re.findall(r"<(?:button|a)\b[^>]*class=\"[^\"]*(?:btn-primary|bg-primary text-primary-foreground)[^\"]*\"", body))
    if prim > 2: results.append(("WARN", "structure", path, f"{prim} primary controls outside nav (aim for 1, max 2)"))
    h1 = len(re.findall(r"<h1\b", txt))
    if h1 != 1 and "<main" in txt: results.append(("WARN", "structure", path, f"{h1} <h1> elements (expected exactly 1)"))
    if re.search(r"<nav\b", txt) and not re.search(r"skip to (?:main )?content", txt, re.I):
        results.append(("WARN", "structure", path, "nav present but no skip link"))
    icon_only = re.findall(r"<button\b(?![^>]*aria-label)[^>]*>\s*<(?:i|svg)\b[^>]*>(?:\s*</(?:i|svg)>)?\s*</button>", txt)
    if icon_only: results.append(("FAIL", "structure", f"{path}:{where(txt.find(icon_only[0]))}", f"{len(icon_only)} icon-only button(s) without aria-label"))
    # contrast on tokens (css or html with <style>)
    for sel in (":root", ".dark"):
        toks = token_block(txt, sel)
        if not toks: continue
        pairs = [("foreground", "background", 4.5), ("primary-foreground", "primary", 4.5), ("muted-foreground", "background", 4.5), ("secondary-foreground", "secondary", 4.5), ("card-foreground", "card", 4.5)]
        for fg, bg, need in pairs:
            a, b = resolve(toks, fg), resolve(toks, bg)
            if sel == ".dark":  # fall back to :root values for tokens not overridden in .dark
                root = token_block(txt, ":root"); a = a or resolve(root, fg); b = b or resolve(root, bg)
            ra, rb = (to_srgb(a) if a else None), (to_srgb(b) if b else None)
            if ra and rb:
                cr = contrast(ra, rb)
                results.append(("FAIL" if cr < need else "OK", "contrast", f"{path} {sel}", f"--{fg} on --{bg}: {cr:.2f}:1 (need {need})"))

def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return 2
    target = a[0]; files = []
    if os.path.isfile(target): files = [target]
    else:
        for d, dirs, fs in os.walk(target):
            dirs[:] = [x for x in dirs if x not in ("node_modules", "dist", ".git", "vendor", "__pycache__")]
            files += [os.path.join(d, f) for f in fs if os.path.splitext(f)[1] in (".html", ".htm", ".css", ".jsx", ".tsx", ".vue", ".svelte", ".razor", ".cshtml")]
    results = []
    for f in files: check_file(f, results)
    fails = [r for r in results if r[0] == "FAIL"]
    if "--json" in a:
        print(json.dumps([dict(status=s, group=g, where=w, detail=d) for s, g, w, d in results], indent=2))
    else:
        for s, g, w, d in results:
            if s != "OK" or g == "contrast": print(f"[{s}] {g:9} {w}: {d}")
        print(f"\npreflight: {len(files)} file(s), {len(fails)} FAIL, {sum(1 for r in results if r[0]=='WARN')} WARN -> {'FAIL' if fails else 'PASS'}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
