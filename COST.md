# Cost — what a screen costs to build with this skill, measured

Agent cost is **Σ (context size × number of steps)**. A skill can blow that up
two ways: by loading a lot of text into the context, and by making the agent
take many tool calls. This file records what was measured and what the skill
does about it. Numbers come from `comparison/` (same model, same brief, runs
in parallel, headless-Edge captures).

## Measured (2026-09-09)

| Run | Brief | Tokens | Minutes | Tool calls | Result |
|-----|-------|--------|---------|------------|--------|
| no skill | simple dashboard | 72,494 | 5.4 | 1 | rendered; 238 raw palette classes, no loading/empty states, no keyboard |
| catalogue skill (`ui-ux-pro-max`) | simple | 155,644 | 16.0 | 37 | rendered; searches + verify loop |
| **jbelly-ui v1** (full references) | simple | 157,840 | 20.3 | 24 | one `@apply group` compile error (fixed in the skill) |
| catalogue skill | complex console | 246,244 | 24.5 | 54 | complete |
| **jbelly-ui v1** | complex console | 398,111 | 55.3 | 90 | complete, most distinct, 7/8 checks; **90 calls** (self-made smoke test + captures) |

Where the house-skill tokens went: ~28K reading every reference, re-sent on
each of the 24–90 later calls (the quadratic term), ~40K output for a 150 KB
page, and a self-invented verification loop.

## What v2 changes (all in this repo)

| Lever | Mechanism | Expected effect |
|-------|-----------|-----------------|
| Read 2K tokens, not 28K | `references/quick-card.md` replaces the full references for a standard screen | −25K context, × every later call |
| Zero-token boilerplate | `scripts/new-screen.ps1` (copy the shell with personality set) and `scripts/build-screen.py` (whole page from a ~2 KB JSON spec) | −60–90% output tokens |
| One verification call | `scripts/verify-page.ps1`: render variants + console errors + token lint → PASS/FAIL | 90 calls → ≤ 12 |
| Hard budget | SKILL.md: read once in a batch, write once, ≤ 12 tool calls, no self-made test harnesses | caps the quadratic term |
| Cheaper class | implementation on a Class-B model; top class only for the personality decision and review | ~40% lower price at equal tokens |
| Cache-friendly order | stable skill text first, volatile content last | cache reads at ~0.1× |

Target for the complex-console brief with v2: **≤ 120K tokens, ≤ 12 minutes,
≤ 12 tool calls**, same or better grade. The measured result follows.

## Iteration 3 (v2 skill, same brief) — measured 2026-09-09

| Run | Tokens | Minutes | Tool calls | Output |
|-----|--------|---------|------------|--------|
| **jbelly-ui v2** | **193,996** | **29.0** | **17** | 121 KB, all brief items, verify PASS first render |
| jbelly-ui v1 | 398,111 | 55.3 | 90 | 150 KB |
| catalogue skill | 246,244 | 24.5 | 54 | 144 KB |

v2 vs v1: **−51% tokens, −81% tool calls, −47% wall time**, same brief
coverage and a better chart look. Target (≤ 120K) not yet reached: the
bespoke widgets the generator does not know (heatmap, kanban, tasks,
notifications, table engine) were still model-written. Next lever: generator
flags for those widgets; expected to land a console like this near 100K.

## Measured again, in isolation (2026-09-19)

The two runs above were timed by hand inside a working session, which cannot be repeated and cannot
be trusted. `evals/run.py` now runs one brief under one condition with every other skill switched
off, in a workspace outside this repository, and records what the agent CLI reports. The first
honest result, on `evals/briefs/01-dashboard.md` with one model:

| Condition | Context tokens | Billed tokens | Minutes | Tool calls |
|---|---|---|---|---|
| no skill | 998,682 | 99,198 | 5.4 | 9 |
| a catalogue skill | 2,855,005 | 152,948 | 9.7 | 30 |
| **jbelly-ui** | **5,417,330** | **190,102** | **8.6** | **47** |

**We are the most expensive of the three.** That is the finding, and it is the reason for the work
now in progress. "Context tokens" counts every token sent, cache reads included, because that is
what the cost model charges for: each step re-sends the prefix. "Billed tokens" excludes cache reads.

Where the 47 calls went, from the transcript: four reads of the same reference, two of another,
three probes of the environment, four calls reading the source of the generator and its example to
learn the spec format, two reading the shell, and seven edits patching the built page by hand. Nine
tool calls built the page; the rest was the skill talking to itself.

What changed because of it:

- `SKILL.md` no longer suggests a budget, it names the three calls and refuses the wasteful moves by
  name: no re-reading, no environment probing, no reading script source, no hand-editing what the
  spec could say, no home-made verification.
- The quick card carries the personality presets, so choosing one costs no second file.
- The generator derives the palette, empty state and notification copy from the spec instead of
  leaving the demo's own words for the model to patch.

The number to beat is the catalogue skill's row. `python evals/scoreboard.py` prints WIN or LOSS
against it from the recorded runs; it is not a matter of opinion.
