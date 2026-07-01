"""Fournisseur LLM configurable (OpenAI ou Ollama)."""

import os

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

import src.startup  # noqa: F401
from src.config import reload_env
from src.http_clients import new_http_clients


def get_llm() -> BaseChatModel:
    """Retourne le modèle de langage selon la configuration."""
    reload_env()
    provider = os.getenv("LLM_PROVIDER", "openai")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    api_key = os.getenv("OPENAI_API_KEY", "")

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            temperature=float(os.getenv("TEMPERATURE", "0")),
            num_predict=int(os.getenv("OLLAMA_NUM_PREDICT", "350")),
            num_ctx=int(os.getenv("OLLAMA_NUM_CTX", "2048")),
        )

    if api_key.strip() in {"", "sk-votre-cle-api", "your-api-key-here", "changeme"}:
        raise ValueError(
            "OPENAI_API_KEY invalide dans .env. "
            "Mettez une vraie cle OpenAI, ou passez a LLM_PROVIDER=ollama"
        )
    if not api_key.startswith("sk-"):
        raise ValueError("OPENAI_API_KEY invalide (doit commencer par sk-).")

    http_client, http_async = new_http_clients()
    return ChatOpenAI(
        model=openai_model,
        temperature=float(os.getenv("TEMPERATURE", "0")),
        openai_api_key=api_key,
        max_tokens=int(os.getenv(
            "OPENAI_MAX_TOKENS",
            "250" if os.getenv("FAST_MODE", "true").lower() in ("1", "true", "yes") else "400",
        )),
        max_retries=2,
        http_client=http_client,
        http_async_client=http_async,
    )
