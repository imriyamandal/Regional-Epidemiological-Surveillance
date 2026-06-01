@echo off
title DOPEWIS Frontend
cd /d "%~dp0..\frontend"
echo.
echo ========================================
echo   DOPEWIS Frontend  ->  http://localhost:3000
echo   Login: admin@dopewis.health / Admin@12345
echo ========================================
echo.
echo Server is RUNNING when you see "Ready".
echo It will look idle — that is normal. Keep this window open.
echo Press Ctrl+C to stop.
echo.
call npm run dev
pause
