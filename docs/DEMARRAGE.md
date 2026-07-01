# Démarrage de l'application

## Règle d'or

| Fichier | Lancer avec Play ▶ ? |
|---------|----------------------|
| `run_app.py` | **OUI** (interface web) |
| `demarrer.bat` | **OUI** (double-clic) |
| `main.py` | **OUI** (CLI, avec arguments) |
| `diagnose.py` | **OUI** (diagnostic) |
| `app.py` | **NON** (module Streamlit, pas un script autonome) |

## Interface web (Streamlit)

### Méthode 1 — Fichier batch (le plus simple)

Double-cliquez sur `demarrer.bat`.

### Méthode 2 — Terminal

```powershell
cd "C:\Users\PC\Desktop\Agent IA stucture doc"
venv\Scripts\activate
python run_app.py
```

Ouvrez : **http://localhost:8501**

### Méthode 3 — Cursor / VS Code

1. Ouvrez **`run_app.py`**
2. Menu **Run and Debug** (F5)
3. Choisissez **« Agent RAG - Interface web »**

Configuration dans `.vscode/launch.json` :

```json
{
  "name": "Agent RAG - Interface web",
  "program": "${workspaceFolder}/run_app.py"
}
```

### Après le démarrage (Streamlit)

1. **Tester connexion OpenAI** (barre latérale)
2. **Recharger l'agent** si vous avez modifié `.env`
3. **Indexer les documents** si `Chunks indexés = 0`
4. Posez vos questions dans le chat

## Ligne de commande (CLI)

```powershell
venv\Scripts\activate

python main.py index              # Indexer les documents
python main.py chat               # Conversation interactive
python main.py ask "article 2"    # Question unique
python main.py search president  # Recherche mot exact
python main.py stats              # Statistiques
python main.py clear              # Supprimer l'index
python diagnose.py                # Diagnostic complet
```

### Mode chat — raccourcis

| Commande | Action |
|----------|--------|
| `quit` / `q` | Quitter |
| `clear` | Effacer la mémoire conversationnelle |

## Arrêter Streamlit

Dans le terminal : **Ctrl+C**

Un simple rafraîchissement du navigateur **ne recharge pas** le code Python.
Après une modification du code, arrêtez et relancez `python run_app.py`.

## Ordre de démarrage recommandé

```
1. pip install -r requirements.txt
2. copy .env.example .env  →  éditer la clé API
3. python diagnose.py      →  doit afficher OK
4. python main.py index    →  indexer les documents
5. python run_app.py       →  interface web
```
