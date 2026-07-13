@echo off
REM DocIA — demarrage staging local (sans build Docker)
cd /d "%~dp0"
echo === DocIA Staging ===

docker info >nul 2>&1
if %errorlevel%==0 (
    echo [1/3] Demarrage PostgreSQL...
    docker compose up -d
    timeout /t 5 /nobreak >nul
) else (
    echo [WARN] Docker indisponible - l'app utilisera ChromaDB en secours
)

echo [2/3] Initialisation base si PostgreSQL joignable...
call venv\Scripts\activate.bat
python main.py pg-init 2>nul
python main.py pg-stats 2>nul

echo [3/3] Lancement interface http://localhost:8501
python run_app.py
