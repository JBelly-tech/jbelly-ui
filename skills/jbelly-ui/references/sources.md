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
| Error summary on every failed submit: "There is a problem", one link per error, focus on the summary, hidden "Error:" prefix, "Error: " in the title | GOV.UK Design System, Error summary (https://design-system.service.gov.uk/components/error-summary/) and Error message (https://design-system.service.gov.uk/components/error-message/), Open Government Licence v3 |
| No cognitive test in sign-in; nothing asked twice in one flow | WCAG 2.2 3.3.8 Accessible Authentication and 3.3.7 Redundant Entry, as summarised in MDN's Understanding WCAG guides (https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides/Understanding_WCAG/Understandable), CC-BY-SA 2.5 |
| Target size 24×24 CSS px with the spacing exception | WCAG 2.2 2.5.8 (MDN's Operable guide); GitHub Primer icon-button guidance (https://primer.style/components/icon-button, MIT); axe-core `target-size` rule (https://github.com/dequelabs/axe-core, MPL-2.0) |
| `check_a11y.py`: lang, alt, names on links and buttons, labels, heading order | The recurring failure list of WebAIM's yearly sweep of the top million home pages (https://webaim.org/projects/million/), restated as checks; W3C WAI tutorials for the fixes (https://www.w3.org/WAI/tutorials/), W3C document licence |
| `text-wrap: pretty` as a progressive enhancement | web-features, `text-wrap-pretty` and `text-wrap` (https://github.com/web-platform-dx/web-features, Apache-2.0): spec and compat keys; balance is Baseline, pretty is not yet |

## Evidence of what people prefer

| Used for | Source |
|---|---|
| The anti-patterns list (what loses head-to-head votes) and the "personality first" rule (what wins) | Design Arena (https://www.designarena.ai), LMArena WebDev (https://web.lmarena.ai): crowd-voted comparisons of generated UI |
| Landing page section order, hero styles, pricing layouts | Curated galleries: Awwwards (https://www.awwwards.com), Godly (https://godly.website), Land-book (https://land-book.com), Refero (https://refero.design) |
| App flows (booking, checkout, onboarding), real screens | Mobbin (https://mobbin.com), Page Flows (https://pageflows.com) |
| Page inventories and flows per business type | A study of the page inventories buyers of admin and SaaS products expect in ten categories (2026-09-09); patterns only, nothing reproduced |

## Other skills and tools this one learned from

Ideas adopted, with the project they came from. Each is restated here in this project's own words
and adapted to its own structure; none of their text is reproduced.

| Source | What it taught this project |
|---|---|
| frontend-design (anthropics/skills) | the AI-tells list, "spend boldness in one place", the copy rules |
| web-design-guidelines (vercel-labs/agent-skills) | terse `file:line` findings, and an interface checklist worth keeping locally |
| design-taste-frontend | a design read before any code, a mechanical pre-flight with thresholds, audit-first redesign |
| redesign-existing-projects | scan → diagnose → fix, and the order to fix in |
| emil-design-eng | animation frequency and duration tables, Before/After/Why review rows |
| impeccable (critique) | the ten-dimension review rubric |
| dataviz | a runnable validator, and the method/parameter split |

## Measured, in this repo

`evals/` and `COST.md`: fixed briefs, isolated runs, deterministic
grader and metrics, tokens and minutes per run.
