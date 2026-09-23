# Patterns — composing screens

Contents: KPI card · KPI row layouts · Callout card · Chart card · Table card with toolbar ·
List card · Highlights / progress list · Activity feed · Notification drawer ·
Settings form · Datatable page · Pricing / billing table · Checkout · Search palette ·
Cards grid (people, products) · Empty & error states · Dashboard blueprint

Every pattern is Cards + Components from the other two files; only the
composition is new. Numbers are the system's, keep them.

---

## KPI card

```html
<div class="card h-full flex-col justify-between gap-6 p-5 relative overflow-hidden">
  <div class="flex items-center justify-between">
    <span class="inline-flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary-accent [&_svg]:size-5"><!-- icon --></span>
    <span class="badge light-success sm"><svg trend-up/> 12%</span>            <!-- optional delta -->
  </div>
  <div class="flex flex-col gap-1">
    <span class="text-3xl font-semibold text-mono tabular-nums">9.3k</span>
    <span class="text-sm text-secondary-foreground">Active members</span>
  </div>
</div>
```

Optional: a faint decorative shape `absolute -end-6 -top-6 size-28 rounded-full bg-primary/5` — the only
decoration allowed on data cards. Optional sparkline: 40px-high inline SVG, stroke `var(--primary)`, fill `primary/10`.

## KPI row layouts

- 4 KPIs across: `grid sm:grid-cols-2 xl:grid-cols-4 gap-5 lg:gap-7.5`.
- 2×2 KPIs beside a wide card: outer `grid lg:grid-cols-3`, KPI block `grid grid-cols-2 gap-5 lg:gap-7.5 h-full`, wide card `lg:col-span-2`.
- Compact KPI strip inside one card: `grid grid-cols-2 md:grid-cols-4 divide-x divide-border` each `p-5` → value `text-xl font-semibold text-mono` + label `text-2sm text-secondary-foreground`.

## Callout card (welcome / upsell / “get started”)

`card h-full` → content `p-7.5 lg:p-10 flex flex-col gap-4` → Avatar group or icon, `h3 text-lg font-semibold text-mono`, `p text-2sm text-secondary-foreground max-w-md`, primary button. Optional
illustration on the end side via `grid md:grid-cols-[1fr_auto]`. Footer `justify-center` with a `link` button when it's a hint rather than a CTA.

## Chart card

```
card h-full
header:  title + toolbar → Select sm (period) or ⋮ ghost icon menu
content: px-3 py-1 grow flex flex-col justify-end      (chart lib draws inside; 220–300px tall)
footer:  optional legend row: flex flex-wrap gap-5 text-2sm → dot size-2 rounded-full bg-primary + label
```

Chart styling (any library): series 1 `var(--primary)`, series 2 `var(--muted-foreground)`, extra series
`var(--info)`, `var(--success)`, `var(--warning)`; grid lines `var(--border)` dashed 3; axis labels `text-xs`
`var(--muted-foreground)`; area fill `primary` at 10% → 0%; tooltips = Tooltip recipe; no drop shadows, no 3D, no gradients beyond that area fill.
Donut: 70% inner radius, centre value `text-2xl font-semibold text-mono`.

## Table card with toolbar

```
card
header:  flex-wrap → title (+ count badge outline sm)  ·  toolbar: search Input sm w-64 with leading icon · Select sm (filter) · outline sm “Filter” · primary sm “Add”
body:    Table directly (no padding). Loading: 5 Skeleton rows. Empty: Empty state inside a td colspan.
footer:  per-page select + range text + Pagination
```

Bulk actions: when ≥1 row checked, swap the toolbar for `flex items-center gap-2.5` → “3 selected” `text-2sm font-medium text-mono` + ghost sm buttons + destructive outline sm.

## List card (recent items, top products, team)

```
card
header:  title + “View all” link button
content: p-0 → ul divide-y divide-border
row:     flex items-center gap-2.5 px-5 py-3
         Avatar size-9 (or icon chip size-9 rounded-lg bg-muted)
         flex flex-col grow min-w-0 → title text-sm font-medium text-mono truncate hover:text-primary-accent · sub text-2sm text-secondary-foreground truncate
         trailing: Badge light / value text-sm font-medium text-mono tabular-nums / ghost icon sm
```

## Highlights / progress list

`content flex flex-col gap-4 p-5 lg:p-7.5 lg:pt-4` → header row `flex justify-between` (`text-2sm text-secondary-foreground` label + `text-2xl font-semibold text-mono` value + delta badge) → stacked bar `flex h-2 gap-1 rounded-full overflow-hidden [&>div]:rounded-full` with token colours → legend list `flex flex-col gap-2.5` rows `flex justify-between text-2sm` (dot + name / value `text-mono font-medium`).

## Activity feed / timeline

```
list:   flex flex-col
item:   relative flex gap-3 pb-6 ps-6 before:absolute before:start-2 before:top-6 before:bottom-0 before:w-px before:bg-border last:before:hidden
dot:    absolute start-0 top-1 size-4 rounded-full border-2 border-background bg-muted-foreground   (primary for the latest)
body:   flex flex-col gap-1 → line text-2sm text-foreground (actor in font-medium text-mono) · meta text-xs text-muted-foreground
attachment: card p-3 flex items-center gap-2.5 mt-2 (file icon chip + name + size)
```

Group by day with a `text-xs font-medium uppercase text-muted-foreground pb-3` heading.

## Notification drawer

Drawer recipe → header “Notifications” + ghost ⋮ → pill/line Tabs `px-5` (All · Inbox · Team) → list rows `flex gap-2.5 px-5 py-3` (Avatar size-8 + text block `text-2sm` with actor `font-medium text-mono`, message, time `text-xs text-muted-foreground`, optional inline actions: two sm buttons) → unread marker `size-2 rounded-full bg-primary ms-auto mt-1.5` → footer two buttons (“Archive all” outline, “Mark all as read” outline).

## Settings form (in a card)

```
card
header:  title + toolbar (optional Switch “Public profile”)
section × n: card section → grid lg:grid-cols-[200px_1fr] items-center gap-2.5 py-2
             label col: text-2sm font-medium text-mono (+ helper text-xs text-muted-foreground)
             control col: Input / Select / Switch / avatar uploader (Avatar size-16 + outline sm “Change” + link “Remove”)
footer:  justify-end → outline “Cancel” + primary “Save changes”
```

Danger zone: separate card with `border-destructive/30`, title `text-destructive-accent`, one sentence, destructive outline button.

## Datatable page

Toolbar (title + count + primary action) → optional KPI strip → Table card with toolbar → sticky bulk-action bar. Row click opens a Drawer with details; edit in a Modal `max-w-2xl`. Column set: check · entity · 2–4 attributes · status · date · actions. Hide low-value columns below `lg` with `hidden lg:table-cell`.

## Pricing / billing table (inside the app)

```
card → table-layout grid: grid grid-cols-[minmax(180px,1fr)_repeat(3,minmax(140px,1fr))]
head row:  plan cells → name text-sm font-semibold text-mono · price text-2xl font-semibold text-mono + /mo text-secondary-foreground · button (current plan: outline disabled “Current plan”; others primary sm “Upgrade”)
rows:      py-3 border-b border-border → feature label text-2sm text-secondary-foreground · cells centred: check size-4 text-success-accent / “—” text-muted-foreground / value text-2sm text-mono
popular:   column bg-primary/5 + Badge primary sm “Popular” above the name
```

Plan cards alternative for ≤3 plans: `grid md:grid-cols-3 gap-5` using the landing-page Pricing recipe.

## Checkout (store-client)

`grid lg:grid-cols-[1fr_380px] gap-5 lg:gap-7.5` → left: stepper (`flex items-center gap-2.5 text-2sm`, step chip `size-6 rounded-full bg-primary text-primary-foreground text-xs font-semibold`, done chip `bg-success`, line `h-px grow bg-border`) + card per step (shipping form / payment method radio-cards `grid sm:grid-cols-2 gap-2.5` with `[&:has(:checked)]:border-primary`) → right: sticky `lg:sticky lg:top-24` order-summary card (items list + totals `flex justify-between text-2sm`, total `text-base font-semibold text-mono`, primary lg w-full). Order placed: centred card with `size-16 rounded-full bg-success/10 text-success-accent` check icon.

## Search palette (⌘K)

Modal `max-w-[600px]` top-aligned (`top-[15%] translate-y-0`) → Input lg with leading search icon and no border (`border-0 shadow-none focus-visible:ring-0`) + Kbd `Esc` → line Tabs `px-5` (Mixed · Settings · Users · Docs) → groups: heading `px-5 py-2 text-xs font-medium uppercase text-muted-foreground` + item rows (Dropdown item recipe, `px-5`, trailing shortcut/arrow) → footer `flex gap-4 px-5 py-2.5 border-t text-xs text-muted-foreground` with Kbd hints. Empty: Empty state; “No results for …”.

## Cards grid (people, teams, products)

```
grid:    grid sm:grid-cols-2 xl:grid-cols-3 gap-5 lg:gap-7.5
person:  card p-5 flex flex-col items-center text-center gap-3 → Avatar size-20 → name text-base font-semibold text-mono · role text-2sm text-secondary-foreground → Badge light → stats row divide-x → footer buttons (outline sm “Message”, primary sm “Follow”)
team:    card p-5 → row: icon chip size-10 + name + Badge · description text-2sm · Avatar group + “+3” · footer: rating or “View” link
product: card overflow-hidden → image aspect-[4/3] object-cover bg-muted → p-5: name text-sm font-medium text-mono · price text-base font-semibold text-mono · rating stars text-warning-accent size-3.5 · outline sm “Add to cart” w-full
```

## Empty & error states

- Empty list: Empty state recipe inside the card content; keep the header so the user knows where they are.
- First-run: Callout card with 3 numbered steps and a primary action.
- Error 404/500 page: Auth-page centred layout, code `text-5xl font-semibold text-mono`, one sentence, primary “Back to home” + outline “Contact support”.
- Inline load failure: Alert destructive inside the card, with a `link` “Retry”.

## Dashboard blueprint (default first screen)

```
toolbar          title “Dashboard” + subtitle (date range) · Select sm (period) · outline “Export” · primary “New …”
row 1            grid lg:grid-cols-3 → [KPI 2×2 block] [callout card lg:col-span-2]        (or 4 KPIs across)
row 2            grid lg:grid-cols-3 → [highlights card] [chart card lg:col-span-2]
row 3            grid lg:grid-cols-3 → [list card] [table card lg:col-span-2]
```

Each row `items-stretch`, each card `h-full`. Above `2xl` nothing changes;
below `lg` everything stacks in source order, so order cards by importance.
