# DOPEWIS one-time local setup (Windows, no Docker)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "=== DOPEWIS Setup ===" -ForegroundColor Cyan

# Backend venv
if (-not (Test-Path "backend\venv\Scripts\python.exe")) {
    Write-Host "Creating Python venv..."
    python -m venv backend\venv
}
Write-Host "Installing Python dependencies..."
& backend\venv\Scripts\pip install -q -r backend\requirements-local.txt

# Backend env
if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env" -ErrorAction SilentlyContinue
    @"
DATABASE_URL=sqlite+aiosqlite:///./dopewis.db
DATABASE_URL_SYNC=sqlite:///./dopewis.db
SECRET_KEY=dev-local-secret-key-for-dopewis
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENVIRONMENT=development
"@ | Set-Content "backend\.env"
}

# Frontend env
if (-not (Test-Path "frontend\.env.local")) {
    "NEXT_PUBLIC_API_URL=http://localhost:8000" | Set-Content "frontend\.env.local"
}

# ML training
Write-Host "Training ML models (may take 1-2 min)..."
& backend\venv\Scripts\python.exe -m ml.training.pipeline_local

# Seed database (backend must use same DB path)
Write-Host "Seeding surveillance database..."
& backend\venv\Scripts\python.exe scripts\seed_database.py
& backend\venv\Scripts\python.exe scripts\register_model.py

Write-Host ""
Write-Host "Setup complete! Run: .\scripts\start-local.bat" -ForegroundColor Green
Write-Host "Login: admin@dopewis.health / Admin@12345"
