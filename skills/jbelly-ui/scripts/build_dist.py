#!/usr/bin/env python3
"""Build the delivery tiers from the skill sources (never hand-copied, so they cannot drift).

  dist/AGENTS.md            Tier 2: for tools that read a rules/knowledge file (Lovable, AGENTS.md readers). ~1.5K tokens.
  dist/jbelly-ui-prompt.md  Tier 3: one paste-in file for chat-only tools (no files, no scripts). < 8K tokens.

Usage: python scripts/build_dist.py            (from anywhere; writes <repo>/dist/)
Fails (exit 1) if a tier exceeds its size limit.
"""
import os, re, sys, time
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(SKILL))
DIST = os.path.join(REPO, "dist")
LIMITS = {"AGENTS.md": 2200, "jbelly-ui-prompt.md": 8000}  # tokens (~4 chars each)

def read(rel): return open(os.path.join(SKILL, rel), encoding="utf-8").read()
def section(md, heading):
    m = re.search(r"^## " + re.escape(heading) + r"\n([\s\S]*?)(?=^## |\Z)", md, re.M)
    return m.group(1).strip() if m else ""
def strip_links(md): return re.sub(r"`(?:scripts|references|assets)/[^`]+`", lambda m: m.group(0), md)

def build():
    quick = read("references/quick-card.md")
    anti = read("references/anti-patterns.md")
    pers = read("references/personalities.md")
    tokens = read("references/tokens.css")
    tokens_core = re.search(r":root \{[\s\S]*?\n\}\n\n[\s\S]*?\.dark \{[\s\S]*?\n\}", tokens).group(0)
    presets = re.findall(r"^### \d\. `(theme-[a-z]+)` — ([^\n]+)\n\n```css\n([\s\S]*?)```", pers, re.M)
    presets_md = "\n".join(f"- **{n}** ({d}):\n```css\n{c.strip()}\n```" for n, d, c in presets[:3])
    rules = section(quick, "Rules that decide the grade")
    manual = """## Without tools (manual checklist)
If you cannot run scripts, apply by hand before you finish:
1. Search your markup for raw palette classes (`bg-blue-500`, `text-gray-600`, hex colours) — replace with roles.
2. Count primary buttons outside the nav: exactly one per view.
3. Every icon-only button has `aria-label`; a skip link exists when there is a nav; one `<h1>`.
4. No purple/indigo gradients, gradient text, Sparkles/Zap icons, emoji icons, `transition: all`, filler words (Elevate, Seamless, Unleash).
5. Contrast: text on background and white on primary ≥ 4.5:1 (check with any contrast tool).
6. Four states per async region: loading skeleton, empty with an action, error with retry, success.
7. Open the page once in light, dark and RTL before calling it done."""

    agents = f"""# jbelly-ui — UI rules for this project (generated from the jbelly-ui skill; do not edit by hand)

You are building or changing a web UI. Follow these rules exactly; values are not suggestions.

## Before any code: the design read (4 fields)
`kind` (dashboard / settings / landing / …) · `audience` (who, how often, keyboard or touch) · `vibe` (three words) · `system` (preset + dials changed). Keep it in `design/personality.md`. Never ship the default look.

## Tokens (roles, never raw palette)
{section(quick, "Tokens (roles, never raw palette)")}

## Sizes
{section(quick, "Sizes")}

## Rules that decide the grade
{rules}

## Anti-patterns (never)
{chr(10).join(l for l in anti.splitlines() if l.startswith("- ⚙"))}

{manual}
"""
    prompt = f"""# jbelly-ui — paste-in UI system for chat tools (generated; self-contained)

Use this whole message as instructions for any UI you produce in this conversation.
Output complete HTML with Tailwind v4 (`<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>`) and Lucide icons unless the user names another stack; then translate the class strings to that stack.

## 1. Design read (first output, four fields)
`kind` · `audience` (who, how often, keyboard or touch) · `vibe` (three words) · `system` (preset + dials changed). State it, then build. Never ship the default look: pick a preset below and change at least two dials (palette, shape, density, signature element).

## 2. Tokens — paste this CSS first (it is the whole colour system; components use roles only)
```css
{tokens_core}
```
Tailwind mapping: `@theme inline {{ --color-background: var(--background); --color-foreground: var(--foreground); --color-card: var(--card); --color-primary: var(--primary); --color-primary-foreground: var(--primary-foreground); --color-secondary: var(--secondary); --color-secondary-foreground: var(--secondary-foreground); --color-muted: var(--muted); --color-muted-foreground: var(--muted-foreground); --color-accent: var(--accent); --color-accent-foreground: var(--accent-foreground); --color-mono: var(--mono); --color-mono-foreground: var(--mono-foreground); --color-destructive: var(--destructive); --color-success: var(--success); --color-warning: var(--warning); --color-info: var(--info); --color-border: var(--border); --color-input: var(--input); --color-ring: var(--ring); --radius-xl: calc(var(--radius) + 4px); --radius-lg: var(--radius); --radius-md: calc(var(--radius) - 2px); --radius-sm: calc(var(--radius) - 4px); }} @theme {{ --text-2sm: 0.8125rem; --text-2xs: 0.6875rem; }} @custom-variant dark (&:where(.dark, .dark *));`

## 3. Personality presets (append one after the tokens, then change two dials)
{presets_md}

## 4. The system in one screen
{section(quick, "Tokens (roles, never raw palette)")}

{section(quick, "Sizes")}

## 5. Recipes (exact class strings)
{section(quick, "Recipes (class strings)")}

## 6. Charts, i18n, weight
{section(quick, "Charts, i18n, weight")}

## 7. Decision tables
{section(quick, "Decision tables (instead of prose)")}

## 8. Rules that decide the grade
{rules}

## 9. Anti-patterns — never do these
{chr(10).join(l for l in anti.splitlines() if l.startswith("- "))}

{manual}
"""
    os.makedirs(DIST, exist_ok=True)
    ok = True
    for name, text in (("AGENTS.md", agents), ("jbelly-ui-prompt.md", prompt)):
        toks = len(text) // 4
        open(os.path.join(DIST, name), "w", encoding="utf-8", newline="\n").write(text)
        status = "OK" if toks <= LIMITS[name] else "OVER LIMIT"
        ok &= toks <= LIMITS[name]
        print(f"dist/{name}: ~{toks:,} tokens (limit {LIMITS[name]:,}) {status}")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(build())
