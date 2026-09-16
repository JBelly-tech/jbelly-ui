# Comparison — jbelly-ui vs a catalogue skill vs no skill vs a commercial template

Everything about the evaluation lives here: the briefs, the raw dashboards each
run produced, screenshots in fixed configurations, deterministic metrics, and
the reports. Open any `dashboard.html` in a browser — they are real, interactive
pages; the PNGs are fixed-size captures of those same pages for side-by-side
viewing.

| Folder | What |
|--------|------|
| `iteration-1-simple-dashboard/` | First eval (single-branch dashboard). `outputs/<maker>/dashboard-<maker>.html` (`jbelly-ui`, `ui-ux-pro-max`, `no-skill`), `notes.md`, `grading.json`, `timing.json`; screenshots; `review-iteration-1.html` (side-by-side viewer) |
| `iteration-2-complex-console/` | Second eval (complex operations console: 6 KPIs, 3 charts, heatmap, full table, kanban, drawer, ⌘K, notifications). `brief.md`, `outputs/<maker>/dashboard-<maker>.html`, `shots/<maker>-<config>.png`, `metrics/`, `report-complex.html` |
| `demo-shots/` | The skill's own demo page (`../skills/jbelly-ui/assets/app-shell.html`) in five personality / state combinations |
| `reference-template/` | Screenshots and metrics of a purchased commercial admin template rendered locally, used only as a quality yardstick. **Git-ignored** — those images are the template vendor's, not ours, and must not be published |

Every dashboard is named after the tool that produced it: `dashboard-jbelly-ui.html`,
`dashboard-ui-ux-pro-max.html`, `dashboard-no-skill.html`; the commercial yardstick is `reference-template`.

| Folder | What |
|--------|------|
| `tools/` | Deterministic scripts: `grade.py` (assertion grader), `dom_metrics.py` (source/DOM metrics), `visual_metrics.py` (screenshot analytics), `build_report.py` (HTML report builder), `screenshot.ps1` (headless Edge capture) |

## How the captures were made

Headless Edge, `--window-size` 1440×1000 (also 1024×900 and 500×900),
`--virtual-time-budget=25000`, `--hide-scrollbars`. Dark / RTL / state variants
are selected through URL hash parameters the pages support
(`#dark=1`, `#dir=rtl`, `#state=loading|empty|error`, `#density=compact`).

## How to re-run

```powershell
# capture
powershell -File tools/screenshot.ps1 -Url "file:///D:/path/dashboard.html#dark=1" -Out shots/x.png -Width 1440 -Height 1000
# metrics
python tools/dom_metrics.py <name> <dashboard.html> [<rendered-dom.html>]
python tools/visual_metrics.py <name> <shot.png> [<shot2.png> ...]
python tools/grade.py <iteration-dir>
python tools/build_report.py <report_data.json> <report.html>
```
