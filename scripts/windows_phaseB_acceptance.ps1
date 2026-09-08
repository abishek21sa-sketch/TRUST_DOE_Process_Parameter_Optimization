$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
Write-Host "TRUST-DOE Phase B Windows Acceptance"

function Resolve-Python {
    foreach ($candidate in @("python", "python3")) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($cmd) {
            try {
                $ver = & $candidate --version 2>&1
                if ($LASTEXITCODE -eq 0) { return @{Kind="command"; Exe=$candidate; Args=@(); Version=$ver} }
            } catch {}
        }
    }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        try {
            $ver = & py -3 --version 2>&1
            if ($LASTEXITCODE -eq 0) { return @{Kind="launcher"; Exe="py"; Args=@("-3"); Version=$ver} }
        } catch {}
    }
    throw "Python 3 was not found on PATH. Install Python 3.11+ and ensure 'python' is available in PowerShell."
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    $base = Resolve-Python
    Write-Host "Using $($base.Exe) -> $($base.Version)"
    Write-Host "Creating isolated virtual environment..."
    & $base.Exe @($base.Args) -m venv .venv
}
$Python = ".venv\Scripts\python.exe"
& $Python -m pip install --upgrade pip
& $Python -m pip install -e ".[dev]"
& $Python -m pytest
& $Python scripts\build_phaseB_evidence.py
& $Python scripts\validate_phaseB.py
& $Python -m compileall -q src scripts
Write-Host "PHASE B WINDOWS ACCEPTANCE: PASS"
Write-Host "Workbench: run .\scripts\start_workbench.ps1 then open http://127.0.0.1:8765"
