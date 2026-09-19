#!/usr/bin/env python3
"""Write design/personality.md for a product: the contract every later screen is checked against (Class D).

Usage:
  python scripts/personality_init.py --product "Acme Ops" --kind dashboard --audience "ops managers, all day, keyboard" \
      --vibe "precise, calm, premium" --preset theme-clinic --change "density compact" --change "radius 0.5rem" \
      --signature "3px start rail on active nav" [--avoid "blue primary" ...] [--out design/personality.md]

Presets: theme-clinic theme-graphite theme-editorial theme-neo theme-slate theme-mint (see references/personalities.md).
The file is short on purpose: four fields of the design read plus the dials; agents read it first on every screen.
"""
import argparse, datetime, os, sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

PRESETS = {
 "theme-clinic":    ("Inter (display + text); Arabic: Noto Sans Arabic", "oklch(50% 0.12 195) teal", "0.75rem", "airy", "tinted page", "micro", "display numerals + 3px start rail on active nav", "teal · amber · slate-blue · sage"),
 "theme-graphite":  ("Inter text; IBM Plex Mono for meta", "oklch(65% 0.17 150) signal green", "0.25rem", "compact", "flat bordered", "still", "monospaced meta + dotted separators", "green · sky · amber · magenta"),
 "theme-editorial": ("Fraunces display / Source Sans 3 text", "oklch(48% 0.16 30) brick", "0.5rem", "standard", "elevated", "one moment (content fade-up)", "serif headings + hairline rules", "brick · olive · mustard · ink"),
 "theme-neo":       ("Space Grotesk display / DM Sans text", "oklch(55% 0.25 290) electric violet", "0.25rem", "standard", "outlined + offset shadow", "micro + press", "offset shadow + uppercase tracked labels", "violet · yellow · black · coral"),
 "theme-slate":     ("Inter (display + text)", "oklch(42% 0.12 260) navy", "0.375rem", "standard", "tinted page + dark sidebar", "micro", "gold active marker on navy", "navy · gold · steel · teal"),
 "theme-mint":      ("Plus Jakarta Sans display / Inter text", "oklch(60% 0.15 165) mint", "1rem", "airy", "elevated, pill controls", "one moment (KPI count-up)", "pill controls + rounded avatar chips", "mint · coral · navy · sand"),
}
# The body below is printed from the preset table, so a dial name is the one thing --change may not get wrong.
DIALS = ("type", "primary", "radius", "density", "surface", "motion", "signature", "data colours")
ALIASES = {"data": "data colours", "data colors": "data colours"}

def split_change(c):
    """Peel a known dial name off the front: a dial name can be two words and a value can contain ':' or '.'."""
    s = " ".join(c.split())
    for name in sorted(DIALS + tuple(ALIASES), key=len, reverse=True):
        head, tail = s[:len(name)].lower(), s[len(name):]
        if head == name and (tail == "" or tail[0] in " :"):
            return ALIASES.get(name, name), tail.lstrip(" :").strip()
    return None, s

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--product", required=True); ap.add_argument("--kind", required=True, help="dashboard | settings | landing | table | auth | …")
    ap.add_argument("--audience", required=True, help="who, how often, keyboard or touch"); ap.add_argument("--vibe", required=True, help="three words")
    ap.add_argument("--preset", required=True, choices=sorted(PRESETS)); ap.add_argument("--change", action="append", default=[], help="a dial you changed, e.g. 'density compact' (give at least two)")
    ap.add_argument("--signature", default=""); ap.add_argument("--avoid", action="append", default=[]); ap.add_argument("--out", default=os.path.join("design", "personality.md"))
    a = ap.parse_args()
    if len(a.change) < 2:
        print("warning: fewer than two dials changed; the product will look like the stock preset", file=sys.stderr)
    dials, applied = dict(zip(DIALS, PRESETS[a.preset])), []
    for c in a.change:
        name, value = split_change(c)
        if name is None:
            sys.exit(f"error: --change {c!r} does not start with a dial name; dials are: {', '.join(DIALS)}")
        if not value:
            sys.exit(f"error: --change {c!r} names the dial '{name}' but gives it no value")
        dials[name] = value; applied.append(f"{name} {value}")
    t, p, r, d, s, m, sig, data = (dials[k] for k in DIALS)
    avoid = a.avoid or ["blue-600 primary", "rounded-2xl + shadow-lg everywhere", "gradient text", "icon-in-a-square on every card"]
    body = f"""# Personality — {a.product}

kind: {a.kind}
audience: {a.audience}
vibe: {a.vibe}
system: {a.preset} · changed: {'; '.join(applied) or '(none yet)'}

type: {t}
primary: {p}
radius: {r}   density: {d}   surface: {s}   motion: {m}
signature: {a.signature or sig}
data colours: {data}
avoid: {' · '.join(avoid)}

written: {datetime.date.today().isoformat()} — every later screen is checked against this file; change it here, never per component.
"""
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8", newline="\n").write(body)
    print(f"wrote {a.out}\n{body}")

if __name__ == "__main__":
    main()
