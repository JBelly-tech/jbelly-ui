# Compatibility — which agents, models and machines

## Format

`jbelly-ui` is an **Agent Skill**: a folder with `SKILL.md` (YAML frontmatter
`name` + `description`, then Markdown instructions), `references/`, `scripts/`
and `assets/`. The format is an open convention read by many coding agents,
not tied to one vendor. Nothing in the skill calls a model API; it is text
the agent reads plus scripts the agent runs.

## Agents

Install with the `skills` CLI (`npx skills add JBelly-tech/<repo>`), which places
the folder where each agent looks for skills:

| Agent | Project path | Global path | Command |
|-------|--------------|-------------|---------|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | `npx skills add JBelly-tech/jbelly-ui -a claude-code` |
| Cursor | `.agents/skills/` | `~/.cursor/skills/` | `npx skills add JBelly-tech/jbelly-ui -a cursor` |
| GitHub Copilot | `.agents/skills/` | `~/.copilot/skills/` | `npx skills add JBelly-tech/jbelly-ui -a copilot` |
| Codex | `.agents/skills/` | `~/.codex/skills/` | `npx skills add JBelly-tech/jbelly-ui -a codex` |
| Gemini CLI, Windsurf, OpenCode, Cline and ~70 more | see `npx skills add --help` | | `-a <agent>` |

Add `-g` for a user-wide install and `-y` to skip prompts. Without the CLI,
copy `skills/jbelly-ui/` to any of the paths above.

## Models

Any model the agent runs can use the skill; the instructions are plain
language and the tooling is deterministic. What changes with the model is
adherence: stronger models follow the personality step and the cost rules
more reliably. Recommended split (from `SKILL.md`): a top-class model for
the personality decision and the final review, a mid-class model for
building screens. Measured runs so far used one model family; the scripts have
no model dependency.

## Machines

| Piece | Windows | macOS / Linux |
|-------|---------|---------------|
| Token lint | `scripts/lint_tokens.py` or `scripts/lint-tokens.ps1` | `scripts/lint_tokens.py` |
| Scaffold | `scripts/new_screen.py` or `scripts/new-screen.ps1` | `scripts/new_screen.py` |
| Spec → page | `scripts/build-screen.py` | `scripts/build-screen.py` |
| Verify (render + console + lint + both runtime probes) | `scripts/verify_page.py` (Playwright, or Chrome/Edge headless) or `scripts/verify-page.ps1` (Edge) | `scripts/verify_page.py` (Playwright, or Chrome/Chromium headless) |
| Colour sweep across every personality | `scripts/verify_theme.py` | `scripts/verify_theme.py` |
| Install without Node | `.\install.ps1 -Agent <agent>` | `./install.sh <agent>` |

Requirements: Python 3.9+ (standard library only). For verification, either
`pip install playwright && playwright install chromium` (best console
capture) or any installed Chrome / Chromium / Edge. Without a renderer the
runtime probes print `[SKIP]` and return 0 — which is not a pass, and they
say so.

The `.ps1` files are Windows conveniences, not requirements: every one of
them has a Python twin that is the same tool. On macOS and Linux the
terminal is the interface, so **every script answers `--help`** with what it
does, how to call it and what its exit codes mean, and does nothing else.

This is checked rather than promised: CI runs the whole script set on
**macOS, Linux and Windows**, on Python 3.9 as well as 3.12 — `--help` on
every script (and fails if one of them writes a file while doing it), the
token lint and pre-flight on every shipped page, a page built from a spec,
the generated files byte-compared, and both installers.

## Stacks

The tokens are CSS custom properties and the recipes are Tailwind v4 utility
strings that map one-to-one to CSS. Used as-is with Tailwind v4 (any
framework), and as a reference for Tailwind v3 (`theme.extend.colors` mapping
in `tokens.css` comments), plain CSS, or component libraries that accept
class names. Charts assume ApexCharts (MIT); any library can be themed from
the same variables (`references/charts.md`).

## What an install depends on

**Nothing we host.** The folder you copy — `skills/jbelly-ui/` — names no address
belonging to this project: no site, no repository, no API. It is text and Python
that reads local files. If this project moves account again, or the site goes
away entirely, an installed copy keeps working exactly as it did. A test holds
that: `tests/smoke.py` fails if any file in the shipped folder so much as
mentions a host we control.

The four demo pages are the one exception worth naming, and they are demos
rather than the skill: each is a single file that pulls Tailwind, ApexCharts,
Lucide and Google Fonts from public CDNs at runtime, so it needs a network the
first time you open it. Pages the generator builds inherit those four `<script>`
and `<link>` tags. Nothing else reaches the network, at build time or after.

## Licence

MIT. Every dependency the skill recommends is MIT / BSD / Apache / OFL. No
commercial template code or assets are included or required.
