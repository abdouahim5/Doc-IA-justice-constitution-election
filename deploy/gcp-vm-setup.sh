#!/usr/bin/env bash
# Script d'installation sur VM GCP Ubuntu 24.04
# Exécuter en root ou avec sudo : bash deploy/gcp-vm-setup.sh

set -euo pipefail

echo "=== DocIA — installation VM GCP ==="

if ! command -v docker >/dev/null 2>&1; then
    echo "[1/4] Installation Docker..."
    apt-get update -qq
    apt-get install -y -qq ca-certificates curl git
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker "$SUDO_USER" 2>/dev/null || true
else
    echo "[1/4] Docker déjà installé"
fi

if [ ! -f .env ]; then
    echo "[2/4] Création .env depuis .env.production.example"
    cp .env.production.example .env
    echo ">>> ÉDITEZ .env : OPENAI_API_KEY et POSTGRES_PASSWORD"
    echo "    nano .env"
    exit 1
fi

if grep -q "changez-moi-mot-de-passe-fort" .env 2>/dev/null; then
    echo "ERREUR: changez POSTGRES_PASSWORD dans .env"
    exit 1
fi

echo "[3/4] Build et démarrage Docker Compose GCP..."
docker compose -f docker-compose.gcp.yml up -d --build

echo "[4/4] Attente santé..."
sleep 15
docker compose -f docker-compose.gcp.yml ps

echo ""
echo "=== Étape suivante : ingestion (première fois) ==="
echo "  docker compose -f docker-compose.gcp.yml exec app python main.py pg-ingest"
echo "  docker compose -f docker-compose.gcp.yml exec app python main.py index"
echo ""
EXTERNAL_IP=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip 2>/dev/null || hostname -I | awk '{print $1}')
echo "Interface : http://${EXTERNAL_IP}:8501"
