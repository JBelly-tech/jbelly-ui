<#
.SYNOPSIS  Capture a page with headless Edge at a fixed size (deterministic, no Playwright needed).
.EXAMPLE   powershell -File tools/screenshot.ps1 -Url "file:///D:/x/dashboard.html#dark=1" -Out shots/dark.png
#>
param(
  [Parameter(Mandatory)] [string] $Url,
  [Parameter(Mandatory)] [string] $Out,
  [int] $Width = 1440,
  [int] $Height = 1000,
  [int] $BudgetMs = 25000,
  [switch] $DumpDom,
  [switch] $Log
)
$edge = @("C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "C:\Program Files\Microsoft\Edge\Application\msedge.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw "Edge not found" }
$prof = Join-Path $env:TEMP ("edge-shot-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
if (-not [System.IO.Path]::IsPathRooted($Out)) { $Out = Join-Path (Get-Location).Path $Out }
$Out = [System.IO.Path]::GetFullPath($Out)
New-Item -ItemType Directory -Force (Split-Path -Parent $Out) | Out-Null
$args = @("--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars", "--window-size=$Width,$Height", "--timeout=$BudgetMs", "--virtual-time-budget=$BudgetMs", "--user-data-dir=$prof")
if ($Log) { $args += @("--enable-logging", "--log-level=0") }
if ($DumpDom) {
  & $edge @args --dump-dom $Url 2>$null | Out-File -Encoding utf8 $Out
} else {
  & $edge @args "--screenshot=$Out" $Url 2>$null | Out-Null
}
if ($Log) {
  $log = Get-ChildItem -Path $prof -Recurse -Filter "chrome_debug.log" -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($log) { Get-Content $log.FullName | Where-Object { $_ -match "CONSOLE" -and $_ -notmatch "Tracking Prevention" } }
}
"{0} bytes -> {1}" -f (Get-Item $Out).Length, $Out
