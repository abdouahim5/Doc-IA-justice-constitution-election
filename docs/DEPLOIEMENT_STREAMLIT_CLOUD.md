# Déploiement Streamlit Community Cloud — DocIA

Guide **pas à pas** pour déployer **France Civique IA** sur [Streamlit Community Cloud](https://share.streamlit.io) (gratuit).

---

## Architecture

```
Utilisateur
    │
    ▼
Streamlit Community Cloud  (héberge app.py)
    │
    ├── OpenAI API          (embeddings + LLM)
    └── PostgreSQL externe  (Neon / Supabase + pgvector)
```

| Composant | Où ? |
|-----------|------|
| **Interface Streamlit** | Streamlit Cloud (gratuit) |
| **PostgreSQL + pgvector** | **Neon** ou **Supabase** (gratuit / low-cost) |
| **Secrets** | Dashboard Streamlit → **Secrets** |
| **ChromaDB local** | ❌ Non persistant sur Cloud → utiliser PostgreSQL |

> Les documents sont **dans le repo Git** ; les **vecteurs** sont dans PostgreSQL (ingestion faite une fois depuis votre PC).

---

## Étape 1 — Prérequis

- [ ] Compte [GitHub](https://github.com) (dépôt à jour)
- [ ] Compte [Streamlit Cloud](https://share.streamlit.io) (connexion GitHub)
- [ ] Clé **OpenAI** (`OPENAI_API_KEY`)
- [ ] Compte **[Neon](https://neon.tech)** (PostgreSQL gratuit + pgvector)

---

## Étape 2 — Préparer le dépôt GitHub

### 2.1 Requirements allégés (obligatoire)

Streamlit Cloud **ne supporte pas** PyTorch (`sentence-transformers`). Utilisez les dépendances cloud :

**Option A — branche dédiée (recommandé)**

```powershell
cd "C:\Users\PC\Desktop\Agent IA stucture doc"
git checkout -b deploy/streamlit
copy requirements-streamlit.txt requirements.txt
git add requirements.txt
git commit -m "Requirements allégés pour Streamlit Cloud"
git push -u origin deploy/streamlit
```

**Option B — remplacer sur `main`**

```powershell
copy requirements-streamlit.txt requirements.txt
git add requirements.txt
git commit -m "Requirements Streamlit Cloud"
git push
```

> En local, réinstallez avec `pip install -r requirements-full.txt` si vous gardez `requirements-full.txt` (voir ci-dessous).

### 2.2 Vérifier les fichiers

| Fichier | Rôle |
|---------|------|
| `app.py` | **Main file** à indiquer sur Streamlit Cloud |
| `requirements.txt` | Dépendances (version allégée) |
| `.streamlit/config.toml` | Config Streamlit |
| `data/documents/` | Sources (déjà dans le repo) |

---

## Étape 3 — Créer PostgreSQL sur Neon

1. Allez sur https://neon.tech → **Sign up**
2. **New Project** → nom `docia` → région **EU (Frankfurt ou Paris proche)**
3. Copiez la **connection string** (format `postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require`)

### 3.1 Activer pgvector et le schéma

Dans le **SQL Editor** Neon, exécutez le contenu de `sql/schema.sql` du projet.

Ou depuis votre PC (avec le projet cloné) :

```powershell
# Remplacez par votre URL Neon (postgresql:// → postgresql+psycopg://)
$env:DATABASE_URL="postgresql+psycopg://user:pass@ep-xxx.neon.tech/neondb?sslmode=require"
python main.py pg-init
```

---

## Étape 4 — Ingérer le corpus (depuis votre PC)

L'ingestion **ne se fait pas** sur Streamlit Cloud (trop long, timeout). Faites-la **en local** vers Neon :

```powershell
cd "C:\Users\PC\Desktop\Agent IA stucture doc"
venv\Scripts\activate

# URL Neon dans .env ou variable :
# DATABASE_URL=postgresql+psycopg://...@ep-xxx.neon.tech/neondb?sslmode=require
# OPENAI_API_KEY=sk-...
# EMBEDDING_PROVIDER=openai

python main.py pg-ingest
python main.py pg-stats
```

Attendu : **centaines de sources**, **milliers de chunks**.

---

## Étape 5 — Déployer sur Streamlit Cloud

1. https://share.streamlit.io → **Create app**
2. **Repository** : `abdouahim5/Doc-IA-justice-constitution-election`
3. **Branch** : `deploy/streamlit` (ou `main`)
4. **Main file path** : `app.py`
5. **App URL** : `docia-france-civique` (ou au choix) → `https://docia-france-civique.streamlit.app`
6. **Deploy**

---

## Étape 6 — Configurer les Secrets

Dans l'app déployée → **⚙️ Settings** → **Secrets**, collez :

```toml
OPENAI_API_KEY = "sk-votre-cle-api"
LLM_PROVIDER = "openai"
OPENAI_MODEL = "gpt-4o-mini"
EMBEDDING_PROVIDER = "openai"
FAST_MODE = "true"

DATABASE_URL = "postgresql+psycopg://user:password@ep-xxx.neon.tech/neondb?sslmode=require"
```

> Modèle : [`.streamlit/secrets.toml.example`](../.streamlit/secrets.toml.example)

Cliquez **Save** → l'app **redémarre** automatiquement.

---

## Étape 7 — Vérifier

1. Ouvrez `https://VOTRE-APP.streamlit.app`
2. Menu **France Civique** → posez une question test : `article 5`
3. Page **Configuration** → **Tester connexion OpenAI** → doit être OK
4. Stats PostgreSQL visibles si la connexion Neon fonctionne

---

## Mettre à jour l'app

```powershell
git add .
git commit -m "Mise à jour"
git push
```

Streamlit Cloud **redéploie automatiquement** à chaque push sur la branche suivie.

---

## Mettre à jour le README staging

Après déploiement, dans `deploy/staging.env` :

```env
STAGING_STATUS=en_ligne
STAGING_URL_APP=https://docia-france-civique.streamlit.app
STAGING_URL_HEALTH=https://docia-france-civique.streamlit.app/_stcore/health
```

```powershell
py scripts/update_staging_status.py
git push
```

---

## Limites Streamlit Cloud (gratuit)

| Limite | Impact |
|--------|--------|
| **1 Go RAM** | `FAST_MODE=true` obligatoire |
| **Pas de Docker** | Postgres externe (Neon) |
| **Filesystem éphémère** | Pas de Chroma persistant → PostgreSQL |
| **Timeout inactivité** | App s'endort après ~inactivité, redémarre au clic |
| **Secrets publics** | App **publique** par défaut — pas de données sensibles dans le code |

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Build échoue (mémoire) | `requirements.txt` allégé, pas de `sentence-transformers` |
| `Cle OpenAI manquante` | Vérifier **Secrets** → `OPENAI_API_KEY` |
| PostgreSQL inaccessible | URL Neon avec `?sslmode=require` et préfixe `postgresql+psycopg://` |
| Réponses vides / pas de sources | Relancer `pg-ingest` vers Neon depuis votre PC |
| App lente au 1er clic | Normal (cold start Streamlit Cloud) |

---

## Alternative : Supabase au lieu de Neon

1. https://supabase.com → nouveau projet
2. **Database** → connection string (mode **Session** ou **Transaction**)
3. SQL Editor → exécuter `sql/schema.sql` + `CREATE EXTENSION IF NOT EXISTS vector;`
4. Même `DATABASE_URL` dans les Secrets Streamlit

---

## Récapitulatif

| Étape | Action |
|-------|--------|
| 1 | Comptes GitHub + Streamlit + Neon |
| 2 | `requirements.txt` allégé sur branche `deploy/streamlit` |
| 3 | Base Neon + `pg-init` |
| 4 | `pg-ingest` depuis votre PC |
| 5 | Create app sur share.streamlit.io → `app.py` |
| 6 | Secrets : `OPENAI_API_KEY` + `DATABASE_URL` |
| 7 | Tester l'URL `.streamlit.app` |

---

Voir aussi : [DEPLOIEMENT.md](DEPLOIEMENT.md) · [DEPLOIEMENT_GCP.md](DEPLOIEMENT_GCP.md) · [STAGING.md](STAGING.md)
