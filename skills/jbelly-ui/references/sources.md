# Sources — where the rules come from

Every rule in this skill traces to one of these public sources or to a
measured run recorded in `evals/`. Nothing is copied from any of them; rules are
restated as instructions with exact values. Use this file to check a rule
or to add one (a new rule needs a row here).

## Research-backed UX rules

| Rule family in the skill | Source |
|---|---|
| Forms: labels above fields, inline errors, focus first error, autosave, progressive disclosure | Nielsen Norman Group articles (https://www.nngroup.com/articles/), Baymard Institute form and checkout research (https://baymard.com/research), GOV.UK Design System patterns (https://design-system.service.gov.uk) |
| Tables: sticky header, row hover actions, bulk bar, saved views, filters in the URL | NN/g data tables, Shopify Polaris and GitHub Primer data-table guidance, Baymard filtering research |
| Dashboards: top-start holds the key number, ≤ 7 focal elements, comparison on every KPI, drill-down | NN/g dashboard guidelines; Laws of UX (Miller, Hick, Fitts) (https://lawsofux.com) |
| Overlays: focus trap, Esc, focus return, scroll lock | WAI-ARIA Authoring Practices dialog pattern (https://www.w3.org/WAI/ARIA/apg/) |
| Contrast 4.5:1 text, 3:1 large text and UI, focus visible, targets ≥ 24px (desktop) / 44px (touch) | WCAG 2.2 (https://www.w3.org/TR/WCAG22/), APCA as the stricter reference (https://apcacontrast.com) |
| Reduced motion, durations 150–400ms, decelerate on enter | Material 3 motion (https://m3.material.io), Apple HIG motion (https://developer.apple.com/design/human-interface-guidelines) |
| State layers (hover 8%, focus 12%, pressed 12%), elevation levels, density steps, type roles | Material 3, Fluent 2 (https://fluent2.microsoft.design), Carbon (https://carbondesignsystem.com) |
| Semantic colour roles, dark-mode role swap, tinted neutrals | Radix Colors (https://www.radix-ui.com/colors), shadcn/ui token conventions |
| Copy: sentence case, verbs on buttons, specific empty and error text | GOV.UK content guidance, Polaris content guidelines |

## Evidence of what people prefer

| Used for | Source |
|---|---|
| The anti-patterns list (what loses head-to-head votes) and the "personality first" rule (what wins) | Design Arena (https://www.designarena.ai), LMArena WebDev (https://web.lmarena.ai): crowd-voted comparisons of generated UI |
| Landing page section order, hero styles, pricing layouts | Curated galleries: Awwwards (https://www.awwwards.com), Godly (https://godly.website), Land-book (https://land-book.com), Refero (https://refero.design) |
| App flows (booking, checkout, onboarding), real screens | Mobbin (https://mobbin.com), Page Flows (https://pageflows.com) |
| Page inventories and flows per business type | A study of the best-selling commercial templates in ten categories (marketplace listings and item pages, 2026-09-09); patterns only |

## Competing skills (what was adopted, what was rejected)

| Skill | Adopted | Rejected (cost) |
|---|---|---|
| frontend-design (anthropics/skills) | the AI-tells list, "spend boldness in one place", copy rules | — |
| web-design-guidelines (vercel-labs/agent-skills) | terse `file:line` findings; interface checklist restated locally | runtime fetch of the rules on every review |
| design-taste-frontend | design read before code, mechanical pre-flight with thresholds, audit-first redesign | 35K-token file loaded every time |
| a catalogue-style UI skill | accessibility-first priority table; searchable data as an idea | 75-word description (fires greedily), style catalogue without build recipes |
| redesign-existing-projects | scan → diagnose → fix, fix-priority order | — |
| emil-design-eng | animation frequency and duration tables, Before/After/Why review rows | — |
| impeccable (critique) | ten-dimension rubric | mandatory two-subagent assessments |
| dataviz | runnable validator, method/parameter split | 230-word description |

## Measured, in this repo

`evals/` and `COST.md`: fixed briefs, isolated runs, deterministic
grader and metrics, tokens and minutes per run.
