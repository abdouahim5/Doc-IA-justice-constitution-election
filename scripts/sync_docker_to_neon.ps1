# Synchronise le corpus PostgreSQL Docker (local) vers Neon (cloud).
# Usage : powershell -ExecutionPolicy Bypass -File scripts\sync_docker_to_neon.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$dumpPath = Join-Path $Root "data\docia_neon_sync.dump"
$envFile = Join-Path $Root ".env"

if (-not (Test-Path $envFile)) {
    Write-Error ".env introuvable. Definissez DATABASE_URL (Neon, sans -pooler)."
}

$neonUrl = $null
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*DATABASE_URL\s*=\s*(.+)\s*$') {
        $neonUrl = $matches[1].Trim().Trim('"').Trim("'")
    }
}
if (-not $neonUrl) {
    Write-Error "DATABASE_URL absent dans .env"
}
$neonUrl = $neonUrl -replace '^postgresql\+psycopg://', 'postgresql://'
if ($neonUrl -match '-pooler\.') {
    Write-Warning "DATABASE_URL utilise le pooler Neon. Preferez l'hote direct pour gros imports."
}

New-Item -ItemType Directory -Force -Path (Join-Path $Root "data") | Out-Null

Write-Host "==> 1/4 Export Docker (365 sources, ~125k chunks)..." -ForegroundColor Cyan
docker exec docia-postgres pg_dump -U docia -d docia_fr `
    --data-only `
    -t public.sources `
    -t public.document_chunks `
    -t public.extracted_tables `
    -t public.structured_facts `
    -Fc -f /tmp/docia_neon_sync.dump
if ($LASTEXITCODE -ne 0) { throw "pg_dump Docker a echoue" }

docker cp docia-postgres:/tmp/docia_neon_sync.dump $dumpPath
$sizeMb = [math]::Round((Get-Item $dumpPath).Length / 1MB, 1)
Write-Host "    Dump : $dumpPath ($sizeMb Mo)" -ForegroundColor Green

Write-Host "==> 2/4 Vidage des tables Neon..." -ForegroundColor Cyan
$truncateSql = @"
TRUNCATE TABLE query_cache, document_chunks, extracted_tables, structured_facts, sources
RESTART IDENTITY CASCADE;
"@
docker run --rm postgres:16 psql $neonUrl -v ON_ERROR_STOP=1 -c $truncateSql
if ($LASTEXITCODE -ne 0) { throw "TRUNCATE Neon a echoue" }

Write-Host "==> 3/4 Import vers Neon (peut prendre 10-30 min)..." -ForegroundColor Cyan
docker run --rm -v "${Root}/data:/backup" postgres:16 `
    pg_restore -d $neonUrl --data-only --no-owner --no-privileges /backup/docia_neon_sync.dump
if ($LASTEXITCODE -ne 0) { throw "pg_restore Neon a echoue" }

Write-Host "==> 4/4 Verification..." -ForegroundColor Cyan
docker run --rm postgres:16 psql $neonUrl -c "SELECT * FROM v_corpus_stats;"

Write-Host ""
Write-Host "Synchronisation terminee. Mettez DATABASE_URL pooler dans Streamlit Secrets." -ForegroundColor Green
