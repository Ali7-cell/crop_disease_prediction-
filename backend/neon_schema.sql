-- ============================================
-- AGRILUX DATABASE SCHEMA — Neon PostgreSQL
-- Run this in Neon SQL Editor to create all tables
-- ============================================

-- 1. Create enum type for prediction types
CREATE TYPE prediction_type AS ENUM ('crop', 'fertilizer', 'yield');

-- 2. Users table
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100)  NOT NULL,
    email         VARCHAR(255)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    created_at    TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- Index on email for fast login lookups
CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

-- 3. Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type        prediction_type NOT NULL,
    input_data  TEXT           NOT NULL,   -- JSON string
    result      VARCHAR(255)   NOT NULL,
    confidence  FLOAT,                     -- NULL for yield (regressor)
    created_at  TIMESTAMP      NOT NULL DEFAULT NOW()
);

-- Index on user_id for fast history lookups
CREATE INDEX IF NOT EXISTS ix_predictions_user_id ON predictions (user_id);

-- Composite index for filtered history queries (user + type)
CREATE INDEX IF NOT EXISTS ix_predictions_user_type ON predictions (user_id, type);

-- ============================================
-- VERIFY: Run these after creating tables
-- ============================================

-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check columns of users table
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- Check columns of predictions table
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'predictions' 
ORDER BY ordinal_position;
