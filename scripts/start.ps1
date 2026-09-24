$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$envFile = Join-Path $projectRoot ".env"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Missing .venv. Run: py -3.12 -m venv .venv"
}
if (-not (Test-Path -LiteralPath $envFile)) {
    throw "Missing .env. Copy .env.example to .env and add DEEPSEEK_API_KEY."
}

$cacheRoot = Join-Path $projectRoot ".cache\huggingface"
$env:HF_HOME = $cacheRoot
$env:SENTENCE_TRANSFORMERS_HOME = $cacheRoot
$env:TORCH_HOME = Join-Path $cacheRoot "torch"
$env:USER_AGENT = "AgentHub/0.1"

Set-Location $projectRoot
& $python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

