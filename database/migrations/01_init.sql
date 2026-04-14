-- Esquema inicial de la POC (DDT seccion 13).
-- Alcance de esta fase: solo estructura de datos e indices.

-- Habilita el tipo VECTOR y operadores de similitud en PostgreSQL.
CREATE EXTENSION IF NOT EXISTS vector;

-- Catalogo de vehiculos identificables por bastidor (VIN).
CREATE TABLE vehicles (
    vin VARCHAR(50) PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    family VARCHAR(100),
    displacement_cc INTEGER,
    market VARCHAR(20),
    model_year INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Banco de FAQs por modelo/categoria.
-- embedding: vector semantico de la pregunta/respuesta para recuperacion por similitud.
CREATE TABLE faqs (
    faq_id SERIAL PRIMARY KEY,
    model VARCHAR(100),
    category VARCHAR(100),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    usage_count INTEGER NOT NULL DEFAULT 0,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    embedding VECTOR(1536),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Arboles de diagnostico versionados en formato JSON.
CREATE TABLE diagnostic_trees (
    tree_id VARCHAR(100) PRIMARY KEY,
    model VARCHAR(100),
    symptom VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    tree_json JSONB NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Casos historicos de diagnostico para soporte del flujo "Otros".
-- embedding: vector semantico del caso para busqueda vectorial.
CREATE TABLE historical_cases (
    case_id VARCHAR(50) PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    symptom_category VARCHAR(100),
    case_text TEXT NOT NULL,
    final_diagnosis VARCHAR(255) NOT NULL,
    base_confidence NUMERIC(5,4) NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Sesion conversacional principal (cabecera de la interaccion).
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
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

-- Estado vivo de sesion (contexto actual del flujo conversacional).
CREATE TABLE session_state (
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

-- Historial de mensajes de la conversacion (usuario/asistente/sistema).
CREATE TABLE messages (
    message_id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Trazabilidad de decisiones por modulo para auditoria y depuracion.
CREATE TABLE decision_logs (
    log_id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    module_name VARCHAR(100) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Feedback final de utilidad de cada sesion.
CREATE TABLE feedback (
    feedback_id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL UNIQUE,
    useful BOOLEAN NOT NULL,
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Indices relacionales para acelerar consultas de sesion, trazas y filtros por modelo.
CREATE INDEX idx_sessions_vin ON sessions(vin);
CREATE INDEX idx_sessions_model ON sessions(model);
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_decision_logs_session_id ON decision_logs(session_id);
CREATE INDEX idx_session_state_model ON session_state(model);
CREATE INDEX idx_historical_cases_model ON historical_cases(model);
CREATE INDEX idx_historical_cases_symptom_category ON historical_cases(symptom_category);
CREATE INDEX idx_faqs_model ON faqs(model);
CREATE INDEX idx_faqs_category ON faqs(category);

-- Indice vectorial HNSW para vecinos mas cercanos aproximados.
-- Se usa para encontrar rapido casos historicos semanticamente similares.
CREATE INDEX idx_historical_cases_embedding_hnsw
    ON historical_cases USING hnsw (embedding vector_cosine_ops);

-- Indice vectorial HNSW para FAQ semantica.
CREATE INDEX idx_faqs_embedding_hnsw
    ON faqs USING hnsw (embedding vector_cosine_ops);