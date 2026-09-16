"""Assemble report_data.json for build_report.py from an iteration folder (Class D).

Usage: python tools/assemble_report_data.py <iteration-dir> [<sections.json>]
Expects, inside <iteration-dir>:
  outputs/<maker>/dashboard-<maker>.html, notes.md, timing.json, grading.json
  shots/<maker>-{light-1440,dark-1440,rtl-1440,light-1024,light-500}.png
  metrics/metrics-<maker>.json, metrics/visual-<maker>.json
Makers: jbelly-ui, ui-ux-pro-max, no-skill (optional), reference-template (reference; shots in ../reference-template/).
Writes <iteration-dir>/report_data.json
"""
import json, os, sys

LABELS = {"jbelly-ui-v2": "jbelly-ui v2 (cost-first: spec build + one verify)", "jbelly-ui": "jbelly-ui v1 (full references)", "ui-ux-pro-max": "ui-ux-pro-max (catalogue skill)",
          "no-skill": "No skill (model alone)", "reference-template": "Commercial template (vendor demo, reference)"}
CONFIGS = [("1440 × 1000 · light", "light-1440"), ("1440 × 1000 · dark", "dark-1440"), ("1440 × 1000 · RTL", "rtl-1440"),
           ("1024 × 900 · light", "light-1024"), ("500 × 900 · light (mobile)", "light-500")]

def load(p, default=None):
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return default

def candidate(it, maker):
    shots_dir = os.path.join(it, "shots") if maker != "reference-template" else os.path.join(os.path.dirname(it.rstrip("/\\")), "reference-template")
    shots = {label: os.path.join(shots_dir, f"{maker}-{suffix}.png") for label, suffix in CONFIGS}
    vis = {("dark" if "dark" in x["name"] else "light"): x for x in load(os.path.join(it, "metrics", f"visual-{maker}.json"), [])}
    c = {"id": maker, "label": LABELS.get(maker, maker), "shots": shots,
         "metrics": load(os.path.join(it, "metrics", f"metrics-{maker}.json"), {}), "visual": vis, "cost": {}, "notes": ""}
    run = os.path.join(it, "outputs", maker)
    if os.path.isdir(run):
        c["cost"] = load(os.path.join(run, "timing.json"), {})
        g = load(os.path.join(run, "grading.json"), {})
        if g: c["cost"]["heuristics_passed"] = f"{sum(1 for e in g['expectations'] if e['passed'])} / {len(g['expectations'])}"
        try: c["notes"] = open(os.path.join(run, "notes.md"), encoding="utf-8").read()
        except Exception: pass
    if maker == "reference-template":
        c["notes"] = "Vendor demo dashboard rendered locally from its own package. Not built for this brief; a quality and weight yardstick only."
    return c

METRIC_ROWS = [
    ["Cost of producing it", "", ""],
    ["Model tokens", "cost.total_tokens", "Total tokens the building agent consumed (skill runs only)"],
    ["Wall time (s)", "cost.total_duration_seconds", ""],
    ["Tool calls", "cost.tool_uses", "Reads, searches, renders"],
    ["Heuristic checks passed", "cost.heuristics_passed", "Deterministic checks from grade.py"],
    ["Page weight", "", ""],
    ["Source bytes (HTML)", "metrics.source_bytes", "Single file for the skill runs; the template page excludes its assets"],
    ["Assets referenced (KB)", "metrics.assets_referenced_kb", "CSS + JS + images the page loads"],
    ["External requests", "metrics.external_requests", "Third-party URLs in src/href"],
    ["DOM elements (rendered)", "metrics.dom_elements", "Fewer for the same screen = leaner"],
    ["Max nesting depth", "metrics.max_nesting_depth", "Deep trees are harder to style and slower to lay out"],
    ["Distinct CSS classes", "metrics.distinct_classes", ""],
    ["Content & controls", "", ""],
    ["Visible text (chars)", "metrics.visible_text_chars", ""],
    ["Buttons", "metrics.buttons", ""],
    ["Inputs / selects", "metrics.inputs", ""],
    ["Tables", "metrics.tables", ""],
    ["Table rows", "metrics.table_rows", ""],
    ["SVG elements", "metrics.svg", "Charts and icons"],
    ["Images", "metrics.img", "Raster images (avatars, photos)"],
    ["Headings", "metrics.headings", ""],
    ["Accessibility signals", "", ""],
    ["aria-* attributes", "metrics.aria_attributes", ""],
    ["role attributes", "metrics.role_attributes", ""],
    ["Icon-only controls with a label", "metrics.icon_only_controls_labelled", "aria-label on buttons/links"],
    ["Skip link", "metrics.has.skip_link", ""],
    ["focus-visible styling", "metrics.has.focus_visible", ""],
    ["Reduced-motion respected", "metrics.has.reduced_motion", ""],
    ["sr-only table for charts", "metrics.has.sr_only_table", ""],
    ["Theming discipline", "", ""],
    ["Raw palette classes in markup", "metrics.raw_palette_classes_in_markup", "0 = every colour comes from tokens"],
    ["CSS custom properties defined", "metrics.css_custom_properties_defined", ""],
    ["Logical (RTL-safe) utilities", "metrics.logical_props", "ps-/pe-/ms-/me-/start-/end-"],
    ["Physical utilities", "metrics.physical_props", "pl-/pr-/ml-/mr-/left-/right-"],
    ["Dark mode class toggle", "metrics.has.dark_class_toggle", ""],
    ["RTL support", "metrics.has.rtl_support", ""],
    ["Preferences persisted", "metrics.has.localStorage", ""],
    ["Fonts", "metrics.fonts", ""],
    ["Behaviours", "", ""],
    ["Skeleton / loading state", "metrics.has.skeleton_state", ""],
    ["Empty state", "metrics.has.empty_state", ""],
    ["Error state with retry", "metrics.has.error_state", ""],
    ["Esc closes overlays", "metrics.has.esc_handler", ""],
    ["Ctrl/⌘+K palette", "metrics.has.cmd_k", ""],
    ["Visual analytics (1440 light screenshot)", "", ""],
    ["Distinct hues", "visual.light.distinct_hues", "Of 36 hue buckets; fewer = tighter palette"],
    ["Chromatic pixel share", "visual.light.chromatic_ratio", "How much of the screen is coloured vs neutral"],
    ["Accent share of coloured pixels", "visual.light.accent_share", "Higher = one primary colour dominates"],
    ["Ink ratio", "visual.light.ink_ratio", "Share of pixels darker than the page: text/line density"],
    ["Mean luminance", "visual.light.mean_luminance", ""],
    ["Hairline rows", "visual.light.hairline_rows", "Proxy for card/section borders"],
    ["Visual analytics (dark)", "", ""],
    ["Distinct hues (dark)", "visual.dark.distinct_hues", ""],
    ["Chromatic pixel share (dark)", "visual.dark.chromatic_ratio", ""],
    ["Mean luminance (dark)", "visual.dark.mean_luminance", ""],
]

def main():
    it = sys.argv[1]
    sections = load(sys.argv[2], []) if len(sys.argv) > 2 else []
    makers = [m for m in ("jbelly-ui-v2", "jbelly-ui", "ui-ux-pro-max", "no-skill") if os.path.isdir(os.path.join(it, "outputs", m))]
    makers.append("reference-template")
    cands = [candidate(it, m) for m in makers]
    title = os.path.basename(it.rstrip("/\\")).replace("-", " ")
    data = {"title": f"{title} — comparison", "subtitle": "Same brief, same model, parallel runs; headless Edge captures at 1440 / 1024 / 500 px. The commercial template is its vendor's demo dashboard, used as a yardstick, not built for the brief.",
            "candidates": cands, "metric_rows": METRIC_ROWS, "sections": sections}
    out = os.path.join(it, "report_data.json")
    json.dump(data, open(out, "w", encoding="utf-8"), indent=1)
    print("wrote", out, "candidates:", makers)

if __name__ == "__main__":
    main()
