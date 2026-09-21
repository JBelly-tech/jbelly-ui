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

**Three calls build a standard screen. Make exactly these, in this order.**

```bash
python scripts/personality_init.py --product "<name>" --kind <kind> --audience "<who, how often>" \
    --vibe "<three words>" --preset <theme-…> --change "<dial>" --change "<dial>"
python scripts/build-screen.py <spec.json> <out.html>
python scripts/verify_page.py <out.html>
```

The spec's `kind` picks the template: **`"app"`** (the default) an application screen, **`"landing"`**
a marketing home page, **`"pricing"`** plans with a billing toggle and a comparison table. Writing a
landing or a pricing page by hand measured 1.6x and 5.9x the cost of a generated dashboard, so the
spec comes first and hand-written markup only for a page none of the three fits.

Before them, read **one** file: `references/quick-card.md`. Before writing the spec, get its shape
from `python scripts/build-screen.py --example`, which prints a complete annotated spec — add
`--kind landing` or `--kind pricing` for those.

**What not to do, because each one was measured costing calls for nothing:**

- **Do not read the same file twice.** Reading a reference, then `cat`-ing it, then opening it again
  is three calls and three copies of it in context, which every later call re-sends.
- **Do not probe the environment.** No `python --version`, no `pwd && ls`, no shell test. Run the
  command; if the interpreter is missing you will be told, and the manual fallback below applies.
- **Do not read the source of the scripts or of the shells in `assets/`.** `--example` tells you the
  spec, `--help` tells you the flags, and the shells' contents are not your concern: the generator
  fills them from the spec and fails loudly when a field does not land.
- **Do not hand-edit the built page to add what the spec could have said.** If a value came out
  wrong, fix the spec and rebuild: one call instead of a chain of edits. Hand-editing is only for
  genuinely bespoke markup, appended through `extra_html`.
- **Do not build your own verification.** `verify_page.py` renders the variants, collects console
  errors, runs the token lint and the pre-flight, and prints one verdict. No screenshot loop, no
  second opinion, no subagents.

Why this is worth obeying: agent cost is the size of the context multiplied by the number of steps,
so a file read early is paid for again on every later call. The generator exists to move the whole
page out of the model's output entirely — nav, toolbar, KPIs with sparklines, chart, donut, table
with its loading, empty and error states, activity feed and the Arabic dictionary all come from the
shell at zero model tokens — and, on the other two kinds, a hero, logo strip, numbered feature
sections, testimonial and FAQ, or plan cards, the billing toggle and a comparison table.

**When the screen is none of the three kinds:** `python scripts/new_screen.py` gives a blank shell
with the personality, density, direction and dark default already set. Everything above still applies.

**When a reference is genuinely needed:** open one, by name, from the table at the end of this file,
and only for something the quick card does not cover. Reading them all costs about 28K tokens.

Implementation belongs to the cheapest model class that passes the done list; reserve the top class
for the personality decision and the final review.

### When the generator does not apply

A page none of the three kinds has a shape for (a checkout, a bespoke app screen) is built by hand.
The order matters, because each step decides the one after it:

1. **Personality first.** Pick a preset from the quick card's table and change at least two dials,
   then write it with `personality_init.py`. Never start on the default look; the default exists so
   the demo renders, nothing more. Open `references/personalities.md` only to derive a new preset.
2. **Tokens next.** Copy `references/tokens.css` into the project and load it right after Tailwind
   (`@import "tailwindcss"; @import "./tokens.css";`), then append the personality overrides. A
   colour changes in one token, never in a component.
3. **Then the shell**, from `references/layouts.md`: sidebar + header, header-only, auth, or
   landing.
4. **Then the parts**: `references/components.md` for controls, `references/patterns.md` for whole
   screens. Every element has exact sizes; that is what keeps mixed rows aligned and ten screens
   looking like one product.
5. **Then the behaviours**, from `references/ux-behaviours.md`: loading, empty and error states,
   table selection and bulk actions, form validation, overlay focus, keyboard, persistence. Not
   optional — they are most of what separates this from a mock-up.
6. **Then verify**, the same single call as always: `python scripts/verify_page.py <page>`.

Reviewing an existing UI instead? Run it backwards: verify first for the deterministic faults, then
compare behaviours, then ask whether the product has any personality at all.

## The foundation in one screen

Everything below is spelled out with exact values in `references/quick-card.md`;
this is the shape of it.

- **Semantic colour roles, never raw palette**: `background/foreground`, `card`,
  `popover`, `primary` (the single brand action), `secondary`, `muted`, `accent`,
  `mono` (strongest text), `destructive/success/warning/info` (always with text
  or an icon), `border/input/ring`, `sidebar-*`. Roles are redefined once under
  `.dark` and once per personality; that is why dark mode and re-branding cost nothing.
- **Rhythm**: 4px unit; `--radius` per personality (cards +4px, controls −2px,
  chips −4px); cards `gap-5 lg:gap-7.5`, rows `gap-2.5`; container max 80rem.
- **Type**: Inter for display and text by default (weights 400/500/600), UI at
  13px, card titles 16px semibold tracking-tight, page title 20px, KPI numbers
  30px semibold `tabular-nums`; a display face only for a brand reason.
- **Controls share three sizes**: 28 / 34 / 40px high with 12 / 13 / 14px text,
  so mixed rows always align. Density presets scale them together.
- **Elevation nearly flat**: hairline border + `shadow-xs` on cards, buttons,
  inputs; `shadow-md` on popovers; nothing else.
- **Layout**: sidebar 280px (80px collapsed, peeks on hover), header 70px (60px
  mobile), both fixed; sidebar is a drawer below `lg`; logical properties only,
  so RTL is `dir="rtl"` and nothing else.
- **Charts**: ApexCharts themed from tokens (`references/charts.md`). **Icons**:
  Lucide 16–20px, stroke 2; never per-project-licensed sets, never emoji.

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

Open one, by name, only for what the quick card does not cover. Reading them all costs ~28K tokens.

**Scripts** (`scripts/`, all `--help`):
`build-screen.py` spec to page, `--kind app|landing|pricing` · `new_screen.py` blank shell ·
`verify_page.py` the one verification
call · `preflight.py` AI-tells, structure, contrast · `lint_tokens.py` raw palette colours ·
`audit_styles.py` redesign inventory · `personality_init.py` the design read ·
`export_tokens.py` DTCG tokens · `build_dist.py` the delivery tiers.
Windows twins: `verify-page.ps1`, `new-screen.ps1`, `lint-tokens.ps1`.

**References** (`references/`):

| Open when you need | File |
|---|---|
| anything on a standard screen | `quick-card.md` |
| to derive a new personality | `personalities.md` |
| the colour system to copy into a project | `tokens.css` |
| a control's exact class string | `components.md` |
| a shell, nav, toolbar, settings, auth or landing skeleton | `layouts.md` |
| a whole pattern: KPI row, chart card, table page, pricing, checkout, palette | `patterns.md` |
| a chart | `charts.md` |
| states, tables, forms, overlays, keyboard, responsive behaviour | `ux-behaviours.md` |
| a library for charts, grids, calendars, editors, uploads, maps | `integrations.md` |
| the pages and flows a known business type expects | `industry-playbooks.md` |
| exact-value rules for forms, focus, motion, type, colour, copy | `interface-guidelines.md` |
| to explain why a page looks generated | `anti-patterns.md` |
| to score a review | `review-rubric.md` |
| plain CSS or React instead of Tailwind | `stacks.md` |
| where a rule comes from | `sources.md` |

`assets/app-shell.html`, `landing-shell.html` and `pricing-shell.html` are the working demos behind
the three kinds; `assets/spec.example.json`, `spec.landing.example.json` and
`spec.pricing.example.json` are what `--example` prints for each.

## Done list

- [ ] `design/personality.md` exists and differs from the default (and from the last product built).
- [ ] `tokens.css` loads first; no other file defines `--primary`; lint passes.
- [ ] Light, dark, `dir="rtl"`, and 375 / 1024 / 1440px checked.
- [ ] Four states per async region; one active nav item; one primary per view.
- [ ] Tables: sort, filter chips, pagination text, bulk bar, hover row actions reachable by keyboard.
- [ ] Forms: labels above, inline errors, focus to first error, dirty guard.
- [ ] Overlays: focus trap, `Esc`, focus return, scroll lock.
- [ ] Icons all Lucide/inline SVG; no template assets; no emoji icons; every dependency on the vetted list.
