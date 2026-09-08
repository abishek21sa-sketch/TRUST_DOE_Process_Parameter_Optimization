$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
$port = if ($env:PPO_PORT) { $env:PPO_PORT } else { "8772" }
$python = Join-Path $repo ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Run .\scripts\windows_phaseD2_acceptance.ps1 first to create .venv." }
Write-Host "TRUST-DOE platform starting on http://127.0.0.1:$port"
& $python .\scripts\start_platform.py --port $port
