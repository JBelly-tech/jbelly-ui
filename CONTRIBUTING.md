# Contributing to jbelly-ui (beta)

jbelly-ui is in **public beta**. The rules, recipes and scripts work and are
measured on a handful of briefs with one model family; the claim "works on
any agent and model" is what the beta is meant to test. Every report and every
run you share makes the next version better.

## The fastest way to help

1. Install it (`npx skills add mohammadJohar/jbelly-ui` or `./install.sh` / `.\install.ps1`).
2. Ask your agent for a real screen from your own work.
3. Run the two checks on the result and open an issue with the numbers:
   ```bash
   python skills/jbelly-ui/scripts/verify_page.py <page.html> --variants ",#dark=1,#dir=rtl" --widths 1440,375
   python skills/jbelly-ui/scripts/preflight.py <page.html>
   ```
4. Use the **"UI came out bad"** issue template: brief, agent, model, the
   verdict lines, and a screenshot. Bad results are the most valuable input;
   each one becomes a new brief in `evals/briefs/`.

## Running the evals

- `evals/briefs/` has 12 fixed briefs. Run one with and without the skill and
  put the outputs under `comparison/<iteration>/outputs/<maker>/dashboard-<maker>.html`
  (name the maker after the tool that produced it).
- Grade and measure: `python comparison/tools/grade.py <iteration-dir>`,
  `python comparison/tools/dom_metrics.py`, `python comparison/tools/visual_metrics.py`,
  then `assemble_report_data.py` + `build_report.py` for the side-by-side page.
- Record tokens, minutes and tool calls in `timing.json` next to each output;
  `COST.md` is built from those numbers.

## Changing the skill

- Source of truth is `skills/jbelly-ui/`. `dist/` is generated: run
  `python skills/jbelly-ui/scripts/build_dist.py` and commit the result;
  CI fails if `dist/` drifts.
- A new rule needs a row in `references/sources.md` (research, design system
  or a measured run). A new "AI tell" goes in `references/anti-patterns.md`
  and, if a script can check it, in `scripts/preflight.py`.
- Keep `SKILL.md` under 500 lines and about 4K tokens; long content belongs in
  `references/`, opened on demand. Keep the `description` short; it rides in
  every request for every user.
- Never add subagent fan-out or mandatory re-check loops: cost is part of the
  design. Prefer a script (deterministic) to a rule the model must remember.
- Never add code, CSS, images, fonts or icons from commercial templates or
  from other skills; restate rules in your own words and cite the source.
- Run `python tests/smoke.py` before a pull request.

## Forking

MIT licence: fork it, rename it, ship it. If you publish a derivative, a link
back helps people find the upstream evals and the fixes, but it is not required.

## Reporting a security or licence concern

Open an issue with the "licence / attribution" label. Anything that turns out
to be copied from a non-permissive source is removed, not argued about.
