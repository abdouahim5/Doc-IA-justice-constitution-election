# Architecture technique

> Documentation complète : [PROJET_COMPLET.md](PROJET_COMPLET.md)

## Vue d'ensemble — double stack

```
Utilisateur
    │
    ├── run_app.py → app.py (Streamlit, 8 pages)
    ├── main.py (CLI, 15 commandes)
    └── diagnose.py
              │
    ┌─────────┴─────────┐
    ▼                   ▼
MultiAgentOrchestrator  RAGAgent
(PostgreSQL pgvector)   (ChromaDB local)
    │                   │
    6 agents            HybridRetriever
    │                   (BM25 + vecteurs)
    ▼                   ▼
CorpusRepository      VectorStoreManager
    │                   │
    ▼                   ▼
PostgreSQL            data/vectorstore/
    │
    ▼
OpenAI / Ollama
```

L'interface web tente **PostgreSQL en priorité** ; si Docker est arrêté, elle bascule sur **Chroma RAG**.

---

## Structure des fichiers

```
src/
├── startup.py              # SSL Windows — IMPORTER EN PREMIER
├── config.py               # .env, FAST_MODE, réglages RAG/multi-agent
├── http_clients.py         # httpx + certifi
├── diagnostics.py          # Tests OpenAI
├── errors.py               # Messages utilisateur
│
├── ingestion/
│   ├── document_loader.py  # PDF, TXT, MD, DOCX
│   ├── chunker.py          # Découpage + articles juridiques
│   ├── classifier.py       # Routage questions + catégories fichiers
│   ├── pg_pipeline.py      # Ingestion PostgreSQL
│   └── table_extractor.py  # Tableaux PDF + faits chiffrés
│
├── retrieval/
│   ├── vector_store.py     # ChromaDB + embeddings (OpenAI/local/tfidf)
│   └── hybrid_retriever.py # BM25 + sémantique + articles
│
├── agent/
│   └── rag_agent.py        # Chaînes LangChain, mémoire conversation
│
├── db/
│   ├── engine.py           # SQLAlchemy, init_db, check_connection
│   ├── models.py           # ORM (Source, DocumentChunk, QueryCache…)
│   └── repository.py       # Recherche vectorielle, trigram, cache
│
├── multi_agent/
│   ├── orchestrator.py     # Routage, cache, ask()
│   ├── agents.py           # 6 agents spécialisés
│   └── conversation.py     # Historique, thèmes, suivis
│
├── scraping/               # Sources officielles FR
├── civic_test/             # Quiz intégré (hors RAG)
├── llm/provider.py         # ChatOpenAI / ChatOllama
└── ui/                     # Streamlit : sidebar, thèmes, i18n
```

---

## Flux multi-agent (PostgreSQL)

```
1. Question (+ historique + thème actif)
        │
2. query_cache hit ? → réponse instantanée
        │
3. resolve_topic() → constitution | elections | justice | test_civique | data | general
        │
4. enrich_search_query() + enrich_with_history()
        │
5. Agent.retrieve()
   ├── search_vector (cosine pgvector)
   ├── search_text (pg_trgm)
   └── search_chunks_patterns (articles, dates, pénal…)
        │
6. Agent.run() → LLM + prompt strict + historique
        │
7. Mise en cache (si réponse valide)
```

### Agents et recherches spéciales

| Agent | Recherche dédiée |
|-------|------------------|
| `ConstitutionAgent` | Articles (`ARTICLE N.`), éligibilité président |
| `ElectionsAgent` | Patterns dates, calendrier |
| `JusticeAgent` | Patterns `%crime%`, `%délit%`, `%viol%` en parallèle |
| `DataAgent` | `structured_facts` + `extracted_tables` |
| `TestCiviqueAgent` | Corpus `test_civique` |
| `GeneralAgent` | Tout le corpus |

---

## Flux RAG (ChromaDB)

```
1. Question utilisateur
        │
2. Type de requête
   ├── Article ("article 5")     → _article_rag_chain
   ├── Mot exact ("laïcité")     → _word_rag_chain
   └── Question générale         → _rag_chain + historique
        │
3. _contextualize_question() si suivi
        │
4. HybridRetriever
   ├── BM25 (mots, articles numérotés)
   └── Vecteurs Chroma (sémantique)
        │
5. _check_relevance() (score minimum)
        │
6. LLM → réponse + sources
        │
7. Mise à jour _chat_history
```

---

## Base de données

Voir `sql/schema.sql` et [PROJET_COMPLET.md §8](PROJET_COMPLET.md#8-base-de-données-postgresql).

```
sources ──< document_chunks (embedding vector 1536)
        ──< extracted_tables
        ──< structured_facts

query_cache (question_hash → answer)
v_corpus_stats (vue agrégée)
```

**Docker** : port hôte `5433`, user `docia`, DB `docia_fr`.

---

## Interface Streamlit

| Page | Fonction |
|------|----------|
| `accueil` | Dashboard |
| `chat` | Chat PG + fallback RAG |
| `france` | Multi-agent dédié |
| `themes` / `theme_explore` | Exploration par domaine |
| `test_civique` | Quiz (contenu local) |
| `admin` | Index, scrape, PG, diagnostic |

État session : `messages`, `active_theme`, `france_messages`, `pending_question`.

---

## Chaînes LangChain (RAG)

| Chaîne | Fichier | Usage |
|--------|---------|-------|
| `_rag_chain` | `rag_agent.py` | QA générale |
| `_article_rag_chain` | `rag_agent.py` | Texte article exact |
| `_word_rag_chain` | `rag_agent.py` | Mot isolé |

Multi-agent : prompts dans `agents.py` (`SYSTEM_CONSTITUTION`, `SYSTEM_JUSTICE`…).

---

## Sécurité

- Secrets dans `.env` uniquement
- SSL explicite (`startup.py`, `certifi`, `truststore`)
- Prompts : pas de connaissance externe, citations `[fichier]`
- Cache : pas de stockage des réponses extractives obsolètes

---

## Points d'entrée

| Fichier | Usage |
|---------|-------|
| `run_app.py` | **Lancer l'interface web** |
| `main.py` | CLI |
| `app.py` | Ne pas lancer directement |
| `docker compose up -d` | PostgreSQL |
