"""Nodo LangGraph: ejecuta el árbol de diagnóstico guiado (Ruta A)."""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from core.exceptions import TreeNodeNotFoundError
from models.knowledge import DiagnosticTree
from models.session import SessionState
from orchestrator.state import ConversationState
from services.response_builder import build_diagnosis_response
from services.tracing import trace_decision

logger = logging.getLogger(__name__)

# Mapa de sinónimos de respuesta para normalizar Sí/No
ANSWER_ALIASES: dict[str, str] = {
    "sí": "si",
    "si": "si",
    "yes": "si",
    "s": "si",
    "no": "no",
    "n": "no",
    "nope": "no",
}


async def tree_engine_node(state: ConversationState) -> ConversationState:
    """
    Ruta A: Motor del árbol de diagnóstico.
    - Si tree_node es None → carga el árbol y presenta el nodo inicial.
    - Si tree_node existe → procesa la respuesta del usuario y avanza.
    - Cuando llega a un nodo 'diagnosis' → devuelve resultado final.
    """
    session_id = state["session_id"]
    tree_id = state.get("tree_id")
    current_tree_node = state.get("tree_node")
    user_message = state["user_message"].strip().lower()

    if not tree_id:
        logger.error("tree_engine_node llamado sin tree_id [session=%s]", session_id)
        return {
            **state,
            "current_node": "show_menu",
            "message_type": "error",
            "assistant_message": "Error interno: árbol de diagnóstico no configurado.",
            "options": None,
        }

    async with AsyncSessionLocal() as db:
        # Cargar árbol desde BD
        tree_result = await db.execute(
            select(DiagnosticTree).where(
                DiagnosticTree.tree_id == tree_id,
                DiagnosticTree.active == True,
            )
        )
        tree = tree_result.scalar_one_or_none()

        if not tree:
            logger.error("Árbol no encontrado: %s [session=%s]", tree_id, session_id)
            return {
                **state,
                "current_node": "show_menu",
                "message_type": "error",
                "assistant_message": f"Error: árbol de diagnóstico '{tree_id}' no disponible.",
                "options": None,
            }

        tree_json: dict[str, Any] = tree.tree_json
        nodes: dict[str, Any] = tree_json.get("nodes", {})
        state_json = state.get("state_json", {})
        asked_questions: list[str] = state_json.get("asked_questions", [])

        # Si no hay nodo activo → inicializar con el nodo de inicio
        if current_tree_node is None:
            start_node_id = tree_json.get("start_node")
            node_data = nodes.get(start_node_id)

            if not node_data:
                raise TreeNodeNotFoundError(start_node_id, tree_id)

            asked_questions.append(start_node_id)
            initial_hypotheses = _compute_active_hypotheses(nodes, start_node_id)
            new_state_json = {
                **state_json,
                "asked_questions": asked_questions,
                "step_number": 1,
                "tree_id": tree_id,
                "facts": {},
                "active_hypotheses": initial_hypotheses,
            }
            await _persist_tree_state(db, session_id, start_node_id, new_state_json)
            await trace_decision(
                session_id=session_id,
                module_name="tree_engine",
                input_data={"tree_id": tree_id, "action": "init"},
                output_data={"node_id": start_node_id, "question": node_data["text"]},
                db=db,
            )
            await db.commit()

            return {
                **state,
                "tree_node": start_node_id,
                "state_json": new_state_json,
                "current_node": "tree_engine",
                "message_type": "question",
                "assistant_message": node_data["text"],
                "step_number": 1,
                "route": "tree",
                "options": [
                    {"id": "si", "label": "Sí"},
                    {"id": "no", "label": "No"},
                ],
            }

        # Hay nodo activo → procesar respuesta del usuario
        node_data = nodes.get(current_tree_node)
        if not node_data:
            raise TreeNodeNotFoundError(current_tree_node, tree_id)

        # Normalizar respuesta
        normalized_answer = ANSWER_ALIASES.get(user_message, user_message)
        answer_map: dict[str, str] = node_data.get("answers", {})
        next_node_id = answer_map.get(normalized_answer)

        if not next_node_id:
            # Respuesta no reconocida — pedir de nuevo
            return {
                **state,
                "current_node": "tree_engine",
                "message_type": "question",
                "assistant_message": (
                    f"No entendí tu respuesta. Por favor responde 'Sí' o 'No'.\n"
                    f"{node_data['text']}"
                ),
                "step_number": len(asked_questions),
                "route": "tree",
                "options": [
                    {"id": "si", "label": "Sí"},
                    {"id": "no", "label": "No"},
                ],
            }

        next_node = nodes.get(next_node_id)
        if not next_node:
            raise TreeNodeNotFoundError(next_node_id, tree_id)

        asked_questions.append(next_node_id)

        # Actualizar facts y active_hypotheses (DDT §12)
        facts: dict = state_json.get("facts", {})
        facts[current_tree_node] = normalized_answer
        updated_hypotheses = _compute_active_hypotheses(nodes, next_node_id)

        new_state_json = {
            **state_json,
            "asked_questions": asked_questions,
            "facts": facts,
            "active_hypotheses": updated_hypotheses,
        }

        await trace_decision(
            session_id=session_id,
            module_name="tree_engine",
            input_data={
                "tree_id": tree_id,
                "node_id": current_tree_node,
                "user_answer": user_message,
                "normalized_answer": normalized_answer,
            },
            output_data={
                "next_node": next_node_id,
                "node_type": next_node["type"],
                "facts": facts,
                "active_hypotheses": updated_hypotheses,
            },
            db=db,
        )

        # Nodo final: diagnóstico
        if next_node["type"] == "diagnosis":
            diagnosis_label = next_node["result"]
            diagnosis_result = build_diagnosis_response(
                primary=diagnosis_label,
                asked_questions=asked_questions,
                tree_nodes=nodes,
            )
            await _persist_tree_state(db, session_id, next_node_id, new_state_json)
            await db.commit()

            logger.info(
                "Diagnóstico encontrado: '%s' [session=%s]",
                diagnosis_label, session_id,
            )

            return {
                **state,
                "tree_node": next_node_id,
                "state_json": new_state_json,
                "current_node": "show_menu",
                "message_type": "diagnosis",
                "assistant_message": "He identificado la causa probable del problema.",
                "step_number": len(asked_questions),
                "route": "tree",
                "options": [
                    {"id": "menu", "label": "Nueva consulta"},
                    {"id": "finish", "label": "Finalizar sesión"},
                ],
                "diagnosis_result": diagnosis_result,
            }

        # Nodo intermedio: siguiente pregunta
        await _persist_tree_state(db, session_id, next_node_id, new_state_json)
        await db.commit()

        return {
            **state,
            "tree_node": next_node_id,
            "state_json": new_state_json,
            "current_node": "tree_engine",
            "message_type": "question",
            "assistant_message": next_node["text"],
            "step_number": len(asked_questions),
            "route": "tree",
            "options": [
                {"id": "si", "label": "Sí"},
                {"id": "no", "label": "No"},
            ],
        }


def _compute_active_hypotheses(
    nodes: dict[str, Any],
    from_node_id: str,
    max_results: int = 3,
) -> list[dict[str, Any]]:
    """
    Recorre el árbol desde el nodo actual y devuelve las hipótesis de diagnóstico
    aún alcanzables, con un score normalizado (DDT §12 active_hypotheses).
    """
    reachable: list[str] = []
    visited: set[str] = set()
    queue: list[str] = [from_node_id]

    while queue:
        node_id = queue.pop(0)
        if node_id in visited:
            continue
        visited.add(node_id)
        node = nodes.get(node_id)
        if not node:
            continue
        if node["type"] == "diagnosis":
            reachable.append(node["result"])
        else:
            for next_id in node.get("answers", {}).values():
                queue.append(next_id)

    if not reachable:
        return []

    score = round(1.0 / len(reachable), 3)
    return [{"label": label, "score": score} for label in reachable[:max_results]]


async def _persist_tree_state(
    db: AsyncSession,
    session_id: str,
    current_node: str,
    state_json: dict[str, Any],
) -> None:
    """Persiste el nodo actual del árbol en session_state."""
    from datetime import datetime

    result = await db.execute(
        select(SessionState).where(SessionState.session_id == session_id)
    )
    session_state = result.scalar_one_or_none()
    if session_state:
        session_state.current_node = current_node
        session_state.state_json = state_json
        session_state.updated_at = datetime.utcnow()
