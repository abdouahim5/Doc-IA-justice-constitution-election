# France Civique IA — Staging

> Une question sur la citoyenneté ? **DocIA** répond à partir des sources officielles — Constitution, élections, justice, test civique — avec les textes et les citations.

📄 **[Détails du projet (PROJET_DETAILS.md)](PROJET_DETAILS.md)** — résumé à jour (stack, **staging**, commandes)  
📚 **[Documentation complète](docs/PROJET_COMPLET.md)** — architecture détaillée  
🚀 **[Staging](docs/STAGING.md)** — URLs, métriques, déploiement VPS / Streamlit Cloud

**Branche :** `main` — environnement de staging à déployer sur Hetzner

<!-- STAGING:AUTO:START -->
**Dernière mise à jour :** 2026-07-13 11:00 UTC · Branche `main` · [Détails complets](docs/STAGING.md)

## Environnement déployé

| | |
|---|---|
| **Serveur** | Streamlit Community Cloud |
| **IP** | `—` |
| **Domaine** | `doc-ia-justice-constitution-election-ejwpemdaupg3flgtrgziax.streamlit.app` |
| **Stack** | Streamlit Cloud + Neon PostgreSQL |
| **Statut** | 🟢 En ligne |

| Interface | URL |
|-----------|-----|
| **Application** | https://doc-ia-justice-constitution-election-ejwpemdaupg3flgtrgziax.streamlit.app |
| **France Civique** (multi-agent) | https://doc-ia-justice-constitution-election-ejwpemdaupg3flgtrgziax.streamlit.app → menu *France Civique* |
| **Test civique** | https://doc-ia-justice-constitution-election-ejwpemdaupg3flgtrgziax.streamlit.app → menu *Test civique* |
| **Admin / diagnostic** | https://doc-ia-justice-constitution-election-ejwpemdaupg3flgtrgziax.streamlit.app → menu *Configuration* |
| **Health** | https://doc-ia-justice-constitution-election-ejwpemdaupg3flgtrgziax.streamlit.app/_stcore/health |

## État du déploiement

| Métrique | Valeur |
|----------|--------|
| **Chunks indexés** | — *(lancer `pg-ingest`)* |
| **Sources actives** | 220 fichiers *(PG après ingestion)* `████████████` 100% |
| **Par catégorie** | constitution 9 · élections 35 · justice 146 · test civique 24 |
| **Phase déployée** | Phase 3 — LangGraph + LangChain LCEL + tools |
| **Modèle routing** | `LangGraph (cache → route → agent) + classifier` |
| **Modèle synthesis** | `gpt-4o-mini` |
| **Embeddings** | `text-embedding-3-small` |
| **Vector store principal** | `PostgreSQL pgvector` |
| **Vector store secours** | `ChromaDB (./data/vectorstore)` |
| **Réponses en cache** | — |

## Architecture déployée

```
                         Internet
                             │
                             ▼
                   Caddy :80 / :443
                   (ou IP:8501 direct)
                             │
                             ▼
                   Streamlit :8501  (docia-app)
                   8 pages · FR/EN
                             │
                   LangGraph (graph.py)
                   MultiAgentOrchestrator
                             │
              ┌──────────────┴──────────────┐
              │  cache PG · route_topic      │
              │  LangChain tools + LCEL      │
              └──────────────┬──────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
  constitution          elections            justice
  test_civique            data              general
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
              Retrieval hybride par agent
              · vecteurs cosine (pgvector)
              · ILIKE + pg_trgm
              · patterns (articles, dates, pénal)
              · query_cache
                             │
                             ▼
              Synthesis LLM (gpt-4o-mini)
              réponses sourcées + citations
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
     PostgreSQL pgvector              ChromaDB local
     (principal · réseau interne)     (secours si PG down)
```

> Mettre à jour : `py scripts/update_staging_status.py` · config VPS : `deploy/staging.env`
<!-- STAGING:AUTO:END -->

---

# France Civique IA (DocIA)

Application **multi-agent** pour interroger des sources officielles françaises (Constitution, élections, justice, test civique) en langage naturel.

## Fonctionnalités

- **Multi-agent PostgreSQL** : 6 agents spécialisés + cache de réponses
- **RAG ChromaDB** : secours si PostgreSQL indisponible
- Ingestion multi-format (PDF, TXT, Markdown, DOCX)
- Recherche hybride : sémantique (vecteurs) + lexicale (BM25 / trigram)
- Mémoire conversationnelle et exploration par thèmes
- Scraping automatique des sources officielles FR
- Test civique intégré (quiz, examen blanc)
- OpenAI (cloud) ou Ollama (local)
- Interface CLI et web Streamlit (FR/EN)

## Démarrage rapide

```powershell
cd "C:\Users\PC\Desktop\Agent IA stucture doc"
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Éditez .env : OPENAI_API_KEY=sk-votre-cle

docker compose up -d
python main.py pg-init
python main.py scrape --ingest
python run_app.py           # → http://localhost:8501
```

**Ou** double-cliquez sur `demarrer.bat`.

> **Important** : lancez `run_app.py`, pas `app.py` directement.

## Configuration minimale (.env)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-votre-cle
EMBEDDING_PROVIDER=openai
DATABASE_URL=postgresql+psycopg://docia:docia_secret@localhost:5433/docia_fr
```

## Documentation

| Document | Sujet |
|----------|-------|
| **[docs/STAGING.md](docs/STAGING.md)** | **Environnement staging (URLs, métriques, architecture)** |
| **[docs/PROJET_COMPLET.md](docs/PROJET_COMPLET.md)** | **★ Tout le projet : architecture, flux, agents, BDD** |
| [docs/README.md](docs/README.md) | Index documentation |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Schémas techniques |
| [docs/MULTI_AGENT.md](docs/MULTI_AGENT.md) | PostgreSQL multi-agent |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Variables `.env` |
| [docs/DEPLOIEMENT.md](docs/DEPLOIEMENT.md) | **Déploiement VPS Docker** |
| **[docs/DEPLOIEMENT_STREAMLIT_CLOUD.md](docs/DEPLOIEMENT_STREAMLIT_CLOUD.md)** | **★ Streamlit Community Cloud** |
| [docs/DEPLOIEMENT_GCP.md](docs/DEPLOIEMENT_GCP.md) | Déploiement Google Cloud |
| [docs/DEPANNAGE.md](docs/DEPANNAGE.md) | Résolution de problèmes |

## Structure du projet

```
├── run_app.py          # Point d'entrée interface web
├── main.py             # Interface CLI (15 commandes)
├── docker-compose.yml      # Dev : PostgreSQL seul (port 5433)
├── docker-compose.prod.yml # Prod : app + Postgres + Caddy
├── Dockerfile              # Image Streamlit
├── app.py              # Streamlit (8 pages)
├── docs/               # Documentation
├── data/documents/     # Sources officielles
├── data/vectorstore/   # Index ChromaDB
└── src/                # Code source
```

## Problème ?

1. `python diagnose.py`
2. [docs/DEPANNAGE.md](docs/DEPANNAGE.md)
3. Streamlit → **Tester connexion OpenAI** → **Recharger l'agent**

## Licence

MIT
