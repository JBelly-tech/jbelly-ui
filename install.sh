#!/usr/bin/env sh
# Install jbelly-ui without Node: copies skills/jbelly-ui into your agent's skills folder.
#   ./install.sh                     # Claude Code, user-wide (~/.claude/skills/jbelly-ui)
#   ./install.sh cursor              # Cursor, user-wide
#   ./install.sh codex --project     # Codex, into ./.agents/skills of the current project
#   ./install.sh custom /path/to/skills
# With Node: npx skills add mohammadJohar/jbelly-ui -a claude-code -g
set -e
here="$(cd "$(dirname "$0")" && pwd)"
src="$here/skills/jbelly-ui"
[ -f "$src/SKILL.md" ] || { echo "skills/jbelly-ui/SKILL.md not found"; exit 1; }
agent="${1:-claude-code}"; mode="${2:-}"
case "$agent" in
  claude-code) g="$HOME/.claude/skills"; l=".claude/skills" ;;
  cursor)      g="$HOME/.cursor/skills"; l=".agents/skills" ;;
  copilot)     g="$HOME/.copilot/skills"; l=".agents/skills" ;;
  codex)       g="$HOME/.codex/skills"; l=".agents/skills" ;;
  windsurf)    g="$HOME/.codeium/windsurf/skills"; l=".windsurf/skills" ;;
  gemini-cli)  g="$HOME/.gemini/skills"; l=".agents/skills" ;;
  custom)      g="$2"; l="$2"; mode="" ;;
  *) echo "unknown agent: $agent (claude-code|cursor|copilot|codex|windsurf|gemini-cli|custom <dir>)"; exit 1 ;;
esac
[ -n "$g" ] || { echo "custom needs a destination folder"; exit 1; }
dest="$g"; [ "$mode" = "--project" ] && dest="$(pwd)/$l"
mkdir -p "$dest"; rm -rf "$dest/jbelly-ui"; cp -R "$src" "$dest/jbelly-ui"
echo "installed jbelly-ui -> $dest/jbelly-ui"
echo "next: ask your agent for any UI (e.g. 'add a dashboard page'); the skill triggers on UI work."
