# How to Run DOPEWIS Smoothly (Windows)

## The #1 rule

**The terminal is NOT stuck after startup.**  
When you see `Application startup complete` (backend) or `Ready` (frontend), the server is running and waiting for browser requests. **Keep that window open.**

---

## Easiest way (recommended)

1. Open File Explorer → go to `dopewis\scripts\`
2. Double-click **`start-local.bat`**
3. Two black windows open (Backend + Frontend) — **do not close them**
4. Open browser → **http://localhost:3000**
5. Login: `admin@dopewis.health` / `Admin@12345`

To stop: double-click **`stop-local.bat`**

---

## Manual way (two separate terminals)

### Terminal 1 — Backend
```cmd
cd "C:\Users\riya\OneDrive\Documents\project\Regional Epidemiological Surveillance\dopewis\backend"
set PYTHONPATH=.
venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Frontend
```cmd
cd "C:\Users\riya\OneDrive\Documents\project\Regional Epidemiological Surveillance\dopewis\frontend"
npm run dev
```

**Do NOT use** `.\venv\Scripts\activate` — PowerShell blocks it on your PC.  
**Do NOT use** plain `uvicorn` — it is not in PATH. Always use `venv\Scripts\python.exe -m uvicorn`.

---

## Common mistakes (from your terminal)

| Mistake | Fix |
|---------|-----|
| `cd dopewis` while already inside `backend` | You are already in the right folder |
| `uvicorn` not recognized | Use `venv\Scripts\python.exe -m uvicorn` |
| `activate.ps1` blocked | Skip activate; use full venv path above |
| Terminal looks frozen | Normal — open http://localhost:3000 |
| Port already in use | Run `scripts\stop-local.bat` first |

---

## First-time only

Double-click or run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```

---

## Quick health check

Open in browser:
- http://localhost:8000/health → should show `{"status":"healthy"}`
- http://localhost:3000 → landing page
