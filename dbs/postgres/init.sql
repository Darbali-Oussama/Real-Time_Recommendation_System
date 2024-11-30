CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS item_embeddings (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    embedding vector(100) NOT NULL
);