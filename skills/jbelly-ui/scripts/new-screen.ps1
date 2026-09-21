<#
.SYNOPSIS
  Scaffold a new app screen from the house shell with zero model tokens (Class D).

.DESCRIPTION
  Copies assets/app-shell.html to the target path, sets the personality, density,
  direction and dark-mode defaults on <html>, and replaces the page title and
  product name. The agent then edits content instead of composing a shell.

.EXAMPLE
  powershell -File scripts/new-screen.ps1 -Out src/pages/dashboard.html -Theme theme-clinic -Title "Dashboard" -Product "Nutrio"
  powershell -File scripts/new-screen.ps1 -Out ops.html -Theme theme-graphite -Density density-compact -Direction rtl -Dark
#>
param(
  [Parameter(Mandatory)] [string] $Out,
  [ValidateSet("", "theme-clinic", "theme-graphite", "theme-editorial", "theme-neo", "theme-slate", "theme-mint")] [string] $Theme = "",
  [ValidateSet("", "density-compact", "density-airy")] [string] $Density = "",
  [ValidateSet("ltr", "rtl")] [string] $Direction = "ltr",
  [switch] $Dark,
  [string] $Title = "Dashboard",
  [string] $Product = "Product",
  [switch] $StripDemoControls
)
$ErrorActionPreference = "Stop"
$src = Join-Path (Split-Path -Parent $PSScriptRoot) "assets\app-shell.html"
if (-not (Test-Path $src)) { throw "scaffold not found: $src" }
$html = Get-Content -Raw -Encoding UTF8 $src

# A -replace whose anchor no longer matches returns the string untouched, so the
# scaffold would ship the shell's own brand and title under a success message.
# Every substitution is therefore asserted, and a missing anchor is fatal.
$script:anchorsApplied = 0
function Set-Anchor {
  param(
    [Parameter(Mandatory)] [string] $Text,
    [Parameter(Mandatory)] [string] $Find,
    [Parameter(Mandatory)] [string] $ReplaceWith,
    [Parameter(Mandatory)] [string] $What
  )
  if (-not $Text.Contains($Find)) {
    throw "new-screen: anchor for '$What' is not in app-shell.html - the shell was reworded, update this script. Looked for: $Find"
  }
  $script:anchorsApplied++
  # Ordinal Replace, not -replace: a $Product or $Title carrying regex or $-group
  # syntax would otherwise be expanded instead of inserted literally.
  return $Text.Replace($Find, $ReplaceWith)
}

# Windows PowerShell reads this BOM-less .ps1 as ANSI, so a literal em dash typed
# here would not match the UTF-8 one in the shell. Build it from its code point.
$emDash = [char]0x2014

$darkClass = ""
if ($Dark) { $darkClass = "dark" }
$classes = @("h-full", $Theme, $Density, $darkClass) | Where-Object { $_ -ne "" }
$html = Set-Anchor $html '<html lang="en" dir="ltr" class="h-full">' ('<html lang="en" dir="' + $Direction + '" class="' + ($classes -join " ") + '">') "root element"
$html = Set-Anchor $html ('<title>jbelly-ui ' + $emDash + ' app shell</title>') ('<title>' + $Product + ' ' + $emDash + ' ' + $Title + '</title>') "page title"
$html = Set-Anchor $html 'Bayan Ops' $Product "product name"
$html = Set-Anchor $html '<h1 class="text-xl font-medium text-mono font-display" data-i18n="Dashboard">Dashboard</h1>' ('<h1 class="text-xl font-medium text-mono font-display" data-i18n="' + $Title + '">' + $Title + '</h1>') "page heading"
if ($StripDemoControls) {
  $stripped = [regex]::Replace($html, '(?s)<!-- ===== Demo controls.*?</details>\s*', '')
  if ($stripped.Length -eq $html.Length) { throw "new-screen: -StripDemoControls matched no demo controls block in app-shell.html - update this script." }
  $html = $stripped
}
if ([System.IO.Path]::IsPathRooted($Out)) { $full = $Out } else { $full = Join-Path (Get-Location).Path $Out }
$full = [System.IO.Path]::GetFullPath($full)
$outDir = Split-Path -Parent $full
if ($outDir -and -not (Test-Path $outDir)) { New-Item -ItemType Directory -Force $outDir | Out-Null }
[System.IO.File]::WriteAllText($full, $html, (New-Object System.Text.UTF8Encoding($false)))
"scaffolded {0} ({1:N0} bytes) theme={2} density={3} dir={4} dark={5} anchors={6}" -f $full, $html.Length, $Theme, $Density, $Direction, $Dark.IsPresent, $script:anchorsApplied
