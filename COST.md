# Cost — what a screen costs to build with this skill, measured

Agent cost is **Σ (context size × number of steps)**: every tool call re-sends the context built up
before it, so a file read early is paid for again and again. A UI skill can inflate both terms, by
loading a lot of text and by making the agent take many steps. This file records what was measured,
what it exposed, and what changed because of it.

## How the numbers are produced

`python evals/run.py --brief evals/briefs/01-dashboard.md --skill jbelly-ui` runs one brief in a
workspace outside this repository with every other skill switched off, and records what the agent
CLI reports: tokens, wall minutes, tool calls counted from the actual tool-use blocks, and whether
any call reached outside its workspace. A run that leaked is marked and not comparable.

Every number below points at the file the run wrote. Those files are in
[`evals/records/`](evals/records/) — one per run, the counts exactly as the CLI reported them, with
only the machine's own paths removed. Anyone can repeat a run; `evals/README.md` explains the
isolation and warns that a run spends real subscription usage. It will not reproduce exactly: an
agent is not deterministic, and one run is not a distribution.

Two token figures, on purpose. **Context** is every token sent, cache reads included, because that
is the term the cost model charges for. **Billed** excludes cache reads.

## Measured: three briefs (2026-09-19)

| Brief | Context tokens | Billed | Minutes | Tool calls | Record |
|---|---|---|---|---|---|
| Dashboard | **831,640** | 97,004 | **2.07** | **10** | [run](evals/records/01-dashboard-jbelly-ui-20260919-162651.json) |
| Landing page | 1,321,657 | 132,137 | 7.21 | 13 | [run](evals/records/02-landing-jbelly-ui-20260919-164728.json) |
| Pricing page | 4,906,916 | 182,638 | 9.28 | 41 | [run](evals/records/03-pricing-jbelly-ui-20260919-170349.json) |

**A pricing page costs six times a dashboard, and that is the most useful number here.** The
dashboard is the shape the page builder knows: a spec of about 2 KB becomes the whole screen, and
the model writes no markup at all. There is no generator shape for a pricing page yet, so the model
writes every line itself — and the cost is what it costs to write a page by hand, which is what this
skill exists to avoid. The gap between those two rows is the honest measure of how much of the work
is actually automated: not all of it.

## What the transcripts showed

Building the page was never the expensive part. An earlier dashboard run took 47 tool calls, and the
transcript showed where they went: the same reference read four times by three different tools, a
second reference opened only to learn the preset names, three probes of the environment, four calls
reading the generator's source to learn its input format, two reading the shell, and seven edits
patching the built page by hand afterwards. Nine calls built the page. The rest was the skill
talking to itself.

| Lever | What was wrong | What it saves |
|---|---|---|
| The router names the three calls | a budget was suggested, not the calls | most of the wasted calls |
| Refusals written out | re-reading, probing, reading source and hand-editing were left to judgement | each one was measured costing calls for nothing |
| Presets moved into the quick card | choosing one meant opening a 2.9K-token reference | one file read, re-sent on every later call |
| The reference directory compressed, third-party notes moved out of the router | 1.2K tokens of listing rode on every request | entry cost 6,843 → 5,907 tokens per screen |
| The generator derives the palette, empty state and tray copy from the spec | the demo's own words survived into built pages | the seven hand edits |
| Every generated slot is asserted after the build | a field that never landed still exited 0 | silent wrong output |

Two real defects surfaced while doing this, both caught by checks that had never been able to fail:
four personality presets missed the 4.5:1 contrast floor, and every generated page overflowed
horizontally at 375px because the generator rebuilt the toolbar without the wrap the shell had.

## A number this file used to publish, and does not any more

An earlier version of this table showed a before-and-after pair: 5,417,330 context tokens and 47
tool calls before the work, 778,232 and 12 after. Both runs were made under a harness that denied
every condition access to its own skill directory, so an agent that tried to read its own reference
was refused and fell back to shell commands — which were then counted against it as waste. The
measurement was wrong in a direction that flattered the result, so the pair is withdrawn rather than
restated, and the runs are archived unpublished. The deny rules are now built one directory at a
time, so a run can read its own skill and nothing else. The comparison will be made again under the
corrected harness and published here, whatever it says.

The same applies to the no-skill baseline that used to sit in this table. It was measured under the
same broken harness and is not shown until it is re-run.

## Honest limits

- Three briefs, one model, one agent, one machine, **one run each**. No repeats, so no variance, and
  a single run of an agent is a weak measurement. Treat the ordering as real and the precision as
  not.
- The three briefs were chosen because they are the shapes this system is for. They are not a random
  sample of UI work.
- "Isolated" in the table means no tool call reached outside the run's workspace except into the
  skill under test. It does not mean the agent knew nothing about the task beforehand.
- "Passes the checks" elsewhere in this repository means this project's own deterministic checks:
  token lint, pre-flight (AI-default tells, structure, WCAG contrast of every colour role the page
  uses as text), a headless render in light, dark and RTL with console errors collected, and no
  horizontal overflow at 375 or 1440. They are a floor, not a review.
