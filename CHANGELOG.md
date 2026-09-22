# Changelog

## Unreleased

**The default palette stops shouting.** `--primary` was chroma 0.2 on a white page and 0.21 on
near-black, which made it the loudest object on every screen the system produces — a template's
accent, not a considered one. It is now deeper and much less saturated, and the dark-mode link
colour gets lighter rather than more saturated, because a dark ground amplifies chroma and not
lightness. Every pair ends up with more contrast than it had: the dark link role went from 4.53:1
to 6.88:1. `--info`, a chroma-0.22 violet on a system that bans purple-to-blue gradients by name,
came down with it. Hues, roles and foregrounds are unchanged, so nothing needs re-mapping.

**The site has an Arabic edition.** The page had been telling people the demos ship AR/EN with full
RTL while existing only in English. The translations are markup in a `<template>` rather than
strings in a table, so a paragraph keeps its `<strong>`, its `<code>` and its links; a template is
parsed and never rendered, so the Arabic costs no layout and no font file until someone presses the
button. Each preset keeps its voice in Arabic — the serif preset stays a serif — and the product
captures follow the page, so a reader who switches to Arabic is shown the demo in Arabic. The smoke
test checks that every element asking for a translation has one, that no translation is unused, and
that switching back restores the served markup byte for byte.

**The storefront is on the site**, with its own section and a capture, instead of being the third of
four small buttons.

## 0.6.0-beta.1 — 2026-09-22

**A motion system, and a linter that refuses decoration.** Motion here reports a state change and
nothing else: every animating element declares its cause from a closed set of six, and an animation
whose target resolves no cause is decoration by definition. It is declared in `references/motion.css`
rather than computed in JavaScript, which is what makes it checkable — a stylesheet cannot animate on
a timer or on scroll position unless someone writes a timeline for it, so nothing moves by default.
`lint_motion.py` implements fourteen source rules and `verify_motion.py` eight runtime ones, both
built against 107 fixtures: one per rule for the smallest source that should trip it, and one for the
legitimate code that most resembles a violation. `prefers-reduced-motion` removes the travel and
shortens the tempo while opacity, colour and position keep carrying the message, with four named
exceptions where the position *is* the state.

**`check_controls.py`: every control is driven, so "everything works" stops being a promise.** It
activates every button, menu item, tab, radio, summary and same-page link in a real browser, each in
its own browser context so nothing the last one chose is remembered, and fails on any control that
produces no change. Getting it to tell the truth took five corrections, every one of them the tool
being wrong rather than a page: an empty fragment counted as a navigation, focus landing on the
control you just clicked counted as evidence, a `<select>` was clicked rather than changed, an
`sr-only` radio behind a visible label was driven directly, and the sweep depended on the order it
happened to run in. It then found real dead controls in four of the five shipped pages.

**A storefront demo**, `assets/commerce-shell.html`: browse, filter, sort, search, quick view,
variants with out-of-stock combinations disabled, a cart with promo codes and undo, and a four-step
checkout that validates — all client-side, one file. Six independent testers reported 119 defects and
sixteen of them were one bug: a region repainted with `innerHTML` deletes the node the reader is
holding, so focus falls to the body. One focus layer replaced sixteen patches.

**Two page shapes joined the builder.** `--kind landing` and `--kind pricing` build from their own
spec schemas, so the two briefs that cost the most — a pricing page measured six times a dashboard —
are generated rather than typed. The app kind is byte-identical to before.

**A colour used as text is now checked as text.** The pre-flight compared the pairs a page declares,
so a page painting links with `text-primary` and never declaring `--primary-accent` had nothing
compared at all: three shells shipped links at 3.96:1 in dark mode. It now reads the roles the markup
actually paints text with. The same check then caught `--destructive` failing as error text, which is
the one sentence a reader most needs to read. Both roles have a readable form derived per scope.

**The pre-flight's cascade model was wrong** and only the new role exposed it: it walked the
stylesheet top to bottom and let the last matching block win, so a `.theme-x` block written below a
`.theme-x.dark` block overrode it. Checked against a real engine before changing anything.

**Every published number points at a file.** `evals/records/` carries the run each figure comes from,
as the agent CLI reported it. Three numbers did not survive that and were withdrawn rather than
restated — including a before-and-after pair that flattered this project, because the harness that
produced it denied every condition access to its own skill directory.

**The site is the product.** `index.html` is built from the skill's own tokens, rethemes itself
through the same six presets, and is held to the skill's own lint, pre-flight, motion checks and
control driver in CI.

## 0.5.0-beta.4 — 2026-09-19

- **`build-screen.py` now applies the whole spec, and fails instead of pretending.** It swapped the
  shell's wording for the spec's by matching the shell's own copy; the shell had been reworded, so
  the chart title, both series names, the highlights total label, the table title, the table columns
  and the sidebar brand were silently ignored and every generated page kept the demo's words. The
  anchors now live in one `SHELL` table, stale translation keys are dropped, and a post-build check
  exits non-zero naming any spec field that did not reach the page.
  **Behaviour change:** a build that previously "succeeded" while dropping fields now exits 2. If
  that happens, the shell's wording moved: update `SHELL` at the top of the script.
- `tests/smoke.py` builds from a spec that shares no wording with the shell, so this class of
  breakage cannot return unnoticed.
- `evals/`: a measurement harness. `run.py` runs one brief under one condition with every other
  skill switched off, records context and billed tokens, wall minutes, real tool calls and which
  skills fired, and flags any run whose calls reached outside its workspace. `matrix.py` runs briefs
  across conditions and resumes where it stopped. `grade_all.py` grades every run with the shipped
  deterministic checks. `blind.py` asks a judge which of two pages is better without telling it who
  made either, in both orders. Read `evals/README.md` first: these spawn real agent sessions on your
  own account.
- The 12 briefs no longer name the skill's own scripts. A brief that says "must pass
  `scripts/verify_page.py`" sends a no-skill baseline hunting for that file, which is how the first
  measured baseline ended up reading the skill it was supposed to be measured without.

## 0.5.0-beta.3 — 2026-09-17

- Demo sidebar fixed: the collapse toggle now works (collapse rules moved out of `@layer components`, where the unlayered `:root` width silently won), the hover-peek no longer re-opens the sidebar while the pointer is still on the toggle, nav and child clicks move the active state and `aria-current`, collapsed items get tooltips, group open state persists, the user card opens a menu, the mobile drawer closes on tap and Esc.
- Demo controls panel moved to the bottom-end corner and closed by default; it used to cover the sidebar's bottom items.
- Toolbar wraps on phone widths.
- `references/layouts.md`: the collapse recipe is now unlayered with the `no-peek` guard, so generated screens do not inherit the bug.
- Every header and table control now does something: notifications popover with mark-all-read, Export and View report feedback, sortable Customer column (`aria-sort`), palette actions close the palette.
- Showcase captures refreshed.

## 0.5.0-beta.2 — 2026-09-17

- `scripts/personality_init.py` writes `design/personality.md` from a preset and the dials changed.
- `SKILL.md` router trimmed (the one-screen summary now points to the quick card); quick-card size stated correctly (~2K tokens) everywhere.
- Strict-YAML frontmatter (quoted description) so the `skills` CLI installs it; CI parses the frontmatter with PyYAML.
- README: what each script touches.

## 0.5.0-beta.1 — 2026-09-17 (public beta)

- Installers without Node (`install.sh`, `install.ps1`), `CONTRIBUTING.md`,
  issue and PR templates, CI (frontmatter/size limits, lint, pre-flight,
  dist drift, smoke test with a headless browser), `tests/smoke.py`.

## 0.5.0 — 2026-09-17 (publish-ready structure)

- Lean install: the skill lives in `skills/jbelly-ui/` (312 KB); evaluation,
  docs and dist stay at the repo root. `license: MIT` in the frontmatter.
- Vendor provenance removed from tracked files and from history (fresh root
  commit); the commercial yardstick stays git-ignored as `reference-template`.
- Delivery tiers generated by `scripts/build_dist.py`: `dist/AGENTS.md` for
  rules-file tools and `dist/jbelly-ui-prompt.md` for chat-only tools.
- `references/interface-guidelines.md`: exact-value rules (forms, focus,
  motion, type, colour, layout, copy, accessibility, performance) restated
  from the most-used interface guidelines and skills; `references/anti-patterns.md`
  (tell, why, instead); `references/sources.md`; `references/stacks.md`
  (plain CSS / Tailwind / React) and DTCG `assets/tokens.json`.
- Manual fallback in `SKILL.md` for environments without scripts.
- `evals/`: 12 briefs and 24 trigger prompts.

## 0.4.0 — 2026-09-17

- Cross-platform tooling: `lint_tokens.py`, `new_screen.py`, `verify_page.py`
  (Playwright, or Chrome/Chromium/Edge headless); PowerShell twins kept.
- Modes: Build / Review / Redesign; the "design read" contract (4 fields).
- `scripts/preflight.py`: AI-default tells, structure checks, token contrast
  (WCAG) — runs inside `verify_page.py`.
- `scripts/audit_styles.py`: redesign inventory and deviation list.
- `references/review-rubric.md`: ten scored dimensions, `file:line` findings.
- Decision tables in the quick card (animate?, card?, which primary?).
- Description trimmed to ~40 words with an explicit scope-out.
- `docs/compatibility.md`: agents, models, machines, install per agent.

## 0.3.0 — 2026-09-17

- Neutral sample data in the demo shell and the example spec (a generic
  commerce/ops product) so the skill reads as general-purpose.
- README rewritten for publishing: what it is, install, demo, measured cost,
  the sources the rules were distilled from, licence.

## 0.2.0 — 2026-09-09 (v2, cost-first)

- `references/quick-card.md`: one-page entry (~2K tokens) instead of the
  full references for standard screens.
- `scripts/build-screen.py` + `assets/spec.example.json`: whole screen from a
  ~2 KB JSON spec, zero model tokens for markup.
- `scripts/verify-page.ps1`: one call renders variants in headless Edge,
  reports console errors, runs the token lint, prints PASS/FAIL.
- `scripts/new-screen.ps1`: scaffold copy with personality/density/RTL/dark preset.
- Inter as the default face (display + text), tuned to the scale of the
  best-selling admin templates; personalities change colour/shape/density.
- ApexCharts house theme from tokens (`references/charts.md`): gradient
  areas, sparklines, donut with centre total, heatmap; dark/RTL re-render.
- Richer sidebar: active rail, groups, badges, "Soon" item, user card,
  optional dark sidebar on a light page.
- `data-i18n` translation pattern; AR/EN toggle flips direction and strings.
- `aria-current`, `aria-sort`, `aria-live`; region markers in the shell.
- Hard cost rules in `SKILL.md`: read once, write once, ≤ 12 tool calls.
- `COST.md`: measured cost per screen, before/after.
- Evaluation workspace:
  deterministic grader and metrics.

## 0.1.0 — 2026-09-09 (v1)

- Tokens, components, layouts, patterns, UX behaviours, integrations,
  industry playbooks, personalities, demo shell, token lint.
