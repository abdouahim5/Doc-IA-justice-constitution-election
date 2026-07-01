#!/bin/sh
set -e

echo "[docia] Démarrage entrypoint — mode: ${1:-web}"

# Attendre PostgreSQL
if [ -n "${DATABASE_URL}" ]; then
    echo "[docia] Attente PostgreSQL..."
    python - <<'PY'
import os, sys, time
from sqlalchemy import create_engine, text

url = os.environ.get("DATABASE_URL", "")
deadline = time.time() + int(os.environ.get("DB_WAIT_SECONDS", "120"))
last_err = ""

while time.time() < deadline:
    try:
        engine = create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[docia] PostgreSQL joignable.")
        sys.exit(0)
    except Exception as exc:
        last_err = str(exc)
        time.sleep(2)

print(f"[docia] ERREUR: PostgreSQL inaccessible après attente: {last_err}", file=sys.stderr)
sys.exit(1)
PY
fi

# Initialiser les tables (idempotent)
if [ "${RUN_PG_INIT:-true}" = "true" ]; then
    echo "[docia] Initialisation schéma PostgreSQL..."
    python main.py pg-init
fi

# Peupler le volume documents si vide (premier démarrage)
if [ ! -f /app/data/documents/.volume_initialized ]; then
    echo "[docia] Premier démarrage — copie des documents embarqués..."
    mkdir -p /app/data/documents
    if [ -d /app/data/documents.bundled ]; then
        cp -an /app/data/documents.bundled/. /app/data/documents/ 2>/dev/null || \
        cp -r /app/data/documents.bundled/. /app/data/documents/
    fi
    touch /app/data/documents/.volume_initialized
fi

# Ingestion optionnelle au démarrage (long — désactivé par défaut)
if [ "${AUTO_PG_INGEST:-false}" = "true" ]; then
    echo "[docia] Ingestion PostgreSQL (AUTO_PG_INGEST=true)..."
    python main.py pg-ingest
fi

if [ "${AUTO_CHROMA_INDEX:-false}" = "true" ]; then
    echo "[docia] Indexation ChromaDB (AUTO_CHROMA_INDEX=true)..."
    python main.py index
fi

case "${1:-web}" in
    web)
        echo "[docia] Lancement Streamlit sur 0.0.0.0:8501"
        exec python run_app.py
        ;;
    shell)
        shift
        exec sh "$@"
        ;;
    *)
        echo "[docia] Commande personnalisée: $*"
        exec "$@"
        ;;
esac
