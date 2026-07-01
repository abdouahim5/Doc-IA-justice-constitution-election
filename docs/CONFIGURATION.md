# Configuration (.env)

Toutes les variables sont lues depuis le fichier `.env` à la racine du projet.
Le module `src/config.py` les recharge à chaque appel (`reload_env()`).

## LLM — modèle de langage

| Variable | Défaut | Description |
|----------|--------|-------------|
| `LLM_PROVIDER` | `openai` | `openai` ou `ollama` |
| `OPENAI_API_KEY` | — | Clé API OpenAI (`sk-...`) |
| `OPENAI_MODEL` | `gpt-4o-mini` | Modèle chat OpenAI |
| `OPENAI_MAX_TOKENS` | `600` | Longueur max des réponses |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL du serveur Ollama |
| `OLLAMA_MODEL` | `llama3.2` | Modèle Ollama |
| `OLLAMA_NUM_PREDICT` | `350` | Tokens max générés (Ollama) |
| `OLLAMA_NUM_CTX` | `2048` | Taille du contexte (Ollama) |
| `TEMPERATURE` | `0` | Créativité (0 = factuel, 1 = créatif) |

## Embeddings — représentation vectorielle

| Variable | Défaut | Description |
|----------|--------|-------------|
| `EMBEDDING_PROVIDER` | `tfidf` | `openai`, `local`, `tfidf` |
| `EMBEDDING_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | Modèle HuggingFace si `local` |

**Important** : si vous changez `EMBEDDING_PROVIDER`, réindexez :

```powershell
python main.py clear
python main.py index
```

Chaque fournisseur utilise une collection Chroma distincte (`rag_openai`, `rag_tfidf`, etc.).

## RAG — recherche documentaire

| Variable | Défaut | Description |
|----------|--------|-------------|
| `CHUNK_SIZE` | `500` | Taille des morceaux de texte (caractères) |
| `CHUNK_OVERLAP` | `100` | Chevauchement entre chunks |
| `TOP_K_RESULTS` | `6` | Passages envoyés au LLM |
| `RETRIEVAL_CANDIDATES` | `15` | Candidats avant filtrage |
| `SCORE_THRESHOLD` | `0.12` | Seuil BM25/hybride minimum |
| `MIN_RELEVANCE_SCORE` | `0.18` | Seuil de pertinence avant réponse |
| `FAST_MODE` | `true` | Mode rapide (recherche directe) |

## Conversation

| Variable | Défaut | Description |
|----------|--------|-------------|
| `CONVERSATION_HISTORY_TURNS` | `6` | Messages gardés en mémoire (3 échanges) |

## Chemins

| Variable | Défaut | Description |
|----------|--------|-------------|
| `DOCUMENTS_DIR` | `./data/documents` | Fichiers source |
| `VECTOR_STORE_DIR` | `./data/vectorstore` | Index ChromaDB |

## Profils recommandés

### Qualité maximale (OpenAI)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
EMBEDDING_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
TOP_K_RESULTS=6
```

### 100 % hors ligne

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
EMBEDDING_PROVIDER=tfidf
```

### Documents juridiques (Constitution, etc.)

```env
CHUNK_SIZE=800
CHUNK_OVERLAP=120
TOP_K_RESULTS=6
MIN_RELEVANCE_SCORE=0.18
```
