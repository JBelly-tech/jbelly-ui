#!/usr/bin/env python3
"""Export tokens.css to a DTCG (Design Tokens Community Group) JSON file: assets/tokens.json.

Usage: python scripts/export_tokens.py [references/tokens.css] [assets/tokens.json]
Groups: color (light + dark modes as $extensions.modes), radius, font, shadow, layout.
Consumers: Style Dictionary, Tokens Studio, Figma plugins, any stack that reads DTCG.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def block(css, selector):
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    return dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", m.group(1))) if m else {}

def main():
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print(__doc__.strip()); return 0
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "references", "tokens.css")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "assets", "tokens.json")
    css = open(src, encoding="utf-8").read()
    root, dark = block(css, ":root"), block(css, ".dark")
    tokens = {"$schema": "https://www.designtokens.org/schema", "color": {}, "font": {}, "radius": {}, "shadow": {}, "layout": {}}
    for k, v in root.items():
        v = v.strip()
        if k.startswith("font-"):
            tokens["font"][k[5:]] = {"$type": "fontFamily", "$value": [f.strip().strip('"') for f in v.split(",")]}
        elif k == "radius":
            tokens["radius"]["base"] = {"$type": "dimension", "$value": v}
            tokens["radius"]["xl"] = {"$type": "dimension", "$value": f"calc({v} + 4px)"}
            tokens["radius"]["lg"] = {"$type": "dimension", "$value": v}
            tokens["radius"]["md"] = {"$type": "dimension", "$value": f"calc({v} - 2px)"}
            tokens["radius"]["sm"] = {"$type": "dimension", "$value": f"calc({v} - 4px)"}
        elif k.startswith("shadow-"):
            tokens["shadow"][k[7:]] = {"$type": "shadow", "$value": v, "$extensions": {"modes": {"dark": dark.get(k, v)}}}
        elif k in ("sidebar-width", "sidebar-width-collapsed", "header-height"):
            tokens["layout"][k] = {"$type": "dimension", "$value": v}
        elif re.match(r"oklch\(|#|var\(", v):
            tokens["color"][k] = {"$type": "color", "$value": v, "$extensions": {"modes": {"dark": dark.get(k, v)}}}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    # An explicit newline, or the same command produces LF on Linux and CRLF on Windows, and the
    # "generated files match their sources" check cannot pass on a Windows machine.
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(tokens, fh, indent=2)
        fh.write("\n")
    print(f"wrote {out}: {len(tokens['color'])} colours, {len(tokens['radius'])} radii, {len(tokens['font'])} fonts, {len(tokens['shadow'])} shadows, {len(tokens['layout'])} layout")

if __name__ == "__main__":
    main()
