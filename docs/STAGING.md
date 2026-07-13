# France Civique IA — Staging

> Une question sur la citoyenneté ? **DocIA** répond à partir des sources officielles — Constitution, élections, justice, test civique — avec les textes et les citations.

**Branche :** `main` — staging cloud (Streamlit) + VPS Hetzner (prévu) · **Repo :** [Doc-IA-justice-constitution-election](https://github.com/abdouahim5/Doc-IA-justice-constitution-election)

> 📄 Résumé projet : [PROJET_DETAILS.md](../PROJET_DETAILS.md) (section Staging)

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

## Agents déployés (Phase 3 — LangGraph)

| Agent | Domaine | Outils LangChain |
|-------|---------|------------------|
| `constitution` | Droit constitutionnel | `search_constitution` |
| `elections` | Scrutins, calendrier | `search_elections` |
| `justice` | Lois, délits, crimes | `search_justice` |
| `test_civique` | Naturalisation | `search_test_civique` |
| `data` | Chiffres officiels | faits + tableaux PG |
| `general` | Fallback | `search_all_corpus` |

Orchestration : **LangGraph** (`validate → cache → route → agent → save_cache`)

---

## Staging local (Windows)

```powershell
demarrer_staging.bat
# ou : docker compose -f docker-compose.staging.yml up -d
```

---

## Staging Streamlit Cloud

| | |
|---|---|
| **URL** | https://doc-ia-justice-constitution-election-ejwpemdaupg3flgtrgziax.streamlit.app |
| **Entrée** | `app.py` |
| **Base** | Neon PostgreSQL (sync civique `--civic`) |
| **Secrets** | `OPENAI_API_KEY`, `DATABASE_URL`, `EMBEDDING_PROVIDER=openai` |

Guide : [DEPLOIEMENT_STREAMLIT_CLOUD.md](DEPLOIEMENT_STREAMLIT_CLOUD.md)

---

## Déployer / mettre à jour le staging

```bash
git clone https://github.com/abdouahim5/Doc-IA-justice-constitution-election.git
cd Doc-IA-justice-constitution-election
cp .env.production.example .env
nano .env   # OPENAI_API_KEY, POSTGRES_PASSWORD, DOMAIN (si HTTPS)

docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec app python main.py pg-ingest
docker compose -f docker-compose.prod.yml exec app python main.py index
```

**HTTPS (Caddy + Let's Encrypt) :**
```bash
docker compose -f docker-compose.prod.yml --profile https up -d --build
```

**Mise à jour après `git push` :**
```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
py scripts/update_staging_status.py   # rafraîchir métriques README
git add README.md docs/STAGING.md deploy/staging.metrics.json
git commit -m "Mise à jour métriques staging"
git push
```

---

## Configurer les URLs après déploiement

1. Copier `deploy/staging.env.example` → `deploy/staging.env`
2. Remplir :

```env
STAGING_IP=65.109.143.85
STAGING_DOMAIN=docia.example.fr
STAGING_STATUS=en_ligne
STAGING_URL_APP=https://docia.example.fr
STAGING_URL_HEALTH=https://docia.example.fr/_stcore/health
```

3. Lancer `py scripts/update_staging_status.py`

---

## Commandes utiles (VPS)

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f app
docker compose -f docker-compose.prod.yml exec app python main.py pg-stats
docker compose -f docker-compose.prod.yml exec app python main.py pg-cache-clear
```

Guide complet : [DEPLOIEMENT.md](DEPLOIEMENT.md)
