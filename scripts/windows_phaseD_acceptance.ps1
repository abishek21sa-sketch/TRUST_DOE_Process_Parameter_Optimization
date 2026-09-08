$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
Write-Host "TRUST-DOE Phase D Windows Acceptance"

function Resolve-Python {
  foreach ($candidate in @("python","python3")) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) { return @{ exe=$candidate; args=@() } }
  }
  $py = Get-Command "py" -ErrorAction SilentlyContinue
  if ($py) { return @{ exe="py"; args=@("-3") } }
  throw "No Python 3 runtime found on PATH."
}

$base = Resolve-Python
$venvPy = Join-Path $repo ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
  Write-Host "Creating isolated virtual environment..."
  & $base.exe @($base.args) -m venv .venv
}
& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install -e ".[dev]"
& $venvPy -m pytest -q -m "not slow"
& $venvPy .\scripts\build_phaseD_evidence.py
& $venvPy .\scripts\validate_phaseD.py
& $venvPy -m compileall -q .\src .\scripts
Write-Host "PHASE D WINDOWS ACCEPTANCE: PASS"
Write-Host "Start product with .\scripts\start_platform.ps1 (default http://127.0.0.1:8772)"
