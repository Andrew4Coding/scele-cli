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

$py = Find-Python
$script:PyExe = $py[0]
$script:PyPre = @(); if ($py.Count -gt 1) { $script:PyPre = @($py[1]) }
function Py { & $script:PyExe @script:PyPre @args }

Write-Host "Using $(Py --version) via $script:PyExe"

Py -m pipx --version *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing pipx..."
    Py -m pip install --user --upgrade pipx
}

if ($Uninstall) {
    Py -m pipx uninstall scele-cli
    Write-Host "Removed. (Session cookie left in place.)"
    exit 0
}

Py -m pipx ensurepath *> $null

$installArgs = @('install', '--force')
if ($Editable) { $installArgs += '--editable' }
$installArgs += $From
Write-Host "Installing scele from $From ..."
Py -m pipx @installArgs

Write-Host ""
if (Get-Command scele -ErrorAction SilentlyContinue) {
    Write-Host "Installed: $((Get-Command scele).Source)"
    Write-Host "Next:  scele login   then   scele courses"
} else {
    Write-Host "Installed, but 'scele' is not on your PATH in this session."
    Write-Host "Close and reopen your terminal, then run:  scele login"
}
