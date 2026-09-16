"""patch1: markup additions on top of build-screen.py output (Class D). Usage: python patch1.py spec.json dashboard.html"""
import json, re, sys, html as H
spec = json.load(open(sys.argv[1], encoding="utf-8")); path = sys.argv[2]
s = open(path, encoding="utf-8").read()
esc = lambda x: H.escape(str(x), quote=True)
def i18n(t): return f'<span data-i18n="{esc(t)}">{esc(t)}</span>'
def must(old, new, n=1):
    global s
    assert old in s, "anchor missing: " + old[:70]
    s = s.replace(old, new, n)

# ---- head: fonts + personality/behaviour CSS (plain CSS, tokens only) ----
if "fonts.googleapis" not in s:
    must('<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>',
         '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700&family=Noto+Sans+Arabic:wght@400;500;600&display=swap" rel="stylesheet">\n'
         '<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>')
CSS = """
<style>
/* personality: theme-clinic modified (radius 0.5rem, compact, own data colours) + Arabic companion face */
.theme-clinic { --radius: 0.5rem; --chart-2: oklch(58% 0.1 255); --chart-3: oklch(70% 0.16 65); --chart-4: oklch(62% 0.08 150); }
.theme-clinic.dark { --chart-2: oklch(72% 0.1 255); --chart-3: oklch(78% 0.15 70); }
html[lang="ar"] { --font-sans: "Noto Sans Arabic", "Inter", ui-sans-serif, sans-serif; --font-display: "Noto Sans Arabic", "Manrope", sans-serif; }
.switch { appearance: none; width: 30px; height: 18px; border-radius: 9999px; background: var(--input); position: relative; cursor: pointer; flex-shrink: 0; transition: background .15s ease-out; }
.switch::before { content: ""; position: absolute; top: 2px; inset-inline-start: 2px; width: 14px; height: 14px; border-radius: 9999px; background: var(--card); box-shadow: var(--shadow-xs, 0 1px 2px rgb(0 0 0 / .1)); transition: transform .15s ease-out; }
.switch:checked { background: var(--primary); } .switch:checked::before { transform: translateX(12px); } [dir="rtl"] .switch:checked::before { transform: translateX(-12px); }
.switch:focus-visible { outline: 2px solid var(--ring); outline-offset: 2px; }
#appt-table thead th { position: sticky; top: 0; background: var(--card); z-index: 1; }
#appt-table.table-compact td { height: 36px; }
.tip { position: relative; } .tip::after { content: attr(data-tip); position: absolute; top: calc(100% + 6px); inset-inline-end: 0; width: max-content; max-width: 260px; padding: 6px 8px; border-radius: 6px; background: var(--mono); color: var(--mono-foreground); font-size: 12px; line-height: 1.3; white-space: normal; opacity: 0; pointer-events: none; transition: opacity .15s ease-out; z-index: 20; }
.tip:hover::after, .tip:focus-visible::after { opacity: 1; }
.task-check:checked ~ span .task-text { text-decoration: line-through; color: var(--muted-foreground); }
.kb-card { cursor: grab; } .kb-card.dragging { opacity: .5; } .kb-col.over { outline: 2px dashed var(--ring); outline-offset: -2px; }
.legend-btn[aria-pressed="false"] { opacity: .45; text-decoration: line-through; }
.palette-active { background: var(--accent); }
</style>"""
must("</style>", "</style>" + CSS)

# ---- skip link + main landmark ----
must('<body class="h-full flex text-2sm">', '<body class="h-full flex text-2sm">\n<a href="#main" class="sr-only focus:not-sr-only fixed top-2 start-2 z-[60] btn btn-primary">Skip to content</a>')
must('<main class="grow pt-5 pb-10">', '<main id="main" class="grow pt-5 pb-10" tabindex="-1">')

# ---- header: branch switcher, notifications, language + density toggles ----
branches = spec.get("branches", ["All branches"])
bitems = "".join(f'<button type="button" class="menu-item justify-between" role="menuitemradio" aria-checked="{"true" if i == 0 else "false"}" data-branch="{esc(b)}">{i18n(b)}<i data-lucide="check" class="branch-check{"" if i == 0 else " hidden"}"></i></button>' for i, b in enumerate(branches))
must('<button id="open-search"',
     f'<div class="relative"><button id="branch-btn" class="btn btn-outline btn-sm gap-2" aria-haspopup="menu" aria-expanded="false"><i data-lucide="building-2"></i><span id="branch-btn-label" data-i18n="{esc(branches[0])}">{esc(branches[0])}</span><i data-lucide="chevron-down" class="size-3.5! text-muted-foreground"></i></button>'
     f'<div id="branch-menu" class="menu absolute start-0 top-full mt-2 w-48 hidden" role="menu" data-pop>{bitems}</div></div>\n        <button id="open-search"')
must('<button class="btn btn-ghost btn-icon relative" aria-label="Notifications"><i data-lucide="bell"></i><span class="absolute top-2 end-2 size-2 rounded-full bg-destructive ring-2 ring-background"></span></button>',
     '<button id="notif-btn" class="btn btn-ghost btn-icon relative" aria-label="Notifications" aria-haspopup="dialog"><i data-lucide="bell"></i><span id="notif-dot" class="absolute top-2 end-2 size-2 rounded-full bg-destructive ring-2 ring-background"></span></button>\n'
     '        <button id="lang-toggle" class="btn btn-ghost btn-sm font-mono" aria-label="Switch language"><span>AR</span></button>\n'
     '        <button id="density-toggle" class="btn btn-ghost btn-icon" aria-label="Toggle density" aria-pressed="true"><i data-lucide="rows-3"></i></button>')

# ---- toolbar: subtitle with live "updated", branch filter, compare switch, custom range ----
h1 = s.index("<h1 ")
m = re.compile(r'<p class="text-2sm text-secondary-foreground">[^<]*</p>').search(s, h1)
s = s[:m.start()] + ('<p class="text-2sm text-secondary-foreground"><span id="branch-label" data-i18n="All branches">All branches</span> · <span id="period-label" data-i18n="Last 30 days">Last 30 days</span> vs previous period · Updated <span id="updated" class="font-mono tabular-nums">4</span> min ago</p>') + s[m.end():]
bopts = "".join(f'<option data-i18n="{esc(b)}">{esc(b)}</option>' for b in branches)
must('<select id="period" class="input select w-40">',
     f'<select id="branch-filter" class="input select w-36" aria-label="Branch">{bopts}</select>\n          <select id="period" class="input select w-36" aria-label="Date range">')
must('<button class="btn btn-outline"><i data-lucide="download"></i>',
     '<div id="custom-range" class="hidden items-center gap-1.5"><input type="date" class="input input-sm w-34" aria-label="From" value="2026-08-10"><span class="text-muted-foreground">–</span><input type="date" class="input input-sm w-34" aria-label="To" value="2026-09-09"></div>\n'
     '          <label class="inline-flex items-center gap-2 text-2sm text-secondary-foreground cursor-pointer"><input type="checkbox" class="switch" id="compare" checked><span data-i18n="Compare to previous period">Compare to previous period</span></label>\n'
     '          <button class="btn btn-outline"><i data-lucide="download"></i>')
must('<div class="flex items-center gap-2.5">\n          <select id="branch-filter"', '<div class="flex flex-wrap items-center gap-2.5">\n          <select id="branch-filter"')
must('<option selected data-i18n="Last 7 days">', '<option data-i18n="Last 7 days">')
must('<option data-i18n="Last 30 days">', '<option selected data-i18n="Last 30 days">')
must('<span class="text-mono" data-i18n="Dashboard">Dashboard</span>', '<span class="text-mono" data-i18n="Operations console">Operations console</span>')

# ---- KPIs: 3-up at lg, 2-up at sm; count-up on integer values; "good" downward delta ----
must('class="grid sm:grid-cols-2 xl:grid-cols-3 gap-(--page-gap)" id="kpis"', 'class="grid sm:grid-cols-2 lg:grid-cols-3 gap-(--page-gap)" id="kpis"')
s = re.sub(r'<span class="text-3xl font-semibold text-mono tabular-nums font-display">(\d{1,3}(?:,\d{3})*)</span>',
           lambda m: f'<span class="text-3xl font-semibold text-mono tabular-nums font-display" data-count="{m.group(1).replace(",", "")}">0</span>', s)
for k in spec.get("kpis", []):
    if k.get("good") and k.get("trend") == "down":
        j = s.index(f'data-i18n="{esc(k["label"])}"'); i = s.rfind('<div class="card p-(--card-p)', 0, j)
        s = s[:i] + s[i:j].replace("badge-light-destructive", "badge-light-success") + s[j:]

# ---- row 2: 4-col grid, clickable legend, sr tables, capacity card ----
r2 = s.index("<!-- @region row2 -->")
s = s[:r2] + s[r2:].replace('<div class="grid lg:grid-cols-3 gap-(--page-gap) items-stretch">', '<div class="grid lg:grid-cols-2 xl:grid-cols-4 gap-(--page-gap) items-stretch">', 1)
ch = spec["chart"]; dots = ["bg-primary", "bg-(--chart-2)", "bg-(--chart-3)"]
legend = '<div class="flex items-center gap-1" role="group" aria-label="Toggle series">' + "".join(
    f'<button type="button" class="legend-btn inline-flex items-center gap-1.5 h-7 px-2 rounded-md text-2sm text-secondary-foreground hover:bg-accent" data-series="{esc(x["name"])}" aria-pressed="true"><span class="size-2 rounded-full {dots[i]}"></span>{i18n(x["name"])}</button>' for i, x in enumerate(ch["series"])) + '</div>'
s = re.sub(r'<div class="flex items-center gap-2\.5"><span class="flex items-center gap-1\.5 text-2sm text-secondary-foreground">[\s\S]*?aria-label="More"><i data-lucide="ellipsis-vertical"></i></button></div>', legend, s, count=1)
sr = lambda cap, heads, rows: f'<table class="sr-only"><caption>{esc(cap)}</caption><thead><tr>{"".join(f"<th>{esc(h)}</th>" for h in heads)}</tr></thead><tbody>{"".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows)}</tbody></table>'
cats = ch["categories"]; ser = ch["series"]
s = re.sub(r'<div id="chart-visits"[^>]*></div>\s*<table class="sr-only">[\s\S]*?</table>',
           f'<div id="chart-visits" class="h-full min-h-60" role="img" aria-label="Consultations rose from {ser[0]["data"][0]} to {ser[0]["data"][-1]} per week over 12 weeks while no-shows fell to {ser[2]["data"][-1]}"></div>\n              '
           + sr(ch["title"], ["Week"] + [x["name"] for x in ser], [[cats[i]] + [x["data"][i] for x in ser] for i in (0, 5, 11)]), s, count=1)
hl = spec["highlights"]
must('18%</span>', f'{esc(hl.get("delta", ""))}</span>')
must('<div id="chart-programmes" class="h-44 -my-1 overflow-hidden"></div>',
     f'<div id="chart-programmes" class="h-44 -my-1 overflow-hidden" role="img" aria-label="{esc(hl["total"])} active patients; {esc(hl["items"][0]["label"])} is the largest programme"></div>' + sr(hl["title"], ["Programme", "Patients"], [[i["label"], i["value"]] for i in hl["items"]]))
cap = spec["capacity"]
capcard = f'''          <div class="card h-full min-w-0">
            <div class="card-header"><h3 class="card-title" data-i18n="{esc(cap["title"])}">{esc(cap["title"])}</h3><span class="text-xs text-muted-foreground">% booked</span></div>
            <div class="card-content px-3 py-2 overflow-hidden"><div id="chart-capacity" class="h-56" role="img" aria-label="{esc(cap["items"][0]["name"])} is the most booked at {cap["items"][0]["pct"]}%; {esc(cap["items"][-1]["name"])} the least at {cap["items"][-1]["pct"]}%"></div>{sr(cap["title"], ["Dietitian", "% booked"], [[i["name"], f'{i["pct"]}%'] for i in cap["items"]])}</div>
          </div>
'''
e2 = s.index("<!-- @endregion row2 -->"); j = s.rfind("</div>", 0, e2); s = s[:j] + capcard + "        " + s[j:]

# ---- row 3: heatmap + adherence progress list ----
hm = spec["heatmap"]; ad = spec["adherence"]
swatch = "".join(f'<span class="inline-flex items-center gap-1"><span class="size-3 rounded-sm {c}"></span>{l}</span>' for c, l in [("bg-primary/10 border border-border", "0"), ("bg-primary/30", "1–3"), ("bg-primary/50", "4–6"), ("bg-primary/75", "7–9"), ("bg-primary", "10+")])
peak = max(range(7), key=lambda d: sum(hm["data"][d]))
row3 = f'''<div class="grid lg:grid-cols-3 gap-(--page-gap) items-stretch">
          <div class="card h-full lg:col-span-2 min-w-0">
            <div class="card-header"><h3 class="card-title" data-i18n="{esc(hm["title"])}">{esc(hm["title"])}</h3><div class="flex items-center gap-3 text-xs text-secondary-foreground" aria-hidden="true">{swatch}</div></div>
            <div class="card-content px-3 py-2 overflow-hidden"><div id="chart-heat" class="h-72" role="img" aria-label="Busiest day is {hm["days"][peak]}; peak hours are 10:00–11:00 and 15:00–16:00; Friday is closed"></div>{sr(hm["title"], ["Day"] + [h + ":00" for h in hm["hours"]], [[hm["days"][d]] + hm["data"][d] for d in range(7)])}</div>
          </div>
          <div class="card h-full">
            <div class="card-header"><h3 class="card-title" data-i18n="{esc(ad["title"])}">{esc(ad["title"])}</h3><span class="text-xs text-muted-foreground">30 days</span></div>
            <div class="card-content flex flex-col gap-4">
''' + "".join(f'''              <div class="flex flex-col gap-1.5"><div class="flex justify-between text-2sm"><span data-i18n="{esc(i["label"])}">{esc(i["label"])}</span><span class="font-medium text-mono tabular-nums">{i["pct"]}%</span></div><div class="h-2 rounded-full bg-muted overflow-hidden" role="progressbar" aria-valuenow="{i["pct"]}" aria-valuemin="0" aria-valuemax="100" aria-label="{esc(i["label"])} adherence"><div class="h-full rounded-full {"bg-primary" if i["pct"] >= 75 else "bg-warning"}" style="width:{i["pct"]}%"></div></div></div>
''' for i in ad["items"]) + '''            </div>
          </div>
        </div>
'''
must("<!-- @endregion row2 -->", "<!-- @endregion row2 -->\n        " + row3)

# ---- row 4: table full width; toolbar, chips, columns, density, states; thead; footer; activity card removed ----
r3 = s.index("<!-- @region row3 -->")
s = s[:r3] + s[r3:].replace('<div class="grid lg:grid-cols-3 gap-(--page-gap) items-stretch">', '<div class="grid gap-(--page-gap)">', 1).replace('<div class="card h-full lg:col-span-2 min-w-0">', '<div class="card min-w-0">', 1)
a = s.index('data-i18n="Activity">Activity</h3>'); a0 = s.rfind('<div class="card h-full">', 0, a); e3 = s.index("<!-- @endregion row3 -->"); a1 = s.rfind("</div>", 0, e3)
s = s[:a0] + s[a1:]
tools = '''<div class="flex items-center gap-2.5 flex-wrap">
                <div class="relative"><i data-lucide="search" class="absolute start-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground"></i><input id="tbl-search" class="input input-sm ps-8 w-48" placeholder="Search patients" data-i18n-placeholder="Search patients" aria-label="Search appointments"></div>
                <div class="relative"><button id="cols-btn" class="btn btn-outline btn-sm gap-1.5" aria-haspopup="menu" aria-expanded="false"><i data-lucide="columns-3"></i><span data-i18n="Columns">Columns</span></button>
                  <div id="cols-menu" class="menu absolute end-0 top-full mt-2 w-44 hidden" role="menu" data-pop>''' + "".join(f'<label class="menu-item"><input type="checkbox" class="checkbox col-toggle" data-col="{k}"{" checked" if k != "d" else ""}><span data-i18n="{l}">{l}</span></label>' for k, l in [("p", "Programme"), ("b", "Branch"), ("d", "Dietitian"), ("t", "Time")]) + '''</div></div>
                <button id="tbl-density" class="btn btn-outline btn-icon btn-sm" aria-label="Toggle table density" aria-pressed="false"><i data-lucide="rows-3"></i></button>
                <div class="inline-flex items-center gap-1 rounded-lg bg-muted p-1" role="tablist" aria-label="Data state">
                  <button class="h-6 px-2.5 rounded-md text-xs bg-background text-mono shadow-xs font-medium" data-state="data" role="tab" data-i18n="Data">Data</button>
                  <button class="h-6 px-2.5 rounded-md text-xs text-secondary-foreground hover:text-foreground" data-state="loading" role="tab" data-i18n="Loading">Loading</button>
                  <button class="h-6 px-2.5 rounded-md text-xs text-secondary-foreground hover:text-foreground" data-state="empty" role="tab" data-i18n="Empty">Empty</button>
                  <button class="h-6 px-2.5 rounded-md text-xs text-secondary-foreground hover:text-foreground" data-state="error" role="tab" data-i18n="Error">Error</button>
                </div>
              </div>'''
s = re.sub(r'<div class="flex items-center gap-2\.5 flex-wrap">\s*<div class="relative">[\s\S]*?aria-label="Demo data state">[\s\S]*?</div>\s*</div>', tools, s, count=1)
must('<div class="card-header hidden bg-accent/60" id="bulk-bar">', '<div class="flex flex-wrap items-center gap-1.5 px-5 py-2.5 border-b border-border" id="chips" role="group" aria-label="Filter by status"></div>\n            <div class="card-header hidden bg-accent/60" id="bulk-bar">')
must('<button class="btn btn-ghost btn-sm"><i data-lucide="mail"></i>Send reminder</button>', '<button class="btn btn-ghost btn-sm" data-bulk="remind"><i data-lucide="mail"></i><span data-i18n="Send reminder">Send reminder</span></button>')
must('<button class="btn btn-ghost btn-sm"><i data-lucide="calendar-clock"></i>Reschedule</button>', '<button class="btn btn-ghost btn-sm" data-bulk="reschedule"><i data-lucide="calendar-clock"></i><span data-i18n="Reschedule">Reschedule</span></button>')
must('<button class="btn btn-outline btn-sm text-destructive border-destructive/40 hover:bg-destructive/10"><i data-lucide="trash-2"></i>Cancel</button>', '<button class="btn btn-outline btn-sm text-destructive border-destructive/40 hover:bg-destructive/10" data-bulk="cancel"><i data-lucide="trash-2"></i><span data-i18n="Cancel">Cancel</span></button><button class="btn btn-ghost btn-icon btn-sm" data-bulk="clear" aria-label="Clear selection"><i data-lucide="x"></i></button>')
must('<div class="overflow-x-auto">\n              <table class="table" id="appt-table">', '<div class="overflow-auto max-h-[520px] scroll-thin">\n              <table class="table" id="appt-table">')
th = lambda k, l, extra="": f'<th data-col="{k}" aria-sort="none" class="{extra}"><button type="button" class="inline-flex items-center gap-1 cursor-pointer select-none" data-sort="{k}"><span data-i18n="{l}">{l}</span> <i data-lucide="chevrons-up-down" class="size-3.5 text-muted-foreground sort-icon"></i></button></th>'
s = re.sub(r'<thead><tr><th class="w-\[52px\] text-center">[\s\S]*?</tr></thead>',
           '<thead><tr><th class="w-[52px] text-center"><input type="checkbox" class="checkbox" id="check-all" aria-label="Select all"></th>' + th("n", "Patient", "min-w-56") + th("p", "Programme") + th("b", "Branch") + th("d", "Dietitian", "hidden") + th("s", "Status") + th("t", "Time") + '<th class="w-[84px]"><span class="sr-only">Actions</span></th></tr></thead>', s, count=1)
must('<select class="input select input-sm w-18"><option>5</option><option>10</option><option>25</option></select>', '<select id="page-size" class="input select input-sm w-18" aria-label="Rows per page"><option>5</option><option selected>10</option><option>25</option></select>')
s = re.sub(r'<span>1–\d+ of \d+</span>', '<span id="page-info" class="tabular-nums">1–10 of 14</span>', s, count=1)
s = re.sub(r'<nav class="flex items-center gap-1" aria-label="Pagination">[\s\S]*?</nav>', '<nav id="pager" class="flex items-center gap-1" aria-label="Pagination"></nav>', s, count=1)

# ---- row 5: kanban + activity (grouped by day) + tasks ----
kb = spec["kanban"]
def kcard(c): return f'<div class="kb-card rounded-md border border-border bg-card shadow-xs p-2.5 flex flex-col gap-1" draggable="true" tabindex="0" title="Drag, or press Alt+Left / Alt+Right to move"><div class="flex items-center gap-2"><i data-lucide="grip-vertical" class="size-4 text-muted-foreground shrink-0"></i><span class="text-sm font-medium text-mono truncate grow">{esc(c["n"])}</span><span class="font-mono text-xs tabular-nums text-secondary-foreground">{esc(c["t"])}</span></div><span class="text-xs text-secondary-foreground ps-6 truncate">{esc(c["p"])} · {esc(c["d"])}</span></div>'
kcols = "".join(f'<div class="kb-col flex flex-col rounded-lg bg-muted/60 p-2 min-h-40" data-col="{esc(c["name"])}"><div class="flex items-center justify-between px-1 pb-2"><span class="text-xs font-medium uppercase text-muted-foreground" data-i18n="{esc(c["name"])}">{esc(c["name"])}</span><span class="badge badge-sm badge-outline kb-count">{len(c["cards"])}</span></div><div class="kb-cards flex flex-col gap-2 grow">{"".join(kcard(x) for x in c["cards"])}</div></div>' for c in kb["columns"])
acts = ""
for g in spec["activity_days"]:
    acts += f'<div class="text-xs font-medium uppercase text-muted-foreground pb-3">{esc(g["day"])}</div>'
    for i, a in enumerate(g["items"]):
        last = i == len(g["items"]) - 1; dot = "bg-primary" if a.get("primary") else "bg-muted-foreground"
        acts += f'<div class="relative flex gap-3 pb-5 ps-6{"" if last else " before:absolute before:start-2 before:top-6 before:bottom-0 before:w-px before:bg-border"}"><span class="absolute start-0 top-1 size-4 rounded-full border-2 border-background {dot}"></span><div class="flex flex-col gap-1"><p class="text-2sm"><span class="font-medium text-mono">{esc(a["who"])}</span> {esc(a["text"])}</p><span class="text-xs text-muted-foreground font-mono">{esc(a["when"])}</span></div></div>'
tasks = "".join(f'<label class="flex items-start gap-2.5 py-2.5 border-b border-border last:border-b-0 cursor-pointer"><input type="checkbox" class="checkbox mt-0.5 task-check"{" checked" if t.get("done") else ""}><span class="flex flex-col gap-0.5 grow min-w-0"><span class="text-2sm task-text">{esc(t["text"])}</span><span class="text-xs text-muted-foreground font-mono">Due {esc(t["due"])}</span></span></label>' for t in spec["tasks"])
open_tasks = sum(1 for t in spec["tasks"] if not t.get("done"))
row5 = f'''<div class="grid lg:grid-cols-3 gap-(--page-gap) items-stretch">
          <div class="card h-full lg:col-span-2 min-w-0">
            <div class="card-header"><h3 class="card-title" data-i18n="{esc(kb["title"])}">{esc(kb["title"])}</h3><button type="button" class="btn btn-ghost btn-icon btn-sm tip" data-tip="Drag a card by its handle, or focus a card and press Alt+Left / Alt+Right to move it between columns." aria-label="How to move cards"><i data-lucide="info"></i></button></div>
            <div class="card-content grid sm:grid-cols-3 gap-2.5" id="kanban">{kcols}</div>
          </div>
          <div class="flex flex-col gap-(--page-gap) min-w-0">
            <div class="card">
              <div class="card-header"><h3 class="card-title" data-i18n="Activity">Activity</h3><a href="#" class="text-primary hover:underline underline-offset-4 text-2sm font-medium" data-i18n="View all">View all</a></div>
              <div class="card-content flex flex-col">{acts}</div>
            </div>
            <div class="card grow">
              <div class="card-header"><div class="flex items-center gap-2.5"><h3 class="card-title" data-i18n="Tasks">Tasks</h3><span class="badge badge-sm badge-outline">{open_tasks} open</span></div><button class="btn btn-ghost btn-sm" data-toast="Task added"><i data-lucide="plus"></i>Add</button></div>
              <div class="card-content flex flex-col pt-1">{tasks}</div>
            </div>
          </div>
        </div>
'''
must("<!-- @endregion row3 -->", row5 + "      <!-- @endregion row3 -->")

# ---- patient drawer with tabs; notifications drawer; confirm modal ----
M = spec["measurements"]
drawer = f'''<aside id="drawer" class="fixed z-50 top-5 bottom-5 end-5 w-[450px] max-w-[90%] rounded-xl border border-border bg-card shadow-md flex flex-col hidden" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
  <div class="flex items-center justify-between px-5 py-2.5 border-b border-border"><span id="drawer-title" class="text-sm font-semibold text-mono" data-i18n="Patient">Patient</span><button class="btn btn-ghost btn-icon btn-sm" data-close-drawer aria-label="Close"><i data-lucide="x"></i></button></div>
  <div class="px-5 pt-4 flex items-center gap-3"><span class="inline-flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary font-semibold text-sm" id="drawer-initials">SK</span><div class="flex flex-col min-w-0"><span class="text-base font-semibold text-mono truncate" id="drawer-name">Sara Khalil</span><span class="text-2sm text-secondary-foreground truncate" id="drawer-plan">Weight loss · wk 6</span></div></div>
  <div class="px-5 pt-4"><nav class="flex gap-6 border-b border-border" role="tablist" aria-label="Patient sections">
    <button type="button" role="tab" data-dtab="overview" aria-selected="true" class="-mb-px pb-2.5 text-sm border-b-2 text-primary border-primary font-medium" data-i18n="Overview">Overview</button>
    <button type="button" role="tab" data-dtab="measure" aria-selected="false" class="-mb-px pb-2.5 text-sm border-b-2 border-transparent text-secondary-foreground hover:text-foreground" data-i18n="Measurements">Measurements</button>
    <button type="button" role="tab" data-dtab="notes" aria-selected="false" class="-mb-px pb-2.5 text-sm border-b-2 border-transparent text-secondary-foreground hover:text-foreground" data-i18n="Notes">Notes</button>
  </nav></div>
  <div class="grow overflow-y-auto scroll-thin p-5">
    <div id="dtab-overview" role="tabpanel" class="flex flex-col gap-4">
      <div class="grid grid-cols-2 gap-2.5 text-2sm">
        <div class="rounded-lg bg-muted p-3 flex flex-col gap-1"><span class="text-xs text-muted-foreground" data-i18n="Time">Time</span><span class="font-medium text-mono font-mono tabular-nums" id="drawer-time"></span></div>
        <div class="rounded-lg bg-muted p-3 flex flex-col gap-1"><span class="text-xs text-muted-foreground" data-i18n="Status">Status</span><span id="drawer-status"></span></div>
        <div class="rounded-lg bg-muted p-3 flex flex-col gap-1"><span class="text-xs text-muted-foreground" data-i18n="Branch">Branch</span><span class="font-medium text-mono" id="drawer-branch"></span></div>
        <div class="rounded-lg bg-muted p-3 flex flex-col gap-1"><span class="text-xs text-muted-foreground" data-i18n="Dietitian">Dietitian</span><span class="font-medium text-mono" id="drawer-diet"></span></div>
      </div>
      <div class="flex flex-col gap-1 text-2sm"><span class="text-xs text-muted-foreground">Contact</span><span class="font-mono tabular-nums">+962 79 555 0142</span><span class="text-secondary-foreground">Prefers WhatsApp reminders · Arabic</span></div>
    </div>
    <div id="dtab-measure" role="tabpanel" class="hidden flex-col gap-3">
      <div class="flex items-end justify-between"><div class="flex flex-col"><span class="text-xs text-muted-foreground">Weight, last 8 weeks</span><span class="text-2xl font-semibold text-mono tabular-nums font-display">{M["data"][-1]} kg</span></div><span class="badge badge-sm badge-light-success"><i data-lucide="trending-down" class="size-3"></i>{round(M["data"][0] - M["data"][-1], 1)} kg</span></div>
      <div id="chart-measure" class="h-40 -mx-2" role="img" aria-label="Weight fell steadily from {M["data"][0]} to {M["data"][-1]} kg over 8 weeks"></div>{sr("Weight by week", ["Week", "kg"], list(zip(M["labels"], M["data"])))}
    </div>
    <div id="dtab-notes" role="tabpanel" class="hidden flex-col gap-1.5"><label class="text-2sm font-medium text-mono" for="note">Visit note</label><textarea id="note" class="input h-auto min-h-32 p-3 leading-normal resize-y" placeholder="Symptoms, measurements, next steps…"></textarea><span class="text-xs text-muted-foreground">Visible to the care team only.</span></div>
  </div>
  <div class="grid grid-cols-2 gap-2.5 p-5 border-t border-border"><button class="btn btn-outline" data-close-drawer>Close</button><button class="btn btn-primary" id="save-note">Save note</button></div>
</aside>
<aside id="notif" class="fixed z-50 top-5 bottom-5 end-5 w-[400px] max-w-[90%] rounded-xl border border-border bg-card shadow-md flex-col hidden" role="dialog" aria-modal="true" aria-labelledby="notif-title">
  <div class="flex items-center justify-between px-5 py-2.5 border-b border-border"><span class="flex items-center gap-2"><span id="notif-title" class="text-sm font-semibold text-mono" data-i18n="Notifications">Notifications</span><span class="badge badge-sm badge-light-primary" id="notif-count">0</span></span><button class="btn btn-ghost btn-icon btn-sm" data-close-notif aria-label="Close"><i data-lucide="x"></i></button></div>
  <div class="px-3 pt-3"><div class="inline-flex gap-1 rounded-lg bg-muted p-1" role="tablist" aria-label="Notification groups">{"".join(f'<button type="button" role="tab" data-ntab="{k}" aria-selected="{"true" if k == "all" else "false"}" class="h-7 px-3 rounded-md text-xs{" bg-background text-mono shadow-xs font-medium" if k == "all" else " text-secondary-foreground hover:text-foreground"}" data-i18n="{l}">{l}</button>' for k, l in [("all", "All"), ("inbox", "Inbox"), ("team", "Team")])}</div></div>
  <div id="notif-list" class="grow overflow-y-auto scroll-thin p-2 flex flex-col gap-0.5"></div>
  <div class="flex items-center justify-between px-3 py-3 border-t border-border"><button class="btn btn-ghost btn-sm" id="notif-read-all"><i data-lucide="check-check"></i>Mark all read</button><button class="btn btn-outline btn-sm" data-close-notif>View all</button></div>
</aside>
<div id="confirm-overlay" class="fixed inset-0 z-50 bg-black/30 backdrop-blur-[2px] hidden"></div>
<div id="confirm" class="fixed z-50 top-1/2 start-1/2 -translate-x-1/2 rtl:translate-x-1/2 -translate-y-1/2 w-[calc(100%-2rem)] max-w-md rounded-lg border border-border bg-popover text-popover-foreground shadow-md hidden flex-col" role="alertdialog" aria-modal="true" aria-labelledby="confirm-title" aria-describedby="confirm-desc">
  <div class="px-5 py-3 border-b border-border flex items-center gap-2"><i data-lucide="triangle-alert" class="size-4 text-destructive"></i><span id="confirm-title" class="text-sm font-semibold text-mono">Cancel appointments?</span></div>
  <div class="px-5 py-4 text-2sm text-secondary-foreground" id="confirm-desc">This cancels <span id="confirm-n" class="font-medium text-mono">0</span> appointments and notifies the patients by SMS. You can undo for 5 seconds.</div>
  <div class="px-5 py-3 border-t border-border flex justify-end gap-2.5"><button class="btn btn-outline" id="confirm-no">Keep them</button><button class="btn btn-destructive" id="confirm-yes">Cancel appointments</button></div>
</div>'''
s = re.sub(r'<aside id="drawer"[\s\S]*?</aside>', drawer, s, count=1)

# ---- palette: grouped results from spec rows ----
pal = ('<div class="px-2 py-1.5 text-xs font-medium uppercase text-muted-foreground">Actions</div>'
       '<a class="menu-item" href="#"><i data-lucide="calendar-plus"></i>New appointment<span class="ms-auto kbd">N</span></a>'
       '<a class="menu-item" href="#"><i data-lucide="user-plus"></i>Add patient<span class="ms-auto kbd">P</span></a>'
       '<a class="menu-item" href="#"><i data-lucide="mail"></i>Send reminders to today\'s no-show risks</a>'
       '<div class="px-2 py-1.5 text-xs font-medium uppercase text-muted-foreground" data-i18n="Patients">Patients</div>'
       + "".join(f'<a class="menu-item" href="#"><i data-lucide="user"></i>{esc(r["name"])}<span class="ms-auto text-xs text-muted-foreground">{esc(r["plan"])} · {esc(r["branch"])}</span></a>' for r in spec["table"]["rows"][:6])
       + '<div class="px-2 py-1.5 text-xs font-medium uppercase text-muted-foreground">Pages</div>'
       '<a class="menu-item" href="#"><i data-lucide="calendar-days"></i>Appointments</a><a class="menu-item" href="#"><i data-lucide="bar-chart-3"></i>Reports → No-shows</a><a class="menu-item" href="#"><i data-lucide="settings"></i>Settings → Branches</a>')
s = re.sub(r'(<div class="p-2 max-h-80 overflow-y-auto scroll-thin" id="palette-list">)[\s\S]*?(</div>\s*<div class="flex gap-4 px-4 py-2\.5 border-t)', lambda m: m.group(1) + pal + "\n  " + m.group(2), s, count=1)
must('<span class="kbd">Esc</span></div>', '<span class="kbd">Esc</span></div>')  # sanity anchor
open(path, "w", encoding="utf-8", newline="\n").write(s)
print("patch1 ok", len(s.encode("utf-8")), "bytes")
