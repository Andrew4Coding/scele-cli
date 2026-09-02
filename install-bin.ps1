<#
Download a prebuilt `scele` from GitHub Releases. No Python needed.

  irm https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.ps1 | iex

Env overrides:
  $env:SCELE_VERSION = 'v0.2.0'          install a specific tag (default: latest)
  $env:SCELE_BIN_DIR = 'C:\tools\scele'  where the bundle is unpacked
#>
$ErrorActionPreference = 'Stop'
$repo = 'Andrew4Coding/scele-cli'
$version = if ($env:SCELE_VERSION) { $env:SCELE_VERSION } else { 'latest' }
$binDir  = if ($env:SCELE_BIN_DIR) { $env:SCELE_BIN_DIR } else { "$env:LOCALAPPDATA\Programs\scele" }

if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') {
    throw "No Windows ARM64 build yet. Install with Python instead: pipx install git+https://github.com/$repo.git"
}
$asset = 'scele-windows-x86_64.zip'
$base = if ($version -eq 'latest') {
    "https://github.com/$repo/releases/latest/download"
} else {
    "https://github.com/$repo/releases/download/$version"
}

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("scele-" + [System.Guid]::NewGuid())
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$zip = Join-Path $tmp $asset

Write-Host "Downloading $asset ($version)..."
Invoke-WebRequest "$base/$asset" -OutFile $zip -UseBasicParsing

try {
    $sums = (Invoke-WebRequest "$base/checksums.txt" -UseBasicParsing).Content
    $line = $sums -split "`n" | Where-Object { $_ -match "\s$([regex]::Escape($asset))\s*$" } | Select-Object -First 1
    if ($line) {
        $want = ($line -split '\s+')[0].ToLower()
        $got = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
        if ($want -ne $got) { throw "checksum mismatch for $asset" }
        Write-Host "checksum ok"
    }
} catch {
    Write-Warning "checksum not verified: $_"
}

# Unpack the onedir bundle (its top-level folder is `scele\`).
if (Test-Path $binDir) { Remove-Item -Recurse -Force $binDir }
New-Item -ItemType Directory -Force -Path $binDir | Out-Null
Expand-Archive -Path $zip -DestinationPath $tmp -Force
Copy-Item -Recurse -Force (Join-Path $tmp 'scele\*') $binDir
Remove-Item -Recurse -Force $tmp

$exe = Join-Path $binDir 'scele.exe'
if (-not (Test-Path $exe)) { throw "bundle missing scele.exe (unpacked to $binDir)" }

$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (($userPath -split ';') -notcontains $binDir) {
    [Environment]::SetEnvironmentVariable('Path', "$userPath;$binDir", 'User')
    Write-Host "Added $binDir to your user PATH. Restart your terminal."
}

Write-Host "Installed: $exe"
Write-Host "Next:  scele login   then   scele courses"
