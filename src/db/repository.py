"""Accès données PostgreSQL — recherche vectorielle, faits, cache."""

import hashlib
import re
from datetime import datetime, timezone

from sqlalchemy import delete, func, select, text
from sqlalchemy.orm import Session

from src.db.models import DocumentChunk, ExtractedTable, QueryCache, Source, StructuredFact


def _normalize_question(q: str) -> str:
    return re.sub(r"\s+", " ", q.strip().lower())


def question_hash(question: str) -> str:
    return hashlib.sha256(_normalize_question(question).encode()).hexdigest()


class CorpusRepository:
  def __init__(self, session: Session):
      self.session = session

  def get_stats(self) -> dict:
      row = self.session.execute(text("SELECT * FROM v_corpus_stats")).mappings().first()
      return dict(row) if row else {}

  def upsert_source(self, filename: str, filepath: str, category: str, source_type: str, page_count: int = 0) -> Source:
      src = self.session.execute(
          select(Source).where(Source.filename == filename)
      ).scalar_one_or_none()
      if src:
          src.category = category
          src.filepath = filepath
          src.page_count = page_count
          self.session.execute(delete(DocumentChunk).where(DocumentChunk.source_id == src.id))
          self.session.execute(delete(ExtractedTable).where(ExtractedTable.source_id == src.id))
          self.session.execute(delete(StructuredFact).where(StructuredFact.source_id == src.id))
      else:
          src = Source(
              filename=filename, filepath=filepath, category=category,
              source_type=source_type, page_count=page_count,
          )
          self.session.add(src)
      self.session.flush()
      return src

  def add_chunks(self, source_id: int, chunks: list[dict]) -> int:
      for i, ch in enumerate(chunks):
          self.session.add(DocumentChunk(
              source_id=source_id,
              chunk_index=i,
              content=ch["content"],
              page_number=ch.get("page_number"),
              embedding=ch.get("embedding"),
              metadata_=ch.get("metadata", {}),
          ))
      return len(chunks)

  def add_table(self, source_id: int, data: dict) -> None:
      self.session.add(ExtractedTable(source_id=source_id, **data))

  def add_fact(self, source_id: int, data: dict) -> None:
      self.session.add(StructuredFact(source_id=source_id, **data))

  def search_vector(
      self, embedding: list[float], category: str | None = None, limit: int = 6
  ) -> list[tuple[DocumentChunk, float, str]]:
      """Recherche sémantique pgvector."""
      vec_str = "[" + ",".join(str(x) for x in embedding) + "]"
      cat_filter = "AND s.category = :cat" if category else ""
      sql = text(f"""
          SELECT c.id, c.content, c.page_number, c.metadata,
                 s.filename, s.category,
                 1 - (c.embedding <=> CAST(:vec AS vector)) AS score
          FROM document_chunks c
          JOIN sources s ON s.id = c.source_id
          WHERE c.embedding IS NOT NULL {cat_filter}
          ORDER BY c.embedding <=> CAST(:vec AS vector)
          LIMIT :lim
      """)
      params: dict = {"vec": vec_str, "lim": limit}
      if category:
          params["cat"] = category
      rows = self.session.execute(sql, params).fetchall()
      results = []
      for row in rows:
          chunk = DocumentChunk(
              id=row[0], content=row[1], page_number=row[2],
              metadata_=row[3] or {},
          )
          results.append((chunk, float(row[6]), row[4]))
      return results

  def search_text(
      self, query: str, category: str | None = None, limit: int = 8
  ) -> list[tuple[str, str, float]]:
      """Recherche full-text trigram."""
      cat_filter = "AND s.category = :cat" if category else ""
      words = " ".join(w for w in query.split() if len(w) >= 2)[:80]
      short = query.strip()[:40]
      prefix_filter = ""
      if len(short) >= 3 and len(short.split()) == 1:
          prefix_filter = " OR c.content ILIKE :pfx"
      sql = text(f"""
          SELECT c.content, s.filename,
                 similarity(c.content, :q) AS score
          FROM document_chunks c
          JOIN sources s ON s.id = c.source_id
          WHERE c.content ILIKE '%' || :q2 || '%'
             OR similarity(c.content, :q) > 0.05
             {prefix_filter}
          {cat_filter}
          ORDER BY score DESC
          LIMIT :lim
      """)
      params: dict = {"q": query, "q2": words or short, "lim": limit}
      if prefix_filter:
          params["pfx"] = f"%{short}%"
      if category:
          params["cat"] = category
      try:
          return [(r[0], r[1], float(r[2])) for r in self.session.execute(sql, params).fetchall()]
      except Exception:
          return []

  def search_chunks_patterns(
      self,
      patterns: list[str],
      category: str | None = None,
      limit: int = 8,
  ) -> list[tuple[str, str, float]]:
      """Recherche ILIKE sur plusieurs motifs (ex. dates d'élections)."""
      if not patterns:
          return []
      cat_filter = "AND s.category = :cat" if category else ""
      conditions = " OR ".join(f"c.content ILIKE :p{i}" for i in range(len(patterns)))
      sql = text(f"""
          SELECT c.content, s.filename, 1.0 AS score
          FROM document_chunks c
          JOIN sources s ON s.id = c.source_id
          WHERE ({conditions}) {cat_filter}
          GROUP BY s.filename, c.content
          LIMIT :lim
      """)
      params: dict = {f"p{i}": p for i, p in enumerate(patterns)}
      params["lim"] = limit
      if category:
          params["cat"] = category
      return [(r[0], r[1], float(r[2])) for r in self.session.execute(sql, params).fetchall()]

  def search_facts(
      self, query: str, category: str | None = None, limit: int = 10
  ) -> list[StructuredFact]:
      q = f"%{query[:60]}%"
      stmt = select(StructuredFact).where(
          (StructuredFact.fact_key.ilike(q)) | (StructuredFact.fact_value.ilike(q))
          | (StructuredFact.context.ilike(q))
      )
      if category:
          stmt = stmt.where(StructuredFact.category == category)
      return list(self.session.execute(stmt.limit(limit)).scalars())

  def search_tables(
      self, query: str, category: str | None = None, limit: int = 5
  ) -> list[ExtractedTable]:
      stmt = select(ExtractedTable).where(ExtractedTable.raw_text.ilike(f"%{query[:50]}%"))
      if category:
          stmt = stmt.where(ExtractedTable.category == category)
      return list(self.session.execute(stmt.limit(limit)).scalars())

  def get_cache(self, question: str) -> QueryCache | None:
      h = question_hash(question)
      return self.session.execute(
          select(QueryCache).where(QueryCache.question_hash == h)
      ).scalar_one_or_none()

  def set_cache(self, question: str, answer: str, agent: str, sources: list) -> None:
      h = question_hash(question)
      existing = self.get_cache(question)
      if existing:
          existing.answer = answer
          existing.agent_used = agent
          existing.sources = sources
          existing.hit_count += 1
          existing.last_hit_at = datetime.now(timezone.utc)
          return
      self.session.add(QueryCache(
          question_hash=h, question=question, answer=answer,
          agent_used=agent, sources=sources,
      ))

  def delete_cache(self, question: str) -> bool:
      cached = self.get_cache(question)
      if not cached:
          return False
      self.session.delete(cached)
      return True

  def clear_cache(self) -> int:
      result = self.session.execute(text("DELETE FROM query_cache"))
      return result.rowcount or 0

  def bump_cache_hit(self, cache: QueryCache) -> None:
      cache.hit_count += 1
      cache.last_hit_at = datetime.now(timezone.utc)
