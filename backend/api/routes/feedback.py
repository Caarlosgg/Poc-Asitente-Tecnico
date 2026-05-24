"""Endpoint para registrar feedback del usuario al finalizar sesión."""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.feedback import FeedbackRequest, FeedbackResponse
from core.database import get_db
from models.feedback import Feedback
from models.session import Session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{session_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    session_id: str,
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
) -> FeedbackResponse:
    """
    Registra el feedback del usuario para una sesión.
    Una sesión solo puede tener un feedback (constraint UNIQUE en BD).
    """
    try:
        # Validar formato UUID
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Formato de session_id inválido: {session_id}",
            )

        # Verificar que la sesión existe
        session_result = await db.execute(
            select(Session).where(Session.session_id == session_uuid)
        )
        session = session_result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesión no encontrada: {session_id}",
            )

        # Verificar que no existe feedback previo
        existing_result = await db.execute(
            select(Feedback).where(Feedback.session_id == session_uuid)
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe feedback para esta sesión.",
            )

        # Guardar feedback
        feedback = Feedback(
            session_id=uuid.UUID(session_id),
            useful=request.useful,
            comment=request.comment,
            created_at=datetime.utcnow(),
        )
        db.add(feedback)

        # Marcar sesión como cerrada
        session.status = "closed"
        session.ended_at = datetime.utcnow()
        session.success = request.useful

        await db.commit()

        logger.info(
            "Feedback registrado: useful=%s [session=%s]",
            request.useful, session_id,
        )

        return FeedbackResponse(
            session_id=session_id,
            useful=request.useful,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error registrando feedback [session=%s]: %s", session_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar el feedback.",
        ) from exc
