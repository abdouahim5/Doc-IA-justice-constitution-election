# Prérequis Docker Desktop sur Windows — WSL 2
# Exécuter en PowerShell ADMINISTRATEUR

Write-Host "=== Installation WSL 2 (requis pour Docker) ===" -ForegroundColor Cyan

wsl --status 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "WSL déjà installé." -ForegroundColor Green
    wsl --status
    exit 0
}

Write-Host "Installation WSL 2 en cours..." -ForegroundColor Yellow
wsl --install --no-distribution

Write-Host ""
Write-Host "IMPORTANT : Redémarrez Windows, puis :" -ForegroundColor Green
Write-Host "  1. Ouvrir Docker Desktop (attendre 'Engine running')"
Write-Host "  2. cd vers le projet"
Write-Host "  3. demarrer_docker.bat"
Write-Host "  4. python main.py pg-init"
Write-Host "  5. python main.py scrape --ingest"
