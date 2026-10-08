$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$pythonPath = Join-Path $projectRoot '.venv/Scripts/python.exe'
$env:PYTHONPATH = Join-Path $projectRoot 'src'
& $pythonPath -m unittest discover -s (Join-Path $projectRoot 'tests/unit') -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $pythonPath -m unittest discover -s (Join-Path $projectRoot 'tests/api') -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& node --test (Join-Path $projectRoot 'tests/e2e/web/app.test.cjs')
exit $LASTEXITCODE
