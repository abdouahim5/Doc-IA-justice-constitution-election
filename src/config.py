"""Configuration centralisée de l'agent RAG."""

import os
from pathlib import Path

import src.startup  # noqa: F401 - SSL Windows en premier

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


def apply_streamlit_secrets() -> None:
    """Injecte st.secrets dans os.environ (Streamlit Community Cloud)."""
    try:
        import streamlit as st

        if not hasattr(st, "secrets"):
            return
        for key, value in st.secrets.items():
            if isinstance(value, str):
                os.environ[key] = value
            elif hasattr(value, "items"):
                for sub_key, sub_val in value.items():
                    os.environ[str(sub_key)] = str(sub_val)
    except Exception:
        pass


def reload_env() -> None:
    """Recharge .env (necessaire car Streamlit met en cache les modules)."""
    load_dotenv(BASE_DIR / ".env", override=True)
    apply_streamlit_secrets()
    try:
        from src.langsmith_setup import configure_langsmith

        configure_langsmith()
    except Exception:
        pass


reload_env()

# LLM — valeurs par defaut au demarrage ; utiliser os.getenv() pour lecture a jour
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Embeddings
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "tfidf")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"
)

# RAG
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "6"))
RETRIEVAL_CANDIDATES = int(os.getenv("RETRIEVAL_CANDIDATES", "15"))
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "0.12"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))
FAST_MODE = os.getenv("FAST_MODE", "true").lower() in ("1", "true", "yes")
MIN_RELEVANCE_SCORE = float(os.getenv("MIN_RELEVANCE_SCORE", "0.18"))

# Ollama — limites pour accelerer la generation
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "350"))
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "2048"))

# Chemins
DOCUMENTS_DIR = Path(os.getenv("DOCUMENTS_DIR", BASE_DIR / "data" / "documents"))
VECTOR_STORE_DIR = Path(os.getenv("VECTOR_STORE_DIR", BASE_DIR / "data" / "vectorstore"))

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}

_PLACEHOLDER_KEYS = {"", "sk-votre-cle-api", "your-api-key-here", "changeme"}

_PERFORMANCE_PROFILES: dict[str, dict] = {
    "fast": {
        "text_only": True,
        "extractive": False,
        "vector_limit": 3,
        "text_limit": 5,
        "max_chunks": 3,
        "chunk_chars": 450,
        "facts_limit": 0,
        "tables_limit": 0,
        "max_tokens": 320,
        "parallel_search": False,
        "answer_style": "short",
    },
    "balanced": {
        "text_only": False,
        "extractive": True,
        "vector_limit": 4,
        "text_limit": 6,
        "max_chunks": 5,
        "chunk_chars": 750,
        "facts_limit": 6,
        "tables_limit": 2,
        "max_tokens": 600,
        "parallel_search": True,
        "answer_style": "rich",
    },
    "quality": {
        "text_only": False,
        "extractive": False,
        "vector_limit": 6,
        "text_limit": 8,
        "max_chunks": 6,
        "chunk_chars": 950,
        "facts_limit": 10,
        "tables_limit": 3,
        "max_tokens": 900,
        "parallel_search": True,
        "answer_style": "rich",
    },
}


def get_performance_mode() -> str:
    """Profil perf : fast | balanced | quality (défaut : balanced)."""
    reload_env()
    mode = os.getenv("PERFORMANCE_MODE", "").strip().lower()
    if mode in _PERFORMANCE_PROFILES:
        return mode
    if os.getenv("FAST_MODE", "true").lower() in ("0", "false", "no"):
        return "quality"
    return "balanced"


def is_openai_configured() -> bool:
    """True si une vraie cle OpenAI est configuree."""
    reload_env()
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return key not in _PLACEHOLDER_KEYS and key.startswith("sk-")


def get_embedding_provider() -> str:
    """Fournisseur d'embeddings lu a chaque appel."""
    reload_env()
    return os.getenv("EMBEDDING_PROVIDER", "tfidf")


def get_multi_agent_settings() -> dict:
    """Paramètres multi-agent selon PERFORMANCE_MODE (balanced = rapide + qualité)."""
    reload_env()
    mode = get_performance_mode()
    profile = dict(_PERFORMANCE_PROFILES[mode])
    profile["mode"] = mode
    profile["fast"] = mode == "fast"
    if os.getenv("TEXT_ONLY_SEARCH", "").lower() in ("1", "true", "yes"):
        profile["text_only"] = True
    override_tokens = os.getenv("OPENAI_MAX_TOKENS", "").strip()
    if override_tokens.isdigit():
        profile["max_tokens"] = int(override_tokens)
    return profile


def get_rag_settings() -> dict:
    """Parametres RAG lus a chaque appel (compatible cache Streamlit)."""
    reload_env()
    mode = get_performance_mode()
    top_k_defaults = {"fast": 4, "balanced": 6, "quality": 8}
    history_defaults = {"fast": 4, "balanced": 5, "quality": 6}
    return {
        "top_k": int(os.getenv("TOP_K_RESULTS", str(top_k_defaults[mode]))),
        "fast_mode": mode == "fast",
        "min_relevance": float(os.getenv("MIN_RELEVANCE_SCORE", "0.16")),
        "history_turns": int(
            os.getenv("CONVERSATION_HISTORY_TURNS", str(history_defaults[mode]))
        ),
    }


def get_llm_status() -> dict:
    """Etat de la configuration LLM pour l'interface."""
    reload_env()
    provider = os.getenv("LLM_PROVIDER", "openai")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
    perf = get_performance_mode()
    cfg = get_multi_agent_settings()

    if provider == "ollama":
        return {
            "provider": "ollama",
            "model": ollama_model,
            "ready": True,
            "message": f"Ollama / {ollama_model} · perf {perf}",
            "performance_mode": perf,
        }
    if not is_openai_configured():
        return {
            "provider": "openai",
            "model": openai_model,
            "ready": False,
            "message": "Cle OpenAI manquante (.env ou Secrets Streamlit)",
            "performance_mode": perf,
        }
    return {
        "provider": "openai",
        "model": openai_model,
        "ready": True,
        "message": (
            f"OpenAI / {openai_model} · perf {perf} "
            f"({cfg['max_chunks']} chunks, {cfg['max_tokens']} tokens)"
        ),
        "performance_mode": perf,
    }
