@echo off
title DOPEWIS Backend
cd /d "%~dp0..\backend"
set PYTHONPATH=.
echo.
echo ========================================
echo   DOPEWIS Backend  ->  http://localhost:8000
echo   API Docs         ->  http://localhost:8000/docs
echo ========================================
echo.
echo Server is RUNNING when you see "Application startup complete".
echo It will look idle — that is normal. Keep this window open.
echo Press Ctrl+C to stop.
echo.
venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
