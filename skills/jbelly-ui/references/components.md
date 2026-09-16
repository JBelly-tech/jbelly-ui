# Components — exact recipes

All class strings assume `tokens.css` is loaded (so `rounded-md`, `text-2sm`,
`bg-card`, `shadow-xs` resolve to the system values). Copy the base string,
add one variant, add one size. Nothing else.

Use them as HTML classes, or as `@apply` inside `@layer components` when a
recipe repeats more than ~5 times. In `@apply`, omit `group` / `peer` (markers,
not utilities) and keep arbitrary variants like `[&_svg]:size-4` — those are
fine. One unknown class fails the whole stylesheet silently (page renders
unstyled), so render the page once after any CSS change.

Contents: Button · Input · Select · Textarea · Checkbox / Radio · Switch ·
Label / Field · Badge · Avatar · Card · Table · Tabs · Dropdown menu ·
Modal · Drawer · Alert / Toast · Tooltip · Progress · Skeleton · Pagination ·
Breadcrumb · Kbd · Separator · Link · Empty state

---

## Button

```
base:  inline-flex items-center justify-center gap-1.5 shrink-0 whitespace-nowrap
       font-medium rounded-md shadow-xs transition-colors cursor-pointer
       focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ring-offset-background
       disabled:opacity-50 disabled:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0

size md (default):  h-8.5 px-3 text-2sm
size sm:            h-7 px-2.5 text-xs gap-1.25
size lg:            h-10 px-4 text-sm
icon-only:          p-0 size-8.5   (sm: size-7, lg: size-10)

primary:      bg-primary text-primary-foreground hover:bg-primary/90
secondary:    bg-secondary text-secondary-foreground hover:bg-secondary/80
outline:      border border-input bg-background text-secondary-foreground hover:bg-accent hover:text-accent-foreground
ghost:        shadow-none bg-transparent text-accent-foreground hover:bg-accent
dim:          shadow-none bg-transparent text-muted-foreground hover:text-foreground
mono:         bg-mono text-mono-foreground hover:bg-mono/90
destructive:  bg-destructive text-destructive-foreground hover:bg-destructive/90
link:         shadow-none h-auto p-0 text-primary hover:underline
```

Hierarchy per view: one `primary`, actions of equal weight `outline`,
tertiary/inline `ghost`, toolbar icon buttons `ghost` + icon-only. Group
buttons with `flex items-center gap-2.5`; split/segmented with
`[&>*:not(:first-child)]:rounded-s-none [&>*:not(:last-child)]:rounded-e-none [&>*:not(:first-child)]:-ms-px`.

## Input

```
base:  flex w-full rounded-md border border-input bg-background text-foreground shadow-xs
       placeholder:text-muted-foreground transition-colors
       focus-visible:outline-none focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/40
       disabled:opacity-50 disabled:cursor-not-allowed read-only:bg-muted
       aria-invalid:border-destructive aria-invalid:ring-destructive/30

size md: h-8.5 px-3 text-2sm     sm: h-7 px-2.5 text-xs     lg: h-10 px-4 text-sm
```

Leading icon: wrap in `relative`, put the icon `absolute start-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground`,
add `ps-9` to the input. Trailing action (clear, eye) the same with `end-2` and `pe-9`.

Input group (add-on + field): `flex items-stretch [&>*]:rounded-none [&>:first-child]:rounded-s-md [&>:last-child]:rounded-e-md [&>*+*]:-ms-px`
add-on: `flex items-center justify-center shrink-0 h-8.5 min-w-8.5 px-3 border border-input bg-muted text-secondary-foreground text-2sm`.

File input: `file:me-3 file:h-full file:border-0 file:bg-muted file:px-3 file:text-2sm file:font-medium file:text-foreground`.

## Select (native)

Input base + `appearance-none cursor-pointer pe-8 bg-no-repeat bg-[position:right_0.6rem_center] rtl:bg-[position:left_0.6rem_center] bg-[length:14px_11px]`
and a chevron as `background-image` (inline SVG, `stroke` = muted-foreground). Same three sizes as Input.
For searchable / multi selects use a headless library styled with the Dropdown menu recipe below.

## Textarea

Input base without height + `min-h-20 p-3 text-2sm leading-normal resize-y`.

## Checkbox / Radio

```
checkbox: appearance-none shrink-0 size-4.5 rounded-sm border border-input bg-background shadow-xs cursor-pointer
          checked:bg-primary checked:border-primary checked:bg-[url(check.svg)] bg-center bg-no-repeat
          focus-visible:ring-2 focus-visible:ring-ring/40 disabled:opacity-50
          sm: size-4      lg: size-5
radio:    same, but rounded-full and a 6px dot via checked:bg-[radial-gradient(circle,var(--primary-foreground)_35%,transparent_40%)]
```

Quick native fallback (fine for admin forms): `size-4 accent-primary`.
Row layout: `label.flex.items-center.gap-2.5.text-2sm.cursor-pointer`. Description under the label in `text-xs text-muted-foreground`.

## Switch

```
appearance-none relative shrink-0 inline-flex h-5 w-7.5 rounded-full bg-input cursor-pointer transition-colors
checked:bg-primary disabled:opacity-50
before:absolute before:top-0.5 before:start-0.5 before:size-4 before:rounded-full before:bg-background before:shadow-xs
before:transition-transform checked:before:translate-x-2.5 rtl:checked:before:-translate-x-2.5
sm: h-4 w-6 before:size-3 checked:before:translate-x-2      lg: h-6 w-10 before:size-5 checked:before:translate-x-4
```

## Label / Field

```
label:   text-2sm font-medium text-mono                 (inline after a checkbox: font-normal text-foreground)
field:   flex flex-col gap-1.5
helper:  text-xs text-muted-foreground
error:   text-xs text-destructive   (+ aria-invalid on the control)
required mark: <span class="text-destructive">*</span>
form:    flex flex-col gap-5      grid forms: grid gap-5 lg:grid-cols-2
```

## Badge

```
base:  inline-flex items-center justify-center gap-1.5 whitespace-nowrap font-medium rounded-md
       h-6 min-w-6 px-[0.45rem] text-xs
sizes: lg h-7 min-w-7 px-2      sm h-5 min-w-5 px-[0.325rem] text-2xs rounded-sm gap-1      xs h-4 min-w-4 px-1 text-[0.625rem] rounded-sm

default:      bg-secondary text-accent-foreground
primary:      bg-primary text-primary-foreground
success:      bg-success text-success-foreground
warning:      bg-warning text-warning-foreground
info:         bg-info text-info-foreground
destructive:  bg-destructive text-destructive-foreground
light-*:      bg-primary/10 text-primary   (same for success / warning / info / destructive)
outline:      border border-border bg-muted text-secondary-foreground
outline-*:    border border-primary/30 bg-primary/5 text-primary
pill:         + rounded-full
dot (inside): <span class="size-1.5 rounded-full bg-current opacity-75"></span>
```

Use `light-*` or `outline-*` for table status cells (calmer), solid for counts
and nav badges. A count badge on an icon button: `absolute -top-1 -end-1 size-4 text-[10px]`.

## Avatar

```
wrapper:   relative flex shrink-0 size-10           sizes: 6 · 7 · 8 · 9 · 10 · 12 · 16 · 20
image:     size-full rounded-full object-cover
initials:  size-full rounded-full inline-flex items-center justify-center bg-primary/10 text-primary font-semibold text-2xs uppercase
status:    absolute -end-0.5 -bottom-0.5 size-2.5 rounded-full border-2 border-background bg-success   (offline: bg-muted-foreground)
group:     flex -space-x-2 rtl:space-x-reverse  ·  each child: ring-1 ring-background hover:z-10 relative
+N chip:   same as initials, bg-secondary text-secondary-foreground
```

Square avatars for products / companies: `rounded-lg` instead of `rounded-full`.

## Card

```
card:      flex flex-col rounded-xl border border-border bg-card text-card-foreground shadow-xs
header:    flex min-h-14 flex-wrap items-center justify-between gap-2.5 border-b border-border px-5
title:     text-base font-semibold tracking-tight leading-none text-mono
subtitle:  text-2sm text-secondary-foreground
toolbar:   flex items-center gap-2.5              (right side of header: select, buttons, ⋮ menu)
content:   grow p-5                                (roomy: p-7.5 · dense: p-3)
section:   border-b border-border px-5 py-5 last:border-b-0   (stacked groups inside one card — instead of nested cards)
footer:    flex items-center border-t border-border px-5 py-4   (justify-end for actions, justify-center for “View all”)
table variant: card + a Table directly inside (no content padding); pagination goes in the footer.
clickable: + hover:border-ring/60 transition-colors cursor-pointer
```

Grid of cards: `grid gap-5 lg:gap-7.5` and `items-stretch` with `h-full` on
each card so a row's cards share height.

## Table

```
wrap:   overflow-x-auto            (scroll the table, never the page)
table:  w-full border-collapse text-sm text-foreground caption-bottom
thead:  bg-muted/50                 (omit for a cleaner look inside cards)
th:     h-11 px-4 text-start align-middle text-xs font-normal text-secondary-foreground border-b border-border whitespace-nowrap
td:     px-4 py-3 align-middle border-b border-border      (last row: [&_tr:last-child_td]:border-b-0 inside cards)
row:    hover:bg-muted/40 transition-colors   selected: bg-accent
dense:  th h-9 · td py-2 · text-2sm
bordered: table + border border-border, td/th + border-e last:border-e-0
sticky header: thead th sticky top-0 z-10 bg-card
sortable th: <span class="inline-flex items-center gap-1 cursor-pointer select-none">Label <svg chevrons size-3.5 text-muted-foreground/></span>
check column: th/td w-[60px] text-center · checkbox size-4 sm
actions column: td text-end · ghost icon button · w-[60px]
```

Cell patterns:

- **Entity**: `flex items-center gap-2.5` → avatar `size-9` → `flex flex-col` with
  name `text-sm font-medium text-mono hover:text-primary` and sub `text-2sm text-secondary-foreground`.
- **Status**: light badge + dot, e.g. `light-success` “Active”.
- **Numeric**: `text-end tabular-nums`.
- **Date**: `text-secondary-foreground whitespace-nowrap`.

Footer (in card footer): `flex flex-wrap items-center justify-between gap-2.5 text-2sm text-secondary-foreground`
→ left “Show [select sm] per page”, right “1–10 of 240” + Pagination.

## Tabs

```
line (default):  nav: flex items-center gap-6 border-b border-border overflow-x-auto
                 tab: -mb-px pb-3 text-sm text-secondary-foreground border-b-2 border-transparent whitespace-nowrap hover:text-primary
                      active: text-primary border-primary font-medium
                 with icon: inline-flex items-center gap-1.5 [&_svg]:size-4
pill:            nav: inline-flex items-center gap-1 rounded-lg bg-muted p-1
                 tab: h-7 px-3 rounded-md text-2sm text-secondary-foreground hover:text-foreground
                      active: bg-background text-mono shadow-xs font-medium
vertical:        nav: flex flex-col gap-1 · tab: rounded-md px-2.5 py-2 text-2sm hover:bg-accent · active: bg-accent text-primary font-medium
```

## Dropdown menu

```
panel:     min-w-44 max-w-64 rounded-md border border-border bg-popover text-popover-foreground shadow-md p-2 flex flex-col gap-0.5 z-50
item:      flex items-center gap-2.5 rounded-md px-2 py-2 text-2sm text-foreground cursor-pointer hover:bg-accent
           [&_svg]:size-4 [&_svg]:text-muted-foreground   destructive item: text-destructive hover:bg-destructive/10
heading:   px-2 py-1.5 text-xs text-muted-foreground
separator: my-1 h-px bg-border
shortcut:  ms-auto text-xs text-muted-foreground   (or a Kbd)
submenu arrow: ms-auto size-4
```

Position with Popper/Floating UI or native `popover` + `anchor`; offset 8px;
placement `bottom-start` (mirrors under RTL automatically with logical values).

## Modal

```
overlay:   fixed inset-0 z-50 bg-black/30 backdrop-blur-[2px]
content:   fixed z-50 top-1/2 start-1/2 -translate-x-1/2 rtl:translate-x-1/2 -translate-y-1/2 w-[calc(100%-2rem)] max-w-lg
           rounded-lg border border-border bg-popover text-popover-foreground shadow-md flex flex-col max-h-[calc(100vh-2rem)]
           sizes: max-w-md · max-w-lg · max-w-2xl · max-w-4xl
header:    flex items-center justify-between gap-2.5 px-5 py-3 border-b border-border
title:     text-sm font-semibold text-mono
close:     ghost icon button sm
body:      p-5 overflow-y-auto grow
footer:    flex items-center justify-end gap-2.5 px-5 py-3 border-t border-border
```

Confirm-delete modal: title, one sentence `text-2sm text-secondary-foreground`,
footer `outline` Cancel + `destructive` Delete.

## Drawer (side panel)

```
overlay: as Modal
panel:   fixed z-50 top-5 bottom-5 end-5 w-[450px] max-w-[90%] rounded-xl border border-border bg-card shadow-md flex flex-col
         (edge-attached variant: top-0 bottom-0 end-0 rounded-none border-s)
header:  flex items-center justify-between px-5 py-2.5 border-b border-border text-sm font-semibold text-mono
body:    grow overflow-y-auto scroll-thin
footer:  grid grid-cols-2 gap-2.5 p-5 border-t border-border   (two equal outline/primary buttons)
```

## Alert / Toast

```
alert:      flex w-full items-start gap-2.5 rounded-lg p-3.5 text-sm bg-muted text-foreground
            primary: bg-primary/10 text-primary · success: bg-success/10 text-success · warning: bg-warning/15 text-warning-foreground
            destructive: bg-destructive/10 text-destructive · outline: border border-border bg-transparent
icon:       size-4 mt-0.5 shrink-0
title:      font-semibold   · text below in text-2sm opacity-90
dismiss:    ms-auto ghost icon button sm
toast:      alert + w-[360px] bg-popover text-popover-foreground border border-border shadow-md
            container: fixed bottom-5 end-5 z-50 flex flex-col gap-2.5
```

## Tooltip

`z-50 rounded-md bg-mono text-mono-foreground px-2 py-1.5 text-xs shadow-md max-w-60` — appears after 300ms, 8px offset.

## Progress

```
track: relative h-1 w-full overflow-hidden rounded-full bg-secondary     (thick: h-2)
bar:   h-full bg-primary transition-[width]    success / warning / destructive variants
label row above: flex justify-between text-2sm → name text-mono, value text-secondary-foreground
```

## Skeleton

`animate-pulse rounded-md bg-accent` — text line `h-3 w-40`, avatar `size-10 rounded-full`, card `h-32`.

## Pagination

```
nav:    flex items-center gap-1
button: inline-flex items-center justify-center size-7 rounded-md text-xs text-secondary-foreground hover:bg-accent
        active: bg-accent text-mono font-medium   disabled: opacity-50 pointer-events-none
prev/next: icon-only with chevrons (auto-mirror: rtl:rotate-180 on the svg)
ellipsis: size-7 inline-flex items-center justify-center text-muted-foreground
```

## Breadcrumb

`flex items-center gap-1.5 text-xs text-secondary-foreground` · link `hover:text-primary` · separator `size-3.5 text-muted-foreground rtl:rotate-180` · current `text-mono`.

## Kbd

`inline-flex h-5 items-center rounded-sm border border-border bg-muted px-1.5 font-mono text-2xs text-secondary-foreground`.

## Separator

`h-px w-full bg-border` (vertical: `w-px self-stretch bg-border`). With label:
`flex items-center gap-3 text-xs text-muted-foreground before:h-px before:grow before:bg-border after:h-px after:grow after:bg-border`.

## Link

`text-primary hover:underline underline-offset-4` · in body text `font-medium`.

## Empty state

```
wrapper: flex flex-col items-center justify-center text-center gap-3 py-12
icon:    inline-flex size-12 items-center justify-center rounded-full bg-muted text-muted-foreground [&_svg]:size-5
title:   text-sm font-semibold text-mono
text:    text-2sm text-secondary-foreground max-w-xs
action:  primary button sm (optional secondary link)
```
