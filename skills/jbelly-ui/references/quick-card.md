# Quick card — the 90% of every app screen on one page (~2K tokens)

Read this INSTEAD of the full references for a standard app screen. Open a
full reference only for something this card does not cover. Start from
`assets/app-shell.html` (copy it — it already contains tokens, shell,
buttons, inputs, badges, cards, table with states, drawer, ⌘K palette, toasts,
dark/RTL/density) and edit; do not compose a shell from scratch.

## Tokens (roles, never raw palette)
`bg-background text-foreground` page · `bg-card border-border` cards · `bg-popover` menus/modals ·
`bg-primary text-primary-foreground` the ONE action · `bg-secondary` / `bg-muted` / `bg-accent` fills ·
`text-mono` headings & numbers · `text-secondary-foreground` second lines · `text-muted-foreground` hints ·
`border-input` fields · `ring-ring` focus · states `success` `warning` `info` `destructive` (always with text/icon).

## Sizes
Controls: sm `h-7 px-2.5 text-xs` · md `h-8.5 px-3 text-2sm` · lg `h-10 px-4 text-sm`; all `rounded-md`.
Type: **Inter** (display + text, house default; Arabic companion Noto Sans Arabic) · body 13px `text-2sm` · labels `text-xs` · card title `text-base font-semibold tracking-tight text-mono` ·
page title `text-xl font-medium text-mono` · KPI `text-3xl font-semibold text-mono tabular-nums font-display`.
Rhythm: cards `gap-5 lg:gap-7.5` · inside rows `gap-2.5` · card padding `p-5` · radius `--radius` (cards +4px, chips −4px).
Shell: sidebar 280 (collapsed 80) · header 70 (60 mobile) · container `px-6 xl:px-7.5 xl:max-w-(--breakpoint-xl)`.

## Recipes (class strings)
- **btn** `inline-flex items-center justify-center gap-1.5 shrink-0 whitespace-nowrap font-medium rounded-md shadow-xs h-8.5 px-3 text-2sm transition-colors focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 [&_svg]:size-4`
  primary `bg-primary text-primary-foreground hover:bg-primary/90` · outline `border border-input bg-background text-secondary-foreground hover:bg-accent` · ghost `shadow-none hover:bg-accent` · icon-only `p-0 w-8.5`
- **input** `flex w-full h-8.5 px-3 text-2sm rounded-md border border-input bg-background shadow-xs placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/40` (leading icon: wrap `relative`, icon `absolute start-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground`, add `ps-9`)
- **select** input + `appearance-none cursor-pointer pe-8` + chevron background · **textarea** input + `min-h-20 p-3 resize-y`
- **checkbox** `appearance-none size-4 rounded-sm border border-input bg-background checked:bg-primary checked:border-primary` · **switch** `h-5 w-7.5 rounded-full bg-input checked:bg-primary` + thumb `before:`
- **badge** `inline-flex items-center gap-1.5 h-6 px-[0.45rem] rounded-md text-xs font-medium` · light-success `bg-success/15 text-success` · light-warning `bg-warning/20 text-warning-foreground` · light-destructive `bg-destructive/10 text-destructive` · outline `border border-border bg-muted text-secondary-foreground` · sm `h-5 text-2xs rounded-sm` · dot `size-1.5 rounded-full bg-current opacity-75`
- **avatar** `size-9 rounded-full` image, or initials `inline-flex items-center justify-center bg-primary/10 text-primary font-semibold text-2xs`
- **card** `flex flex-col rounded-xl border border-border bg-card shadow-xs` · header `flex min-h-14 items-center justify-between gap-2.5 border-b border-border px-5` · content `grow p-5` · footer `flex items-center border-t border-border px-5 py-4`
- **table** `w-full text-sm` · th `h-11 px-4 text-start text-xs font-normal text-secondary-foreground border-b` · td `px-4 h-11.5 border-b border-border` · row `hover:bg-muted/40` · check col `w-[52px] text-center` · actions `text-end opacity-0 group-hover:opacity-100 group-focus-within:opacity-100`
- **tabs (line)** nav `flex gap-6 border-b border-border` · tab `-mb-px pb-3 text-sm text-secondary-foreground border-b-2 border-transparent` · active `text-primary border-primary font-medium` · **pill** nav `inline-flex gap-1 rounded-lg bg-muted p-1`, active `bg-background text-mono shadow-xs`
- **menu** `min-w-44 rounded-md border border-border bg-popover shadow-md p-2 flex flex-col gap-0.5` · item `flex items-center gap-2.5 rounded-md px-2 py-2 text-2sm hover:bg-accent [&_svg]:size-4 [&_svg]:text-muted-foreground`
- **modal** overlay `fixed inset-0 z-50 bg-black/30` · panel `fixed top-1/2 start-1/2 -translate-x-1/2 rtl:translate-x-1/2 -translate-y-1/2 w-[calc(100%-2rem)] max-w-lg rounded-lg border bg-popover shadow-md` · header `px-5 py-3 border-b` · footer `px-5 py-3 border-t flex justify-end gap-2.5`
- **drawer** `fixed z-50 top-5 bottom-5 end-5 w-[450px] max-w-[90%] rounded-xl border bg-card shadow-md flex flex-col`
- **toast** `flex items-start gap-2.5 rounded-lg border bg-popover shadow-md p-3.5 text-sm w-[360px]` in `fixed bottom-5 end-5 flex flex-col gap-2.5`
- **skeleton** `animate-pulse rounded-md bg-accent` · **empty** icon chip `size-12 rounded-full bg-muted text-muted-foreground`, title `text-sm font-semibold text-mono`, text `text-2sm text-secondary-foreground`, one button
- **kbd** `inline-flex h-5 items-center rounded-sm border bg-muted px-1.5 font-mono text-2xs`
- **KPI card** icon chip `size-9 rounded-lg bg-primary/10 text-primary` · delta badge light-success/destructive with trend icon · value + label; optional 40px sparkline SVG
- **page toolbar** `flex flex-wrap items-center justify-between gap-5 pb-7.5` → title/subtitle · `flex gap-2.5` select · outline · ONE primary
- **grid** page `grid gap-5 lg:gap-7.5` · row `grid lg:grid-cols-3 … items-stretch`, wide card `lg:col-span-2`, every card `h-full`

## Charts, i18n, weight
- **Charts**: ApexCharts with `apexBase()` from the scaffold (`references/charts.md`): smooth area with gradient fill for trends, sparklines (`height: 40`) in KPI cards, donut with centre total, heatmap with printed values. Explicit pixel heights. Never hand-draw dashboard charts.
- **RTL + Arabic**: `dir` alone is not enough for an Arabic product: use the scaffold's `data-i18n` pattern (one dictionary, `setLang('ar')` flips `dir`, `lang` and every tagged string, numbers stay LTR). Translate nav, titles, KPI labels, legends, table headers and statuses.
- **Weight budget**: ≤ 2,300 DOM elements for a full console, ≤ 45 nesting depth, no wrapper divs around single children; 5 skeleton rows, not 12.
- **Production**: the Tailwind browser build and CDN scripts are for demos and prototypes; a shipped product compiles Tailwind and self-hosts fonts and Lucide.

## Rules that decide the grade
one primary per view · four states per async region (skeleton/empty/error/success) · `Esc` closes overlays, focus returns ·
`Ctrl/⌘+K` opens search · logical props only (`ps/pe/ms/me/start/end`, `rtl:rotate-180` on chevrons) · dark = `html.dark`, persisted ·
personality chosen and written to `design/personality.md` · never `@apply group` / `peer` · render once in headless Edge before done.

## Decision tables (instead of prose)
Animate it? — appears > 10×/session (hover, toggles, list rows): no or ≤ 100ms · 1–10×/session (open/close, tabs, toasts): 150–250ms ease-out · once (page enter, KPI count-up): ≤ 600ms, this is the one signature moment · reduced-motion: none.
Card or no card? — data with a title and a toolbar: card · a single sentence of help: plain text in the toolbar · a list inside a card: `divide-y`, never nested cards.
Which primary? — the one action the user came for (New order, Save, Book); Export/Filter/Import are outline; row actions ghost.

## Design read (first output, 4 fields)
Write it with `python scripts/personality_init.py --product … --kind … --audience … --vibe … --preset … --change … --change …` (two dials minimum).
`kind` · `audience` (who, how often, keyboard or touch) · `vibe` (three words) · `system` (preset + dials changed). Written to `design/personality.md`; every later choice is checked against it.

## Cost rules for the building agent
Read this card + the personality preset you need in ONE batch at the start; do not re-read. Copy the scaffold, then edit.
Write the file once (no parts). Verify once with `python scripts/verify_page.py <page> --variants ",#dark=1,#dir=rtl"`, fix, verify once more at most. Budget: ≤ 12 tool calls for a screen.
