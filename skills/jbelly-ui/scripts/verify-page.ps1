<#
.SYNOPSIS
  One-call verification of a page: render in headless Edge, capture console errors, lint tokens, screenshot,
  run the pre-flight (scripts/preflight.py). The verdict names the checks that actually ran.
  Replaces multi-step verify loops (the main cost driver in agent runs). Class D.

.EXAMPLE
  powershell -File scripts/verify-page.ps1 -Path src/pages/dashboard.html
  powershell -File scripts/verify-page.ps1 -Path dashboard.html -Variants "#dark=1","#dir=rtl" -OutDir shots
#>
param(
  [Parameter(Mandatory)] [string] $Path,
  [string[]] $Variants = @(""),
  [string] $OutDir = "",
  [int] $Width = 1440,
  [int] $Height = 1000,
  [int] $BudgetMs = 20000
)
$ErrorActionPreference = "Stop"
$Variants = @($Variants | ForEach-Object { $_ -split "," })
$edge = @("C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "C:\Program Files\Microsoft\Edge\Application\msedge.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw "Edge not found; install Microsoft Edge or use Playwright" }
$full = (Resolve-Path -LiteralPath $Path).Path
$url = "file:///" + ($full -replace '\\', '/')
if (-not $OutDir) { $OutDir = Join-Path $env:TEMP "verify-page" }
New-Item -ItemType Directory -Force $OutDir | Out-Null
$name = [System.IO.Path]::GetFileNameWithoutExtension($full)
$fail = $false
$lint = Join-Path $PSScriptRoot "lint-tokens.ps1"
$lintOut = & powershell -NoProfile -ExecutionPolicy Bypass -File $lint (Split-Path -Parent $full) -Quiet 2>&1
$lintCode = $LASTEXITCODE
foreach ($v in $Variants) {
  $prof = Join-Path $env:TEMP ("edge-verify-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
  $tag = if ($v) { ($v -replace '[^a-z0-9]+', '-').Trim('-') } else { "default" }
  $png = Join-Path $OutDir "$name-$tag.png"
  $ErrorActionPreference = "Continue"
  & $edge --headless=new --disable-gpu --no-first-run --hide-scrollbars "--window-size=$Width,$Height" "--timeout=$BudgetMs" "--virtual-time-budget=$BudgetMs" --enable-logging --log-level=0 "--user-data-dir=$prof" "--screenshot=$png" ($url + $v) 2>&1 | Out-Null
  $ErrorActionPreference = "Stop"
  $log = Get-ChildItem -Path $prof -Recurse -Filter "chrome_debug.log" -ErrorAction SilentlyContinue | Select-Object -First 1
  $errors = @()
  if ($log) { $errors = Get-Content $log.FullName | Where-Object { $_ -match "CONSOLE" -and $_ -match "Uncaught|Error|error|Cannot apply|Failed to" -and $_ -notmatch "Tracking Prevention|ProtocolLaunch" } }
  $size = (Get-Item $png).Length
  $status = if ($errors.Count -gt 0) { "FAIL" } elseif ($size -lt 40000) { "SUSPECT" } else { "OK" }
  if ($status -eq "FAIL") { $fail = $true }
  "[{0}] variant '{1}': screenshot {2:N0} bytes -> {3}" -f $status, $(if ($v) { $v } else { "(default)" }), $size, $png
  foreach ($e in $errors | Select-Object -First 3) { "    " + ($e -replace '^.*CONSOLE:\d+\] ', '') }
  if ($status -eq "SUSPECT") { "    screenshot is very small: page may be unstyled or blank; open it and check" }
}
"[{0}] token lint: {1}" -f $(if ($lintCode -eq 0) { "OK" } else { "FAIL" }), $(if ($lintCode -eq 0) { "no raw palette classes" } else { ($lintOut | Select-Object -Last 3) -join " | " })
if ($lintCode -ne 0) { $fail = $true }
$checks = @(("render ({0} variant(s))" -f $Variants.Count), "token lint")
# The PASS line tells the agent to stop verifying, so every check it names must really have run:
# a pre-flight that cannot start fails the run instead of quietly dropping off the list.
$pfScript = Join-Path $PSScriptRoot "preflight.py"
$py = @("py", "python", "python3") | Where-Object { Get-Command $_ -ErrorAction SilentlyContinue } | Select-Object -First 1
if (-not (Test-Path $pfScript)) {
  "[FAIL] pre-flight: preflight.py not found next to this script ($pfScript)"
  $fail = $true
} elseif (-not $py) {
  "[FAIL] pre-flight: no Python interpreter on PATH; install Python 3.9+ or run scripts/verify_page.py instead"
  $fail = $true
} else {
  $ErrorActionPreference = "Continue"
  $pfOut = & $py $pfScript $full 2>&1
  $pfCode = $LASTEXITCODE
  $ErrorActionPreference = "Stop"
  $pfLines = @($pfOut | ForEach-Object { "$_" })
  $pfLast = $pfLines | Where-Object { $_.Trim() } | Select-Object -Last 1
  "[{0}] pre-flight: {1}" -f $(if ($pfCode -eq 0) { "OK" } else { "FAIL" }), $(if ($pfLast) { $pfLast } else { "no output" })
  foreach ($l in $pfLines | Where-Object { $_ -match '^\[(FAIL|WARN)\]' } | Select-Object -First 6) { "    " + $l }
  if ($pfCode -ne 0) { $fail = $true }
  $checks += "pre-flight"
}
$ran = $checks -join ", "
if ($fail) { "VERDICT: FAIL (ran: $ran) - fix the items above, then run this script once more."; exit 1 } else { "VERDICT: PASS (ran: $ran) - done; do not add further verification rounds."; exit 0 }
