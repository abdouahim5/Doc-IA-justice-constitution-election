"""Tests de connexion et diagnostics."""

import os

import src.startup  # noqa: F401 - SSL en premier

from src.config import is_openai_configured, reload_env
from src.errors import describe_error
from src.http_clients import test_https


def test_openai_connection() -> tuple[bool, str]:
    """Teste SSL puis LLM + embeddings OpenAI."""
    reload_env()
    provider = os.getenv("LLM_PROVIDER", "openai")

    if provider == "ollama":
        return True, "Mode Ollama — test OpenAI ignore"

    ssl_ok, ssl_msg = test_https()
    if not ssl_ok:
        return False, (
            f"Echec SSL : {ssl_msg}\n\n"
            "Solutions :\n"
            "1. pip install truststore certifi pip-system-certs\n"
            "2. Redemarrez avec : python run_app.py\n"
            "3. Ne lancez PAS streamlit run app.py directement"
        )

    if not is_openai_configured():
        return False, "OPENAI_API_KEY manquante ou invalide dans .env"

    try:
        from src.llm import get_llm
        from src.retrieval.vector_store import _get_embeddings

        get_llm().invoke("ok")
        dim = len(_get_embeddings().embed_query("test"))
        return True, f"OpenAI OK (SSL + LLM + embeddings dim={dim})"
    except Exception as e:
        return False, describe_error(e)


def full_diagnostic() -> list[str]:
    """Rapport de diagnostic complet."""
    reload_env()
    lines = [
        f"LLM_PROVIDER={os.getenv('LLM_PROVIDER', '?')}",
        f"EMBEDDING_PROVIDER={os.getenv('EMBEDDING_PROVIDER', '?')}",
        f"OPENAI_KEY={'OK' if is_openai_configured() else 'MANQUANTE'}",
    ]
    ssl_ok, ssl_msg = test_https()
    lines.append(f"SSL: {'OK' if ssl_ok else 'ECHEC'} — {ssl_msg}")
    ok, msg = test_openai_connection()
    lines.append(f"OpenAI: {'OK' if ok else 'ECHEC'} — {msg}")
    return lines
