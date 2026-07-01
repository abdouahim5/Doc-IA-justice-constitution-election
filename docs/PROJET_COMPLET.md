# France Civique IA (DocIA) — Documentation complète du projet

Application **multi-agent RAG** pour interroger des sources officielles françaises : Constitution, élections, justice, test civique. Interface **Streamlit**, stockage **PostgreSQL + pgvector**, index local **ChromaDB** en secours.

---

## 1. Objectif et périmètre

| Objectif | Détail |
|----------|--------|
| Répondre en français | À partir des documents indexés uniquement (pas d'invention) |
| Sources officielles | Conseil constitutionnel, service-public, Légifrance, INSEE, data.gouv.fr, justice.gouv.fr, formation civique |
| Modes d'usage | Interface web, CLI, chat multi-agent, exploration par thèmes |
| Public cible | Préparation test civique, recherche institutionnelle, assistant documentaire |

---

## 2. Architecture globale (double stack)

Le projet combine **deux moteurs de recherche** :

```mermaid
flowchart TB
    subgraph UI [Interface utilisateur]
        ST[Streamlit app.py]
        CLI[main.py CLI]
    end

    subgraph MoteurPG [Stack principal — PostgreSQL]
        ORCH[MultiAgentOrchestrator]
        AGENTS[6 agents spécialisés]
        REPO[CorpusRepository]
        PG[(PostgreSQL pgvector)]
        CACHE[query_cache]
    end

    subgraph MoteurRAG [Stack secours — ChromaDB]
        RAG[RAGAgent]
        HYB[HybridRetriever BM25+vecteurs]
        CHROMA[(ChromaDB local)]
    end

    subgraph Externe [Services externes]
        OAI[OpenAI API]
        OLL[Ollama optionnel]
    end

    ST --> ORCH
    ST --> RAG
    CLI --> ORCH
    CLI --> RAG

    ORCH --> CACHE
    ORCH --> AGENTS --> REPO --> PG
    AGENTS --> OAI
    AGENTS --> OLL

    RAG --> HYB --> CHROMA
    RAG --> OAI

    ORCH -.->|si PG indisponible| RAG
```

### Quand quel moteur est utilisé ?

| Contexte | Moteur | Condition |
|----------|--------|-----------|
| Page **Chat**, **France Civique**, **Exploration thème** | PostgreSQL multi-agent | Docker Postgres joignable (`localhost:5433`) |
| Même pages, PG down | Chroma RAG | Fallback automatique dans `app.py` |
| `main.py index` / `chat` / `ask` | Chroma RAG | Toujours |
| `main.py multi-ask` / `multi-chat` | PostgreSQL | Connexion PG requise |

---

## 3. Structure du projet

```
Agent IA stucture doc/
├── run_app.py              # ★ Point d'entrée web (lancer celui-ci)
├── app.py                  # Interface Streamlit (8 pages)
├── main.py                 # CLI (15 commandes)
├── diagnose.py             # Diagnostic SSL + OpenAI + index
├── docker-compose.yml      # PostgreSQL pgvector (port 5433)
├── sql/schema.sql          # Schéma base (auto-chargé au 1er démarrage Docker)
├── requirements.txt
├── .env / .env.example
│
├── data/
│   ├── documents/          # Sources (PDF, TXT, MD, DOCX)
│   │   └── sources_officielles/
│   │       ├── constitution, elections, justice, test_civique…
│   │       └── manifest.json
│   └── vectorstore/        # Index ChromaDB (généré)
│
├── docs/                   # Documentation
├── scripts/                # Utilitaires (calendrier, tests agents)
│
└── src/
    ├── config.py           # Variables .env, FAST_MODE, réglages RAG/multi-agent
    ├── startup.py          # SSL Windows (importer en premier)
    ├── ingestion/          # Chargement, chunking, classification, pg-ingest
    ├── retrieval/            # Chroma + HybridRetriever (BM25 + sémantique)
    ├── agent/                # RAGAgent (chaînes LangChain)
    ├── db/                   # SQLAlchemy, CorpusRepository, modèles
    ├── multi_agent/          # Orchestrateur + 6 agents + conversation
    ├── scraping/             # Téléchargement sources officielles FR
    ├── civic_test/           # Quiz / examen blanc (contenu intégré)
    ├── llm/                  # OpenAI / Ollama
    └── ui/                   # Sidebar, thèmes, i18n FR/EN
```

---

## 4. Flux de données détaillé

### 4.1 Collecte des documents

```
Sites officiels (scraping)
        │
        ▼
src/scraping/runner.py → scrape_all()
        │
        ├── sources.py          (constitution, elections)
        ├── justice_sources.py  + justice_crawler.py
        ├── civic_test_sources.py + civic_crawler.py
        └── datagouv.py           (CSV résultats électoraux)
        │
        ▼
data/documents/sources_officielles/
```

Commande : `python main.py scrape [--category X] [--ingest]`

### 4.2 Ingestion PostgreSQL (stack principal)

```
Fichiers sources
        │
        ▼
document_loader.py  →  Document LangChain (chemin relatif en metadata)
        │
        ▼
classifier.py  →  category: constitution | elections | justice | test_civique | general
        │
        ▼
pg_pipeline.py  →  ingest_directory()
        │
        ├── sources              (1 ligne / fichier)
        ├── document_chunks      (texte + embedding 1536)
        ├── extracted_tables     (PDF via pdfplumber)
        └── structured_facts     (chiffres extraits)
```

Commandes : `python main.py pg-init` puis `python main.py pg-ingest`

### 4.3 Ingestion ChromaDB (stack secours)

```
document_loader → chunker → embeddings → VectorStoreManager (Chroma)
```

Commande : `python main.py index`

### 4.4 Traitement d'une question (multi-agent)

```
Question utilisateur
        │
        ▼
classify_question() + resolve_topic()  (historique + thème actif)
        │
        ▼
query_cache ?  ──hit──►  réponse instantanée
        │
        miss
        │
        ▼
Agent spécialisé (Constitution, Élections, Justice…)
        │
        ├── retrieve() : vecteurs PG + ILIKE + patterns (articles, dates, pénal…)
        └── run() : LLM + prompt strict + historique conversation
        │
        ▼
Réponse + sources  →  mise en cache (si qualité OK)
```

### 4.5 Traitement d'une question (RAG Chroma)

```
RAGAgent.query()
        │
        ├── Détection : article | mot exact | question générale
        ├── Contextualisation si suivi conversationnel
        ├── HybridRetriever (BM25 + vecteurs Chroma)
        ├── Vérification score de pertinence
        └── LLM + citations
```

---

## 5. Interface Streamlit (`app.py`)

| Page | Clé | Rôle |
|------|-----|------|
| Accueil | `accueil` | Hero, statistiques corpus |
| Poser une question | `chat` | Chat général (PG puis fallback RAG) |
| France Civique | `france` | Multi-agent dédié + stats PG |
| Thèmes | `themes` | Grille des 7 domaines |
| Exploration thème | `theme_explore` | Conversation guidée + suggestions de suite |
| Test civique | `test_civique` | Cours, quiz, examen blanc (hors RAG) |
| FAQ | `faq` | Aide |
| Configuration | `admin` | Upload, index, scrape, PG, diagnostic |

### Thèmes d'exploration

| ID | Domaine | Agent routé |
|----|---------|-------------|
| `constitution` | Constitution | `constitution` |
| `elections` | Élections | `elections` |
| `justice` | Justice & Droit | `justice` |
| `institutions` | Institutions | `constitution` |
| `calendrier` | Calendrier électoral | `elections` |
| `chiffres` | Chiffres & résultats | `data` |
| `citoyennete` | Citoyenneté / vote | `elections` |

### Mémoire conversationnelle (interface)

- Messages stockés dans `st.session_state.messages`
- Historique transmis au multi-agent (`format_history`)
- Thème actif (`active_theme`) pour les questions de suite
- Synchronisation RAG : `agent.restore_conversation()`

---

## 6. Multi-agent — agents spécialisés

Fichier : `src/multi_agent/agents.py`

| Clé | Classe | Catégorie PG | Spécialités |
|-----|--------|--------------|-------------|
| `constitution` | `ConstitutionAgent` | `constitution` | Articles (recherche ciblée), éligibilité président |
| `elections` | `ElectionsAgent` | `elections` | Dates, calendrier, patterns électoraux |
| `justice` | `JusticeAgent` | `justice` | Crimes, délits, lois, patterns pénaux parallèles |
| `test_civique` | `TestCiviqueAgent` | `test_civique` | Formation civique, naturalisation |
| `data` | `DataAgent` | — | Faits chiffrés, tableaux (`structured_facts`) |
| `general` | `GeneralAgent` | — | Fallback tout corpus |

### Routage (`src/ingestion/classifier.py`)

- Mots-clés par domaine (constitution, elections, justice, test_civique)
- Mots isolés : `vote` → elections, `crime` → justice, `president` → constitution
- Regex `article N` → constitution (sauf code pénal/civil)
- `resolve_topic()` : thème épinglé + détection de suivi (`et l'article 3 ?`)

### Cache (`query_cache`)

- Hash SHA-256 de la question normalisée
- Bypass si historique conversation ou réponse extractive obsolète
- Commande : `python main.py pg-cache-clear`

### Modes de performance (`FAST_MODE=true`)

| Paramètre | Effet |
|-----------|-------|
| `text_only` | Recherche ILIKE sans appel embedding (sauf articles) |
| `extractive` | Désactivé (réponses en phrases via LLM) |
| `max_chunks` | 3 au lieu de 5 |
| `max_tokens` | 250 au lieu de 400 |

---

## 7. RAG local (ChromaDB)

Fichier : `src/agent/rag_agent.py`

| Chaîne LangChain | Usage |
|------------------|-------|
| `_rag_chain` | Questions générales + historique |
| `_article_rag_chain` | Articles juridiques (texte exact) |
| `_word_rag_chain` | Recherche mot exact (`laïcité`, `vote`) |

**HybridRetriever** (`src/retrieval/hybrid_retriever.py`) :
- BM25 + similarité vectorielle
- Détection articles numérotés (`_doc_has_article`)
- Expansion synonymes (`président` → pouvoirs, attributions)
- Score minimum de pertinence configurable

**Embeddings** (`EMBEDDING_PROVIDER`) :
- `openai` — text-embedding-3-small (1536 dim, aligné PG)
- `local` — HuggingFace multilingue
- `tfidf` — hors ligne, sans API

---

## 8. Base de données PostgreSQL

### Connexion Docker

| Paramètre | Valeur |
|-----------|--------|
| Image | `pgvector/pgvector:pg16` |
| Container | `docia-postgres` |
| Port hôte | **5433** → 5432 |
| User / Password / DB | `docia` / `docia_secret` / `docia_fr` |
| URL | `postgresql+psycopg://docia:docia_secret@localhost:5433/docia_fr` |

### Tables

| Table | Rôle |
|-------|------|
| `sources` | Fichiers indexés + catégorie + metadata JSONB |
| `document_chunks` | Morceaux de texte + `embedding vector(1536)` |
| `extracted_tables` | Tableaux PDF (headers/rows JSONB) |
| `structured_facts` | Faits chiffrés (clé, valeur, unité, contexte) |
| `query_cache` | Réponses mises en cache |
| `v_corpus_stats` | Vue agrégée (compteurs par catégorie) |

### Extensions

- `vector` — recherche cosine IVFFlat
- `pg_trgm` — recherche full-text floue (ILIKE, similarity)

### Requêtes utiles

```sql
-- Stats globales
SELECT * FROM v_corpus_stats;

-- Documents justice
SELECT filename, category FROM sources WHERE category = 'justice' LIMIT 20;

-- Vider le cache
DELETE FROM query_cache;
```

---

## 9. Scraping des sources officielles

| Catégorie | Fichiers principaux | Sources web |
|-----------|---------------------|-------------|
| `constitution` | `sources.py` | conseil-constitutionnel.fr, vie-publique.fr |
| `elections` | `sources.py`, `datagouv.py` | service-public, INSEE, intérieur.gouv.fr |
| `justice` | `justice_sources.py`, `justice_crawler.py` | justice.gouv.fr, service-public F* |
| `test_civique` | `civic_test_sources.py`, `civic_crawler.py` | formation-civique.interieur.gouv.fr |

Manifeste : `data/documents/sources_officielles/manifest.json`

---

## 10. Configuration (`.env`)

### Indispensable (mode cloud)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
EMBEDDING_PROVIDER=openai
DATABASE_URL=postgresql+psycopg://docia:docia_secret@localhost:5433/docia_fr
```

### Optionnel

| Variable | Défaut | Description |
|----------|--------|-------------|
| `OPENAI_MODEL` | `gpt-4o-mini` | Modèle chat |
| `OPENAI_MAX_TOKENS` | 250–400 | Longueur réponses |
| `FAST_MODE` | `true` | Mode rapide (moins de chunks) |
| `MIN_RELEVANCE_SCORE` | `0.18` | Seuil pertinence RAG Chroma |
| `CONVERSATION_HISTORY_TURNS` | 4–6 | Tours d'historique |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | 500 / 100 | Découpage documents |
| `DOCUMENTS_DIR` | `./data/documents` | Dossier sources |
| `VECTOR_STORE_DIR` | `./data/vectorstore` | Index Chroma |
| `OLLAMA_*` | — | LLM local gratuit |
| `TEXT_ONLY_SEARCH` | — | Force ILIKE sans embedding PG |

Voir [CONFIGURATION.md](CONFIGURATION.md) pour le détail complet.

---

## 11. Commandes CLI (`main.py`)

| Commande | Description |
|----------|-------------|
| `index [--dir]` | Indexer dans ChromaDB |
| `chat` | Conversation RAG interactive |
| `ask "question"` | Une question RAG |
| `search mot` | Recherche mot exact dans Chroma |
| `stats` | Stats Chroma + LLM |
| `clear` | Supprimer index Chroma |
| `pg-init` | Créer tables PostgreSQL |
| `pg-ingest [--dir] [--justice-only]` | Ingérer dans PostgreSQL |
| `pg-stats` | Statistiques corpus PG |
| `pg-cache-clear [--question]` | Vider cache réponses |
| `multi-ask "question" [--no-cache]` | Question multi-agent |
| `multi-chat` | Chat multi-agent interactif |
| `scrape [--category] [--ingest] [--light]` | Télécharger sources officielles |
| `docker-install [--launch]` | Aide installation Docker |

---

## 12. Démarrage complet (ordre recommandé)

```powershell
# 1. Environnement
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Éditer .env : OPENAI_API_KEY

# 2. PostgreSQL
docker compose up -d
python main.py pg-init

# 3. Sources + ingestion
python main.py scrape --ingest
# ou : python main.py pg-ingest

# 4. Index Chroma (secours)
python main.py index

# 5. Interface web
python run_app.py
# → http://localhost:8501
```

---

## 13. Déploiement

| Composant | Fichier |
|-----------|---------|
| Image app | `Dockerfile` |
| Stack production | `docker-compose.prod.yml` |
| HTTPS | `deploy/Caddyfile` (profil `--profile https`) |
| Guide complet | **[docs/DEPLOIEMENT.md](DEPLOIEMENT.md)** |

### Démarrage VPS (résumé)

```bash
cp .env.production.example .env   # éditer OPENAI_API_KEY + POSTGRES_PASSWORD
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec app python main.py pg-ingest
```

| Option | Détail |
|--------|--------|
| Ressources min | 2 vCPU, 4 Go RAM, 40 Go SSD |
| HTTPS | Caddy + Let's Encrypt (`DOMAIN` dans `.env`) |
| Secrets | Jamais committer `.env` |
| Auth publique | Basic auth Caddy ou VPN recommandé |

---

## 14. Sécurité

- Clé OpenAI **uniquement** dans `.env` (vérifier `.gitignore`)
- Régénérer la clé avant toute mise en production publique
- Ne pas exposer le port PostgreSQL (5433) sur Internet
- Ajouter une authentification devant Streamlit si déploiement public
- Prompts stricts : réponses limitées aux sources indexées

---

## 15. Dépendances principales

| Package | Rôle |
|---------|------|
| `streamlit` | Interface web |
| `langchain` + `langchain-openai` | Chaînes RAG + LLM |
| `chromadb` | Vector store local |
| `sqlalchemy` + `psycopg` + `pgvector` | PostgreSQL |
| `sentence-transformers` | Embeddings locaux |
| `rank-bm25` | Recherche lexicale |
| `pdfplumber` / `pypdf` | Extraction PDF |
| `beautifulsoup4` | Scraping HTML |

---

## 16. Documentation associée

| Fichier | Sujet |
|---------|-------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Schémas techniques détaillés |
| [MULTI_AGENT.md](MULTI_AGENT.md) | Multi-agent et PostgreSQL |
| [SCRAPING.md](SCRAPING.md) | Sources officielles |
| [CONFIGURATION.md](CONFIGURATION.md) | Variables `.env` |
| [COMMANDES.md](COMMANDES.md) | Référence CLI |
| [CONVERSATION.md](CONVERSATION.md) | Mémoire et suivis |
| [DEPLOIEMENT.md](DEPLOIEMENT.md) | Déploiement VPS Docker |
| [DEPANNAGE.md](DEPANNAGE.md) | Résolution de problèmes |
| [INSTALLATION.md](INSTALLATION.md) | Installation pas à pas |
| [DEMARRAGE.md](DEMARRAGE.md) | Lancement IDE / CLI |

---

## 17. Évolutions récentes (état actuel)

- Agent **justice** (141+ sources : crimes, délits, lois)
- Agent **test_civique** + page quiz intégrée
- Recherche **article N** ciblée (Constitution)
- Réponses en **phrases complètes** (extractif désactivé)
- **Exploration par thèmes** avec conversation continue
- Cache intelligent (ignore anciennes réponses extractives)
- Interface **bilingue** FR/EN (`src/ui/i18n.py`)
- **Déploiement Docker** : `Dockerfile`, `docker-compose.prod.yml`, HTTPS Caddy
