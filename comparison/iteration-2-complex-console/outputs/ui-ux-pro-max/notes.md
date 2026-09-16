# Nutrio Ops Console — notes

**Design.** Used the verified `data-dense-dashboard` style from ui-ux-pro-max and rejected its Neumorphism suggestion (high a11y risk for a keyboard-heavy console). Palette from the healthcare design-system result: calm teal primary (#0F766E light / #14B8A6 dark) plus health green, semantic success/warning/danger/info, five programme hues with distinct line dashes so colour is never the only signal. Tokens are CSS variables mapped into Tailwind v4 via `@theme inline`; theme, density and direction only swap variables. Component CSS lives in `@layer components` so utilities win.

**Fonts.** Fira Sans (UI) + Fira Code (tabular figures) — the "Dashboard Data" pairing — with Noto Sans Arabic for RTL.

**Verified.** Headless Edge at 1440×1000/2400 and 900px: light, `#dark=1&dir=rtl&density=compact`, `#state=loading|empty|error`, patient drawer, Ctrl-K palette, notifications, bulk-cancel confirm. Console: no JS errors, no "unknown utility class", all Lucide icons resolved; Node syntax check passed. Extra presets: `#open=patient|notifs|palette|bulk|appt`.
