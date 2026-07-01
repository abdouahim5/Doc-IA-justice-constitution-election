# Installation Docker Desktop pour DocIA (PostgreSQL)
# Clic droit > Exécuter en tant qu'administrateur

$ErrorActionPreference = "Continue"

Write-Host "=== DocIA — Installation Docker Desktop ===" -ForegroundColor Cyan

$dockerExe = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
if (Test-Path $dockerExe) {
    Write-Host "Docker Desktop déjà installé." -ForegroundColor Green
    Start-Process $dockerExe
    exit 0
}

$envPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($envPath -match "Docker") {
    Write-Host "Docker semble installé — redémarrez Windows puis lancez Docker Desktop." -ForegroundColor Yellow
    exit 0
}

Write-Host "[1/2] Installation via winget..." -ForegroundColor Yellow
$winget = Start-Process winget -ArgumentList @(
    "install", "Docker.DockerDesktop",
    "--source", "winget",
    "--accept-package-agreements",
    "--accept-source-agreements"
) -Wait -PassThru -NoNewWindow

if ($winget.ExitCode -ne 0) {
    Write-Host "[2/2] winget échoué — téléchargement direct..." -ForegroundColor Yellow
    $installer = "$env:TEMP\DockerDesktopInstaller.exe"
    $url = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
    try {
        Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
        Write-Host "Lancement de l'installateur Docker..." -ForegroundColor Green
        Start-Process -FilePath $installer -ArgumentList "install", "--quiet", "--accept-license" -Wait
    } catch {
        Write-Host "Échec téléchargement : $_" -ForegroundColor Red
        Write-Host "Téléchargez manuellement : https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
        exit 1
    }
}

if (Test-Path $dockerExe) {
    Write-Host "Installation réussie !" -ForegroundColor Green
    Start-Process $dockerExe
} else {
    Write-Host "Installation lancée — terminez l'assistant si une fenêtre s'ouvre." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Étapes suivantes :" -ForegroundColor Cyan
Write-Host "  1. Redémarrer Windows (recommandé)"
Write-Host "  2. Lancer Docker Desktop"
Write-Host "  3. Activer WSL 2 si demandé"
Write-Host "  4. docker compose up -d"
Write-Host "  5. python main.py pg-init && python main.py scrape --ingest"
