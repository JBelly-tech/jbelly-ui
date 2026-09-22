# jbelly-ui — UI design skill for AI agents

> **Public beta.** The system, recipes and scripts are complete and measured on a handful of briefs with one model family. What the beta tests is the claim that it works well in *every* agent and model. Try it on your own screens and report with the [issue templates](.github/ISSUE_TEMPLATE/); bad results are the most useful. Fork freely (MIT). Versions: [`CHANGELOG.md`](CHANGELOG.md).

[![ci](https://github.com/mohammadJohar/jbelly-ui/actions/workflows/ci.yml/badge.svg)](https://github.com/mohammadJohar/jbelly-ui/actions/workflows/ci.yml) · MIT · Agent Skills format · Python 3.9+ tooling, no dependencies

**Live demos:** [app shell](https://mohammadjohar.github.io/jbelly-ui/skills/jbelly-ui/assets/app-shell.html) · [landing page](https://mohammadjohar.github.io/jbelly-ui/skills/jbelly-ui/assets/landing-shell.html) · [pricing page](https://mohammadjohar.github.io/jbelly-ui/skills/jbelly-ui/assets/pricing-shell.html)
[Cost, measured](COST.md) · [Recorded runs](evals/records/) · [Roadmap](docs/roadmap.md)

**A licence-free UI system for web products, packaged as an agent skill.**
Dashboards, admin panels, settings and auth pages, data tables, landing
pages. Exact tokens and recipes, a spec-driven page builder, admin-grade
behaviours, licence-safe libraries, and a mandatory *personality* step so
every product looks deliberately different instead of default-AI generic.

Works with anything that renders HTML: plain HTML + Tailwind v4, React /
Next, Vue / Nuxt, Blazor, Laravel. Tokens are CSS variables; recipes are
utility class strings.

![Default shell](docs/showcase/default-light.png)

## What it is good at

Four claims, each with the thing in this repository that proves it.

**1. A screen costs little to build.** The dashboard brief measures at 831,640 context tokens,
97,004 billed tokens, 2.07 minutes and 10 tool calls, and the page it produces passes every
deterministic check. That is one run, not an average, and the file it wrote is in the repository:
[`01-dashboard-jbelly-ui-20260919-162651.json`](evals/records/01-dashboard-jbelly-ui-20260919-162651.json). Reproduce it with `python evals/run.py
--brief evals/briefs/01-dashboard.md --skill jbelly-ui`. A pricing page, where the generator has no
shape yet, costs six times as much — that run is published too, and the method, the isolation and
the limits are in [`COST.md`](COST.md).

**2. Quality is decided by scripts, not by opinion.** One call renders the page headlessly in
light, dark and RTL, collects console errors, fails on horizontal overflow, runs the token lint and
runs a pre-flight that checks page structure, the tells that make a page read as AI-generated, and
the WCAG contrast of every colour role the markup paints text with. A second call drives every
control in the page and fails on any that does nothing. Every one of those checks exits non-zero
when it fails, and CI runs them on every push — including against this project's own website.

**3. Two products cannot ship the same page by accident.** The personality step is mandatory and
persisted: eight dials, six presets, written to `design/personality.md` before any code, and every
later screen is checked against that file. Colour lives in semantic tokens, so a re-brand is one
token, not a sweep.

**4. Nothing here is licensed per project, and nothing is copied.** MIT, one copyright holder, no
dependencies beyond a stock Python 3.9+, under 500 KB installed. Every rule is restated in the
project's own words with its source recorded in `references/sources.md`.

## Where it is weak

Said plainly, because you will find out anyway.

**The published cost figures are older than the tool they describe.** They were measured when the
page builder knew one shape, the app screen, so the landing and pricing runs are the cost of a model
writing that markup by hand. Both shapes now have templates, which should move those two numbers a
long way — but *should* is not *measured*, and nothing here will claim the improvement until the
briefs have been run again. The dashboard figure is unaffected.

**One run each, one model, one agent.** No repeats, so no variance. Treat the ordering as real and
the precision as not, and treat every other agent and model as untested.

**Only three page shapes are generated**: the app screen, the landing page and the pricing page. The
storefront ships as a demo shell to copy from, not yet as a generator kind. Anything else is the
model writing markup with the system's rules in front of it, which is better than nothing and costs
what it costs.

**It is web only.**

## Install (three ways, one source)

**1. Agents that read skills** (Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, Windsurf, Kiro, Roo Code, OpenCode, Amp, Goose and ~70 more):

```bash
npx skills add mohammadJohar/jbelly-ui -a claude-code     # or -a cursor, -a codex, -a copilot, -a gemini-cli …
npx skills add mohammadJohar/jbelly-ui -g -y              # user-wide, no prompts
```
No Node? `./install.sh cursor` (macOS/Linux) or `.\install.ps1 -Agent cursor` (Windows) copies the skill into the agent's folder; `docs/compatibility.md` lists every path.

**2. Tools that read a rules file** (Lovable and other AGENTS.md readers): copy `dist/AGENTS.md` to your project root (or into the tool's knowledge box).

**3. Chat-only tools** (ChatGPT, Gemini, Kimi, DeepSeek, a custom GPT or project): paste `dist/jbelly-ui-prompt.md` (about 5K tokens, self-contained, includes the tokens and a manual checklist).

Both `dist/` files are generated from the skill by `scripts/build_dist.py`, so they never drift from the source.

Then ask for any UI ("add a dashboard", "build the settings page", "restyle this table", "review this screen"). The skill triggers on UI work only.

## Try it in 30 seconds

Open the [live demo](https://mohammadjohar.github.io/jbelly-ui/skills/jbelly-ui/assets/app-shell.html) (or `skills/jbelly-ui/assets/app-shell.html` locally). The *Demo controls* panel in the corner switches personality, density, dark mode, sidebar style and AR/EN (RTL); everything in the page works: collapse, ⌘K palette, table states, drawer, sort, notifications. Or build a page from a spec:

```bash
python skills/jbelly-ui/scripts/build-screen.py skills/jbelly-ui/assets/spec.example.json out/dashboard.html
python skills/jbelly-ui/scripts/verify_page.py out/dashboard.html --variants ",#dark=1,#dir=rtl"   # render + console + lint + pre-flight
```

| Dark sidebar on a light page | Personality "neo", empty state | RTL |
|---|---|---|
| ![](docs/showcase/demo-sidebar-dark.png) | ![](docs/showcase/demo-neo-empty.png) | ![](docs/showcase/demo-slate-rtl.png) |

Two more shells ship with the skill, both self-contained and both built from the same tokens: a
[landing page](https://mohammadjohar.github.io/jbelly-ui/skills/jbelly-ui/assets/landing-shell.html) and a [pricing page](https://mohammadjohar.github.io/jbelly-ui/skills/jbelly-ui/assets/pricing-shell.html). Every
control in them works, and each carries the same six personality presets, dark mode and RTL.

| Landing shell | Pricing shell |
|---|---|
| ![](docs/showcase/landing-light.png) | ![](docs/showcase/pricing-light.png) |

Every capture on this page is taken from the shells themselves by
`python scripts/capture_showcase.py`, so a screenshot cannot quietly fall behind the code.

## What is inside

`skills/jbelly-ui/` is the installable skill (what `npx skills add` copies). Everything else is evidence and tooling around it.

**The skill**

| Path | Purpose |
|------|---------|
| `SKILL.md` | The workflow, the system in one screen, the rules, the done list (about 4K tokens) |
| `references/quick-card.md` | One page: tokens, sizes, the presets, the most-used recipes, cost rules. About 2.6K tokens, and the only reference a standard screen needs |
| `references/personalities.md` | 8 dials, 6 presets, density block, how to derive a new one, the persisted file format |
| `references/tokens.css` | Drop-in tokens: light/dark roles, states, sidebar roles, radius scale, Tailwind v4 mapping, base resets |
| `references/components.md` · `layouts.md` · `patterns.md` | Exact class strings for 25 controls; shells, nav, toolbar, settings, auth, landing, RTL; KPI, chart, table, feed, drawer, pricing, checkout, palette, empty states |
| `references/charts.md` · `ux-behaviours.md` · `integrations.md` | ApexCharts theme from tokens + 8 recipes; loading/empty/error, tables, forms, overlays, keyboard, responsive; licence-safe libraries per need |
| `references/industry-playbooks.md` · `interface-guidelines.md` · `anti-patterns.md` · `review-rubric.md` · `stacks.md` · `sources.md` | Page inventories for 10 business types; exact-value interface rules; the AI-tells list; ten scored review dimensions; plain-CSS and React mappings; where every rule comes from |
| `assets/app-shell.html` · `landing-shell.html` · `pricing-shell.html` | Three self-contained demos and scaffolds: shell, dark mode, RTL + i18n, density, personality switcher, table states, drawer, ⌘K palette, toasts, ApexCharts |
| `assets/spec.example.json` · `assets/tokens.json` | Example spec for the page builder; DTCG tokens for design tools |

**The scripts** (Python 3.9+, no dependencies; PowerShell twins where noted)

| Script | Does |
|--------|------|
| `personality_init.py` | Writes `design/personality.md` (design read + dials) so every product starts with its own look |
| `build-screen.py` | Whole screen from a ~2 KB JSON spec, zero model tokens for markup |
| `new_screen.py` (`new-screen.ps1`) | Scaffold copy with personality / density / RTL / dark preset |
| `verify_page.py` (`verify-page.ps1`) | One call: render variants headlessly, console errors, token lint, pre-flight, PASS/FAIL |
| `preflight.py` | Deterministic judgement: AI-default tells, structure checks, and the WCAG contrast of every colour role the markup uses as text — not only the pairs the stylesheet happens to declare |
| `check_controls.py` | Drives every button, tab, radio, summary and same-page link in a real browser and fails on any control that changes nothing. A dead button is the commonest defect in a demo and the hardest to see in review |
| `lint_tokens.py` (`lint-tokens.ps1`) | No raw palette colours outside `tokens.css` |
| `audit_styles.py` | Redesign inventory: fonts, colours, radii, shadows, spacing, raw palette classes; deviation list in fix order |
| `export_tokens.py` · `build_dist.py` | Generate `assets/tokens.json` and the two `dist/` tiers from the sources |

**Around the skill**

| Path | Purpose |
|------|---------|
| `COST.md` | Measured token/time cost per screen and the levers that cut it |
| `evals/tools/` | The deterministic graders: assertion grader, source and DOM metrics, screenshot analytics |
| `evals/` | 12 fixed briefs (incl. RTL Arabic, mobile, dark-first, empty states) and 24 trigger / no-trigger prompts |
| `dist/` | Generated delivery tiers: `AGENTS.md` (rules-file tools) and `jbelly-ui-prompt.md` (chat-only tools) |
| `docs/` | `compatibility.md` (agents, models, install paths), `roadmap.md`, showcase captures |
| `tests/smoke.py` · `.github/workflows/ci.yml` | What CI runs on every push: frontmatter limits, lint, pre-flight, dist drift, build + render + verify |

## What was tested, honestly

- Measured runs so far: one model family, in one agent, on the briefs in `evals/briefs/` (see `COST.md`).
- Format-compatible but not yet measured: every other agent the `skills` CLI supports, and the two `dist/` tiers. The [roadmap](docs/roadmap.md) covers models, agents and blind human rating; results will replace this paragraph.

## Help test the beta

1. Install, ask your agent for a real screen, run `verify_page.py` and `preflight.py` on the result.
2. Open an issue with the template: brief, agent, model, verdict lines, screenshot.
3. Want to change something? `CONTRIBUTING.md` explains the layout, the tests (`python tests/smoke.py`) and the one rule that matters: nothing copied, every rule sourced.

## What the scripts touch

Every script is read-only except for the file it says it writes: `build-screen.py` and `new_screen.py` write the page you name, `personality_init.py` writes `design/personality.md`, `verify_page.py` writes screenshots to a folder you name (default: the OS temp folder), `export_tokens.py` and `build_dist.py` write into the skill's own `assets/` and `dist/`. Nothing calls a network API; the only network use is the page itself loading CDN scripts when rendered.

## Principles

1. Colour comes from semantic tokens; raw palette classes live in one file.
2. One primary action per view; cards are the unit of layout.
3. Every async region has loading, empty, error and success states.
4. Personality first: never ship the default look.
5. Only MIT / BSD / Apache / OFL dependencies; no template code, ever.
6. Read once, write once, verify once: the agent's cost is part of the design.

## Where the rules come from

Distilled from public, licence-free sources developers already trust:
shadcn/ui and Radix conventions, Shopify Polaris and GitHub Primer content
and data-table guidance, the Refactoring UI rules, Vercel's Web Interface
Guidelines, Linear-style keyboard and density patterns, Tremor/shadcn
dashboard blocks, and a study of the page inventories and flows that
buyers of admin and SaaS products expect in ten business categories. Nothing is
copied; every rule is restated as an instruction.

## Licence

MIT, see `LICENSE`. Fonts via Google Fonts (OFL), icons Lucide (ISC),
charts ApexCharts (MIT).
