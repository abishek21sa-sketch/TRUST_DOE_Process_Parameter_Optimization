$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    & $VenvPython "scripts\start_workbench.py"
    exit $LASTEXITCODE
}
foreach ($candidate in @("python", "python3")) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) { & $candidate "scripts\start_workbench.py"; exit $LASTEXITCODE }
}
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) { & py -3 "scripts\start_workbench.py"; exit $LASTEXITCODE }
throw "Python was not found. Run windows_phaseB_acceptance.ps1 first."
