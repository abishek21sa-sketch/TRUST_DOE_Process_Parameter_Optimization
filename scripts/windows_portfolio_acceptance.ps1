$ErrorActionPreference = "Stop"
Write-Host "TRUST-DOE Portfolio release Acceptance"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root
if (-not (Test-Path ".venv\Scripts\python.exe")) { py -3 -m venv .venv }
$python = ".venv\Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -e ".[dev]"
& $python -m pytest -q
& $python scripts/run_portfolio_validation.py
Write-Host "TRUST_DOE_PORTFOLIO_RELEASE_ACCEPTANCE=PASS"
