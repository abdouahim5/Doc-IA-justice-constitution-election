-- DocIA France — Constitution & Élections
-- Exécuté automatiquement au premier démarrage Docker

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Catégories : constitution | elections | justice | test_civique | general
CREATE TABLE IF NOT EXISTS sources (
    id              SERIAL PRIMARY KEY,
    filename        TEXT NOT NULL UNIQUE,
    filepath        TEXT,
    category        TEXT NOT NULL DEFAULT 'general',
    source_type     TEXT NOT NULL DEFAULT 'pdf',
    page_count      INT DEFAULT 0,
    metadata        JSONB DEFAULT '{}',
    indexed_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sources_category ON sources(category);
CREATE INDEX IF NOT EXISTS idx_sources_filename_trgm ON sources USING gin (filename gin_trgm_ops);

-- Chunks texte + embedding (1536 = text-embedding-3-small)
CREATE TABLE IF NOT EXISTS document_chunks (
    id              SERIAL PRIMARY KEY,
    source_id       INT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    chunk_index     INT NOT NULL,
    content         TEXT NOT NULL,
    page_number     INT,
    embedding       vector(1536),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chunks_source ON document_chunks(source_id);
CREATE INDEX IF NOT EXISTS idx_chunks_category ON document_chunks((metadata->>'category'));
CREATE INDEX IF NOT EXISTS idx_chunks_content_trgm ON document_chunks USING gin (content gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON document_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Tableaux extraits des PDF
CREATE TABLE IF NOT EXISTS extracted_tables (
    id              SERIAL PRIMARY KEY,
    source_id       INT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    page_number     INT,
    table_index     INT DEFAULT 0,
    title           TEXT,
    headers         JSONB,
    rows            JSONB NOT NULL,
    raw_text        TEXT,
    category        TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tables_source ON extracted_tables(source_id);
CREATE INDEX IF NOT EXISTS idx_tables_category ON extracted_tables(category);

-- Chiffres / faits structurés (extraction rapide)
CREATE TABLE IF NOT EXISTS structured_facts (
    id              SERIAL PRIMARY KEY,
    source_id       INT REFERENCES sources(id) ON DELETE SET NULL,
    category        TEXT NOT NULL,
    fact_key        TEXT NOT NULL,
    fact_value      TEXT NOT NULL,
    numeric_value   DOUBLE PRECISION,
    unit            TEXT,
    context         TEXT,
    page_number     INT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_facts_category ON structured_facts(category);
CREATE INDEX IF NOT EXISTS idx_facts_key_trgm ON structured_facts USING gin (fact_key gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_facts_value_trgm ON structured_facts USING gin (fact_value gin_trgm_ops);

-- Cache réponses instantanées
CREATE TABLE IF NOT EXISTS query_cache (
    id              SERIAL PRIMARY KEY,
    question_hash   TEXT NOT NULL UNIQUE,
    question        TEXT NOT NULL,
    answer          TEXT NOT NULL,
    agent_used      TEXT,
    sources         JSONB DEFAULT '[]',
    hit_count       INT DEFAULT 1,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_hit_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cache_hash ON query_cache(question_hash);

-- Vue statistiques
CREATE OR REPLACE VIEW v_corpus_stats AS
SELECT
    (SELECT COUNT(*) FROM sources) AS total_sources,
    (SELECT COUNT(*) FROM sources WHERE category = 'constitution') AS constitution_sources,
    (SELECT COUNT(*) FROM sources WHERE category = 'elections') AS elections_sources,
    (SELECT COUNT(*) FROM sources WHERE category = 'justice') AS justice_sources,
    (SELECT COUNT(*) FROM sources WHERE category = 'test_civique') AS test_civique_sources,
    (SELECT COUNT(*) FROM document_chunks) AS total_chunks,
    (SELECT COUNT(*) FROM extracted_tables) AS total_tables,
    (SELECT COUNT(*) FROM structured_facts) AS total_facts,
    (SELECT COUNT(*) FROM query_cache) AS cached_queries;
