# Charts — the look buyers of top admin templates expect, from tokens

Use **ApexCharts** (MIT) with the house theme below. The scaffold
(`assets/app-shell.html`) already contains it: `apexBase()`, `mountCharts()`,
and a `MutationObserver` that re-renders when `dark`, the personality class or
`dir` changes. Copy that block; do not hand-draw SVG charts for dashboards
(they read as "unfinished" next to a smooth area chart), and do not use any
chart library with a per-project licence.

```html
<script src="https://cdn.jsdelivr.net/npm/apexcharts@4.7.0/dist/apexcharts.min.js"></script>
```

## Theme (all values from tokens)

```js
const cssVar = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
function apexBase() { return {
  chart: { fontFamily: cssVar('--font-sans') || 'Inter, sans-serif', foreColor: cssVar('--muted-foreground'),
           toolbar: { show: false }, zoom: { enabled: false }, background: 'transparent', parentHeightOffset: 0,
           animations: { enabled: !matchMedia('(prefers-reduced-motion: reduce)').matches, speed: 600 } },
  colors: [cssVar('--primary'), cssVar('--chart-2') || cssVar('--info'), cssVar('--chart-3') || cssVar('--success'),
           cssVar('--chart-4') || cssVar('--warning'), cssVar('--muted-foreground')],
  grid: { borderColor: cssVar('--border'), strokeDashArray: 3, padding: { left: 8, right: 8, top: -10 }, xaxis: { lines: { show: false } } },
  stroke: { curve: 'smooth', width: 2.5, lineCap: 'round' },
  dataLabels: { enabled: false }, legend: { show: false },
  tooltip: { theme: document.documentElement.classList.contains('dark') ? 'dark' : 'light', style: { fontSize: '12px' } },
  xaxis: { axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { fontSize: '11px' } }, tooltip: { enabled: false } },
  yaxis: { labels: { style: { fontSize: '11px' } } },
  states: { hover: { filter: { type: 'none' } }, active: { filter: { type: 'none' } } },
}; }
```

Give every chart an explicit pixel `height` (or `'100%'` inside a container
with a real height such as `h-full min-h-60`); percentage heights inside
`h-10` boxes overflow. Put the legend in the card header (dot + label,
`text-2sm text-secondary-foreground`) and keep Apex's own legend off.

## Recipes

| Chart | Options on top of `apexBase()` | Where |
|-------|-------------------------------|-------|
| **Area / line (trend)** | `type:'area'`, `fill:{type:'gradient',gradient:{opacityFrom:.28,opacityTo:.02,stops:[0,90,100]}}`, `markers:{size:0,hover:{size:5}}`, `yaxis:{min:0,tickAmount:4}` | main KPI trend, 2–3 series max |
| **Sparkline** | `type:'area'`, `chart.sparkline:{enabled:true}`, `height:40`, `stroke.width:2`, `tooltip:{enabled:false}` | inside KPI cards, bottom, `-mx-1 -mb-2` |
| **Bar (columns)** | `type:'bar'`, `plotOptions:{bar:{columnWidth:'38%',borderRadius:4,borderRadiusApplication:'end'}}`, second series `colors[4]` at 35% opacity | weekly volumes, category comparison |
| **Horizontal bars** | `type:'bar'`, `plotOptions:{bar:{horizontal:true,barHeight:'55%',borderRadius:3}}`, `dataLabels.enabled:true` (values at end) | capacity, rankings |
| **Donut** | `type:'donut'`, `stroke:{width:3,colors:[cssVar('--card')]}`, `plotOptions.pie.donut.size:'74%'`, centre `total` label (`fontSize:'24px'`, weight 600, `--mono`) | share by category; legend list under it with value + % |
| **Radial (goal)** | `type:'radialBar'`, `plotOptions.radialBar:{hollow:{size:'62%'},track:{background:cssVar('--secondary')},dataLabels:{value:{fontSize:'22px',fontWeight:600}}}` | single KPI vs target |
| **Heatmap** | `type:'heatmap'`, `plotOptions.heatmap:{radius:4,colorScale:{ranges:[…5 steps from primary/10 to primary]}}`, `dataLabels.enabled:true` at 11px | bookings per hour × day |
| **Stacked bar** | `type:'bar'`, `chart.stacked:true`, `plotOptions.bar.columnWidth:'40%'` | composition over time |

## Rules

- Series ≤ 5; the 6th becomes "Other". Colours in order: primary, chart-2, chart-3, chart-4, muted.
- **`--chart-*` are series colours, not the state fills.** `--success` and `--warning` are made to carry
  white text, which makes them far too light to be seen as a line: on a white card they measure 2.08:1
  and 1.44:1. A series is a graphical object the reader needs in order to read the chart, so it clears
  3:1 against the card — which is what `--chart-3` and `--chart-4` hold, in each mode. Reach for
  `var(--chart-N)`, never `var(--success)`, when you are drawing.
- Never colour alone: second series dashed (`stroke.dashArray:[0,4]`) or a marker shape; heatmap prints its values.
- Y axis starts at 0 for bars; thousands separators via `yaxis.labels.formatter`.
- One `sr-only` `<table>` per chart with the key points, and `role="img" aria-label="<the takeaway>"` on the container.
- Dark mode: re-render on `html` class change (the observer in the scaffold); tooltips follow the theme.
- Mobile: hide the y axis labels below `md`, keep the tooltip; never squash a 12-point series below 320px wide — show "Better on a larger screen" instead.
