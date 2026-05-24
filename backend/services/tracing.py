"""Servicio de trazabilidad: escribe decision_logs y messages en BD."""

import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.decision_log import DecisionLog
from models.message import Message
from models.session import Session

logger = logging.getLogger(__name__)


async def trace_decision(
    session_id: str,
    module_name: str,
    input_data: dict[str, Any] | None,
    output_data: dict[str, Any] | None,
    db: AsyncSession,
) -> None:
    """
    Registra una decisión del sistema en la tabla decision_logs.

    Args:
        session_id: UUID de la sesión activa.
        module_name: Nombre del módulo que tomó la decisión.
        input_data: Datos de entrada del módulo.
        output_data: Datos de salida / resultado.
        db: Sesión de BD activa (no hace commit — responsabilidad del llamador).
    """
    try:
        log = DecisionLog(
            session_id=uuid.UUID(session_id),
            module_name=module_name,
            input_data=input_data or {},
            output_data=output_data or {},
            created_at=datetime.utcnow(),
        )
        db.add(log)
        logger.debug(
            "DecisionLog registrado: module=%s [session=%s]",
            module_name, session_id,
        )
    except Exception as exc:
        logger.error(
            "Error registrando DecisionLog: %s [session=%s]",
            exc, session_id,
        )


async def save_message(
    session_id: str,
    role: str,
    content: str,
    db: AsyncSession,
) -> None:
    """
    Guarda un mensaje de la conversación en la tabla messages.

    Args:
        session_id: UUID de la sesión.
        role: 'user' o 'assistant'.
        content: Contenido del mensaje.
        db: Sesión de BD activa (no hace commit).
    """
    try:
        message = Message(
            session_id=uuid.UUID(session_id),
            role=role,
            content=content,
            created_at=datetime.utcnow(),
        )
        db.add(message)
        logger.debug(
            "Mensaje guardado: role=%s [session=%s]",
            role, session_id,
        )
    except Exception as exc:
        logger.error(
            "Error guardando mensaje: %s [session=%s]",
            exc, session_id,
        )


async def increment_session_steps(
    session_id: str,
    db: AsyncSession,
) -> None:
    """
    Incrementa el contador total_steps de la sesión.

    Args:
        session_id: UUID de la sesión.
        db: Sesión de BD activa.
    """
    try:
        result = await db.execute(
            select(Session).where(Session.session_id == uuid.UUID(session_id))
        )
        session = result.scalar_one_or_none()
        if session:
            session.total_steps = (session.total_steps or 0) + 1
    except Exception as exc:
        logger.error(
            "Error incrementando steps: %s [session=%s]",
            exc, session_id,
        )


def trace_decision_sync(
    session_id: str,
    module_name: str,
    input_data: dict[str, Any] | None,
    output_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Versión síncrona para uso en contextos no-async.
    Devuelve el log como dict (no persiste en BD).
    DESIGN DECISION: Usado solo donde async no es posible.
    """
    return {
        "session_id": session_id,
        "module_name": module_name,
        "input_data": input_data,
        "output_data": output_data,
        "created_at": datetime.utcnow().isoformat(),
    }
