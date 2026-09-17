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
