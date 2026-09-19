"""Build a complete app screen from a small JSON spec, using assets/app-shell.html as the template (Class D).

The model writes ~2 KB of JSON instead of ~150 KB of HTML. Everything the spec does not mention keeps the
scaffold's defaults, so a partial spec still yields a working page.

Usage:
  python scripts/build-screen.py spec.json out.html
  python scripts/build-screen.py --example > spec.json     (prints the example spec)

Spec keys (all optional except product/title): see assets/spec.example.json
  product, title, subtitle, theme, density, dark, dir, lang,
  nav: [ {heading} | {label, icon, active, badge, children:[...]} ],
  toolbar: { periods:[...], secondary, primary },
  kpis: [ {label, value, delta, trend:"up|down", icon, spark:[numbers]} ]  (1–6),
  chart: { title, subtitle, series:[{name,data}], categories:[...], axis } (axis names the category
         column of the chart's screen-reader table; it keeps the shell's word when the spec omits it),
  highlights: { title, total_label, total, delta, trend:"up|down", items:[{label, value}] },
  table: { title, count, columns:[4 labels], rows:[{name, initials, sub, plan, status, time}] },
         sub is the second line under the name, plan is the Item column; either one alone fills both.
  activity: [ {who, text, when, primary} ],
  i18n: { ar: { "English": "العربية", ... } },
  extra_html: "<div class='card'>...</div>"   (appended as a full-width row after the table row)
"""
import json, os, re, sys, html
try:    # "--example > spec.json" must write the Arabic labels whole; a cp1252 console truncates the spec
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "assets", "app-shell.html")
# What the shipped shell says today, per slot. The generator swaps these for the spec's words;
# if the shell is reworded, update this table -- tests/smoke.py builds a spec with different
# words on purpose and fails when a slot stops landing.
SHELL = {
    "brand": "Acme Ops",
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
EXAMPLE = os.path.join(ROOT, "assets", "spec.example.json")

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

def region(s, name, new_inner):
    pat = re.compile(r"(<!-- @region " + name + r" -->\n)([\s\S]*?)(<!-- @endregion " + name + r" -->)")
    if not pat.search(s):
        MISSES.append(f"region {name} (the shell's own {name} markup shipped instead)"); return s
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
            out.append(f'    <div class="nav-group{" open" if it.get("open", True) else ""}">\n      <a class="nav-link" href="#" data-toggle-group><i data-lucide="{esc(icon)}"></i><span class="nav-title grow truncate" data-i18n="{esc(label)}">{esc(label)}</span><i data-lucide="chevron-right" class="nav-arrow size-4! transition-transform rtl:rotate-180"></i></a>\n      <div class="nav-children">{kids}\n      </div>\n    </div>')
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
          <p class="text-2sm text-secondary-foreground">{esc(spec.get("subtitle",""))}</p>
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
            <div class="flex items-center justify-between"><span class="inline-flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary"><i data-lucide="{esc(k.get("icon","activity"))}" class="size-5"></i></span>{badge}</div>
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


def main():
    if "--example" in sys.argv:
        print(open(EXAMPLE, encoding="utf-8").read()); return
    spec = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
    s = open(TEMPLATE, encoding="utf-8").read()
    product = spec.get("product", "Product"); title = spec.get("title", "Dashboard")
    classes = " ".join(c for c in ["h-full", spec.get("theme", ""), spec.get("density", ""), "dark" if spec.get("dark") else ""] if c)
    s = s.replace('<html lang="en" dir="ltr" class="h-full">', f'<html lang="{esc(spec.get("lang","en"))}" dir="{esc(spec.get("dir","ltr"))}" class="{classes}">')
    s = s.replace("<title>jbelly-ui — app shell</title>", f"<title>{esc(product)} — {esc(title)}</title>")
    s = s.replace(f'<span class="font-display">{SHELL["brand"]}</span>', f'<span class="font-display">{esc(product)}</span>')
    s = s.replace(f'© 2026 {SHELL["brand"]}', f'© 2026 {esc(product)}')
    theme_fonts = {"theme-clinic": ["Manrope:wght@400;500;600;700"], "theme-graphite": ["IBM+Plex+Sans:wght@400;500;600", "IBM+Plex+Mono:wght@400;500"],
                   "theme-editorial": ["Fraunces:opsz,wght@9..144,500;9..144,600", "Source+Sans+3:wght@400;500;600"], "theme-neo": ["Space+Grotesk:wght@500;600;700", "DM+Sans:wght@400;500;600"],
                   "theme-slate": [], "theme-mint": ["Plus+Jakarta+Sans:wght@400;500;600;700"]}
    fams = ["Inter:wght@400;500;600"] + theme_fonts.get(spec.get("theme", ""), []) + ["Noto+Sans+Arabic:wght@400;500;600"]
    s = re.sub(r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">', '<link href="https://fonts.googleapis.com/css2?' + "&".join("family=" + f for f in fams) + '&display=swap" rel="stylesheet">', s, count=1)
    if spec.get("nav"): s = region(s, "nav", build_nav(spec["nav"]))
    s = region(s, "toolbar", build_toolbar(spec))
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
        s = sub1(s, r'<span class="badge badge-sm badge-light-(?:success|destructive) mb-1"><i data-lucide="trending-(?:up|down)" class="size-3"></i>[^<]*</span>',
                 lambda m: f'<span class="badge badge-sm badge-light-{"success" if up else "destructive"} mb-1">'
                           f'<i data-lucide="trending-{"up" if up else "down"}" class="size-3"></i>{esc(hl["delta"])}</span>',
                 "highlights.delta badge")
    if hl.get("items"):
        items = hl["items"]; total = sum(int(str(i.get("value", 0)).replace(",", "")) for i in items)
        ht = hl.get("title", SHELL["highlights_title"]); old_ht = SHELL["highlights_title"]
        s = s.replace(f'data-i18n="{old_ht}">{old_ht}</h3>', f'data-i18n="{esc(ht)}">{esc(ht)}</h3>')
        old_tl = SHELL["highlights_total_label"]; tl = hl.get("total_label", old_tl)
        s = s.replace(f'data-i18n="{old_tl}">{old_tl}</span>', f'data-i18n="{esc(tl)}">{esc(tl)}</span>')
        s = s.replace('<span class="text-2xl font-semibold text-mono tabular-nums font-display">214</span>', f'<span class="text-2xl font-semibold text-mono tabular-nums font-display">{esc(hl.get("total", total))}</span>')
        s = sub1(s, r"series: \[98, 58, 36, 22\], labels: \[[^\]]*\]",
                 lambda m: "series: " + js([int(str(i.get("value", 0)).replace(",", "")) for i in items]) + ", labels: " + js([i["label"] for i in items]),
                 "highlights donut data")
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
    def prune_i18n(m):
        d = json.loads(m.group(1))
        page_without_dict = s.replace(m.group(0), "")
        kept = {k: v for k, v in d.items() if k in page_without_dict}
        kept.update((spec.get("i18n") or {}).get("ar") or {})
        return "const I18N = " + js(kept) + ";"
    s = re.sub(r"const I18N = (\{[\s\S]*?\});", prune_i18n, s, count=1)
    if spec.get("i18n", {}).get("ar"):
        s = re.sub(r"const I18N = (\{[\s\S]*?\});", lambda m: "const I18N = " + js({**json.loads(m.group(1)), **spec["i18n"]["ar"]}) + ";", s, count=1)
    # remove demo controls unless asked to keep them
    if not spec.get("keep_demo_controls"):
        s = re.sub(r"(?s)<!-- ===== Demo controls.*?</details>\s*", "", s)
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
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8", newline="\n").write(s)
    print(f"built {out} ({len(s.encode('utf-8')):,} bytes) from spec: nav={len(spec.get('nav',[]))} kpis={len(spec.get('kpis',[]))} rows={len((spec.get('table') or {}).get('rows',[]))}")
    missing = applied_check(spec, s)
    if MISSES or missing:
        print("SPEC NOT FULLY APPLIED - the page kept the shell's own content here:", file=sys.stderr)
        for what in MISSES:
            print(f"  anchor never matched: {what}", file=sys.stderr)
        for field, value in missing:
            print(f"  {field} = {value!r}", file=sys.stderr)
        print("The shell's wording or its @region markers probably changed; update SHELL and the anchors "
              "in this script to match assets/app-shell.html.", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
