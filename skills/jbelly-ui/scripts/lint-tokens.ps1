<#
.SYNOPSIS
  jbelly-ui token lint — finds raw Tailwind palette colours used outside tokens.css.

.DESCRIPTION
  The design system allows raw colours (bg-blue-500, text-gray-600, border-zinc-200 …)
  in exactly one file: tokens.css. Anywhere else they bypass the semantic roles,
  break dark mode and make re-branding a search-and-replace job.

  Deterministic (Class D) — no model call needed. Exit code 1 when violations exist.

.EXAMPLE
  pwsh scripts/lint-tokens.ps1 src
  pwsh scripts/lint-tokens.ps1 . -Exclude legacy,vendor
#>
param(
  [Parameter(Position = 0)] [string] $Path = ".",
  [string[]] $Exclude = @(),
  [switch] $Quiet
)

$ErrorActionPreference = "Stop"

$palette = 'slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose'
$prefix  = 'bg|text|border|ring|fill|stroke|from|via|to|divide|outline|shadow|accent|caret|decoration|placeholder'
# matches  bg-blue-500  dark:text-gray-400/70  hover:border-zinc-200  etc.
$pattern = "(?<![\w-])(?:[\w-]+:)*(?:$prefix)-(?:$palette)-\d{2,3}(?:/\d{1,3})?(?![\w-])"

$extensions = '*.html','*.htm','*.css','*.scss','*.js','*.jsx','*.ts','*.tsx','*.vue','*.svelte','*.razor','*.cshtml','*.php','*.astro','*.md'
$skipDirs   = @('node_modules', 'dist', 'build', '.git', '.next', 'bin', 'obj', 'vendor') + $Exclude

$files = Get-ChildItem -Path $Path -Recurse -File -Include $extensions |
  Where-Object {
    $full = $_.FullName
    -not ($skipDirs | Where-Object { $full -match "[\\/]$([regex]::Escape($_))[\\/]" }) -and
    $_.Name -ne 'tokens.css'
  }

$violations = @()
foreach ($f in $files) {
  $n = 0
  foreach ($line in [System.IO.File]::ReadLines($f.FullName)) {
    $n++
    if ($line -match 'ui-lint-ignore') { continue }
    foreach ($m in [regex]::Matches($line, $pattern)) {
      $violations += [pscustomobject]@{ File = $f.FullName; Line = $n; Match = $m.Value }
    }
  }
}

if ($violations.Count -eq 0) {
  if (-not $Quiet) { Write-Host "jbelly-ui lint: OK - $($files.Count) files, no raw palette colours." -ForegroundColor Green }
  exit 0
}

$violations | ForEach-Object { Write-Host ("{0}:{1}: {2}" -f $_.File, $_.Line, $_.Match) }
Write-Host ""
$fileCount = ($violations | Select-Object -ExpandProperty File -Unique).Count
Write-Host "jbelly-ui lint: $($violations.Count) raw palette colour(s) in $fileCount file(s)." -ForegroundColor Red
Write-Host "Replace with a semantic role (bg-primary, text-muted-foreground, border-border, ...) or add the colour to tokens.css."
Write-Host "Silence a deliberate exception by putting 'ui-lint-ignore' in a comment on that line."
exit 1
