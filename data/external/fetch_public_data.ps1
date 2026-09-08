$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$url = "https://www.itl.nist.gov/div898/handbook/datasets/IMPROVE-5_4_7_3.DAT"
Invoke-WebRequest -Uri $url -OutFile (Join-Path $root "IMPROVE-5_4_7_3.DAT")
Write-Host "EXTERNAL_DATA_REFRESH=PASS"
