#!/usr/bin/env python3
"""Scaffold a new screen from the house shell with zero model tokens (cross-platform).

Usage: python scripts/new_screen.py <out.html> [--theme theme-clinic] [--density density-compact] [--dir rtl] [--dark]
                                    [--title "Dashboard"] [--product "Your product"] [--strip-demo-controls]
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEMES = {"", "theme-clinic", "theme-graphite", "theme-editorial", "theme-neo", "theme-slate", "theme-mint"}
DENS = {"", "density-compact", "density-airy"}

def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return 2
    out = a[0]
    def opt(n, d): return a[a.index(n) + 1] if n in a else d
    theme, dens, direction = opt("--theme", ""), opt("--density", ""), opt("--dir", "ltr")
    if theme not in THEMES or dens not in DENS or direction not in ("ltr", "rtl"): print("invalid option"); return 2
    title, product = opt("--title", "Dashboard"), opt("--product", "Product")
    s = open(os.path.join(ROOT, "assets", "app-shell.html"), encoding="utf-8").read()
    classes = " ".join(c for c in ["h-full", theme, dens, "dark" if "--dark" in a else ""] if c)
    s = s.replace('<html lang="en" dir="ltr" class="h-full">', f'<html lang="en" dir="{direction}" class="{classes}">')
    s = s.replace("<title>jbelly-ui — app shell</title>", f"<title>{product} — {title}</title>")
    s = s.replace("Bayan Ops", product)
    s = s.replace('<h1 class="text-xl font-medium text-mono font-display" data-i18n="Dashboard">Dashboard</h1>', f'<h1 class="text-xl font-medium text-mono font-display">{title}</h1>')
    if "--strip-demo-controls" in a:
        s = re.sub(r"(?s)<!-- ===== Demo controls.*?</details>\s*", "", s)
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8", newline="\n").write(s)
    print(f"scaffolded {out} ({len(s.encode()):,} bytes) theme={theme or '-'} density={dens or '-'} dir={direction} dark={'--dark' in a}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
