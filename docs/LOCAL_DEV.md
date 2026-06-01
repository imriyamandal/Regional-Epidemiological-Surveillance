# One-time local setup (Windows, no Docker)

```powershell
cd dopewis\backend
python -m venv venv
.\venv\Scripts\pip install -r requirements-local.txt

cd ..
.\backend\venv\Scripts\python.exe -m ml.training.pipeline_local
.\backend\venv\Scripts\python.exe scripts\seed_database.py
```

# Start platform

Double-click `scripts/start-local.bat` or:

```powershell
# Terminal 1 — Backend
cd dopewis\backend
$env:PYTHONPATH="."
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd dopewis\frontend
npm run dev
```

| URL | Service |
|-----|---------|
| http://localhost:3000 | Dashboard |
| http://localhost:8000/docs | API Swagger |
| Login | `admin@dopewis.health` / `Admin@12345` |

Uses **SQLite** (`backend/dopewis.db`) when Docker is unavailable. For production, use `docker compose up`.
