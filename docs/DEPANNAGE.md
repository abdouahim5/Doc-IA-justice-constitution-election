# Dépannage

## Diagnostic automatique

Toujours commencer par :

```powershell
venv\Scripts\activate
python diagnose.py
```

Résultat attendu :

```
SSL: OK
OpenAI: OK
Index ChromaDB valide: True
RESULTAT: OK
```

Dans Streamlit : boutons **« Tester connexion OpenAI »** et **« Diagnostic complet »**.

---

## Erreur SSL : `CERTIFICATE_VERIFY_FAILED`

**Message** :
```
APIConnectionError: Connection error.
cause -> ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Cause** : Windows ne valide pas les certificats HTTPS pour `httpx` (client OpenAI).

**Solutions** :

```powershell
pip install truststore certifi pip-system-certs
python run_app.py
```

**Ne pas utiliser** `streamlit run app.py` — utilisez `python run_app.py`.

Vérifiez que `src/startup.py` est chargé (automatique via `run_app.py`).

---

## Erreur : `Connexion OpenAI echouee`

**Causes possibles** :

| Cause | Vérification |
|-------|--------------|
| Clé API invalide | `OPENAI_API_KEY=sk-...` dans `.env` |
| Pas de `load_dotenv` | Utilisez `run_app.py` ou `main.py` |
| SSL (voir ci-dessus) | `python diagnose.py` |
| Quota dépassé | Message « Quota OpenAI depasse » |
| Agent en cache (Streamlit) | **Recharger l'agent** |

**Test manuel** :

```powershell
python -c "from dotenv import load_dotenv; load_dotenv('.env'); from src.diagnostics import test_openai_connection; print(test_openai_connection())"
```

---

## ImportError : `cannot import name '...' from 'src.config'`

**Cause** : Streamlit garde d'anciennes versions des modules en mémoire.

**Solutions** :

1. **Arrêter complètement** Streamlit (`Ctrl+C`)
2. Relancer : `python run_app.py`
3. Ne pas rafraîchir seulement le navigateur

Le fichier `app.py` recharge les modules `src.*` à chaque démarrage.

---

## `Chunks indexés = 0` ou index corrompu

**Symptômes** :
- Réponses « non présente dans les documents »
- Dossier `data/vectorstore/` sans `chroma.sqlite3`

**Solution** :

```powershell
python main.py clear
python main.py index
```

Puis dans Streamlit : **Recharger l'agent**.

---

## OpenAI OK en CLI mais pas dans Streamlit

1. Arrêtez Streamlit (`Ctrl+C`)
2. `python run_app.py` (pas Play sur `app.py`)
3. **Tester connexion OpenAI**
4. **Recharger l'agent**
5. Si échec : **Diagnostic complet** → copier le message

---

## Erreur après changement d'embeddings

Changer `EMBEDDING_PROVIDER` nécessite une réindexation :

```powershell
python main.py clear
python main.py index
```

Collections Chroma distinctes : `rag_openai`, `rag_tfidf`, `rag_local`.

---

## Ollama : connexion refusée

```powershell
ollama serve
ollama pull llama3.2
```

Dans `.env` :

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

---

## PyCharm / Cursor : bouton Play ▶

| Fichier ouvert | Résultat |
|----------------|----------|
| `app.py` + Play | **Erreur** — ne pas faire |
| `run_app.py` + Play | **OK** |
| `demarrer.bat` | **OK** |

Configuration debug : `.vscode/launch.json` → « Agent RAG - Interface web ».

---

## Fichier `.env` non lu dans un script

```python
# INCORRECT
import os
print(os.getenv("OPENAI_API_KEY"))  # → None

# CORRECT
from dotenv import load_dotenv
load_dotenv(".env", override=True)
import os
print(os.getenv("OPENAI_API_KEY"))
```

Le projet charge `.env` automatiquement via `src/config.py`.

---

## Checklist complète

- [ ] `venv\Scripts\activate`
- [ ] `pip install -r requirements.txt`
- [ ] `.env` avec vraie clé `sk-...`
- [ ] `python diagnose.py` → OK
- [ ] `python main.py index` → chunks > 0
- [ ] `python run_app.py` (pas `streamlit run app.py`)
- [ ] Tester connexion OpenAI → OK
- [ ] Recharger l'agent
