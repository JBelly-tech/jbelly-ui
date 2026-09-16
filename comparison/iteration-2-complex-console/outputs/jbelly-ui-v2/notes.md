# Nutrio Ops Console — notes

**Personality:** `theme-clinic` modified — Manrope display / Inter text, Noto Sans Arabic for AR; teal primary, radius 0.5rem (was 0.75), density compact (was airy, keyboard-heavy managers); signature: 3px start-border on active nav + monospaced meta (times, IDs). Data colours teal · slate-blue · amber · sage.

**From the generator (`build-screen.py` + spec.json):** shell, nav, toolbar, 6 KPIs with sparklines, 3-series area chart, donut, table skeleton, ⌘K palette, toasts, dark/RTL/i18n, ApexCharts theme.

**Added by patch scripts (data still from spec.json):** branch switcher, notifications drawer, lang/density toggles, compare switch, custom range, clickable legend, capacity bars, heatmap, adherence list, full table engine (sort/search/chips/columns/pagination/error state/bulk + confirm modal), kanban, grouped activity, tasks, tabbed patient drawer with measurement chart, focus trap, hash presets.

**verify-page.ps1:** dark, rtl, error, loading+standard variants all OK, no console errors, token lint clean — PASS. Kept ApexCharts (skill's charts.md) despite the brief's "no other CDN".
