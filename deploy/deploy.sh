#!/usr/bin/env bash
# Déploiement DocIA sur VPS Linux (Ubuntu/Debian)
set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"
PROFILE="${1:-}"

echo "=== DocIA — déploiement production ==="

if [ ! -f .env ]; then
    echo "Fichier .env manquant. Copie depuis .env.production.example..."
    cp .env.production.example .env
    echo "Éditez .env (OPENAI_API_KEY, POSTGRES_PASSWORD) puis relancez ce script."
    exit 1
fi

if grep -q "changez-moi-mot-de-passe-fort" .env 2>/dev/null; then
    echo "ERREUR: changez POSTGRES_PASSWORD dans .env avant le déploiement."
    exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker non installé. Installation..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER" || true
    echo "Reconnectez-vous pour utiliser Docker sans sudo, puis relancez."
    exit 0
fi

echo "Build et démarrage des services..."
if [ "$PROFILE" = "https" ]; then
    docker compose -f "$COMPOSE_FILE" --profile https up -d --build
else
    docker compose -f "$COMPOSE_FILE" up -d --build
fi

echo ""
echo "Attente santé des conteneurs..."
sleep 10
docker compose -f "$COMPOSE_FILE" ps

echo ""
echo "=== Étape suivante : ingestion du corpus ==="
echo "  docker compose -f $COMPOSE_FILE exec app python main.py pg-ingest"
echo "  docker compose -f $COMPOSE_FILE exec app python main.py index"
echo ""
echo "Interface : http://$(hostname -I 2>/dev/null | awk '{print $1}'):8501"
echo "Logs      : docker compose -f $COMPOSE_FILE logs -f app"
