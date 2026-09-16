# Brief — "Nutrio Ops Console" (complex operations dashboard)

Build ONE self-contained HTML file: Tailwind v4 via `<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>`,
icons via `<script src="https://unpkg.com/lucide@0.469.0/dist/umd/lucide.min.js"></script>`, Google Fonts allowed, no build step,
no other CDN. Vanilla JS only. Realistic Jordanian data (Arabic-Jordanian names, JOD, Amman branches: Abdoun, Sweifieh, Khalda).

Product: the operations console of a 3-branch nutrition clinic chain in Amman. Users: clinic manager (all day, keyboard-heavy).

## Must include (all on one page)

1. **App shell**: collapsible sidebar (3 groups, one nested group with 3 children, one active item, badge counts),
   header with breadcrumb, global search opening a ⌘K command palette (grouped results, arrow keys, Enter, Esc),
   notifications drawer (tabs All / Inbox / Team, unread markers, footer actions), user menu, **branch switcher**,
   dark/light toggle, EN/AR language toggle that flips `dir` to RTL, density toggle (compact/standard).
2. **Toolbar**: title + subtitle with "Updated N min ago", date-range control with presets (Today, 7d, 30d, Quarter, Custom),
   branch filter, "Compare to previous period" switch, Export (secondary), ONE primary action.
3. **Row 1**: six KPI cards, each with value, label, delta vs previous period (icon + sign + colour + text), and a sparkline.
4. **Row 2**: multi-series chart (12 weeks × 3 series: consultations, follow-ups, no-shows) with clickable legend that toggles series;
   a donut "patients by programme" with the total in the centre; horizontal bars "capacity by dietitian" (6 dietitians, % booked).
5. **Row 3**: appointments heatmap (7 days × 12 hours, colour scale with legend, hover tooltip); progress list "plan adherence by programme" (5 rows).
6. **Row 4**: data table with ≥ 12 appointment rows: sortable columns (click header, 3 states), search, status filter chips with counts,
   column chooser, density toggle, checkbox selection with a bulk-action bar (count, Send reminder, Reschedule, Cancel → confirm modal),
   hover-revealed row actions (keyboard reachable), pagination with page-size select and "1–10 of N", sticky header inside the card,
   and a state switch Data / Loading (skeleton) / Empty / Error (with Retry).
7. **Row 5**: "Today's queue" kanban with 3 columns (Waiting / In session / Done, ≥ 3 cards each, drag handles, keyboard alternative described in a tooltip);
   activity feed grouped by day; tasks list with checkboxes and due dates.
8. **Patient drawer**: clicking a table row opens a side drawer with tabs (Overview, Measurements — small line chart, Notes — textarea + Save),
   focus moves into it, Esc closes, focus returns.
9. **Feedback**: toasts (max 3, Undo on the bulk action), confirm modal for the destructive bulk action.
10. **Preferences persist** in localStorage: theme, dir, density, sidebar collapsed.
11. **URL presets for screenshots** (read `location.hash` as query params): `#dark=1`, `#dir=rtl`, `#state=loading|empty|error`, `#density=compact`.
12. Responsive: sidebar becomes a drawer below 1024px; KPI grid 3-up at 1024, 2-up at 640; table scrolls horizontally inside its card.

## Quality bar

- Accessibility: aria-labels on icon-only buttons, visible focus rings, skip link, `sr-only` data table for each chart, colour never the only status signal.
- No emoji icons. No copied commercial template code.
- **Before finishing, render the page in headless Edge and look at it**:
  `& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --hide-scrollbars --window-size=1440,1000 --virtual-time-budget=20000 "--user-data-dir=$env:TEMP\edge-probe-<random>" --screenshot=<png> <file-url>`
  and check the Edge console log (`--enable-logging --log-level=0`, then `chrome_debug.log` in the profile dir) for any "Cannot apply unknown utility class" or JS errors. An unstyled screenshot means the stylesheet failed to compile.

## Deliverables

- `dashboard.html` (the page) and `notes.md` (≤ 150 words: the design decisions, fonts, palette, and what you verified).
