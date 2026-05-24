-- Extensión pgvector para búsqueda semántica
CREATE EXTENSION IF NOT EXISTS vector;

-- Vehículos (bastidores mock)
CREATE TABLE IF NOT EXISTS vehicles (
    vin VARCHAR(50) PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    family VARCHAR(100),
    displacement_cc INTEGER,
    market VARCHAR(20),
    model_year INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- FAQs del sistema
CREATE TABLE IF NOT EXISTS faqs (
    faq_id SERIAL PRIMARY KEY,
    model VARCHAR(100),
    category VARCHAR(100),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    usage_count INTEGER NOT NULL DEFAULT 0,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Árboles de diagnóstico (JSON versionado)
CREATE TABLE IF NOT EXISTS diagnostic_trees (
    tree_id VARCHAR(100) PRIMARY KEY,
    model VARCHAR(100),
    symptom VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    tree_json JSONB NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Casos históricos de diagnóstico
CREATE TABLE IF NOT EXISTS historical_cases (
    case_id VARCHAR(50) PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    symptom_category VARCHAR(100),
    case_text TEXT NOT NULL,
    final_diagnosis VARCHAR(255) NOT NULL,
    base_confidence NUMERIC(5,4) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Sesiones de conversación
CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vin VARCHAR(50),
    model VARCHAR(100),
    entry_point VARCHAR(50),
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP,
    total_steps INTEGER NOT NULL DEFAULT 0,
    final_result VARCHAR(255),
    success BOOLEAN,
    FOREIGN KEY (vin) REFERENCES vehicles(vin)
);

-- Estado vivo de sesión (una fila por sesión, se actualiza)
CREATE TABLE IF NOT EXISTS session_state (
    session_id UUID PRIMARY KEY,
    vin VARCHAR(50),
    model VARCHAR(100),
    current_symptom VARCHAR(100),
    current_node VARCHAR(100),
    state_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (vin) REFERENCES vehicles(vin)
);

-- Historial de mensajes de la conversación
CREATE TABLE IF NOT EXISTS messages (
    message_id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Logs de decisiones del sistema (trazabilidad)
CREATE TABLE IF NOT EXISTS decision_logs (
    log_id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    module_name VARCHAR(100) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Feedback final del usuario
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL UNIQUE,
    useful BOOLEAN NOT NULL,
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Chunks de conocimiento con embeddings vectoriales
-- DESIGN DECISION: dimension 768 para nomic-embed-text-v1_5 (Groq)
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    chunk_id BIGSERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(100) NOT NULL,
    model VARCHAR(100),
    symptom_category VARCHAR(100),
    text_chunk TEXT NOT NULL,
    embedding vector(768),
    lexical tsvector,
    base_confidence NUMERIC(5,4),
    chunk_index INTEGER NOT NULL DEFAULT 0,
    embedding_provider VARCHAR(50),
    embedding_model VARCHAR(100),
    metadata JSONB,
    embedding_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Jobs de generación de embeddings
CREATE TABLE IF NOT EXISTS embedding_jobs (
    job_id BIGSERIAL PRIMARY KEY,
    chunk_id BIGINT NOT NULL,
    provider VARCHAR(50),
    model VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (chunk_id) REFERENCES knowledge_chunks(chunk_id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_sessions_vin ON sessions(vin);
CREATE INDEX IF NOT EXISTS idx_sessions_model ON sessions(model);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_decision_logs_session_id ON decision_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_session_state_model ON session_state(model);
CREATE INDEX IF NOT EXISTS idx_historical_cases_model ON historical_cases(model);
CREATE INDEX IF NOT EXISTS idx_historical_cases_symptom_category ON historical_cases(symptom_category);
CREATE INDEX IF NOT EXISTS idx_faqs_model ON faqs(model);
CREATE INDEX IF NOT EXISTS idx_faqs_category ON faqs(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_model ON knowledge_chunks(model);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_source ON knowledge_chunks(source_type, source_id);

-- Índice único para idempotencia en seed de knowledge_chunks
CREATE UNIQUE INDEX IF NOT EXISTS idx_knowledge_chunks_unique
    ON knowledge_chunks(source_type, source_id, chunk_index);

-- Índice GIN para búsqueda léxica en knowledge_chunks
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_lexical
    ON knowledge_chunks USING GIN(lexical);

-- Trigger para actualizar el campo lexical automáticamente
CREATE OR REPLACE FUNCTION update_lexical() RETURNS trigger AS $$
BEGIN
    NEW.lexical := to_tsvector('spanish', COALESCE(NEW.text_chunk, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trig_knowledge_chunks_lexical ON knowledge_chunks;
CREATE TRIGGER trig_knowledge_chunks_lexical
    BEFORE INSERT OR UPDATE ON knowledge_chunks
    FOR EACH ROW EXECUTE FUNCTION update_lexical();

