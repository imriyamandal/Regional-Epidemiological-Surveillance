# GitHub Push Checklist

## Before first push

```powershell
cd dopewis

# 1. Ensure secrets are NOT staged
git status   # .env, venv/, node_modules/, *.db should NOT appear

# 2. Copy env templates (if fresh clone)
copy .env.example backend\.env
copy frontend\.env.example frontend\.env.local

# 3. Verify backend
cd backend
set PYTHONPATH=.
venv\Scripts\pytest.exe -v

# 4. Verify frontend
cd ..\frontend
npm run lint
npm run build
```

## Init git (from repo root)

```powershell
cd "Regional Epidemiological Surveillance"
git init
git add .
git status   # review — no .env, no venv, no node_modules
git commit -m "Initial commit: DOPEWIS disease surveillance platform"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Files that must NEVER be committed

- `backend/.env`, `dopewis/.env`
- `backend/venv/`
- `frontend/node_modules/`, `frontend/.next/`
- `backend/dopewis.db`
- `backend/artifacts/*.joblib`
- `mlruns/`
