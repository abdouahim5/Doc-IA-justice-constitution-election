# Mémoire conversationnelle

## Principe

L'agent garde les **derniers échanges** pour comprendre les questions de suivi.

Exemple :

```
Vous   : Qu'est-ce que dit l'article 2 ?
Agent  : [réponse sur l'article 2]

Vous   : et l'article 3 ?
Agent  : comprend le contexte → cherche l'article 3 → répond
```

## Deux niveaux de mémoire

| Niveau | Où | Rôle |
|--------|-----|------|
| **Affichage** | `st.session_state.messages` (Streamlit) | Historique visible dans le chat |
| **Intelligence** | `RAGAgent._chat_history` | Contexte pour recherche + LLM |

Les deux sont synchronisés via `restore_conversation()` quand l'agent est rechargé.

## Comment ça fonctionne

### 1. Stockage

Après chaque réponse, l'agent enregistre :

- `HumanMessage` (votre question)
- `AIMessage` (réponse de l'agent)

### 2. Détection des suivis

Une question est traitée comme **suivi** si :

- Elle commence par « et », « ou », « donc »…
- Elle contient « aussi », « développe », « le suivant »…
- C'est un article court après un échange (`article 5` après `article 2`)

### 3. Enrichissement pour la recherche

Si c'est un suivi, la question est enrichie :

```
et l'article 3 ?

Contexte de la conversation precedente :
Utilisateur: article 2
Assistant: L'article 2 stipule que...
```

Cela aide à trouver le bon passage dans les documents.

### 4. Historique dans le prompt LLM

Pour les questions générales et les articles, le LLM reçoit :

- Les **6 derniers messages** (configurable)
- Les **extraits** trouvés dans les documents

## Configuration

Dans `.env` :

```env
CONVERSATION_HISTORY_TURNS=6
```

- `6` = 3 échanges (utilisateur + assistant)
- Augmentez pour des conversations plus longues (coût API plus élevé)

## Utilisation

### Interface web

Posez plusieurs questions à la suite dans le chat.

**Effacer** : bouton « Effacer la conversation » (barre latérale).

**Recharger l'agent** : conserve l'affichage Streamlit ; la mémoire agent est resynchronisée.

### CLI

```powershell
python main.py chat
```

| Commande | Action |
|----------|--------|
| `clear` | Efface la mémoire |
| `quit` | Quitte |

## Limites

| Situation | Comportement |
|-----------|--------------|
| Recherche mot (`search president`) | Pas d'historique (volontaire) |
| Fermeture complète de Streamlit | Historique perdu |
| Question très vague (« et ? ») | Peut échouer — précisez |
| Nouveau sujet sans lien | Reformulez clairement |

## Conseils pour de bonnes conversations

1. **Première question** : soyez précis (`article 2`, `droits du président`)
2. **Suivis** : « et l'article 3 ? », « développe », « même chose pour le Sénat »
3. **Nouveau sujet** : commencez une phrase complète plutôt qu'un pronom seul

## Code source

- Mémoire : `src/agent/rag_agent.py` → `_chat_history`
- Contextualisation : `_contextualize_question()`, `_is_follow_up()`
- Sync Streamlit : `app.py` → `_get_agent()` + `restore_conversation()`
