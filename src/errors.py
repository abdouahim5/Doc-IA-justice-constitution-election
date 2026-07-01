"""Messages d'erreur utilisateur pour les appels LLM / embeddings."""

import os

from src.config import reload_env

_CONNECTION_TYPES = (
    "apiconnectionerror",
    "connecterror",
    "connectionerror",
    "connecttimeout",
    "readtimeout",
    "timeoutexception",
    "connectionreseterror",
)

_CONNECTION_MARKERS = (
    "connection error",
    "connection refused",
    "failed to connect",
    "connect call failed",
    "connection aborted",
    "connection reset",
    "timed out",
    "timeout",
    "ssl",
    "certificate",
    "certificate_verify_failed",
    "client has been closed",
    "network is unreachable",
    "name or service not known",
    "getaddrinfo failed",
)


def _root_cause(exc: BaseException) -> BaseException:
    current = exc
    while current.__cause__ is not None:
        current = current.__cause__
    return current


def _wrap_error(message: str, exc: BaseException) -> RuntimeError:
    wrapped = RuntimeError(message)
    wrapped.__cause__ = exc
    return wrapped


def _is_connection_error(exc: BaseException) -> bool:
    root = _root_cause(exc)
    name = type(root).__name__.lower()
    detail = str(root).lower()

    if any(t in name for t in _CONNECTION_TYPES):
        return True
    if any(m in detail for m in _CONNECTION_MARKERS):
        return True
    return False


def _is_auth_error(exc: BaseException) -> bool:
    root = _root_cause(exc)
    name = type(root).__name__.lower()
    detail = str(root).lower()
    return (
        "auth" in name
        or "401" in str(root)
        or "invalid api key" in detail
        or "incorrect api key" in detail
        or "invalid_api_key" in detail
    )


def _is_rate_limit_error(exc: BaseException) -> bool:
    root = _root_cause(exc)
    name = type(root).__name__.lower()
    detail = str(root).lower()
    return "ratelimit" in name or "rate limit" in detail or "429" in str(root)


def describe_error(exc: BaseException) -> str:
    """Texte technique complet pour le diagnostic."""
    parts = [f"{type(exc).__name__}: {exc}"]
    cause = exc.__cause__
    while cause is not None:
        parts.append(f"  cause -> {type(cause).__name__}: {cause}")
        cause = cause.__cause__
    return "\n".join(parts)


def format_llm_error(exc: BaseException) -> RuntimeError:
    """Convertit une exception technique en message clair."""
    reload_env()
    provider = os.getenv("LLM_PROVIDER", "openai")
    root = _root_cause(exc)

    if provider == "ollama":
        detail = str(root).lower()
        name = type(root).__name__
        if _is_connection_error(exc):
            return _wrap_error(
                "Impossible de joindre Ollama. Lancez Ollama puis : ollama pull llama3.2",
                exc,
            )
        if "not found" in detail or "NotFound" in name:
            model = os.getenv("OLLAMA_MODEL", "llama3.2")
            return _wrap_error(
                f"Modele introuvable ({model}). Lancez : ollama pull {model}",
                exc,
            )
        return _wrap_error(f"Erreur Ollama ({type(root).__name__}) : {root}", exc)

    if _is_auth_error(exc):
        return _wrap_error(
            "Cle API OpenAI invalide. Verifiez OPENAI_API_KEY dans .env.",
            exc,
        )
    if _is_rate_limit_error(exc):
        return _wrap_error(
            "Quota OpenAI depasse ou limite de requetes atteinte. Reessayez plus tard.",
            exc,
        )
    if _is_connection_error(exc):
        return _wrap_error(
            "Connexion OpenAI echouee. Verifiez .env, internet et relancez "
            "l'application (python run_app.py) puis Recharger l'agent.",
            exc,
        )
    return _wrap_error(f"Erreur OpenAI ({type(root).__name__}) : {root}", exc)


def is_transient_error(exc: BaseException) -> bool:
    """Erreurs susceptibles de disparaitre apres reconnexion."""
    return _is_connection_error(exc)
