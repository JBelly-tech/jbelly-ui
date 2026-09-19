# Cost — what a screen costs to build with this skill, measured

Agent cost is **Σ (context size × number of steps)**: every tool call re-sends the context built up
before it, so a file read early is paid for again and again. A UI skill can inflate both terms, by
loading a lot of text and by making the agent take many steps. This file records what was measured,
what it exposed, and what changed because of it.

## How the numbers are produced

`python evals/run.py --brief evals/briefs/01-dashboard.md --skill jbelly-ui` runs one brief in a
workspace outside this repository with every other skill switched off, and records what the agent
CLI reports: tokens, wall minutes, tool calls counted from the actual tool-use blocks, and whether
any call reached outside its workspace. A run that leaked is marked and not comparable. Anyone can
repeat it; `evals/README.md` explains the isolation and warns that a run spends real subscription
usage.

Two token figures, on purpose. **Context** is every token sent, cache reads included, because that
is the term the cost model charges for. **Billed** excludes cache reads.

## Measured: one screen, the dashboard brief (2026-09-19)

| Version | Context tokens | Billed tokens | Minutes | Tool calls | Page passes the checks |
|---|---|---|---|---|---|
| before this work | 5,417,330 | 190,102 | 8.6 | 47 | no |
| **now** | **778,232** | **42,859** | **2.3** | **12** | **yes** |
| the same brief with no skill at all | 998,682 | 99,198 | 5.4 | 9 | no |

Building the page was never the expensive part. The losing run's transcript showed where its 47
calls went: the same reference read four times by three different tools, a second reference opened
only to learn the preset names, three probes of the environment, four calls reading the generator's
source to learn its input format, two reading the shell, and seven edits patching the built page by
hand afterwards. Nine calls built the page. The rest was the skill talking to itself.

## What changed

| Lever | What was wrong | What it saves |
|---|---|---|
| The router names the three calls | a budget was suggested, not the calls | most of the 35 wasted calls |
| Refusals written out | re-reading, probing, reading source and hand-editing were left to judgement | each one was measured costing calls for nothing |
| Presets moved into the quick card | choosing one meant opening a 2.9K-token reference | one file read, re-sent on every later call |
| The reference directory compressed, third-party notes moved out of the router | 1.2K tokens of listing rode on every request | entry cost 6,843 → 5,907 tokens per screen |
| The generator derives the palette, empty state and tray copy from the spec | the demo's own words survived into built pages | the seven hand edits |
| Every generated slot is asserted after the build | a field that never landed still exited 0 | silent wrong output |

Two real defects surfaced while doing this, both caught by checks that had never been able to fail:
four personality presets missed the 4.5:1 contrast floor, and every generated page overflowed
horizontally at 375px because the generator rebuilt the toolbar without the wrap the shell had.

## Honest limits

- One brief, one model, one agent, one machine, one run. No repeats, so no variance.
- The dashboard is the shape the generator was written for. A landing page or a pricing page has no
  generator shape yet, so the model writes the markup and these numbers do not carry over. Those
  briefs are next, and their results will be published here whether or not they flatter the skill.
- "Passes the checks" means this project's own deterministic checks: token lint, pre-flight
  (AI-default tells, structure, WCAG contrast of the token pairs), a headless render in light, dark
  and RTL with console errors collected, and no horizontal overflow at 375 or 1440.
