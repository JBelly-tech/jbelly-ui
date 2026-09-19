#!/usr/bin/env python3
"""Audit-first inventory for a redesign (Class D): what the existing UI actually uses, and where it deviates
from the house system. Run this BEFORE proposing any redesign; fix in the printed priority order.

Usage: python scripts/audit_styles.py <src-dir> [--json]   (flag order does not matter)
Exit 2, never a clean-looking report, when <src-dir> is missing or holds no source files.
Reports: font families, hex/rgb colours, radius values, shadows, spacing values, raw palette classes,
         transition durations, z-index values, icon libraries, and the top offenders by file.
Priority order for fixes (from what makes the biggest visible difference first):
  1 fonts  2 colour system  3 radius + shadow  4 spacing rhythm  5 states (hover/focus/empty/loading)  6 motion
"""
import json, os, re, sys
from collections import Counter, defaultdict

EXT = (".html", ".htm", ".css", ".scss", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".razor", ".cshtml")
PALETTE = re.compile(r"(?<![\w-])(?:[\w-]+:)*(?:bg|text|border|ring|from|via|to)-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3}(?![\w-])")
PATTERNS = {
    "fonts": re.compile(r"font-family\s*:\s*([^;}]+)|family=([A-Za-z+0-9]+)|font-\[['\"]?([A-Za-z ]+)"),
    "colours": re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]+\)|hsla?\([^)]+\)|oklch\([^)]+\)"),
    # Arbitrary values end in "]", a non-word character, so a trailing \b there can only match when the
    # next character is a word one -- i.e. never in real markup. (?![\w-]) is the boundary these need.
    "radius": re.compile(r"border-radius\s*:\s*([^;}]+)|\brounded(?:-[a-z]+)?(?:-(?:none|sm|md|lg|xl|2xl|3xl|full|\[[^\]]+\]))?(?![\w-])"),
    "shadows": re.compile(r"box-shadow\s*:\s*([^;}]+)|\bshadow-(?:none|xs|sm|md|lg|xl|2xl|inner|\[[^\]]+\])(?![\w-])"),
    "spacing": re.compile(r"\b(?:p|px|py|pt|pb|ps|pe|m|mx|my|mt|mb|ms|me|gap)-(?:\d+(?:\.\d+)?|\[[^\]]+\])(?![\w-])"),
    "durations": re.compile(r"duration-\d+|transition(?:-duration)?\s*:\s*[^;}]*?(\d+m?s)"),
    "zindex": re.compile(r"\bz-(?:\d+|\[[^\]]+\])(?![\w-])|z-index\s*:\s*(-?\d+)"),
    "icons": re.compile(r"lucide|heroicons|fontawesome|fa-[a-z]|material-icons|tabler|phosphor|iconify|keenicons|bi-[a-z]"),
}
GENERIC = {"sans-serif", "serif", "monospace", "cursive", "fantasy", "system-ui", "ui-sans-serif",
           "ui-serif", "ui-monospace", "ui-rounded", "emoji", "math", "inherit", "initial", "unset", "revert"}

def family(raw):
    """One declaration names one family in use; everything after the first comma is a fallback. Google-fonts
    URLs spell the space as '+' and tokens name no family at all, so both fold here -- otherwise one family
    spelled two ways counts as two and the "more than two families" deviation fires on a compliant page."""
    for part in raw.replace("+", " ").split(","):
        name = re.sub(r"\s+", " ", part.strip().strip("'\"").strip()).lower()
        if name and name not in GENERIC and not name.startswith("var("): return name
    return None

def main():
    a = sys.argv[1:]
    flags = {x for x in a if x.startswith("-")}
    args = [x for x in a if not x.startswith("-")]
    if flags & {"-h", "--help"}: print(__doc__); return 0
    bad = sorted(flags - {"--json"})
    if bad: print(f"audit: unknown option {bad[0]}", file=sys.stderr); print(__doc__, file=sys.stderr); return 2
    if not args: print(__doc__, file=sys.stderr); return 2
    root = args[0]
    # An inventory of nothing prints exactly like a clean codebase, so a bad target must never reach the report.
    if not os.path.isdir(root): print(f"audit: not a directory: {root}", file=sys.stderr); return 2
    files = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in ("node_modules", "dist", "build", ".git", "vendor", "__pycache__", ".next")]
        files += [os.path.join(d, f) for f in fs if f.lower().endswith(EXT)]
    if not files: print(f"audit: no source files under {root} (looked for {' '.join(EXT)})", file=sys.stderr); return 2
    counts = {k: Counter() for k in PATTERNS}; palette = Counter(); by_file = defaultdict(int)
    for f in files:
        try: txt = open(f, encoding="utf-8", errors="replace").read()
        except OSError: continue
        for k, pat in PATTERNS.items():
            for m in pat.finditer(txt):
                val = next((g for g in m.groups() if g), m.group(0)).strip().lower()[:60]
                if k == "fonts":
                    val = family(val)
                    if not val: continue
                counts[k][val] += 1
        for m in PALETTE.finditer(txt):
            palette[m.group(0)] += 1; by_file[f] += 1
    report = {
        "files": len(files),
        "fonts_distinct": len(counts["fonts"]), "fonts": counts["fonts"].most_common(8),
        "colours_distinct": len(counts["colours"]), "colours_top": counts["colours"].most_common(12),
        "radius_distinct": len(counts["radius"]), "radius_top": counts["radius"].most_common(8),
        "shadows_distinct": len(counts["shadows"]), "shadows_top": counts["shadows"].most_common(6),
        "spacing_distinct": len(counts["spacing"]), "spacing_top": counts["spacing"].most_common(10),
        "durations": counts["durations"].most_common(6), "zindex": counts["zindex"].most_common(6),
        "icon_libraries": counts["icons"].most_common(4),
        "raw_palette_classes": sum(palette.values()), "raw_palette_top": palette.most_common(10),
        "worst_files": sorted(by_file.items(), key=lambda x: -x[1])[:8],
    }
    if "--json" in flags: print(json.dumps(report, indent=2)); return 0
    print(f"audit: {report['files']} files")
    def row(label, val): print(f"  {label:22} {val}")
    row("font families", f"{report['fonts_distinct']} distinct: " + ", ".join(f"{k} ({n})" for k, n in report["fonts"]) if report["fonts"] else "none found")
    row("distinct colours", f"{report['colours_distinct']}  (house system: ~25 roles)  top: " + ", ".join(f"{k}×{n}" for k, n in report["colours_top"][:6]))
    row("distinct radii", f"{report['radius_distinct']}  (house: 4 steps)  top: " + ", ".join(f"{k}×{n}" for k, n in report["radius_top"][:5]))
    row("distinct shadows", f"{report['shadows_distinct']}  (house: 2)  top: " + ", ".join(f"{k}×{n}" for k, n in report["shadows_top"][:4]))
    row("spacing values", f"{report['spacing_distinct']} distinct  top: " + ", ".join(f"{k}×{n}" for k, n in report["spacing_top"][:6]))
    row("durations", ", ".join(f"{k}×{n}" for k, n in report["durations"]) or "none")
    row("z-index values", ", ".join(f"{k}×{n}" for k, n in report["zindex"]) or "none")
    row("icon libraries", ", ".join(f"{k}×{n}" for k, n in report["icon_libraries"]) or "none detected")
    row("raw palette classes", f"{report['raw_palette_classes']}  top: " + ", ".join(f"{k}×{n}" for k, n in report["raw_palette_top"][:5]))
    row("worst files", "; ".join(f"{os.path.relpath(f, root)} ({n})" for f, n in report["worst_files"][:5]) or "-")
    print("\nDeviation list (fix in this order):")
    if report["fonts_distinct"] > 2: print("  1. fonts: more than two families -> pick display + text (Inter default), delete the rest")
    if report["colours_distinct"] > 30 or report["raw_palette_classes"] > 0: print("  2. colour: map every raw colour to a token role in tokens.css; components use roles only")
    if report["radius_distinct"] > 4 or report["shadows_distinct"] > 2: print("  3. radius/shadow: collapse to --radius scale (xl/lg/md/sm) and shadow-xs / shadow-md")
    if report["spacing_distinct"] > 14: print("  4. spacing: use the 4px scale with gap-2.5 inside rows and gap-5/7.5 between cards")
    print("  5. states: add loading/empty/error/focus states where missing (verify with preflight + verify_page)")
    if len(report["durations"]) > 2: print("  6. motion: one duration for colour/opacity (150ms), one for open/close (200-250ms)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
