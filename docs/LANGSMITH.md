# LangSmith — observabilité DocIA

[LangSmith](https://smith.langchain.com) enregistre chaque exécution **LangGraph** et **LangChain** : routage, retrieval pgvector, appels OpenAI, latence, tokens, coûts.

---

## Activation (2 minutes)

1. Créez un compte sur https://smith.langchain.com  
2. **Settings → API Keys** → copiez la clé `lsv2_...`  
3. Ajoutez dans `.env` (local) ou **Secrets Streamlit** (cloud) :

```toml
LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_API_KEY = "lsv2_votre-cle"
LANGCHAIN_PROJECT = "docia-france-civique"
```

4. Redémarrez l'app (`run_app.py` ou reboot Streamlit Cloud)  
5. Posez une question dans **France Civique** → ouvrez le projet sur LangSmith

---

## Ce que vous voyez dans LangSmith

| Trace | Contenu |
|-------|---------|
| `france_civique_ask` | Run principal (question, tags, métadonnées) |
| Nœuds LangGraph | `validate` → `check_cache` → `route` → agent → `save_cache` |
| Chaînes LCEL | Prompt → `gpt-4o-mini` → réponse |
| Embeddings | Appels `text-embedding-3-small` (recherche vectorielle) |

**Tags automatiques :** `docia`, `france-civique`, `streamlit` ou `cli`, `theme:constitution` si thème épinglé.

---

## Production / RGPD

- Les **questions utilisateurs** sont envoyées à LangSmith si le tracing est actif.  
- En production publique : désactivez (`LANGCHAIN_TRACING_V2=false`) ou utilisez l'échantillonnage :

```toml
LANGCHAIN_TRACING_SAMPLING_RATE = "0.1"
```

- Recommandé : tracing **staging/dev uniquement**.

---

## Vérification

- **Admin** → section *LangSmith — observabilité*  
- **Diagnostic complet** : ligne `LangSmith: ACTIF`  
- CLI : `python main.py multi-ask "article 5" --no-cache` (tag `cli` dans LangSmith)

---

## Fichiers concernés

| Fichier | Rôle |
|---------|------|
| `src/langsmith_setup.py` | Activation env + métadonnées runs |
| `src/config.py` | Appel `configure_langsmith()` au reload |
| `src/multi_agent/orchestrator.py` | `run_name`, tags, metadata sur `graph.invoke` |

Aucun changement de logique métier : instrumentation transparente via variables d'environnement.
