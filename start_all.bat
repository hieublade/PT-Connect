@echo off
title Khoi dong he thong PTConnect
echo =======================================================
echo    Khoi dong ca Backend va Frontend PTConnect
echo =======================================================

start "PTConnect Backend (8080)" "%~dp0run_backend.bat"
timeout /t 3 /nobreak >nul
start "PTConnect Frontend (3000)" "%~dp0run_frontend.bat"

echo.
echo He thong dang duoc khoi dong trong 2 cua so rieng biet:
echo - Backend:  http://localhost:8080
echo - Frontend: http://localhost:3000
echo.
pause
