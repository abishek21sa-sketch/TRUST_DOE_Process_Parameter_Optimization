$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
Write-Host "TRUST-DOE Phase D2 Windows Acceptance"
Write-Host "Repository: $repo"
Write-Host "Acceptance runner: v0.96.4"

function Invoke-Checked([string]$Exe, [string[]]$CommandArgs) {
  Write-Host "RUNNING: $Exe $($CommandArgs -join ' ')"
  & $Exe @CommandArgs
  if ($LASTEXITCODE -ne 0) { throw "Command failed with exit code ${LASTEXITCODE}: $Exe $($CommandArgs -join ' ')" }
}
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
  if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
}
Invoke-Checked $venvPy @("-m","pip","install","--upgrade","pip")
Invoke-Checked $venvPy @("-m","pip","install","-e",".[dev]")
Invoke-Checked $venvPy @("-m","pytest","-q","-m","not slow")
Write-Host "TEST SUITE: PASS"
Invoke-Checked $venvPy @(".\scripts\build_phaseD_evidence.py")
Invoke-Checked $venvPy @(".\scripts\validate_phaseD2.py")
Invoke-Checked $venvPy @("-m","compileall","-q",".\src",".\scripts")
Write-Host "PHASE D2 WINDOWS ACCEPTANCE: PASS"
Write-Host "Start product with .\scripts\start_platform.ps1 (default http://127.0.0.1:8772)"
