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

These runs use the agent CLI you are already signed into, so they cost no money beyond the
subscription you have. They do consume its usage allowance, and a full matrix can exhaust a
rate-limit window, which is why `matrix.py` resumes where it stopped.

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

- Across models: a wrapper that runs the same briefs on whichever models the agent you already use
  offers. Everything here runs through that agent's own CLI, on the subscription you already have;
  no API key, no paid service, and none will be added.
- Blind preference: two pages of the same brief judged without maker names.
