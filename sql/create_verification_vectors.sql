-- ==============================================================================
-- EMAILAI VERIFICATION RAG - SUPABASE PGVECTOR ISOLATED SCHEMA
-- ==============================================================================
-- This standalone SQL script creates an isolated vector table for document
-- verification in Supabase without modifying or touching any existing tables.
-- Run this in your Supabase SQL Editor:
-- https://supabase.com/dashboard/project/_/sql
-- ==============================================================================

-- 1. Enable the pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the dedicated verification vectors table
-- Compatible with LlamaIndex PGVectorStore schema
CREATE TABLE IF NOT EXISTS emailai_verification_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    node_id VARCHAR(255) UNIQUE,
    embedding vector(1536), -- Default 1536 dimensions (compatible with OpenAI text-embedding-3 or NVIDIA NIM embeddings)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create metadata and lookup indexes for sub-millisecond filtering
CREATE INDEX IF NOT EXISTS idx_verification_vectors_node_id 
    ON emailai_verification_vectors(node_id);

CREATE INDEX IF NOT EXISTS idx_verification_vectors_metadata 
    ON emailai_verification_vectors USING GIN (metadata);

CREATE INDEX IF NOT EXISTS idx_verification_vectors_category 
    ON emailai_verification_vectors ((metadata->>'category'));

CREATE INDEX IF NOT EXISTS idx_verification_vectors_domain 
    ON emailai_verification_vectors ((metadata->>'domain'));

-- 4. Create an HNSW index on embeddings for fast cosine similarity search
-- Note: Requires at least a few rows to build optimally; HNSW provides higher recall than IVFFlat
CREATE INDEX IF NOT EXISTS idx_verification_vectors_embedding_hnsw
    ON emailai_verification_vectors 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- 5. Helper function for fast cosine similarity search via Supabase RPC (fallback interface)
CREATE OR REPLACE FUNCTION match_verification_vectors(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.65,
    match_count int DEFAULT 5,
    filter_category text DEFAULT NULL,
    filter_domain text DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    text TEXT,
    metadata JSONB,
    node_id VARCHAR(255),
    similarity float
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.id,
        v.text,
        v.metadata,
        v.node_id,
        1 - (v.embedding <=> query_embedding) AS similarity
    FROM emailai_verification_vectors v
    WHERE (1 - (v.embedding <=> query_embedding)) > match_threshold
      AND (filter_category IS NULL OR v.metadata->>'category' = filter_category)
      AND (filter_domain IS NULL OR v.metadata->>'domain' = filter_domain)
    ORDER BY v.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
