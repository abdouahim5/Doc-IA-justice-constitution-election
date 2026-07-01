@echo off
cd /d "%~dp0"
set "DOCKER=C:\Program Files\Docker\Docker\resources\bin"
set "PATH=%DOCKER%;%PATH%"

echo === DocIA - Demarrage PostgreSQL (Docker) ===

wsl --status >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERREUR] WSL 2 non installe - Docker ne peut pas demarrer.
    echo Lancez : install_wsl.bat  ^(admin^), redemarrez Windows, puis relancez.
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo Docker installe mais moteur arrete. Ouvrez Docker Desktop et attendez "Engine running".
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    pause
    exit /b 1
)

docker compose up -d
if errorlevel 1 (
    echo.
    echo Docker non disponible. Installez-le :
    echo   scripts\install_docker.ps1  ^(PowerShell administrateur^)
    echo   python main.py docker-install --launch
    pause
    exit /b 1
)
echo.
echo PostgreSQL demarre sur localhost:5432
echo Lancez : python main.py pg-init
pause
