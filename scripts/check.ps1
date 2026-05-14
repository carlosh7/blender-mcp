# blender-mcp — Environment Check (Windows PowerShell)
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  blender-mcp — System Check (Windows)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Python
try {
    $py = python --version 2>&1
    Write-Host "  ✅ Python: $py" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python not found. Download: https://python.org" -ForegroundColor Red
}

# Blender
try {
    $bl = Get-Command blender.exe -ErrorAction Stop
    $ver = & $bl.Source --version 2>&1 | Select -First 1
    Write-Host "  ✅ Blender: $ver" -ForegroundColor Green
    Write-Host "         Path: $($bl.Source)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Blender not found. Download: https://www.blender.org/download/" -ForegroundColor Red
}

# Disk space
$drive = (Get-Location).Drive.Root
$free = (Get-PSDrive -Name $drive[0]).Free / 1MB
Write-Host "  ✅ Disk free: $([math]::Round($free)) MB" -ForegroundColor Green

# pip
try {
    pip --version 2>&1 | Out-Null
    Write-Host "  ✅ pip installed" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️ pip not found. Run: python -m ensurepip" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  To install dependencies:" -ForegroundColor Cyan
Write-Host "    pip install -r requirements.txt" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
