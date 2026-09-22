# jbelly-ui — paste-in UI system for chat tools (generated; self-contained)

Use this whole message as instructions for any UI you produce in this conversation.
Output complete HTML with Tailwind v4 (`<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>`) and Lucide icons unless the user names another stack; then translate the class strings to that stack.

## 1. Design read (first output, four fields)
`kind` · `audience` (who, how often, keyboard or touch) · `vibe` (three words) · `system` (preset + dials changed). State it, then build. Never ship the default look: pick a preset below and change at least two dials (palette, shape, density, signature element).

## 2. Tokens — paste this CSS first (it is the whole colour system; components use roles only)
```css
:root {
  --destructive-accent: oklch(57.5% 0.22 27);   /* --destructive as text: a fill's lightness is not a reader's */
  color-scheme: light;

  /* shape + type */
  --radius: 0.5rem;
  /* Type: Inter for display AND text (the professional-template look): 13px UI, 600 headings,
     tracking-tight on card titles only. Change --font-display only for a brand reason. */
  --font-display: "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-sans: "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI",
    Roboto, "Noto Sans Arabic", "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, "JetBrains Mono", "Cascadia Mono", Consolas,
    "Liberation Mono", monospace;

  /* surfaces */
  --background: oklch(100% 0 0);
  --foreground: oklch(14.5% 0.005 285);
  --card: oklch(100% 0 0);
  --card-foreground: oklch(14.5% 0.005 285);
  --popover: oklch(100% 0 0);
  --popover-foreground: oklch(14.5% 0.005 285);

  /* brand — the one colour that carries identity */
  --primary: oklch(54% 0.2 258);
  /* the brand colour as text: a link has to be readable on the surface, which a fill does not */
  --primary-accent: oklch(54% 0.2 258);
  --primary-foreground: oklch(100% 0 0);

  /* neutrals */
  --secondary: oklch(96.5% 0.002 285);
  --secondary-foreground: oklch(21% 0.006 285);
  --muted: oklch(96.5% 0.002 285);
  --muted-foreground: oklch(55% 0.014 285);
  --accent: oklch(96.5% 0.002 285);
  --accent-foreground: oklch(21% 0.006 285);
  --mono: oklch(14.5% 0.005 285);
  --mono-foreground: oklch(100% 0 0);

  /* state */
  --destructive: oklch(57.5% 0.22 27);
  --destructive-foreground: oklch(100% 0 0);
  --success: oklch(72% 0.19 150);
  --success-foreground: oklch(100% 0 0);
  --warning: oklch(85% 0.17 90);
  --warning-foreground: oklch(30% 0.05 90);   /* dark text: white on amber fails contrast */
  --info: oklch(60% 0.22 293);
  --info-foreground: oklch(100% 0 0);

  /* lines + focus */
  --border: oklch(94% 0.004 286);
  --input: oklch(92% 0.004 286);
  --ring: oklch(71% 0.01 286);

  /* sidebar roles — override in .sidebar-dark for the dark-sidebar layout */
  --sidebar: var(--card);
  --sidebar-foreground: var(--foreground);
  --sidebar-muted: var(--muted-foreground);
  --sidebar-accent: var(--accent);
  --sidebar-accent-foreground: var(--accent-foreground);
  --sidebar-primary: var(--primary);
  --sidebar-border: var(--border);

  /* elevation — nearly flat by design */
  --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.06);

  /* app shell */
  --sidebar-width: 280px;
  --sidebar-width-collapsed: 80px;
  --header-height: 70px;
}

@media (max-width: 63.99rem) {
  :root { --header-height: 60px; }
}

.dark { --destructive-accent: oklch(60.25% 0.22 27); --primary-accent: oklch(59% 0.21 258);
  color-scheme: dark;

  --background: oklch(14.5% 0.005 285);
  --foreground: oklch(98.5% 0 0);
  --card: oklch(14.5% 0.005 285);
  --card-foreground: oklch(98.5% 0 0);
  --popover: oklch(14.5% 0.005 285);
  --popover-foreground: oklch(98.5% 0 0);

  --primary: oklch(55% 0.21 258);
  --primary-foreground: oklch(100% 0 0);

  --secondary: oklch(27.5% 0.006 286);
  --secondary-foreground: oklch(98.5% 0 0);
  --muted: oklch(21% 0.006 285);
  --muted-foreground: oklch(64% 0.014 285);
  --accent: oklch(21% 0.006 285);
  --accent-foreground: oklch(98.5% 0 0);
  --mono: oklch(87% 0.006 286);
  --mono-foreground: oklch(0% 0 0);

  --destructive: oklch(57.5% 0.22 27);
  --destructive-foreground: oklch(100% 0 0);
  --warning-foreground: oklch(92% 0.12 90);   /* light amber text on tinted warning fills in dark mode */

  --border: oklch(27.5% 0.006 286);
  --input: oklch(27.5% 0.006 286);
  --ring: oklch(44% 0.01 286);

  --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.4);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.5), 0 2px 4px -2px rgb(0 0 0 / 0.4);
}
```
Tailwind mapping — paste this too (generated from the token file, so no role is missing):
```css
@theme inline {
  --font-sans: var(--font-sans);
  --font-display: var(--font-display);
  --font-mono: var(--font-mono);

  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary); --color-primary-accent: var(--primary-accent);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-mono: var(--mono);
  --color-mono-foreground: var(--mono-foreground);
  --color-destructive: var(--destructive); --color-destructive-accent: var(--destructive-accent);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-success: var(--success);
  --color-success-foreground: var(--success-foreground);
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
  --color-info: var(--info);
  --color-info-foreground: var(--info-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-sidebar: var(--sidebar);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-muted: var(--sidebar-muted);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-border: var(--sidebar-border);
  --color-scrim: var(--scrim);

  --radius-xl: calc(var(--radius) + 4px);
  --radius-lg: var(--radius);
  --radius-md: calc(var(--radius) - 2px);
  --radius-sm: calc(var(--radius) - 4px);

  --shadow-xs: var(--shadow-xs);
  --shadow-md: var(--shadow-md);

  /* Easings: mapped so the system's curves replace Tailwind's own --ease-* and
     resolve through var(), which is how the reduced-motion override still
     reaches them. The tempo tokens are deliberately NOT mapped — a duration in
     a class attribute is the thing lint_motion.py refuses (see motion.md). */
  --ease-enter: var(--ease-enter);
  --ease-exit: var(--ease-exit);
  --ease-move: var(--ease-move);
  --ease-tint: var(--ease-tint);
  --ease-flat: var(--ease-flat);
  --ease-elapsed: var(--ease-elapsed);
  --ease-spring-ui: var(--spring-ui);
  --ease-spring-heavy: var(--spring-heavy);
}

@theme {
  /* the two extra UI sizes the system relies on */
  --text-2sm: 0.8125rem;
  --text-2sm--line-height: 1.3;
  --text-2xs: 0.6875rem;
  --text-2xs--line-height: 1.2;
}

@custom-variant dark (&:where(.dark, .dark *));
```

## 3. Personality presets (append one after the tokens, then change two dials)
- **theme-clinic** (calm, clinical, trustworthy (health, nutrition, insurance)):
```css
.theme-clinic {
  --font-display: "Manrope", var(--font-sans);          /* geometric, soft */
  --font-sans: "Manrope", ui-sans-serif, system-ui, sans-serif;
  --primary: oklch(50% 0.12 195);                        /* deep teal, 4.6:1 with white */
  --primary-accent: oklch(50% 0.12 195);               /* links: 5.16:1 */
  --primary-foreground: oklch(100% 0 0);
  --accent-strong: oklch(72% 0.17 60);                   /* one warm highlight: amber-peach */
  --background: oklch(98.5% 0.006 190);                  /* faint teal tint */
  --card: oklch(100% 0 0);
  --border: oklch(92% 0.012 190);
  --input: oklch(90% 0.014 190);
  --muted: oklch(96% 0.01 190);
  --radius: 0.75rem;
  --density: airy;                                       /* see density block below */
}
```
- **theme-graphite** (dense, technical, precise (fintech, ops, dev tools)):
```css
.theme-graphite {
  --font-display: "IBM Plex Sans", var(--font-sans);
  --font-sans: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, monospace;
  --primary: oklch(65% 0.17 150);                        /* signal green */
  --primary-accent: oklch(52.25% 0.17 150);            /* links: 4.52:1 */
  --primary-foreground: oklch(14% 0 0);
  --background: oklch(97% 0.002 260); --muted-foreground: oklch(54% 0.014 285);
  --card: oklch(100% 0 0);
  --border: oklch(88% 0.004 260);
  --radius: 0.25rem;
  --density: compact;
}
.theme-graphite.dark { --background: oklch(12% 0.004 260); --muted-foreground: oklch(60% 0.014 285); --card: oklch(15% 0.004 260); --border: oklch(24% 0.005 260); }
```
- **theme-editorial** (warm, human, content-first (community, education, media)):
```css
.theme-editorial {
  --font-display: "Fraunces", Georgia, serif;             /* serif display with optical sizing */
  --font-sans: "Source Sans 3", ui-sans-serif, system-ui, sans-serif;
  --primary: oklch(48% 0.16 30);                          /* brick */
  --primary-accent: oklch(48% 0.16 30);                /* links: 6.59:1 */
  --primary-foreground: oklch(98% 0.01 60);
  --background: oklch(97.5% 0.012 75);                    /* warm paper */
  --card: oklch(99% 0.008 75);
  --foreground: oklch(22% 0.02 50);
  --border: oklch(90% 0.02 70);
  --muted: oklch(94% 0.015 75);
  --muted-foreground: oklch(50% 0.03 50);
  --radius: 0.5rem;
  --density: standard;
}
```

## 4. The system in one screen
`bg-background text-foreground` page · `bg-card border-border` cards · `bg-popover` menus/modals ·
`bg-primary text-primary-foreground` the ONE action · `bg-secondary` / `bg-muted` / `bg-accent` fills ·
`text-mono` headings & numbers · `text-secondary-foreground` second lines · `text-muted-foreground` hints ·
`border-input` fields · `ring-ring` focus · states `success` `warning` `info` `destructive` (always with text/icon).

`text-primary-accent` is the brand colour **as text** (links, emphasised labels). `bg-primary` with `text-primary-foreground` is the brand colour as a fill. They are different values on purpose: a fill light enough to carry white text is too light to be read as text.

Controls: sm `h-7 px-2.5 text-xs` · md `h-8.5 px-3 text-2sm` · lg `h-10 px-4 text-sm`; all `rounded-md`.
Type: **Inter** (display + text, house default; Arabic companion Noto Sans Arabic) · body 13px `text-2sm` · labels `text-xs` · card title `text-base font-semibold tracking-tight text-mono` ·
page title `text-xl font-medium text-mono` · KPI `text-3xl font-semibold text-mono tabular-nums font-display`.
Rhythm: cards `gap-5 lg:gap-7.5` · inside rows `gap-2.5` · card padding `p-5` · radius `--radius` (cards +4px, chips −4px).
Shell: sidebar 280 (collapsed 80) · header 70 (60 mobile) · container `px-6 xl:px-7.5 xl:max-w-(--breakpoint-xl)`.

## 5. Recipes (exact class strings)
- **btn** `inline-flex items-center justify-center gap-1.5 shrink-0 whitespace-nowrap font-medium rounded-md shadow-xs h-8.5 px-3 text-2sm focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 [&_svg]:size-4`
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
- **skeleton** `rounded-md bg-accent` — static; it reserves height and nothing else. The wait itself is reported by the `.pends` elapsed bar, never by a pulse or a spinner. · **empty** icon chip `size-12 rounded-full bg-muted text-muted-foreground`, title `text-sm font-semibold text-mono`, text `text-2sm text-secondary-foreground`, one button
- **kbd** `inline-flex h-5 items-center rounded-sm border bg-muted px-1.5 font-mono text-2xs`
- **KPI card** icon chip `size-9 rounded-lg bg-primary/10 text-primary` · delta badge light-success/destructive with trend icon · value + label; optional 40px sparkline SVG
- **page toolbar** `flex flex-wrap items-center justify-between gap-5 pb-7.5` → title/subtitle · `flex gap-2.5` select · outline · ONE primary
- **grid** page `grid gap-5 lg:gap-7.5` · row `grid lg:grid-cols-3 … items-stretch`, wide card `lg:col-span-2`, every card `h-full`

## 6. Charts, i18n, weight
- **Charts**: ApexCharts with `apexBase()` from the scaffold: smooth area with gradient fill for trends, sparklines (`height: 40`) in KPI cards, donut with centre total, heatmap with printed values. Explicit pixel heights. Never hand-draw dashboard charts.
- **RTL + Arabic**: `dir` alone is not enough for an Arabic product: use the scaffold's `data-i18n` pattern (one dictionary, `setLang('ar')` flips `dir`, `lang` and every tagged string, numbers stay LTR). Translate nav, titles, KPI labels, legends, table headers and statuses.
- **Weight budget**: ≤ 2,300 DOM elements for a full console, ≤ 45 nesting depth, no wrapper divs around single children; 5 skeleton rows, not 12.
- **Production**: the Tailwind browser build and CDN scripts are for demos and prototypes; a shipped product compiles Tailwind and self-hosts fonts and Lucide.

## 7. Decision tables
Animate it? — only if something changed and the user needs to know what, where it went or where it came from; then use the recipe for that change, never a duration you chose. Decoration, page-enter reveals, count-ups and spinners are refusals.
Card or no card? — data with a title and a toolbar: card · a single sentence of help: plain text in the toolbar · a list inside a card: `divide-y`, never nested cards.
Which primary? — the one action the user came for (New order, Save, Book); Export/Filter/Import are outline; row actions ghost.

## 8. Rules that decide the grade
one primary per view · four states per async region (skeleton/empty/error/success) · `Esc` closes overlays, focus returns ·
`Ctrl/⌘+K` opens search · logical props only (`ps/pe/ms/me/start/end`, `rtl:rotate-180` on chevrons) · dark = `html.dark`, persisted ·
personality chosen and written to `design/personality.md` · never `@apply group` / `peer` · render once in headless Edge before done.

## 9. Anti-patterns — never do these
- ⚙ **Purple-to-blue gradients (indigo/violet)** → the single most recognised AI signature; carries no meaning → one primary with real chroma from the personality; gradients only as a 10% area fill in charts.
- ⚙ **Gradient text** → unreadable at small sizes, fails contrast tools, dates fast → solid `text-mono` headings; let size and weight do the work.
- ⚙ **Glass (backdrop-blur) on every card** → blurs content behind it, costs GPU, hides hierarchy → blur only on a sticky header or an overlay scrim.
- **Colour as decoration** (random tinted cards, rainbow badges) → users read colour as status; noise destroys the signal → colour only for the primary action, states and chart series.
- ⚙ **Pure `#000` text on white** → harsh, vibrates on dark mode inversion → `--foreground` near-black with a hint of the brand hue.
- **Grey text on coloured backgrounds** → fails contrast → white or the surface's own foreground token; check 4.5:1.
- **Inter/system font at one size everywhere** → nothing is first → the house scale: 13px UI, 16px card titles, 20px page title, 30px KPI numbers, 600 weight on titles.
- ⚙ **Uppercase letter-spaced "eyebrow" labels on every section** → visual tic; more than one per three sections reads as template → sentence-case section titles; eyebrows only for a category chip.
- **Thin weights (300) on small text** → illegible, especially on Windows → 400 minimum; 500/600 for emphasis.
- **Centred paragraphs longer than two lines** → hard to scan → left-aligned (start-aligned in RTL), `max-w-prose`.
- **Hero + three identical feature cards** → the landing-page template everyone recognises → bento with one hero card, real product screenshots, sections that differ in shape.
- ⚙ **`rounded-2xl` + `shadow-lg` on everything** → cards float like stickers; no grouping → `rounded-xl`, hairline border, `shadow-xs`; elevation only for popovers.
- **Cards inside cards** → borders within borders, wasted padding → sections with `border-b` inside one card.
- **Everything the same size in a grid** → no hierarchy → 2/3 + 1/3 rows; the most important number top-start and largest.
- **Empty page background with text floating on it** → looks unfinished → toolbar or card for every piece of text.
- **Uniform `p-6 gap-4` on every element** → no rhythm → cards `p-5`, rows `gap-2.5`, cards apart `gap-5/7.5`.
- ⚙ **Sparkles / Zap / Rocket icons for "AI" and "fast"** → cliché; says nothing → the icon of the object (invoice, patient, order) or none.
- **Icon-in-a-rounded-square on every card and list row** → decorative repetition → icon chips only on KPI cards and empty states.
- ⚙ **Emoji as icons** → inconsistent across platforms, not themable, screen readers read them aloud → Lucide at 16–20px.
- ⚙ **Generated avatar services (DiceBear)** → obviously fake → initials chips from the real name.
- **Stock photos of handshakes and laptops** → trust drops → product screenshots or no image.
- ⚙ **`transition: all`**, `transition-property: all`, `transition-all` → animates layout the moment a class adds padding → name the properties. (M03)
- ⚙ **Any Tailwind motion utility** — `transition*`, `duration-*`, `ease-*`, `delay-*`, `animate-*`, including inside `@apply` → motion scattered across markup cannot be reviewed or reduced → declare it in `motion.css`. (M02)
- **A literal duration or curve outside the token region** → six tempos nobody agreed on → `var(--t-*)`, `var(--ease-*)`. (M01)
- **`infinite`, `animation-iteration-count`, `animate-pulse|spin|ping|bounce|marquee`** → a loop reports nothing and fails WCAG 2.2.2 once it runs past five seconds beside other content → the finite elapsed bar, R10. (M09)
- **An animated property outside the compositor, discrete and paint tiers** → layout thrash → a `/* motion-exception: <selector> — <reason> */` line. There are exactly three in this system. (M03)
- **Animated `box-shadow`, `background-position`, `background-size`** → a repaint every frame → `opacity` on a shadow pseudo-element. (M03)
- **Animated `filter: blur()` on text** → illegible for the whole duration. (M03)
- **A transition on the focus ring** — `outline`, `outline-offset`, `box-shadow`, `border-color` under `:focus-visible` → a ring that lags the keyboard reads as input latency. (M03)
- **Any delay other than `0s` or `var(--t-grace)`**, and every stagger: a loop index, an `nth-child` ladder, `stagger(`, `sibling-index()` → a set arriving is one report, not N. (M11, M12)
- **The blanket `@media (prefers-reduced-motion: reduce) { * { …!important } }`** → it freezes loading indicators, never matches `::view-transition-*`, and proves no per-recipe answer was made → `--travel-on: 0` and `--motion-reduce: 0.7`. (M05)
- **An entrance at first paint** — an ungated `@starting-style`, `opacity: 0` in the initial viewport, anything animating within 200ms of load → it animates the page's own arrival and holds the LCP candidate invisible. (M11, V08)
- **Scroll-triggered reveal** — `data-aos`, `AOS.init(`, `whileInView`, `useInView`, an IntersectionObserver writing opacity, `pointer-events: none` as a reveal gate → it reports the viewport moving, not anything changing. `animation-timeline` is permitted on `.read-progress` and `.app-seam::after` and nowhere else. (M10)
- **Scroll hijack and parallax** — Lenis, Locomotive, ScrollSmoother, `ScrollTrigger` with `pin:`/`scrub:`, a `wheel` listener calling `preventDefault()`, `background-attachment: fixed`, `data-speed` → the scrollbar stops telling the truth. (M10)
- **Pointer-driven motion** — magnetic buttons, tilt cards, cursor followers, `cursor: none` → it reports the pointer, and it does not exist on a keyboard. (M08)
- **Per-character or per-word text splitting** → it breaks Arabic letter joining, which makes it a correctness bug and not a taste argument. (M14)
- **A count-up, an odometer, a JavaScript loop writing `textContent`** → a false number in the DOM that assistive technology announces and copy captures → write the true value, then mark it changed. R8. (M14)
- **rAF or a timer writing a motion style**, and `.animate(`, `startViewTransition(` or `view-transition-name` outside the one identity module → JavaScript declares a delta; it never draws a frame. (M08)
- **Overshoot** — a `linear()` stop above 1, a `cubic-bezier` control point outside 0–1 → on a clamped value it is a visible dead hold, not a bounce. (M13)
- **`will-change` in a static stylesheet** → a hint that cannot know when it stopped being true. (M08)
- **Motion as the only delta** → if two states differ only in that one of them moved, the motion was decoration. (V06)
- **Any animation dependency**: gsap, framer-motion, motion, motion-one, aos, lenis, locomotive-scroll, canvas-confetti, tsparticles, tw-animate-css, tailwindcss-animate. (M08)
- **A chart that draws itself in** → motion at first paint → ApexCharts with `animations: { enabled: false }`. (M01)
- **Skeletons that never end / spinners for everything** → users cannot tell loading from broken → a static skeleton at the real row height plus the finite elapsed bar, and an error state with retry after timeout. (M09)
- ⚙ **"Elevate", "Seamless", "Unleash", "Supercharge"** → marketing filler inside a product → verbs and nouns of the domain; sentence case.
- **Lorem ipsum, "John Doe", `user@example.com`, round fake metrics (1,000 users, 99%)** → reads as a mock-up → realistic names for the market, uneven numbers, a comparison line under each KPI.
- **No empty / loading / error states** → the first real user sees a blank → four states per async region.
- **"Submit" / "OK" buttons** → say nothing → "Save changes", "Send invite", "Delete plan".
- **Colour-only status** (green dot, red dot) → invisible to 8% of men, fails audits → text or icon with the colour.
- ⚙ **Icon buttons without a name** → screen readers announce "button" → `aria-label`.
- **No personality file** → the default look shipped → `design/personality.md` first.
- **Hand-drawn SVG charts** → look unfinished next to a real chart library → ApexCharts with the token theme.
- **Composed from scratch instead of the scaffold** → 3× the tokens and more bugs → `build-screen.py` or `new_screen.py`, then edit.

## Without tools (manual checklist)
If you cannot run scripts, apply by hand before you finish:
1. Search your markup for raw palette classes (`bg-blue-500`, `text-gray-600`, hex colours) — replace with roles.
2. Count primary buttons outside the nav: exactly one per view.
3. Every icon-only button has `aria-label`; a skip link exists when there is a nav; one `<h1>`.
4. No purple/indigo gradients, gradient text, Sparkles/Zap icons, emoji icons, `transition: all`, filler words (Elevate, Seamless, Unleash).
5. Contrast: text on background and white on primary ≥ 4.5:1 (check with any contrast tool).
6. Four states per async region: loading skeleton, empty with an action, error with retry, success.
7. Open the page once in light, dark and RTL before calling it done.
