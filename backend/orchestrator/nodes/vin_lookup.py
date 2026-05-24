"""Nodo LangGraph: validación del bastidor (VIN) en base de datos."""

import logging
import uuid as _uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from core.config import settings
from models.vehicle import Vehicle
from models.session import Session, SessionState
from orchestrator.state import ConversationState
from services.tracing import trace_decision

logger = logging.getLogger(__name__)


async def vin_lookup_node(state: ConversationState) -> ConversationState:
    """
    Valida el VIN introducido por el usuario contra la base de datos.
    Actualiza la sesión si el VIN es válido.
    """
    user_message = state["user_message"].strip()
    session_id = state["session_id"]

    async with AsyncSessionLocal() as db:
        # Buscar vehículo en BD
        result = await db.execute(select(Vehicle).where(Vehicle.vin == user_message))
        vehicle = result.scalar_one_or_none()

        if vehicle is None:
            attempts = state["vin_attempts"] + 1
            logger.warning(
                "VIN no encontrado: %s (intento %d/%d) [session=%s]",
                user_message, attempts, settings.max_vin_attempts, session_id,
            )

            await trace_decision(
                session_id=session_id,
                module_name="vin_lookup",
                input_data={"vin": user_message, "attempt": attempts},
                output_data={"valid": False},
                db=db,
            )
            await db.commit()

            if attempts >= settings.max_vin_attempts:
                return {
                    **state,
                    "vin_attempts": attempts,
                    "current_node": "session_end_error",
                    "message_type": "error",
                    "assistant_message": (
                        "Se ha superado el número máximo de intentos. "
                        "No se pudo identificar el vehículo. Sesión finalizada."
                    ),
                    "options": None,
                }

            return {
                **state,
                "vin_attempts": attempts,
                "current_node": "request_vin",
                "message_type": "text",
                "assistant_message": (
                    f"Bastidor no encontrado: '{user_message}'. "
                    f"Por favor, verifica el número e inténtalo de nuevo "
                    f"({attempts}/{settings.max_vin_attempts} intentos)."
                ),
                "options": None,
            }

        # VIN válido — actualizar sesión en BD
        session_result = await db.execute(
            select(Session).where(Session.session_id == _uuid.UUID(session_id))
        )
        session = session_result.scalar_one_or_none()
        if session:
            session.vin = vehicle.vin
            session.model = vehicle.model

        # Actualizar o crear session_state
        state_result = await db.execute(
            select(SessionState).where(SessionState.session_id == _uuid.UUID(session_id))
        )
        session_state = state_result.scalar_one_or_none()
        if session_state:
            session_state.vin = vehicle.vin
            session_state.model = vehicle.model
        else:
            session_state = SessionState(
                session_id=_uuid.UUID(session_id),
                vin=vehicle.vin,
                model=vehicle.model,
                state_json={},
            )
            db.add(session_state)

        await trace_decision(
            session_id=session_id,
            module_name="vin_lookup",
            input_data={"vin": user_message},
            output_data={"valid": True, "model": vehicle.model, "model_year": vehicle.model_year},
            db=db,
        )
        await db.commit()

        logger.info(
            "VIN válido: %s → modelo=%s [session=%s]",
            vehicle.vin, vehicle.model, session_id,
        )

        return {
            **state,
            "vin": vehicle.vin,
            "model": vehicle.model,
            "vin_attempts": 0,
            "current_node": "show_menu",
            "message_type": "text",
            "assistant_message": f"Vehículo identificado: {vehicle.model} ({vehicle.model_year}).",
            "options": None,
        }
