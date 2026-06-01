@echo off
echo Starting DOPEWIS in two separate windows...
cd /d "%~dp0"
start "DOPEWIS Backend"  cmd /k "%~dp0run-backend.bat"
timeout /t 4 /nobreak >nul
start "DOPEWIS Frontend" cmd /k "%~dp0run-frontend.bat"
echo.
echo Open http://localhost:3000 in your browser.
echo Login: admin@dopewis.health / Admin@12345
echo.
echo TIP: Do NOT close the two black windows that opened.
timeout /t 5
