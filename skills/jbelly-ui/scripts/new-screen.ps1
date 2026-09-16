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

$darkClass = ""
if ($Dark) { $darkClass = "dark" }
$classes = @("h-full", $Theme, $Density, $darkClass) | Where-Object { $_ -ne "" }
$html = $html -replace '<html lang="en" dir="ltr" class="h-full">', ('<html lang="en" dir="' + $Direction + '" class="' + ($classes -join " ") + '">')
$html = $html -replace '<title>jbelly-ui — app shell</title>', ('<title>' + $Product + ' — ' + $Title + '</title>')
$html = $html -replace 'Nutrio Clinic', $Product
$html = $html -replace '<h1 class="text-xl font-medium text-mono font-display">Dashboard</h1>', ('<h1 class="text-xl font-medium text-mono font-display">' + $Title + '</h1>')
if ($StripDemoControls) {
  $html = [regex]::Replace($html, '(?s)<!-- ===== Demo controls.*?</details>\s*', '')
}
if ([System.IO.Path]::IsPathRooted($Out)) { $full = $Out } else { $full = Join-Path (Get-Location).Path $Out }
$full = [System.IO.Path]::GetFullPath($full)
$outDir = Split-Path -Parent $full
if ($outDir -and -not (Test-Path $outDir)) { New-Item -ItemType Directory -Force $outDir | Out-Null }
[System.IO.File]::WriteAllText($full, $html, (New-Object System.Text.UTF8Encoding($false)))
"scaffolded {0} ({1:N0} bytes) theme={2} density={3} dir={4} dark={5}" -f $full, $html.Length, $Theme, $Density, $Direction, $Dark.IsPresent
