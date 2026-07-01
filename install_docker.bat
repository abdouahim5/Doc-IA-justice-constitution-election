@echo off
cd /d "%~dp0"
echo Lancement install Docker (admin requis)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0scripts\install_docker.ps1\"'"
pause
