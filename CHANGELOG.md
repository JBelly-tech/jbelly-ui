# Changelog

## Unreleased

**The project moved to the `JBelly-tech` organisation.** `github.com/JBelly-tech/jbelly-ui` is the
repository now, and `https://jbelly-tech.github.io/jbelly-ui/` is the site. GitHub redirects the old
repository URL and the old `git remote`, so clones and `npx skills add mohammadJohar/jbelly-ui` keep
working — but it does **not** redirect a Pages site, so the old
`mohammadjohar.github.io/jbelly-ui/` address stops resolving. Every link in the README, the
compatibility table, CONTRIBUTING, both installers and the site itself points at the new home, and
the install command names it: `npx skills add JBelly-tech/jbelly-ui`.

**You could not see where a form field was, or which control had focus.** WCAG 1.4.11 asks 3:1 of
the boundary of a user interface component and 2.4.11 asks it of the focus indicator, for the same
reason: they are the only thing telling a reader where the control is. `--input`, a field's edge,
measured **1.27:1** against the page it sits on. `--ring`, the focus outline, measured 2.33:1 in
light and **1.91:1** in dark. The storefront had already fixed both locally — the second time in
this release that the newest shell was right and the rest of the system had not caught up — and even
its values were a shade under once measured against every surface a field can sit on rather than
only the page. Every `--input` and `--ring` in every personality now clears 3:1; the weakest is
3.04:1, and the focus ring takes the storefront's stronger value rather than the minimum that passes.

`--border` is deliberately left where it is. It separates cards and rows — structure that layout
already states — and the system is nearly flat on purpose. A rule that could not tell a hairline
from a control boundary would push every one of them to 3:1 and call it an improvement.

`preflight.py` checks both roles against every surface the scope declares, so this cannot come back,
and a fixture carrying the old shipped values proves the rule can fail.

**And the chart drew two of its series with the state fills.** `--success` and `--warning` are made
to carry white text, which makes them far too light to be seen as a line: on a white card the
success series measured **2.08:1** and the warning series **1.44:1** — a pale yellow line on white
paper. A series is a graphical object a reader needs in order to read the chart, so `--chart-3` and
`--chart-4` now hold values that clear 3:1 there, keeping each hue and chroma and moving only in
lightness so the ladder that tells the series apart survives: 48, 56, 60.5, 63, 52.5 instead of 48,
56, 72, 85, 52.5. Dark mode keeps the bright fills, which are already 8:1 and 11:1 on its card.

That exposed a second thing: the donut's legend dots were painted `bg-success` and `bg-warning`
while the donut itself drew `--chart-3` and `--chart-4`. They held the same values until now, so
nothing showed. A legend whose colours do not match the thing it labels is not a contrast problem,
it is a wrong legend; the dots read the series roles.

**In Windows High Contrast there was no focus indicator at all.** A Tailwind `ring` is a
`box-shadow`, and `forced-colors: active` drops `box-shadow`. Probed in a real engine with forced
colours on, every button in every shell reported `box-shadow: none` and `outline: none` — nothing,
for the readers most likely to be navigating by keyboard and most likely to have turned High
Contrast on. WCAG 2.4.7 asks for an indicator. Every shipped page now carries
`@media (forced-colors: active) { …:focus-visible { outline: 3px solid CanvasText; outline-offset: 2px } }`,
kept deliberately **outside** `@layer components` — an unlayered author rule beats a layered one
whatever the specificity, which is what lets it win against the component's own `outline-none`, and
the block says so where someone might otherwise tidy it into the layer. `forced-color-adjust: none`
goes only where the colour *is* the information — and each of those selectors was checked against a
rendered page rather than written from memory: the storefront's tone swatches (15) and colour filter
(12), its product art (9), the dashboard's chart canvases (6) and its legend dots (5). Two selectors
that matched nothing anywhere were dropped. Re-probed after the change: eight controls on each of the
five pages, none without an indicator.


**The skill is checked on macOS, Linux and Windows now, not assumed to work there.** On Windows the
`.ps1` twins and the agent hide the command line; on macOS and Linux the terminal *is* the
interface, and `--help` is the first thing anyone types. `SKILL.md` said "all `--help`". Six of
thirteen scripts did something else with it: two answered "unknown option", `preflight.py` tried to
review a file called `--help`, `verify_page.py` launched a browser and rendered one, `export_tokens.py`
ignored the flag, and `new_screen.py` -- which takes its output path from the first argument --
**wrote a 110 KB scaffold to a file named `--help`**, in the repository root, where it was committed
by accident in the previous change. A later `export_tokens.py --help` then read that file as its
stylesheet, which is how `assets/tokens.json` came to ship three `chart-*` roles that `tokens.css`
has never declared. A help screen with a side effect is not a small thing.

Every script now prints what it does, how to call it and what its exit codes mean, and does nothing
else. `export_tokens.py` writes an explicit LF -- without it the same command produces LF
on Linux and CRLF on Windows, and the "generated files match their sources" check could not pass on
a Windows machine. `install.sh` is executable in the index (a fresh clone answered `./install.sh`
with "permission denied") and its project-mode branch is an `if` rather than an `&&` that depends on
how a shell reads `set -e`.

A new CI job runs the whole script set on **macOS, Linux and Windows**, on **Python 3.9** as well as
3.12 -- the floor the compatibility table promises: `--help` on every script, failing if one of them
so much as touches the working tree; the token lint and pre-flight on every shipped page; a page
built from a spec and put through the same checks; the generated files byte-compared; and both
installers.

**Three of the five state colours had no value for text.** The system states the rule itself --
"a fill light enough to carry white text is too light to be read as text" -- and it is why
`--primary-accent` and `--destructive-accent` exist. It had been applied to two roles out of five.
So the recipes reached for the fill: `badge-light-success` was `bg-success/15 text-success`, which
is a 72%-light green painted on a 15% tint of itself, **1.97:1**. Warning was worse. `--success-accent`,
`--warning-accent` and `--info-accent` now exist, `--destructive-accent` is corrected (it measured
3.78:1 light, 3.23:1 dark), and every value clears 4.9:1 on **every** surface any personality
declares in that mode -- 16 light and 21 dark across the four shells, plus the tinted badge ground
over each.

**`text-primary` was the same mistake, and it is the one people saw.** It is the fill used as text.
In the default palette `--primary` and `--primary-accent` hold the same value, so it looks correct;
the moment a personality is chosen -- which this skill requires -- it stops being correct. In
graphite it was a 65% green on white, 2.72:1, which is why active nav items and avatar initials went
pale as soon as anyone switched personality. 32 uses across the four shells and 37 recipes across
the references now name the text role. `--sidebar-primary` followed the fill too, and now follows
the text value; the sidebar avatar uses the sidebar's own brand role instead of the page's, so it
survives a dark sidebar on a light page.

**A personality was leaking its light values into dark mode.** `.theme-x` and `.dark` are each a
single class and a personality is written after dark mode, so source order hands the personality
every role it declares -- in *both* modes. Five of six were doing it: graphite kept `--primary` and
a 53%-grey `--muted-foreground` on a 13% ground, editorial and mint kept warm paper shadows on a
black page. `preflight.py` has a new rule that names the role and the scope rather than waiting for
a contrast pair to happen to cover it, and it found a broken declaration in this very change on its
first run.

**A new runtime probe, because the source cannot answer this.** `preflight.py` reads the declared
tokens and checks the role pairs. A class like `bg-success/15 text-success` names no pair -- it
names a fill and then paints that fill as text on a tint of itself, and whether that reads depends
on a composite the stylesheet never states and on which personality is active. `verify_theme.py`
drives the real engine: it sets each personality on `<html>`, walks every element that paints,
composites the background the way the compositor does, and compares. C01 text, C02 icons, C03
nothing painting itself invisible, C04 every personality actually reached. It is folded into
`verify_page.py`, so it costs no extra call.

Writing it taught three things about measuring a live page, all of which had produced a confident
wrong answer first: a URL fragment is a same-document navigation, so a page that reads it once on
load never sees the second one and every personality measures as whatever loaded first; a demo that
remembers dark mode hands back the previous state and reads as a clean sweep; and colours sampled
during the tint crossfade come back as an interpolated `oklab()` of the state being *left*.
Transitions are switched off for the sweep rather than waited out.

**Measured, on every page this repo ships**, before and after, with the same probe: 12,026 painted
elements across 14 personality states each -- seven personalities, light and dark -- against the
ground each element is actually painted on.

| page | before | after |
|------|-------:|------:|
| `app-shell.html` | 109 | **0** |
| `commerce-shell.html` | 63 | **0** |
| `landing-shell.html` | 45 | **0** |
| `pricing-shell.html` | 24 | **0** |
| `index.html` | 0 | **0** |

The site was already clean: it is plain CSS with no utility classes to get wrong, and its six
personality dark blocks landed in the previous change. The defect was in what the skill *ships*.

**Two storefront defects that were visible rather than measured.** The quick-view button was
absolutely positioned across the bottom of every product photograph at `lg` and up -- permanently,
because the hover gate that would normally hide it had been removed when V08 caught it (a control
resting at opacity 0 is invisible to anyone who never hovers, and to print). It sits in the card
footer beside "Add to bag" now. And the demo-controls panel had been faded to 70% to stop it
covering the grid, which made every label on it 2.75:1 at rest -- a second defect standing in for a
fix. It is opaque again, and narrow until opened, which is what the overlap needed in the first place.

**The default palette stops shouting.** `--primary` was chroma 0.2 on a white page and 0.21 on
near-black, which made it the loudest object on every screen the system produces — a template's
accent, not a considered one. It is now deeper and much less saturated, and the dark-mode link
colour gets lighter rather than more saturated, because a dark ground amplifies chroma and not
lightness. Every pair ends up with more contrast than it had: the dark link role went from 4.53:1
to 6.88:1. `--info`, a chroma-0.22 violet on a system that bans purple-to-blue gradients by name,
came down with it. Hues, roles and foregrounds are unchanged, so nothing needs re-mapping.

**Six personalities were broken in dark mode on the site, and the checker said PASS.** A
personality is two blocks -- `.theme-x` for the light surfaces, `.theme-x.dark` for the dark ones --
and the site had copied only the first. Both are a single class, so the one written later wins, and
the preset is written after `.dark`: the preset's *light* card ended up under dark mode's white
text. The buttons vanished, and hovering brought them back, because hover paints `--accent`, which
was still the dark one.

The pre-flight missed it for a reason worth naming: it only built states somebody had written a
block for. `.dark` and `.theme-clinic` were declared separately and their combination never was, so
no environment for it was ever built and nothing was ever compared -- even though it is one class
toggle away and exactly what a theme rail next to a dark toggle produces. It now synthesises that
state and labels it, and pointed at the site it reports 1.00:1 where it used to report nothing.
`references/personalities.md` documented one preset's dark half and five presets' light halves
only, so anyone copying a preset out of it reproduced the same defect; all six are now paired.

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
