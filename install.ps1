# install.ps1 — Install blender-mcp addon for Blender (Windows)
# Detects Blender version and copies addon files to the correct directory.

param(
    [switch]$Help
)

if ($Help) {
    Write-Host "install.ps1 — Install blender-mcp addon for Blender"
    Write-Host ""
    Write-Host "Usage: .\install.ps1"
    exit 0
}

$AddonSrc = Join-Path $PSScriptRoot "addon"

# Find Blender
$BlenderPaths = @(
    "${env:PROGRAMFILES}\Blender Foundation\Blender*",
    "${env:LOCALAPPDATA}\Microsoft\WindowsApps\blender.exe",
    "${env:USERPROFILE}\AppData\Local\Blender Foundation\Blender*"
)

$BlenderFound = $false
$BlenderVersion = $null

foreach ($pattern in $BlenderPaths) {
    $items = Get-ChildItem $pattern -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        if ($item.PSIsContainer -or $item.Name -eq "blender.exe") {
            if ($item.PSIsContainer) {
                $ver = $item.Name -replace 'Blender ', ''
                $BlenderVersion = $ver
            }
            $BlenderFound = $true
            break
        }
    }
    if ($BlenderFound) { break }
}

# Also try via command
try {
    $ver = & blender --version 2>&1 | Select-String -Pattern "Blender (\d+\.\d+)" | ForEach-Object { $_.Matches.Groups[1].Value }
    if ($ver) { $BlenderVersion = $ver; $BlenderFound = $true }
} catch {}

if (-not $BlenderFound -or -not $BlenderVersion) {
    Write-Host "❌ Blender not found."
    Write-Host "   Download from: https://www.blender.org/download/"
    exit 1
}

$AddonDir = "$env:APPDATA\Blender Foundation\Blender\$BlenderVersion\scripts\addons\ai_assistant"

if (-not (Test-Path $AddonSrc)) {
    Write-Host "❌ Addon source not found: $AddonSrc"
    Write-Host "   Run this script from the blender-mcp root directory."
    exit 1
}

New-Item -ItemType Directory -Force -Path $AddonDir | Out-Null
Copy-Item -Path "$AddonSrc\*" -Destination $AddonDir -Recurse -Force

Write-Host "✅ blender-mcp addon installed!" -ForegroundColor Green
Write-Host "   Location: $AddonDir" -ForegroundColor Green
Write-Host "   Blender:  $BlenderVersion" -ForegroundColor Green
Write-Host ""
Write-Host "   Next steps:"
Write-Host "   1. Open Blender"
Write-Host "   2. Edit → Preferences → Add-ons"
Write-Host "   3. Search for 'AI Assistant'"
Write-Host "   4. Enable it"
Write-Host "   5. In 3D Viewport, open the Sidebar (N) → AI tab"
