# Nutrio dashboard — skill notes

**Recommended (ui-ux-pro-max):** `--design-system` returned Neumorphism (a11y risk: high, dark: conditional), Healthcare palette (cyan #0891B2 + green #059669), Atkinson Hyperlegible. Supplementary searches: style *Data-Dense Dashboard* (a11y risk: low, light+dark); color *Calorie & Nutrition Counter* (green #059669 + orange #EA580C); typography *Noto Sans Arabic* for RTL; chart *Trend Over Time* → line/area, distinct line styles, table fallback.

**Applied:** Data-Dense Dashboard style (rejected Neumorphism on the a11y/dark-mode flags). Green/orange nutrition palette as semantic tokens with a dark set. Atkinson Hyperlegible Next + Noto Sans Arabic. SVG area/line chart (solid vs dashed, weekend bands, tooltip, sr-only table). Logical CSS properties for RTL; class-based dark mode; localStorage persistence.
