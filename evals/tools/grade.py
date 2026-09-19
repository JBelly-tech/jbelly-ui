"""Programmatic grader for dashboard evals (Class D).

Usage: python grade.py <iteration-dir>
Finds every run dir containing outputs/dashboard*.html and writes grading.json next to outputs/.
Checks are deterministic string/DOM heuristics; evidence strings explain each verdict.
v2: fairer checks: the primary-action count looks only at <button>/<a> elements outside nav/bulk bars,
    the personality check looks only at the --primary token, control heights accept CSS variables/component classes.
"""
import json, re, sys
from pathlib import Path

PALETTE = r"(?<![\w-])(?:[\w-]+:)*(?:bg|text|border|ring|fill|stroke|from|via|to|divide|outline|shadow|accent)-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3}(?:/\d{1,3})?(?![\w-])"

def strip_styles_scripts(html):
    return re.sub(r"<script[\s\S]*?</script>", "", re.sub(r"<style[\s\S]*?</style>", "", html))

def primary_hue_is_default_blue(html):
    ms = re.findall(r"--primary\s*:\s*([^;]+);", html)
    if not ms: return False
    v = ms[-1].strip().lower()  # last definition wins (theme overrides after the root defaults)
    if v in ("#2563eb", "#3b82f6", "#1d4ed8") or "blue-600" in v or "blue-500" in v: return True
    o = re.match(r"oklch\(\s*([\d.]+)%?\s+([\d.]+)\s+([\d.]+)", v)
    if o:
        hue = float(o.group(3)); l = float(o.group(1)); l = l if l > 1 else l * 100
        return 250 <= hue <= 268 and 50 <= l <= 66
    return False

def check(html: str):
    res = []
    markup = strip_styles_scripts(html)
    raw = re.findall(PALETTE, markup)
    res.append(("tokens-not-raw-palette", len(raw) == 0, f"{len(raw)} raw palette classes in markup" + (f", e.g. {sorted(set(raw))[:5]}" if raw else "")))

    fonts = sorted(set(f.replace("+", " ") for f in re.findall(r"family=([A-Za-z+0-9]+)", html)))
    has_tokens = bool(re.search(r"--primary\s*:", html))
    blue = primary_hue_is_default_blue(html)
    res.append(("deliberate-personality", has_tokens and not blue,
                f"--primary defined: {'yes' if has_tokens else 'no'}; default blue: {'yes' if blue else 'no'}; fonts={fonts or ['(system)']}"))

    dark_class = bool(re.search(r"classList\.(toggle|add)\(\s*['\"]dark['\"]", html)) and bool(re.search(r"@custom-variant dark|\.dark\s*\{", html))
    persisted = "localStorage" in html
    res.append(("dark-mode-class", dark_class and persisted, f"class toggle={'yes' if dark_class else 'no'}, localStorage={'yes' if persisted else 'no'}"))

    logical = len(re.findall(r"\b(?:ps|pe|ms|me|start|end|inset-inline-start|inset-inline-end)-", html))
    physical = len(re.findall(r"\b(?:pl|pr|ml|mr|left|right)-\d", html))
    mirrored = "rtl:" in html or "[dir=rtl]" in html or 'dir="rtl"' in html or "'rtl'" in html
    res.append(("rtl-logical-properties", logical >= 10 and physical <= max(3, logical // 5) and mirrored, f"logical={logical}, physical={physical}, rtl handling={'yes' if mirrored else 'no'}"))

    has_badge_text = bool(re.search(r"(Confirmed|Pending|Cancelled|No-show|Completed|In progress|Checked-in|مؤكد|قيد)", html))
    has_actions = bool(re.search(r"aria-label=\"(More|Open|Edit|Reschedule|Check-in|Cancel|Actions|Row actions)[^\"]*\"|data-open-drawer|row-actions|ellipsis", html))
    has_state = bool(re.search(r"animate-pulse|skeleton|shimmer|No (appointments|results|data)|empty-state|state=empty", html, re.I))
    res.append(("table-states-and-actions", has_badge_text and has_actions and has_state, f"badge text={has_badge_text}, row actions={has_actions}, loading/empty state={has_state}"))

    util_h = set(re.findall(r"\bh-(?:7|8|8\.5|9|10)\b", html))
    var_h = bool(re.search(r"--ctl-h|height:\s*var\(--", html)) or bool(re.search(r"\.btn\s*\{[^}]*height", html))
    res.append(("control-sizing-consistency", (1 <= len(util_h) <= 4) or var_h, f"utility heights={sorted(util_h) or 'none'}; component/variable heights={'yes' if var_h else 'no'}"))

    body = markup
    body = re.sub(r"<(nav|aside)\b[\s\S]*?</\1>", "", body)
    body = re.sub(r"<[^>]*id=\"bulk[^\"]*\"[\s\S]*?</div>", "", body)
    prim = re.findall(r"<(?:button|a)\b[^>]*class=\"[^\"]*(?:btn-primary|bg-primary text-primary-foreground)[^\"]*\"", body)
    res.append(("one-primary-per-view", 1 <= len(prim) <= 2, f"{len(prim)} primary control(s) outside nav/bulk bars (1 or 2 allowed: toolbar + one overlay confirm)"))

    focus = "focus-visible" in html
    esc = "Escape" in html
    ck = bool(re.search(r"key\s*(===|==)\s*['\"]k['\"]|toLowerCase\(\)\s*===\s*['\"]k['\"]", html))
    res.append(("keyboard-and-focus", focus and esc, f"focus-visible={focus}, Esc handler={esc}, Ctrl/Cmd+K={ck}"))
    return res

def main():
    it = Path(sys.argv[1])
    for html_path in sorted(it.rglob("dashboard*.html")):
        if "as-produced" in html_path.name or "parts" in html_path.parts or "outputs" not in html_path.parts: continue
        run_dir = html_path.parent.parent if html_path.parent.name == "outputs" else html_path.parent
        html = html_path.read_text(encoding="utf-8", errors="replace")
        results = check(html)
        (run_dir / "grading.json").write_text(json.dumps({"expectations": [{"text": n, "passed": ok, "evidence": ev} for n, ok, ev in results]}, indent=2), encoding="utf-8")
        passed = sum(1 for _, ok, _ in results if ok)
        print(f"{run_dir.name:18} {passed}/{len(results)}  " + "  ".join(f"{'PASS' if ok else 'FAIL'}:{n}" for n, ok, _ in results))

if __name__ == "__main__":
    main()
