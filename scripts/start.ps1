# start.ps1 — Start blender-mcp MCP server (Windows)
# Usage: .\start.ps1
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogFile = Join-Path $env:TEMP "blender-mcp-server.log"

# Kill any existing instance
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*mcp_server*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Process -FilePath "python" -ArgumentList "$ScriptDir\mcp_server.py" `
    -WindowStyle Hidden -RedirectStandardOutput $LogFile

Write-Host "✅ blender-mcp started (log: $LogFile)"
