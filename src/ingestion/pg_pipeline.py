"""Pipeline d'ingestion vers PostgreSQL (texte, tableaux, chiffres, embeddings)."""

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import src.startup  # noqa: F401
from src.config import CHUNK_OVERLAP, CHUNK_SIZE, DOCUMENTS_DIR, reload_env
from src.db.engine import get_session, init_db
from src.db.repository import CorpusRepository
from src.ingestion.classifier import classify_text
from src.ingestion.document_loader import load_documents
from src.ingestion.table_extractor import extract_facts_from_text, extract_tables_from_pdf


def _get_embedder():
    reload_env()
    from src.retrieval.vector_store import _get_embeddings
    return _get_embeddings()


def _chunk_text(docs: list[Document], category: str) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\nARTICLE ", "\nArticle ", "\n\n", "\n", ". "],
    )
    chunks_out: list[dict] = []
    for doc in splitter.split_documents(docs):
        page = doc.metadata.get("page")
        chunks_out.append({
            "content": f"[{doc.metadata.get('source', '?')}]\n{doc.page_content}",
            "page_number": int(page) + 1 if isinstance(page, int) else page,
            "metadata": {"category": category, "source": doc.metadata.get("source")},
        })
    return chunks_out


def ingest_directory(
    directory: Path | None = None,
    batch_embed: int = 32,
    path_filter: str | None = None,
) -> dict:
    """Ingère tous les documents dans PostgreSQL."""
    init_db()
    docs_dir = directory or DOCUMENTS_DIR
    raw_docs, errors = load_documents(docs_dir)

    stats = {"sources": 0, "chunks": 0, "tables": 0, "facts": 0, "errors": errors}
    if not raw_docs:
        return stats

    embedder = _get_embedder()
    session = get_session()
    repo = CorpusRepository(session)

    by_file: dict[str, list[Document]] = {}
    for doc in raw_docs:
        name = doc.metadata.get("source", "inconnu")
        if path_filter and path_filter not in name.replace("\\", "/"):
            continue
        by_file.setdefault(name, []).append(doc)

    for filename, file_docs in by_file.items():
        full_text = "\n".join(d.page_content for d in file_docs)
        filepath = file_docs[0].metadata.get("file_path") or str(docs_dir / filename)
        category = classify_text(full_text, filename, filepath=filepath)

        src = repo.upsert_source(
            filename=filename,
            filepath=filepath,
            category=category,
            source_type=Path(filename).suffix.lower().lstrip(".") or "txt",
            page_count=len(file_docs),
        )

        chunks = _chunk_text(file_docs, category)
        texts = [c["content"] for c in chunks]
        for i in range(0, len(texts), batch_embed):
            batch = texts[i : i + batch_embed]
            vectors = embedder.embed_documents(batch)
            for j, vec in enumerate(vectors):
                # pgvector attend 1536 dims (OpenAI) ; tfidf local = recherche texte seule
                if len(vec) == 1536:
                    chunks[i + j]["embedding"] = vec
                else:
                    chunks[i + j]["embedding"] = None

        stats["chunks"] += repo.add_chunks(src.id, chunks)

        ext = Path(filename).suffix.lower().lstrip(".")
        if ext == "pdf":
            pdf_path = Path(filepath)
            if pdf_path.exists():
                for tbl in extract_tables_from_pdf(pdf_path):
                    tbl["category"] = category
                    repo.add_table(src.id, tbl)
                    stats["tables"] += 1
                    for fact in extract_facts_from_text(
                        tbl.get("raw_text", ""), category, tbl.get("page_number")
                    ):
                        repo.add_fact(src.id, fact)
                        stats["facts"] += 1

        for doc in file_docs:
            page = doc.metadata.get("page")
            pg = int(page) + 1 if isinstance(page, int) else None
            for fact in extract_facts_from_text(doc.page_content, category, pg):
                repo.add_fact(src.id, fact)
                stats["facts"] += 1

        stats["sources"] += 1
        session.commit()

    session.close()
    return stats
