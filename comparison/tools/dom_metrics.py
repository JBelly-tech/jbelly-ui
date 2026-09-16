"""Deterministic page metrics from source HTML and a headless-rendered DOM dump.

Usage: python dom_metrics.py <name> <source.html> [<rendered_dom.html>] [--assets <dir>]
Prints one JSON object. Class D: no model involved.
"""
import json, re, sys, os
from html.parser import HTMLParser
from collections import Counter

PALETTE = r"(?<![\w-])(?:[\w-]+:)*(?:bg|text|border|ring|fill|stroke|from|via|to|divide|outline|shadow|accent)-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3}(?:/\d{1,3})?(?![\w-])"

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = Counter(); self.classes = Counter(); self.attrs = Counter()
        self.icon_only_buttons = 0; self.buttons_with_label = 0; self.depth = 0; self.max_depth = 0
        self._btn_stack = []
        self.text_chars = 0; self.in_script = 0; self.in_style = 0
    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1; self.depth += 1; self.max_depth = max(self.max_depth, self.depth)
        a = dict(attrs)
        for k in a:
            if k.startswith("aria-") or k in ("role", "tabindex", "alt", "for", "id"): self.attrs[k] += 1
        for c in (a.get("class") or "").split(): self.classes[c] += 1
        if tag in ("script",): self.in_script += 1
        if tag in ("style",): self.in_style += 1
        if tag in ("button", "a") and (a.get("aria-label")): self.buttons_with_label += 1
    def handle_endtag(self, tag):
        self.depth = max(0, self.depth - 1)
        if tag == "script": self.in_script = max(0, self.in_script - 1)
        if tag == "style": self.in_style = max(0, self.in_style - 1)
    def handle_data(self, data):
        if not self.in_script and not self.in_style: self.text_chars += len(data.strip())

def analyse(name, src_path, dom_path=None, assets_dir=None):
    src = open(src_path, encoding="utf-8", errors="replace").read()
    dom = open(dom_path, encoding="utf-8", errors="replace").read() if dom_path and os.path.exists(dom_path) else src
    p = P(); p.feed(dom)
    tags = p.tags
    out = {
        "name": name,
        "source_bytes": len(src.encode("utf-8")),
        "dom_elements": sum(tags.values()),
        "max_nesting_depth": p.max_depth,
        "visible_text_chars": p.text_chars,
        "buttons": tags["button"], "links": tags["a"], "inputs": tags["input"] + tags["select"] + tags["textarea"],
        "tables": tags["table"], "table_rows": tags["tr"], "svg": tags["svg"], "img": tags["img"],
        "headings": sum(tags[f"h{i}"] for i in range(1, 7)),
        "aria_attributes": sum(v for k, v in p.attrs.items() if k.startswith("aria-")),
        "role_attributes": p.attrs["role"],
        "icon_only_controls_labelled": p.buttons_with_label,
        "distinct_classes": len(p.classes),
        "class_tokens_total": sum(p.classes.values()),
        "raw_palette_classes_in_markup": len(re.findall(PALETTE, re.sub(r"<style[\s\S]*?</style>", "", src))),
        "css_custom_properties_defined": len(set(re.findall(r"--[a-z][\w-]*(?=\s*:)", src))),
        "logical_props": len(re.findall(r"\b(?:ps|pe|ms|me|start|end)-", src)),
        "physical_props": len(re.findall(r"\b(?:pl|pr|ml|mr|left|right)-\d", src)),
        "external_requests": len(re.findall(r"(?:src|href)=\"https?://", src)),
        "fonts": sorted(set(f.replace("+", " ") for f in re.findall(r"family=([A-Za-z+0-9]+)", src))),
        "has": {
            "dark_class_toggle": bool(re.search(r"classList\.(toggle|add)\(\s*['\"]dark['\"]", src)) or 'data-kt-theme-mode' in src,
            "rtl_support": 'dir="rtl"' in src or "rtl:" in src or "setAttribute('dir'" in src or 'setAttribute("dir"' in src,
            "localStorage": "localStorage" in src,
            "skeleton_state": bool(re.search(r"animate-pulse|skeleton", src)),
            "empty_state": bool(re.search(r"No (appointments|results|data)|empty", src, re.I)),
            "error_state": bool(re.search(r"Retry|Couldn.t|Something went wrong", src)),
            "esc_handler": "Escape" in src,
            "cmd_k": bool(re.search(r"key\s*(===|==)\s*['\"]k['\"]|toLowerCase\(\)\s*===\s*['\"]k['\"]", src)),
            "sr_only_table": "sr-only" in src and "<table" in src,
            "skip_link": bool(re.search(r"Skip to (main )?content", src, re.I)),
            "focus_visible": "focus-visible" in src,
            "reduced_motion": "prefers-reduced-motion" in src,
        },
    }
    if assets_dir and os.path.isdir(assets_dir):
        total = 0; by_ext = Counter()
        for root, _, files in os.walk(assets_dir):
            for f in files:
                sz = os.path.getsize(os.path.join(root, f)); total += sz; by_ext[os.path.splitext(f)[1].lower()] += sz
        out["assets_dir_bytes"] = total
        out["assets_by_ext_kb"] = {k: round(v / 1024) for k, v in by_ext.most_common(8)}
    return out

if __name__ == "__main__":
    args = sys.argv[1:]
    assets = None
    if "--assets" in args:
        i = args.index("--assets"); assets = args[i + 1]; del args[i:i + 2]
    name, src = args[0], args[1]
    dom = args[2] if len(args) > 2 else None
    print(json.dumps(analyse(name, src, dom, assets), indent=2))
