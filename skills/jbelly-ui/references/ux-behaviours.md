# UX behaviours — what makes an admin UI feel professional

Looks are the tokens and recipes. *Feel* is the behaviour below. This is the
part users mean when they say a template "feels expensive": every state is
handled, nothing jumps, keyboard works, data screens respect expert users.
Implement all of it; none of it is optional polish.

Contents: Navigation · Loading & feedback · Tables & data · Forms · Overlays ·
Keyboard · Dashboards · Responsive · Theme & preferences · Copy · Delivery check

---

## Navigation

- **One active item, always.** The sidebar marks exactly one link (`.active`); parent groups of the active child are `.open`. Deep links restore this state on load.
- **Breadcrumb or subtitle under every page title** so users know where they are without the sidebar (mobile hides it).
- **Sidebar state persists** (`localStorage`: collapsed / open, and which groups are open). Collapsed sidebar peeks on hover and shows tooltips for icons.
- **Back always works.** Drawers and modals push nothing to history; tabs and filters *do* update the URL query so a refreshed or shared link shows the same view.
- **Mega menu / header nav**: opens on hover on desktop after 100ms, on tap on touch; closes on `Esc` and outside click; never traps focus.
- **Search / command palette** on `Ctrl/⌘+K` from any screen: recent items, grouped results, arrow-key navigation, `Enter` opens, `Esc` closes.

## Loading & feedback

- **Skeletons, not spinners,** for anything that takes > 300ms and has a known shape (cards, rows, charts). Reserve the final height so nothing shifts (CLS < 0.1).
- **Spinners only inside the control that triggered the work** (button shows spinner + disabled, keeps its width).
- **Optimistic updates** for toggles, favourites, reordering; revert with a toast on failure.
- **Toasts** for outcomes of actions that happened elsewhere or asynchronously (saved, exported, invited). 4s auto-dismiss, pause on hover, stack from the bottom-end corner, max 3, an **Undo** action on destructive-but-reversible operations (archive, remove from list).
- **Inline alerts** for outcomes tied to the current view (validation summary, permission notice, partial failure). Never both a toast and an inline alert for the same event.
- **Empty states carry the next action** (primary button or link) and, on first run, a 3-step guide. A filtered-to-nothing table says "No results for *x*" with a "Clear filters" link, not the first-run illustration.
- **Errors say what happened and what to do**, in one sentence each: "Couldn't save the plan. Check your connection and try again." + Retry.
- **Confirm only destructive or irreversible actions**; the confirm modal names the object ("Delete *Ahmad's plan*?") and the destructive button is labelled with the verb, never "OK". Typing the name to confirm is for bulk or org-level deletes only.

## Tables & data

- **Sticky header** inside scrolling cards; **sticky first column** on wide tables at `lg-`.
- **Row hover** reveals up to 3 row actions on the end side; a ⋮ menu holds the rest. Actions exist in the DOM always (keyboard/screen-reader reachable), visibility is the only thing hover changes.
- **Selection**: obvious checkbox column; header checkbox = page; "Select all 240" link when a page is selected; **bulk-action bar** replaces the toolbar while ≥ 1 row is selected and shows the count.
- **Sort** by clicking the header (three states: asc → desc → none), one sorted column at a time, indicator visible. Numbers `text-end tabular-nums`; dates right-aligned or in one consistent format with a full timestamp in a tooltip.
- **Filters**: 1–3 primary filters visible (search + status + date), the rest behind a "Filters" button with a count badge; active filters shown as removable chips; **"Clear all"**. Filters and sort live in the URL.
- **Saved views** for any list expert users revisit (name + filters + sort + columns). Default views: All · Mine · Needs attention.
- **Column chooser + density toggle** (compact / standard) on data-heavy tables; persist per user.
- **Pagination** with page size (10 / 25 / 50 / 100) and "1–25 of 1,204"; infinite scroll only for feeds. Keep the scroll position and selection on page change when possible.
- **Inline edit** for one-field tweaks (name, quantity): click-to-edit with `Enter` save / `Esc` cancel; otherwise open a Drawer.
- **Drawer for details, page for full records**: clicking a row opens a side drawer (context kept) with the key fields and a "Open full page" link.
- **Export** (CSV/XLSX) respects current filters and says so ("Export 312 filtered rows").
- **Truncate with tooltip**, never clip silently; IDs and emails `overflow-wrap:anywhere` inside a shrinkable cell.

## Forms

- **Labels above fields**, always visible (placeholders are examples, not labels). Required marked with `*`; optional forms mark "(optional)" instead when most fields are required.
- **Validate on blur, re-validate on input** after the first error; error text under the field + `aria-invalid` + `aria-describedby`; on submit, focus the first invalid field and show a linked summary if > 2 errors.
- **Sticky action bar** on long forms (`sticky bottom-0 bg-background/90 backdrop-blur border-t`) with Cancel + Save; Save disabled until dirty; **unsaved-changes guard** on navigation.
- **Autosave** for settings and drafts, with a quiet "Saved · just now" status, not a toast per keystroke.
- **Smart defaults**: prefill from the record, the last used value, or the org default; date pickers default to today; selects with ≤ 5 options become radio/segmented controls.
- **Progressive disclosure**: advanced options collapsed under "Advanced" with a summary of what's set; wizards for ≥ 3 dependent steps with a stepper and per-step validation.
- **Password managers and paste allowed**; OTP inputs auto-advance, accept a pasted 6-digit code, and submit on the last digit.
- **Destructive settings** live in a separate "Danger zone" card at the bottom.

## Overlays

- **Modal**: focus moves in on open, returns to the trigger on close; `Esc` and overlay click close (not while a form is dirty — ask first); body scroll locked; max one modal at a time (a confirm may stack over a form modal).
- **Drawer**: same rules; width 450px default; content scrolls, header/footer fixed; supports a "next / previous record" pair in the header for lists.
- **Dropdown / popover**: opens below-start, flips when out of viewport, `Esc` closes, arrow keys move, typeahead selects, closes on selection unless multi-select.
- **Tooltip**: on hover *and* focus, 300ms delay, plain text only, never the sole carrier of a required label.

## Keyboard

- Tab order = visual order; visible focus ring (`ring-2 ring-ring ring-offset-2`) on every control; skip-link to main content.
- **Global**: `Ctrl/⌘+K` search · `?` shortcut sheet · `Esc` closes the topmost overlay.
- **Lists**: `↑/↓` move, `Enter` open, `Space` select, `Shift+↑/↓` range, `Ctrl/⌘+A` select page, `Delete` = destructive action (with confirm).
- **Forms**: `Ctrl/⌘+Enter` submits, `Esc` cancels inline edits.
- Show shortcuts in menus with the Kbd recipe; never override browser/OS shortcuts.

## Dashboards

- **Top-left holds the most important number**; F-pattern scanning means the first row and the start column get the KPIs users decide with.
- **≤ 7 focal elements above the fold**; more than that becomes a wall of data.
- **Every KPI has a comparison** (Δ vs previous period, with icon + sign + colour) and the period is visible in the toolbar; comparison period is selectable.
- **Page-level date range + filters** in the toolbar apply to everything; a module-level filter (period select in a card header) overrides only that card and shows it.
- **Charts**: title top-start, legend bottom or inline, tooltips on hover/focus, y-axis starts at zero for bars, thousands separators, tabular labels, ≤ 5 series, colour-blind safe (vary line style / add texture when it matters), "better on a larger screen" note instead of squashing a chart on mobile.
- **Consistent module anatomy**: same title / toolbar / legend positions across cards so eyes don't hunt.
- **Drill-down**: KPI card and chart segments are links to the filtered list.
- **Customisable when it matters**: hide/show cards, reorder, or "build your dashboard" for expert users; persist per user.
- **Refresh semantics**: show "Updated 2 min ago" and a refresh button when data isn't live.

## Responsive

- Shell switches at `lg`; below it: header 60px, hamburger opens the sidebar drawer, toolbar actions collapse into a ⋮ menu, KPI grid goes 2-up then 1-up, tables become card lists or horizontal-scroll with sticky first column, drawers go full-width.
- Touch targets ≥ 44px on touch devices (`min-h-11` on mobile menus and row actions), `touch-action: manipulation`, no hover-only affordances.
- Mobile shows the top section of a dashboard; ask which cards matter on the go and hide the rest behind a "More" section.
- Use `min-h-dvh`, respect safe areas, never disable zoom.

## Theme & preferences

- Light / dark / system toggle in the user menu; class on `<html>`, persisted; charts and images have dark variants or reduced opacity.
- **RTL** via `dir="rtl"` only; mirror directional icons; test with Arabic text lengths (30% longer than English on average).
- Density toggle for data-heavy products; sidebar collapse; per-user saved views, column sets and dashboard layout — all persisted, all resettable from Settings → Appearance.
- Language switch never reloads to the home page; it keeps the current route.

## Copy

- Sentence case for titles and buttons; verbs on buttons ("Invite member", "Export CSV"), never "Submit"/"OK".
- No "Elevate / Seamless / Powerful" marketing filler inside the app; empty states and errors are plain and specific.
- Numbers: thousands separators, one decimal for percentages, currency with symbol first (locale-aware), relative times under 24h ("3 h ago") with the absolute time in a tooltip.

## Delivery check (behaviour)

- [ ] Every async region has loading, empty, error and success states.
- [ ] Every list: sort, filter chips, pagination text, bulk bar, row actions reachable by keyboard.
- [ ] Every form: labels, inline errors, focus-to-first-error, dirty guard, one primary button.
- [ ] Every overlay: focus trap, `Esc`, focus return, scroll lock.
- [ ] Sidebar: one active item, state persisted, drawer on mobile.
- [ ] Toolbar filters and tabs reflected in the URL.
- [ ] Light + dark + RTL + 375px checked.
