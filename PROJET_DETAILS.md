# France Civique IA (DocIA) — Détails du projet

> Document de référence à jour — **juillet 2026**  
> Application multi-agent RAG : Constitution, élections, justice, test civique.

---

## 1. Résumé

| Élément | Détail |
|---------|--------|
| **Nom** | France Civique IA / DocIA |
| **Type** | Agent RAG multi-sources + interface web |
| **Langue** | Français (UI FR/EN) |
| **Repo GitHub** | `abdouahim5/Doc-IA-justice-constitution-election` |
| **Branche** | `main` |
| **Entrée web** | `run_app.py` → **http://localhost:8501** |
| **Entrée cloud** | `app.py` sur Streamlit Community Cloud |

---

## 2. Stack technique

| Couche | Technologie | Rôle |
|--------|-------------|------|
| **Interface** | Streamlit 1.40+ | 8 pages, chat, thèmes, test civique, admin |
| **Orchestration** | **LangGraph** | Graphe : cache → routage → agent → sauvegarde |
| **Observabilité** | **LangSmith** (optionnel) | Traces LangGraph / LLM, latence, coûts — voir `docs/LANGSMITH.md` |
| **IA / RAG** | **LangChain** | Prompts LCEL, LLM, embeddings, retrieval |
| **LLM** | OpenAI `gpt-4o-mini` (ou Ollama local) | Synthèse des réponses |
| **Embeddings** | `text-embedding-3-small` (cloud) / TF-IDF (local rapide) | Vecteurs pgvector |
| **Base principale** | PostgreSQL 16 + **pgvector** + pg_trgm | Corpus, cache, recherche hybride |
| **Base secours** | ChromaDB local | RAG simple si PG indisponible |
| **Conteneur local** | Docker (`docia-postgres`, port **5433**) | Dev + corpus complet |
| **Cloud DB** | Neon PostgreSQL (plan gratuit 512 Mo) | Streamlit Cloud |

---

## 3. Architecture (juillet 2026)

```
Streamlit (app.py)
    │
    ├── France Civique ──► LangGraph (graph.py)
    │                           │
    │                      validate → check_cache → route_topic
    │                           → run_agent → save_cache
    │                           │
    │                      agents.py (6 agents)
    │                      chains.py (LCEL + historique)
    │                      tools.py (search_constitution, …)
    │                           │
    │                           ▼
    │                      PostgreSQL (pgvector)
    │
    ├── Poser une question ──► RAGAgent (Chroma + HybridRetriever)
    │
    └── Admin ──► diagnostic, index, scraping, schéma LangGraph
```

### 6 agents spécialisés

| Agent | Catégorie | Exemples de questions |
|-------|-----------|----------------------|
| `constitution` | constitution | « article 5 », « rôle du président » |
| `elections` | elections | dates des scrutins, calendrier |
| `justice` | justice | délits, crimes, procédure |
| `test_civique` | test_civique | naturalisation, examen civique |
| `data` | chiffres | statistiques électorales |
| `general` | tous | questions transverses |

### Outils LangChain (`tools.py`)

- `search_constitution`
- `search_elections`
- `search_justice`
- `search_test_civique`
- `search_all_corpus`

---

## 4. Structure des dossiers

```
Agent IA stucture doc/
├── run_app.py              ★ Lancer l'app (local)
├── app.py                  Interface Streamlit
├── main.py                 CLI (15+ commandes)
├── PROJET_DETAILS.md       ★ Ce fichier
├── requirements.txt        Dépendances cloud (léger)
├── requirements-full.txt   Dev local complet
├── .env                    Configuration (ne pas committer)
├── docker-compose.yml      PostgreSQL local
│
├── .streamlit/
│   ├── config.toml         Port 8501, fileWatcherType=none
│   └── secrets.toml.example
│
├── data/
│   ├── documents/          Sources PDF/TXT (365 fichiers)
│   └── vectorstore/        Index ChromaDB
│
├── sql/schema.sql          Schéma PostgreSQL + vue v_corpus_stats
│
├── scripts/
│   ├── sync_docker_to_neon.py   Sync Docker → Neon
│   ├── sync_docker_to_neon.ps1
│   └── check_neon_constitution.py
│
├── docs/                   Documentation détaillée
│   ├── PROJET_COMPLET.md
│   ├── ARCHITECTURE.md
│   ├── COMMANDES.md
│   ├── DEPLOIEMENT_STREAMLIT_CLOUD.md
│   └── DEPANNAGE.md
│
└── src/
    ├── config.py
    ├── agent/rag_agent.py
    ├── multi_agent/
    │   ├── graph.py        LangGraph
    │   ├── chains.py       LCEL
    │   ├── tools.py        Outils recherche
    │   ├── agents.py       Agents spécialisés
    │   ├── orchestrator.py Façade MultiAgentOrchestrator
    │   └── conversation.py Historique / routage
    ├── db/                 PostgreSQL
    ├── ingestion/          Chargement + pg-ingest
    ├── retrieval/          Chroma + hybrid
    ├── scraping/           Sources gouvernementales
    └── ui/                 Thème Streamlit
```

---

## 5. Bases de données

### Docker local (corpus complet)

```env
DATABASE_URL=postgresql+psycopg://docia:docia_secret@localhost:5433/docia_fr
```

| Métrique | Valeur typique |
|----------|----------------|
| Sources | **365** |
| Chunks | **~125 374** |
| Constitution | 6 |
| Élections | 39 |
| Justice | **302** |
| Test civique | 17 |
| Faits structurés | ~11 951 |

```powershell
docker compose up -d
venv\Scripts\python.exe main.py pg-stats
```

### Neon (Streamlit Cloud — plan gratuit)

| Métrique | Valeur (sync civique) |
|----------|------------------------|
| Sources | **63** (civique uniquement) |
| Chunks | **~8 666** |
| Justice | **0** (trop volumineux pour 512 Mo) |

```powershell
# Sync civique depuis Docker
venv\Scripts\python.exe scripts\sync_docker_to_neon.py --civic
```

---

## 6. Configuration `.env` essentielle

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_PROVIDER=openai
FAST_MODE=true

# Local (corpus complet)
DATABASE_URL=postgresql+psycopg://docia:docia_secret@localhost:5433/docia_fr

# Neon (cloud) — URL sans -pooler pour ingestion, avec -pooler pour l'app
# DATABASE_URL=postgresql+psycopg://...@ep-....neon.tech/neondb?sslmode=require
```

---

## 7. Commandes principales

### Lancer l'application

```powershell
cd "C:\Users\PC\Desktop\Agent IA stucture doc"
docker compose up -d
venv\Scripts\python.exe run_app.py
# → http://localhost:8501
```

### PostgreSQL

```powershell
venv\Scripts\python.exe main.py pg-init
venv\Scripts\python.exe main.py pg-ingest
venv\Scripts\python.exe main.py pg-stats
```

### Multi-agent (CLI)

```powershell
venv\Scripts\python.exe main.py multi-ask "article 5"
venv\Scripts\python.exe main.py multi-chat
```

### Scraping sources officielles

```powershell
venv\Scripts\python.exe main.py scrape
venv\Scripts\python.exe main.py scrape --category constitution --ingest
```

---

## 8. Pages Streamlit

| Page | Route | Moteur |
|------|-------|--------|
| Accueil | `accueil` | Stats PostgreSQL |
| Poser une question | `chat` | RAGAgent (Chroma) |
| France Civique | `france` | LangGraph + PostgreSQL |
| Thèmes | `themes` | Navigation |
| Exploration thème | `theme_explore` | RAGAgent |
| Test civique | `test_civique` | Module dédié |
| FAQ | `faq` | Statique |
| Configuration | `admin` | Diagnostic, index, **schéma LangGraph** |

---

## 9. Déploiements

| Cible | Fichier doc | Entrée |
|-------|-------------|--------|
| **Local dev** | `docs/DEMARRAGE.md` | `run_app.py` |
| **Staging local** | ci-dessous | `demarrer_staging.bat` |
| **Streamlit Cloud** | `docs/DEPLOIEMENT_STREAMLIT_CLOUD.md` | `app.py` |
| **VPS / Hetzner** | `docs/STAGING.md` | `docker-compose.prod.yml` |
| **Staging Docker** | — | `docker-compose.staging.yml` |
| **GCP** | `docs/DEPLOIEMENT_GCP.md` | `docker-compose.gcp.yml` |

---

## 10. Environnement STAGING

### Les 3 niveaux

| Niveau | Où | URL | Base |
|--------|-----|-----|------|
| **Dev local** | Votre PC | http://localhost:8501 | Docker `localhost:5433` (365 sources) |
| **Staging cloud** | Streamlit Community Cloud | [doc-ia….streamlit.app](https://doc-ia-justice-constitution-election-ejwpemdaupg3flgtrgziax.streamlit.app) | Neon (~63 sources civiques) |
| **Staging VPS** | Hetzner (prévu) | IP ou domaine | Docker prod complet |

### Démarrer le staging local (Windows)

Double-clic ou :

```powershell
demarrer_staging.bat
```

Équivalent à : Docker Postgres → `pg-init` → `run_app.py`

### Staging Docker (sans build image lourde)

```powershell
docker compose -f docker-compose.staging.yml up -d
```

Utilise `python:3.12-slim` + volume monté + `requirements.docker.txt` (sans torch).

### Mettre à jour le statut staging (README + docs)

1. Copier la config :

```powershell
copy deploy\staging.env.example deploy\staging.env
# Éditer deploy\staging.env (URLs, statut)
```

2. Rafraîchir les métriques :

```powershell
venv\Scripts\python.exe scripts\update_staging_status.py
```

Met à jour automatiquement :
- `README.md` (bloc `STAGING:AUTO`)
- `docs/STAGING.md` (bloc `STAGING:AUTO`)
- `deploy/staging.metrics.json`

3. Commit si besoin :

```powershell
git add README.md docs/STAGING.md deploy/staging.metrics.json
git commit -m "Mise a jour metriques staging"
```

### Fichiers staging

| Fichier | Rôle |
|---------|------|
| `docs/STAGING.md` | Page staging complète (URLs, agents, commandes VPS) |
| `deploy/staging.env.example` | Modèle de configuration URLs |
| `deploy/staging.env` | Config active (à créer, non versionné si secrets) |
| `deploy/staging.metrics.json` | Métriques JSON générées |
| `scripts/update_staging_status.py` | Script de mise à jour auto |
| `demarrer_staging.bat` | Lancement staging local Windows |
| `docker-compose.staging.yml` | Stack Docker légère |

### Déployer le staging VPS (Hetzner)

```bash
git clone https://github.com/abdouahim5/Doc-IA-justice-constitution-election.git
cd Doc-IA-justice-constitution-election
cp .env.production.example .env
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec app python main.py pg-ingest
```

Guide : [docs/STAGING.md](docs/STAGING.md) · [docs/DEPLOIEMENT.md](docs/DEPLOIEMENT.md)

---

## 11. Dépannage rapide

| Problème | Solution |
|----------|----------|
| `ERR_ADDRESS_INVALID` sur `0.0.0.0:8501` | Utiliser **http://localhost:8501** |
| `python app.py` → NameError | Utiliser **`run_app.py`** |
| Bruit `torchvision` / `transformers` | Normal si `sentence-transformers` installé ; `fileWatcherType=none` dans config |
| « Non trouvé dans les sources » | Vérifier `DATABASE_URL` et `pg-stats` |
| Justice vide sur cloud | Normal sur Neon gratuit ; utiliser Docker local |
| Erreur SQLAlchemy session | Corrigé (recherches séquentielles) |
| Page blanche Streamlit Cloud | Secrets + `app.py` + requirements légers |

---

## 12. Documentation complète

| Fichier | Contenu |
|---------|---------|
| [docs/PROJET_COMPLET.md](docs/PROJET_COMPLET.md) | Documentation exhaustive |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Schémas techniques |
| [docs/STAGING.md](docs/STAGING.md) | **Environnement staging (URLs, métriques, VPS)** |
| [docs/MULTI_AGENT.md](docs/MULTI_AGENT.md) | Agents et routage |
| [docs/COMMANDES.md](docs/COMMANDES.md) | Toutes les commandes CLI |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Variables `.env` |
| [docs/DEPANNAGE.md](docs/DEPANNAGE.md) | SSL, OpenAI, Postgres |

---

## 13. Historique récent (évolutions)

- **LangGraph** : orchestration France Civique (`src/multi_agent/graph.py`)
- **LangChain LCEL** : chaînes unifiées + historique (`chains.py`)
- **Tools** : recherche par catégorie (`tools.py`)
- **Admin** : visualisation schéma LangGraph (Mermaid)
- **Sync Neon** : script `--civic` pour plan gratuit 512 Mo
- **Streamlit Cloud** : démarrage optimisé, secrets, `app.py`

---

*Généré pour le dossier projet — France Civique IA / DocIA*
