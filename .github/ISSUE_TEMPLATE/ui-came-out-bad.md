---
name: "UI came out bad"
about: The skill produced a page that looks wrong, generic, broken or off-brief
title: "[bad output] <one line: what was asked>"
labels: ["bad-output", "beta"]
---

**Brief you gave the agent** (paste it; it becomes an eval brief)

**Agent and model** (e.g. Cursor + GPT-5, Claude Code + Sonnet, chat-only with the paste-in prompt)

**How the skill was installed** (skills CLI / install script / dist/AGENTS.md / dist/jbelly-ui-prompt.md)

**Verdicts** (paste the last lines)
```
python skills/jbelly-ui/scripts/verify_page.py <page> --variants ",#dark=1,#dir=rtl" --widths 1440,375
python skills/jbelly-ui/scripts/preflight.py <page>
```

**Screenshot** (1440 and, if relevant, 375)

**What is wrong, in one or two sentences**

**Did the agent write `design/personality.md` first?** yes / no
