# Multi-agent France — Constitution & Élections

DocIA dispose d'un **système multi-agent** spécialisé pour la France civique, avec stockage PostgreSQL (pgvector) et cache de réponses instantanées.

## Architecture

```mermaid
flowchart LR
    Q[Question] --> R[Routeur]
    R --> C[Agent Constitution]
    R --> E[Agent Élections]
    R --> J[Agent Justice]
    R --> T[Agent Test civique]
    R --> D[Agent Données]
    R --> G[Agent Général]
    C --> PG[(PostgreSQL)]
    E --> PG
    J --> PG
    T --> PG
    D --> PG
    G --> PG
    PG --> Cache[query_cache]
    Cache -->|hit| Q
```

### Agents

| Agent | Domaine | Sources utilisées |
|-------|---------|-------------------|
| `constitution` | Droit constitutionnel | Articles, institutions, éligibilité |
| `elections` | Scrutins, calendrier | Chunks + tableaux électoraux |
| `justice` | Lois, délits, crimes | Légifrance, service-public, crawler |
| `test_civique` | Naturalisation, civique | Formation civique, livret citoyen |
| `data` | Chiffres, taux, statistiques | `structured_facts`, tableaux |
| `general` | Fallback | Tout le corpus |

### Tables PostgreSQL

- `sources` — fichiers classés (constitution / elections / general)
- `document_chunks` — texte + embedding vector(1536)
- `extracted_tables` — tableaux extraits des PDF (pdfplumber)
- `structured_facts` — paires clé-valeur numériques
- `query_cache` — réponses mises en cache (SHA-256 de la question)

## Démarrage rapide

### 1. Lancer PostgreSQL

```powershell
docker compose up -d
```

### 2. Installer les dépendances

```powershell
pip install -r requirements.txt
```

### 3. Configurer `.env`

```env
DATABASE_URL=postgresql+psycopg://docia:docia_secret@localhost:5433/docia_fr
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

### 4. Initialiser et ingérer

```powershell
python main.py pg-init
python main.py scrape          # télécharge les sources officielles
python main.py scrape --ingest # télécharge + indexe PostgreSQL
# ou : python main.py pg-ingest
```

Placez vos PDF (Constitution, guides électoraux, résultats INSEE…) dans `data/documents/`.

### 5. Poser des questions

**CLI :**

```powershell
python main.py multi-ask "Que dit l'article 2 de la Constitution ?"
python main.py multi-chat
python main.py pg-stats
```

**Interface web :** `python run_app.py` → menu **France Civique**.

## Pipeline d'ingestion

1. Chargement PDF / TXT / MD / DOCX
2. Classification automatique (`constitution` | `elections` | `general`)
3. Découpage en chunks + embeddings OpenAI
4. Extraction tableaux PDF → `extracted_tables`
5. Extraction chiffres → `structured_facts`

## Cache instantané

Les questions déjà posées sont stockées dans `query_cache`. Une deuxième fois, la réponse est servie **sans appel LLM** (badge « cache » dans l'interface).

Pour forcer un recalcul en CLI : `python main.py multi-ask "..." --no-cache`

## Compatibilité

L'agent RAG Chroma (`python main.py index`, page **Poser une question**) reste disponible en parallèle. Le multi-agent PostgreSQL est indépendant et recommandé pour Constitution & Élections.
