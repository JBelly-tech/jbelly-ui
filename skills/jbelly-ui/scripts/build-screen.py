#!/usr/bin/env python3
"""Build a complete page from a small JSON spec, using one of the assets/*-shell.html files as the template (Class D).

The model writes ~2 KB of JSON instead of ~150 KB of HTML. Everything the spec does not mention keeps the
scaffold's defaults, so a partial spec still yields a working page.

`kind` picks the template, the spec schema and the checks that follow the build:
  "app"      (the default) an application screen  — assets/app-shell.html
  "landing"  a marketing home page                — assets/landing-shell.html
  "pricing"  plans, a billing toggle and a comparison table — assets/pricing-shell.html
A landing or pricing page written by hand cost 1.6x and 5.9x a generated dashboard in this repo's
own eval runs, which is what these two kinds exist to stop.

Usage:
  python scripts/build-screen.py spec.json out.html          (kind comes from the spec, default "app")
  python scripts/build-screen.py spec.json out.html --kind landing
  python scripts/build-screen.py --example > spec.json       (prints the example spec)
  python scripts/build-screen.py --example --kind pricing > spec.json

Keys shared by every kind (all optional except product/title):
  kind, product, title, theme, density, dark, dir, lang, i18n: { ar: { "English": "العربية", ... } }

app spec keys: see assets/spec.example.json
  subtitle,
  nav: [ {heading} | {label, icon, active, badge, children:[...]} ],
  toolbar: { periods:[...], secondary, primary },
  kpis: [ {label, value, delta, trend:"up|down", icon, spark:[numbers]} ]  (1–6),
  chart: { title, subtitle, series:[{name,data}], categories:[...], axis } (axis names the category
         column of the chart's screen-reader table; it keeps the shell's word when the spec omits it),
  highlights: { title, total_label, total, delta, trend:"up|down", items:[{label, value}] },
  table: { title, count, columns:[4 labels], rows:[{name, initials, sub, plan, status, time}] },
         sub is the second line under the name, plan is the Item column; either one alone fills both.
  activity: [ {who, text, when, primary} ],
  extra_html: "<div class='card'>...</div>"   (appended as a full-width row after the table row)

landing spec keys: see assets/spec.landing.example.json
  description (the meta description, and the line under the footer brand), icon (a lucide name for the brand mark),
  nav: [ {label, href} ]              (defaults to the sections' own names),
  actions: { sign_in, primary }       (primary defaults to the hero's),
  hero: { eyebrow, headline, lead, primary, secondary, note, panel },
  logos: { caption, names:[...], note },
  sections: [ {step, title, lead, ticks:[...], link:"text"|{label,href}, panel, stats:[{value,label}]} ],
         numbered in order; every second one takes the muted surface and reverses its columns.
  panel (in the hero and in any section): { title, meta, badge, tone:"success|warning|primary",
         rows: [{label, meta, status, tone, bar: 0-100}], ticks:[...], note },
  testimonial: { quote, name, role, badge },
  pricing: { eyebrow, title, lead, price, price_note, ticks:[...], cta },
  faq: { eyebrow, title, note, items:[{q, a}] },
  cta: { title, lead, note, primary, secondary },
  footer: { tagline, columns:[{heading, links:[...]}], legal, contact }
  Anchors a nav or link href can point at: #hero #customers #<section step> #pricing #faq #start

pricing spec keys: see assets/spec.pricing.example.json
  icon, nav: [ {label, href, active} ], actions: { sign_in },
  intro: { title, lead, monthly, yearly, save, monthly_note, yearly_note, period,
           billed_monthly, billed_yearly },      (the last two are the default for every plan)
  plans: [ {name, blurb, price, price_yearly, yearly_total, period, cta, badge, featured,
            inherits, features:[...]} ]  — 1 to 4; price_yearly on any plan raises the billing toggle,
         and cta defaults to the page's own call to action.
  note (the line under the plan grid),
  comparison: { title, lead, caption, feature_column,
                groups: [ {heading, rows:[{label, cells:[...]}]} ] }
         one cell per plan, in the plans' order: true = included, false = not, anything else is printed.
  faq: { title, items:[{q, a}] },
  cta: { title, lead, primary, secondary },
  footer: { legal, links:[...] }
"""
import json, os, re, sys, html
try:    # "--example > spec.json" must write the Arabic labels whole; a cp1252 console truncates the spec
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def asset(name): return os.path.join(ROOT, "assets", name)

# What the shipped app shell says today, per slot. The generator swaps these for the spec's words;
# if the shell is reworded, update this table -- tests/smoke.py builds a spec with different
# words on purpose and fails when a slot stops landing.
SHELL = {
    "brand": "Bayan Ops",
    "chart_title": "Orders per week",
    "series": ["Completed", "Refunded"],
    "highlights_title": "Highlights",
    "highlights_total_label": "Orders completed",
    "table_title": "Recent orders",
    "columns": ["Customer", "Item", "Status", "Time"],
    # Demo copy the generator must not leave on a real page.
    "palette_actions": [("New order", "N"), ("Add customer", "P")],
    "palette_people": ["Sara Khalil", "Omar Haddad"],
    "palette_group": "Customers",
    "empty_title": "No orders match",
    "notifications": ["Order #1042 delivered", "Payment pending on #1039", "New wholesale account"],
}

def esc(x): return html.escape(str(x), quote=True)
def js(x): return json.dumps(x, ensure_ascii=False)

# Anchors that matched nothing. A page built over a stale anchor keeps the shell's demo content and
# still looks built, so main() turns anything recorded here into a non-zero exit, not a warning.
MISSES = []

def sub1(s, pattern, repl, what):
    """re.sub(count=1) that cannot fail quietly. repl is always a function, so no backslash is special."""
    out, n = re.subn(pattern, repl, s, count=1)
    if n == 0: MISSES.append(what)
    return out

def region(s, name, new_inner, through=None):
    """Rebuild the markup between a region's markers.

    `through` names a later region's closing marker, so a run of regions that are one shape repeated
    is rebuilt from one list. new_inner=None deletes the span outright: on the landing and pricing
    kinds a region the spec says nothing about must not ship the shell's demo copy instead.
    """
    pat = re.compile(r"(<!-- @region " + name + r" -->\n)([\s\S]*?)(<!-- @endregion " + (through or name) + r" -->)")
    if not pat.search(s):
        MISSES.append(f"region {name} (the shell's own {name} markup shipped instead)"); return s
    if new_inner is None: return pat.sub("", s, count=1)
    return pat.sub(lambda m: m.group(1) + new_inner + "\n" + m.group(3), s, count=1)

def build_nav(items):
    out = ['<nav class="grow overflow-y-auto scroll-thin py-3 ps-5 pe-3 flex flex-col gap-1">']
    for it in items:
        if "heading" in it:
            out.append(f'    <div class="nav-heading" data-i18n="{esc(it["heading"])}">{esc(it["heading"])}</div>'); continue
        label, icon = it.get("label", ""), it.get("icon", "circle")
        badge = f'<span class="nav-badge badge badge-sm badge-outline">{esc(it["badge"])}</span>' if it.get("badge") else ""
        if it.get("children"):
            kids = "".join(f'\n        <a class="nav-child{" active" if c == it.get("active_child") else ""}" href="#" data-i18n="{esc(c)}">{esc(c)}</a>' for c in it["children"])
            out.append(f'    <div class="nav-group{" open" if it.get("open", True) else ""}">\n      <a class="nav-link" href="#" data-toggle-group role="button" aria-expanded="{"true" if it.get("open", True) else "false"}" data-motion="state"><i data-lucide="{esc(icon)}"></i><span class="nav-title grow truncate" data-i18n="{esc(label)}">{esc(label)}</span><i data-lucide="chevron-right" class="nav-arrow disclosure-chevron size-4!"></i></a>\n      <div class="nav-children">{kids}\n      </div>\n    </div>')
        else:
            active = ' active" aria-current="page' if it.get("active") else ''
            out.append(f'    <a class="nav-link{active}" href="#"><i data-lucide="{esc(icon)}"></i><span class="nav-title grow truncate" data-i18n="{esc(label)}">{esc(label)}</span>{badge}</a>')
    out.append("  </nav>")
    return "\n".join(out)

def build_toolbar(spec):
    t = spec.get("toolbar", {})
    periods = t.get("periods", ["Last 7 days", "Last 30 days", "This quarter"])
    opts = "".join(f'<option{" selected" if i == min(1, len(periods)-1) else ""} data-i18n="{esc(p)}">{esc(p)}</option>' for i, p in enumerate(periods))
    sec = t.get("secondary", "Export"); prim = t.get("primary", "New item")
    return f'''      <!-- toolbar -->
      <div class="flex flex-wrap items-center justify-between gap-5 pb-7.5">
        <div class="flex flex-col gap-1">
          <h1 class="text-xl font-medium text-mono font-display" data-i18n="{esc(spec.get("title","Dashboard"))}">{esc(spec.get("title","Dashboard"))}</h1>
          <p class="text-2sm text-secondary-foreground">{esc(spec.get("subtitle",""))}{" · " if spec.get("subtitle") else ""}<span id="period-label">{esc(periods[min(1, len(periods)-1)])}</span></p>
        </div>
        <div class="flex flex-wrap items-center gap-2.5">
          <select id="period" class="input select w-40">{opts}</select>
          <button class="btn btn-outline"><i data-lucide="download"></i><span data-i18n="{esc(sec)}">{esc(sec)}</span></button>
          <button class="btn btn-primary" data-toast="{esc(prim)}" data-toast-undo><i data-lucide="plus"></i><span data-i18n="{esc(prim)}">{esc(prim)}</span></button>
        </div>
      </div>
'''

def derive_copy(s, spec):
    """Replace the shell's demo nouns with the spec's own words.

    Nothing here asks the spec for anything new. The palette's actions are the toolbar's buttons,
    the people it lists are the table's first rows, the empty state names the table, and the
    notification tray shows the activity feed. A page that cannot supply a line loses that line
    instead of shipping the demo's.
    """
    tb = spec.get("table") or {}
    toolbar = spec.get("toolbar") or {}

    # Command palette: actions first, then the people the table is actually about.
    actions = [a for a in (toolbar.get("primary"), toolbar.get("secondary")) if a]
    for (old, _kbd), new in zip(SHELL["palette_actions"], actions):
        s = s.replace(f">{old}<", f">{esc(new)}<")
    if len(actions) < len(SHELL["palette_actions"]):          # nothing to put there: drop the row
        for old, _kbd in SHELL["palette_actions"][len(actions):]:
            s = re.sub(r'<a class="menu-item" href="#">(?:(?!</a>).)*?>' + re.escape(old) +
                       r'<(?:(?!</a>).)*?</a>\s*', "", s, count=1)
    rows = tb.get("rows") or []
    for old, row in zip(SHELL["palette_people"], rows):
        s = s.replace(f">{old}<", f">{esc(row.get('name', old))}<")
    if len(rows) < len(SHELL["palette_people"]):
        for old in SHELL["palette_people"][len(rows):]:
            s = re.sub(r'<a class="menu-item" href="#">(?:(?!</a>).)*?>' + re.escape(old) +
                       r'<(?:(?!</a>).)*?</a>\s*', "", s, count=1)
    if tb.get("title"):
        s = s.replace(f">{SHELL['palette_group']}<", f">{esc(tb['title'])}<")

    # Empty state: name the thing the table holds.
    if tb.get("title"):
        s = s.replace(SHELL["empty_title"], "No " + esc(tb["title"]).lower() + " match")

    # Notification tray: the activity feed is the same information, already in the spec.
    acts = spec.get("activity") or []
    for old, a in zip(SHELL["notifications"], acts):
        line = f"{a.get('who', '')} {a.get('text', '')}".strip() or old
        s = s.replace(f">{old}<", f">{esc(line)}<")
    if len(acts) < len(SHELL["notifications"]):
        for old in SHELL["notifications"][len(acts):]:
            s = re.sub(r'<a class="menu-item items-start"[\s\S]{0,400}?>' + re.escape(old) +
                       r'<[\s\S]{0,300}?</a>\s*', "", s, count=1)
    return s


def build_kpis(kpis):
    n = max(1, min(6, len(kpis)))
    cols = {1: "sm:grid-cols-1", 2: "sm:grid-cols-2", 3: "sm:grid-cols-3", 4: "sm:grid-cols-2 xl:grid-cols-4", 5: "sm:grid-cols-2 xl:grid-cols-5", 6: "sm:grid-cols-2 xl:grid-cols-3"}[n]
    cards = []
    for k in kpis[:6]:
        up = k.get("trend", "up") == "up"
        badge = f'<span class="badge badge-sm {"badge-light-success" if up else "badge-light-destructive"}"><i data-lucide="{"trending-up" if up else "trending-down"}" class="size-3"></i>{esc(k.get("delta",""))}</span>' if k.get("delta") else ""
        spark = f'<div class="h-10 -mx-1 -mb-2 apex-spark" data-spark="{",".join(str(v) for v in k["spark"])}"></div>' if k.get("spark") else ""
        cards.append(f'''          <div class="card p-(--card-p) gap-6 justify-between overflow-hidden">
            <div class="flex items-center justify-between"><span class="inline-flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary-accent"><i data-lucide="{esc(k.get("icon","activity"))}" class="size-5"></i></span>{badge}</div>
            <div class="flex flex-col gap-1"><span class="text-3xl font-semibold text-mono tabular-nums font-display">{esc(k.get("value",""))}</span><span class="text-sm text-secondary-foreground" data-i18n="{esc(k.get("label",""))}">{esc(k.get("label",""))}</span></div>{spark}
          </div>''')
    return f'        <!-- KPIs -->\n        <div class="grid {cols} gap-(--page-gap)" id="kpis">\n' + "\n".join(cards) + "\n        </div>"

CHART_DOTS = ["bg-primary", "bg-muted-foreground/40", "bg-info", "bg-success", "bg-warning"]

def chart_legend(names):
    return "".join(f'<span class="flex items-center gap-1.5 text-2sm text-secondary-foreground"><span class="size-2 rounded-full {CHART_DOTS[i % len(CHART_DOTS)]}"></span>{esc(n)}</span>'
                   for i, n in enumerate(names))

def sr_table(axis, title, cats, series):
    """The chart's text alternative. It carries every point the chart draws, so the screen-reader version
    cannot drift from the picture -- the three hand-written sample rows it replaces kept the demo's numbers."""
    head = "".join(f"<th>{esc(x.get('name',''))}</th>" for x in series)
    body = ""
    for i, c in enumerate(cats):
        cells = "".join(f"<td>{esc(x['data'][i]) if i < len(x.get('data') or []) else ''}</td>" for x in series)
        body += f"<tr><td>{esc(c)}</td>{cells}</tr>"
    return f'<table class="sr-only"><caption>{esc(title)}</caption><thead><tr><th>{esc(axis)}</th>{head}</tr></thead><tbody>{body}</tbody></table>'

def chart_aria(title, cats, series):
    parts = [f"{x.get('name','')} from {x['data'][0]} to {x['data'][-1]}" for x in series if x.get("data")]
    if not parts: return title
    span = f", across {len(cats)} points from {cats[0]} to {cats[-1]}" if cats else ""
    return f"{title}: " + "; ".join(parts) + span

def present(value, page):
    """A spec value can reach the page raw, HTML-escaped, or JSON-escaped inside a <script>."""
    v = str(value)
    return v in page or html.escape(v, quote=True) in page or js(v)[1:-1] in page

def applied_check(spec, out_html):
    """Every label the spec asked for must be in the page. A miss means an anchor went stale."""
    want = []
    if spec.get("product"): want.append(("product", spec["product"]))
    for i, it in enumerate(spec.get("nav") or []):
        for key in ("heading", "label"):
            if it.get(key): want.append((f"nav[{i}].{key}", it[key]))
    tbar = spec.get("toolbar") or {}
    for i, p in enumerate(tbar.get("periods") or []):
        want.append((f"toolbar.periods[{i}]", p))
    for key in ("secondary", "primary"):
        if tbar.get(key): want.append((f"toolbar.{key}", tbar[key]))
    for i, k in enumerate((spec.get("kpis") or [])[:6]):
        for key in ("label", "value", "delta"):
            if k.get(key): want.append((f"kpis[{i}].{key}", k[key]))
    ch = spec.get("chart") or {}
    if ch.get("title"): want.append(("chart.title", ch["title"]))
    for i, ser in enumerate(ch.get("series") or []):
        if ser.get("name"): want.append((f"chart.series[{i}].name", ser["name"]))
    hl = spec.get("highlights") or {}
    if hl.get("title"): want.append(("highlights.title", hl["title"]))
    if hl.get("total_label"): want.append(("highlights.total_label", hl["total_label"]))
    if hl.get("delta"): want.append(("highlights.delta", hl["delta"]))
    tb = spec.get("table") or {}
    if tb.get("title"): want.append(("table.title", tb["title"]))
    for i, a in enumerate((spec.get("activity") or [])[:1]):
        if a.get("text"): want.append((f"activity[{i}].text", a["text"]))
    for i, c in enumerate(tb.get("columns") or []):
        want.append((f"table.columns[{i}]", c))
    for i, r in enumerate(tb.get("rows") or []):
        for key in ("name", "sub", "plan", "status", "time"):
            if r.get(key): want.append((f"table.rows[{i}].{key}", r[key]))
    for i, a in enumerate(spec.get("activity") or []):
        for key in ("who", "text", "when"):
            if a.get(key): want.append((f"activity[{i}].{key}", a[key]))
    return [(field, value) for field, value in want if not present(value, out_html)]

# ---------------------------------------------------------------- shared ----
# What every kind does the same way: the head, the Arabic dictionary and the demo panel.

THEME_FONTS = {"theme-clinic": ["Manrope:wght@400;500;600;700"], "theme-graphite": ["IBM+Plex+Sans:wght@400;500;600", "IBM+Plex+Mono:wght@400;500"],
               "theme-editorial": ["Fraunces:opsz,wght@9..144,500;9..144,600", "Source+Sans+3:wght@400;500;600"], "theme-neo": ["Space+Grotesk:wght@500;600;700", "DM+Sans:wght@400;500;600"],
               "theme-slate": [], "theme-mint": ["Plus+Jakarta+Sans:wght@400;500;600;700"]}

def set_head(s, spec, base="", theme="", density=""):
    """Title, language, direction, theme classes and the font link.

    base, theme and density are what the shell already carries, so a spec that says nothing about
    them keeps the look its template was verified in.
    """
    th = spec.get("theme", theme)
    classes = " ".join(c for c in [base, th, spec.get("density", density), "dark" if spec.get("dark") else ""] if c)
    opening = f'<html lang="{esc(spec.get("lang", "en"))}" dir="{esc(spec.get("dir", "ltr"))}" class="{classes}">'
    s = sub1(s, r"<html[^>]*>", lambda m: opening, "<html> opening tag")
    head = f"<title>{esc(spec.get('product', 'Product'))} — {esc(spec.get('title', 'Page'))}</title>"
    s = sub1(s, r"<title>[\s\S]*?</title>", lambda m: head, "<title>")
    if '<meta name="description"' in s:   # never ship the demo's: rewrite it, or drop the tag
        s = sub1(s, r'<meta name="description" content="[^"]*">\n?',
                 lambda m: f'<meta name="description" content="{esc(spec["description"])}">\n' if spec.get("description") else "",
                 "meta description")
    # the shells load every personality's families so the demo can switch live; a built page needs one
    fams = ["Inter:wght@400;500;600"] + THEME_FONTS.get(th, []) + ["Noto+Sans+Arabic:wght@400;500;600"]
    return re.sub(r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">',
                  '<link href="https://fonts.googleapis.com/css2?' + "&".join("family=" + f for f in fams) + '&display=swap" rel="stylesheet">', s, count=1)

def apply_i18n(s, spec):
    """Drop the dictionary keys whose English left with the demo copy, then add the spec's own pairs."""
    def prune(m):
        d = json.loads(m.group(1))
        page_without_dict = s.replace(m.group(0), "")
        kept = {k: v for k, v in d.items() if k in page_without_dict}
        kept.update((spec.get("i18n") or {}).get("ar") or {})
        return "const I18N = " + js(kept) + ";"
    return re.sub(r"const I18N = (\{[\s\S]*?\});", prune, s, count=1)

def strip_demo_controls(s, spec):
    """The demo panel is not part of a built page; every control it drives is guarded in the shells."""
    if spec.get("keep_demo_controls"): return s
    return re.sub(r"(?s)<!-- ===== Demo controls.*?</details>\s*", "", s)

def slug(text):
    """A section's id, and what a nav link points at."""
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-") or "section"

def i18n(text):
    """Every visible string carries its own English as data-i18n: that attribute is the key the
    Arabic dictionary is looked up by, so a generated line translates like the shell's own."""
    t = esc(text)
    return f'<span data-i18n="{t}">{t}</span>'

def initials(name):
    return "".join(w[0] for w in str(name).split()[:2]).upper()

TONES = {"success": "badge-light-success", "warning": "badge-light-warning", "primary": "badge-light-primary"}

def leftovers(s, shell):
    """Demo copy still on the page.

    The landing and pricing kinds rebuild each region whole instead of swapping words inside it, so
    the failure they have to catch is the opposite of the app's: not a field that never landed, but
    a region that was never rebuilt. applied_check cannot see that -- the fields it looks for may
    all have landed in the regions that were -- so the shell's own wording is asserted against too.
    """
    out = []
    for slot, phrases in shell.items():
        for phrase in phrases:
            if phrase in s: out.append(f"region {slot} kept the shell's own copy: {phrase[:48]!r}")
    return out


# ---------------------------------------------------------------- app ----

def build_app(spec, s):
    s = set_head(s, spec, base="h-full")
    s = s.replace(f'<span class="font-display">{SHELL["brand"]}</span>', f'<span class="font-display">{esc(spec.get("product", "Product"))}</span>')
    s = s.replace(f'© 2026 {SHELL["brand"]}', f'© 2026 {esc(spec.get("product", "Product"))}')
    if spec.get("nav"): s = region(s, "nav", build_nav(spec["nav"]))
    s = region(s, "toolbar", build_toolbar(spec))
    # The period control is keyed by the period's own name, so a spec that names its own periods
    # left every lookup missing and the control moved nothing. The table is built from the spec.
    periods = (spec.get("toolbar") or {}).get("periods") or ["Last 7 days", "Last 30 days", "This quarter"]
    kpis_for_table = spec.get("kpis") or []
    if kpis_for_table and periods:
        sel = min(1, len(periods) - 1)                 # build_toolbar selects this one
        def as_num(v):
            t = str(v).replace(",", "").strip()
            keep = "".join(c for c in t if c.isdigit() or c == ".")
            try: return float(keep) if keep else 0.0
            except ValueError: return 0.0
        def fmt(sample, value):
            t = str(sample)
            # However many decimals the spec printed, print that many. A rate written 78% does not
            # become 74.88% because the window moved.
            dp = len(t.split(".")[1].rstrip("%").strip()) if "." in t else 0
            body = f"{value:,.{dp}f}" if ("," in t or value >= 1000) else f"{value:.{dp}f}"
            pre = t[:len(t) - len(t.lstrip("$£€"))]
            suf = "%" if t.rstrip().endswith("%") else ""
            return pre + body + suf
        base = [as_num(k.get("value", 0)) for k in kpis_for_table]
        # A longer window holds more; the shape is the spec's numbers scaled by the window's length.
        weight = {p: (i + 1) / (sel + 1) for i, p in enumerate(periods)}
        rows = []
        for idx, name in enumerate(periods):
            w = weight[name] if name != periods[sel] else 1.0
            vals = []
            for k, b in zip(kpis_for_table, base):
                sample = str(k.get("value", 0))
                if sample.rstrip().endswith("%"):
                    # A rate drifts with the window; it does not multiply by it.
                    v = max(0.0, min(100.0, b * (0.96 + 0.02 * idx)))
                else:
                    v = b * w
                vals.append(fmt(k.get("value", 0), v))
            rows.append(f"  {js(name)}: {js(vals)},")
        s = sub1(s, r"const KPI_PERIODS = \{[\s\S]*?\n\};",
                 lambda m: "const KPI_PERIODS = {\n" + "\n".join(rows) + "\n};",
                 "period -> KPI table")
        s = sub1(s, r"let kpiPeriod = '[^']*';",
                 lambda m: "let kpiPeriod = " + js(periods[sel]) + ";",
                 "the period the page opens on")

    if spec.get("kpis"): s = region(s, "kpis", build_kpis(spec["kpis"]))
    ch = spec.get("chart")
    if ch:
        ct = ch.get("title", "Trend"); old_ct = SHELL["chart_title"]
        s = s.replace(f'data-i18n="{old_ct}">{old_ct}</h3>', f'data-i18n="{esc(ct)}">{esc(ct)}</h3>')
        series = [x for x in ch.get("series", []) if x.get("name")]
        if series:
            # the whole chip strip is rebuilt rather than swapped name by name: pairing the spec's names
            # against the shell's left the shell's spare chip behind whenever the spec had fewer series.
            s = sub1(s, r'(?:<span class="flex items-center gap-1\.5 text-2sm text-secondary-foreground"><span class="size-2 rounded-full [^"]*"></span>[^<]*</span>)+',
                     lambda m: chart_legend([x["name"] for x in series]), "chart legend chips")
        cats = ch.get("categories")
        if not cats:                                            # no categories in the spec: keep the shell's axis
            cm = re.search(r"categories: \[([^\]]*)\]", s)   # the shell writes them as 'W1','W2',...
            cats = re.findall(r"'([^']*)'", cm.group(1)) if cm else []
        s = sub1(s, r'<table class="sr-only"><caption>[\s\S]*?<thead><tr><th>([^<]*)</th>[\s\S]*?</table>',
                 lambda m: sr_table(ch.get("axis") or m.group(1), ct, cats, series), "chart sr-only data table")
        s = sub1(s, r'(<div id="chart-visits"[^>]*aria-label=")[^"]*(")',
                 lambda m: m.group(1) + esc(chart_aria(ct, cats, series)) + m.group(2), "chart aria-label")
        s = sub1(s, r"series: \[\{ name: '[^']*', data: \[[^\]]*\] \}, \{ name: '[^']*', data: \[[^\]]*\] \}\]",
                 lambda m: "series: " + js([{"name": x["name"], "data": x.get("data", [])} for x in series]), "chart series data")
        if ch.get("categories"):
            s = sub1(s, r"categories: \['W1'[^\]]*\]", lambda m: "categories: " + js(ch["categories"]), "chart categories")
            ymax = max(max(x["data"]) for x in series if x.get("data")) if series else 100
            import math
            m = ymax * 1.15; step = 10 ** max(0, int(math.floor(math.log10(max(m, 1))))); step = step if m / step >= 4 else step / 2
            nice = int(math.ceil(m / step) * step)
            s = s.replace("{ min: 0, max: 100, tickAmount: 4 }", "{ min: 0, max: %d, tickAmount: 4 }" % nice)
    hl = spec.get("highlights") or {}
    if hl.get("delta"):
        # the shell hard-codes a green "up" badge, so a falling delta has to repaint it too
        up = hl.get("trend", "down" if str(hl["delta"]).lstrip().startswith("-") else "up") == "up"
        s = sub1(s, r'<span id="hl-delta" class="badge badge-sm badge-light-(?:success|destructive) mb-1"><i data-lucide="trending-(?:up|down)" class="size-3"></i><span data-hl="delta">[^<]*</span></span>',
                 lambda m: f'<span id="hl-delta" class="badge badge-sm badge-light-{"success" if up else "destructive"} mb-1">'
                           f'<i data-lucide="trending-{"up" if up else "down"}" class="size-3"></i>'
                           f'<span data-hl="delta">{esc(hl["delta"])}</span></span>',
                 "highlights.delta badge")
    if hl.get("items"):
        items = hl["items"]; total = sum(int(str(i.get("value", 0)).replace(",", "")) for i in items)
        ht = hl.get("title", SHELL["highlights_title"]); old_ht = SHELL["highlights_title"]
        s = s.replace(f'data-i18n="{old_ht}">{old_ht}</h3>', f'data-i18n="{esc(ht)}">{esc(ht)}</h3>')
        old_tl = SHELL["highlights_total_label"]; tl = hl.get("total_label", old_tl)
        s = s.replace(f'data-i18n="{old_tl}">{old_tl}</span>', f'data-i18n="{esc(tl)}">{esc(tl)}</span>')
        s = s.replace('<span id="hl-total" class="text-2xl font-semibold text-mono tabular-nums font-display">214</span>', f'<span class="text-2xl font-semibold text-mono tabular-nums font-display">{esc(hl.get("total", total))}</span>')
        # The shell reads its series from PERIOD so the month/quarter control can redraw the donut.
        # A generated page has one period, so both entries carry the spec's numbers.
        vals = [int(str(i.get("value", 0)).replace(",", "")) for i in items]
        s = sub1(s, r"month:\s*\{[^}]*\}", lambda m: "month:   { total: " + js(total) +
                 ", delta: " + js(str(hl.get("delta", ""))) + ", up: " + ("true" if up else "false") +
                 ", split: " + js(vals) + " }", "highlights period data")
        s = sub1(s, r"quarter:\s*\{[^}]*\}", lambda m: "quarter: { total: " + js(total) +
                 ", delta: " + js(str(hl.get("delta", ""))) + ", up: " + ("true" if up else "false") +
                 ", split: " + js(vals) + " }", "highlights period data (quarter)")
        s = sub1(s, r"labels: \['Online store', 'Marketplace', 'Wholesale', 'In-store'\]",
                 lambda m: "labels: " + js([i["label"] for i in items]),
                 "highlights donut labels")
        dots = ["bg-primary", "bg-info", "bg-success", "bg-warning", "bg-muted-foreground"]
        legend = "\n".join(f'                <div class="flex justify-between"><span class="flex items-center gap-2"><span class="size-2 rounded-full {dots[i % 5]}"></span><span data-i18n="{esc(it["label"])}">{esc(it["label"])}</span></span><span class="text-mono font-medium tabular-nums">{esc(it.get("value",""))}</span></div>' for i, it in enumerate(items))
        s = sub1(s, r'<div class="flex flex-col gap-2\.5 text-2sm">[\s\S]*?</div>\n[ \t]*</div>\n[ \t]*<div class="card-footer justify-center">',
                 lambda m: '<div class="flex flex-col gap-2.5 text-2sm">\n' + legend + '\n              </div>\n            </div>\n            <div class="card-footer justify-center">',
                 "highlights legend")
    tb = spec.get("table")
    if tb:
        old_tt = SHELL["table_title"]; tt = tb.get("title", old_tt)
        s = s.replace(f'data-i18n="{old_tt}">{old_tt}</h3><span class="badge badge-sm badge-outline">24</span>',
                      f'data-i18n="{esc(tt)}">{esc(tt)}</h3><span class="badge badge-sm badge-outline">{esc(tb.get("count", len(tb.get("rows", []))))}</span>')
        cols = tb.get("columns")
        if cols and len(cols) == len(SHELL["columns"]):
            for old, new in zip(SHELL["columns"], cols):
                s = s.replace(f'data-i18n="{old}">{old}', f'data-i18n="{esc(new)}">{esc(new)}', 1)
        if tb.get("rows"):
            rows = []
            for r in tb["rows"]:
                sub = str(r.get("sub", ""))
                plan = r.get("plan") or sub.split(" \u00b7")[0]   # shell convention: "plan . detail" in one string
                rows.append({"n": r.get("name", ""), "i": r.get("initials", "".join(w[0] for w in r.get("name", "??").split()[:2]).upper()),
                             "p": plan, "sub": sub or plan, "s": r.get("status", ""), "t": r.get("time", "")})
            s = sub1(s, r"const rows = \[[\s\S]*?\n\];", lambda m: "const rows = " + js(rows) + ";", "table rows")
            # the shell prints one field in both slots, which threw away whichever of sub/plan lost;
            # give the second line its own field so a row can say two different things.
            s = sub1(s, r'<span class="text-2sm text-secondary-foreground truncate">\$\{r\.p\}</span>',
                     lambda m: '<span class="text-2sm text-secondary-foreground truncate">${r.sub}</span>', "table row sub-line")
            s = sub1(s, r'<td class="text-secondary-foreground whitespace-nowrap">\$\{r\.p\.split\([^)]*\)\[0\]\}</td>',
                     lambda m: '<td class="text-secondary-foreground whitespace-nowrap">${r.p}</td>', "table row item cell")
            s = s.replace("<span>1–5 of 24</span>", f"<span>1–{min(5, len(rows))} of {tb.get('count', len(rows))}</span>")
    act = spec.get("activity")
    if act:
        items = []
        for i, a in enumerate(act):
            last = i == len(act) - 1
            dot = "bg-primary" if a.get("primary") or i == 0 else "bg-muted-foreground"
            items.append(f'''              <div class="relative flex gap-3 {"" if last else "pb-6 "}ps-6{"" if last else " before:absolute before:start-2 before:top-6 before:bottom-0 before:w-px before:bg-border"}"><span class="absolute start-0 top-1 size-4 rounded-full border-2 border-background {dot}"></span><div class="flex flex-col gap-1"><p class="text-2sm"><span class="font-medium text-mono">{esc(a.get("who",""))}</span> {esc(a.get("text",""))}</p><span class="text-xs text-muted-foreground">{esc(a.get("when",""))}</span></div></div>''')
        # the closing marker is indented in the shell, so the anchor may not assume column 0
        s = sub1(s, r'(<div class="card-content flex flex-col">\n)[\s\S]*?(\n[ \t]*</div>\n[ \t]*</div>\n[ \t]*</div>\n[ \t]*<!-- @endregion row3 -->)',
                 lambda m: m.group(1) + "\n".join(items) + m.group(2), "activity timeline")
    s = derive_copy(s, spec)
    if spec.get("extra_html"):
        s = s.replace("<!-- @endregion row3 -->", spec["extra_html"] + "\n<!-- @endregion row3 -->")
    s = apply_i18n(s, spec)          # apply_i18n already merges spec["i18n"]["ar"] into what it keeps
    s = strip_demo_controls(s, spec)
    if not spec.get("keep_demo_controls"):
        # The demo panel held the only language switch. A shipped page still needs one, so the
        # header gets a real control bound to the same function.
        if '<button id="lang-toggle"' not in s:
            s = s.replace('<button id="theme-toggle"',
                          '<button id="lang-toggle" class="btn btn-ghost btn-icon" '
                          'aria-label="Switch language" title="English / العربية">'
                          '<i data-lucide="languages"></i></button>\n        '
                          '<button id="theme-toggle"', 1)
            s = s.replace("renderRows(); lucide.createIcons(); mountCharts();",
                          "if ($('#lang-toggle')) $('#lang-toggle').onclick = () => "
                          "setLang(html.getAttribute('dir') === 'rtl' ? 'en' : 'ar');\n"
                          "renderRows(); lucide.createIcons(); mountCharts();", 1)
    return s, spec


# ---------------------------------------------------------------- landing ----
# What the shipped landing shell says today, per region -- the wording a built page must never keep.
SHELL_LANDING = {
    "site-header": ["Mishwar"],
    "hero": ["Tomorrow's routes, planned before the depot opens.", "Beirut depot"],
    "customer-logos": ["Planning with Mishwar today"],
    "capabilities": ["The plan starts from the order list you already keep", "orders-2025-10-11.csv",
                     "A window you promised is a constraint, not a note", "The driver gets a sequence, not a map puzzle",
                     "Every change is on the record"],
    "testimonial": ["Dispatch supervisor, Barakat Dairy"],
    "pricing-teaser": ["Priced per active van, not per seat"],
    "faq": ["Asked by every dispatcher we meet", "Do we have to replace our ERP?"],
    "closing-cta": ["Plan one depot tomorrow morning."],
    "site-footer": ["Route planning for wholesale delivery fleets."],
}
# The six marks the shell draws beside its customer names: geometry only, no brand in any of them.
LOGO_MARKS = [
    '<circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="8" cy="8" r="1.8" fill="currentColor"/>',
    '<path d="M2 11c2-4 4-6 6-6s4 2 6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M2 14h12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    '<path d="M8 2 14 5.5v5L8 14 2 10.5v-5z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>',
    '<rect x="2.5" y="2.5" width="11" height="11" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M5.5 8h5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
    '<path d="M3 13V6l5-3 5 3v7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M6.5 13V9.5h3V13" fill="none" stroke="currentColor" stroke-width="1.6"/>',
    '<path d="M2.5 12.5 6 4l2 5 2-5 3.5 8.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>',
]
STAT_COLS = {1: "", 2: "sm:grid-cols-2", 3: "sm:grid-cols-3", 4: "sm:grid-cols-2 lg:grid-cols-4"}

def derive_landing(spec):
    """What the chrome says, taken from what the spec already says elsewhere.

    The app screen swaps the shell's demo nouns after the build; a landing page has no demo copy left
    to swap, because every region is rebuilt whole, so the same idea runs before the build instead.
    Nothing here asks the spec for anything new: the top nav is the sections' own names, the header's
    action is the hero's, and the line under the footer brand is the page description.
    """
    d = dict(spec)
    d["nav"] = spec.get("nav") or [{"label": x["step"], "href": "#" + slug(x["step"])} for x in (spec.get("sections") or []) if x.get("step")][:5]
    acts = dict(spec.get("actions") or {})
    if not acts.get("primary"): acts["primary"] = (spec.get("hero") or {}).get("primary", "")
    d["actions"] = acts
    h = spec.get("hero") or {}
    # a page with no description of its own still gets one; the demo's must not reach a search result
    d["description"] = spec.get("description") or h.get("lead") or h.get("headline", "")
    foot = dict(spec.get("footer") or {})
    foot.setdefault("tagline", spec.get("description", ""))
    foot.setdefault("legal", "© 2026 " + str(spec.get("product", "")))
    d["footer"] = foot
    return d

def nav_links(items, cls):
    return "".join(f'<a class="{cls}" href="{esc(it.get("href", "#"))}" data-i18n="{esc(it.get("label"))}">{esc(it.get("label"))}</a>'
                   for it in items if it.get("label"))

def brand_mark(spec, size="size-7"):
    """A lucide mark when the spec names one, the product's own initial when it does not."""
    icon = spec.get("icon")
    inner = f'<i data-lucide="{esc(icon)}" class="size-4"></i>' if icon else f'<span class="text-xs font-bold">{esc(str(spec.get("product", "?"))[:1])}</span>'
    return f'<span class="inline-flex {size} items-center justify-center rounded-md bg-primary text-primary-foreground">{inner}</span>'

def ticks(items, gap="gap-3"):
    rows = "".join(f'\n        <li class="tick"><i data-lucide="check"></i>{i18n(t)}</li>' for t in items)
    return f'<ul class="flex flex-col {gap}">{rows}\n      </ul>'

def panel_row(r):
    """One row of a panel: a name, a second line, a share bar and a status word, in that order.

    That is every list the shell draws by hand -- a van's schedule, a column mapping, a day log --
    so a section describes its own picture with four fields instead of forty lines of markup.
    """
    out = f'<span class="flex min-w-20 items-center gap-2 font-mono text-2sm text-mono">{esc(r.get("label", ""))}</span>' if r.get("label") else ""
    if r.get("meta"): out += f'<span class="meta tabular-nums leading-relaxed" data-i18n="{esc(r["meta"])}">{esc(r["meta"])}</span>'
    bar = ""
    if r.get("bar") is not None:
        n = max(0, min(100, int(r["bar"])))
        bar = ('<span class="ms-auto flex items-center gap-2"><span class="block h-1.5 w-16 overflow-hidden rounded-full bg-muted">'
               f'<span class="block h-full bg-primary" style="inline-size:{n}%"></span></span>'
               f'<span class="meta w-8 text-end tabular-nums">{n}%</span></span>')
    status = ""
    if r.get("status"):
        cls = TONES.get(r.get("tone"), "badge-outline") + ("" if bar else " ms-auto")
        status = f'<span class="badge badge-sm {cls}"><span class="dot"></span>{i18n(r["status"])}</span>'
    return f'\n          <div class="flex flex-wrap items-center gap-x-4 gap-y-2 px-5 py-3.5">{out}{bar}{status}</div>'

def build_panel(p):
    """The card beside a section's prose. A section that describes no panel simply has none."""
    if not p: return ""
    head = ""
    if p.get("title") or p.get("badge"):
        title = f'<span class="card-title" data-i18n="{esc(p["title"])}">{esc(p["title"])}</span>' if p.get("title") else ""
        meta = f'<span class="meta" data-i18n="{esc(p["meta"])}">{esc(p["meta"])}</span>' if p.get("meta") else ""
        badge = f'<span class="badge badge-sm {TONES.get(p.get("tone"), "badge-outline")}"><span class="dot"></span>{i18n(p["badge"])}</span>' if p.get("badge") else ""
        head = f'\n        <div class="card-header">\n          <span class="flex flex-col gap-0.5 min-w-0">{title}{meta}</span>{badge}\n        </div>'
    rows = "".join(panel_row(r) for r in p.get("rows") or [])
    if rows: rows = f'\n        <div class="divide-y divide-border">{rows}\n        </div>'
    tk = ""
    if p.get("ticks"):
        tk = '\n        <div class="card-content flex flex-col gap-4">' + "".join(f'\n          <span class="tick"><i data-lucide="check"></i>{i18n(t)}</span>' for t in p["ticks"]) + '\n        </div>'
    note = f'\n        <div class="card-footer bg-muted/40"><span class="meta leading-relaxed" data-i18n="{esc(p["note"])}">{esc(p["note"])}</span></div>' if p.get("note") else ""
    return f'<div class="card overflow-hidden">{head}{rows}{tk}{note}\n      </div>'

def build_site_header(spec):
    acts = spec.get("actions") or {}
    sign = f'\n      <a class="btn btn-ghost btn-sm hidden sm:inline-flex" href="#" data-i18n="{esc(acts["sign_in"])}">{esc(acts["sign_in"])}</a>' if acts.get("sign_in") else ""
    cta = f'\n      <a class="btn btn-primary btn-sm ms-1" href="{"#start" if spec.get("cta") else "#"}" data-i18n="{esc(acts["primary"])}">{esc(acts["primary"])}</a>' if acts.get("primary") else ""
    return f'''<header class="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur-sm">
  <div class="container-fixed flex h-16 items-center justify-between gap-4">
    <a href="#hero" class="flex items-center gap-2.5 font-display text-base font-semibold text-mono">
      {brand_mark(spec)}
      {esc(spec.get("product", ""))}
    </a>
    <nav class="flex items-center gap-1" aria-label="Main">
      <span class="hidden md:flex items-center gap-0.5 me-2">{nav_links(spec.get("nav") or [], "top-link")}</span>
      <button id="lang-toggle" class="btn btn-ghost btn-icon btn-sm" aria-label="Switch language" title="English / العربية"><i data-lucide="languages"></i></button>
      <button id="theme-toggle" class="btn btn-ghost btn-icon btn-sm" aria-label="Toggle dark mode"><i data-lucide="moon" class="dark:hidden"></i><i data-lucide="sun" class="hidden dark:block"></i></button>{sign}{cta}
      <button id="menu-btn" class="btn btn-ghost btn-icon btn-sm md:hidden" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-nav"><i data-lucide="menu"></i></button>
    </nav>
  </div>
  <nav id="mobile-nav" class="hidden md:hidden border-t border-border bg-background" aria-label="Mobile">
    <div class="container-fixed flex flex-col py-2">{nav_links(spec.get("nav") or [], "top-link py-2.5")}</div>
  </nav>
</header>'''

def build_hero(spec):
    h = spec.get("hero") or {}
    if not h: return None
    first = ([x for x in (spec.get("sections") or []) if x.get("step")] or [{}])[0].get("step")
    eyebrow = f'<span class="eyebrow"><i data-lucide="{esc(spec.get("icon", "circle"))}" class="size-3.5"></i>{i18n(h["eyebrow"])}</span>\n      ' if h.get("eyebrow") else ""
    head = esc(h.get("headline", ""))
    lead = f'<p class="lead max-w-xl" data-i18n="{esc(h["lead"])}">{esc(h["lead"])}</p>\n      ' if h.get("lead") else ""
    btns = ""
    if h.get("primary"):
        btns += f'<a class="btn btn-primary btn-lg" href="{"#start" if spec.get("cta") else "#"}">{i18n(h["primary"])}<i data-lucide="arrow-right" class="rtl:rotate-180"></i></a>'
    if h.get("secondary"):
        btns += f'\n        <a class="btn btn-outline btn-lg" href="#{slug(first) if first else ""}"><i data-lucide="play" class="rtl:-scale-x-100"></i>{i18n(h["secondary"])}</a>'
    if btns: btns = f'<div class="flex flex-wrap items-center gap-3">\n        {btns}\n      </div>\n      '
    note = f'<p class="meta max-w-md leading-relaxed" data-i18n="{esc(h["note"])}">{esc(h["note"])}</p>\n      ' if h.get("note") else ""
    panel = build_panel(h.get("panel"))
    grid = "grid gap-12 lg:grid-cols-[1.05fr_1fr] lg:items-center lg:gap-16" if panel else "max-w-3xl"
    return f'''<section id="hero" class="section border-b border-border">
  <div class="container-fixed {grid}">
    <div class="flex flex-col items-start gap-6">
      {eyebrow}<h1 class="font-display text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight leading-[1.05] text-mono text-balance" data-i18n="{head}">{head}</h1>
      {lead}{btns}{note}</div>
    {panel}
  </div>
</section>'''

def build_logos(lg):
    if not lg or not lg.get("names"): return None
    items = "".join(f'''\n      <li class="flex items-center justify-center gap-2 text-secondary-foreground">
        <svg viewBox="0 0 16 16" class="size-4 shrink-0" aria-hidden="true">{LOGO_MARKS[i % len(LOGO_MARKS)]}</svg>
        <span class="font-display text-sm font-semibold">{esc(n)}</span>
      </li>''' for i, n in enumerate(lg["names"]))
    cap = f'\n    <p class="meta text-center" data-i18n="{esc(lg["caption"])}">{esc(lg["caption"])}</p>' if lg.get("caption") else ""
    note = f'\n    <p class="meta text-center leading-relaxed" data-i18n="{esc(lg["note"])}">{esc(lg["note"])}</p>' if lg.get("note") else ""
    cols = "sm:grid-cols-3 lg:grid-cols-6" if len(lg["names"]) > 4 else "sm:grid-cols-4"
    return f'''<section id="customers" class="border-b border-border bg-muted/40 py-10 lg:py-12">
  <div class="container-fixed flex flex-col gap-7">{cap}
    <ul class="grid grid-cols-2 items-center gap-x-6 gap-y-6 {cols}">{items}
    </ul>{note}
  </div>
</section>'''

def build_sections(items):
    """The shell's four capability regions are one shape repeated, so the spec fills them as a list.

    Every second section takes the muted surface and puts its prose after the panel, which is what
    stops four identical sections reading as a template.
    """
    if not items: return None
    out = []
    for i, sec in enumerate(items):
        odd = i % 2 == 1
        step = f'<span class="step">{i + 1:02d} · {i18n(sec["step"])}</span>\n      ' if sec.get("step") else ""
        title = f'<h2 class="h2" data-i18n="{esc(sec["title"])}">{esc(sec["title"])}</h2>\n      ' if sec.get("title") else ""
        lead = f'<p class="lead" data-i18n="{esc(sec["lead"])}">{esc(sec["lead"])}</p>\n      ' if sec.get("lead") else ""
        tk = ticks(sec.get("ticks") or []) + "\n      " if sec.get("ticks") else ""
        link = sec.get("link")
        if isinstance(link, str): link = {"label": link}
        ln = (f'<a class="link text-2sm font-medium inline-flex items-center gap-1.5" href="{esc((link or {}).get("href", "#faq"))}">'
              f'{i18n(link["label"])}<i data-lucide="arrow-right" class="size-4 rtl:rotate-180"></i></a>\n      ') if link and link.get("label") else ""
        panel = build_panel(sec.get("panel"))
        prose = f'''<div class="flex flex-col items-start gap-5{" lg:order-last" if odd else ""}">
      {step}{title}{lead}{tk}{ln}</div>'''
        body = (f'<div class="grid gap-10 lg:grid-cols-2 lg:items-center lg:gap-16">\n      {prose}\n\n      {panel}\n    </div>'
                if panel else f'<div class="max-w-3xl">\n      {prose}\n    </div>')
        stats = ""
        if sec.get("stats"):
            cells = "".join(f'''\n      <div class="flex flex-col gap-1.5">
        <span class="font-display text-3xl font-semibold text-mono tabular-nums">{esc(st.get("value", ""))}</span>
        <span class="text-2sm text-secondary-foreground" data-i18n="{esc(st.get("label", ""))}">{esc(st.get("label", ""))}</span>
      </div>''' for st in sec["stats"])
            stats = f'\n    <div class="grid gap-8 border-t border-border pt-10 {STAT_COLS.get(len(sec["stats"]), "sm:grid-cols-3")}">{cells}\n    </div>'
        out.append(f'''<section id="{slug(sec.get("step") or sec.get("title") or i)}" class="section border-b border-border{" bg-muted/40" if odd else ""}">
  <div class="container-fixed flex flex-col gap-12">
    {body}{stats}
  </div>
</section>''')
    return "\n\n".join(out)

def build_testimonial(t):
    if not t or not t.get("quote"): return None
    who = f'<span class="text-sm font-medium text-mono">{esc(t["name"])}</span>' if t.get("name") else ""
    role = f'<span class="text-2sm text-secondary-foreground" data-i18n="{esc(t["role"])}">{esc(t["role"])}</span>' if t.get("role") else ""
    badge = f'\n      <span class="badge badge-sm badge-outline ms-auto" data-i18n="{esc(t["badge"])}">{esc(t["badge"])}</span>' if t.get("badge") else ""
    return f'''<section class="section border-b border-border">
  <figure class="container-fixed flex max-w-3xl flex-col gap-7">
    <i data-lucide="quote" class="size-7 text-primary-accent"></i>
    <blockquote class="font-display text-2xl lg:text-3xl font-medium leading-snug text-mono text-balance" data-i18n="{esc(t["quote"])}">{esc(t["quote"])}</blockquote>
    <figcaption class="flex flex-wrap items-center gap-x-4 gap-y-2">
      <span class="inline-flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 font-semibold text-2xs text-primary-accent">{esc(initials(t.get("name", "")))}</span>
      <span class="flex flex-col gap-0.5 min-w-0">{who}{role}</span>{badge}
    </figcaption>
  </figure>
</section>'''

def build_pricing_teaser(p):
    if not p or not p.get("price"): return None
    eyebrow = f'<span class="eyebrow"><i data-lucide="wallet" class="size-3.5"></i>{i18n(p["eyebrow"])}</span>\n        ' if p.get("eyebrow") else ""
    title = f'<h2 class="h2 text-2xl lg:text-3xl" data-i18n="{esc(p["title"])}">{esc(p["title"])}</h2>\n        ' if p.get("title") else ""
    lead = f'<p class="lead text-base max-w-xl" data-i18n="{esc(p["lead"])}">{esc(p["lead"])}</p>' if p.get("lead") else ""
    note = f'\n          <span class="meta pb-2 leading-tight" data-i18n="{esc(p["price_note"])}">{esc(p["price_note"])}</span>' if p.get("price_note") else ""
    tk = "\n        " + ticks(p["ticks"], gap="gap-2.5") if p.get("ticks") else ""
    cta = f'\n        <a class="btn btn-outline" href="#faq">{i18n(p["cta"])}<i data-lucide="arrow-right" class="rtl:rotate-180"></i></a>' if p.get("cta") else ""
    return f'''<section id="pricing" class="section border-b border-border bg-muted/40">
  <div class="container-fixed">
    <div class="card flex-col lg:flex-row lg:items-stretch">
      <div class="card-content flex flex-col items-start gap-4">
        {eyebrow}{title}{lead}
      </div>
      <div class="flex shrink-0 flex-col gap-5 border-t border-border p-(--card-p) lg:w-80 lg:border-t-0 lg:border-s">
        <div class="flex items-end gap-2">
          <span class="font-display text-5xl font-semibold text-mono tabular-nums" dir="ltr">{esc(p["price"])}</span>{note}
        </div>{tk}{cta}
      </div>
    </div>
  </div>
</section>'''

def build_landing_faq(f):
    if not f or not f.get("items"): return None
    eyebrow = f'<span class="eyebrow"><i data-lucide="message-circle" class="size-3.5"></i>{i18n(f["eyebrow"])}</span>\n      ' if f.get("eyebrow") else ""
    title = f'<h2 class="h2" data-i18n="{esc(f["title"])}">{esc(f["title"])}</h2>\n      ' if f.get("title") else ""
    note = f'<p class="text-2sm leading-relaxed text-secondary-foreground" data-i18n="{esc(f["note"])}">{esc(f["note"])}</p>' if f.get("note") else ""
    items = "".join(f'''
      <details name="faq" class="disclosure group rounded-lg border border-border bg-card px-5 shadow-xs" data-motion="state"{" open" if i == 0 else ""}>
        <summary class="flex cursor-pointer list-none items-center justify-between gap-4 py-4 text-sm font-medium text-mono [&::-webkit-details-marker]:hidden">
          {i18n(it.get("q", ""))}
          <i data-lucide="chevron-down" class="faq-chevron size-4 shrink-0 text-muted-foreground"></i>
        </summary>
        <p class="pb-5 text-2sm leading-relaxed text-secondary-foreground" data-i18n="{esc(it.get("a", ""))}">{esc(it.get("a", ""))}</p>
      </details>''' for i, it in enumerate(f["items"]))
    return f'''<section id="faq" class="section border-b border-border">
  <div class="container-fixed grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:gap-16">
    <div class="flex flex-col items-start gap-4">
      {eyebrow}{title}{note}
    </div>
    <div class="flex flex-col gap-3">{items}
    </div>
  </div>
</section>'''

def build_closing_cta(c):
    if not c or not c.get("title"): return None
    lead = f'\n        <p class="text-2sm leading-relaxed text-secondary-foreground max-w-xl" data-i18n="{esc(c["lead"])}">{esc(c["lead"])}</p>' if c.get("lead") else ""
    note = f'\n        <p class="meta leading-relaxed" data-i18n="{esc(c["note"])}">{esc(c["note"])}</p>' if c.get("note") else ""
    btns = ""
    if c.get("primary"): btns += f'<a class="btn btn-primary btn-lg" href="#">{i18n(c["primary"])}<i data-lucide="arrow-right" class="rtl:rotate-180"></i></a>'
    if c.get("secondary"): btns += f'\n        <a class="btn btn-outline btn-lg" href="#"><i data-lucide="calendar"></i>{i18n(c["secondary"])}</a>'
    return f'''<section id="start" class="section">
  <div class="container-fixed">
    <div class="card gap-6 p-(--card-p) lg:flex-row lg:items-center lg:justify-between lg:gap-10">
      <div class="flex flex-col gap-3">
        <h2 class="h2 text-2xl lg:text-3xl" data-i18n="{esc(c["title"])}">{esc(c["title"])}</h2>{lead}{note}
      </div>
      <div class="flex shrink-0 flex-wrap items-center gap-3">
        {btns}
      </div>
    </div>
  </div>
</section>'''

def build_site_footer(spec):
    f = spec.get("footer") or {}
    tag = f'\n        <p class="text-2sm leading-relaxed text-secondary-foreground" data-i18n="{esc(f["tagline"])}">{esc(f["tagline"])}</p>' if f.get("tagline") else ""
    cols = "".join(f'''
      <nav class="flex flex-col gap-2.5" aria-label="{esc(c.get("heading", "More"))}">
        <span class="text-xs font-medium text-mono" data-i18n="{esc(c.get("heading", ""))}">{esc(c.get("heading", ""))}</span>
        {nav_links([l if isinstance(l, dict) else {"label": l} for l in c.get("links") or []], "foot-link")}
      </nav>''' for c in f.get("columns") or [])
    contact = f'\n      <p class="meta">{esc(f["contact"])}</p>' if f.get("contact") else ""
    wide = {0: "lg:grid-cols-1", 1: "lg:grid-cols-2", 2: "lg:grid-cols-3", 3: "lg:grid-cols-4"}.get(len(f.get("columns") or []), "lg:grid-cols-5")
    return f'''<footer class="border-t border-border bg-muted/40 py-12 lg:py-16">
  <div class="container-fixed flex flex-col gap-10">
    <div class="grid gap-8 sm:grid-cols-2 {wide}">
      <div class="flex flex-col gap-3 lg:pe-8">
        <span class="flex items-center gap-2.5 font-display text-base font-semibold text-mono">
          {brand_mark(spec)}
          {esc(spec.get("product", ""))}
        </span>{tag}
      </div>{cols}
    </div>
    <div class="flex flex-col gap-3 border-t border-border pt-6 sm:flex-row sm:items-center sm:justify-between">
      <p class="meta">{esc(f.get("legal", ""))}</p>{contact}
    </div>
  </div>
</footer>'''

def build_landing(spec, s):
    spec = derive_landing(spec)
    s = set_head(s, spec, theme="theme-graphite", density="density-airy")
    s = region(s, "site-header", build_site_header(spec))
    s = region(s, "hero", build_hero(spec))
    s = region(s, "customer-logos", build_logos(spec.get("logos")))
    s = region(s, "capability-import", build_sections(spec.get("sections")), through="capability-record")
    s = region(s, "testimonial", build_testimonial(spec.get("testimonial")))
    s = region(s, "pricing-teaser", build_pricing_teaser(spec.get("pricing")))
    s = region(s, "faq", build_landing_faq(spec.get("faq")))
    s = region(s, "closing-cta", build_closing_cta(spec.get("cta")))
    s = region(s, "site-footer", build_site_footer(spec))
    s = apply_i18n(s, spec)
    return strip_demo_controls(s, spec), spec

def panel_fields(prefix, p):
    """The spec fields a panel puts on the page, for applied_check."""
    want = []
    if not p: return want
    for key in ("title", "meta", "badge", "note"):
        if p.get(key): want.append((f"{prefix}.{key}", p[key]))
    for i, r in enumerate(p.get("rows") or []):
        for key in ("label", "meta", "status"):
            if r.get(key): want.append((f"{prefix}.rows[{i}].{key}", r[key]))
    for i, t in enumerate(p.get("ticks") or []):
        want.append((f"{prefix}.ticks[{i}]", t))
    return want

def applied_check_landing(spec, out_html):
    """Every label the spec asked for must be in the page. A miss means an anchor went stale."""
    want = []
    for key in ("product", "description"):
        if spec.get(key): want.append((key, spec[key]))
    for i, n in enumerate(spec.get("nav") or []):
        if n.get("label"): want.append((f"nav[{i}].label", n["label"]))
    for key, v in (spec.get("actions") or {}).items():
        if v: want.append((f"actions.{key}", v))
    h = spec.get("hero") or {}
    for key in ("eyebrow", "headline", "lead", "primary", "secondary", "note"):
        if h.get(key): want.append((f"hero.{key}", h[key]))
    want += panel_fields("hero.panel", h.get("panel"))
    lg = spec.get("logos") or {}
    for key in ("caption", "note"):
        if lg.get(key): want.append((f"logos.{key}", lg[key]))
    for i, n in enumerate(lg.get("names") or []): want.append((f"logos.names[{i}]", n))
    for i, sec in enumerate(spec.get("sections") or []):
        for key in ("step", "title", "lead"):
            if sec.get(key): want.append((f"sections[{i}].{key}", sec[key]))
        for j, t in enumerate(sec.get("ticks") or []): want.append((f"sections[{i}].ticks[{j}]", t))
        link = sec.get("link")
        if link: want.append((f"sections[{i}].link", link if isinstance(link, str) else link.get("label", "")))
        for j, st in enumerate(sec.get("stats") or []):
            for key in ("value", "label"):
                if st.get(key): want.append((f"sections[{i}].stats[{j}].{key}", st[key]))
        want += panel_fields(f"sections[{i}].panel", sec.get("panel"))
    t = spec.get("testimonial") or {}
    for key in ("quote", "name", "role", "badge"):
        if t.get(key): want.append((f"testimonial.{key}", t[key]))
    p = spec.get("pricing") or {}
    for key in ("eyebrow", "title", "lead", "price", "price_note", "cta"):
        if p.get(key): want.append((f"pricing.{key}", p[key]))
    for i, x in enumerate(p.get("ticks") or []): want.append((f"pricing.ticks[{i}]", x))
    f = spec.get("faq") or {}
    for key in ("eyebrow", "title", "note"):
        if f.get(key): want.append((f"faq.{key}", f[key]))
    for i, it in enumerate(f.get("items") or []):
        for key in ("q", "a"):
            if it.get(key): want.append((f"faq.items[{i}].{key}", it[key]))
    c = spec.get("cta") or {}
    for key in ("title", "lead", "note", "primary", "secondary"):
        if c.get(key): want.append((f"cta.{key}", c[key]))
    fo = spec.get("footer") or {}
    for key in ("tagline", "legal", "contact"):
        if fo.get(key): want.append((f"footer.{key}", fo[key]))
    for i, col in enumerate(fo.get("columns") or []):
        if col.get("heading"): want.append((f"footer.columns[{i}].heading", col["heading"]))
        for j, l in enumerate(col.get("links") or []):
            want.append((f"footer.columns[{i}].links[{j}]", l if isinstance(l, str) else l.get("label", "")))
    return [(field, value) for field, value in want if not present(value, out_html)]


# ---------------------------------------------------------------- pricing ----
# What the shipped pricing shell says today, per region -- the wording a built page must never keep.
SHELL_PRICING = {
    "header": ["Sijil"],
    "pricing-intro": ["Pricing that follows your order volume", "Every plan carries the whole order pipeline."],
    "plans": ["For one shop and a team that fits around one table.", "1,500 orders a month",
              "Prices in US dollars per workspace."],
    "comparison": ["The table scrolls inside its own frame.", "Orders and stores"],
    "faq": ["What counts as an order?"],
    "closing-cta": ["Start on the plan you need this month"],
}
PLAN_COLS = {1: "max-w-sm mx-auto", 2: "md:grid-cols-2", 3: "md:grid-cols-3", 4: "sm:grid-cols-2 xl:grid-cols-4"}

def derive_pricing(spec):
    """What a plan's button says, and what the comparison table's columns are.

    Both are already in the spec once: the button is the page's own call to action, and the columns
    are the plans. Asking for them twice is a spec that can disagree with itself.
    """
    d = dict(spec)
    cta = (spec.get("cta") or {}).get("primary", "")
    plans = [dict(p) for p in spec.get("plans") or []]
    for p in plans:
        if not p.get("cta") and cta: p["cta"] = cta
    d["plans"] = plans
    cmp_ = dict(spec.get("comparison") or {})
    if cmp_ and not cmp_.get("caption"): cmp_["caption"] = cmp_.get("lead") or cmp_.get("title", "")
    d["comparison"] = cmp_
    foot = dict(spec.get("footer") or {})
    foot.setdefault("legal", "© 2026 " + str(spec.get("product", "")))
    d["footer"] = foot
    return d

def yearly(spec):
    """The billing toggle exists only when a plan has a second price to show."""
    return [p for p in spec.get("plans") or [] if p.get("price_yearly")]

def pricing_nav(items, indent, active, idle):
    """The same links twice: the wide strip and the drawer under it, which the shell keeps in step."""
    out = ""
    for n in items:
        if not n.get("label"): continue
        current = ' aria-current="page"' if n.get("active") else ""
        out += f'{indent}<a href="{esc(n.get("href", "#"))}"{current} class="rounded-md {active if n.get("active") else idle}">{i18n(n["label"])}</a>'
    return out

def build_pricing_header(spec):
    acts = spec.get("actions") or {}
    nav = spec.get("nav") or []
    wide = pricing_nav(nav, "\n      ", "bg-accent px-2.5 py-1.5 text-2sm font-medium text-mono",
                       "px-2.5 py-1.5 text-2sm text-secondary-foreground hover:bg-accent hover:text-mono")
    small = pricing_nav(nav, "\n    ", "bg-accent px-2.5 py-2 text-2sm font-medium text-mono",
                        "px-2.5 py-2 text-2sm text-secondary-foreground hover:bg-accent")
    sign = f'\n      <a href="#" class="btn btn-outline hidden sm:inline-flex">{i18n(acts["sign_in"])}</a>' if acts.get("sign_in") else ""
    sign_small = f'\n    <a href="#" class="rounded-md px-2.5 py-2 text-2sm text-secondary-foreground hover:bg-accent sm:hidden">{i18n(acts["sign_in"])}</a>' if acts.get("sign_in") else ""
    return f'''<header class="sticky top-0 z-40 border-b border-border bg-background">
  <div class="container-fixed flex h-(--header-height) items-center justify-between gap-4">
    <a href="#" class="flex shrink-0 items-center gap-2.5 font-semibold text-mono">
      {brand_mark(spec)}
      <span class="font-display">{esc(spec.get("product", ""))}</span>
    </a>
    <nav class="hidden items-center gap-0.5 md:flex" aria-label="Main">{wide}
    </nav>
    <div class="flex items-center gap-1.5">
      <button id="lang-toggle" class="btn btn-ghost btn-icon" aria-label="Switch language" title="English / العربية"><i data-lucide="languages"></i></button>
      <button id="theme-toggle" class="btn btn-ghost btn-icon" aria-label="Toggle dark mode"><i data-lucide="moon" class="dark:hidden"></i><i data-lucide="sun" class="hidden dark:block"></i></button>{sign}
      <button id="nav-toggle" class="btn btn-ghost btn-icon md:hidden" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-nav"><i data-lucide="menu"></i></button>
    </div>
  </div>
  <nav id="mobile-nav" hidden aria-label="Main, small screens" class="container-fixed flex flex-col gap-0.5 border-t border-border py-2 md:hidden">{small}{sign_small}
  </nav>
</header>'''

def build_pricing_intro(spec):
    it = spec.get("intro") or {}
    if not it: return None
    title = esc(it.get("title", ""))
    lead = f'\n    <p class="max-w-xl text-sm text-secondary-foreground">{i18n(it["lead"])}</p>' if it.get("lead") else ""
    toggle = ""
    if yearly(spec):
        save = f'<span class="badge badge-sm bg-primary text-primary-foreground">{i18n(it["save"])}</span>' if it.get("save") else ""
        notes = ""
        for when in ("monthly", "yearly"):
            n = it.get(when + "_note")
            if n: notes += f'\n        <span data-when="{when}"{" hidden" if when == "yearly" else ""}>{i18n(n)}</span>'
        notes = f'\n      <p class="min-h-4 text-xs text-muted-foreground" aria-live="polite">{notes}\n      </p>' if notes else ""
        toggle = f'''
    <fieldset class="mt-2 flex flex-col items-center gap-2.5">
      <legend class="sr-only" data-i18n="Billing period">Billing period</legend>
      <div class="inline-flex items-center gap-1 rounded-lg border border-border bg-muted p-1">
        <label class="inline-flex"><input type="radio" name="billing" value="monthly" class="seg-input sr-only" checked><span class="seg">{i18n(it.get("monthly", "Monthly"))}</span></label>
        <label class="inline-flex"><input type="radio" name="billing" value="yearly" class="seg-input sr-only"><span class="seg">{i18n(it.get("yearly", "Yearly"))}{save}</span></label>
      </div>{notes}
    </fieldset>'''
    return f'''<section class="container-fixed flex flex-col items-center gap-4 pt-10 pb-7.5 text-center md:pt-14">
    <h1 class="max-w-2xl font-display text-3xl font-medium text-mono md:text-4xl"><span data-i18n="{title}">{title}</span></h1>{lead}{toggle}
  </section>'''

def build_plans(spec):
    plans = spec.get("plans") or []
    if not plans: return None
    it = spec.get("intro") or {}
    cards = []
    for p in plans:
        badge = f'\n        <span class="badge badge-sm absolute -top-2.5 start-1/2 -translate-x-1/2 bg-primary text-primary-foreground rtl:translate-x-1/2">{i18n(p["badge"])}</span>' if p.get("badge") else ""
        blurb = f'\n            <p class="min-h-9 text-2sm text-secondary-foreground">{i18n(p["blurb"])}</p>' if p.get("blurb") else ""
        price = esc(p.get("price", ""))
        billed = ""
        for when, key in (("monthly", "billed_monthly"), ("yearly", "billed_yearly")):
            text = p.get(key) or it.get(key)
            if not text or (when == "yearly" and not p.get("price_yearly")): continue
            total = f', <span dir="ltr" class="tabular-nums">{esc(p["yearly_total"])}</span>' if when == "yearly" and p.get("yearly_total") else ""
            billed += f'\n              <span data-when="{when}"{" hidden" if when == "yearly" else ""}>{i18n(text)}{total}</span>'
        billed = f'\n            <p class="mt-1.5 text-xs text-muted-foreground">{billed}\n            </p>' if billed else ""
        feats = "".join(f'\n            <li class="plan-feature"><i data-lucide="check"></i>{i18n(x)}</li>' for x in p.get("features") or [])
        if p.get("inherits"): feats = f'\n            <li class="text-xs font-medium text-mono">{i18n(p["inherits"])}</li>' + feats
        cta = f'\n          <a href="#cta" class="btn btn-outline w-full{" border-primary text-primary-accent hover:bg-primary/10" if p.get("featured") else ""}">{i18n(p["cta"])}</a>' if p.get("cta") else ""
        cards.append(f'''      <article class="plan{" plan-featured md:-mt-4 md:mb-4" if p.get("featured") else ""}">{badge}
        <div class="flex grow flex-col gap-5 p-(--card-p)">
          <div class="flex flex-col gap-1">
            <h3 class="text-base font-semibold tracking-tight text-mono">{i18n(p.get("name", ""))}</h3>{blurb}
          </div>
          <div>
            <div class="flex items-baseline gap-1.5">
              <span dir="ltr" class="font-display text-4xl font-semibold tabular-nums text-mono" data-price data-m="{price}" data-y="{esc(p.get("price_yearly", p.get("price", "")))}">{price}</span>
              <span class="text-2sm text-muted-foreground">{i18n(p.get("period") or it.get("period", "per month"))}</span>
            </div>{billed}
          </div>{cta}
          <ul class="flex grow flex-col gap-2.5 border-t border-border pt-5">{feats}
          </ul>
        </div>
      </article>''')
    note = f'\n    <p class="pt-5 text-center text-xs text-muted-foreground">{i18n(spec["note"])}</p>' if spec.get("note") else ""
    return f'''<section class="container-fixed pb-12" aria-labelledby="plans-heading">
    <h2 id="plans-heading" class="sr-only" data-i18n="Plans">Plans</h2>
    <div class="grid items-stretch gap-5 {PLAN_COLS.get(len(plans), "md:grid-cols-3")} lg:gap-7.5">

''' + "\n\n".join(cards) + f'''

    </div>{note}
  </section>'''

def cmp_cell(v):
    """A cell is a word, a number, or the plain fact that a plan has the feature or has not."""
    if v is True: return '<td><i data-lucide="check" class="mx-auto block size-4 text-primary-accent"></i><span class="sr-only" data-i18n="Included">Included</span></td>'
    if v is False or v is None: return '<td><i data-lucide="minus" class="mx-auto block size-4 text-muted-foreground"></i><span class="sr-only" data-i18n="Not included">Not included</span></td>'
    if re.fullmatch(r"[\d.,%\s]+", str(v)): return f'<td dir="ltr" class="tabular-nums">{esc(v)}</td>'
    return f'<td>{i18n(v)}</td>'

def build_comparison(spec):
    c = spec.get("comparison") or {}
    plans = spec.get("plans") or []
    if not c.get("groups") or not plans: return None
    heads = ""
    for p in plans:
        rec = f'\n                <span class="mt-1 block text-2xs text-primary-accent">{i18n(p["badge"])}</span>' if p.get("badge") else ""
        heads += f'''
              <th scope="col" class="h-auto py-3.5 text-center">
                <span class="block text-2sm font-medium text-mono" data-i18n="{esc(p.get("name", ""))}">{esc(p.get("name", ""))}</span>
                <span dir="ltr" class="mt-1 block text-xs tabular-nums text-muted-foreground" data-price data-m="{esc(p.get("price", ""))}" data-y="{esc(p.get("price_yearly", p.get("price", "")))}">{esc(p.get("price", ""))}</span>{rec}
              </th>'''
    bodies = ""
    for g in c["groups"]:
        rows = f'\n            <tr class="group-row"><th scope="colgroup" colspan="{len(plans) + 1}">{i18n(g.get("heading", ""))}</th></tr>'
        for r in g.get("rows") or []:
            # one cell per plan, whatever the spec supplied: a row that is short reads as "not
            # included" rather than as a table with a hole in it, and a row that is long is caught
            # by applied_check, which looks at every cell the spec wrote.
            row = (r.get("cells") or []) + [None] * len(plans)
            cells = "".join(cmp_cell(v) for v in row[:len(plans)])
            rows += f'\n            <tr><th scope="row">{i18n(r.get("label", ""))}</th>{cells}</tr>'
        bodies += f'\n          <tbody>{rows}\n          </tbody>'
    lead = f'\n      <p class="text-2sm text-secondary-foreground">{i18n(c["lead"])}</p>' if c.get("lead") else ""
    return f'''<section class="container-fixed pb-12" aria-labelledby="compare-heading">
    <div class="flex flex-col gap-1 pb-5">
      <h2 id="compare-heading" class="font-display text-xl font-medium text-mono">{i18n(c.get("title", ""))}</h2>{lead}
    </div>
    <div class="card overflow-hidden">
      <div class="relative max-h-[32rem] overflow-auto scroll-thin">
        <table class="table cmp min-w-[46rem]">
          <caption class="sr-only" data-i18n="{esc(c.get("caption", ""))}">{esc(c.get("caption", ""))}</caption>
          <thead>
            <tr>
              <th scope="col" class="h-auto min-w-[15rem] py-3.5">{i18n(c.get("feature_column", "Feature"))}</th>{heads}
            </tr>
          </thead>{bodies}
        </table>
      </div>
    </div>
  </section>'''

def build_pricing_faq(f):
    if not f or not f.get("items"): return None
    items = "".join(f'''
      <details class="faq disclosure px-5" data-motion="state">
        <summary>{i18n(it.get("q", ""))}<i data-lucide="chevron-down" class="faq-chevron size-4 shrink-0 text-muted-foreground"></i></summary>
        <p class="pb-4 pe-8 text-2sm text-secondary-foreground">{i18n(it.get("a", ""))}</p>
      </details>''' for it in f["items"])
    return f'''<section class="container-fixed pb-12" aria-labelledby="faq-heading">
    <h2 id="faq-heading" class="pb-5 font-display text-xl font-medium text-mono">{i18n(f.get("title", ""))}</h2>
    <div class="card divide-y divide-border">{items}
    </div>
  </section>'''

def build_pricing_cta(c):
    if not c or not c.get("title"): return None
    lead = f'\n      <p class="max-w-lg text-2sm text-secondary-foreground">{i18n(c["lead"])}</p>' if c.get("lead") else ""
    btns = ""
    if c.get("primary"): btns += f'<a href="#" class="btn btn-primary h-10 px-5 text-sm">{i18n(c["primary"])}<i data-lucide="arrow-right" class="rtl:rotate-180"></i></a>'
    if c.get("secondary"): btns += f'\n        <a href="#" class="btn btn-ghost h-10 px-4 text-sm">{i18n(c["secondary"])}</a>'
    return f'''<section id="cta" class="container-fixed pb-14" aria-labelledby="cta-heading">
    <div class="card flex flex-col items-center gap-4 p-7.5 text-center md:p-10">
      <h2 id="cta-heading" class="max-w-xl font-display text-2xl font-medium text-mono">{i18n(c["title"])}</h2>{lead}
      <div class="flex flex-wrap items-center justify-center gap-2.5 pt-1">
        {btns}
      </div>
    </div>
  </section>'''

def build_pricing_footer(spec):
    f = spec.get("footer") or {}
    links = "".join(f'\n      <a href="{esc(l.get("href", "#"))}" class="hover:text-primary-accent">{i18n(l.get("label", ""))}</a>'
                    for l in [x if isinstance(x, dict) else {"label": x} for x in f.get("links") or []])
    nav = f'\n    <nav class="flex flex-wrap gap-4" aria-label="Footer">{links}\n    </nav>' if links else ""
    return f'''<footer class="border-t border-border">
  <div class="container-fixed flex flex-wrap items-center justify-between gap-2.5 py-5 text-2sm text-muted-foreground">
    <span>{esc(f.get("legal", ""))}</span>{nav}
  </div>
</footer>'''

def build_pricing(spec, s):
    spec = derive_pricing(spec)
    s = set_head(s, spec, base="h-full")
    s = region(s, "header", build_pricing_header(spec))
    s = region(s, "pricing-intro", build_pricing_intro(spec))
    s = region(s, "plans", build_plans(spec))
    s = region(s, "comparison", build_comparison(spec))
    s = region(s, "faq", build_pricing_faq(spec.get("faq")))
    s = region(s, "closing-cta", build_pricing_cta(spec.get("cta")))
    s = region(s, "footer", build_pricing_footer(spec))
    s = apply_i18n(s, spec)
    return strip_demo_controls(s, spec), spec

def applied_check_pricing(spec, out_html):
    """Every label the spec asked for must be in the page. A miss means an anchor went stale."""
    want = []
    if spec.get("product"): want.append(("product", spec["product"]))
    for i, n in enumerate(spec.get("nav") or []):
        if n.get("label"): want.append((f"nav[{i}].label", n["label"]))
    for key, v in (spec.get("actions") or {}).items():
        if v: want.append((f"actions.{key}", v))
    it = spec.get("intro") or {}
    for key in ("title", "lead", "save", "monthly_note", "yearly_note"):
        if it.get(key): want.append((f"intro.{key}", it[key]))
    for i, p in enumerate(spec.get("plans") or []):
        for key in ("name", "blurb", "price", "price_yearly", "yearly_total", "cta", "badge", "inherits"):
            if p.get(key): want.append((f"plans[{i}].{key}", p[key]))
        for j, x in enumerate(p.get("features") or []): want.append((f"plans[{i}].features[{j}]", x))
    if spec.get("note"): want.append(("note", spec["note"]))
    c = spec.get("comparison") or {}
    for key in ("title", "lead", "caption", "feature_column"):
        if c.get(key): want.append((f"comparison.{key}", c[key]))
    for i, g in enumerate(c.get("groups") or []):
        if g.get("heading"): want.append((f"comparison.groups[{i}].heading", g["heading"]))
        for j, r in enumerate(g.get("rows") or []):
            if r.get("label"): want.append((f"comparison.groups[{i}].rows[{j}].label", r["label"]))
            for k, v in enumerate(r.get("cells") or []):
                if isinstance(v, str) and v: want.append((f"comparison.groups[{i}].rows[{j}].cells[{k}]", v))
    f = spec.get("faq") or {}
    if f.get("title"): want.append(("faq.title", f["title"]))
    for i, x in enumerate(f.get("items") or []):
        for key in ("q", "a"):
            if x.get(key): want.append((f"faq.items[{i}].{key}", x[key]))
    cta = spec.get("cta") or {}
    for key in ("title", "lead", "primary", "secondary"):
        if cta.get(key): want.append((f"cta.{key}", cta[key]))
    fo = spec.get("footer") or {}
    if fo.get("legal"): want.append(("footer.legal", fo["legal"]))
    for i, l in enumerate(fo.get("links") or []):
        want.append((f"footer.links[{i}]", l if isinstance(l, str) else l.get("label", "")))
    return [(field, value) for field, value in want if not present(value, out_html)]


# ---------------------------------------------------------------- driver ----
# One template, one spec schema, one applied-check and one leftover table per kind. "app" is the default.
KINDS = {
    "app":     dict(template="app-shell.html",     example="spec.example.json",         build=build_app,     check=applied_check,         shell=None),
    "landing": dict(template="landing-shell.html", example="spec.landing.example.json", build=build_landing, check=applied_check_landing, shell=SHELL_LANDING),
    "pricing": dict(template="pricing-shell.html", example="spec.pricing.example.json", build=build_pricing, check=applied_check_pricing, shell=SHELL_PRICING),
}
SUMMARY = {"app": lambda sp: f"nav={len(sp.get('nav', []))} kpis={len(sp.get('kpis', []))} rows={len((sp.get('table') or {}).get('rows', []))}",
           "landing": lambda sp: f"nav={len(sp.get('nav', []))} sections={len(sp.get('sections', []))} faq={len((sp.get('faq') or {}).get('items', []))}",
           "pricing": lambda sp: f"plans={len(sp.get('plans', []))} groups={len((sp.get('comparison') or {}).get('groups', []))} faq={len((sp.get('faq') or {}).get('items', []))}"}

def main():
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print(__doc__.strip()); return 0
    argv = sys.argv[1:]; kind = None; args = []; skip = False
    for i, a in enumerate(argv):                        # --kind overrides the spec's own "kind"
        if skip: skip = False
        elif a == "--kind": kind, skip = (argv[i + 1] if i + 1 < len(argv) else None), True
        elif a.startswith("--kind="): kind = a.split("=", 1)[1]
        elif not a.startswith("--"): args.append(a)
    if kind is not None and kind not in KINDS:
        print(f"unknown --kind {kind!r}: expected one of {', '.join(KINDS)}", file=sys.stderr); sys.exit(2)
    if "--example" in argv:
        print(open(asset(KINDS[kind or "app"]["example"]), encoding="utf-8").read()); return
    if len(args) < 2:
        print(__doc__.split("Keys shared")[0].strip(), file=sys.stderr); sys.exit(2)
    spec = json.load(open(args[0], encoding="utf-8")); out = args[1]
    kind = kind or spec.get("kind", "app")
    if kind not in KINDS:
        print(f"unknown kind {kind!r} in {args[0]}: expected one of {', '.join(KINDS)}", file=sys.stderr); sys.exit(2)
    k = KINDS[kind]
    s, spec = k["build"](spec, open(asset(k["template"]), encoding="utf-8").read())
    if k["shell"]: MISSES.extend(leftovers(s, k["shell"]))
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8", newline="\n").write(s)
    print(f"built {out} ({len(s.encode('utf-8')):,} bytes) from a {kind}-kind spec: " + SUMMARY[kind](spec))
    missing = k["check"](spec, s)
    if MISSES or missing:
        print("SPEC NOT FULLY APPLIED - the page kept the shell's own content here:", file=sys.stderr)
        for what in MISSES:
            print(f"  anchor never matched: {what}", file=sys.stderr)
        for field, value in missing:
            print(f"  {field} = {value!r}", file=sys.stderr)
        print("The shell's wording or its @region markers probably changed; update the SHELL table and the "
              f"anchors in this script to match assets/{k['template']}.", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
