# Integrations — vetted libraries and interaction rules

Professional admin products are ~30% custom UI and ~70% well-styled
third-party parts: charts, grids, calendars, editors, uploads, maps. Two
rules govern all of them:

1. **Licence-safe only.** MIT / BSD / Apache / OFL. Anything GPL, "free for
   non-commercial", or with a per-project fee is out, because the same product
   ships to many customers. The table below is the allowed list; add to it
   only after checking the licence file, not the marketing page.
2. **Styled through tokens.** A library's default theme is never shipped.
   Map its CSS variables or theme options to the system tokens so it follows
   light/dark, personality and density automatically.

Contents: Library table · Charts · Data grids · Calendar & dates · Rich text ·
File upload · Maps · Drag & drop · Command palette · Toasts · Forms · i18n/RTL ·
Animation · Interaction rules (state layers, motion, density, type roles) ·
Vanilla stack

---

## Library table (per need)

| Need | Vanilla / any stack | React | Licence | Notes |
|------|--------------------|-------|---------|-------|
| Charts (business) | ApexCharts | react-apexcharts / Recharts | MIT | ApexCharts for dashboards (sparklines, radial, heatmap); Recharts for simple React charts |
| Charts (custom/big data) | D3, uPlot | visx, uPlot | BSD/MIT | uPlot for > 10k points |
| Data grid | TanStack Table (headless) + own markup; DataTables.net | @tanstack/react-table | MIT | Headless keeps the Table recipe; virtualise with @tanstack/virtual |
| Calendar (events) | FullCalendar core + daygrid/timegrid/list/interaction | @fullcalendar/react | MIT (core plugins) | Premium plugins (resource timeline) are paid — avoid |
| Date / range picker | vanilla-calendar-pro, flatpickr | react-day-picker | MIT | Style day cells with tokens; range = two inputs + one popover |
| OTP / PIN input | own 6-input recipe | input-otp | MIT | auto-advance, paste, submit on last |
| Rich text | Tiptap (ProseMirror), Quill 2 | @tiptap/react | MIT | Not TinyMCE (GPL/commercial) or CKEditor (GPL/commercial) |
| Markdown render | marked / markdown-it + DOMPurify | react-markdown + remark-gfm | MIT | always sanitise |
| File upload | Dropzone, Uppy, FilePond | react-dropzone, Uppy | MIT | Uppy for resumable/tus; show per-file progress rows |
| Image crop | Cropper.js | react-easy-crop | MIT | |
| Maps | Leaflet + OSM/MapTiler tiles, MapLibre GL | react-leaflet, react-map-gl (maplibre) | BSD/MIT | Tile provider terms apply; never Google Maps JS without a billing decision |
| Drag & drop / sortable | SortableJS | @dnd-kit/core + sortable | MIT | Keyboard sensors on; announce moves |
| Tree view | own recipe | @headless-tree/react | MIT | |
| Resizable panes | Split.js | react-resizable-panels | MIT | |
| Carousel | Embla, Swiper | embla-carousel-react | MIT | pause on hover/focus, reduced-motion → static |
| Popover positioning | Floating UI | Radix UI / react-aria-components | MIT | Headless primitives; all styling from recipes |
| Command palette | own recipe + Floating UI | cmdk | MIT | |
| Toasts | own recipe (Toast in components.md) | sonner, notistack | MIT | |
| Modals/drawers/menus | native `<dialog>` + `popover` | Radix UI, vaul (drawer) | MIT | Focus management comes free with Radix/dialog |
| Forms & validation | native constraint API + own messages | react-hook-form + zod | MIT | |
| Data fetching/cache | fetch + own cache | @tanstack/react-query | MIT | gives loading/error states for free |
| i18n | i18next | react-i18next, react-intl | MIT | ICU plurals; RTL via `dir` |
| Animation | CSS transitions; motion (vanilla) | motion/react, tw-animate-css | MIT | GSAP is now free (Webflow) but keep to one signature moment |
| Icons | Lucide (static SVG sprite) | lucide-react | ISC/MIT | one set, stroke 2, 16/20/24 |
| Tables to CSV/XLSX | own CSV; SheetJS community | — | Apache-2.0 | |
| PDF export | pdfmake, jsPDF | @react-pdf/renderer | MIT | print stylesheet first |
| Syntax highlight | Prism, Shiki | shiki | MIT | |
| Tooltips | Floating UI + Tooltip recipe | Radix Tooltip | MIT | |
| Confetti / celebration | canvas-confetti | — | ISC | once per milestone, respects reduced motion |
| Clipboard | `navigator.clipboard` | — | — | show "Copied" toast 1.5s |
| Auth UI | own recipes (auth pages) | — | — | never a hosted-widget default look |

## Charts

- Theme once, globally: text `var(--muted-foreground)` at 12px in the UI
  font; grid `var(--border)`, dashed 3; no chart background; legend markers
  `size-2 rounded-full`; tooltip = Tooltip recipe (dark mono surface).
- Series colours in this order: `--primary`, `--chart-2` … `--chart-5`
  (define per personality; default: primary, info, success, warning, muted).
  Never more than 5 series; the 6th becomes "Other".
- Area fills `primary` at 12% → 0%; bars `rounded-t-[3px]`, column width
  ≤ 40%; lines 2px, no markers until hover; donut inner radius 70% with the
  total in the centre.
- Axes: y starts at 0 for bars; thousands separators; time axis shows one label
  per period bucket (week → per-Monday, quarter → per-month); rotate nothing —
  drop labels instead.
- Sparklines inside KPI cards: 40px tall, no axes, no tooltip, one series.
- Provide the data as a table for screen readers (`sr-only` `<table>` or an
  "as table" toggle) and give the chart an `aria-label` with the takeaway.
- Dark mode: same hues, +8% lightness for series; gridlines at
  `var(--border)`; never pure white text.

## Data grids

- Keep the Table recipe markup; the library only computes. Row height 46px
  (compact 38px), header 44px, checkbox column 60px, actions column 60px.
- Column widths in `minmax(…)`; sticky first column below `lg`; horizontal
  scroll inside the card.
- Virtualise above 200 rows; paginate server-side above 10k. Pagination text
  "1–25 of 1,204".
- Sorting, filtering, column visibility and page live in the URL query so
  views are shareable.
- Inline edit: cell turns into Input sm on `Enter`/double-click; `Esc` cancels;
  invalid cells get `aria-invalid` + error tooltip.
- Export honours current filters and column set.

## Calendar & dates

- Calendar surfaces use `bg-card`; today `bg-primary/10 text-primary-accent font-semibold`;
  selected `bg-primary text-primary-foreground`; range fill `bg-primary/10`;
  other-month days `text-muted-foreground/60`; weekend header `text-muted-foreground`.
- Events: `rounded-sm border-s-2 px-1.5 text-xs` with the category colour as
  `border-s` and a 10% tint background; all-day bar full width; +N "more" link.
- Date input format follows locale; show a calendar icon on the end side;
  keyboard typing allowed; `Today` and `Clear` buttons in the popover footer.
- Ranges: presets on the start side of the popover (Today · Yesterday · Last 7
  · Last 30 · This month · Custom); Apply/Cancel footer.
- Week starts per locale (Sat/Sun/Mon); Hijri or dual calendars where the
  market needs them (Arabic products: show Gregorian with optional Hijri line).

## Rich text

- Toolbar = ghost icon buttons sm in groups with Separators; active state
  `bg-accent text-mono`; sticky toolbar at the top of the editor card.
- Editor body `prose` (Tailwind typography) with the system fonts and
  `max-w-none`; min height 200px; placeholder in `text-muted-foreground`.
- Paste sanitised; images uploaded through the File upload rules; slash
  commands (`/`) open the Dropdown recipe.

## File upload

- Drop zone: `border border-dashed border-input rounded-lg bg-background p-5 text-center`
  with an icon chip, "Drop files or **browse**", allowed types + max size in
  `text-xs text-muted-foreground`; drag-over → `border-primary bg-primary/5`.
- File rows: icon chip · name `text-2sm font-medium text-mono` · size `text-xs` ·
  Progress (thin) · remove ghost icon; error rows `text-destructive-accent` + retry.
- Avatar/image inputs: preview `size-16 rounded-full` + outline sm "Change" +
  link "Remove"; crop dialog for avatars.

## Maps

- Tiles in a neutral style (light grey for light mode, dark for dark mode);
  markers use `var(--primary)`; clusters `bg-primary text-primary-foreground rounded-full size-8 text-xs font-semibold`.
- Map + list split `lg:grid-cols-[1fr_420px]` (list on the end side); hovering a
  list row highlights its marker and vice-versa; "Search this area" button
  appears after pan.
- Always a list fallback and a text address; keyboard-accessible controls.

## Drag & drop

- Sortable handles are visible (`grip-vertical` icon, `cursor-grab`); dragging
  item `shadow-md rotate-[1deg] opacity-90`; drop target `border-2 border-dashed border-primary/60 bg-primary/5`.
- Keyboard alternative on every sortable: focus the handle, `Space` to lift,
  arrows to move, `Space` to drop, `Esc` to cancel; announce with a live region.
- Kanban columns `w-80 shrink-0 bg-muted/60 rounded-xl p-2.5` with a count
  badge; cards are Card recipe `p-3` with a light badge, avatar group and
  due-date meta.

## Command palette

- `Ctrl/⌘+K` opens; Input lg borderless + Kbd `Esc`; groups (Recent, Pages,
  Actions, Records) with headings; item = Dropdown item recipe with a
  trailing shortcut; typeahead filters; `↑/↓/Enter`; max 8 results per group;
  actions can chain ("Create → Invoice").

## Toasts

- Bottom-end stack (top-centre for global system notices), max 3 visible,
  4s auto-dismiss, pause on hover/focus, close button, optional action
  (Undo / View); success uses the success icon, not a green background.

## Forms

- Validation library only produces messages; presentation is the Field recipe.
- Async validation (unique email) shows a spinner in the field's end slot and
  a check on success.
- Schema-driven forms render each field type through the same recipes so
  generated and hand-made forms look identical.

## i18n / RTL

- Strings out of components from day one; ICU plural rules; dates/numbers
  via `Intl`; never concatenate sentences.
- Direction from `dir` on `<html>`; icons that imply direction get
  `rtl:rotate-180`; text-align follows `start/end`; numbers stay LTR inside
  RTL (`unicode-bidi: plaintext` on numeric cells).
- Arabic type: Latin UI font + an Arabic companion (`IBM Plex Sans Arabic`,
  `Noto Sans Arabic`, `Cairo`, `Tajawal`) at the same optical weight; line-height
  1.7 for Arabic body; avoid tracking on Arabic; test with 30% longer strings.

## Animation

- Transitions: `--t-tint` for colour/opacity, `--t-pop` / `--t-panel` for
  overlays (enter faster than exit: 200 in / 150 out); 300ms sidebar collapse.
- Enter: `opacity 0→1` + `translateY 4px→0` (menus, toasts) or `scale .98→1`
  (modals); never bounce, never slide across the screen.
- One signature moment per product (page-enter stagger of cards 40ms apart,
  or KPI count-up 600ms) — chosen in the personality file, applied everywhere
  it applies, and disabled under `prefers-reduced-motion`.
- Scroll-triggered motion is for marketing pages only, once per element,
  ≤ 400ms, no parallax on content.

## Interaction rules (borrowed from mature platform systems, restated as instructions)

**State layers.** Hover, focus and pressed states are an overlay of the
control's own text colour, not a new colour: hover 8%, focus 12%, pressed
12%, dragged 16% (`hover:bg-[color-mix(in_oklab,currentColor_8%,transparent)]`
on ghost/outline; solid buttons use `/90` then `/85`). Disabled = 38% opacity
on content, never a grey fill. This keeps states consistent across every
personality without per-variant colours.

**Elevation.** Five levels are enough: 0 page, 1 card (`shadow-xs`), 2 raised
card on hover, 3 popover/dropdown (`shadow-md`), 4 modal/drawer (`shadow-md` +
scrim 30%). In dark mode elevation is expressed by *lighter surface*
(+3–4% lightness per level), not bigger shadows.

**Motion durations.** short 100–200ms (state changes, icons), medium
250–400ms (open/close, expand), long 450–600ms (page-level, signature
moment). Decelerate on enter (`cubic-bezier(0,0,.2,1)`), accelerate on exit
(`cubic-bezier(.4,0,1,1)`), standard for in-place changes.

**Density steps.** Default 0, −1 = 4px less height per control, −2 = 8px
less; apply the same step to control height, row height and list-item
padding together; never below 24px pointer targets on desktop, 44px on touch.

**Type roles.** Map the system to roles so choices are consistent:
display (KPI numbers, marketing h1) · headline (page title) · title (card
title, modal title) · body (13–14px UI text) · label (12px captions, table
headers, badges). Each role has one font, one weight and one line-height;
components reference roles, not sizes.

**Targets.** 24px minimum pointer targets on desktop, 44px on touch; 8px gap
between adjacent targets; hit area may extend beyond the visual bounds.

## Vanilla stack (no framework)

Tailwind v4 + tokens.css + Lucide sprite + Floating UI + a 150-line
`ui.js` for: theme toggle, sidebar state, dropdown/modal/drawer open-close with
focus trap and `Esc`, tabs, toasts, command palette, and `data-confirm`
buttons. Everything else is a library from the table. Do not write a custom
datepicker, editor or chart.

