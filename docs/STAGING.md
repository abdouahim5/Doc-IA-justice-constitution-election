# France Civique IA — Staging

> Une question sur la citoyenneté ? **DocIA** répond à partir des sources officielles — Constitution, élections, justice, test civique — avec les textes et les citations.

**Branche :** `main` — environnement de staging à déployer sur Hetzner · **Repo :** [Doc-IA-justice-constitution-election](https://github.com/abdouahim5/Doc-IA-justice-constitution-election)

<!-- STAGING:AUTO:START -->
**Dernière mise à jour :** 2026-07-01 13:40 UTC · Branche `main` · [Détails complets](docs/STAGING.md)

## Environnement déployé

| | |
|---|---|
| **Serveur** | Hetzner CX22 — Ubuntu 24.04 |
| **IP** | `—` |
| **Domaine** | `—` |
| **Stack** | Docker Compose (caddy + app Streamlit + postgres pgvector) |
| **Statut** | 🟡 En attente de déploiement |

| Interface | URL |
|-----------|-----|
| **Application** | http://IP_OU_DOMAINE |
| **France Civique** (multi-agent) | http://IP_OU_DOMAINE → menu *France Civique* |
| **Test civique** | http://IP_OU_DOMAINE → menu *Test civique* |
| **Admin / diagnostic** | http://IP_OU_DOMAINE → menu *Configuration* |
| **Health** | http://IP_OU_DOMAINE/_stcore/health |

## État du déploiement

| Métrique | Valeur |
|----------|--------|
| **Chunks indexés** | — *(lancer `pg-ingest`)* |
| **Sources actives** | 220 fichiers *(PG après ingestion)* `████████████` 100% |
| **Par catégorie** | constitution 9 · élections 35 · justice 146 · test civique 24 |
| **Phase déployée** | Phase 2 — Multi-Agents (6 agents) |
| **Modèle routing** | `Classifier hybride (mots-clés + historique + thème)` |
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
                   MultiAgentOrchestrator
                             │
              ┌──────────────┴──────────────┐
              │  Classifier + resolve_topic  │
              │  (historique · thème actif)    │
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

## Agents déployés (Phase 2)

| Agent | Domaine | Recherche spécialisée |
|-------|---------|----------------------|
| `constitution` | Droit constitutionnel | Articles `ARTICLE N.`, éligibilité président |
| `elections` | Scrutins, calendrier | Dates, résultats, patterns électoraux |
| `justice` | Lois, délits, crimes | Patterns pénaux, crawler service-public |
| `test_civique` | Naturalisation | Formation civique, examen |
| `data` | Chiffres officiels | `structured_facts`, tableaux PDF |
| `general` | Fallback | Tout le corpus |

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
