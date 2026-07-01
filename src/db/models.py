"""Modèles SQLAlchemy — corpus France constitution & élections."""

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    filepath: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(Text, default="general")
    source_type: Mapped[str] = mapped_column(Text, default="pdf")
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    indexed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="source", cascade="all, delete-orphan")
    tables: Mapped[list["ExtractedTable"]] = relationship(back_populates="source", cascade="all, delete-orphan")
    facts: Mapped[list["StructuredFact"]] = relationship(back_populates="source")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer)
    embedding = mapped_column(Vector(1536), nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source: Mapped["Source"] = relationship(back_populates="chunks")


class ExtractedTable(Base):
    __tablename__ = "extracted_tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    page_number: Mapped[int | None] = mapped_column(Integer)
    table_index: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str | None] = mapped_column(Text)
    headers: Mapped[dict | None] = mapped_column(JSONB)
    rows: Mapped[dict] = mapped_column(JSONB, nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source: Mapped["Source"] = relationship(back_populates="tables")


class StructuredFact(Base):
    __tablename__ = "structured_facts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id", ondelete="SET NULL"))
    category: Mapped[str] = mapped_column(Text, nullable=False)
    fact_key: Mapped[str] = mapped_column(Text, nullable=False)
    fact_value: Mapped[str] = mapped_column(Text, nullable=False)
    numeric_value: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(Text)
    context: Mapped[str | None] = mapped_column(Text)
    page_number: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source: Mapped["Source | None"] = relationship(back_populates="facts")


class QueryCache(Base):
    __tablename__ = "query_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    agent_used: Mapped[str | None] = mapped_column(Text)
    sources: Mapped[dict] = mapped_column(JSONB, default=list)
    hit_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_hit_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
