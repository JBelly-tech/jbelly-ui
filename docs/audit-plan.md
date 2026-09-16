# jbelly-ui — gap audit against the power-up plan (handoff for an agent session)

Goal: check **what already exists** in this skill against every item in
[`power-up-plan.md`](power-up-plan.md), with proof, before any improvement work starts.

## Rules

- **Read-only.** Do not fix, rename, move or commit anything except the report file.
- **Evidence or it did not happen.** Every status needs a `path:line`, a file
  list, or the output of a command. "Looks fine" is not evidence.
- **Deterministic first.** Use `git grep`, `git ls-files`, file sizes and line
  counts before reading any file. Open a file only when a command cannot answer.
- **Shipped folder** = the folder `npx skills add` would install. Today that is the
  repo root; if `skills/jbelly-ui/` exists, it is that folder.
- **Vendor name:** do not type it into the report. Take it from the ignored folder in
  `.gitignore` (`comparison/<vendor>-reference/`) and write `<vendor>` in the report.
- Shell is PowerShell on Windows.

## Status values

| Status | Meaning |
|---|---|
| `done` | Fully meets the plan item; evidence proves it |
| `partial` | Some of it exists; say exactly what is missing |
| `missing` | Nothing exists |
| `conflict` | The skill does the opposite of the plan — flag for the owner |

## Checks (one row per plan item)

| # | Plan item | How to check |
|---|---|---|
| 1 | Provenance leak | `git grep -i -I <vendor>`; `git ls-files` filtered for `<vendor>`; `git log --all --name-only --format=` filtered for `<vendor>`. Any hit = not done. Also scan shipped files for other brand names used in sample data. |
| 2 | Lean install | Does `skills/jbelly-ui/SKILL.md` exist? Total size of the shipped folder (exclude `.git`). Over 1 MB = not done. List the 5 largest shipped files. |
| 3 | Spec compliance | Frontmatter: `name` equals folder name and is lowercase-hyphen; `description` char count (≤ 1024); `license` field present; SKILL.md line count (< 500) and char count ÷ 4 as token estimate (< 5000); any reference file that links to another reference file (depth > 1). Run `skills-ref validate` only if it installs without extra setup; otherwise say so. |
| 4 | No agent-specific wording | In shipped files: `git grep -n -i -E "claude|anthropic|\.claude|Read tool|Bash tool|Agent tool|subagent|TodoWrite|Skill tool"`. Classify each hit: acceptable (README install example among several agents) or must change. |
| 5 | Cross-platform scripts | List `scripts/` by extension. Each `.ps1` = gap. For each script: does it support `--help` (grep for help handling)? Are `_*.py` one-off scripts shipped? Any hard-coded Windows paths (`[A-Z]:\\`)? |
| 6 | Stack-neutral output | `references/tokens.css` exists? Any DTCG tokens JSON (`*.tokens.json` or `$value` keys)? Is there one table mapping recipes to plain CSS / Tailwind / React? (`git grep -n -i -E "tailwind|react"` in references). |
| 7 | Cross-agent smoke test | Any recorded run in a non-Claude agent (grep `comparison/` and `evals/` for `codex|cursor|gemini|copilot|kimi`). No record = missing. |
| 7a | Tier 1 native skill tools | README lists install paths for more than one agent? |
| 7b | Tier 2 rules file | `dist/AGENTS.md` or any AGENTS.md-style file exists? |
| 7c | Tier 3 paste-in file | A single self-contained prompt file exists? Its size ÷ 4 as token estimate. |
| 7d | Works without tools | For each script mentioned in SKILL.md, is there a manual fallback next to it? List those without. |
| 7e | Build script for tiers | Any script that generates 7b/7c from sources? |
| 8 | Human preference data | Any reference citing designarena.ai or lmarena, or notes on winning vs losing traits. |
| 9 | Real-product patterns | Links to mobbin / pageflows / awwwards / godly / land-book / refero in references or docs. |
| 10 | Research-backed rules | Count rules in `references/ux-behaviours.md` and `patterns.md`; count those with a source (nngroup, baymard, lawsofux, w3.org/WCAG, apca). Report `sourced / total`. Check contrast rules name WCAG 2.2 or APCA. |
| 11 | Mature design systems | References to Material 3, Apple HIG, Fluent 2, GOV.UK, Carbon, Radix Colors. |
| 12 | Competitor comparison | `comparison/` iterations: which competitor skills were compared, and is there a written list of gaps + token cost per competitor? (`COST.md`, `notes.md`). |
| 13 | Anti-slop list | `references/anti-patterns.md` exists? Otherwise grep `slop|default-AI|generic|gradient|emoji` in SKILL.md and `personalities.md`; does each item give why + what instead? |
| 14 | Brief set | `evals/briefs/` exists? Count briefs; which of the 12 types in the plan are covered; is there an RTL / Arabic brief (`git grep -n -i -E "rtl|dir=|arabic"`)? |
| 15 | Deterministic checks | What `scripts/verify-page.*` and `lint-tokens.*` actually check. Mark each: axe-core, contrast, hard-coded colours/sizes, screenshots at 375/768/1440, horizontal overflow, Lighthouse, single command writing JSON. |
| 16 | Blind human rating | Open one `grading.json`: graded by a model or humans? Blind (no labels)? Number of raters and votes. |
| 17 | Across models | Which models appear in `timing.json` / metrics / `COST.md`? Is a small model and a non-Anthropic model included? Are tokens per page logged? |
| 18 | One change at a time | Is there a before/after table (win rate + tokens) per iteration? `CHANGELOG.md` entries linked to measured results? |
| 19 | Trigger precision | Any should-trigger / should-not-trigger prompt set (grep `evals/` for `should_trigger|trigger`)? Current description length. |
| 20 | Router SKILL.md | Does SKILL.md contain only the mandatory steps + pointers, or long recipe content that belongs in references? List sections over ~40 lines. |
| 21 | README | Check for: one-line pitch, before/after images, `npx skills add` command, supported-agents list, win-rate table. Mark each. |
| 22 | Published | `git remote -v` (empty = not published). |
| 23 | Releases + feedback | `git tag`; `CHANGELOG.md` uses semver; `.github/ISSUE_TEMPLATE/` exists. |

## Also report

- **Built but not in the plan.** Things the skill has that the plan does not
  mention (for example the personality step, industry playbooks, the spec-driven
  page builder). One line each: path + what it does + keep / move to references.
  These must not be lost during Phase 0–5 work.
- **Conflicts.** Any place the skill's current rules contradict the plan.

## Output

Write **one file**: `docs/audit-report.md`, front-matter
`title / status: draft / updated: <date>`, then:

1. Summary line: counts of `done / partial / missing / conflict`.
2. Table: `# | item | status | evidence | what is missing | fix size (S/M/L)`.
3. "Built but not in the plan" list.
4. "Conflicts" list.
5. Suggested order of work: the first 5 fixes, blockers first (Phase 0 items always first).

Stop after writing the report. Do not start fixing.
