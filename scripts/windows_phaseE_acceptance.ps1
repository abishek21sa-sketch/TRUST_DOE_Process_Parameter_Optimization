$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { $Python = (Get-Command python -ErrorAction SilentlyContinue).Source }
if (-not $Python) { throw 'Python 3.11+ is required; no interpreter found.' }
Write-Host 'TRUST-DOE Phase E acceptance'
& $Python -m pip install -e "$Root[dev]" --disable-pip-version-check
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& $Python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Test suite failed.' }
& $Python -m compileall -q (Join-Path $Root 'src')
if ($LASTEXITCODE -ne 0) { throw 'Compilation failed.' }
Write-Host 'ACCEPTANCE STATUS: PASS'
