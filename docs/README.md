# Documentation — France Civique IA (DocIA)

Index de toute la documentation du projet.

| Fichier | Contenu |
|---------|---------|
| **[PROJET_COMPLET.md](PROJET_COMPLET.md)** | **★ Documentation complète : architecture, flux, agents, BDD, déploiement** |
| [INSTALLATION.md](INSTALLATION.md) | Prérequis, venv, dépendances, première config |
| [CONFIGURATION.md](CONFIGURATION.md) | Toutes les variables `.env` expliquées |
| [DEMARRAGE.md](DEMARRAGE.md) | CLI, Streamlit, PyCharm, Cursor — quoi lancer |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Schémas techniques, double stack PG + Chroma |
| [CONVERSATION.md](CONVERSATION.md) | Mémoire conversationnelle et questions de suivi |
| [DEPANNAGE.md](DEPANNAGE.md) | Erreurs connues : SSL, OpenAI, ImportError, index |
| [COMMANDES.md](COMMANDES.md) | Référence complète CLI et interface web |
| [MULTI_AGENT.md](MULTI_AGENT.md) | Multi-agent France, PostgreSQL, cache instantané |
| [SCRAPING.md](SCRAPING.md) | Téléchargement automatique des sources officielles |
| [DEPLOIEMENT.md](DEPLOIEMENT.md) | Déploiement VPS Docker (production) |

## Fichiers racine utiles

| Fichier | Rôle |
|---------|------|
| `README.md` | Vue d'ensemble rapide |
| `.env.example` | Modèle de configuration |
| `run_app.py` | **Point d'entrée Streamlit** (à utiliser) |
| `main.py` | Interface ligne de commande |
| `diagnose.py` | Diagnostic automatique (SSL, OpenAI, index) |
| `demarrer.bat` | Double-clic Windows pour lancer l'interface |

## Diagnostic rapide

```powershell
cd "C:\Users\PC\Desktop\Agent IA stucture doc"
venv\Scripts\activate
python diagnose.py
```

Résultat attendu : `RESULTAT: OK`
