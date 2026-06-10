$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
Set-Location (Join-Path $root "daemon")
& $python -m uvicorn main:app --host 0.0.0.0 --port 8765 --reload
