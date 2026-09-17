---
name: jbelly-ui
license: MIT
description: "Licence-free UI system for web apps and sites: build, review or redesign dashboards, admin panels, settings/auth, tables and landing pages with exact tokens, a spec-driven page builder, a pre-flight against AI-default looks, and a mandatory personality step. Not for backend, API or non-visual work."
---

# jbelly-ui — the house UI system

A complete design system expressed as **rules and recipes**: exact sizes,
class strings, behaviours and checklists. Nothing here depends on a purchased
template or a per-project licence, so it ships in any number of products.

Two layers, and both are mandatory:

1. **Foundation** (shared by every product): semantic tokens, app shell, exact
   component sizes, admin-grade behaviours. This is what makes a UI feel like
   a paid template — every state handled, nothing shifts, keyboard works.
2. **Personality** (unique per product): type pairing, palette, shape,
   density, surface, motion, one signature element. This is what stops every
   AI-built product from looking like the same site in a different colour.

Stack-neutral: tokens are CSS variables, recipes are Tailwind v4 utility
strings that map 1:1 to CSS.

## Modes

| Mode | Trigger | Path |
|------|---------|------|
| **Build** | "make / add / create a page, dashboard, form…" | workflow below |
| **Review** | "review / critique / audit / does this look professional" | `references/review-rubric.md`: run `scripts/preflight.py` + `scripts/verify_page.py`, score ten dimensions once, report `file:line` rows. No second opinions, no subagents. |
| **Redesign** | "restyle / modernise / make it look like…" | `scripts/audit_styles.py` first, then personality, then fix in priority order (fonts → colour → radius/shadow → spacing → states → motion). |

**Design read (first output in every mode).** Before any code or verdict,
emit four fields and keep them in `design/personality.md`:
`kind` (dashboard / settings / landing / …), `audience` (who, how often,
keyboard or touch), `vibe` (three words), `system` (preset + dials changed).
It is the contract everything else is checked against.

## Workflow

**Cost first.** The references total ~28K tokens; every tool call after
reading them re-sends them. So: for a standard app screen read only
`references/quick-card.md` (~1.2K tokens) plus the one personality preset you
need, in a single batch at the start. Then **generate, do not compose**:
write a ~2 KB JSON spec (see `assets/spec.example.json`) and run
`python scripts/build-screen.py spec.json out.html` — nav, toolbar, KPIs with
sparklines, chart, highlights donut, table with states, activity, i18n all
come from the shell for zero model tokens; add only bespoke widgets as
`extra_html` or by editing the built file. (For a blank shell use
`python scripts/new_screen.py`.) Write once; verify once with
`python scripts/verify_page.py <page>` (render + console + lint + pre-flight in one call). Open a full reference only for something the card and scaffold do not
cover. Budget: no more than 12 tool calls per screen. Implementation belongs
to the cheapest model class that passes the done list (Class B); reserve the
top class for the personality decision and the final review.

1. **Choose the personality first** — `references/personalities.md`. Pick the
   closest preset and change at least two dials, or derive one from the brief.
   Write it to `design/personality.md` in the product. Never start on the
   default look; the default exists only so the demo renders.
2. **Install the tokens** — copy `references/tokens.css` into the project,
   load it right after Tailwind (`@import "tailwindcss"; @import "./tokens.css";`),
   append the personality overrides. To change a colour later, edit a token,
   never a component.
3. **Pick a shell** — `references/layouts.md`: app shell (sidebar + header),
   header-only, auth, or landing. Copy the skeleton.
4. **Build with the recipes** — `references/components.md` for controls,
   `references/patterns.md` for screens. Every element has a recipe with
   exact sizes; that is what keeps mixed rows aligned and ten screens coherent.
5. **Wire the behaviours** — `references/ux-behaviours.md`. Loading, empty and
   error states, table selection and bulk actions, form validation, overlay
   focus rules, keyboard, persistence. Not optional.
6. **Lint and check** — `python scripts/lint_tokens.py <src-dir>` (or the
   PowerShell twin `scripts/lint-tokens.ps1`) flags raw palette classes that
   bypass tokens. Then the done list below.

Want to see it first? Open `assets/app-shell.html` — a self-contained page
with the shell, the core recipes, dark mode and a personality switcher.

Reviewing an existing UI? Run steps 6 → 5 → 1 in that order: lint, then
compare behaviours, then ask whether the product has a personality at all.

## The foundation in one screen

**Semantic colour tokens, never raw palette.** Components reference roles
(`bg-card`, `text-muted-foreground`, `border-border`); the roles are
redefined once under `.dark` and once per personality. This is why dark
mode and re-branding cost nothing.

| Role | Used for |
|------|----------|
| `background` / `foreground` | the page |
| `card` / `popover` (+ `-foreground`) | cards, panels, header, sidebar / dropdowns, modals |
| `primary` / `primary-foreground` | the single brand action colour, active nav |
| `secondary` · `muted` · `accent` (+ `-foreground`) | secondary buttons and badges · subtle fills and helper text · hover and selected fills |
| `mono` / `mono-foreground` | strongest text (headings, KPI numbers), tooltips |
| `destructive` · `success` · `warning` · `info` | states — always with text or an icon, never colour alone |
| `border` · `input` · `ring` | hairlines · field borders · focus |
| `sidebar-*` | lets the sidebar carry its own palette (dark sidebar on a light page) |

**Rhythm.** 4px base unit. `--radius` per personality (default 0.5rem);
cards `radius + 4px`, controls `radius − 2px`, chips `radius − 4px`. Cards
sit in a grid with `gap-5 lg:gap-7.5`; rows inside use `gap-2.5`. Container
max 80rem, `px-6 xl:px-7.5`.

**Type.** Inter for display and text by default (the look of the best-selling admin templates), weights 400 / 500 / 600 only; a display face only for a brand reason.
UI is small and dense: controls and body at **13px** (`text-2sm`), labels
`text-xs`, card titles `text-base font-semibold tracking-tight`, page titles
`text-xl font-medium`, KPI numbers `text-3xl font-semibold text-mono` in the
display face. Headings `text-mono`, body `text-foreground`, secondary lines
`text-secondary-foreground`, hints `text-muted-foreground`. Numbers
`tabular-nums`.

**Elevation is nearly flat.** Hairline border + `shadow-xs` on cards,
buttons, inputs; `shadow-md` on popovers; nothing else. Depth comes from
borders and `muted` / `accent` fills. (A personality may swap this for
elevated or outlined surfaces — deliberately, everywhere.)

**Control sizes** (buttons, inputs, selects, add-ons share them exactly):

| Size | Height | Padding-x | Font |
|------|--------|-----------|------|
| sm | 28px `h-7` | `px-2.5` | 12px `text-xs` |
| md | 34px `h-8.5` | `px-3` | 13px `text-2sm` |
| lg | 40px `h-10` | `px-4` | 14px `text-sm` |

Density presets (compact / standard / airy) scale these together; see
personalities.md.

**Layout.** Sidebar 280px (collapses to 80px, peeks on hover), header 70px
desktop / 60px mobile, both fixed; sidebar becomes a drawer below `lg`.
Logical properties throughout (`ps-`, `pe-`, `start-`, `inset-inline-*`), so
RTL is `dir="rtl"` on `<html>` and nothing else — essential for Arabic products.

**Charts.** ApexCharts (MIT) themed from tokens (`references/charts.md`): smooth gradient areas, sparklines in KPI cards, donuts with a centre total, heatmaps with printed values. This is the chart look buyers of the best-selling templates expect; hand-drawn SVG charts read as unfinished.

**Icons.** Lucide (MIT) at 16–20px, stroke-width 2, colour inherits. Never
a per-project-licensed icon set; never emoji.

## Rules

- **Colour comes from tokens.** Raw palette classes are allowed in exactly one
  file: `tokens.css` (and the personality block). The lint enforces this.
- **Recipes are HTML class strings.** If you move one into CSS with `@apply`,
  drop `group` and `peer` (they are markers, not utilities — Tailwind v4 fails
  the whole stylesheet with "Cannot apply unknown utility class") and write
  `.parent:hover .child` selectors instead. Always open the page once in a
  browser (or headless Edge/Chrome with `--screenshot`) before calling it done;
  a compile error renders as an unstyled page, not as a warning.
- **One primary per view.** The brand colour marks the single main action and
  the active nav item. Everything else is `secondary`, `outline` or `ghost`.
- **Cards are the unit of layout**; no cards inside cards — use bordered
  sections. No bare text on the page background.
- **Tables are dense, forms are calm.** Tables 13–14px, ~46px rows, hairline
  row borders, no zebra. Forms one column, labels above, `gap-5`.
- **Every async region has four states**: loading (skeleton), empty (with next
  action), error (what happened + retry), success.
- **Status is never colour alone.** Text or an icon accompanies every colour.
- **Dark mode is a class** (`html.dark`), persisted, and every screen is
  checked in both modes.
- **Motion is 150ms ease-out** on colour / opacity / transform; the sidebar
  collapse is the one 300ms transition; a personality may add **one**
  signature moment. `prefers-reduced-motion` is honoured by tokens.css.
- **Anti-defaults** (the AI-generic tells — refuse them unless the personality
  chose them on purpose): blue-600 primary ·
  untouched zinc greys · `rounded-2xl shadow-lg` on everything · purple/blue
  gradients or gradient text · glassmorphism by reflex · icon-in-a-rounded-square
  on every card · hero + three feature cards · uniform `gap-4 p-6` with no
  hierarchy · `Sparkles`/`Zap` icons · "Elevate / Seamless / Powerful" copy ·
  emoji as icons · DiceBear avatars.
- **Never paste code, CSS, images, fonts or icons from a commercial
  template** into a product, even one the team owns a licence for — licences
  are per project and per deployment. Build from these recipes; look at
  templates only for layout ideas.
- **Libraries must be MIT/BSD/Apache-licensed** and styled through tokens —
  see `references/integrations.md` for the vetted list per need (charts,
  tables, calendars, editors, uploads, maps, drag-and-drop).

## Working alongside `ui-ux-pro-max`

If that skill is installed, it is a catalogue (styles, 192 palettes, 74 font
pairings, 119 UX rules); this skill is the system. Use them together like
this: run its `--design-system` search **only** to shortlist a type pairing or
palette for step 1, then encode the choice as jbelly-ui tokens in
`design/personality.md`. Its `MASTER.md` must not define colours that
`tokens.css` does not; on any conflict, tokens.css wins. Do not adopt a
"style" it names (glassmorphism, neumorphism…) unless the personality dials
call for it — that is exactly how products end up looking random.

## Without tools (manual fallback)

If scripts cannot run in your environment, do these by hand before finishing:
search the markup for raw palette classes and hex colours and replace them
with roles; count primary buttons outside the nav (exactly one); give every
icon-only button an `aria-label`, add a skip link when there is a nav, keep one
`<h1>`; remove purple/indigo gradients, gradient text, Sparkles/Zap icons,
emoji icons, `transition: all` and filler words; check text-on-background and
white-on-primary contrast (4.5:1 or better); confirm four states per async
region; open the page once in light, dark and RTL.

## Reference files

| File | Read when |
|------|-----------|
| `references/quick-card.md` | **First, for any standard app screen**: tokens, sizes and the 20 most-used recipes on one page, plus the cost rules. Usually the only reference you need together with the scaffold. |
| `scripts/verify_page.py` (`verify-page.ps1` on Windows) | The one verification call before done: renders variants headlessly (Playwright, or Chrome/Chromium/Edge), reports console errors, runs the token lint, prints PASS/FAIL. Replaces multi-step verify loops. |
| `scripts/build-screen.py` + `assets/spec.example.json` | **The default build path**: a small JSON spec in, a complete verified-pattern page out (charts, table states, drawer, palette, i18n included). Edit the output only for bespoke widgets. |
| `scripts/new_screen.py` (`new-screen.ps1` on Windows) | A blank copy of the shell with personality, density, direction and dark default set, when the page is unlike a dashboard. |
| `references/review-rubric.md` | Review and Redesign modes: ten scored dimensions with evidence, the `file:line` output format, the audit-first protocol. |
| `scripts/preflight.py` | Any mode, before done: AI-tells list (gradient purple, gradient text, Sparkles icons, filler copy, emoji icons…), structure checks (one primary, h1, skip link, labelled icon buttons), WCAG contrast of the token pairs. Runs inside `verify_page.py`. |
| `scripts/audit_styles.py` | Redesign mode, first: inventory of fonts, colours, radii, shadows, spacing, durations, raw palette classes; prints the deviation list in fix order. |
| `references/interface-guidelines.md` | Building or reviewing any control: the exact-value rules for forms, focus, motion, typography, colour, layout, copy, accessibility and performance, restated from the most-used interface guidelines. |
| `references/anti-patterns.md` | When a page looks generated, or in Review mode: each tell, why it fails, what to do instead; the marked ones are checked by `preflight.py`. |
| `references/stacks.md` | When the project is not Tailwind v4: the same recipes in plain CSS and React; DTCG tokens (`assets/tokens.json`, built by `scripts/export_tokens.py`). |
| `references/sources.md` | To check or add a rule: which research, design system or measured run each rule family comes from. |
| `references/charts.md` | Any chart: the ApexCharts house theme (from tokens), 8 chart recipes, the rules (heights, legends in card headers, sr-only tables, dark re-render). |
| `references/personalities.md` | Step 1, always. Eight dials, six presets with token overrides, density block, how to derive a new one, the persisted file format. |
| `references/tokens.css` | Step 2. Light/dark roles, states, sidebar roles, radius scale, Tailwind v4 `@theme` mapping, base resets, reduced-motion. |
| `references/layouts.md` | Step 3. App shell, sidebar nav, header bar, collapse + mobile drawer, page toolbar, grids, settings variants, profile hero, header-only shell, auth pages, landing page order, containers, RTL. |
| `references/components.md` | Step 4. Button, input, select, textarea, checkbox, radio, switch, label, badge, avatar, card, table, tabs, dropdown, modal, drawer, alert, toast, tooltip, progress, skeleton, pagination, breadcrumb, kbd, separator, link, empty state — exact class strings. |
| `references/patterns.md` | Step 4. KPI cards, callout, chart card, table card with toolbar, list card, progress list, activity feed, notification drawer, settings form, datatable page, pricing, checkout, search palette, cards grid, empty/error states, dashboard blueprint. |
| `references/ux-behaviours.md` | Step 5. Navigation, loading & feedback, tables, forms, overlays, keyboard, dashboards, responsive, preferences, copy, behaviour checklist. |
| `references/integrations.md` | Any time a screen needs a chart, data grid, calendar, date picker, rich-text editor, file upload, map, drag-and-drop, command palette, toasts, forms/validation, i18n or animation: the licence-safe library per need, how to style it with tokens, and the interaction rules (state layers, motion durations, density steps). |
| `references/industry-playbooks.md` | Step 3–4 when the product is a known business type (SaaS, admin/ops, e-commerce, clinic/wellness, restaurant, education, real estate, finance, travel, corporate/agency): the page inventory, the flows, and the patterns buyers of top-selling templates consistently expect. |
| `assets/app-shell.html` | A working, self-contained starting point and visual check (dark mode, RTL, personality switcher). |
| `scripts/lint_tokens.py` (`lint-tokens.ps1` on Windows) | Step 6. Finds raw palette colours outside the token file. |

## Done list

- [ ] `design/personality.md` exists and differs from the default (and from the last product built).
- [ ] `tokens.css` loads first; no other file defines `--primary`; lint passes.
- [ ] Light, dark, `dir="rtl"`, and 375 / 1024 / 1440px checked.
- [ ] Four states per async region; one active nav item; one primary per view.
- [ ] Tables: sort, filter chips, pagination text, bulk bar, hover row actions reachable by keyboard.
- [ ] Forms: labels above, inline errors, focus to first error, dirty guard.
- [ ] Overlays: focus trap, `Esc`, focus return, scroll lock.
- [ ] Icons all Lucide/inline SVG; no template assets; no emoji icons; every dependency on the vetted list.
