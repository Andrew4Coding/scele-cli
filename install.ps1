<#
Cross-platform installer for the `scele` CLI (Windows PowerShell 5.1 / PowerShell 7+).

  .\install.ps1                 install from this checkout, via pipx
  .\install.ps1 -Editable       install in editable mode (code changes apply live)
  .\install.ps1 -From <src>     install from a path or git URL instead of this dir
  .\install.ps1 -Uninstall      remove it

Needs: Python >= 3.10 (from python.org or the Microsoft Store).
Everything else (pip, pipx) is bootstrapped.
#>
[CmdletBinding()]
param(
    [switch]$Editable,
    [switch]$Uninstall,
    [string]$From
)
$ErrorActionPreference = 'Stop'

try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

$tick  = if ([Console]::OutputEncoding.CodePage -eq 65001) { [char]0x2714 } else { '[OK]' }
$cross = if ([Console]::OutputEncoding.CodePage -eq 65001) { [char]0x2716 } else { '[FAIL]' }
$info  = if ([Console]::OutputEncoding.CodePage -eq 65001) { [char]0x2139 } else { '[!]' }

function Show-Banner {
    Write-Host ""
    Write-Host "     _____ _____ _____ __    _____ " -ForegroundColor Yellow
    Write-Host "    |   __|     |   __|  |  |   __|" -ForegroundColor Yellow
    Write-Host "    |__   |   --|   __|  |__|   __|" -ForegroundColor Yellow
    Write-Host "    |_____|_____|_____|_____|_____|  " -ForegroundColor Yellow -NoNewline
    Write-Host "CLI" -ForegroundColor Cyan
    Write-Host "    Moodle client for CS Universitas Indonesia (scele.cs.ui.ac.id)" -ForegroundColor DarkGray
    Write-Host ""
}

function Write-StepStart {
    param([int]$Step, [int]$Total, [string]$Message)
    Write-Host "  " -NoNewline
    Write-Host "[$Step/$Total] " -ForegroundColor Cyan -NoNewline
    Write-Host "$Message..."
}

function Write-StepSuccess {
    param([int]$Step, [int]$Total, [string]$Message)
    Write-Host "  " -NoNewline
    Write-Host "$tick " -ForegroundColor Green -NoNewline
    Write-Host "[$Step/$Total] " -ForegroundColor White -NoNewline
    Write-Host $Message
}

function Write-StepFailed {
    param([int]$Step, [int]$Total, [string]$Message)
    Write-Host "  " -NoNewline
    Write-Host "$cross " -ForegroundColor Red -NoNewline
    Write-Host "[$Step/$Total] " -ForegroundColor White -NoNewline
    Write-Host "$Message (failed)" -ForegroundColor Red
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $From) { $From = $ScriptDir }

function Find-Python {
    $probe = 'import sys; sys.exit(0 if sys.version_info[:2] >= (3,10) else 1)'
    foreach ($cand in @(@('py','-3'), @('python'), @('python3'))) {
        $exe = $cand[0]
        if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
        $probeArgs = @()
        if ($cand.Count -gt 1) { $probeArgs += $cand[1] }
        $probeArgs += @('-c', $probe)
        & $exe @probeArgs 2>$null
        if ($LASTEXITCODE -eq 0) { return ,$cand }
    }
    throw "Python >= 3.10 not found. Install it from https://www.python.org/downloads/ (tick 'Add python.exe to PATH') and re-run."
}

Show-Banner

$py = Find-Python
$script:PyExe = $py[0]
$script:PyPre = @(); if ($py.Count -gt 1) { $script:PyPre = @($py[1]) }
function Py { & $script:PyExe @script:PyPre @args }

if ($Uninstall) {
    Write-StepStart 1 1 "Uninstalling scele-cli via pipx"
    try {
        Py -m pipx uninstall scele-cli *> $null
        Write-StepSuccess 1 1 "Uninstalled scele-cli"
        Write-Host ""
        Write-Host "  $tick Successfully removed scele-cli." -ForegroundColor Green
        Write-Host "  (Auth token left in ~/.config/scele/token.json; run 'scele logout' if desired.)" -ForegroundColor DarkGray
        Write-Host ""
    } catch {
        Write-StepFailed 1 1 "Uninstalling scele-cli"
        throw $_
    }
    exit 0
}

$totalSteps = 4

# Step 1: Detect Python
$pyVer = (Py --version 2>&1)
Write-StepSuccess 1 $totalSteps "Detected Python: $pyVer ($script:PyExe)"

# Step 2: Bootstrap pipx if needed
Py -m pipx --version *> $null
if ($LASTEXITCODE -ne 0) {
    Write-StepStart 2 $totalSteps "Bootstrapping pipx package runner"
    try {
        Py -m pip install --user --upgrade pipx *> $null
        Write-StepSuccess 2 $totalSteps "Bootstrapped pipx package runner"
    } catch {
        Write-StepFailed 2 $totalSteps "Bootstrapping pipx"
        throw "Could not install pipx: $_"
    }
} else {
    $pipxVer = (Py -m pipx --version 2>&1)
    Write-StepSuccess 2 $totalSteps "pipx package runner is available: v$pipxVer"
}

# Step 3: Configure PATH via pipx
Write-StepStart 3 $totalSteps "Configuring pipx environment PATH"
try {
    Py -m pipx ensurepath *> $null
    Write-StepSuccess 3 $totalSteps "Configured pipx environment PATH"
} catch {
    Write-StepFailed 3 $totalSteps "Configuring pipx PATH"
}

# Step 4: Install package
$installArgs = @('install', '--force')
$installDesc = "from $From"
if ($Editable) {
    $installArgs += '--editable'
    $installDesc = "editable mode from $From"
}
$installArgs += $From

Write-StepStart 4 $totalSteps "Installing scele CLI ($installDesc)"
try {
    Py -m pipx @installArgs *> $null
    Write-StepSuccess 4 $totalSteps "Installed scele CLI ($installDesc)"
} catch {
    Write-StepFailed 4 $totalSteps "Installing scele CLI"
    throw "Installation failed: $_"
}

# Summary Card
Write-Host ""
if (Get-Command scele -ErrorAction SilentlyContinue) {
    $exe = (Get-Command scele).Source
    $installedVer = try { (& $exe --version 2>$null) } catch { "scele" }

    Write-Host "  " -NoNewline
    Write-Host $tick -ForegroundColor Green -NoNewline
    Write-Host " SCELE CLI installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  │  " -ForegroundColor Cyan -NoNewline
    Write-Host "Executable: " -ForegroundColor White -NoNewline
    Write-Host "$exe"
    Write-Host "  │  " -ForegroundColor Cyan -NoNewline
    Write-Host "Source:     " -ForegroundColor White -NoNewline
    Write-Host "$From"
    Write-Host "  │  " -ForegroundColor Cyan -NoNewline
    Write-Host "Version:    " -ForegroundColor White -NoNewline
    Write-Host "$installedVer"
    Write-Host ""
    Write-Host "  Quick Start:" -ForegroundColor White
    Write-Host "    scele login" -ForegroundColor Cyan -NoNewline
    Write-Host "     Authenticate with your SCELE account"
    Write-Host "    scele courses" -ForegroundColor Cyan -NoNewline
    Write-Host "   List your enrolled courses"
    Write-Host "    scele --help" -ForegroundColor Cyan -NoNewline
    Write-Host "    Explore available commands and options"
    Write-Host ""
} else {
    Write-Host "  " -NoNewline
    Write-Host $info -ForegroundColor Yellow -NoNewline
    Write-Host " Notice: 'scele' is not on your PATH in this session." -ForegroundColor Yellow
    Write-Host "  Close and reopen your terminal, then run: " -NoNewline
    Write-Host "scele login" -ForegroundColor Cyan
    Write-Host ""
}
