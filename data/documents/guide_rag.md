# Guide de l'Intelligence Artificielle et du RAG

## Qu'est-ce que le RAG ?

Le **Retrieval-Augmented Generation** (RAG) est une technique qui combine :
1. **Recherche** dans une base de connaissances (vos documents)
2. **Génération** de réponses par un modèle de langage (LLM)

Cela permet à l'IA de répondre avec précision sur VOS données, sans hallucinations.

## Architecture de cet agent

```
Documents (PDF, TXT, MD, DOCX)
        │
        ▼
   Ingestion & Chunking
        │
        ▼
  Embeddings (vecteurs)
        │
        ▼
   ChromaDB (vector store)
        │
        ▼
  Recherche hybride (BM25 + sémantique)
        │
        ▼
   LLM (OpenAI / Ollama)
        │
        ▼
   Réponse avec citations
```

## Fonctionnalités

- **Multi-format** : PDF, TXT, Markdown, DOCX
- **Recherche hybride** : combine similarité sémantique et mots-clés (BM25)
- **Mémoire conversationnelle** : comprend le contexte des échanges précédents
- **Citations de sources** : chaque réponse référence les documents utilisés
- **Multilingue** : embeddings optimisés pour le français
- **Flexible** : OpenAI (cloud) ou Ollama (local, gratuit)

## Formats supportés

| Format | Extension | Description |
|--------|-----------|-------------|
| PDF    | .pdf      | Documents Adobe |
| Texte  | .txt      | Fichiers texte brut |
| Markdown | .md     | Documentation technique |
| Word   | .docx     | Documents Microsoft Word |

## Bonnes pratiques

1. **Documents structurés** : titres, sections claires = meilleurs chunks
2. **Taille des chunks** : 1000 caractères par défaut (ajustable dans .env)
3. **Questions précises** : plus la question est ciblée, meilleure la réponse
4. **Réindexer** après ajout de nouveaux documents

## Exemples de questions

- "Quels sont les principes fondamentaux du RAG ?"
- "Résume le document sur l'architecture"
- "Quelle est la différence entre BM25 et la recherche sémantique ?"
