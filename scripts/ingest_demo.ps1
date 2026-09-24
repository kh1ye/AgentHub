$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$document = Join-Path $projectRoot "data\documents\agenthub_demo.md"

curl.exe --fail-with-body -X POST "http://localhost:8000/documents/upload" `
    -F "file=@$document;type=text/markdown"

