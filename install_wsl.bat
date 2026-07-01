@echo off
cd /d "%~dp0"
echo === DocIA - Installation WSL 2 (requis pour Docker) ===
echo.
echo Une fenetre administrateur va s'ouvrir...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0scripts\install_wsl.ps1\"'"
echo.
echo Apres installation : REDEMARREZ Windows, lancez Docker Desktop, puis demarrer_docker.bat
pause
