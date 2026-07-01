# Référence des commandes

## CLI — `main.py`

```powershell
python main.py <commande> [arguments]
```

| Commande | Syntaxe | Description |
|----------|---------|-------------|
| `index` | `python main.py index` | Indexe `data/documents/` |
| `index` | `python main.py index --dir ./mes_docs` | Indexe un dossier personnalisé |
| `chat` | `python main.py chat` | Conversation interactive |
| `ask` | `python main.py ask "question"` | Une question, une réponse |
| `search` | `python main.py search mot` | Recherche mot exact dans les docs |
| `stats` | `python main.py stats` | Chunks indexés, config LLM |
| `clear` | `python main.py clear` | Supprime l'index vectoriel |
| `pg-init` | `python main.py pg-init` | Crée tables PostgreSQL + extensions |
| `pg-ingest` | `python main.py pg-ingest` | Ingère docs (texte, tableaux, chiffres) |
| `pg-ingest` | `python main.py pg-ingest --dir ./docs` | Ingestion depuis un dossier |
| `pg-stats` | `python main.py pg-stats` | Statistiques corpus PostgreSQL |
| `multi-ask` | `python main.py multi-ask "question"` | Question multi-agent France |
| `multi-ask` | `python main.py multi-ask "..." --no-cache` | Sans cache instantané |
| `multi-chat` | `python main.py multi-chat` | Chat multi-agent interactif |
| `scrape` | `python main.py scrape` | Télécharger sources officielles FR |
| `scrape` | `python main.py scrape --ingest` | Télécharger + PostgreSQL |
| `docker-install` | `python main.py docker-install --launch` | Installer Docker Desktop |

Voir aussi [MULTI_AGENT.md](MULTI_AGENT.md) pour l'architecture PostgreSQL.

### Exemples

```powershell
python main.py index
python main.py ask "article 2"
python main.py ask "Quels sont les droits du president"
python main.py search Marseillaise
python main.py search president
python main.py chat

# Multi-agent France (PostgreSQL)
docker compose up -d
python main.py pg-init
python main.py pg-ingest
python main.py multi-ask "Que dit l'article 2 ?"
python main.py multi-chat
```

### Mode `chat`

| Entrée | Action |
|--------|--------|
| Votre question | Envoi à l'agent |
| `clear` | Efface la mémoire |
| `quit` / `q` / `exit` | Quitte |

---

## Diagnostic — `diagnose.py`

```powershell
python diagnose.py
```

Affiche :
- Configuration LLM et embeddings
- Test SSL vers OpenAI
- Test LLM + embeddings
- Liste des documents
- État de l'index ChromaDB

Code de sortie `1` si échec.

---

## Interface web — `run_app.py`

```powershell
python run_app.py
```

URL : http://localhost:8501

### Barre latérale

| Bouton | Action |
|--------|--------|
| Tester connexion OpenAI | Test SSL + API |
| Diagnostic complet | Rapport texte |
| Recharger l'agent | Nouvelle instance (après .env) |
| Enregistrer les fichiers | Sauvegarde uploads |
| Indexer les documents | Crée l'index ChromaDB |
| Supprimer l'index | Efface `data/vectorstore/` |
| Effacer la conversation | Reset mémoire chat |

### Zone principale

- Chat multi-tours avec sources
- Avertissement si index vide

---

## Types de questions reconnus

| Type | Exemple | Comportement |
|------|---------|--------------|
| Article | `article 2`, `art. 5` | Recherche article précis |
| Mot exact | `president`, `Marseillaise` | Recherche littérale |
| Question | `Quels sont les droits du president ?` | RAG + historique |
| Suivi | `et l'article 3 ?` | Contexte conversationnel |

---

## Fichiers batch

| Fichier | Commande équivalente |
|---------|---------------------|
| `demarrer.bat` | `venv\Scripts\activate` + `python run_app.py` |

---

## Debug VS Code / Cursor

Configurations dans `.vscode/launch.json` :

| Nom | Script | Args |
|-----|--------|------|
| Agent RAG - Interface web | `run_app.py` | — |
| Agent RAG - Indexer documents | `main.py` | `index` |
| Agent RAG - Chat CLI | `main.py` | `chat` |
