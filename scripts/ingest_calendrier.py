"""Ingestion rapide d'un seul fichier texte dans PostgreSQL."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import src.startup  # noqa: F401
from langchain_core.documents import Document
from src.ingestion.pg_pipeline import _chunk_text, _get_embedder
from src.ingestion.classifier import classify_text
from src.db.engine import get_session, init_db
from src.db.repository import CorpusRepository
from src.ingestion.table_extractor import extract_facts_from_text

CALENDAR = Path("data/documents/sources_officielles/calendrier_elections_france.txt")


def main():
    print("init_db...")
    init_db()
    text = CALENDAR.read_text(encoding="utf-8")
    category = classify_text(text, CALENDAR.name)
    print(f"category={category}, len={len(text)}")

    docs = [Document(page_content=text, metadata={"source": CALENDAR.name})]
    chunks = _chunk_text(docs, category)
    print(f"chunks={len(chunks)}")

    embedder = _get_embedder()
    texts = [c["content"] for c in chunks]
    print("embedding...")
    vectors = embedder.embed_documents(texts)
    for c, vec in zip(chunks, vectors):
        c["embedding"] = vec

    session = get_session()
    repo = CorpusRepository(session)
    src = repo.upsert_source(
        filename=CALENDAR.name,
        filepath=str(CALENDAR.resolve()),
        category=category,
        source_type="txt",
        page_count=1,
    )
    n = repo.add_chunks(src.id, chunks)
    for fact in extract_facts_from_text(text, category):
        repo.add_fact(src.id, fact)
    source_id = src.id
    session.commit()
    session.close()
    print(f"OK: source_id={source_id}, chunks={n}")


if __name__ == "__main__":
    main()
