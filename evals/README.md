# Evals

- `briefs/`: 12 fixed briefs (dashboard, landing, pricing, sign-up, data table, settings, product page, mobile, dark-first, RTL Arabic, dense admin, empty states). Run each with and without the skill; save outputs in `../comparison/<iteration>/outputs/<maker>/`.
- `trigger-prompts.json`: 12 prompts that should trigger the skill and 12 that should not; use them to tune `description` (target: 90% correct both ways).
- Deterministic checks per output: `scripts/verify_page.py` (render, console errors, lint, pre-flight) and `comparison/tools/grade.py`.
- Across models: a `run-matrix` script is not written yet; the plan is in `docs/power-up-plan.md` Phase 3 (OpenRouter key in `OPENROUTER_API_KEY`, never committed).
