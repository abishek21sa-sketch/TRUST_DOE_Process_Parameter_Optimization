$ErrorActionPreference = "Stop"

Write-Host "TRUST-DOE Phase A Windows Acceptance"

# Always run from the repository root, regardless of the caller's current folder.
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

function Resolve-PythonCommand {
    $candidates = @(
        @{ Command = "python"; PrefixArgs = @() },
        @{ Command = "python3"; PrefixArgs = @() },
        @{ Command = "py"; PrefixArgs = @("-3") }
    )

    foreach ($candidate in $candidates) {
        $resolved = Get-Command $candidate.Command -ErrorAction SilentlyContinue
        if ($null -eq $resolved) { continue }

        try {
            $versionOutput = & $candidate.Command @($candidate.PrefixArgs) --version 2>&1
            if ($LASTEXITCODE -eq 0 -and "$versionOutput" -match "Python 3\.") {
                return @{
                    Command = $candidate.Command
                    PrefixArgs = $candidate.PrefixArgs
                    Version = "$versionOutput"
                }
            }
        }
        catch {
            # Continue probing other launchers.
        }
    }

    throw @"
Python 3.11+ was not found on PATH.
Install/enable Python 3.11 or newer, then reopen PowerShell and verify one of these works:
  python --version
  python3 --version
  py -3 --version
No other project dependency has been installed or changed.
"@
}

$Python = Resolve-PythonCommand
Write-Host "Using $($Python.Command) $($Python.PrefixArgs -join ' ') -> $($Python.Version)"

$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating isolated virtual environment..."
    & $Python.Command @($Python.PrefixArgs) -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
}

if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment Python was not created at $VenvPython"
}

& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }

& $VenvPython -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) { throw "Project dependency installation failed." }

& $VenvPython -m pytest
if ($LASTEXITCODE -ne 0) { throw "Automated tests failed." }

& $VenvPython scripts\validate_phaseA.py
if ($LASTEXITCODE -ne 0) { throw "Phase A validator failed." }

& $VenvPython -m trustdoe.cli
if ($LASTEXITCODE -ne 0) { throw "Closed-loop diagnostic failed." }

Write-Host "PHASE A WINDOWS ACCEPTANCE: PASS"
