"""Schemas Pydantic para los endpoints de sesión."""

from typing import Any, Optional
from pydantic import BaseModel, Field
import uuid


class SessionStartResponse(BaseModel):
    """Respuesta al iniciar una nueva sesión."""

    session_id: str
    message: str
    message_type: str = "text"
    options: Optional[list[dict[str, str]]] = None


class MessageRequest(BaseModel):
    """Request para enviar un mensaje a la sesión."""

    session_id: str = Field(..., description="UUID de la sesión activa")
    message: str = Field(..., min_length=1, max_length=2000, description="Mensaje del usuario")


class DiagnosisData(BaseModel):
    """Contrato de salida estándar para diagnósticos."""

    primary_hypothesis: str
    alternatives: list[str] = []
    next_check: str
    short_explanation: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    source_type: str = "tree"  # 'tree' | 'faq' | 'historical'


class MessageResponse(BaseModel):
    """Respuesta tras procesar un mensaje del usuario."""

    session_id: str
    message: str
    message_type: str  # 'text'|'menu'|'question'|'diagnosis'|'error'
    options: Optional[list[dict[str, str]]] = None
    diagnosis: Optional[DiagnosisData] = None
    route: Optional[str] = None           # 'tree'|'faq'|'other'
    step_number: Optional[int] = None     # paso actual en árbol
    suggests_tree: Optional[str] = None   # tree_id sugerido desde Ruta C


class MessageSummary(BaseModel):
    """Resumen de un mensaje para la respuesta de detalle de sesión."""

    role: str
    content: str
    created_at: Optional[str] = None


class SessionDetailResponse(BaseModel):
    """Detalle del estado actual de una sesión."""

    session_id: str
    vin: Optional[str] = None
    model: Optional[str] = None
    status: str
    total_steps: int
    current_node: Optional[str] = None
    current_symptom: Optional[str] = None
    started_at: str
    entry_point: Optional[str] = None
    final_result: Optional[str] = None
    messages: list[MessageSummary] = []
