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

- ⚙ **`transition: all`** → animates layout properties, janky, accidental → transition colour/opacity/transform only, 150ms.
- **Bounce/spring on everything, parallax on content** → distracting, motion-sickness → one signature moment; `prefers-reduced-motion` honoured.
- **Skeletons that never end / spinners for everything** → users cannot tell loading from broken → skeleton with reserved height, error state with retry after timeout.

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
