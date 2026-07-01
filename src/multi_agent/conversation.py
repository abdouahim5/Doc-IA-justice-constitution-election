"""Contexte conversationnel pour le multi-agent (suites de questions, thèmes)."""

from src.ingestion.classifier import classify_question
from src.retrieval.hybrid_retriever import _extract_article_numbers

_FOLLOW_UP_MARKERS = (
    "et l'", "et la ", "et le ", "et les ", "aussi", "également", "egalement",
    "developpe", "développe", "plus de", "en savoir", "le suivant", "la suite",
    "l'autre", "celui", "celle", "qu'en est", "précise", "precise", "résume",
    "resume", "meme ", "même ", "pareil", "autre article", "et pour",
    "explique", "pourquoi", "comment", "donc", "alors",
)

THEME_TO_TOPIC: dict[str, str] = {
    "constitution": "constitution",
    "elections": "elections",
    "justice": "justice",
    "institutions": "constitution",
    "calendrier": "elections",
    "chiffres": "data",
    "citoyennete": "elections",
}


def format_history(messages: list[dict], max_turns: int = 4) -> str:
    """Formate les derniers échanges pour le LLM."""
    if not messages:
        return ""
    recent = messages[-max_turns * 2 :]
    lines: list[str] = []
    for msg in recent:
        if msg.get("role") not in ("user", "assistant"):
            continue
        role = "Utilisateur" if msg["role"] == "user" else "Assistant"
        content = str(msg.get("content", "")).strip()
        if content:
            lines.append(f"{role}: {content[:400]}")
    return "\n".join(lines)


def is_follow_up(question: str, history: list[dict]) -> bool:
    """Détecte une question de suite dans un fil de discussion."""
    if not history:
        return False
    q = question.strip().lower()
    if any(marker in q for marker in _FOLLOW_UP_MARKERS):
        return True
    if q.startswith(("et ", "ou ", "donc ", "alors ", "puis ")):
        return True
    if len(q.split()) <= 4 and _extract_article_numbers(question):
        return True
    return False


def enrich_with_history(question: str, history: list[dict]) -> str:
    """Enrichit la requête de recherche avec le contexte récent."""
    ctx = format_history(history)
    if not ctx:
        return question
    return f"{question}\n\nContexte de la conversation precedente :\n{ctx}"


def resolve_topic(
    question: str,
    history: list[dict],
    pinned_theme: str | None = None,
) -> str:
    """Route vers le bon agent en tenant compte du thème actif."""
    if pinned_theme:
        mapped = THEME_TO_TOPIC.get(pinned_theme)
        if mapped and (not history or is_follow_up(question, history)):
            return mapped
    return classify_question(question)
