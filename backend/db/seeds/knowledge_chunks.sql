-- ─── Knowledge Chunks — Seed inicial ─────────────────────────────────────────
-- Pobla knowledge_chunks desde FAQs y casos históricos.
-- El trigger trig_knowledge_chunks_lexical calcula automáticamente el tsvector.
-- embedding_status='pending': los embeddings se generarán al vuelo por el sistema.
-- Hasta que haya embeddings, el faq_matcher usa el fallback léxico (Python).

-- ─── Chunks de FAQs ──────────────────────────────────────────────────────────
INSERT INTO knowledge_chunks (
    source_type, source_id, model, symptom_category,
    text_chunk, embedding_status, chunk_index
)
SELECT
    'faq',
    faq_id::TEXT,
    model,
    category,
    question || E'\n' || answer,  -- combina pregunta + respuesta para mejor recall
    'pending',
    0
FROM faqs
ON CONFLICT (source_type, source_id, chunk_index) DO NOTHING;

-- ─── Chunks de casos históricos ──────────────────────────────────────────────
INSERT INTO knowledge_chunks (
    source_type, source_id, model, symptom_category,
    text_chunk, base_confidence, embedding_status, chunk_index
)
SELECT
    'historical',
    case_id,
    model,
    symptom_category,
    case_text || E'\nDiagnóstico: ' || final_diagnosis,
    base_confidence,
    'pending',
    0
FROM historical_cases
ON CONFLICT (source_type, source_id, chunk_index) DO NOTHING;
