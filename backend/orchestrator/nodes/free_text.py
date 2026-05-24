"""Nodo LangGraph: procesa texto libre mediante historial híbrido (Ruta C)."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import AsyncSessionLocal
from models.knowledge import HistoricalCase
from orchestrator.state import ConversationState
from services.groq_client import extract_tags, generate_free_text_diagnosis, get_embedding
from services.ranking import rank_candidates
from services.response_builder import build_free_text_response
from services.tracing import trace_decision

logger = logging.getLogger(__name__)

# Mapa de categorías de síntoma conocidas → tree_id disponible
# Si el top candidato encaja con una categoría aquí, se sugiere reconducción al árbol
SYMPTOM_TO_TREE: dict[str, str] = {
    "paradas de motor": "AK550_MOTOR_V1",
    "paro de motor": "AK550_MOTOR_V1",
    "motor se para": "AK550_MOTOR_V1",
    "testigo celp": "AK550_CELP_V1",
    "celp encendido": "AK550_CELP_V1",
    "luz celp": "AK550_CELP_V1",
    "avería electrónica": "AK550_CELP_V1",
    "problemas de arranque": "AK550_ARRANQUE_V1",
    "arranque": "AK550_ARRANQUE_V1",
    "no arranca": "AK550_ARRANQUE_V1",
    "dificultad de arranque": "AK550_ARRANQUE_V1",
    "consumo": "AK550_CONSUMO_V1",
    "consumo excesivo": "AK550_CONSUMO_V1",
    "gasta mucha gasolina": "AK550_CONSUMO_V1",
}

RECONDUCTION_THRESHOLD = 0.72  # Confianza mínima para sugerir árbol


async def free_text_node(state: ConversationState) -> ConversationState:
    """
    Ruta C: Procesa entrada libre del usuario.
    1. Extrae tags con LLM.
    2. Filtra históricos por modelo (RN-NEG-006).
    3. Ranking híbrido de candidatos.
    4. Devuelve top-3 hipótesis con contrato estándar.
    """
    user_message = state["user_message"].strip()
    model = state.get("model")
    session_id = state["session_id"]

    logger.info("free_text_node iniciado [session=%s model=%s]", session_id, model)

    async with AsyncSessionLocal() as db:
        # 1. Extraer tags con LLM — módulo: free_text_parser (DDT §21)
        tags_data: dict = {}
        try:
            tags_data = await extract_tags(user_message, model or "")
            logger.debug("Tags extraídos: %s [session=%s]", tags_data, session_id)
        except Exception as exc:
            logger.warning("Error extrayendo tags: %s [session=%s]", exc, session_id)

        await trace_decision(
            session_id=session_id,
            module_name="free_text_parser",
            input_data={"query": user_message, "model": model},
            output_data={"tags": tags_data},
            db=db,
        )

        # 2. Generar embedding del texto del usuario
        query_embedding: list[float] | None = None
        try:
            query_embedding = await get_embedding(user_message)
        except Exception as exc:
            logger.warning("Error generando embedding: %s [session=%s]", exc, session_id)

        # 3. Recuperar candidatos históricos filtrados por modelo — módulo: historical_retrieval (DDT §21)
        candidates = await _get_historical_candidates(db, model)

        await trace_decision(
            session_id=session_id,
            module_name="historical_retrieval",
            input_data={"model": model, "tags": tags_data},
            output_data={"candidates_count": len(candidates), "case_ids": [c["case_id"] for c in candidates[:5]]},
            db=db,
        )

        if not candidates:
            await db.commit()
            return {
                **state,
                "current_node": "show_menu",
                "message_type": "text",
                "assistant_message": (
                    "No encontré casos históricos similares para tu vehículo. "
                    "Te recomiendo contactar con el servicio técnico oficial."
                ),
                "options": [
                    {"id": "menu", "label": "Volver al menú"},
                    {"id": "finish", "label": "Finalizar sesión"},
                ],
            }

        # 4. Ranking híbrido — módulo: hybrid_ranking (DDT §21)
        ranked = rank_candidates(
            candidates=candidates,
            query=user_message,
            query_embedding=query_embedding,
            user_model=model,
        )

        top_candidates = ranked[: settings.top_k_results]

        await trace_decision(
            session_id=session_id,
            module_name="hybrid_ranking",
            input_data={"candidates_count": len(candidates), "query": user_message},
            output_data={
                "top_diagnoses": [c["final_diagnosis"] for c in top_candidates],
                "top_scores": [c["score"] for c in top_candidates],
            },
            db=db,
        )

        # 5. Generar narrativa diagnóstica con LLM (respuesta personalizada al técnico)
        narrative = "He analizado tu consulta y encontré las siguientes hipótesis."
        try:
            narrative = await generate_free_text_diagnosis(
                user_message=user_message,
                model=model or "el vehículo",
                top_candidates=top_candidates,
                tags_data=tags_data,
            )
            logger.info("Narrativa LLM generada (%d chars) [session=%s]", len(narrative), session_id)
        except Exception as exc:
            logger.warning("Error narrativa LLM: %s → usando texto por defecto [session=%s]", exc, session_id)

        # 6. Construir respuesta estructurada (card de diagnóstico) — módulo: response_builder (DDT §21)
        diagnosis_result = build_free_text_response(
            top_candidates=top_candidates,
            user_query=user_message,
            tags_data=tags_data,
        )

        await trace_decision(
            session_id=session_id,
            module_name="response_builder",
            input_data={"source_type": "historical", "top_candidates_count": len(top_candidates)},
            output_data={
                "primary_hypothesis": diagnosis_result.get("primary_hypothesis"),
                "confidence": diagnosis_result.get("confidence"),
                "source_type": diagnosis_result.get("source_type"),
            },
            db=db,
        )

        # 7. Detectar si el top candidato encaja con un árbol conocido (reconducción)
        suggests_tree: str | None = None
        if top_candidates:
            top = top_candidates[0]
            top_score = top.get("score", 0.0)
            top_symptom = (top.get("symptom_category") or "").lower()
            if top_score >= RECONDUCTION_THRESHOLD:
                for keyword, tree_id in SYMPTOM_TO_TREE.items():
                    if keyword in top_symptom:
                        suggests_tree = tree_id
                        logger.info(
                            "Reconducción sugerida: %s → %s [session=%s]",
                            top_symptom, tree_id, session_id,
                        )
                        break

        await db.commit()

        logger.info(
            "free_text_node completado: %d hipótesis [session=%s]",
            len(top_candidates), session_id,
        )

        return {
            **state,
            "current_node": "show_menu",
            "message_type": "diagnosis",
            "assistant_message": narrative,
            "options": [
                {"id": "menu", "label": "Nueva consulta"},
                {"id": "finish", "label": "Finalizar sesión"},
            ],
            "diagnosis_result": diagnosis_result,
            "route": "other",
            "suggests_tree": suggests_tree,
        }


async def _get_historical_candidates(
    db: AsyncSession,
    model: str | None,
) -> list[dict]:
    """
    Recupera casos históricos filtrados por modelo (RN-NEG-006).
    Devuelve lista de dicts con los datos del caso.
    """
    query = select(HistoricalCase)
    if model:
        query = query.where(HistoricalCase.model == model)

    result = await db.execute(query)
    cases = result.scalars().all()

    return [
        {
            "case_id": c.case_id,
            "model": c.model,
            "symptom_category": c.symptom_category,
            "case_text": c.case_text,
            "final_diagnosis": c.final_diagnosis,
            "base_confidence": float(c.base_confidence),
        }
        for c in cases
    ]
