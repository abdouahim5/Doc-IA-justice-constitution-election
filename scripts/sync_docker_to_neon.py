"""Synchronise Docker PostgreSQL -> Neon (sans embeddings, compatible limite 512 Mo).

Exemples :
  python scripts/sync_docker_to_neon.py --civic
  python scripts/sync_docker_to_neon.py --categories constitution,elections
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import src.startup  # noqa: F401

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

LOCAL_URL = "postgresql+psycopg://docia:docia_secret@localhost:5433/docia_fr"
BATCH = 1000
CIVIC_CATEGORIES = ("constitution", "elections", "test_civique", "general")


def _engine(url: str):
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 30})


def _truncate_neon(session: Session) -> None:
    session.execute(text("""
        TRUNCATE TABLE query_cache, document_chunks, extracted_tables,
                       structured_facts, sources
        RESTART IDENTITY CASCADE
    """))
    session.commit()


def _row_params(row: dict) -> dict:
    out = dict(row)
    for key in ("metadata", "headers", "rows"):
        if key in out and out[key] is not None and not isinstance(out[key], str):
            out[key] = json.dumps(out[key])
    return out


def _copy_sources(local: Session, neon: Session, categories: list[str] | None) -> int:
    if categories:
        rows = local.execute(text("""
            SELECT id, filename, filepath, category, source_type, page_count, metadata, indexed_at
            FROM sources WHERE category = ANY(:cats) ORDER BY id
        """), {"cats": categories}).mappings().all()
    else:
        rows = local.execute(text("""
            SELECT id, filename, filepath, category, source_type, page_count, metadata, indexed_at
            FROM sources ORDER BY id
        """)).mappings().all()
    for row in rows:
        neon.execute(text("""
            INSERT INTO sources (id, filename, filepath, category, source_type, page_count, metadata, indexed_at)
            VALUES (:id, :filename, :filepath, :category, :source_type, :page_count, CAST(:metadata AS jsonb), :indexed_at)
        """), _row_params(dict(row)))
    neon.execute(text("SELECT setval('sources_id_seq', (SELECT COALESCE(MAX(id), 1) FROM sources))"))
    neon.commit()
    return len(rows)


def _copy_chunks(local: Session, neon: Session, categories: list[str] | None) -> int:
    last_id = 0
    total = 0
    cat_sql = "AND s.category = ANY(:cats)" if categories else ""
    params_base: dict = {"cats": categories} if categories else {}
    while True:
        params = {**params_base, "last_id": last_id, "batch": BATCH}
        rows = local.execute(text(f"""
            SELECT dc.id, dc.source_id, dc.chunk_index, dc.content, dc.page_number, dc.metadata, dc.created_at
            FROM document_chunks dc
            JOIN sources s ON s.id = dc.source_id
            WHERE dc.id > :last_id {cat_sql}
            ORDER BY dc.id
            LIMIT :batch
        """), params).mappings().all()
        if not rows:
            break
        for row in rows:
            neon.execute(text("""
                INSERT INTO document_chunks
                    (id, source_id, chunk_index, content, page_number, embedding, metadata, created_at)
                VALUES
                    (:id, :source_id, :chunk_index, :content, :page_number, NULL,
                     CAST(:metadata AS jsonb), :created_at)
            """), _row_params(dict(row)))
        last_id = rows[-1]["id"]
        total += len(rows)
        neon.commit()
        print(f"  chunks: {total}", end="\r", flush=True)
    neon.execute(text(
        "SELECT setval('document_chunks_id_seq', (SELECT COALESCE(MAX(id), 1) FROM document_chunks))"
    ))
    neon.commit()
    print()
    return total


def _copy_tables(local: Session, neon: Session, categories: list[str] | None) -> int:
    if categories:
        rows = local.execute(text("""
            SELECT t.id, t.source_id, t.page_number, t.table_index, t.title, t.headers, t.rows,
                   t.raw_text, t.category, t.created_at
            FROM extracted_tables t
            JOIN sources s ON s.id = t.source_id
            WHERE s.category = ANY(:cats)
            ORDER BY t.id
        """), {"cats": categories}).mappings().all()
    else:
        rows = local.execute(text("""
            SELECT id, source_id, page_number, table_index, title, headers, rows, raw_text, category, created_at
            FROM extracted_tables ORDER BY id
        """)).mappings().all()
    for row in rows:
        neon.execute(text("""
            INSERT INTO extracted_tables
                (id, source_id, page_number, table_index, title, headers, rows, raw_text, category, created_at)
            VALUES
                (:id, :source_id, :page_number, :table_index, :title, CAST(:headers AS jsonb),
                 CAST(:rows AS jsonb), :raw_text, :category, :created_at)
        """), _row_params(dict(row)))
    neon.execute(text(
        "SELECT setval('extracted_tables_id_seq', (SELECT COALESCE(MAX(id), 1) FROM extracted_tables))"
    ))
    neon.commit()
    return len(rows)


def _copy_facts(local: Session, neon: Session, categories: list[str] | None) -> int:
    last_id = 0
    total = 0
    cat_sql = "AND category = ANY(:cats)" if categories else ""
    params_base: dict = {"cats": categories} if categories else {}
    while True:
        params = {**params_base, "last_id": last_id, "batch": BATCH}
        rows = local.execute(text(f"""
            SELECT id, source_id, category, fact_key, fact_value, numeric_value, unit, context, page_number, created_at
            FROM structured_facts
            WHERE id > :last_id {cat_sql}
            ORDER BY id
            LIMIT :batch
        """), params).mappings().all()
        if not rows:
            break
        for row in rows:
            neon.execute(text("""
                INSERT INTO structured_facts
                    (id, source_id, category, fact_key, fact_value, numeric_value, unit, context, page_number, created_at)
                VALUES
                    (:id, :source_id, :category, :fact_key, :fact_value, :numeric_value, :unit, :context, :page_number, :created_at)
            """), dict(row))
        last_id = rows[-1]["id"]
        total += len(rows)
        neon.commit()
        print(f"  facts: {total}", end="\r", flush=True)
    neon.execute(text(
        "SELECT setval('structured_facts_id_seq', (SELECT COALESCE(MAX(id), 1) FROM structured_facts))"
    ))
    neon.commit()
    print()
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Docker -> Neon")
    parser.add_argument(
        "--civic",
        action="store_true",
        help="constitution + elections + test_civique + general (~9k chunks, tient dans Neon gratuit)",
    )
    parser.add_argument(
        "--categories",
        help="Liste de categories separees par des virgules",
    )
    args = parser.parse_args()

    categories: list[str] | None = None
    if args.civic:
        categories = list(CIVIC_CATEGORIES)
    elif args.categories:
        categories = [c.strip() for c in args.categories.split(",") if c.strip()]

    from src.config import reload_env

    reload_env()
    neon_url = os.getenv("DATABASE_URL", "").strip()
    if not neon_url:
        print("DATABASE_URL manquant dans .env")
        sys.exit(1)
    if "-pooler" in neon_url:
        neon_url = neon_url.replace("-pooler.", ".")

    label = ", ".join(categories) if categories else "toutes categories"
    print("Source : Docker localhost:5433")
    print(f"Cible  : Neon — {label} (texte seul, FAST_MODE)")
    print()

    local_eng = _engine(LOCAL_URL)
    neon_eng = _engine(neon_url)

    with Session(local_eng) as local, Session(neon_eng) as neon:
        print("Vidage Neon...")
        _truncate_neon(neon)

        print("Copie sources...")
        n_src = _copy_sources(local, neon, categories)
        print(f"  {n_src} sources")

        print("Copie chunks...")
        n_chunks = _copy_chunks(local, neon, categories)
        print(f"  {n_chunks} chunks")

        print("Copie tableaux...")
        n_tbl = _copy_tables(local, neon, categories)
        print(f"  {n_tbl} tableaux")

        print("Copie faits...")
        n_facts = _copy_facts(local, neon, categories)
        print(f"  {n_facts} faits")

        stats = neon.execute(text("SELECT * FROM v_corpus_stats")).mappings().first()
        print()
        print("Neon apres sync :")
        for k, v in dict(stats).items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
