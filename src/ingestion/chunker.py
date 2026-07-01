"""Découpage intelligent des documents en chunks."""

import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import src.bootstrap  # noqa: F401
from src.config import CHUNK_OVERLAP, CHUNK_SIZE

_ARTICLE_SPLIT = re.compile(
    r"(?=\n(?:ARTICLE|Article)\s+\d+\s*[\.:\-])",
    re.IGNORECASE,
)


def _split_legal_document(doc: Document) -> list[Document]:
    """Découpe un document juridique article par article si possible."""
    text = doc.page_content
    if not re.search(r"(?i)\bARTICLE\s+\d+", text):
        return [doc]

    parts = _ARTICLE_SPLIT.split(text)
    sections: list[Document] = []
    for part in parts:
        part = part.strip()
        if len(part) < 40:
            continue
        sections.append(
            Document(page_content=part, metadata=dict(doc.metadata))
        )
    return sections or [doc]


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Découpe les documents en petits chunks ciblés pour plus de précision."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", "? ", "! ", " ", ""],
    )

    prepared: list[Document] = []
    for doc in documents:
        prepared.extend(_split_legal_document(doc))

    chunks = splitter.split_documents(prepared)
    for i, chunk in enumerate(chunks):
        source = chunk.metadata.get("source", "inconnu")
        chunk.metadata["chunk_id"] = i
        chunk.metadata.setdefault("source", source)
        if not chunk.page_content.startswith(f"[{source}]"):
            chunk.page_content = f"[{source}]\n{chunk.page_content}"
    return chunks
