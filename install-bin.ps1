<#
Download a prebuilt `scele` from GitHub Releases. No Python needed.

  irm https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.ps1 | iex

Env overrides:
  $env:SCELE_VERSION = 'v0.2.0'          install a specific tag (default: latest)
  $env:SCELE_BIN_DIR = 'C:\tools\scele'  where the bundle is unpacked
#>
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

$repo = 'Andrew4Coding/scele-cli'
$version = if ($env:SCELE_VERSION) { $env:SCELE_VERSION } else { 'latest' }
$binDir  = if ($env:SCELE_BIN_DIR) { $env:SCELE_BIN_DIR } else { "$env:LOCALAPPDATA\Programs\scele" }
$totalSteps = 4

Show-Banner

# Step 1: Detect architecture
if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') {
    Write-Host "  $cross " -ForegroundColor Red -NoNewline
    Write-Host "Error: No Windows ARM64 build yet. Install with Python instead: pipx install git+https://github.com/$repo.git" -ForegroundColor Red
    exit 1
}

Write-StepSuccess 1 $totalSteps "Detected environment: Windows x86_64"

$asset = 'scele-windows-x86_64.zip'
$base = if ($version -eq 'latest') {
    "https://github.com/$repo/releases/latest/download"
} else {
    "https://github.com/$repo/releases/download/$version"
}

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("scele-" + [System.Guid]::NewGuid())
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$zip = Join-Path $tmp $asset

# Step 2: Download release asset
Write-StepStart 2 $totalSteps "Downloading prebuilt bundle ($asset)"
try {
    Invoke-WebRequest "$base/$asset" -OutFile $zip -UseBasicParsing
    Write-StepSuccess 2 $totalSteps "Downloaded prebuilt bundle ($asset)"
} catch {
    Write-StepFailed 2 $totalSteps "Downloading prebuilt bundle ($asset)"
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    throw "Download failed: $_"
}

# Step 3: Verify SHA-256 checksum
Write-StepStart 3 $totalSteps "Verifying SHA-256 integrity checksum"
try {
    $sums = (Invoke-WebRequest "$base/checksums.txt" -UseBasicParsing).Content
    $line = $sums -split "`n" | Where-Object { $_ -match "\s$([regex]::Escape($asset))\s*$" } | Select-Object -First 1
    if ($line) {
        $want = ($line -split '\s+')[0].ToLower()
        $got = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
        if ($want -ne $got) {
            Write-StepFailed 3 $totalSteps "Checksum verification mismatch"
            Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
            throw "checksum mismatch for $asset (expected: $want, got: $got)"
        }
    }
    Write-StepSuccess 3 $totalSteps "Verified SHA-256 integrity checksum"
} catch {
    Write-StepFailed 3 $totalSteps "Verifying SHA-256 integrity checksum"
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    throw $_
}

# Step 4: Unpack bundle and link
Write-StepStart 4 $totalSteps "Unpacking application bundle to $binDir"
try {
    if (Test-Path $binDir) { Remove-Item -Recurse -Force $binDir }
    New-Item -ItemType Directory -Force -Path $binDir | Out-Null
    Expand-Archive -Path $zip -DestinationPath $tmp -Force
    Copy-Item -Recurse -Force (Join-Path $tmp 'scele\*') $binDir
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue

    $exe = Join-Path $binDir 'scele.exe'
    if (-not (Test-Path $exe)) {
        throw "bundle missing scele.exe (unpacked to $binDir)"
    }
    Write-StepSuccess 4 $totalSteps "Unpacked application bundle to $binDir"
} catch {
    Write-StepFailed 4 $totalSteps "Unpacking application bundle"
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    throw $_
}

$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$needsPath = ($userPath -split ';') -notcontains $binDir
if ($needsPath) {
    [Environment]::SetEnvironmentVariable('Path', "$userPath;$binDir", 'User')
}

# Summary Card
Write-Host ""
Write-Host "  " -NoNewline
Write-Host $tick -ForegroundColor Green -NoNewline
Write-Host " SCELE CLI installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "  │  " -ForegroundColor Cyan -NoNewline
Write-Host "Executable: " -ForegroundColor White -NoNewline
Write-Host "$exe"
Write-Host "  │  " -ForegroundColor Cyan -NoNewline
Write-Host "Version:    " -ForegroundColor White -NoNewline
Write-Host "$version"
Write-Host ""
Write-Host "  Quick Start:" -ForegroundColor White
Write-Host "    scele login" -ForegroundColor Cyan -NoNewline
Write-Host "     Authenticate with your SCELE account"
Write-Host "    scele courses" -ForegroundColor Cyan -NoNewline
Write-Host "   List your enrolled courses"
Write-Host "    scele --help" -ForegroundColor Cyan -NoNewline
Write-Host "    Explore available commands and options"
Write-Host ""

if ($needsPath) {
    Write-Host "  " -NoNewline
    Write-Host $info -ForegroundColor Yellow -NoNewline
    Write-Host " Notice: Added $binDir to your User PATH." -ForegroundColor Yellow
    Write-Host "  Close and restart your terminal to begin using " -NoNewline
    Write-Host "scele" -ForegroundColor Cyan -NoNewline
    Write-Host "."
    Write-Host ""
}
