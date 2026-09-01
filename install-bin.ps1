<#
Download a prebuilt `scele` binary from GitHub Releases. No Python needed.

  irm https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.ps1 | iex

Env overrides:
  $env:SCELE_VERSION = 'v0.1.0'          install a specific tag (default: latest)
  $env:SCELE_BIN_DIR = 'C:\tools\scele'  install location
#>
$ErrorActionPreference = 'Stop'
$repo = 'Andrew4Coding/scele-cli'
$version = if ($env:SCELE_VERSION) { $env:SCELE_VERSION } else { 'latest' }
$binDir  = if ($env:SCELE_BIN_DIR) { $env:SCELE_BIN_DIR } else { "$env:LOCALAPPDATA\Programs\scele" }

if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') {
    throw "No Windows ARM64 build yet. Install with Python instead: pipx install git+https://github.com/$repo.git"
}
$asset = 'scele-windows-x86_64.exe'
$base = if ($version -eq 'latest') {
    "https://github.com/$repo/releases/latest/download"
} else {
    "https://github.com/$repo/releases/download/$version"
}

New-Item -ItemType Directory -Force -Path $binDir | Out-Null
$dest = Join-Path $binDir 'scele.exe'

Write-Host "Downloading $asset ($version)..."
Invoke-WebRequest "$base/$asset" -OutFile $dest -UseBasicParsing

try {
    $sums = (Invoke-WebRequest "$base/checksums.txt" -UseBasicParsing).Content
    $line = $sums -split "`n" | Where-Object { $_ -match "\s$([regex]::Escape($asset))\s*$" } | Select-Object -First 1
    if ($line) {
        $want = ($line -split '\s+')[0].ToLower()
        $got = (Get-FileHash $dest -Algorithm SHA256).Hash.ToLower()
        if ($want -ne $got) { Remove-Item $dest; throw "checksum mismatch for $asset" }
        Write-Host "checksum ok"
    }
} catch {
    Write-Warning "checksum not verified: $_"
}

$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (($userPath -split ';') -notcontains $binDir) {
    [Environment]::SetEnvironmentVariable('Path', "$userPath;$binDir", 'User')
    Write-Host "Added $binDir to your user PATH. Restart your terminal."
}

Write-Host "Installed: $dest"
Write-Host "Next:  scele login   then   scele courses"
