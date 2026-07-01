"""Configuration centralisée de l'agent RAG."""

import os
from pathlib import Path

import src.startup  # noqa: F401 - SSL Windows en premier

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


def reload_env() -> None:
    """Recharge .env (necessaire car Streamlit met en cache les modules)."""
    load_dotenv(BASE_DIR / ".env", override=True)


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
    """Paramètres multi-agent (mode rapide = moins de chunks, recherches parallèles)."""
    reload_env()
    fast = os.getenv("FAST_MODE", "true").lower() in ("1", "true", "yes")
    return {
        "fast": fast,
        "text_only": fast or os.getenv("TEXT_ONLY_SEARCH", "").lower() in ("1", "true", "yes"),
        "extractive": False,
        "vector_limit": 3 if fast else 5,
        "text_limit": 5 if fast else 6,
        "max_chunks": 3 if fast else 5,
        "chunk_chars": 450 if fast else 700,
        "facts_limit": 0 if fast else 6,
        "tables_limit": 0 if fast else 2,
        "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "250" if fast else "400")),
    }


def get_rag_settings() -> dict:
    """Parametres RAG lus a chaque appel (compatible cache Streamlit)."""
    reload_env()
    fast = os.getenv("FAST_MODE", "true").lower() in ("1", "true", "yes")
    return {
        "top_k": int(os.getenv("TOP_K_RESULTS", "4" if fast else "6")),
        "fast_mode": fast,
        "min_relevance": float(os.getenv("MIN_RELEVANCE_SCORE", "0.18")),
        "history_turns": int(os.getenv("CONVERSATION_HISTORY_TURNS", "4" if fast else "6")),
    }


def get_llm_status() -> dict:
    """Etat de la configuration LLM pour l'interface."""
    reload_env()
    provider = os.getenv("LLM_PROVIDER", "openai")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")

    if provider == "ollama":
        return {
            "provider": "ollama",
            "model": ollama_model,
            "ready": True,
            "message": f"Ollama / {ollama_model}",
        }
    if not is_openai_configured():
        return {
            "provider": "openai",
            "model": openai_model,
            "ready": False,
            "message": "Cle OpenAI manquante ou invalide dans .env",
        }
    return {
        "provider": "openai",
        "model": openai_model,
        "ready": True,
        "message": f"OpenAI / {openai_model}",
    }
