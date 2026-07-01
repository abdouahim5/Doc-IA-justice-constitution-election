# France Civique IA — Staging

> Une question sur la citoyenneté ? **DocIA** répond à partir des sources officielles — Constitution, élections, justice, test civique — avec les textes et les citations.

**Branche :** `main` — environnement de staging à déployer sur Hetzner · [Détails staging](docs/STAGING.md)

## Environnement déployé

| | |
|---|---|
| **Serveur** | Hetzner CX22 — Ubuntu 24.04 |
| **IP** | `—` *(à compléter après déploiement)* |
| **Stack** | Docker Compose (caddy + app + postgres pgvector) |
| **Statut** | 🟡 En attente de déploiement |

| Interface | URL |
|-----------|-----|
| **Application** | `http://IP_OU_DOMAINE` |
| **France Civique** | `http://IP_OU_DOMAINE` → menu *France Civique* |
| **Test civique** | `http://IP_OU_DOMAINE` → menu *Test civique* |
| **Health** | `http://IP_OU_DOMAINE/_stcore/health` |

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
| **[docs/STAGING.md](docs/STAGING.md)** | **Environnement staging (URLs, statut, mise à jour)** |
| **[docs/PROJET_COMPLET.md](docs/PROJET_COMPLET.md)** | **★ Tout le projet : architecture, flux, agents, BDD** |
| [docs/README.md](docs/README.md) | Index documentation |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Schémas techniques |
| [docs/MULTI_AGENT.md](docs/MULTI_AGENT.md) | PostgreSQL multi-agent |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Variables `.env` |
| [docs/DEPLOIEMENT.md](docs/DEPLOIEMENT.md) | **Déploiement VPS Docker** |
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
