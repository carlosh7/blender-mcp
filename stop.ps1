# stop.ps1 — Stop blender-mcp MCP server (Windows)
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*mcp_server*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "✅ blender-mcp stopped"
