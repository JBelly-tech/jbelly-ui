# Interface guidelines — exact values a script can check and a small model can follow

Restated in our own words from the most-used public interface guidelines and
skills (see `sources.md`). Each line is a rule with a number where one exists.
Use in Build mode as you write a control, and in Review mode as the checklist
behind the ten dimensions.

## Forms and inputs
- Label above the field, always visible; placeholder is an example, never the label. Error text under the field, linked with `aria-describedby`; `aria-invalid` on the control.
- Correct `type`, `inputmode` and `autocomplete` on every input; never block paste; `spellcheck="false"` on emails, codes and usernames.
- Validate on blur, re-validate on input after the first error. On a failed submit keep inline errors and focus a `role="alert"` summary that links to each field when there are more than two.
- Submit stays enabled until the request starts, then disabled with a spinner inside the button (width unchanged). Warn before leaving with unsaved changes.
- Sign-in must accept password managers and paste; OTP inputs auto-advance, accept a pasted code, submit on the last digit.
- Selects with 5 options or fewer become radios or a segmented control. Dates default to today; prefill from the record or the last value.

## Navigation and focus
- `<a>` for navigation, `<button>` for actions; never a `div` with a click handler.
- `:focus-visible` ring on every control (`ring-2 ring-ring ring-offset-2`); `outline-none` only with a replacement.
- **A ring is a box-shadow, and Windows High Contrast drops box-shadow.** Probed with `forced-colors`
  active, a page whose only focus indicator is a ring reports `box-shadow: none` and `outline: none` —
  no indicator at all, for the readers most likely to be on the keyboard. Ship the block in the shells:
  `@media (forced-colors: active) { …:focus-visible { outline: 3px solid CanvasText; outline-offset: 2px } }`,
  and keep it **outside** `@layer components` so it beats the component's own `outline-none`. Add
  `forced-color-adjust: none` only where the colour *is* the information (swatches, chart series). Sticky headers must not cover the focused element: `scroll-padding-top` = header height; heading anchors get `scroll-margin-top`.
- Filters, tabs, sort and page live in the URL so a refresh or a shared link shows the same view.
- One active nav item; nav fits on one line at 1024px; header 70px desktop, 60px mobile.
- Skip link as the first focusable element when there is a nav.
- Destructive actions: confirm only when irreversible, otherwise Undo in a toast (4s).

## Motion
- Motion is declared in `references/motion.css`, never in a class attribute: see `motion.md`. Animate only `transform` and `opacity`; never `transition: all`; `transform-origin` at the trigger for menus and popovers.
- Durations: press feedback 100–160ms, tooltip 125–200ms, dropdown 150–250ms, modal or drawer 200–300ms in, faster out; nothing in the UI above 400ms except the one signature moment (600ms max).
- Easing comes from a token, never a keyword: `--ease-enter` decelerates, `--ease-exit` accelerates, `--ease-move` for identity moves, `--ease-flat` for elapsed time and scroll. Never an accelerating curve for an entering elements.
- Never scale in from 0; start at 0.96–0.98 with opacity. Press feedback `scale(0.97)` on `:active`.
- No animation on keyboard-initiated actions or on anything a user sees more than ten times a session (row hover, toggles, tabs).
- Stagger list entrances 30–80ms per item, max 8 items; exits faster than entrances.
- Hover effects only under `@media (hover: hover) and (pointer: fine)`.
- `prefers-reduced-motion`: keep opacity and colour changes, drop movement; also honour `prefers-reduced-transparency` (drop blur) and `prefers-contrast`.
- Scroll-triggered reveals use `IntersectionObserver`, fire once, never a scroll listener; no parallax on content.
- Anything auto-playing longer than 5s has pause/stop and stops on focus.

## Typography
- UI text 13px, body copy 14–16px, line-height 1.5–1.75 for paragraphs, 1.3 for UI; measure 65–75 characters, never above 80.
- Tracking by size: display `-0.02em`, titles `-0.01em`, body 0, small uppercase labels `+0.04em`. Display line-height 1.05–1.15.
- Weights 400 / 500 / 600 (700 only for display); never 300 on text below 16px.
- `tabular-nums` where digits align (tables, KPIs, axis ticks); proportional in running text.
- `text-wrap: balance` on headings, `…` not `...`, curly quotes, non-breaking space between a number and its unit (`10 MB`, `⌘ K`).
- Arabic: pair a Latin UI face with an Arabic companion at the same optical weight, line-height 1.7 for Arabic body, no tracking on Arabic, numbers stay LTR.

## Colour and contrast
- Text 4.5:1 against its background; large text (≥ 24px, or ≥ 19px bold), icons and control borders 3:1; check light and dark separately.
- One accent (the primary), chroma real but not neon; one neutral family (warm or cool), tinted 0.005–0.015 toward the brand hue.
- No pure `#000` on `#fff`: near-black foreground, off-white page; dark mode surfaces get lighter with elevation, not bigger shadows.
- Shadows tinted toward the background hue, opacity 5% light / 40% dark; two levels only (`shadow-xs`, `shadow-md`).
- Status colours are reserved for status and always carry text or an icon.
- Charts: categorical hues in a fixed order, at most 5 series then "Other"; sequential = one hue light to dark; diverging = two hues with a neutral middle; never recolour on filter.

## Layout and responsive
- `min-height: 100dvh`, never `100vh` or `h-screen` for full-height shells.
- Container max 80rem (1280px) for apps, 72rem for reading; breakpoints 640 / 768 / 1024 / 1280 / 1536; check 375, 768, 1024, 1440.
- Multi-column layouts collapse to one column below 768px, declared per component; tables scroll inside their card, the page never scrolls horizontally.
- Touch targets 44px on touch devices, 24px minimum on desktop, 8px between adjacent targets; `touch-action: manipulation`.
- Z-index scale 10 / 20 / 30 / 40 / 50 (content, sticky, header, sidebar, overlays); never 9999.
- One radius system (`--radius` scale) and one rule per element class; never mix pills and sharp corners on the same control type.
- Images carry `width` and `height`; skeletons reserve height; CLS below 0.1, LCP below 2.5s, INP below 200ms.
- Safe-area insets on fixed bars; scrolling lists get bottom padding equal to any sticky bar.
- Chart marks: 2px lines, markers at least 8px on hover, a 2px surface gap between adjacent fills, hairline grid.

## Content and copy
- Active voice, second person; buttons name the action ("Save changes"); the label stays the same across the flow ("Publish" → "Published").
- Hero: headline at most 2 lines and 8 words, subtitle at most 25 words, two CTAs at most; section headlines at most 8 words.
- Uppercase eyebrow labels at most one per three sections; one CTA label per intent; testimonials at most 3 lines with name and role.
- Numerals for counts; locale formatting for dates and numbers via `Intl`; `translate="no"` on brand names and codes.
- Errors say what happened and what to do next; no "Oops", no apologies, no exclamation marks.
- Sentence case everywhere except proper nouns; no em-dashes in UI copy.

## Accessibility
- Icon-only controls get `aria-label`; decorative icons `aria-hidden="true"`; async regions `aria-live="polite"`; count badges announce context ("3 unread").
- Interactive chips are `<button aria-pressed>`; sortable headers carry `aria-sort`; the active nav item `aria-current="page"`.
- Every drag or swipe interaction has a button and keyboard alternative; announce moves in a live region.
- Every chart has a table twin (`sr-only` or a toggle) and a legend when it has 2 or more series.
- Overlays trap focus, close on Esc, return focus to the opener, lock body scroll.

## Performance
- Lists above 50 rows are virtualised; above 10k rows, server-side pagination.
- Fonts: at most 2 families and 4 weights, preloaded, `font-display: swap`; self-hosted in production.
- `backdrop-blur` only on fixed or sticky layers, blur below 20px; no grain overlays on content.
- CSS transitions for interruptible UI; keyframes only for loaders; no layout reads inside render or scroll handlers.
- Demo and prototype pages may use CDN scripts; a shipped product compiles its CSS and bundles its JS.
