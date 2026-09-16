#!/usr/bin/env python3
"""Token lint (cross-platform): finds raw Tailwind palette colours outside tokens.css.

Usage: python scripts/lint_tokens.py <dir-or-file> [--exclude name ...] [--quiet]
Exit 1 when violations exist. Silence a line with a 'ui-lint-ignore' comment.
"""
import os, re, sys

PALETTE = "slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose"
PREFIX = "bg|text|border|ring|fill|stroke|from|via|to|divide|outline|shadow|accent|caret|decoration|placeholder"
PATTERN = re.compile(rf"(?<![\w-])(?:[\w-]+:)*(?:{PREFIX})-(?:{PALETTE})-\d{{2,3}}(?:/\d{{1,3}})?(?![\w-])")
EXT = {".html", ".htm", ".css", ".scss", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".razor", ".cshtml", ".php", ".astro", ".md"}
SKIP = {"node_modules", "dist", "build", ".git", ".next", "bin", "obj", "vendor", "__pycache__"}

def main():
    args = sys.argv[1:]
    quiet = "--quiet" in args
    excl = set()
    if "--exclude" in args:
        i = args.index("--exclude"); excl = set(args[i + 1:]); args = args[:i]
    root = next((a for a in args if not a.startswith("--")), ".")
    files = []
    if os.path.isfile(root): files = [root]
    else:
        for d, dirs, fs in os.walk(root):
            dirs[:] = [x for x in dirs if x not in SKIP and x not in excl]
            files += [os.path.join(d, f) for f in fs if os.path.splitext(f)[1].lower() in EXT and f != "tokens.css"]
    viol = []
    for f in files:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                for n, line in enumerate(fh, 1):
                    if "ui-lint-ignore" in line: continue
                    for m in PATTERN.finditer(line): viol.append((f, n, m.group(0)))
        except OSError: pass
    if not viol:
        if not quiet: print(f"jbelly-ui lint: OK - {len(files)} files, no raw palette colours.")
        return 0
    for f, n, m in viol: print(f"{f}:{n}: {m}")
    print(f"\njbelly-ui lint: {len(viol)} raw palette colour(s) in {len({v[0] for v in viol})} file(s).")
    print("Replace with a semantic role (bg-primary, text-muted-foreground, border-border, ...) or add the colour to tokens.css.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
