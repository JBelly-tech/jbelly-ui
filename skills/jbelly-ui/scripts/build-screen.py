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
  chart: { title, subtitle, series:[{name,data}], categories:[...] },
  highlights: { title, total_label, total, delta, items:[{label, value}] },
  table: { title, count, columns:[4 labels], rows:[{name, initials, sub, plan, status, time}] },
  activity: [ {who, text, when, primary} ],
  i18n: { ar: { "English": "العربية", ... } },
  extra_html: "<div class='card'>...</div>"   (appended as a full-width row after the table row)
"""
import json, os, re, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "assets", "app-shell.html")
EXAMPLE = os.path.join(ROOT, "assets", "spec.example.json")

def esc(x): return html.escape(str(x), quote=True)
def js(x): return json.dumps(x, ensure_ascii=False)

def region(s, name, new_inner):
    pat = re.compile(r"(<!-- @region " + name + r" -->\n)([\s\S]*?)(<!-- @endregion " + name + r" -->)")
    if not pat.search(s):
        print(f"WARN region {name} not found in template; skipped", file=sys.stderr); return s
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
        <div class="flex items-center gap-2.5">
          <select id="period" class="input select w-40">{opts}</select>
          <button class="btn btn-outline"><i data-lucide="download"></i><span data-i18n="{esc(sec)}">{esc(sec)}</span></button>
          <button class="btn btn-primary" data-toast="{esc(prim)}" data-toast-undo><i data-lucide="plus"></i><span data-i18n="{esc(prim)}">{esc(prim)}</span></button>
        </div>
      </div>
'''

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

def main():
    if "--example" in sys.argv:
        print(open(EXAMPLE, encoding="utf-8").read()); return
    spec = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
    s = open(TEMPLATE, encoding="utf-8").read()
    product = spec.get("product", "Product"); title = spec.get("title", "Dashboard")
    classes = " ".join(c for c in ["h-full", spec.get("theme", ""), spec.get("density", ""), "dark" if spec.get("dark") else ""] if c)
    s = s.replace('<html lang="en" dir="ltr" class="h-full">', f'<html lang="{esc(spec.get("lang","en"))}" dir="{esc(spec.get("dir","ltr"))}" class="{classes}">')
    s = s.replace("<title>jbelly-ui — app shell</title>", f"<title>{esc(product)} — {esc(title)}</title>")
    s = s.replace("Nutrio Clinic", esc(product))
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
        s = s.replace('data-i18n="Appointments per week">Appointments per week</h3>', f'data-i18n="{esc(ch.get("title","Trend"))}">{esc(ch.get("title","Trend"))}</h3>')
        names = [x["name"] for x in ch.get("series", [])][:2]
        if len(names) == 2:
            s = s.replace('data-i18n="Completed">Completed</span>', f'data-i18n="{esc(names[0])}">{esc(names[0])}</span>')
            s = s.replace('data-i18n="No-show">No-show</span>', f'data-i18n="{esc(names[1])}">{esc(names[1])}</span>')
        s = re.sub(r"series: \[\{ name: 'Completed', data: \[[^\]]*\] \}, \{ name: 'No-show', data: \[[^\]]*\] \}\]",
                   "series: " + js([{"name": x["name"], "data": x["data"]} for x in ch.get("series", [])]), s, count=1)
        if ch.get("categories"):
            s = re.sub(r"categories: \['W1'[^\]]*\]", "categories: " + js(ch["categories"]), s, count=1)
            ymax = max(max(x["data"]) for x in ch.get("series", []) if x.get("data")) if ch.get("series") else 100
            import math
            m = ymax * 1.15; step = 10 ** max(0, int(math.floor(math.log10(max(m, 1))))); step = step if m / step >= 4 else step / 2
            nice = int(math.ceil(m / step) * step)
            s = s.replace("{ min: 0, max: 100, tickAmount: 4 }", "{ min: 0, max: %d, tickAmount: 4 }" % nice)
    hl = spec.get("highlights")
    if hl and hl.get("items"):
        items = hl["items"]; total = sum(int(str(i.get("value", 0)).replace(",", "")) for i in items)
        s = s.replace('data-i18n="Highlights">Highlights</h3>', f'data-i18n="{esc(hl.get("title","Highlights"))}">{esc(hl.get("title","Highlights"))}</h3>')
        s = s.replace('data-i18n="Plans completed">Plans completed</span>', f'data-i18n="{esc(hl.get("total_label","Total"))}">{esc(hl.get("total_label","Total"))}</span>')
        s = s.replace('<span class="text-2xl font-semibold text-mono tabular-nums font-display">214</span>', f'<span class="text-2xl font-semibold text-mono tabular-nums font-display">{esc(hl.get("total", total))}</span>')
        s = re.sub(r"series: \[98, 58, 36, 22\], labels: \[[^\]]*\]", "series: " + js([int(str(i.get("value", 0)).replace(",", "")) for i in items]) + ", labels: " + js([i["label"] for i in items]), s, count=1)
        dots = ["bg-primary", "bg-info", "bg-success", "bg-warning", "bg-muted-foreground"]
        legend = "\n".join(f'                <div class="flex justify-between"><span class="flex items-center gap-2"><span class="size-2 rounded-full {dots[i % 5]}"></span><span data-i18n="{esc(it["label"])}">{esc(it["label"])}</span></span><span class="text-mono font-medium tabular-nums">{esc(it.get("value",""))}</span></div>' for i, it in enumerate(items))
        s = re.sub(r'<div class="flex flex-col gap-2.5 text-2sm">[\s\S]*?</div>\n            </div>\n            <div class="card-footer justify-center">',
                   '<div class="flex flex-col gap-2.5 text-2sm">\n' + legend + '\n              </div>\n            </div>\n            <div class="card-footer justify-center">', s, count=1)
    tb = spec.get("table")
    if tb:
        s = s.replace('data-i18n="Upcoming appointments">Upcoming appointments</h3><span class="badge badge-sm badge-outline">24</span>',
                      f'data-i18n="{esc(tb.get("title","Records"))}">{esc(tb.get("title","Records"))}</h3><span class="badge badge-sm badge-outline">{esc(tb.get("count", len(tb.get("rows", []))))}</span>')
        cols = tb.get("columns")
        if cols and len(cols) == 4:
            for old, new in zip(["Patient", "Plan", "Status", "Time"], cols):
                s = s.replace(f'data-i18n="{old}">{old}', f'data-i18n="{esc(new)}">{esc(new)}', 1)
        if tb.get("rows"):
            rows = [{"n": r.get("name", ""), "i": r.get("initials", "".join(w[0] for w in r.get("name", "??").split()[:2]).upper()), "p": r.get("plan", r.get("sub", "")), "s": r.get("status", ""), "t": r.get("time", "")} for r in tb["rows"]]
            s = re.sub(r"const rows = \[[\s\S]*?\n\];", "const rows = " + js(rows) + ";", s, count=1)
            s = s.replace("<span>1–5 of 24</span>", f"<span>1–{min(5, len(rows))} of {tb.get('count', len(rows))}</span>")
    act = spec.get("activity")
    if act:
        items = []
        for i, a in enumerate(act):
            last = i == len(act) - 1
            dot = "bg-primary" if a.get("primary") or i == 0 else "bg-muted-foreground"
            items.append(f'''              <div class="relative flex gap-3 {"" if last else "pb-6 "}ps-6{"" if last else " before:absolute before:start-2 before:top-6 before:bottom-0 before:w-px before:bg-border"}"><span class="absolute start-0 top-1 size-4 rounded-full border-2 border-background {dot}"></span><div class="flex flex-col gap-1"><p class="text-2sm"><span class="font-medium text-mono">{esc(a.get("who",""))}</span> {esc(a.get("text",""))}</p><span class="text-xs text-muted-foreground">{esc(a.get("when",""))}</span></div></div>''')
        s = re.sub(r'(<div class="card-content flex flex-col">\n)[\s\S]*?(\n            </div>\n          </div>\n        </div>\n<!-- @endregion row3 -->)', lambda m: m.group(1) + "\n".join(items) + m.group(2), s, count=1)
    if spec.get("extra_html"):
        s = s.replace("<!-- @endregion row3 -->", spec["extra_html"] + "\n<!-- @endregion row3 -->")
    if spec.get("i18n", {}).get("ar"):
        s = re.sub(r"const I18N = (\{[\s\S]*?\});", lambda m: "const I18N = " + js({**json.loads(m.group(1)), **spec["i18n"]["ar"]}) + ";", s, count=1)
    # remove demo controls unless asked to keep them
    if not spec.get("keep_demo_controls"):
        s = re.sub(r"(?s)<!-- ===== Demo controls.*?</details>\s*", "", s)
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8", newline="\n").write(s)
    print(f"built {out} ({len(s.encode('utf-8')):,} bytes) from spec: nav={len(spec.get('nav',[]))} kpis={len(spec.get('kpis',[]))} rows={len((spec.get('table') or {}).get('rows',[]))}")

if __name__ == "__main__":
    main()
