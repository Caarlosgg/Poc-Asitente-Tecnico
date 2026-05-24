"""Schemas Pydantic para los endpoints de feedback."""

from typing import Optional
from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    """Request para registrar feedback del usuario."""

    useful: bool = Field(..., description="¿Fue útil la sesión?")
    comment: Optional[str] = Field(None, max_length=1000, description="Comentario opcional")


class FeedbackResponse(BaseModel):
    """Respuesta al registrar feedback."""

    session_id: str
    useful: bool
    message: str = "Feedback registrado. ¡Gracias por tu valoración!"
