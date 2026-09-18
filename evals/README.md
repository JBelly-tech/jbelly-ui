# Evals

What a screen costs and whether it is any good, measured the same way every time.

## The briefs

`briefs/` holds 12 fixed briefs (dashboard, landing, pricing, sign-up, data table, settings,
product page, mobile, dark-first, RTL Arabic, dense admin, empty states). `trigger-prompts.json`
holds 12 prompts that should trigger the skill and 12 that should not, for tuning `description`
(target: 90% correct both ways).

## Running one brief

```bash
python evals/run.py --brief evals/briefs/01-dashboard.md --skill jbelly-ui --model claude-sonnet-5
python evals/run.py --brief evals/briefs/01-dashboard.md --skill none                 # baseline
python evals/run.py --brief evals/briefs/01-dashboard.md --skill some-other-skill     # any installed skill
```

Each run gets its own directory under `evals/runs/` (git-ignored) holding `timing.json`,
`stream.jsonl`, `prompt.txt`, `settings.json` and a `workspace/` with whatever the agent produced.

**One condition means one skill.** Every other skill on the machine is switched off for the run
through `skillOverrides`, and the baseline adds `--disable-slash-commands`, so "no skill" really is
no skill. The init event in `stream.jsonl` records which skills were visible, so the isolation is
checkable after the fact rather than assumed.

**Least privilege, not bypassed permissions.** The run gets file tools plus `python`/`node` for the
skills' own scripts. No network tools, no subagents, no arbitrary shell. The tool list is recorded
in `timing.json`.

`timing.json` records tokens (input, output, cache read, cache creation), wall minutes, tool calls
counted from the actual `tool_use` blocks, which skills fired, cost, and whether the page exists.

## Grading every run

```bash
python evals/grade_all.py --json evals/results.json --markdown evals/results.md
```

Deterministic only: token lint, pre-flight, page size. No model opinion enters the table. For the
side-by-side visual report use `comparison/tools/`.

## What is not here yet

- Across models: a wrapper over several model families (one OpenRouter key read from
  `OPENROUTER_API_KEY`, never committed). See `docs/roadmap.md` item 1.
- Blind preference: two pages of the same brief judged without maker names.
