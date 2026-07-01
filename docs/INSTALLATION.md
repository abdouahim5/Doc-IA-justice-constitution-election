# Installation

## Prérequis

- **Python 3.10+** (testé avec 3.13)
- **Windows 10/11** (le projet inclut des correctifs SSL pour Windows)
- Connexion internet (si `LLM_PROVIDER=openai` ou `EMBEDDING_PROVIDER=openai`)
- Optionnel : [Ollama](https://ollama.com) pour un mode 100 % local

## Étapes

### 1. Ouvrir le projet

```powershell
cd "C:\Users\PC\Desktop\Agent IA stucture doc"
```

### 2. Environnement virtuel

```powershell
py -m venv venv
venv\Scripts\activate
```

### 3. Dépendances

```powershell
pip install -r requirements.txt
```

Paquets critiques pour Windows :

| Paquet | Rôle |
|--------|------|
| `certifi` | Bundle de certificats CA |
| `truststore` | Certificats système Windows |
| `pip-system-certs` | Correctif SSL pour `requests` |
| `langchain-openai` | Client OpenAI (utilise `httpx`) |

### 4. Configuration

```powershell
copy .env.example .env
```

Éditez `.env` :

**OpenAI (recommandé)** :
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-votre-vraie-cle
EMBEDDING_PROVIDER=openai
```

**Ollama (local, gratuit)** :
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
EMBEDDING_PROVIDER=tfidf
```

### 5. Documents

Placez vos fichiers dans `data/documents/` :

- PDF, TXT, MD, DOCX

Un `guide_rag.md` d'exemple peut déjà être présent.

### 6. Indexation

```powershell
python main.py index
```

### 7. Vérification

```powershell
python diagnose.py
```

## Obtenir une clé OpenAI

1. Créez un compte sur [platform.openai.com](https://platform.openai.com)
2. Section API Keys → Create new secret key
3. Collez la clé dans `.env` : `OPENAI_API_KEY=sk-...`

**Ne commitez jamais** le fichier `.env` (il est dans `.gitignore`).

## Ollama (option local)

```powershell
# Installer Ollama depuis https://ollama.com
ollama pull llama3.2
ollama serve
```

Puis dans `.env` : `LLM_PROVIDER=ollama`
