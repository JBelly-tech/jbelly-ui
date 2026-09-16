# jbelly-ui — UI rules for this project (generated from the jbelly-ui skill; do not edit by hand)

You are building or changing a web UI. Follow these rules exactly; values are not suggestions.

## Before any code: the design read (4 fields)
`kind` (dashboard / settings / landing / …) · `audience` (who, how often, keyboard or touch) · `vibe` (three words) · `system` (preset + dials changed). Keep it in `design/personality.md`. Never ship the default look.

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

## Rules that decide the grade
one primary per view · four states per async region (skeleton/empty/error/success) · `Esc` closes overlays, focus returns ·
`Ctrl/⌘+K` opens search · logical props only (`ps/pe/ms/me/start/end`, `rtl:rotate-180` on chevrons) · dark = `html.dark`, persisted ·
personality chosen and written to `design/personality.md` · never `@apply group` / `peer` · render once in headless Edge before done.

## Anti-patterns (never)
- ⚙ **Purple-to-blue gradients (indigo/violet)** → the single most recognised AI signature; carries no meaning → one primary with real chroma from the personality; gradients only as a 10% area fill in charts.
- ⚙ **Gradient text** → unreadable at small sizes, fails contrast tools, dates fast → solid `text-mono` headings; let size and weight do the work.
- ⚙ **Glass (backdrop-blur) on every card** → blurs content behind it, costs GPU, hides hierarchy → blur only on a sticky header or an overlay scrim.
- ⚙ **Pure `#000` text on white** → harsh, vibrates on dark mode inversion → `--foreground` near-black with a hint of the brand hue.
- ⚙ **Uppercase letter-spaced "eyebrow" labels on every section** → visual tic; more than one per three sections reads as template → sentence-case section titles; eyebrows only for a category chip.
- ⚙ **`rounded-2xl` + `shadow-lg` on everything** → cards float like stickers; no grouping → `rounded-xl`, hairline border, `shadow-xs`; elevation only for popovers.
- ⚙ **Sparkles / Zap / Rocket icons for "AI" and "fast"** → cliché; says nothing → the icon of the object (invoice, patient, order) or none.
- ⚙ **Emoji as icons** → inconsistent across platforms, not themable, screen readers read them aloud → Lucide at 16–20px.
- ⚙ **Generated avatar services (DiceBear)** → obviously fake → initials chips from the real name.
- ⚙ **`transition: all`** → animates layout properties, janky, accidental → transition colour/opacity/transform only, 150ms.
- ⚙ **"Elevate", "Seamless", "Unleash", "Supercharge"** → marketing filler inside a product → verbs and nouns of the domain; sentence case.
- ⚙ **Icon buttons without a name** → screen readers announce "button" → `aria-label`.

## Without tools (manual checklist)
If you cannot run scripts, apply by hand before you finish:
1. Search your markup for raw palette classes (`bg-blue-500`, `text-gray-600`, hex colours) — replace with roles.
2. Count primary buttons outside the nav: exactly one per view.
3. Every icon-only button has `aria-label`; a skip link exists when there is a nav; one `<h1>`.
4. No purple/indigo gradients, gradient text, Sparkles/Zap icons, emoji icons, `transition: all`, filler words (Elevate, Seamless, Unleash).
5. Contrast: text on background and white on primary ≥ 4.5:1 (check with any contrast tool).
6. Four states per async region: loading skeleton, empty with an action, error with retry, success.
7. Open the page once in light, dark and RTL before calling it done.
