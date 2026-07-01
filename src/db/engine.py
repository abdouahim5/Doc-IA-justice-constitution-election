"""Connexion PostgreSQL."""

import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

import src.startup  # noqa: F401
from src.config import reload_env
from src.db.models import Base


def get_database_url() -> str:
    reload_env()
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://docia:docia_secret@localhost:5433/docia_fr",
    )


_engine = None
_SessionLocal = None


def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(
            get_database_url(),
            pool_pre_ping=True,
            pool_size=5,
            pool_timeout=3,
            connect_args={"connect_timeout": 3},
        )
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    return _engine


def get_session() -> Session:
    get_engine()
    return _SessionLocal()


def init_db() -> None:
    """Crée les tables (si pas Docker init)."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        conn.commit()
    Base.metadata.create_all(engine)
    with engine.connect() as conn:
        conn.execute(text("DROP VIEW IF EXISTS v_corpus_stats"))
        conn.execute(text("""
            CREATE VIEW v_corpus_stats AS
            SELECT
                (SELECT COUNT(*) FROM sources) AS total_sources,
                (SELECT COUNT(*) FROM sources WHERE category = 'constitution') AS constitution_sources,
                (SELECT COUNT(*) FROM sources WHERE category = 'elections') AS elections_sources,
                (SELECT COUNT(*) FROM sources WHERE category = 'justice') AS justice_sources,
                (SELECT COUNT(*) FROM sources WHERE category = 'test_civique') AS test_civique_sources,
                (SELECT COUNT(*) FROM document_chunks) AS total_chunks,
                (SELECT COUNT(*) FROM extracted_tables) AS total_tables,
                (SELECT COUNT(*) FROM structured_facts) AS total_facts,
                (SELECT COUNT(*) FROM query_cache) AS cached_queries
        """))
        conn.commit()


def check_connection() -> tuple[bool, str]:
    try:
        with get_engine().connect() as conn:
            row = conn.execute(text("SELECT 1")).scalar()
            stats = conn.execute(
                text("SELECT total_chunks, total_facts FROM v_corpus_stats")
            ).fetchone()
        if stats:
            return True, f"PostgreSQL OK — {stats[0]} chunks, {stats[1]} faits"
        return True, "PostgreSQL OK"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
