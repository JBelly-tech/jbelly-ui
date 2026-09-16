"""Visual analytics from a screenshot (Pillow). Class D — deterministic.

Usage: python visual_metrics.py <name> <png> [<png> ...]  -> JSON list
Metrics:
  - distinct_hues: number of hue buckets (of 36) with > 0.15% of chromatic pixels — palette discipline
  - chromatic_ratio: share of pixels with saturation > 0.25 — how much colour vs neutral chrome
  - ink_ratio: share of pixels darker than the page background by > 12% luminance — text/line density
  - mean_luminance: overall brightness (0..1)
  - accent_share: share of chromatic pixels belonging to the dominant hue bucket — "one primary" discipline
  - card_edges: number of long horizontal hairline runs — a proxy for card/section count
"""
import sys, json, colorsys
from collections import Counter
from PIL import Image

def analyse(name, path):
    im = Image.open(path).convert("RGB")
    im.thumbnail((720, 720))
    w, h = im.size
    px = list(im.getdata())
    n = len(px)
    # background = most common colour
    bg = Counter(px).most_common(1)[0][0]
    bg_l = (0.2126 * bg[0] + 0.7152 * bg[1] + 0.0722 * bg[2]) / 255
    hues = Counter(); chromatic = 0; ink = 0; lum_sum = 0.0
    for r, g, b in px:
        l = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
        lum_sum += l
        if abs(l - bg_l) > 0.12: ink += 1
        hh, ss, vv = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if ss > 0.25 and vv > 0.2:
            chromatic += 1; hues[int(hh * 36) % 36] += 1
    distinct = sum(1 for k, v in hues.items() if v > 0.0015 * max(1, chromatic))
    dominant = hues.most_common(1)[0][1] / chromatic if chromatic else 0
    # hairline detection: rows where many consecutive pixels differ from bg slightly
    edges = 0
    for y in range(h):
        run = 0; best = 0
        for x in range(w):
            r, g, b = im.getpixel((x, y))
            d = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
            if 12 < d < 90: run += 1; best = max(best, run)
            else: run = 0
        if best > w * 0.25: edges += 1
    return {
        "name": name, "file": path, "size": [w, h],
        "distinct_hues": distinct,
        "chromatic_ratio": round(chromatic / n, 4),
        "ink_ratio": round(ink / n, 4),
        "mean_luminance": round(lum_sum / n, 3),
        "accent_share": round(dominant, 3),
        "hairline_rows": edges,
    }

if __name__ == "__main__":
    name = sys.argv[1]
    print(json.dumps([analyse(name if len(sys.argv) == 3 else f"{name}:{p.split('/')[-1].split(chr(92))[-1]}", p) for p in sys.argv[2:]], indent=2))
