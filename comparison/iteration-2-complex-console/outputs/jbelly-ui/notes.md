# Nutrio Ops Console — notes

**Personality** (jbelly-ui `theme-clinic`, four dials changed for a keyboard-heavy ops manager): density compact, radius 0.375rem, dark teal-navy sidebar on a teal-tinted page, Manrope display / IBM Plex Sans text (+ IBM Plex Sans Arabic for AR). Signature: 3px teal start-rail on active nav, KPI cards and selected rows. Primary `oklch(54% 0.13 192)`; data colours teal · slate-blue · amber · sage; status is never colour alone (icon + sign + text). Anti-list: no blue primary, no rounded-2xl/shadow-lg, no icon-in-a-square, no gradients.

**Build**: one file; Tailwind v4 browser build with all colour in one `<style type="text/tailwindcss">` token block; hand-drawn SVG charts (no chart CDN); vanilla JS; an sr-only data table per chart.

**Verified in headless Edge** (`chrome_debug.log` free of compile/JS errors after fixing one `@apply scroll-thin`): 1440 light, 1440 dark + RTL/Arabic, `#state=error&density=compact` full page, 1024 loading, 375 empty. Token lint: 0 raw palette classes.
