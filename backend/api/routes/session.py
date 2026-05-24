"""Endpoints de gestión de sesión conversacional."""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.session import (
    DiagnosisData,
    MessageRequest,
    MessageResponse,
    MessageSummary,
    SessionDetailResponse,
    SessionStartResponse,
)
from core.database import get_db
from core.exceptions import SessionNotFoundError
from models.message import Message
from models.session import Session, SessionState
from orchestrator.graph import conversation_graph
from orchestrator.state import ConversationState
from services.tracing import save_message, increment_session_steps

logger = logging.getLogger(__name__)

router = APIRouter()

# Mensaje de bienvenida inicial
WELCOME_MESSAGE = (
    "Hola. Soy el asistente técnico de diagnóstico. "
    "Indícame el bastidor (VIN) del vehículo para identificarlo y ayudarte."
)


@router.post("/start", response_model=SessionStartResponse, status_code=status.HTTP_201_CREATED)
async def start_session(db: AsyncSession = Depends(get_db)) -> SessionStartResponse:
    """
    Inicia una nueva sesión conversacional.
    Crea session + session_state en BD y devuelve el primer mensaje del asistente.
    """
    session_id = str(uuid.uuid4())

    try:
        # Crear sesión en BD
        session = Session(
            session_id=uuid.UUID(session_id),
            status="active",
            started_at=datetime.utcnow(),
            total_steps=0,
        )
        db.add(session)

        # Crear estado inicial
        session_state = SessionState(
            session_id=uuid.UUID(session_id),
            state_json={},
            updated_at=datetime.utcnow(),
        )
        db.add(session_state)

        # Guardar mensaje de bienvenida
        await save_message(
            session_id=session_id,
            role="assistant",
            content=WELCOME_MESSAGE,
            db=db,
        )
        await db.commit()

        logger.info("Nueva sesión iniciada: %s", session_id)

        return SessionStartResponse(
            session_id=session_id,
            message=WELCOME_MESSAGE,
            message_type="text",
            options=None,
        )
    except Exception as exc:
        logger.error("Error iniciando sesión: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al iniciar la sesión.",
        ) from exc


@router.post("/message", response_model=MessageResponse)
async def process_message(
    request: MessageRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Procesa un turno de conversación.
    Recupera el estado de sesión, invoca el grafo LangGraph y devuelve la respuesta.
    """
    session_id = request.session_id
    user_msg = request.message.strip()

    if not user_msg:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El mensaje no puede estar vacío.",
        )

    try:
        # Verificar que la sesión existe
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Formato de session_id inválido: {session_id}",
            )

        session_result = await db.execute(
            select(Session).where(Session.session_id == session_uuid)
        )
        session = session_result.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesión no encontrada: {session_id}",
            )

        if session.status == "closed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La sesión ya está cerrada.",
            )

        # Cargar estado actual de sesión
        state_result = await db.execute(
            select(SessionState).where(SessionState.session_id == session_uuid)
        )
        session_state = state_result.scalar_one_or_none()

        current_state_json = session_state.state_json if session_state else {}
        current_node = session_state.current_node if session_state else None

        # Determinar nodo de entrada del grafo
        entry_node = _determine_entry_node(session, session_state, user_msg)

        # Construir el estado inicial para el grafo
        graph_state: ConversationState = {
            "session_id": str(session_id),
            "vin": str(session.vin) if session.vin else None,
            "model": session.model,
            "current_node": entry_node,
            "tree_node": session_state.current_node if session_state and _is_tree_node(session_state.current_node) else None,
            "tree_id": current_state_json.get("tree_id"),
            "user_message": user_msg,
            "assistant_message": "",
            "message_type": "text",
            "options": None,
            "state_json": current_state_json,
            "vin_attempts": current_state_json.get("vin_attempts", 0),
            "route": current_state_json.get("route"),
            "diagnosis_result": None,
            "step_number": current_state_json.get("step_number", 0),
            "suggests_tree": None,
        }

        # Guardar mensaje del usuario
        await save_message(session_id=str(session_id), role="user", content=user_msg, db=db)

        # Invocar grafo LangGraph
        result_state: ConversationState = await conversation_graph.ainvoke(graph_state)

        # Persistir cambios de sesión
        await _update_session_from_result(db, session, session_state, result_state, session_id)
        await save_message(
            session_id=str(session_id),
            role="assistant",
            content=result_state["assistant_message"],
            db=db,
        )
        await increment_session_steps(str(session_id), db)
        await db.commit()

        # Construir respuesta
        diagnosis_data: DiagnosisData | None = None
        if result_state.get("diagnosis_result"):
            dr = result_state["diagnosis_result"]
            diagnosis_data = DiagnosisData(
                primary_hypothesis=dr.get("primary_hypothesis", ""),
                alternatives=dr.get("alternatives", []),
                next_check=dr.get("next_check", ""),
                short_explanation=dr.get("short_explanation", ""),
                confidence=float(dr.get("confidence", 0.0)),
                source_type=dr.get("source_type", "tree"),
            )

        logger.info(
            "Respuesta generada: type=%s [session=%s]",
            result_state["message_type"], session_id,
        )

        return MessageResponse(
            session_id=str(session_id),
            message=result_state["assistant_message"],
            message_type=result_state["message_type"],
            options=result_state.get("options"),
            diagnosis=diagnosis_data,
            route=result_state.get("route"),
            step_number=result_state.get("step_number"),
            suggests_tree=result_state.get("suggests_tree"),
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error procesando mensaje [session=%s]: %s", session_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar el mensaje.",
        ) from exc


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> SessionDetailResponse:
    """Devuelve el estado actual de una sesión."""
    try:
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Formato de session_id inválido: {session_id}",
            )

        result = await db.execute(
            select(Session).where(Session.session_id == session_uuid)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesión no encontrada: {session_id}",
            )

        state_result = await db.execute(
            select(SessionState).where(SessionState.session_id == session_uuid)
        )
        session_state = state_result.scalar_one_or_none()

        # Cargar mensajes de la sesión
        msg_result = await db.execute(
            select(Message)
            .where(Message.session_id == session_uuid)
            .order_by(Message.created_at)
        )
        messages = msg_result.scalars().all()

        return SessionDetailResponse(
            session_id=str(session.session_id),
            vin=session.vin,
            model=session.model,
            status=session.status,
            total_steps=session.total_steps,
            current_node=session_state.current_node if session_state else None,
            current_symptom=session_state.current_symptom if session_state else None,
            started_at=session.started_at.isoformat(),
            entry_point=session.entry_point,
            final_result=session.final_result,
            messages=[
                MessageSummary(
                    role=m.role,
                    content=m.content,
                    created_at=m.created_at.isoformat() if m.created_at else None,
                )
                for m in messages
            ],
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error recuperando sesión %s: %s", session_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar la sesión.",
        ) from exc


def _determine_entry_node(
    session: Session,
    session_state: SessionState | None,
    user_msg: str,
) -> str:
    """Determina el nodo de entrada del grafo según el estado actual."""
    if not session.vin:
        # Sin VIN → siempre validar VIN
        return "vin_lookup"

    # Comandos especiales que vuelven al menú directamente
    if user_msg.strip().lower() in ("menu", "volver", "nueva consulta", "inicio"):
        return "show_menu"

    state_json = session_state.state_json if session_state else {}
    current_node = session_state.current_node if session_state else None

    # Si estamos en medio de un árbol de diagnóstico
    if current_node and _is_tree_node(current_node):
        return "tree_engine"

    # En cualquier otro caso → clasificador
    return "classifier_node"


def _is_tree_node(node: str | None) -> bool:
    """Determina si el nodo actual pertenece a un árbol de diagnóstico."""
    if not node:
        return False
    # Los nodos de árbol siguen el patrón n1, n2, c1, c2, a1, a2, x1, x2, q1, q2, etc.
    return len(node) <= 5 and (node[0] in ("n", "c", "a", "x", "q")) and node[1:].isdigit()


async def _update_session_from_result(
    db: AsyncSession,
    session: Session,
    session_state: SessionState | None,
    result_state: ConversationState,
    session_id: Any,
) -> None:
    """Actualiza la sesión y session_state con los resultados del grafo."""
    msg_type = result_state["message_type"]

    # Actualizar session
    if result_state.get("vin") and not session.vin:
        session.vin = result_state["vin"]
    if result_state.get("model") and not session.model:
        session.model = result_state["model"]

    # Fijar entry_point la primera vez que se elige una ruta
    if not session.entry_point and result_state.get("route"):
        session.entry_point = result_state["route"]

    if msg_type == "diagnosis":
        session.success = True
        dr = result_state.get("diagnosis_result") or {}
        session.final_result = dr.get("primary_hypothesis", "")
    elif msg_type == "error":
        session.success = False

    # Actualizar session_state
    if session_state:
        # Preservar estado diagnóstico enriquecido
        inner_state = result_state.get("state_json") or {}
        new_state_json = {
            **inner_state,
            "vin_attempts": result_state.get("vin_attempts", 0),
            "route": result_state.get("route"),
            "tree_id": result_state.get("tree_id"),
            "step_number": result_state.get("step_number", 0),
        }
        session_state.state_json = new_state_json
        session_state.updated_at = datetime.utcnow()

        # current_node: solo lo mantenemos mientras estamos DENTRO del árbol (pregunta activa).
        # Tras diagnóstico, faq, menú u otro resultado final lo limpiamos.
        if msg_type == "question" and result_state.get("tree_node"):
            # Estamos en medio de un árbol — guardar nodo actual para el siguiente turno
            session_state.current_node = result_state["tree_node"]
        else:
            # Flujo completado (diagnosis, faq, menú, error) — limpiar para evitar re-entrada al árbol
            session_state.current_node = None

        # current_symptom: actualizar cuando hay síntoma en el estado interno
        symptom_from_state = inner_state.get("current_symptom")
        if symptom_from_state:
            session_state.current_symptom = symptom_from_state

        if result_state.get("model"):
            session_state.model = result_state["model"]
        if result_state.get("vin"):
            session_state.vin = result_state["vin"]

        state_json_extra = result_state.get("state_json", {})
        if state_json_extra.get("current_symptom"):
            session_state.current_symptom = state_json_extra["current_symptom"]
