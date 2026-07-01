# France Civique IA (DocIA) — image production
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dépendances système (PDF, PostgreSQL client libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Code applicatif
COPY src/ ./src/
COPY app.py main.py run_app.py diagnose.py ./
COPY sql/ ./sql/
COPY data/documents/ ./data/documents/

# Sauvegarde des documents embarqués (copiés dans le volume au 1er démarrage)
RUN cp -a data/documents /app/data/documents.bundled

COPY docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

COPY .streamlit/ ./.streamlit/

RUN mkdir -p data/vectorstore

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8501/_stcore/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["web"]
