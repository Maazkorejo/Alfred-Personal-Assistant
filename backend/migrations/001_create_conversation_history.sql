-- Migration: 001_create_conversation_history
-- Creates the conversation_history table for storing chat turns

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS conversation_history (
    id          SERIAL PRIMARY KEY,
    role        VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    embedding   vector(1024),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversation_history_created_at
    ON conversation_history (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversation_history_embedding
    ON conversation_history USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
