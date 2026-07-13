"""Configuration LangSmith — tracing LangChain / LangGraph."""

from __future__ import annotations

import os
from typing import Any

_DEFAULT_PROJECT = "docia-france-civique"
_PLACEHOLDER_KEYS = {
    "",
    "lsv2_...",
    "your-langsmith-key",
    "changeme",
    "sk-votre-cle-api",
}


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in ("1", "true", "yes", "on")


def _api_key() -> str:
    return (
        os.getenv("LANGCHAIN_API_KEY", "").strip()
        or os.getenv("LANGSMITH_API_KEY", "").strip()
    )


def _project_name() -> str:
    return (
        os.getenv("LANGCHAIN_PROJECT", "").strip()
        or os.getenv("LANGSMITH_PROJECT", "").strip()
        or _DEFAULT_PROJECT
    )


def is_langsmith_configured() -> bool:
    """True si tracing activé et clé API valide."""
    if not _truthy(os.getenv("LANGCHAIN_TRACING_V2", os.getenv("LANGSMITH_TRACING"))):
        return False
    key = _api_key()
    return key not in _PLACEHOLDER_KEYS and len(key) > 12


def configure_langsmith() -> bool:
    """Active le tracing LangSmith dans os.environ. Retourne True si actif."""
    if not _truthy(os.getenv("LANGCHAIN_TRACING_V2", os.getenv("LANGSMITH_TRACING"))):
        return False

    key = _api_key()
    if not key or key in _PLACEHOLDER_KEYS:
        return False

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = key
    os.environ["LANGCHAIN_PROJECT"] = _project_name()

    endpoint = (
        os.getenv("LANGCHAIN_ENDPOINT", "").strip()
        or os.getenv("LANGSMITH_ENDPOINT", "").strip()
    )
    if endpoint:
        os.environ["LANGCHAIN_ENDPOINT"] = endpoint

    sampling = (
        os.getenv("LANGCHAIN_TRACING_SAMPLING_RATE", "").strip()
        or os.getenv("LANGSMITH_TRACING_SAMPLING_RATE", "").strip()
    )
    if sampling:
        os.environ["LANGCHAIN_TRACING_SAMPLING_RATE"] = sampling

    return True


def get_langsmith_status() -> dict[str, Any]:
    """État LangSmith pour l'interface admin / diagnostics."""
    tracing_requested = _truthy(
        os.getenv("LANGCHAIN_TRACING_V2", os.getenv("LANGSMITH_TRACING"))
    )
    configured = is_langsmith_configured()
    project = _project_name()

    if configured:
        message = f"Tracing actif — projet « {project} »"
    elif tracing_requested and not _api_key():
        message = "LANGCHAIN_TRACING_V2=true mais clé API manquante"
    elif tracing_requested:
        message = "Clé API LangSmith invalide ou placeholder"
    else:
        message = "Désactivé (LANGCHAIN_TRACING_V2=false)"

    return {
        "enabled": configured,
        "tracing_requested": tracing_requested,
        "project": project,
        "message": message,
        "dashboard_url": "https://smith.langchain.com",
    }


def build_run_config(
    question: str,
    *,
    pinned_theme: str | None = None,
    use_cache: bool = True,
    source: str = "streamlit",
) -> dict[str, Any]:
    """Métadonnées LangSmith pour un appel LangGraph."""
    tags = ["docia", "france-civique", source]
    if pinned_theme:
        tags.append(f"theme:{pinned_theme}")

    metadata: dict[str, Any] = {
        "use_cache": use_cache,
        "pinned_theme": pinned_theme or "",
        "question_preview": (question or "")[:240],
        "source": source,
    }

    return {
        "run_name": "france_civique_ask",
        "tags": tags,
        "metadata": metadata,
    }
