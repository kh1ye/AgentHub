$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$tempRoot = Join-Path $projectRoot ".test_tmp\manual"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Missing .venv. Install requirements-dev.txt first."
}

$env:TEMP = Join-Path $projectRoot ".test_tmp"
$env:TMP = $env:TEMP
$env:MEMORY_BACKEND = "memory"
$env:USER_AGENT = "AgentHub/0.1 test"
New-Item -ItemType Directory -Path $env:TEMP -Force | Out-Null

Set-Location $projectRoot
& $python -m pytest -p no:cacheprovider --basetemp=$tempRoot

