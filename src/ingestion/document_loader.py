"""Chargement multi-format de documents."""

from pathlib import Path

from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_core.documents import Document

import src.bootstrap  # noqa: F401
from src.config import SUPPORTED_EXTENSIONS


def _load_single_file(file_path: Path, base_dir: Path) -> list[Document]:
    """Charge un fichier selon son extension."""
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        loader = PyPDFLoader(str(file_path))
    elif suffix == ".docx":
        loader = Docx2txtLoader(str(file_path))
    elif suffix == ".md":
        loader = TextLoader(str(file_path), encoding="utf-8")
    elif suffix == ".txt":
        loader = TextLoader(str(file_path), encoding="utf-8")
    else:
        raise ValueError(f"Format non supporté : {suffix}")

    try:
        rel = file_path.relative_to(base_dir).as_posix()
    except ValueError:
        rel = file_path.name

    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = rel
        doc.metadata["file_path"] = str(file_path.resolve())
    return docs


def load_documents(directory: Path) -> tuple[list[Document], list[str]]:
    """Charge tous les documents supportés d'un répertoire.

    Returns:
        (documents, erreurs) — liste des erreurs de chargement par fichier.
    """
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        return [], []

    all_docs: list[Document] = []
    errors: list[str] = []
    for file_path in sorted(directory.rglob("*")):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                all_docs.extend(_load_single_file(file_path, directory))
            except Exception as e:
                msg = f"{file_path.name}: {e}"
                errors.append(msg)
                print(f"[WARN] Erreur lors du chargement de {file_path.name}: {e}")

    return all_docs, errors
