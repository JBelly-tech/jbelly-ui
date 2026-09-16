# Review rubric — judge a UI like a senior designer, in one pass

Use when asked to review, critique, audit or "make this look professional".
No subagents, no second opinions: run the two scripts first (they are the
objective half), then score the ten dimensions below from the rendered
screenshot and the markup, and report findings as `file:line` rows.

```
python scripts/preflight.py <page-or-dir>        # AI tells, structure, token contrast
python scripts/verify_page.py <page> --variants ",#dark=1,#dir=rtl"   # renders + console + lint
python scripts/audit_styles.py <src-dir>         # for redesigns: inventory + deviation list
```

## Ten dimensions (score 1–5; 3 = acceptable shipping quality)

| # | Dimension | 5 looks like | 1 looks like | Evidence to cite |
|---|-----------|--------------|--------------|------------------|
| 1 | Hierarchy | one thing is clearly first; sizes and weights step down predictably | everything the same weight; three competing headlines | KPI/title sizes, primary count |
| 2 | Spacing rhythm | 4px scale, `gap-5/7.5` between cards, `gap-2.5` in rows, equal card padding | random paddings, cards touching, orphaned margins | spacing audit distinct count |
| 3 | Alignment | text baselines and card edges line up on a grid; numbers right-aligned | ragged columns, mixed-height controls in one row | control heights, `tabular-nums` |
| 4 | Colour discipline | one primary, neutral chrome, status colours only for status | raw palette classes, gradients, colour as decoration | preflight tells, lint |
| 5 | Typography | ≤ 2 families, 3 weights, 13px UI / 16px card titles / 20px page title, tight tracking on titles only | 4 families, thin weights on small text, letter-spaced body | fonts audit |
| 6 | Density | matches the user (compact for operators, airy for consumers), consistent across cards | half the page dense, half sparse | density class, row heights |
| 7 | States | loading, empty, error, success each designed; hover and focus visible | blank areas while loading, no empty state, invisible focus | verify screenshots per `#state=` |
| 8 | Motion | 150ms colour/opacity, 200–250ms open/close, one signature moment, reduced-motion honoured | `transition: all`, bounces, parallax on content | durations audit, tells |
| 9 | Accessibility | contrast ≥ 4.5, labels on icon buttons, skip link, `aria-current`/`aria-sort`, keyboard closes overlays | icon-only buttons unnamed, 3:1 grey text, Esc does nothing | preflight contrast + structure |
| 10 | Copy | sentence case, verbs on buttons, specific empty/error text | "Submit", "Elevate your workflow", lorem | filler-word tells |

Weighting for the headline score: dimensions 4, 7 and 9 count double (they
are what users notice and what fails audits). Anything scored 1 or 2 is a
finding; 3 is not.

## Output format (machine-readable, no narrative)

```
score: 3.6/5  (colour 4, states 2, a11y 3 …)
| file:line | dimension | before | after | why |
| index.html:212 | states | table shows nothing while loading | 5 skeleton rows (skeleton recipe) | users think it is broken |
| index.html:88 | colour | bg-blue-600 on the CTA | bg-primary | tokens drive dark mode and re-brand |
```

One row per finding, ordered by impact (colour and states first, copy last),
at most 12 rows. If the scripts already printed a finding, reference it
rather than restating it. End with the three fixes that raise the score the
most; nothing else.

## Redesign protocol (audit first)

1. `audit_styles.py` on the source; read its deviation list.
2. Decide the personality (`references/personalities.md`) before touching CSS.
3. Fix in priority order: fonts → colour system → radius/shadow → spacing → states → motion.
4. Change tokens, not components, wherever a token exists; touch markup only for structure and states.
5. Verify once (`verify_page.py`), pre-flight once, done.
