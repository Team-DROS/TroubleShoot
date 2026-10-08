param([int]$Port = 8765)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$pythonPath = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Create .venv and install requirements.lock first. See docs/MEMBER_3_SETUP.md.' }
$env:PYTHONPATH = Join-Path $projectRoot 'src'
& $pythonPath -m troubleshoot.api --port $Port
exit $LASTEXITCODE
