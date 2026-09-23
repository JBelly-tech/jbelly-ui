# Stacks — the same recipe in plain CSS, Tailwind and React

The system is tokens (CSS variables) plus recipes (utility strings). Pick the
column of the project's stack; never force a stack. `assets/tokens.json` is
the same token set in DTCG format for design tools and token pipelines.

| Piece | Plain HTML + CSS | Tailwind v4 | React (any UI lib) |
|---|---|---|---|
| Install tokens | `<link rel="stylesheet" href="tokens.css">` first | `@import "tailwindcss"; @import "./tokens.css";` | same as the stack's CSS entry; or feed `tokens.json` to Style Dictionary |
| Use a colour | `background: var(--primary); color: var(--primary-foreground)` | `bg-primary text-primary-foreground` | `className="bg-primary text-primary-foreground"` or `style={{ background: "var(--primary)" }}` |
| Button (md, primary) | `.btn { display:inline-flex; align-items:center; gap:6px; height:34px; padding:0 12px; font:500 13px/1.3 var(--font-sans); border-radius:calc(var(--radius) - 2px); box-shadow:var(--shadow-xs) } .btn-primary { background:var(--primary); color:var(--primary-foreground) }` | `inline-flex items-center gap-1.5 h-8.5 px-3 text-2sm font-medium rounded-md shadow-xs bg-primary text-primary-foreground hover:bg-primary/90` | `<Button className={btn("primary")}>` where `btn()` returns the Tailwind string; with shadcn/ui: map `--primary` etc. and keep its `Button` |
| Input | `.input { height:34px; padding:0 12px; font-size:13px; border:1px solid var(--input); border-radius:calc(var(--radius) - 2px); background:var(--background) } .input:focus-visible { outline:none; border-color:var(--ring); box-shadow:0 0 0 2px color-mix(in oklab, var(--ring) 40%, transparent) }` | `h-8.5 px-3 text-2sm rounded-md border border-input bg-background focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/40` | `<input className={input()} />`; react-hook-form + zod for validation, messages in the Field recipe |
| Card | `.card { border:1px solid var(--border); background:var(--card); border-radius:calc(var(--radius) + 4px); box-shadow:var(--shadow-xs) }` | `rounded-xl border border-border bg-card shadow-xs` | `<Card>` from any lib, restyled with the same classes |
| Badge (light success) | `.badge { display:inline-flex; height:24px; padding:0 7px; font-size:12px; font-weight:500; border-radius:calc(var(--radius) - 2px); background:color-mix(in oklab, var(--success) 15%, transparent); color:var(--success) }` | `inline-flex h-6 px-[0.45rem] text-xs font-medium rounded-md bg-success/15 text-success-accent` | same string |
| Table | `table { width:100%; font-size:14px } th { height:44px; padding:0 16px; text-align:start; font:400 12px var(--font-sans); color:var(--secondary-foreground); border-bottom:1px solid var(--border) } td { padding:0 16px; height:46px; border-bottom:1px solid var(--border) }` | `w-full text-sm` · th `h-11 px-4 text-start text-xs font-normal text-secondary-foreground border-b` · td `px-4 h-11.5 border-b border-border` | TanStack Table (headless) rendering the same markup |
| Dark mode | `html.dark { … }` block in tokens.css; toggle the class, persist in `localStorage` | `@custom-variant dark (&:where(.dark, .dark *))` in tokens.css; `dark:` utilities rarely needed because roles swap | same class toggle; `next-themes` or a 6-line hook |
| RTL | `dir="rtl"` on `<html>`; logical properties (`padding-inline-start`, `inset-inline-end`) | `ps- pe- ms- me- start- end-` utilities; `rtl:rotate-180` on chevrons | same; `dir` from the i18n library |
| Charts | ApexCharts with `apexBase()` from `references/charts.md` | same | `react-apexcharts` with the same options object |
| Icons | Lucide static SVG sprite or `<i data-lucide>` + `lucide.createIcons()` | same | `lucide-react` |

## Notes

- Tailwind v3 projects: copy the `:root` / `.dark` blocks from `tokens.css`
  and map them in `tailwind.config.js` under `theme.extend.colors`
  (`primary: "var(--primary)"`, …); the recipes then work unchanged except
  `h-8.5` (use `h-[34px]`) and `rounded-*` names (map the radius scale).
- Component libraries (shadcn/ui, Radix Themes, Mantine, Chakra, MUI): map the
  library's theme variables to the same tokens; keep their components, apply
  the house sizes (28/34/40px controls, 13px UI text) through the theme, not
  per component.
- Design tools: import `assets/tokens.json` with a DTCG-aware plugin so Figma
  and the code share one set of values.
