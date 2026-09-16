"""Build a self-contained comparison report (HTML, screenshots embedded as data URIs).

Usage: python build_report.py report_data.json out.html
report_data.json:
{
  "title": "...", "subtitle": "...",
  "candidates": [ {"id": "jbelly", "label": "jbelly-ui", "shots": {"1440 light": "path.png", ...},
                   "metrics": {...}, "visual": {...}, "cost": {...}, "notes": "..."} ],
  "metric_rows": [["Label", "metrics.key" or "cost.key" or "visual.key", "hint"], ...],
  "sections": [ {"heading": "...", "html": "..."} ]
}
"""
import base64, json, sys, html, os

def data_uri(p):
    if not p or not os.path.exists(p): return ""
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()

def get(d, dotted):
    cur = d
    for k in dotted.split("."):
        if isinstance(cur, dict) and k in cur: cur = cur[k]
        else: return ""
    if isinstance(cur, bool): return "yes" if cur else "no"
    if isinstance(cur, float): return f"{cur:,.3f}".rstrip("0").rstrip(".")
    if isinstance(cur, int): return f"{cur:,}"
    if isinstance(cur, list): return ", ".join(map(str, cur))
    return str(cur)

def main():
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    cands = data["candidates"]
    css = """
    :root{--bg:#fff;--fg:#18181b;--muted:#71717a;--line:#e4e4e7;--card:#fff;--accent:#2563eb}
    @media(prefers-color-scheme:dark){:root{--bg:#0f0f11;--fg:#f4f4f5;--muted:#a1a1aa;--line:#27272a;--card:#141416}}
    body{margin:0;font:14px/1.5 system-ui,Segoe UI,Inter,sans-serif;background:var(--bg);color:var(--fg)}
    main{max-width:1500px;margin:0 auto;padding:28px 24px 80px}
    h1{font-size:26px;margin:0 0 4px}h2{font-size:18px;margin:36px 0 12px;padding-top:12px;border-top:1px solid var(--line)}h3{font-size:14px;margin:18px 0 8px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
    .sub{color:var(--muted);margin:0 0 18px}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
    figure{margin:0;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--card)}
    figure img{display:block;width:100%;height:auto}figcaption{padding:8px 10px;font-size:12px;color:var(--muted);border-top:1px solid var(--line)}
    table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
    th{color:var(--muted);font-weight:500}td.num{font-variant-numeric:tabular-nums;text-align:right}th.num{text-align:right}
    .hint{color:var(--muted);font-size:12px}.win{font-weight:600}
    .notes{white-space:pre-wrap;font-size:13px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
    details{border:1px solid var(--line);border-radius:10px;padding:8px 12px;margin:8px 0}summary{cursor:pointer;font-weight:600}
    """
    out = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(data['title'])}</title><style>{css}</style></head><body><main>"]
    out.append(f"<h1>{html.escape(data['title'])}</h1><p class='sub'>{html.escape(data.get('subtitle',''))}</p>")
    # screenshots by configuration
    configs = []
    for c in cands:
        for k in c["shots"]:
            if k not in configs: configs.append(k)
    out.append("<h2>Visual comparison</h2>")
    for cfg in configs:
        out.append(f"<h3>{html.escape(cfg)}</h3><div class='grid'>")
        for c in cands:
            p = c["shots"].get(cfg)
            if p and os.path.exists(p):
                out.append(f"<figure><img loading='lazy' src='{data_uri(p)}' alt='{html.escape(c['label'])} — {html.escape(cfg)}'><figcaption>{html.escape(c['label'])}</figcaption></figure>")
        out.append("</div>")
    # metrics table
    out.append("<h2>Analytics</h2><table><thead><tr><th>Metric</th>" + "".join(f"<th class='num'>{html.escape(c['label'])}</th>" for c in cands) + "<th>What it tells you</th></tr></thead><tbody>")
    for label, key, hint in data["metric_rows"]:
        if key == "":
            out.append(f"<tr><th colspan='{len(cands)+2}' style='padding-top:14px'>{html.escape(label)}</th></tr>"); continue
        out.append(f"<tr><td>{html.escape(label)}</td>" + "".join(f"<td class='num'>{html.escape(get(c, key))}</td>" for c in cands) + f"<td class='hint'>{html.escape(hint)}</td></tr>")
    out.append("</tbody></table>")
    # notes
    out.append("<h2>Each candidate's own notes</h2><div class='grid'>")
    for c in cands:
        out.append(f"<div><h3>{html.escape(c['label'])}</h3><div class='notes'>{html.escape(c.get('notes','') or '—')}</div></div>")
    out.append("</div>")
    for s in data.get("sections", []):
        out.append(f"<h2>{html.escape(s['heading'])}</h2>{s['html']}")
    out.append("</main></body></html>")
    open(sys.argv[2], "w", encoding="utf-8").write("".join(out))
    print("wrote", sys.argv[2], os.path.getsize(sys.argv[2]) // 1024, "KB")

if __name__ == "__main__":
    main()
