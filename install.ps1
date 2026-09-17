<#
.SYNOPSIS
  Install jbelly-ui without Node: copies skills/jbelly-ui into your agent's skills folder.

.EXAMPLE
  .\install.ps1                      # Claude Code, user-wide  (~/.claude/skills/jbelly-ui)
  .\install.ps1 -Agent cursor        # Cursor, user-wide
  .\install.ps1 -Agent codex -Project # Codex, into ./.agents/skills of the current project
  .\install.ps1 -Dest "C:\path\to\skills"   # any folder

  With Node installed you can use the skills CLI instead:  npx skills add mohammadJohar/jbelly-ui -a claude-code -g
#>
param(
  [ValidateSet("claude-code", "cursor", "copilot", "codex", "windsurf", "gemini-cli", "custom")] [string] $Agent = "claude-code",
  [switch] $Project,
  [string] $Dest = ""
)
$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "skills\jbelly-ui"
if (-not (Test-Path (Join-Path $src "SKILL.md"))) { throw "skills/jbelly-ui/SKILL.md not found next to this script" }
$global = @{ "claude-code" = "$HOME\.claude\skills"; "cursor" = "$HOME\.cursor\skills"; "copilot" = "$HOME\.copilot\skills"; "codex" = "$HOME\.codex\skills"; "windsurf" = "$HOME\.codeium\windsurf\skills"; "gemini-cli" = "$HOME\.gemini\skills" }
$local  = @{ "claude-code" = ".claude\skills"; "cursor" = ".agents\skills"; "copilot" = ".agents\skills"; "codex" = ".agents\skills"; "windsurf" = ".windsurf\skills"; "gemini-cli" = ".agents\skills" }
if (-not $Dest) {
  if ($Agent -eq "custom") { throw "Pass -Dest for a custom agent" }
  $Dest = if ($Project) { Join-Path (Get-Location).Path $local[$Agent] } else { $global[$Agent] }
}
$target = Join-Path $Dest "jbelly-ui"
New-Item -ItemType Directory -Force $Dest | Out-Null
if (Test-Path $target) { Remove-Item -Recurse -Force $target }
Copy-Item -Recurse $src $target
"installed jbelly-ui -> $target"
"next: ask your agent for any UI (e.g. 'add a dashboard page'); the skill triggers on UI work."
