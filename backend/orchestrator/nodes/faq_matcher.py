"""Nodo LangGraph: busca coincidencias en FAQs mediante búsqueda semántica (Ruta B)."""

import logging
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import AsyncSessionLocal
from models.knowledge import FAQ
from models.knowledge_chunk import KnowledgeChunk
from orchestrator.state import ConversationState
from services.groq_client import get_embedding, generate_response
from services.tracing import trace_decision

logger = logging.getLogger(__name__)


async def faq_matcher_node(state: ConversationState) -> ConversationState:
    """
    Ruta B: Busca la consulta del usuario en FAQs.
    1. Genera embedding del texto del usuario.
    2. Busca en knowledge_chunks con pgvector (similitud coseno).
    3. Si similitud >= umbral → responde con FAQ.
    4. Si no → deriva a free_text_node (Ruta C).

    RN-NEG-004: Si la consulta textual encaja claramente con una FAQ, se responde por FAQ.
    """
    user_message = state["user_message"].strip()
    model = state.get("model")
    session_id = state["session_id"]

    logger.info("FAQ matcher iniciado [session=%s model=%s]", session_id, model)

    async with AsyncSessionLocal() as db:
        # Intentar búsqueda semántica si hay chunks con embeddings
        best_chunk, best_score = await _semantic_search_faq(db, user_message, model)

        if best_chunk and best_score >= settings.similarity_threshold:
            # Recuperar la FAQ completa
            faq_result = await db.execute(
                select(FAQ).where(FAQ.faq_id == int(best_chunk.source_id))
            )
            faq = faq_result.scalar_one_or_none()

            if faq:
                # Incrementar contador de uso
                await db.execute(
                    update(FAQ).where(FAQ.faq_id == faq.faq_id).values(usage_count=FAQ.usage_count + 1)
                )

                # Redactar respuesta con LLM
                answer_text = await _build_faq_response(user_message, faq.question, faq.answer)

                await trace_decision(
                    session_id=session_id,
                    module_name="faq_matcher",
                    input_data={"query": user_message, "model": model},
                    output_data={
                        "matched": True,
                        "faq_id": faq.faq_id,
                        "similarity": best_score,
                        "question": faq.question,
                    },
                    db=db,
                )
                await db.commit()

                logger.info(
                    "FAQ match encontrado: faq_id=%d score=%.3f [session=%s]",
                    faq.faq_id, best_score, session_id,
                )

                return {
                    **state,
                    "current_node": "show_menu",
                    "message_type": "text",
                    "assistant_message": answer_text,
                    "options": [
                        {"id": "menu", "label": "Volver al menú principal"},
                        {"id": "finish", "label": "Finalizar sesión"},
                    ],
                    "route": "faq",
                }

        # No hay match suficiente → derivar a Ruta C
        await trace_decision(
            session_id=session_id,
            module_name="faq_matcher",
            input_data={"query": user_message, "model": model},
            output_data={"matched": False, "redirect": "free_text_node"},
            db=db,
        )
        await db.commit()

        logger.info("FAQ no encontrada → derivando a free_text_node [session=%s]", session_id)

        return {
            **state,
            "route": "other",
            "current_node": "free_text_node",
            "message_type": "text",
            "assistant_message": "",
            "options": None,
        }


async def _semantic_search_faq(
    db: AsyncSession,
    query: str,
    model: str | None,
) -> tuple[KnowledgeChunk | None, float]:
    """
    Busca en knowledge_chunks (source_type='faq') usando pgvector.
    Devuelve el mejor chunk y su score de similitud.
    DESIGN DECISION: Si no hay embeddings disponibles (status != 'done'),
    hace búsqueda lexical básica como fallback.
    """
    # Intentar generar embedding de la query
    try:
        query_embedding = await get_embedding(query)
    except Exception as exc:
        logger.warning("No se pudo generar embedding para FAQ search: %s", exc)
        query_embedding = None

    if query_embedding:
        # Búsqueda vectorial con pgvector — SQL raw con operador <=>
        from sqlalchemy import text as sql_text
        embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

        # Filtrar por modelo o FAQ general (model IS NULL)
        sql = sql_text("""
            SELECT chunk_id, source_id, text_chunk,
                   1 - (embedding::vector <=> :emb::vector) AS similarity
            FROM knowledge_chunks
            WHERE source_type = 'faq'
              AND embedding_status = 'done'
              AND (:model IS NULL OR model = :model OR model IS NULL)
            ORDER BY embedding::vector <=> :emb::vector
            LIMIT 1
        """)
        result = await db.execute(sql, {"emb": embedding_str, "model": model})
        row = result.fetchone()

        if row:
            chunk_result = await db.execute(
                select(KnowledgeChunk).where(KnowledgeChunk.chunk_id == row.chunk_id)
            )
            chunk = chunk_result.scalar_one_or_none()
            return chunk, float(row.similarity)

    # Fallback: búsqueda por palabras clave en text_chunk
    chunks_result = await db.execute(
        select(KnowledgeChunk).where(
            KnowledgeChunk.source_type == "faq",
        )
    )
    chunks = chunks_result.scalars().all()

    query_lower = query.lower()
    best_chunk = None
    best_score = 0.0

    for chunk in chunks:
        # Score léxico simple: proporción de palabras del query que aparecen en el texto
        words = [w for w in query_lower.split() if len(w) > 3]
        if not words:
            continue
        matches = sum(1 for w in words if w in chunk.text_chunk.lower())
        score = matches / len(words)
        if score > best_score:
            best_score = score
            best_chunk = chunk

    # El umbral léxico es más permisivo que el vectorial
    return (best_chunk, best_score * 0.8) if best_chunk else (None, 0.0)


async def _build_faq_response(query: str, faq_question: str, faq_answer: str) -> str:
    """Usa el LLM para redactar la respuesta de FAQ de forma natural."""
    try:
        prompt = (
            f"Eres un asistente técnico de motocicletas. El usuario pregunta: '{query}'\n\n"
            f"La respuesta oficial es: {faq_answer}\n\n"
            "Redacta una respuesta clara y directa en español, sin inventar información adicional."
        )
        response = await generate_response(prompt)
        return response
    except Exception as exc:
        logger.warning("Error generando respuesta FAQ con LLM: %s. Usando respuesta directa.", exc)
        return faq_answer
