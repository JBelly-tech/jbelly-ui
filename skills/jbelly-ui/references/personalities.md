# Personalities — the layer that stops every product looking the same

The foundation (tokens roles, shell, recipes, behaviours) is shared. The
**personality** is not. Every product must pick or derive one before the first
screen is built, and the choice is written down in the project (see "Persist"
at the end). Skipping this step is how AI-built UIs all converge on the same
look: blue-600 buttons, Inter, zinc greys, `rounded-2xl shadow-lg`, purple
gradients, icon-in-a-rounded-square, hero + three cards.

A personality decides eight things. Change all eight together; changing only
the primary colour produces "the same site in a different shirt".

| Dial | What it sets | Range |
|------|--------------|-------|
| **Type pairing** | display face for headings/KPI numbers + text face for UI | **House default: Inter for both**, tuned like the best admin templates (13px UI, 600 headings, `tracking-tight` on card titles, `tabular-nums` on figures). Change the display face only when the brand asks for it; the palette, shape, density and signature carry identity on their own |
| **Palette** | `--primary` (+ optional `--accent` for one sharp highlight), neutral tint (cool / warm / pure), `--background` tint | primary with real chroma; neutrals tinted toward the brand hue |
| **Shape** | `--radius` | 0 (sharp) · 0.25rem · 0.5rem · 0.75rem · 1rem (soft) |
| **Density** | control heights, table rows, card padding | compact (ops tools) · standard · airy (consumer / clinical) |
| **Surface** | how cards separate from the page | flat-bordered · tinted-page (white cards on tinted bg) · elevated (soft shadow, no border) · outlined-only |
| **Motion** | tempo and character | `--motion-preset` 0.85–1.15 · optionally `--ease-enter`, `--press-depth`, `--pop-depth` · at most three overrides · a preset may **nominate one of the twelve recipes as its signature**, never invent a thirteenth |
| **Signature element** | one recognisable device, used consistently | e.g. thick start-border on active nav, oversized KPI numerals, hairline grid backdrop, dotted separators, offset shadow, corner tab on cards, monospaced meta text |
| **Data colour set** | the 3–5 series colours for charts | derived from primary + one contrasting hue, never rainbow |

## Link colour

Every preset declares `--primary-accent` next to `--primary`. It is the same hue, moved in
lightness until it reaches 4.5:1 against that preset's card and page. Declare it inside the preset
block: a `var(--primary)` written on `:root` is computed there, so it keeps the default blue no
matter which preset is active.

## Six ready presets

All presets keep **Inter** as the text face unless a line says otherwise; the `--font-display` lines are optional accents you may delete to stay 100% Inter (the recommended default for admin products).

Each is a `.theme-*` class on `<html>` that overrides tokens. Pick the closest,
then **change at least two dials** so the product owns it. Font imports are
Google Fonts (all OFL-licensed).

**A preset is two blocks.** `.theme-x` sets the light surfaces; `.theme-x.dark` sets the dark
ones. Ship both or neither. Both `.theme-x` and `.dark` are a single class, so source order decides
between them, and a preset written after `.dark` -- the normal order -- leaves the preset's *light*
card under dark mode's white text: the buttons vanish and come back on hover, because hover paints
`--accent`, which is still the dark one. `preflight.py` builds `.theme-x.dark` and checks it even
when no rule declares it, so a missing dark half fails rather than passing quietly.

**And every role it sets belongs in both.** `.theme-x` and `.dark` are each a single class, and a
preset is written after dark mode, so source order hands the preset every role it declares -- in
*both* modes. A `--muted-foreground` chosen for a light page is then what the dark page paints, and
nothing takes it back except the same role in `.theme-x.dark`. That is why `--destructive-accent`,
`--success-accent`, `--warning-accent` and `--info-accent` are declared once in `:root` and once in
`.dark` and never inside a preset: a role a preset does not declare cannot leak. `preflight.py`
names any role that does.

### 1. `theme-clinic` — calm, clinical, trustworthy (health, nutrition, insurance)

```css
.theme-clinic {
  --font-display: "Manrope", var(--font-sans);          /* geometric, soft */
  --font-sans: "Manrope", ui-sans-serif, system-ui, sans-serif;
  --primary: oklch(50% 0.12 195);                        /* deep teal, 4.6:1 with white */
  --primary-accent: oklch(45% 0.12 195);               /* links: 5.16:1 */
  --primary-foreground: oklch(100% 0 0);
  --accent-strong: oklch(72% 0.17 60);                   /* one warm highlight: amber-peach */
  --background: oklch(98.5% 0.006 190);                  /* faint teal tint */
  --card: oklch(100% 0 0);
  --border: oklch(92% 0.012 190);
  --input: oklch(62.3% 0.014 190);
  --muted: oklch(96% 0.01 190);
  --radius: 0.75rem;
  --density: airy;                                       /* see density block below */
}
.theme-clinic.dark { --primary-accent: oklch(70% 0.13 195); --background: oklch(15% 0.012 195); --card: oklch(18% 0.012 195); --popover: oklch(18% 0.012 195); --border: oklch(28% 0.015 195); --input: oklch(55.2% 0.015 195); --muted: oklch(22% 0.012 195); --accent: oklch(24% 0.014 195); --primary: oklch(70% 0.13 195); --primary-foreground: oklch(12% 0.02 195); }
```
Surface: tinted-page. Motion: `--ease-enter: var(--spring-ui)`; signature R3, the drawer settles. Signature: KPI numerals in `--font-display` at `text-4xl`, and a 3px `bg-primary` start-border on the active nav item. Data colours: teal · amber · slate-blue · sage.

### 2. `theme-graphite` — dense, technical, precise (fintech, ops, dev tools)

```css
.theme-graphite {
  --font-display: "IBM Plex Sans", var(--font-sans);
  --font-sans: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, monospace;
  --primary: oklch(65% 0.17 150);                        /* signal green */
  --primary-accent: oklch(47.5% 0.17 150);            /* links: 4.52:1 */
  --primary-foreground: oklch(14% 0 0);
  --background: oklch(97% 0.002 260); --muted-foreground: oklch(54% 0.014 285);
  --card: oklch(100% 0 0);
  --border: oklch(88% 0.004 260);
  --radius: 0.25rem;
  --density: compact;
}
.theme-graphite.dark { --muted-foreground: oklch(65.5% 0.014 285); --primary: oklch(65% 0.17 150); --primary-accent: oklch(69% 0.17 150); --background: oklch(12% 0.004 260); --card: oklch(15% 0.004 260); --popover: oklch(15% 0.004 260); --border: oklch(24% 0.005 260); --input: oklch(55.5% 0.005 260); }
```
Surface: flat-bordered, tables everywhere, `tabular-nums` on all numbers. Motion: `--motion-preset: 0.85`; signature none, deliberately: still. Signature: monospaced meta text (IDs, timestamps, amounts) and 1px dotted separators. Data colours: green · sky · amber · magenta (all at equal lightness).

### 3. `theme-editorial` — warm, human, content-first (community, education, media)

```css
.theme-editorial {
  --font-display: "Fraunces", Georgia, serif;             /* serif display with optical sizing */
  --font-sans: "Source Sans 3", ui-sans-serif, system-ui, sans-serif;
  --primary: oklch(48% 0.16 30);                          /* brick */
  --primary-accent: oklch(48% 0.16 30);                /* links: 6.59:1 */
  --primary-foreground: oklch(98% 0.01 60);
  --background: oklch(97.5% 0.012 75);                    /* warm paper */
  --card: oklch(99% 0.008 75);
  --foreground: oklch(22% 0.02 50);
  --border: oklch(90% 0.02 70);
  --muted: oklch(94% 0.015 75);
  --muted-foreground: oklch(50% 0.03 50);
  --radius: 0.5rem;
  --density: standard;
}
.theme-editorial.dark { --shadow-xs: 0 1px 3px rgb(20 10 0 / 0.5); --shadow-md: 0 6px 16px -6px rgb(10 5 0 / 0.6); --primary-accent: oklch(73% 0.15 35); --background: oklch(16% 0.012 60); --card: oklch(19% 0.012 60); --popover: oklch(19% 0.012 60); --foreground: oklch(95% 0.01 75); --mono: oklch(95% 0.01 75); --border: oklch(28% 0.015 60); --input: oklch(55.5% 0.015 60); --muted: oklch(23% 0.012 60); --accent: oklch(25% 0.014 60); --muted-foreground: oklch(65% 0.02 60); --primary: oklch(70% 0.15 35); --primary-foreground: oklch(14% 0.02 40); }
```
Surface: elevated (no border, `shadow-md` at 6% warm black). Motion: `--motion-preset: 1.15`; signature R4, the disclosure. Signature: serif display headings, generous `max-w-prose` measure, hairline rules with small caps labels. Data colours: brick · olive · mustard · ink.

### 4. `theme-neo` — bold, energetic, opinionated (startups, creator tools, marketing)

```css
.theme-neo {
  --font-display: "Space Grotesk", var(--font-sans);
  --font-sans: "DM Sans", ui-sans-serif, system-ui, sans-serif;
  --primary: oklch(55% 0.25 290);                         /* electric violet */
  --primary-accent: oklch(51.5% 0.25 290);               /* links: 5.32:1 */
  --primary-foreground: oklch(100% 0 0);
  --accent-strong: oklch(90% 0.2 105);                    /* acid yellow for one highlight */
  --background: oklch(99% 0 0);
  --card: oklch(100% 0 0);
  --foreground: oklch(10% 0 0);
  --border: oklch(10% 0 0);                               /* hard 1px ink borders */
  --radius: 0.25rem;
  --shadow-xs: 3px 3px 0 0 var(--foreground);             /* offset shadow — the signature */
  --shadow-md: 5px 5px 0 0 var(--foreground);
  --density: standard;
}
.theme-neo.dark { --shadow-xs: 3px 3px 0 0 var(--foreground); --shadow-md: 5px 5px 0 0 var(--foreground); --primary-accent: oklch(75% 0.2 290); --background: oklch(12% 0 0); --card: oklch(15% 0 0); --popover: oklch(15% 0 0); --foreground: oklch(98% 0 0); --mono: oklch(98% 0 0); --border: oklch(98% 0 0); --input: oklch(98% 0 0); --primary: oklch(75% 0.2 290); --primary-foreground: oklch(10% 0 0); }
```
Surface: outlined-only with offset shadows. Motion: `--motion-preset: 0.85; --press-depth: 0.05`; signature R1, a harder press. Signature: offset shadow + uppercase `tracking-wide` labels. Use sparingly on data-heavy admin screens (keep tables plain). Data colours: violet · yellow · black · coral.

### 5. `theme-slate` — quiet enterprise, high contrast (B2B admin, legal, government)

```css
.theme-slate {
  --font-display: "Public Sans", var(--font-sans);
  --font-sans: "Public Sans", ui-sans-serif, system-ui, sans-serif;
  --primary: oklch(42% 0.12 260);                         /* navy */
  --primary-accent: oklch(42% 0.12 260);               /* links: 7.76:1 */
  --primary-foreground: oklch(100% 0 0);
  --background: oklch(96.5% 0.004 250); --muted-foreground: oklch(53% 0.014 285);
  --card: oklch(100% 0 0);
  --foreground: oklch(18% 0.02 260);
  --border: oklch(88% 0.008 250);
  --radius: 0.375rem;
  --density: standard;
  --sidebar: oklch(18% 0.03 260);                          /* dark navy sidebar on light page */
  --sidebar-foreground: oklch(92% 0.01 250);
  --sidebar-muted: oklch(65% 0.02 250);
  --sidebar-accent: oklch(24% 0.03 260);
  --sidebar-accent-foreground: oklch(100% 0 0);
  --sidebar-primary: oklch(78% 0.12 80);                   /* gold active marker */
  --sidebar-border: oklch(26% 0.03 260);
}
.theme-slate.dark { --muted-foreground: oklch(65.5% 0.014 285); --primary-accent: oklch(72% 0.12 80); --background: oklch(13% 0.02 260); --card: oklch(17% 0.02 260); --popover: oklch(17% 0.02 260); --foreground: oklch(95% 0.01 250); --border: oklch(26% 0.02 260); --input: oklch(55.5% 0.02 260); --primary: oklch(72% 0.12 80); --primary-foreground: oklch(15% 0.03 80); --sidebar: oklch(11% 0.02 260); }
```
Surface: tinted-page with a dark sidebar. Motion: `--motion-preset: 0.9`; signature R5, the marker. Signature: gold active-nav marker on navy; sentence-case everything; no icons in table headers. Data colours: navy · gold · steel · teal.

### 6. `theme-mint` — light, friendly, consumer-grade (wellness, retail, apps with a public face)

```css
.theme-mint {
  --font-display: "Plus Jakarta Sans", var(--font-sans);
  --font-sans: "Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif;
  --primary: oklch(60% 0.15 165);                         /* mint-green */
  --primary-accent: oklch(45.5% 0.15 165);             /* links: 4.51:1 */
  --primary-foreground: oklch(14% 0 0);
  --accent-strong: oklch(70% 0.18 25);                    /* coral */
  --background: oklch(98% 0.01 160);
  --card: oklch(100% 0 0);
  --border: oklch(93% 0.02 160);
  --radius: 1rem;
  --shadow-xs: 0 1px 2px rgb(20 60 40 / 0.06);
  --shadow-md: 0 8px 24px -8px rgb(20 60 40 / 0.18);
  --density: airy;
}
.theme-mint.dark { --shadow-xs: 0 1px 2px rgb(0 20 12 / 0.5); --shadow-md: 0 8px 24px -8px rgb(0 20 12 / 0.6); --primary-accent: oklch(72% 0.15 165); --background: oklch(14% 0.01 160); --card: oklch(18% 0.012 160); --popover: oklch(18% 0.012 160); --border: oklch(27% 0.015 160); --input: oklch(55.2% 0.015 160); --muted: oklch(22% 0.012 160); --accent: oklch(24% 0.014 160); --primary: oklch(72% 0.15 165); }
```
Surface: elevated, pill buttons (`rounded-full` on buttons and badges only). Motion: `--motion-preset: 1.1; --pop-depth: 0.06`; signature R2, the menu. Signature: pill controls + big rounded avatar chips. Data colours: mint · coral · navy · sand.

## Density block (add once to your CSS; the presets set `--density`)

Density changes sizes, not the recipes. Implement it as three token sets and
use the `ctl-*` / `row-*` variables in the recipes instead of fixed `h-8.5` when a
product needs a non-standard density.

```css
:root, .density-standard { --ctl-h: 34px; --ctl-h-sm: 28px; --ctl-h-lg: 40px; --row-h: 46px; --card-p: 1.25rem; --page-gap: 1.25rem; }
.density-compact              { --ctl-h: 30px; --ctl-h-sm: 24px; --ctl-h-lg: 36px; --row-h: 38px; --card-p: 1rem;    --page-gap: 1rem; }
.density-airy                 { --ctl-h: 40px; --ctl-h-sm: 32px; --ctl-h-lg: 48px; --row-h: 56px; --card-p: 1.75rem; --page-gap: 1.75rem; }
```

Tailwind usage: `h-(--ctl-h)`, `p-(--card-p)`, `gap-(--page-gap)`, `[&_td]:h-(--row-h)`.

## Deriving a new personality (when no preset fits)

1. **Name the feeling in three words** from the brief (e.g. "precise, calm, premium"). Write them down; every dial must agree with them.
2. **Type: keep Inter unless the brand says otherwise.** Inter at the house scale reads as "professional admin" immediately and pairs with every Arabic companion. If the brand needs a display face, pick one with the feeling and keep Inter for text. Load ≤ 2 families, ≤ 4 weights total. Check Arabic/Latin fallback if the product is bilingual (`Noto Sans Arabic`, `IBM Plex Sans Arabic`, `Cairo`, `Tajawal` pair well with the presets above).
3. **Primary from the brand, chroma ≥ 0.12** in OKLCH so it reads as a colour, not a grey. Tint the neutrals 0.005–0.015 chroma toward the same hue. Add at most one `--accent-strong` for a single highlight (delta badges, the one CTA on a marketing page).
4. **Pick shape and density from the users**, not from taste: keyboard-heavy operators → compact + small radius; occasional or anxious users (patients, customers) → airy + larger radius.
5. **Choose one signature element** and put it in the three places users see most: active nav item, KPI card, primary button. Nowhere else.
6. **Write the anti-list**: the three defaults you are explicitly avoiding for this product (e.g. "no blue primary, no rounded-2xl, no gradient text").
7. Persist it (below) and run the lint.

## Persist

Save the decision at `design/personality.md` in the product repo (or the
```md
# Personality — <Product>
feeling: precise, calm, premium
preset: theme-clinic (modified)
type: Manrope display / Manrope text · Arabic: IBM Plex Sans Arabic
primary: oklch(58% 0.13 195)  accent-strong: oklch(72% 0.17 60)
radius: 0.75rem   density: airy   surface: tinted-page   motion: micro
signature: 3px start-border on active nav + display-face KPI numerals
data colours: teal · amber · slate-blue · sage
avoid: blue primary · rounded-2xl everywhere · gradient text · icon-in-square
```

Every later screen reads this file first. Two products built by the same
agent on the same day must have different files here.
