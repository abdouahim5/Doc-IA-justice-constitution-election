"""Outils LangChain — recherche corpus PostgreSQL par catégorie."""

from __future__ import annotations

from typing import Callable

from langchain_core.tools import StructuredTool

from src.config import get_multi_agent_settings
from src.db.repository import CorpusRepository

_CATEGORIES = (
    ("constitution", "Constitution française (articles, institutions)"),
    ("elections", "Élections et vie démocratique"),
    ("justice", "Droit, justice, codes et procédures"),
    ("test_civique", "Examen civique et naturalisation"),
)


def _normalize_hits(hits: list) -> list[tuple[str, float, str]]:
    from src.multi_agent.agents import _unpack_hit

    return [_unpack_hit(h) for h in hits]


def _format_hits(hits: list) -> str:
    if not hits:
        return "Aucun extrait trouvé dans les sources indexées."
    parts: list[str] = []
    for content, _score, fname in _normalize_hits(hits):
        parts.append(f"=== [{fname}] ===\n{content[:500]}")
    return "\n\n".join(parts)


def search_category(
    repo: CorpusRepository,
    embed_fn: Callable[[str], list[float]],
    category: str | None,
    query: str,
) -> str:
    """Recherche texte (+ vecteur si disponible) dans une catégorie."""
    cfg = get_multi_agent_settings()
    cat = category if category in {c[0] for c in _CATEGORIES} else None
    hits = repo.search_text(query, cat, cfg["text_limit"])
    if not hits and not cfg["text_only"]:
        try:
            emb = embed_fn(query)
            vector_hits = repo.search_vector(emb, cat, cfg["vector_limit"])
            hits = _normalize_hits(vector_hits)
        except Exception:
            pass
    return _format_hits(hits)


def create_corpus_tools(
    repo: CorpusRepository,
    embed_fn: Callable[[str], list[float]],
) -> list[StructuredTool]:
    """Crée un outil LangChain par catégorie documentaire."""
    tools: list[StructuredTool] = []

    for category, description in _CATEGORIES:

        def _make_search(cat: str):
            def _run(query: str) -> str:
                return search_category(repo, embed_fn, cat, query)

            return _run

        tools.append(
            StructuredTool.from_function(
                func=_make_search(category),
                name=f"search_{category}",
                description=(
                    f"Recherche dans les documents : {description}. "
                    "Entrée : question ou mots-clés en français."
                ),
            )
        )

    tools.append(
        StructuredTool.from_function(
            func=lambda query: search_category(repo, embed_fn, None, query),
            name="search_all_corpus",
            description="Recherche dans tout le corpus France Civique (toutes catégories).",
        )
    )
    return tools


def tool_hits_for_topic(
    repo: CorpusRepository,
    embed_fn: Callable[[str], list[float]],
    topic: str,
    query: str,
) -> list[tuple[str, float, str]]:
    """Fallback retrieve via outil de recherche."""
    cat = topic if topic in {c[0] for c in _CATEGORIES} else None
    cfg = get_multi_agent_settings()
    hits = repo.search_text(query, cat, cfg["text_limit"])
    if not hits and not cfg["text_only"]:
        try:
            emb = embed_fn(query)
            hits = _normalize_hits(repo.search_vector(emb, cat, cfg["vector_limit"]))
        except Exception:
            pass
    return hits
