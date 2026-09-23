#!/usr/bin/env python3
"""Token lint (cross-platform): finds raw colours used outside tokens.css.

Catches Tailwind palette classes (bg-blue-500), arbitrary-value colour utilities
(bg-[#0ea5e9]) and hex / rgb() / hsl() literals in a declaration or a style attribute.

Usage: python scripts/lint_tokens.py <dir-or-file> [--exclude NAME[,NAME]]... [--quiet]
Exit 1 when violations exist, 2 when the arguments or the target are wrong.
Silence a line with a 'ui-lint-ignore' comment.
"""
import os, re, sys

PALETTE = "slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose"
PREFIX = "bg|text|border|ring|fill|stroke|from|via|to|divide|outline|shadow|accent|caret|decoration|placeholder"
PATTERN = re.compile(rf"(?<![\w-])(?:[\w-]+:)*(?:{PREFIX})-(?:{PALETTE})-\d{{2,3}}(?:/\d{{1,3}})?(?![\w-])")
EXT = {".html", ".htm", ".css", ".scss", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".razor", ".cshtml", ".php", ".astro", ".md"}
SKIP = {"node_modules", "dist", "build", ".git", ".next", "bin", "obj", "vendor", "__pycache__"}

LITERAL = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![0-9a-fA-F])|(?:rgba?|hsla?)\([^)\n]{0,160}\)")
CPROP = ("color|background|background-color|background-image|border|border-color|border-[a-z]+-color|"
         "outline|outline-color|fill|stroke|box-shadow|text-shadow|caret-color|accent-color|"
         "text-decoration-color|column-rule-color|stop-color|flood-color|scrollbar-color")
# A literal only paints something where CSS can read it as a value, so a bare "#1042"
# in body text or a "#000" quoted in prose stays clean. ":" covers CSS and inline
# style="...", "=" covers SVG presentation attributes (fill="#fff").
DECL = re.compile(rf"(?<![\w-])(--[\w-]+|(?:{CPROP}))\s*[:=]\s*(\"[^\"\n]*\"|'[^'\n]*'|[^;{{}}\n]*)")
ARB = re.compile(rf"(?<![\w-])(?:[\w-]+:)*((?:{PREFIX})-\[[^\]\n]*\])")
# tokens.css itself tints --shadow-* with a translucent rgb(); that is the system's own
# shadow recipe, not a hard-coded brand colour. An opaque one still fails.
TRANSLUCENT = re.compile(r"[/,]\s*(?:\d*\.\d+|\d{1,2}%|0)\s*\)$")

def colour_hits(line):
    """Raw colour literals on one line, keyed by offset so overlapping contexts count once."""
    hits = {}
    def scan(text, base, prop=""):
        for x in LITERAL.finditer(text):
            if "shadow" in prop and TRANSLUCENT.search(x.group(0)): continue
            hits[base + x.start()] = x.group(0)
    for m in ARB.finditer(line): scan(m.group(1), m.start(1), m.group(1))
    for m in DECL.finditer(line): scan(m.group(2), m.start(2), m.group(1))
    return [hits[k] for k in sorted(hits)]

def die(msg):
    print(f"jbelly-ui lint: {msg}", file=sys.stderr)
    return 2

def main():
    argv = sys.argv[1:]
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print(__doc__.strip()); return 0
    quiet = False; excl = set(); targets = []; i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--quiet": quiet = True
        elif a == "--exclude" or a.startswith("--exclude="):
            if "=" in a: val = a.split("=", 1)[1]
            else:
                i += 1; val = argv[i] if i < len(argv) else ""
            if not val or val.startswith("--"): return die("--exclude needs one directory name (repeat the flag, or comma-separate)")
            excl |= {p for p in val.split(",") if p}
        elif a.startswith("--"): return die(f"unknown option {a}")
        else: targets.append(a)
        i += 1
    if not targets: return die("no target given. Usage: lint_tokens.py <dir-or-file> [--exclude NAME]... [--quiet]")
    if len(targets) > 1: return die(f"expected one target, got {len(targets)}: {' '.join(targets)}")
    # A caller passing os.path.dirname(<page in the cwd>) hands us "", which means the cwd.
    root = targets[0] or "."
    if not os.path.exists(root): return die(f"target not found: {targets[0]}")
    files = []
    if os.path.isfile(root): files = [root]
    else:
        for d, dirs, fs in os.walk(root):
            dirs[:] = [x for x in dirs if x not in SKIP and x not in excl]
            files += [os.path.join(d, f) for f in fs if os.path.splitext(f)[1].lower() in EXT and f != "tokens.css"]
    # Zero files scanned is not a pass: it means a wrong path or an over-broad --exclude,
    # and reporting OK there is how a broken page slips through a green build.
    if not files: return die(f"no lintable files under {root} - wrong path, or everything excluded?")
    viol = []
    for f in files:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                for n, line in enumerate(fh, 1):
                    if "ui-lint-ignore" in line: continue
                    for m in PATTERN.finditer(line): viol.append((f, n, m.group(0)))
                    for m in colour_hits(line): viol.append((f, n, m))
        except OSError as e: return die(f"cannot read {f}: {e}")
    if not viol:
        if not quiet: print(f"jbelly-ui lint: OK - {len(files)} files, no raw palette colours.")
        return 0
    for f, n, m in viol: print(f"{f}:{n}: {m}")
    print(f"\njbelly-ui lint: {len(viol)} raw colour(s) in {len({v[0] for v in viol})} file(s).")
    print("Replace with a semantic role (bg-primary, text-muted-foreground, border-border, ...) or add the colour to tokens.css.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
