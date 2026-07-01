"""Gestion du vector store ChromaDB avec embeddings configurables."""

import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

import src.startup  # noqa: F401
from src.config import (
    EMBEDDING_MODEL,
    VECTOR_STORE_DIR,
    get_embedding_provider,
    is_openai_configured,
    reload_env,
)
from src.http_clients import new_http_clients


class TfidfEmbeddings(Embeddings):
    """Embeddings TF-IDF locaux — fonctionne hors ligne sans téléchargement."""

    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._vectorizer = TfidfVectorizer(max_features=512)
        self._fitted = False

    def _fit_if_needed(self, texts: list[str]) -> None:
        if not self._fitted:
            self._vectorizer.fit(texts)
            self._fitted = True

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self._fit_if_needed(texts)
        matrix = self._vectorizer.transform(texts)
        return matrix.toarray().tolist()

    def embed_query(self, text: str) -> list[float]:
        if not self._fitted:
            return [0.0] * 512
        return self._vectorizer.transform([text]).toarray()[0].tolist()


def _get_local_embeddings() -> Embeddings:
    """Tente HuggingFace, sinon bascule sur TF-IDF local."""
    try:
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    except Exception as e:
        raise RuntimeError(
            f"Embeddings locaux indisponibles ({e}). "
            "Utilisez EMBEDDING_PROVIDER=openai ou tfidf dans .env"
        ) from e


def _get_embeddings() -> Embeddings:
    """Retourne le modèle d'embeddings selon la configuration."""
    reload_env()
    provider = get_embedding_provider()

    if provider == "openai":
        if not is_openai_configured():
            raise ValueError(
                "EMBEDDING_PROVIDER=openai mais OPENAI_API_KEY invalide dans .env"
            )
        http_client, http_async = new_http_clients()
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            max_retries=3,
            http_client=http_client,
            http_async_client=http_async,
        )
    if provider == "tfidf":
        return TfidfEmbeddings()
    return _get_local_embeddings()


class VectorStoreManager:
    """Crée, charge et interroge le vector store."""

    def __init__(self, persist_dir: Path | None = None):
        self.persist_dir = persist_dir or VECTOR_STORE_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings = _get_embeddings()
        self._load_tfidf_if_available()
        self._store: Chroma | None = None

    @property
    def collection_name(self) -> str:
        return f"rag_{get_embedding_provider()}"

    def _load_tfidf_if_available(self) -> None:
        if isinstance(self.embeddings, TfidfEmbeddings):
            tfidf_path = self.persist_dir / "tfidf.pkl"
            if tfidf_path.exists():
                import joblib

                self.embeddings._vectorizer = joblib.load(tfidf_path)
                self.embeddings._fitted = True

    def _save_tfidf_if_needed(self) -> None:
        if isinstance(self.embeddings, TfidfEmbeddings) and self.embeddings._fitted:
            import joblib

            joblib.dump(self.embeddings._vectorizer, self.persist_dir / "tfidf.pkl")

    @property
    def store(self) -> Chroma:
        if self._store is None:
            try:
                self._store = Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=str(self.persist_dir),
                )
            except Exception as e:
                raise RuntimeError(
                    f"Index vectoriel illisible ({e}). Lancez : python main.py clear "
                    "puis python main.py index"
                ) from e
        return self._store

    def index_documents(self, documents: list[Document]) -> int:
        """Indexe les documents dans le vector store."""
        if not documents:
            return 0

        try:
            self._store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=self.collection_name,
                persist_directory=str(self.persist_dir),
            )
        except Exception as e:
            raise RuntimeError(
                f"Echec d'indexation ({e}). Verifiez OPENAI_API_KEY / internet "
                "ou passez EMBEDDING_PROVIDER=tfidf"
            ) from e
        self._save_tfidf_if_needed()
        return len(documents)

    def similarity_search(self, query: str, k: int = 5) -> list[Document]:
        """Recherche sémantique par similarité."""
        try:
            return self.store.similarity_search(query, k=k)
        except Exception:
            return []

    def similarity_search_with_score(
        self, query: str, k: int = 5
    ) -> list[tuple[Document, float]]:
        """Recherche sémantique avec score de similarité (0 = identique)."""
        try:
            return self.store.similarity_search_with_score(query, k=k)
        except Exception:
            return []

    def get_all_documents(self) -> list[Document]:
        """Récupère tous les documents indexés."""
        try:
            data = self.store.get()
        except Exception:
            return []
        docs = []
        for i, content in enumerate(data.get("documents", [])):
            metadata = data.get("metadatas", [{}])[i] if data.get("metadatas") else {}
            docs.append(Document(page_content=content, metadata=metadata))
        return docs

    def count(self) -> int:
        """Nombre de chunks indexés."""
        if not is_index_healthy(self.persist_dir):
            return 0
        try:
            return self.store._collection.count()
        except Exception:
            return 0

    def clear(self) -> None:
        """Supprime le vector store."""
        import shutil
        import time

        self._store = None
        if not self.persist_dir.exists():
            return
        for attempt in range(3):
            try:
                shutil.rmtree(self.persist_dir)
                break
            except PermissionError:
                time.sleep(0.5)
        self.persist_dir.mkdir(parents=True, exist_ok=True)


def is_index_healthy(persist_dir: Path | None = None) -> bool:
    """True si l'index ChromaDB est valide (pas corrompu)."""
    directory = persist_dir or VECTOR_STORE_DIR
    if not directory.exists():
        return False
    return (directory / "chroma.sqlite3").exists()
