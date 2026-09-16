"""patch2: behaviour (JS) on top of the scaffold script. Usage: python patch2.py spec.json dashboard.html"""
import json, re, sys
spec = json.load(open(sys.argv[1], encoding="utf-8")); path = sys.argv[2]
s = open(path, encoding="utf-8").read()
js = lambda x: json.dumps(x, ensure_ascii=False)
def sub(pat, new, flags=0):
    global s
    assert re.search(pat, s, flags), "anchor missing: " + pat[:70]
    s = re.sub(pat, lambda m: new, s, count=1, flags=flags)
def must(old, new):
    global s
    assert old in s, "anchor missing: " + old[:70]
    s = s.replace(old, new, 1)

rows = [{"n": r["name"], "i": "".join(w[0] for w in r["name"].split()[:2]).upper(), "p": r.get("plan", ""), "sub": r.get("sub", ""), "s": r["status"], "t": r["time"], "b": r.get("branch", ""), "d": r.get("dietitian", "")} for r in spec["table"]["rows"]]
sub(r"const rows = \[[\s\S]*?\];", "const rows = " + js(rows) + ";")
must("const badge = s => ({ 'Confirmed': 'badge-light-success', 'Pending': 'badge-light-warning', 'No-show risk': 'badge-light-destructive' }[s] || 'badge-outline');",
     "const badge = s => ({ 'Confirmed': 'badge-light-success', 'Pending': 'badge-light-warning', 'No-show risk': 'badge-light-destructive', 'Cancelled': 'badge-outline' }[s] || 'badge-outline');\n"
     "const badgeHtml = st => `<span class=\"badge badge-sm ${badge(st)}\"><span class=\"dot\"></span><span data-i18n=\"${st}\">${(html.lang === 'ar' && I18N[st]) || st}</span></span>`;")

# ---- table engine: search, chips, sort (3 states), columns, pagination, 4 states ----
TABLE = r"""
const COLS = ['n', 'p', 'b', 'd', 's', 't'];
const T = { q: '', status: 'All', sortK: null, sortDir: 0, page: 1, size: 10, hidden: new Set(['d']), state: 'data' };
const searched = () => rows.map((r, k) => Object.assign({ k }, r)).filter(r => !T.q || [r.n, r.p, r.b, r.d, r.s, r.t].join(' ').toLowerCase().includes(T.q));
function view() { let v = searched().filter(r => T.status === 'All' || r.s === T.status);
  if (T.sortDir) v.sort((a, b) => String(a[T.sortK]).localeCompare(String(b[T.sortK]), undefined, { numeric: true }) * T.sortDir); return v; }
function rowHtml(r) { const c = k => T.hidden.has(k) ? ' hidden' : '';
  return `<tr class="group" data-i="${r.k}">
    <td class="text-center"><input type="checkbox" class="checkbox row-check" aria-label="Select ${r.n}"></td>
    <td><div class="flex items-center gap-2.5"><span class="inline-flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary font-semibold text-2xs">${r.i}</span><div class="flex flex-col min-w-0"><a href="#" class="text-sm font-medium text-mono hover:text-primary truncate" data-open-drawer="${r.k}">${r.n}</a><span class="text-xs text-secondary-foreground truncate">${r.sub}</span></div></div></td>
    <td class="text-secondary-foreground whitespace-nowrap${c('p')}">${r.p}</td>
    <td class="text-secondary-foreground whitespace-nowrap${c('b')}">${r.b}</td>
    <td class="text-secondary-foreground whitespace-nowrap${c('d')}">${r.d}</td>
    <td class="${c('s').trim()}">${badgeHtml(r.s)}</td>
    <td class="text-secondary-foreground whitespace-nowrap font-mono tabular-nums text-xs${c('t')}">${r.t}</td>
    <td class="text-end"><div class="flex justify-end gap-0.5 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity"><button class="btn btn-ghost btn-icon btn-sm" aria-label="Open ${r.n}" data-open-drawer="${r.k}"><i data-lucide="panel-right-open"></i></button><button class="btn btn-ghost btn-icon btn-sm" aria-label="Send reminder to ${r.n}" data-toast="Reminder sent to ${r.n}"><i data-lucide="mail"></i></button></div></td></tr>`; }
function renderRows() {
  const v = view(), total = v.length, pages = Math.max(1, Math.ceil(total / T.size)); T.page = Math.min(T.page, pages);
  const slice = v.slice((T.page - 1) * T.size, T.page * T.size), tb = $('#tbody');
  tb.innerHTML = total ? slice.map(rowHtml).join('') : emptyHtml('No appointments match', 'Try another status or clear the search.', 'Clear filters', 'clear-filters');
  $('#page-info').textContent = `${total ? (T.page - 1) * T.size + 1 : 0}–${Math.min(T.page * T.size, total)} of ${total}`;
  $('#pager').innerHTML = `<button class="inline-flex size-7 items-center justify-center rounded-md text-xs text-secondary-foreground hover:bg-accent disabled:opacity-50" data-page="${T.page - 1}" aria-label="Previous"${T.page === 1 ? ' disabled' : ''}><i data-lucide="chevron-left" class="size-4 rtl:rotate-180"></i></button>` +
    Array.from({ length: pages }, (_, i) => `<button class="inline-flex size-7 items-center justify-center rounded-md text-xs ${i + 1 === T.page ? 'bg-accent text-mono font-medium' : 'text-secondary-foreground hover:bg-accent'}" data-page="${i + 1}"${i + 1 === T.page ? ' aria-current="page"' : ''}>${i + 1}</button>`).join('') +
    `<button class="inline-flex size-7 items-center justify-center rounded-md text-xs text-secondary-foreground hover:bg-accent disabled:opacity-50" data-page="${T.page + 1}" aria-label="Next"${T.page === pages ? ' disabled' : ''}><i data-lucide="chevron-right" class="size-4 rtl:rotate-180"></i></button>`;
  const base = searched(), counts = {}; base.forEach(r => counts[r.s] = (counts[r.s] || 0) + 1);
  $('#chips').innerHTML = ['All', 'Confirmed', 'Pending', 'No-show risk', 'Cancelled'].map(st => { const on = T.status === st, n = st === 'All' ? base.length : counts[st] || 0;
    return `<button type="button" class="inline-flex items-center gap-1.5 h-6 px-2 rounded-md text-xs border transition-colors ${on ? 'bg-primary/10 text-primary border-primary/30 font-medium' : 'bg-muted text-secondary-foreground border-border hover:bg-accent'}" data-chip="${st}" aria-pressed="${on}"><span data-i18n="${st}">${(html.lang === 'ar' && I18N[st]) || st}</span><span class="tabular-nums opacity-70">${n}</span></button>`; }).join('');
  $$('#appt-table th[data-col]').forEach(th => { th.classList.toggle('hidden', T.hidden.has(th.dataset.col)); const on = T.sortK === th.dataset.col && T.sortDir;
    th.setAttribute('aria-sort', on ? (T.sortDir > 0 ? 'ascending' : 'descending') : 'none'); th.querySelector('.sort-icon').outerHTML = `<i data-lucide="${on ? (T.sortDir > 0 ? 'chevron-up' : 'chevron-down') : 'chevrons-up-down'}" class="size-3.5 ${on ? 'text-primary' : 'text-muted-foreground'} sort-icon"></i>`; });
  $('#check-all').checked = false; syncBulk(); lucide.createIcons();
}
const emptyHtml = (t, d, b, act, icon = 'calendar-x') => `<tr><td colspan="8"><div class="flex flex-col items-center justify-center text-center gap-3 py-12"><span class="inline-flex size-12 items-center justify-center rounded-full bg-muted text-muted-foreground"><i data-lucide="${icon}" class="size-5"></i></span><span class="text-sm font-semibold text-mono">${t}</span><span class="text-2sm text-secondary-foreground max-w-xs">${d}</span><button class="btn btn-outline btn-sm" data-state="data" data-act="${act}">${b}</button></div></td></tr>`;
function renderState(state) {
  const tb = $('#tbody'); T.state = state;
  if (state === 'loading') tb.innerHTML = Array.from({ length: 5 }, () => `<tr><td class="text-center"><span class="skeleton inline-block size-4"></span></td><td><div class="flex items-center gap-2.5"><span class="skeleton size-8 rounded-full"></span><div class="flex flex-col gap-1.5"><span class="skeleton h-3 w-32"></span><span class="skeleton h-2.5 w-20"></span></div></div></td><td><span class="skeleton h-3 w-20 inline-block"></span></td><td><span class="skeleton h-3 w-16 inline-block"></span></td><td class="hidden"></td><td><span class="skeleton h-5 w-16 inline-block"></span></td><td><span class="skeleton h-3 w-16 inline-block"></span></td><td></td></tr>`).join('');
  else if (state === 'empty') tb.innerHTML = emptyHtml('No appointments match', 'Try another status or clear the search.', 'Clear filters', 'clear-filters');
  else if (state === 'error') tb.innerHTML = emptyHtml('Couldn’t load appointments', 'The scheduling service returned 503. Your filters are kept.', 'Retry', 'retry', 'circle-alert');
  else { renderRows(); return; }
  lucide.createIcons(); syncTabs(state);
}
function syncTabs(state) { $$('[role=tab][data-state]').forEach(b => { const on = b.dataset.state === state; b.className = on ? 'h-6 px-2.5 rounded-md text-xs bg-background text-mono shadow-xs font-medium' : 'h-6 px-2.5 rounded-md text-xs text-secondary-foreground hover:text-foreground'; b.setAttribute('aria-selected', on); }); }
function syncBulk() { const n = $$('.row-check:checked').length; $('#sel-count').textContent = n; $('#bulk-bar').classList.toggle('hidden', n === 0); $('#table-toolbar').classList.toggle('hidden', n > 0); }
document.addEventListener('click', e => {
  const st = e.target.closest('[data-state]'); if (st) { if (st.dataset.act === 'clear-filters') { T.q = ''; T.status = 'All'; $('#tbl-search').value = ''; } if (st.dataset.state === 'data') syncTabs('data'); renderState(st.dataset.state); return; }
  const chip = e.target.closest('[data-chip]'); if (chip) { T.status = chip.dataset.chip; T.page = 1; renderRows(); return; }
  const so = e.target.closest('[data-sort]'); if (so) { const k = so.dataset.sort; if (T.sortK !== k) { T.sortK = k; T.sortDir = 1; } else T.sortDir = T.sortDir === 1 ? -1 : T.sortDir === -1 ? 0 : 1; renderRows(); return; }
  const pg = e.target.closest('[data-page]'); if (pg && !pg.disabled) { T.page = +pg.dataset.page; renderRows(); return; }
  const tr = e.target.closest('#tbody tr[data-i]'); if (tr && !e.target.closest('input,button,a')) openDrawer(+tr.dataset.i);
});
$('#tbl-search').addEventListener('input', e => { T.q = e.target.value.trim().toLowerCase(); T.page = 1; renderRows(); });
$('#page-size').onchange = e => { T.size = +e.target.value; T.page = 1; renderRows(); };
$('#tbl-density').onclick = e => { const b = e.currentTarget, on = b.getAttribute('aria-pressed') !== 'true'; b.setAttribute('aria-pressed', on); $('#appt-table').classList.toggle('table-compact', on); };
$$('.col-toggle').forEach(c => c.onchange = () => { c.checked ? T.hidden.delete(c.dataset.col) : T.hidden.add(c.dataset.col); renderRows(); });
"""
sub(r"function renderRows\(\) \{[\s\S]*?document\.addEventListener\('click', e => \{ const b = e\.target\.closest\('\[data-state\]'\); if \(b\) renderState\(b\.dataset\.state\); \}\);", TABLE.strip())

# ---- popovers (branch, columns), bulk actions, confirm modal ----
POPS = r"""
// popovers
function closePops() { $$('.menu[data-pop]').forEach(m => { m.classList.add('hidden'); m.previousElementSibling?.setAttribute('aria-expanded', 'false'); }); }
$$('.menu[data-pop]').forEach(m => { const b = m.previousElementSibling; b.onclick = e => { e.stopPropagation(); const open = m.classList.contains('hidden'); closePops(); m.classList.toggle('hidden', !open); b.setAttribute('aria-expanded', open); if (open) m.querySelector('button,input')?.focus(); }; m.onclick = e => e.stopPropagation(); });
document.addEventListener('click', closePops);
function setBranch(b) { $('#branch-label').textContent = (html.lang === 'ar' && I18N[b]) || b; $('#branch-btn-label').textContent = (html.lang === 'ar' && I18N[b]) || b; $('#branch-filter').value = [...$('#branch-filter').options].find(o => o.dataset.i18n === b)?.value ?? b;
  $$('#branch-menu [data-branch]').forEach(x => { const on = x.dataset.branch === b; x.setAttribute('aria-checked', on); x.querySelector('.branch-check')?.classList.toggle('hidden', !on); }); closePops(); }
document.addEventListener('click', e => { const b = e.target.closest('[data-branch]'); if (b) setBranch(b.dataset.branch); });
$('#branch-filter').onchange = e => setBranch(e.target.selectedOptions[0].dataset.i18n);
// bulk actions + confirm modal
const selected = () => $$('.row-check:checked').map(c => +c.closest('tr').dataset.i);
let lastFocus2 = null;
function openConfirm(n) { lastFocus2 = document.activeElement; $('#confirm-n').textContent = n; $('#confirm').classList.remove('hidden'); $('#confirm').classList.add('flex'); $('#confirm-overlay').classList.remove('hidden'); $('#confirm-no').focus(); }
function closeConfirm() { $('#confirm').classList.add('hidden'); $('#confirm').classList.remove('flex'); $('#confirm-overlay').classList.add('hidden'); lastFocus2?.focus(); }
$('#confirm-no').onclick = closeConfirm; $('#confirm-overlay').onclick = closeConfirm;
$('#confirm-yes').onclick = () => { const ks = selected(), prev = ks.map(k => rows[k].s); ks.forEach(k => rows[k].s = 'Cancelled'); closeConfirm(); renderRows();
  toast(`${ks.length} appointments cancelled`, true, () => { ks.forEach((k, i) => rows[k].s = prev[i]); renderRows(); }); };
document.addEventListener('click', e => { const b = e.target.closest('[data-bulk]'); if (!b) return; const n = selected().length;
  if (b.dataset.bulk === 'clear') { $$('.row-check').forEach(c => { c.checked = false; c.closest('tr').classList.remove('selected'); }); syncBulk(); }
  else if (b.dataset.bulk === 'remind') { toast(`Reminder sent to ${n} patients`, true, () => toast('Reminders recalled')); $('[data-bulk=clear]').click(); }
  else if (b.dataset.bulk === 'reschedule') { toast(`${n} appointments moved to the next free slot`, true, () => toast('Reschedule reverted')); $('[data-bulk=clear]').click(); }
  else if (b.dataset.bulk === 'cancel') openConfirm(n); });
"""
must("// KPI count-up (signature moment; skipped under reduced motion)", POPS.strip() + "\n// KPI count-up (signature moment; skipped under reduced motion)")

# ---- drawer with tabs + measurement chart; notifications drawer ----
M = spec["measurements"]
DRAWER = r"""
let lastFocus = null, curRow = 0, measureChart = null;
const MEAS = %s;
const TAB_ON = '-mb-px pb-2.5 text-sm border-b-2 text-primary border-primary font-medium', TAB_OFF = '-mb-px pb-2.5 text-sm border-b-2 border-transparent text-secondary-foreground hover:text-foreground';
function openDrawer(k) { const r = rows[k]; if (!r) return; lastFocus = document.activeElement; curRow = k;
  $('#drawer-name').textContent = r.n; $('#drawer-initials').textContent = r.i; $('#drawer-plan').textContent = r.sub; $('#drawer-time').textContent = r.t; $('#drawer-branch').textContent = r.b; $('#drawer-diet').textContent = r.d;
  $('#drawer-status').innerHTML = badgeHtml(r.s); $('#note').value = r.note || '';
  $('#drawer').classList.remove('hidden'); $('#drawer-overlay').classList.remove('hidden'); document.body.style.overflow = 'hidden'; showDtab('overview'); $('#drawer [data-dtab="overview"]').focus(); }
function showDtab(t) { $$('#drawer [data-dtab]').forEach(b => { const on = b.dataset.dtab === t; b.className = on ? TAB_ON : TAB_OFF; b.setAttribute('aria-selected', on); });
  ['overview', 'measure', 'notes'].forEach(x => { const p = $('#dtab-' + x); p.classList.toggle('hidden', x !== t); p.classList.toggle('flex', x === t); });
  if (t === 'measure') mountMeasure(); if (t === 'notes') $('#note').focus(); }
function mountMeasure() { measureChart?.destroy(); const base = apexBase();
  measureChart = new ApexCharts($('#chart-measure'), Object.assign({}, base, { chart: Object.assign({}, base.chart, { type: 'line', height: 160 }), series: [{ name: 'Weight (kg)', data: MEAS.data }],
    xaxis: Object.assign({}, base.xaxis, { categories: MEAS.labels }), yaxis: Object.assign({}, base.yaxis, { tickAmount: 3, labels: { style: { fontSize: '11px' }, formatter: v => v.toFixed(1) } }), markers: { size: 3, strokeWidth: 0 }, stroke: { curve: 'smooth', width: 2 } })); measureChart.render(); }
function closeDrawer() { $('#drawer').classList.add('hidden'); $('#drawer-overlay').classList.add('hidden'); document.body.style.overflow = ''; measureChart?.destroy(); measureChart = null; lastFocus?.focus(); }
document.addEventListener('click', e => { const o = e.target.closest('[data-open-drawer]'); if (o) { e.preventDefault(); openDrawer(+o.dataset.openDrawer); } if (e.target.closest('[data-close-drawer]')) closeDrawer(); if (e.target.closest('[data-close-notif]')) closeNotif();
  const t = e.target.closest('[data-dtab]'); if (t) showDtab(t.dataset.dtab); });
$('#save-note').onclick = () => { rows[curRow].note = $('#note').value; closeDrawer(); toast('Note saved'); };
$('#drawer-overlay').onclick = () => { closeDrawer(); closeNotif(); };
// notifications
const NOTIFS = %s; let ntab = 'all';
function renderNotifs() { const unread = NOTIFS.filter(n => n.unread).length; $('#notif-count').textContent = unread; $('#notif-dot').classList.toggle('hidden', !unread); $('#notif-btn').setAttribute('aria-label', `Notifications, ${unread} unread`);
  $('#notif-list').innerHTML = NOTIFS.map((n, i) => ntab !== 'all' && n.group !== ntab ? '' : `<button type="button" class="flex items-start gap-3 rounded-md px-2.5 py-2.5 text-start hover:bg-accent w-full" data-notif="${i}"><span class="mt-1.5 size-2 rounded-full shrink-0 ${n.unread ? 'bg-primary' : 'bg-transparent'}" aria-hidden="true"></span><span class="flex flex-col gap-0.5 min-w-0"><span class="text-2sm ${n.unread ? 'font-medium text-mono' : 'text-foreground'}">${n.title}${n.unread ? '<span class="sr-only"> (unread)</span>' : ''}</span><span class="text-xs text-secondary-foreground">${n.text}</span><span class="text-2xs font-mono text-muted-foreground">${n.when}</span></span></button>`).join('') || `<div class="flex flex-col items-center gap-2 py-10 text-center"><i data-lucide="bell-off" class="size-5 text-muted-foreground"></i><span class="text-2sm text-secondary-foreground">Nothing here yet.</span></div>`;
  $$('[data-ntab]').forEach(b => { const on = b.dataset.ntab === ntab; b.className = 'h-7 px-3 rounded-md text-xs ' + (on ? 'bg-background text-mono shadow-xs font-medium' : 'text-secondary-foreground hover:text-foreground'); b.setAttribute('aria-selected', on); }); lucide.createIcons(); }
function openNotif() { lastFocus = document.activeElement; renderNotifs(); $('#notif').classList.remove('hidden'); $('#notif').classList.add('flex'); $('#drawer-overlay').classList.remove('hidden'); document.body.style.overflow = 'hidden'; $('#notif [data-ntab="all"]').focus(); }
function closeNotif() { if ($('#notif').classList.contains('hidden')) return; $('#notif').classList.add('hidden'); $('#notif').classList.remove('flex'); $('#drawer-overlay').classList.add('hidden'); document.body.style.overflow = ''; lastFocus?.focus(); }
$('#notif-btn').onclick = openNotif; $('#notif-read-all').onclick = () => { NOTIFS.forEach(n => n.unread = false); renderNotifs(); toast('All notifications marked as read'); };
document.addEventListener('click', e => { const t = e.target.closest('[data-ntab]'); if (t) { ntab = t.dataset.ntab; renderNotifs(); } const n = e.target.closest('[data-notif]'); if (n) { NOTIFS[+n.dataset.notif].unread = false; renderNotifs(); } });
renderNotifs();
""" % (js(M), js(spec["notifications"]))
sub(r"let lastFocus = null;\nfunction openDrawer\(k\)[\s\S]*?\$\('#drawer-overlay'\)\.onclick = closeDrawer;", DRAWER.strip())

# ---- palette keyboard nav; keydown: Esc order, focus trap, kanban keys ----
must("$('#palette-input').addEventListener('input', e => { const q = e.target.value.toLowerCase(); $$('#palette-list .menu-item').forEach(i => i.classList.toggle('hidden', q && !i.textContent.toLowerCase().includes(q))); });",
     "$('#palette-input').addEventListener('input', e => { const q = e.target.value.toLowerCase(); $$('#palette-list .menu-item').forEach(i => { i.classList.toggle('hidden', q && !i.textContent.toLowerCase().includes(q)); i.classList.remove('palette-active'); }); $$('#palette-list > div').forEach(h => { let n = h.nextElementSibling, any = false; while (n && n.tagName === 'A') { any = any || !n.classList.contains('hidden'); n = n.nextElementSibling; } h.classList.toggle('hidden', !any); }); });\n"
     "$('#palette-input').addEventListener('keydown', e => { const items = $$('#palette-list .menu-item:not(.hidden)'); let i = items.findIndex(x => x.classList.contains('palette-active'));\n"
     "  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); items.forEach(x => x.classList.remove('palette-active')); i = e.key === 'ArrowDown' ? (i + 1) % items.length : (i - 1 + items.length) % items.length; items[i]?.classList.add('palette-active'); items[i]?.scrollIntoView({ block: 'nearest' }); }\n"
     "  if (e.key === 'Enter' && items.length) { e.preventDefault(); const it = items[Math.max(i, 0)]; closePalette(); toast('Opened: ' + it.textContent.trim().replace(/\\s+/g, ' ')); } });")
KEYS = r"""
const isOpen = sel => !$(sel).classList.contains('hidden');
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); openPalette(); }
  if (e.key === 'Escape') { if (isOpen('#confirm')) closeConfirm(); else if (isOpen('#palette')) closePalette(); else if (isOpen('#notif')) closeNotif(); else if (isOpen('#drawer')) closeDrawer(); else { um.classList.add('hidden'); ub.setAttribute('aria-expanded', 'false'); closePops(); } }
  if (e.key === 'Tab') { const box = ['#confirm', '#palette', '#notif', '#drawer'].map(x => $(x)).find(el => !el.classList.contains('hidden')); if (box) { const f = $$('a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]:not([tabindex="-1"])', box).filter(x => x.offsetParent !== null); if (!f.length) return;
    if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); } else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); } } }
  if (e.altKey && (e.key === 'ArrowLeft' || e.key === 'ArrowRight') && e.target.classList?.contains('kb-card')) { e.preventDefault(); moveCard(e.target, (e.key === 'ArrowRight') === (html.dir !== 'rtl') ? 1 : -1); }
});
// kanban drag + keyboard
let dragEl = null;
document.addEventListener('dragstart', e => { const c = e.target.closest?.('.kb-card'); if (!c) return; dragEl = c; c.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', 'card'); });
document.addEventListener('dragend', () => { dragEl?.classList.remove('dragging'); $$('.kb-col.over').forEach(c => c.classList.remove('over')); dragEl = null; });
document.addEventListener('dragover', e => { const col = e.target.closest?.('.kb-col'); if (col && dragEl) { e.preventDefault(); $$('.kb-col.over').forEach(c => c !== col && c.classList.remove('over')); col.classList.add('over'); } });
document.addEventListener('drop', e => { const col = e.target.closest?.('.kb-col'); if (col && dragEl) { e.preventDefault(); col.querySelector('.kb-cards').appendChild(dragEl); kbCounts(); } });
function moveCard(card, dir) { const cols = $$('.kb-col'), i = cols.indexOf(card.closest('.kb-col')), to = cols[i + dir]; if (!to) return; to.querySelector('.kb-cards').appendChild(card); card.focus(); kbCounts(); toast(`${card.querySelector('.text-mono').textContent} moved to ${to.dataset.col}`); }
function kbCounts() { $$('.kb-col').forEach(c => c.querySelector('.kb-count').textContent = c.querySelectorAll('.kb-card').length); }
"""
sub(r"document\.addEventListener\('keydown', e => \{\n  if \(\(e\.ctrlKey[\s\S]*?\n\}\);", KEYS.strip())

# ---- toasts with undo callback; period + compare; header toggles; prefs; url presets ----
sub(r"function toast\(msg, undo\) \{[\s\S]*?while \(\$\('#toasts'\)\.children\.length > 3\) \$\('#toasts'\)\.firstChild\.remove\(\); \}",
    r"""function toast(msg, undo, onUndo) { const el = document.createElement('div');
  el.className = 'flex items-start gap-2.5 rounded-lg border border-border bg-popover text-popover-foreground shadow-md p-3.5 text-sm';
  el.innerHTML = `<i data-lucide="check-circle-2" class="size-4 mt-0.5 text-success shrink-0"></i><div class="grow"><div class="font-medium text-mono">${msg}</div><div class="text-2sm text-secondary-foreground">${undo ? 'You can undo this for 5 seconds.' : 'Done.'}</div></div>${undo ? '<button class="btn btn-ghost btn-sm" data-undo>Undo</button>' : ''}<button class="btn btn-ghost btn-icon btn-sm" aria-label="Dismiss"><i data-lucide="x"></i></button>`;
  $('#toasts').appendChild(el); lucide.createIcons(); let t = setTimeout(() => el.remove(), undo ? 5000 : 4000);
  el.addEventListener('mouseenter', () => clearTimeout(t)); el.addEventListener('mouseleave', () => t = setTimeout(() => el.remove(), 2000));
  $$('button', el).forEach(b => b.onclick = () => { if (b.hasAttribute('data-undo') && onUndo) onUndo(); el.remove(); }); while ($('#toasts').children.length > 3) $('#toasts').firstChild.remove(); }""")
must("$('#period').onchange = e => $('#period-label').textContent = e.target.value;",
     "$('#period').onchange = e => { const o = e.target.selectedOptions[0]; $('#period-label').textContent = o.textContent; const custom = (o.dataset.i18n || '').startsWith('Custom'); $('#custom-range').classList.toggle('hidden', !custom); $('#custom-range').classList.toggle('flex', custom); };\n"
     "$('#compare').onchange = e => $$('#kpis .badge').forEach(b => b.classList.toggle('invisible', !e.target.checked));\n"
     "setInterval(() => { const u = $('#updated'); u.textContent = +u.textContent + 1; }, 60000);\n"
     "function syncLangBtn() { $('#lang-toggle span').textContent = html.dir === 'rtl' ? 'EN' : 'AR'; }\n"
     "$('#lang-toggle').onclick = () => setLang(html.dir === 'rtl' ? 'en' : 'ar');\n"
     "function setDensity(compact, persist = true) { html.classList.toggle('density-compact', compact); $('#density-toggle').setAttribute('aria-pressed', compact); if (persist) try { localStorage.setItem('ui.density', compact ? 'compact' : 'standard'); } catch {} }\n"
     "$('#density-toggle').onclick = () => setDensity(!html.classList.contains('density-compact'));\n"
     "try { const d = localStorage.getItem('ui.density'); if (d) setDensity(d === 'compact', false); } catch {}")
sub(r"\(function fromUrl\(\) \{[\s\S]*?setTimeout\(\(\) => renderState\(q\.get\('state'\)\), 0\); \}\)\(\);",
    r"""(function fromUrl() { const q = new URLSearchParams(location.search || location.hash.slice(1));
  if (q.get('dark') === '1') html.classList.add('dark'); if (q.get('dark') === '0') html.classList.remove('dark');
  const d = q.get('density'); if (d) setDensity(d === 'compact' || d === 'density-compact', false);
  if (q.get('dir') === 'rtl' || q.get('lang') === 'ar') setLang('ar');
  if (q.get('state')) setTimeout(() => renderState(q.get('state')), 0); })();
syncLangBtn();""")
must("new MutationObserver(() => {", "new MutationObserver(() => { syncLangBtn(); if (T.state === 'data' && !$('#tbody').querySelector('.skeleton')) renderRows();")

# ---- charts: legend toggle, dashed series, donut label, capacity bars, heatmap ----
cap = spec["capacity"]; hm = spec["heatmap"]
must("const charts = [];", "const charts = []; let chartVisits = null; const hiddenSeries = new Set();\n"
     "const _cv = document.createElement('canvas').getContext('2d');\n"
     "function toHex(c) { _cv.fillStyle = '#000'; _cv.fillStyle = c; return _cv.fillStyle; }\n"
     "function mix(a, b, t) { const A = a.match(/\\w\\w/g).map(x => parseInt(x, 16)), B = b.match(/\\w\\w/g).map(x => parseInt(x, 16)); return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, '0')).join(''); }\n"
     "document.addEventListener('click', e => { const b = e.target.closest('.legend-btn'); if (!b || !chartVisits) return; const on = b.getAttribute('aria-pressed') !== 'true'; b.setAttribute('aria-pressed', on); on ? hiddenSeries.delete(b.dataset.series) : hiddenSeries.add(b.dataset.series); on ? chartVisits.showSeries(b.dataset.series) : chartVisits.hideSeries(b.dataset.series); });")
must("charts.push(new ApexCharts($('#chart-visits'),", "charts.push(chartVisits = new ApexCharts($('#chart-visits'),")
must("    markers: { size: 0, hover: { size: 5 } },\n  })));", "    markers: { size: 0, hover: { size: 5 } }, stroke: Object.assign({}, base.stroke, { dashArray: [0, 5, 2] }),\n  })));")
must("total: { show: true, label: 'Plans',", "total: { show: true, label: 'Patients',")
CHARTS = r"""
  const prim = toHex(cssVar('--primary')), card = toHex(cssVar('--card')), fg = toHex(cssVar('--foreground'));
  if ($('#chart-capacity')) charts.push(new ApexCharts($('#chart-capacity'), Object.assign({}, base, {
    chart: Object.assign({}, base.chart, { type: 'bar', height: 224 }),
    series: [{ name: 'Booked', data: %s }], xaxis: Object.assign({}, base.xaxis, { categories: %s, min: 0, max: 100, tickAmount: 2, labels: { style: { fontSize: '11px' }, formatter: v => Math.round(v) + '%%' } }),
    yaxis: { labels: { minWidth: 96, maxWidth: 110, style: { fontSize: '11px' } } },
    plotOptions: { bar: { horizontal: true, barHeight: '55%%', borderRadius: 3, dataLabels: { position: 'center' } } },
    dataLabels: { enabled: true, formatter: v => v + '%%', style: { fontSize: '11px', colors: [toHex(cssVar('--primary-foreground'))], fontWeight: 600 } },
    grid: Object.assign({}, base.grid, { padding: { left: 0, right: 8, top: -16, bottom: -8 }, xaxis: { lines: { show: true } }, yaxis: { lines: { show: false } } }),
    tooltip: Object.assign({}, base.tooltip, { y: { formatter: v => v + '%% booked' } }),
  })));
  if ($('#chart-heat')) charts.push(new ApexCharts($('#chart-heat'), Object.assign({}, base, {
    chart: Object.assign({}, base.chart, { type: 'heatmap', height: 288 }),
    series: %s,
    stroke: { width: 2, colors: [card] }, dataLabels: { enabled: true, style: { fontSize: '11px', colors: [fg], fontWeight: 500 } },
    plotOptions: { heatmap: { radius: 4, enableShades: false, colorScale: { ranges: [
      { from: 0, to: 0, color: mix(card, prim, 0.08), name: '0' }, { from: 1, to: 3, color: mix(card, prim, 0.28), name: '1–3' }, { from: 4, to: 6, color: mix(card, prim, 0.5), name: '4–6' },
      { from: 7, to: 9, color: mix(card, prim, 0.74), name: '7–9' }, { from: 10, to: 999, color: prim, name: '10+' } ] } } },
    xaxis: Object.assign({}, base.xaxis, { categories: %s, labels: { style: { fontSize: '11px' }, formatter: v => v + ':00' } }),
    grid: Object.assign({}, base.grid, { padding: { left: 4, right: 4, top: -20, bottom: -8 } }),
    tooltip: Object.assign({}, base.tooltip, { x: { formatter: v => v + ':00' }, y: { formatter: v => v + ' appointments' } }),
  })));
  if (measureChart) mountMeasure();
""" % (js([i["pct"] for i in cap["items"]]), js([i["name"] for i in cap["items"]]),
       js([{"name": hm["days"][d], "data": [{"x": h, "y": v} for h, v in zip(hm["hours"], hm["data"][d])]} for d in reversed(range(7))]), js(hm["hours"]))
must("  $$('.apex-spark').forEach(el => charts.push(", CHARTS.rstrip() + "\n  $$('.apex-spark').forEach(el => charts.push(")
must("  charts.forEach(c => c.render());\n}", "  charts.forEach(c => c.render()); if (chartVisits) hiddenSeries.forEach(n => chartVisits.hideSeries(n));\n}")
open(path, "w", encoding="utf-8", newline="\n").write(s)
print("patch2 ok", len(s.encode("utf-8")), "bytes")
