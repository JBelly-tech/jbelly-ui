#!/usr/bin/env python3
"""Build the delivery tiers from the skill sources (never hand-copied, so they cannot drift).

  dist/AGENTS.md            Tier 2: for tools that read a rules/knowledge file (Lovable, AGENTS.md readers). ~1.5K tokens.
  dist/jbelly-ui-prompt.md  Tier 3: one paste-in file for chat-only tools (no files, no scripts). < 8K tokens.

Usage: python scripts/build_dist.py            (from anywhere; writes <repo>/dist/)
Fails (exit 1) if a tier exceeds its size limit, a source section is missing or empty, a colour
role in references/tokens.css has no Tailwind mapping, or the paste-in tier still points at a
repo path.
"""
import os, re, sys, time
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(SKILL))
DIST = os.path.join(REPO, "dist")
LIMITS = {"AGENTS.md": 2200, "jbelly-ui-prompt.md": 8000}  # tokens (~4 chars each)

def read(rel): return open(os.path.join(SKILL, rel), encoding="utf-8").read()

def need(value, what):
    # An empty extraction reads exactly like an empty section in the output, so it has to stop the
    # build: returning "" shipped a tier with a blank heading and still printed OK.
    if not value: sys.exit("build_dist: nothing extracted for " + what + " - the source changed shape")
    return value

def section(md, heading, src="references/quick-card.md"):
    m = re.search(r"^## " + re.escape(heading) + r"\n([\s\S]*?)(?=^## |\Z)", md, re.M)
    return need(m.group(1).strip() if m else "", "section '## " + heading + "' of " + src)

def anti_lines(anti, prefix): return need(chr(10).join(l for l in anti.splitlines() if l.startswith(prefix)), "anti-pattern lines starting " + repr(prefix))

def _alias(value):
    m = re.fullmatch(r"var\(--([a-z-]+)\)", value.strip())
    return m.group(1) if m else None

def colour_roles(tokens):
    """Every custom property in tokens.css whose value is a colour, or an alias of one
    (--sidebar: var(--card)) - exactly the set a Tailwind mapping has to cover."""
    body = re.sub(r"@theme[^{]*\{[\s\S]*?\n\}", "", tokens)  # a mapping entry is not a declaration
    decls = dict(re.findall(r"^\s*--([a-z-]+):\s*([^;]+);", body, re.M))
    roles = {n for n, v in decls.items() if re.match(r"(oklch|rgba?|hsla?|color-mix)\(|#[0-9a-fA-F]{3,8}", v.strip())}
    for _ in range(len(decls)):  # an alias may point at an alias, so grow until the set is stable
        grew = {n for n, v in decls.items() if _alias(v) in roles}
        if grew <= roles: break
        roles |= grew
    return roles

def theme_map(tokens):
    """The Tailwind mapping is lifted from tokens.css, never retyped here: a hand-copied copy drifts
    the moment a role is added, and nothing in the generated file shows that it has."""
    blocks = []
    for pat, what in ((r"^@theme inline \{[\s\S]*?\n\}", "the @theme inline block"),
                      (r"^@theme \{[\s\S]*?\n\}", "the @theme block"),
                      (r"^@custom-variant dark [^\n]+", "the @custom-variant dark line")):
        m = re.search(pat, tokens, re.M)
        blocks.append(need(m.group(0) if m else "", what + " of references/tokens.css"))
    mapped, roles = set(re.findall(r"--color-([a-z-]+):", blocks[0])), colour_roles(tokens)
    if roles - mapped: sys.exit("build_dist: colour roles in tokens.css with no --color-* mapping: " + ", ".join(sorted(roles - mapped)))
    if mapped - roles: sys.exit("build_dist: --color-* mappings for roles tokens.css never declares: " + ", ".join(sorted(mapped - roles)))
    return "\n\n".join(blocks)

def strip_links(md):
    """Tier 3 is pasted into a chat with no checkout, so a repo path in it is a pointer the reader can
    never follow. A parenthesised pointer is dropped; anything else has to be reworded in the source,
    because a builder cannot rewrite prose safely."""
    md = re.sub(r"[ \t]*\(`?(?:scripts|references|assets)/[^`)\s]+`?\)", "", md)
    left = sorted(set(re.findall(r"(?:scripts|references|assets)/[\w./-]+", md)))
    if left: sys.exit("build_dist: the paste-in tier still points at repo paths a chat tool cannot open: " + ", ".join(left) + " - reword them in the source")
    return md

def build():
    quick = read("references/quick-card.md")
    anti = read("references/anti-patterns.md")
    pers = read("references/personalities.md")
    tokens = read("references/tokens.css")
    _core = re.search(r":root \{[\s\S]*?\n\}\n\n[\s\S]*?\.dark \{[\s\S]*?\n\}", tokens)
    tokens_core = need(_core.group(0) if _core else "", "the :root/.dark blocks of references/tokens.css")
    tmap = theme_map(tokens)
    presets = re.findall(r"^### \d\. `(theme-[a-z]+)` — ([^\n]+)\n\n```css\n([\s\S]*?)```", pers, re.M)
    presets_md = need("\n".join(f"- **{n}** ({d}):\n```css\n{c.strip()}\n```" for n, d, c in presets[:3]),
                      "personality presets of references/personalities.md")
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
{anti_lines(anti, "- ⚙")}

{manual}
"""
    prompt = strip_links(f"""# jbelly-ui — paste-in UI system for chat tools (generated; self-contained)

Use this whole message as instructions for any UI you produce in this conversation.
Output complete HTML with Tailwind v4 (`<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>`) and Lucide icons unless the user names another stack; then translate the class strings to that stack.

## 1. Design read (first output, four fields)
`kind` · `audience` (who, how often, keyboard or touch) · `vibe` (three words) · `system` (preset + dials changed). State it, then build. Never ship the default look: pick a preset below and change at least two dials (palette, shape, density, signature element).

## 2. Tokens — paste this CSS first (it is the whole colour system; components use roles only)
```css
{tokens_core}
```
Tailwind mapping — paste this too (generated from the token file, so no role is missing):
```css
{tmap}
```

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
{anti_lines(anti, "- ")}

{manual}
""")
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
