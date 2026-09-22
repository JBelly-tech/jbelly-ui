# Anti-patterns — the tells of default-AI UI, why they fail, what to do instead

`scripts/preflight.py` checks the ones marked ⚙ mechanically. The rest are
judgement calls for Review mode. Each entry: the tell → why it fails → the
replacement. Use this list when a page "looks generated".

## Colour

- ⚙ **Purple-to-blue gradients (indigo/violet)** → the single most recognised AI signature; carries no meaning → one primary with real chroma from the personality; gradients only as a 10% area fill in charts.
- ⚙ **Gradient text** → unreadable at small sizes, fails contrast tools, dates fast → solid `text-mono` headings; let size and weight do the work.
- ⚙ **Glass (backdrop-blur) on every card** → blurs content behind it, costs GPU, hides hierarchy → blur only on a sticky header or an overlay scrim.
- **Colour as decoration** (random tinted cards, rainbow badges) → users read colour as status; noise destroys the signal → colour only for the primary action, states and chart series.
- ⚙ **Pure `#000` text on white** → harsh, vibrates on dark mode inversion → `--foreground` near-black with a hint of the brand hue.
- **Grey text on coloured backgrounds** → fails contrast → white or the surface's own foreground token; check 4.5:1.

## Typography

- **Inter/system font at one size everywhere** → nothing is first → the house scale: 13px UI, 16px card titles, 20px page title, 30px KPI numbers, 600 weight on titles.
- ⚙ **Uppercase letter-spaced "eyebrow" labels on every section** → visual tic; more than one per three sections reads as template → sentence-case section titles; eyebrows only for a category chip.
- **Thin weights (300) on small text** → illegible, especially on Windows → 400 minimum; 500/600 for emphasis.
- **Centred paragraphs longer than two lines** → hard to scan → left-aligned (start-aligned in RTL), `max-w-prose`.

## Layout

- **Hero + three identical feature cards** → the landing-page template everyone recognises → bento with one hero card, real product screenshots, sections that differ in shape.
- ⚙ **`rounded-2xl` + `shadow-lg` on everything** → cards float like stickers; no grouping → `rounded-xl`, hairline border, `shadow-xs`; elevation only for popovers.
- **Cards inside cards** → borders within borders, wasted padding → sections with `border-b` inside one card.
- **Everything the same size in a grid** → no hierarchy → 2/3 + 1/3 rows; the most important number top-start and largest.
- **Empty page background with text floating on it** → looks unfinished → toolbar or card for every piece of text.
- **Uniform `p-6 gap-4` on every element** → no rhythm → cards `p-5`, rows `gap-2.5`, cards apart `gap-5/7.5`.

## Icons and imagery

- ⚙ **Sparkles / Zap / Rocket icons for "AI" and "fast"** → cliché; says nothing → the icon of the object (invoice, patient, order) or none.
- **Icon-in-a-rounded-square on every card and list row** → decorative repetition → icon chips only on KPI cards and empty states.
- ⚙ **Emoji as icons** → inconsistent across platforms, not themable, screen readers read them aloud → Lucide at 16–20px.
- ⚙ **Generated avatar services (DiceBear)** → obviously fake → initials chips from the real name.
- **Stock photos of handshakes and laptops** → trust drops → product screenshots or no image.

## Motion

Twenty-two refusals, each one a rule `scripts/lint_motion.py` or `scripts/verify_motion.py` runs
rather than an opinion in a document. The rule id is in brackets; the reasoning and the replacement
for each are in `motion.md`.

- ⚙ **`transition: all`**, `transition-property: all`, `transition-all` → animates layout the moment a class adds padding → name the properties. (M03)
- ⚙ **Any Tailwind motion utility** — `transition*`, `duration-*`, `ease-*`, `delay-*`, `animate-*`, including inside `@apply` → motion scattered across markup cannot be reviewed or reduced → declare it in `motion.css`. (M02)
- **A literal duration or curve outside the token region** → six tempos nobody agreed on → `var(--t-*)`, `var(--ease-*)`. (M01)
- **`infinite`, `animation-iteration-count`, `animate-pulse|spin|ping|bounce|marquee`** → a loop reports nothing and fails WCAG 2.2.2 once it runs past five seconds beside other content → the finite elapsed bar, R10. (M09)
- **An animated property outside the compositor, discrete and paint tiers** → layout thrash → a `/* motion-exception: <selector> — <reason> */` line. There are exactly three in this system. (M03)
- **Animated `box-shadow`, `background-position`, `background-size`** → a repaint every frame → `opacity` on a shadow pseudo-element. (M03)
- **Animated `filter: blur()` on text** → illegible for the whole duration. (M03)
- **A transition on the focus ring** — `outline`, `outline-offset`, `box-shadow`, `border-color` under `:focus-visible` → a ring that lags the keyboard reads as input latency. (M03)
- **Any delay other than `0s` or `var(--t-grace)`**, and every stagger: a loop index, an `nth-child` ladder, `stagger(`, `sibling-index()` → a set arriving is one report, not N. (M11, M12)
- **The blanket `@media (prefers-reduced-motion: reduce) { * { …!important } }`** → it freezes loading indicators, never matches `::view-transition-*`, and proves no per-recipe answer was made → `--travel-on: 0` and `--motion-reduce: 0.7`. (M05)
- **An entrance at first paint** — an ungated `@starting-style`, `opacity: 0` in the initial viewport, anything animating within 200ms of load → it animates the page's own arrival and holds the LCP candidate invisible. (M11, V08)
- **Scroll-triggered reveal** — `data-aos`, `AOS.init(`, `whileInView`, `useInView`, an IntersectionObserver writing opacity, `pointer-events: none` as a reveal gate → it reports the viewport moving, not anything changing. `animation-timeline` is permitted on `.read-progress` and `.app-seam::after` and nowhere else. (M10)
- **Scroll hijack and parallax** — Lenis, Locomotive, ScrollSmoother, `ScrollTrigger` with `pin:`/`scrub:`, a `wheel` listener calling `preventDefault()`, `background-attachment: fixed`, `data-speed` → the scrollbar stops telling the truth. (M10)
- **Pointer-driven motion** — magnetic buttons, tilt cards, cursor followers, `cursor: none` → it reports the pointer, and it does not exist on a keyboard. (M08)
- **Per-character or per-word text splitting** → it breaks Arabic letter joining, which makes it a correctness bug and not a taste argument. (M14)
- **A count-up, an odometer, a JavaScript loop writing `textContent`** → a false number in the DOM that assistive technology announces and copy captures → write the true value, then mark it changed. R8. (M14)
- **rAF or a timer writing a motion style**, and `.animate(`, `startViewTransition(` or `view-transition-name` outside the one identity module → JavaScript declares a delta; it never draws a frame. (M08)
- **Overshoot** — a `linear()` stop above 1, a `cubic-bezier` control point outside 0–1 → on a clamped value it is a visible dead hold, not a bounce. (M13)
- **`will-change` in a static stylesheet** → a hint that cannot know when it stopped being true. (M08)
- **Motion as the only delta** → if two states differ only in that one of them moved, the motion was decoration. (V06)
- **Any animation dependency**: gsap, framer-motion, motion, motion-one, aos, lenis, locomotive-scroll, canvas-confetti, tsparticles, tw-animate-css, tailwindcss-animate. (M08)
- **A chart that draws itself in** → motion at first paint → ApexCharts with `animations: { enabled: false }`. (M01)
- **Skeletons that never end / spinners for everything** → users cannot tell loading from broken → a static skeleton at the real row height plus the finite elapsed bar, and an error state with retry after timeout. (M09)

## Content and states

- ⚙ **"Elevate", "Seamless", "Unleash", "Supercharge"** → marketing filler inside a product → verbs and nouns of the domain; sentence case.
- **Lorem ipsum, "John Doe", `user@example.com`, round fake metrics (1,000 users, 99%)** → reads as a mock-up → realistic names for the market, uneven numbers, a comparison line under each KPI.
- **No empty / loading / error states** → the first real user sees a blank → four states per async region.
- **"Submit" / "OK" buttons** → say nothing → "Save changes", "Send invite", "Delete plan".
- **Colour-only status** (green dot, red dot) → invisible to 8% of men, fails audits → text or icon with the colour.
- ⚙ **Icon buttons without a name** → screen readers announce "button" → `aria-label`.

## Process tells (how the page was made)

- **No personality file** → the default look shipped → `design/personality.md` first.
- **Hand-drawn SVG charts** → look unfinished next to a real chart library → ApexCharts with the token theme.
- **Composed from scratch instead of the scaffold** → 3× the tokens and more bugs → `build-screen.py` or `new_screen.py`, then edit.
