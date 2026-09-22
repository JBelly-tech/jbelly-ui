# Motion — twelve recipes, all of them reports

Motion in this system reports a state change and nothing else. It is **declared
in CSS**, never written in a class attribute and never computed in JavaScript.
A stylesheet cannot animate on a timer or on scroll position unless someone
writes a timeline for it, so the default state of this system is *nothing
moves*: decorative motion has to be added on purpose, and `scripts/lint_motion.py`
rejects it when it is. Reduced motion is not a switch that turns the system off
— two tokens remove the travel and shorten the tempo while opacity, colour and
position keep working, so every state is still reported.

If you are adding an animation and cannot name what changed, you are decorating.
Stop.

## Files

```
references/tokens.css   the MOTION TOKENS region — the only place a literal duration,
                        curve or distance may be written
references/motion.css   every transition, keyframe and @starting-style in the system
assets/motion.js        the only file permitted to contain element.animate(,
                        startViewTransition( or view-transition-name
```

Plain CSS, loaded **after** Tailwind. In a single-file page it is a
`<style id="jb-motion">` block placed immediately after the closing `</style>`
of the `type="text/tailwindcss"` block. Unlayered on purpose: it must beat
`@layer utilities` and must not pass through the browser compiler.
`build-screen.py` and `new_screen.py` inline it for you.

## Principles

| # | Rule | Checked by |
|---|---|---|
| P1 | Tokens only. No literal duration, easing or distance outside the sentinel region of `tokens.css`. | M01 |
| P2 | Motion lives in one stylesheet. No Tailwind motion utility in any class attribute. | M02 |
| P3 | Compositor or declared. Animate `transform/translate/rotate/scale/opacity/clip-path/filter`, discrete properties with `allow-discrete`, or paint properties at `--t-tint`. Anything else needs a `/* motion-exception: */` line. There are exactly three. | M03, V03 |
| P4 | Declared cause. Every animating element has `data-motion` on itself or an ancestor. | V02 |
| P5 | State selector only: `:hover :active :focus-visible :checked [data-open] [open] :popover-open ::backdrop`, a gated `@starting-style`, or a guarded `animation-timeline`. Never page load, scroll alone, or a timer. | M05, M11, V08 |
| P6 | JavaScript declares a delta; it never draws a frame. No rAF or timer writes a style. | M08 |
| P7 | Reduce by token: `--travel-on: 0`, `--motion-reduce: 0.7`, plus four named exceptions. | M05 |
| P8 | Substitute or fail. A state whose only delta is positional must carry a second, non-motion delta. | V06 |
| P9 | One subject. At most one element animates a positional property per state change. | V05 |
| P10 | Mirror by sign. Authored inline-axis lengths take `var(--flow-x)`; **measured geometry never does** — it is already mirrored. | M06, M07, V07 |
| P11 | Asymmetry. Enter decelerates and is slower; exit accelerates and is faster. A scrim and its panel reference identical tokens. | V04 |
| P12 | No loops. `infinite` appears nowhere. Waiting is a finite elapsed duration. | M09 |
| P13 | No delays, no stagger. Every delay is `0s` or `var(--t-grace)`. A set arriving is one report, not N. | M11, M12 |
| P14 | The focus ring is never animated. `--motion-preset` stays within 0.85–1.15. | M03, M13 |

## Declared cause

Six values, closed set. An animation whose target resolves no cause is
decoration by definition.

`feedback` the control received the input · `state` a value or selection changed ·
`spatial` a surface opened and it came from somewhere · `continuity` the same
object is in a new place · `status` a wait is outstanding · `position` the
reader moved, not the data.

## Tokens

Durations are named by **class of change**, never by component. Every one
resolves through `--motion-scale` (preset × reduce).

| Token | Base | Use |
|---|---|---|
| `--t-press` | 100ms | the control received the press |
| `--t-tint` | 140ms | paint-tier change; also the paint-tier cap |
| `--t-pop` / `--t-pop-out` | 180 / 130ms | tooltip, menu, popover |
| `--t-menu` / `--t-menu-out` | 220 / 150ms | disclosure, marker, inline panel, list member |
| `--t-move` | 260ms | an object kept its identity and changed position |
| `--t-panel` / `--t-panel-out` | 300 / 200ms | drawer, dialog, sheet, palette |
| `--t-heavy` | 390ms | destructive or irreversible; overdamped |
| `--d-0` | 0ms | keyboard-initiated, and `[data-frequency="constant"]` |
| `--t-grace` | 250ms | no wait shorter than this is reported |
| `--t-elapsed` | 30s | how long a wait has lasted (finite, not a loop) |
| `--t-linger` | 6s | how long a "this just changed" mark stays |

Curves: `--ease-enter` decelerates · `--ease-exit` accelerates · `--ease-move`
for identity moves · `--ease-tint` for paint · `--ease-flat` (linear) for
elapsed time and scroll only · `--spring-ui` (critically damped, pair with
`--t-panel`) · `--spring-heavy` (overdamped, pair with `--t-heavy`) ·
`--ease-elapsed`. No curve in this system has a stop above 1.

Distance: `--travel-sm` 4px · `--travel` 8px · `--travel-lg` 16px ·
`--recoil` 3px · `--panel-travel` 100% · `--press-scale` · `--pop-scale`.
All are multiplied by `--travel-on` (reduce sets it to 0) and `--travel-density`
(compact 0.75, airy 1.25). Density changes distance only: a compact UI is not a
faster UI.

Direction: `--flow-x` is `1` in LTR and `-1` in RTL; `--origin-inline` is
`left`/`right` because `transform-origin` has no logical keyword. Surface:
`--scrim`.

A personality may set `--motion-preset` (0.85–1.15), `--ease-enter`,
`--press-depth`, `--pop-depth` — at most three — and may **nominate one of the
twelve recipes as its signature**, never invent a thirteenth.

## The twelve recipes

The CSS is in `motion.css`. What follows is the markup contract, the reduced
answer and the RTL answer for each.

### R1 Press — `feedback`

```html
<button class="btn" data-motion="feedback">Save changes</button>
<button class="btn" data-motion="feedback" data-frequency="constant">…</button>
```
`scale` to `--press-scale` at `--t-press`, plus `background-color`,
`border-color` and `color` at `--t-tint`. Three named properties, never
`transition-all`. A control used more than about ten times a session takes
`data-frequency="constant"` and gets `--d-0`: no motion at all.
**Reduced:** `--press-scale` resolves to 1, so the scale transition is inert;
the colour step still runs and was always the report.
**RTL:** uniform scale is direction-neutral. Never multiply it by `--flow-x`.

### R2 Menu from its trigger — `spatial`

```html
<button class="btn" popovertarget="acct-menu" data-motion="spatial" data-anchor>Account</button>
<div id="acct-menu" popover class="menu" data-anchored data-motion="spatial">…</div>
```
Zero JavaScript: `display` and `overlay` with `allow-discrete`, a
`@starting-style` for the enter, `transform-origin: top var(--origin-inline)`
so it grows out of its button. The shell form is the same `.menu` with
`data-menu`, and the existing JS flips `data-open` instead of `.hidden` —
not the top layer, so the exit animates in every engine.
**Reduced:** `--pop-scale` → 1 and `--travel-sm` → 0: a pure crossfade. The
provenance is carried by the anchored position and by `aria-expanded`.
**RTL:** `--origin-inline` flips the origin; `position-area` is already logical.

### R3 Panel and scrim — `spatial` / `continuity`

```html
<div class="scrim" data-open></div>
<aside class="panel" data-open data-motion="spatial">…</aside>        <!-- drawer  -->
<div class="panel panel-centre" data-open>…</div>                      <!-- dialog  -->
<div class="panel panel-centre panel-heavy" data-open>…</div>          <!-- destructive -->
```
The drawer travels from its inline edge; a centred overlay belongs to the
viewport, so it scales and does not travel. The scrim is the **same event**:
same two tokens, no exceptions. `panel-heavy` swaps in `--t-heavy` and
`--spring-heavy` for both.
**Reduced:** `--panel-travel` → 0% and `--pop-scale` → 1; the opacity halves
still run. Arrival is reported by the scrim and by focus moving into the panel.
**RTL:** `inset-inline-end` picks the edge, one `--flow-x` multiplier makes it
leave by that same edge. `panel-centre` has no inline bias.

### R4 Disclosure — `state` · declared layout exception

```html
<details class="disclosure" data-motion="state">
  <summary>…<i class="disclosure-chevron" data-lucide="chevron-right"></i></summary>
  …
</details>
```
`::details-content` transitions `block-size` (upgraded silently by
`interpolate-size` where it exists, `grid-template-rows: 0fr→1fr` where it does
not). The chevron rotates `calc(90deg * var(--flow-x))`.
**The sidebar nav group gets no height animation at all** — high frequency, so
only its chevron rotates.
**Reduced:** the panel's `transition-property` narrows to `opacity` and it snaps
open; the chevron snaps to its rotated **end state**. The rotation is state;
only its travel was motion.
**RTL:** `[dir="rtl"] .disclosure-chevron { rotate: 180deg }` for the resting
direction, `--flow-x` for the open rotation, so a closed chevron always points
along the reading direction and always rotates the short way.

### R5 Selection marker — `state`

```html
<div class="marker-group" style="--mark-n: 3" role="tablist">
  <label><input class="sr-only" type="radio" name="t" checked>Monthly</label>
  <label><input class="sr-only" type="radio" name="t">Yearly</label>
  <label><input class="sr-only" type="radio" name="t">Lifetime</label>
  <span class="marker" aria-hidden="true"></span>
</div>
```
Non-negotiable: equal columns (`grid-auto-columns: 1fr`), options as direct
children, the marker last. `:has()` reads the checked index, so the position is
arithmetic — no measurement, no layout effect, no library. Add `marker-fill`
for a segmented control.
**Reduced:** `.marker { transition-property: none }` — it *jumps*. This is the
case that proves "null the travel" is not universal: zeroing the translate
would park the marker under the first option and report the wrong state.
**RTL:** `--flow-x` flips the sign, `inset-inline-start` the origin. One
multiplier, no duplicated rule.

### R6 Arrival and departure — `state`

```html
<tr class="arrives" data-new data-motion="state">…</tr>
<li class="departs list-item">…</li>          <!-- removed through JBMotion.leave(el) -->
```
Entrance is gated on `html[data-ready]`, which one line of script sets after
load: rows that were in the server markup render with no entrance, because the
page arriving is not a state change. `data-new` paints a static inline-start
rail that outlives the motion for `--t-linger`. **The mutation must also produce
a non-motion delta** — a count, an `aria-live` line, an Undo affordance.
`list-item` closes the gap after a removal; that is the second half of the
departure report.
**Reduced:** `--travel` → 0, so members crossfade with no displacement. The
`[data-new]` rail is static and readable minutes later.
**RTL:** entrance travel is block-axis and does not mirror; the departure and
the rail carry `--flow-x`, so a dismissed item leaves by the reading-end edge.

### R7 Sidebar collapse — `continuity` · declared layout exception

`#sidebar` transitions `inline-size` at `--t-panel`; labels and badges fade at
`--t-menu-out`. The content pane and header transition **nothing** — they follow
the rail through layout for free. That is P9 enforced by deletion: the Tailwind
`transition-[padding]` and `transition-[inset]` come off and are not replaced.
**Reduced:** `transition-property: opacity`. The rail snaps, the labels still
fade. A whole-shell reflow is the most vestibular motion an admin page can
produce, so under reduce it is deleted rather than shortened.
**RTL:** `inline-size` and `inset-inline-start` are logical. No signed value.

### R8 Revised in place — `state`

```html
<td class="revises" data-motion="state" data-changed="up">$48,290</td>
```
Script writes the true `textContent` **first**, then sets
`data-changed="up|down"`, then removes it after `--t-linger`. A 2px rail fades
in on the inline-start edge. The element must also carry a non-colour delta —
the KPI's trend badge and icon satisfy it.
**This recipe replaces the count-up**, which writes a false number into the DOM
for 600ms: assistive tech announces intermediate values, copy captures a wrong
figure, and a screenshot is non-deterministic.
**Reduced:** untouched. The only animated property is `opacity` on a 2px rail.
It arrives and stays for six seconds rather than pulsing and decaying, so a user
who blinked can still find what changed.
**RTL:** `inset-inline-start`. No transform, no sign.

### R9 Refusal — `state`

```html
<input class="input refuses" aria-invalid="true" data-refused aria-describedby="err">
<p id="err" role="alert">Card number is 16 digits.</p>
```
One 3px displacement returned by an overdamped curve — resistance, not distress.
Script sets `aria-invalid`, fills the `role="alert"` message, moves focus, then
sets `data-refused` and removes it on `animationend`. Not a three-cycle shake.
**Reduced:** `--recoil` → 0, so the keyframe is inert. The refusal is carried by
`aria-invalid`, the destructive border `.input` already paints, the alert text
and the focus move — all required, so the reduced state is strictly more
informative than the animated one minus its animation.
**RTL:** the recoil carries `--flow-x`. A hard-coded leftward shake means
"pushed back" in English and "pushed forward" in Arabic.

### R10 Pending — `status`

```html
<div class="pends" data-motion="status" aria-busy="true">
  <p role="status" class="sr-only">Loading orders…</p>
  <div class="skeleton h-11"></div>   <!-- static: it reserves height, nothing else -->
</div>
```
A 2px bar that reports **elapsed time**, which the page can know, not activity,
which it cannot. Finite, decelerating, stopping at 92% because it does not know
when the wait ends, and delayed by `--t-grace` so a wait nobody noticed is never
reported. `aria-busy` flips to `"false"` when the data lands.
**This recipe replaces `animate-pulse` and every spinner.** `.skeleton` is
`rounded-md bg-accent` and has no animation.
**Reduced:** the bar keeps running — stopping a progress indicator destroys the
only information it carries — but `--ease-elapsed` becomes `steps(8, end)`, so
it advances in eight discrete jumps. The `role="status"` text is the primary
carrier in both modes.
**RTL:** `transform-origin: var(--origin-inline) center` grows it from the
reading-start edge.

### R11 Position — `position`

```html
<body>
  <div class="read-progress" aria-hidden="true" data-motion="position"></div>
  <header class="app-seam" data-motion="position">…</header>
```
The only scroll-driven motion in the system, and the only thing scroll genuinely
knows. Pure CSS `animation-timeline: scroll(root block)`, no listener, no
library. `aria-hidden` because the browser's own scrollbar is the accessible
equivalent; a `role="progressbar"` with no `aria-valuenow` would be a lie.
`.read-progress` is landing pages only; `.app-seam` is any sticky header.
**Reduced:** `animation-timeline: none` and rest at the true state — the seam
stays visible, the progress bar is removed. The resting styles live *outside*
the `@supports` guard for exactly this reason. A scroll-linked animation has no
duration to shorten, which is the hole the blanket reduce snippet leaves.
**RTL:** `--origin-inline` fills from the reading-start edge; the scroll axis is
block and does not mirror.

### R12 Identity — `continuity`

```html
<tbody data-motion="continuity">
  <tr data-vt-key="ord-10482">…</tr>     <!-- a STABLE domain id, never a row index -->
```
```js
// rare, node-replacing → view transition
JBMotion.reorder(tbody, () => {
  th.setAttribute('aria-sort', dir);        // the non-motion carrier
  tbody.append(...sorted);                  // MOVE the nodes; never re-render
}, { anchor: tbody.querySelector('tr:focus-within') || tbody.rows[0] });

// repeatable → FLIP, and the page stays fully interactive
JBMotion.reflow(grid, () => {
  for (const tile of grid.children) tile.hidden = !match(tile);
  count.textContent = `${n} of ${total} shown`;   // the non-motion carrier
});
```
`view-transition-name` is never authored — `motion.js` leases it at runtime from
`data-vt-key`, only for rendered members within 200px of the scrollport, nearest
the action first, capped at 24. A 5,000-row table therefore produces at most 24
snapshot layers, and a second sort mid-flight is refused rather than snapping.
An element that did not move produces no animation object at all.
**Reduced:** `reflow` returns before animating — a CSS duration override cannot
reach a WAAPI animation, which the blanket snippet misses entirely. `reorder`
still runs, because the identity claim *is* the information; the group animation
collapses to 1ms and the old/new pair keeps cross-fading. `aria-sort` and the
count text are unchanged in every mode.
**RTL:** nothing to do. Both mechanisms derive motion from measured screen
coordinates, which are already mirrored. Applying `--flow-x` to them mirrors
twice; M07 fails that on sight.

## Three things a page has to say for itself

**`.app-seam` on a host that is already positioned.** The recipe sets
`position: relative` so its pseudo-element has something to anchor to, which is
right for a static host and wrong for a header that is already `fixed` or
`sticky` — and `motion.css` is unlayered, so it wins. Such a page adds one line
after it: `header.app-seam { position: fixed; }` (or `sticky`, with its inset).

**A `jb-motion` style block must not contain the character sequence that closes
a style element** — not in a rule, not in a comment. The HTML parser ends the
block there and the rest of the sheet is dropped silently: the page renders
perfectly and simply never animates. V01 is the rule that catches it, and it is
the reason V01 exists.

**A chevron that points down turns a half-turn, not a quarter.** R4's
`calc(90deg * var(--flow-x))` is for a chevron that points along the reading
direction. A `chevron-down` FAQ marker keeps the recipe's tempo and curve and
declares its own angle:

```css
.disclosure summary .faq-chevron { rotate: 0deg; transition: rotate var(--t-menu) var(--ease-move); }
.disclosure[open] summary .faq-chevron { rotate: 180deg; }
```

## Reduced motion

Two tokens do the work: `--travel-on: 0` nulls every displacement, scale depth
and panel travel; `--motion-reduce: 0.7` shortens the tempo. Opacity, colour and
final position keep working, so every state is still reported. Use `1ms`, never
`0.01ms` — some engines treat a sub-millisecond duration as zero and never fire
`transitionend`.

Four exceptions, because in these the position *is* the state:

| Recipe | Why the token is not enough | Answer |
|---|---|---|
| R5 marker | zeroing the translate parks it under option 1 — the wrong state | remove the transition, keep the position |
| R7 sidebar, R4 panel, R6 list gap | layout is not reached by `--travel-on`, and a shell reflow is the most vestibular motion here | narrow `transition-property` to `opacity`; delete, do not shorten |
| R11 seam and progress | a scroll timeline has no duration to shorten | `animation-timeline: none`, rest at the true state |
| R12 view transition | a `*` selector never matches `::view-transition-*`, and CSS cannot reach a WAAPI animation | group to 1ms, keep the old/new cross-fade; `reflow` returns early in JS |

## RTL

Multiply every authored inline-axis length by `var(--flow-x)` and use
`var(--origin-inline)` for any inline `transform-origin`. Do **not** multiply
block-axis motion, uniform `scale`, or non-directional `rotate`. Do **not**
multiply measured geometry from `getBoundingClientRect()` — it is already
mirrored, and doing so sends the element the wrong way. A motion that means
"forward" must not mean "backward" in Arabic.

## Refusals

Each is a linter rule, not an opinion. `lint_motion.py` reads source;
`verify_motion.py` probes the render. Both honour a `motion-lint-ignore`
comment on the line.

1. No `transition: all`, `transition-property: all`, `transition-all`, or Tailwind's bare `transition`. (M02, M03)
2. No Tailwind motion utility anywhere: `transition*`, `duration-*`, `ease-*`, `delay-*`, `animate-*` — including in `@apply`. (M02)
3. No literal duration or curve outside the sentinel token region. Distance comes from the travel tokens, and any authored inline-axis length is checked separately. (M01, M06)
4. No `infinite`, no `animation-iteration-count`, none of `animate-pulse|spin|ping|bounce|marquee`. Waiting is finite. (M09)
5. No animated property outside the three tiers without a `/* motion-exception: <selector> — <reason> */` line. There are exactly three: `#sidebar`, `.disclosure::details-content`, `.list-item`. (M03)
6. No `box-shadow`, `background-position` or `background-size` animation. A lift is `opacity` on a shadow pseudo-element. (M03)
7. No `filter: blur()` animated on an element containing text. (M03)
8. No transition on `:focus-visible` outline, outline-color, outline-offset, box-shadow or border-color. A transitioned focus ring reads as input latency. (M03)
9. No delay other than `0s` or `var(--t-grace)`; none derived from a loop index, an `nth-child` ladder, `stagger(` or `sibling-index()`. (M11, M12)
10. No blanket `@media (prefers-reduced-motion: reduce) { * { …!important } }`. Its presence is itself a failure: it proves no per-recipe answer was made, it freezes loading indicators, and `*` never matches `::view-transition-*`. (M05)
11. No entrance at first paint: no ungated `@starting-style`, no `opacity: 0` or positive delay in the initial viewport, no animation within 200ms of load absent an input event. (M11, V08)
12. No scroll-triggered reveal: no `data-aos`, `AOS.init(`, `whileInView`, `useInView`, no IntersectionObserver writing opacity or transform, no `pointer-events: none` as a reveal gate. `animation-timeline` is permitted on `.read-progress` and `.app-seam::after` and nowhere else. (M10)
13. No scroll hijack or parallax: no Lenis, Locomotive, ScrollSmoother, `ScrollTrigger` with `pin:`/`scrub:`, no `wheel` listener calling `preventDefault()`, no `background-attachment: fixed`, no `data-speed`. (M10)
14. No pointer-driven motion: no `mousemove`/`pointermove` writing a transform (magnetic buttons, tilt cards, cursor followers), no `cursor: none`. A `:hover` rule changing a transform needs a `:focus-visible` counterpart. (M08)
15. No per-character or per-word text splitting. It breaks Arabic letter joining — a correctness bug, not a taste argument. (M14)
16. No JavaScript loop writing `textContent` to animate a value. Count-ups and odometers put a false number in the DOM. (M14)
17. No rAF or timer writing a motion style property. No `.animate(`, `startViewTransition(` or `view-transition-name` outside `assets/motion.js`. (M08)
18. No overshoot: no `linear()` stop above 1, no `cubic-bezier` with y > 1. An overshoot on a clamped value is a visible dead hold. (M13)
19. No `will-change` in a static stylesheet. A hint cannot know when it stopped being true. (M08)
20. No motion-only state change: if two states differ only in that one of them moved, the motion was decoration. (V06)
21. No animation dependency: gsap, framer-motion, motion, motion-one, aos, lenis, locomotive-scroll, canvas-confetti, tsparticles, tw-animate-css, tailwindcss-animate. (M08)
22. ApexCharts renders with `animations: { enabled: false }`. A chart drawing itself in is motion at first paint. (M01)

No thirteenth recipe without an entry here saying what state it reports and
which rule permits it.

## Checking it

```
python scripts/lint_motion.py <file-or-dir>      # M01-M14, source only, no browser
python scripts/verify_motion.py <page.html>      # V01-V08, drives the page in Chromium
```

Both print `file:line: RULE — evidence` and exit 1 on any finding, 2 when there was nothing to
check — a zero-file scan is never a pass. `verify_page.py` runs both, and without Playwright the
runtime probe prints `[SKIP] motion runtime: no Playwright — not verified` and returns 0 without
claiming a pass. One line is silenced with a `motion-lint-ignore` comment on it; there is exactly
one in the shipped system, on the `1ms` that collapses a view-transition group under reduce.
