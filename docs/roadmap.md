# Roadmap

What the beta still has to prove, in the order it will be done. Each item lands with numbers in `COST.md` or `comparison/`, not with a promise.

| # | Item | Done when |
|---|------|-----------|
| 1 | **Eval matrix across models**: the 12 briefs in `evals/briefs/` run with and without the skill on whatever models the contributor's own agent already gives them, graded by `scripts/preflight.py` and `comparison/tools/grade.py`. No paid API is required and none will be added | A table of pass rates and token cost per model replaces the "one model family" caveat in the README |
| 2 | **Cross-agent runs**: the same brief in at least three agents that read the Agent Skills format, plus the two `dist/` tiers in a chat-only tool | Recorded runs under `comparison/` for each agent, with `timing.json` |
| 3 | **Blind rating**: pairs of screens (skill / no skill / catalogue skill) rated by people who do not know which is which | Ratings and method published in `comparison/` |
| 4 | **Generator widgets**: heatmap, kanban, task list and notification drawer as spec options in `scripts/build-screen.py`, so a complex console needs no model-written markup | Complex-console brief at or under 120K tokens with the same grade |
| 5 | **Accessibility in CI**: an axe-core pass on the demo and on every smoke-test page | CI fails on a new violation |
| 6 | **Trigger precision**: `evals/trigger-prompts.json` measured against the `description` | 90% correct both ways or better, recorded in `evals/README.md` |

Ideas and reports go through the [issue templates](../.github/ISSUE_TEMPLATE/); a report with a screenshot and the verdict lines is worth more than a feature request.
