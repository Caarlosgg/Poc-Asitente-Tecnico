"""Nodo LangGraph: muestra el menú principal al usuario."""

import logging

from orchestrator.state import ConversationState
from services.tracing import trace_decision_sync

logger = logging.getLogger(__name__)

# Síntomas disponibles por modelo
_MODEL_SYMPTOMS: dict[str, list[dict]] = {
    "AK550": [
        {"id": "symptom_motor",    "label": "🔧 Paradas de motor"},
        {"id": "symptom_arranque", "label": "🔩 Problemas de arranque"},
        {"id": "symptom_celp",     "label": "⚠️ Testigo CELP encendido"},
        {"id": "symptom_consumo",  "label": "⛽ Consumo excesivo"},
    ],
    "Xciting S 400": [
        {"id": "symptom_motor", "label": "🔧 Paradas de motor"},
        {"id": "symptom_celp",  "label": "⚠️ Testigo CELP / Avería"},
    ],
    "DT X360": [
        {"id": "symptom_motor", "label": "🔧 Motor / Pérdida de potencia"},
    ],
    "CV5": [
        {"id": "symptom_motor", "label": "🔧 Paradas de motor"},
    ],
}

_DEFAULT_SYMPTOMS: list[dict] = [
    {"id": "symptom_motor", "label": "🔧 Paradas de motor"},
    {"id": "symptom_celp",  "label": "⚠️ Testigo CELP encendido"},
]

_COMMON_OPTIONS: list[dict] = [
    {"id": "faq",   "label": "📋 Consultas frecuentes"},
    {"id": "other", "label": "💬 Describir el problema"},
]


def _build_menu(model: str | None) -> list[dict]:
    symptom_opts = _MODEL_SYMPTOMS.get(model or "", _DEFAULT_SYMPTOMS)
    return symptom_opts + _COMMON_OPTIONS


async def show_menu_node(state: ConversationState) -> ConversationState:
    """
    Muestra el menú principal de síntomas y opciones.
    Se activa después de identificar el vehículo correctamente.
    El menú es dinámico según el modelo identificado.
    """
    model = state.get("model", "")
    session_id = state["session_id"]

    menu_options = _build_menu(model)
    vehicle_label = model or "tu vehículo"

    logger.info(
        "Mostrando menú principal: %d opciones [session=%s model=%s]",
        len(menu_options), session_id, model,
    )

    return {
        **state,
        "current_node": "classifier_node",
        "message_type": "menu",
        "assistant_message": f"Vehículo identificado: **{vehicle_label}**. ¿En qué puedo ayudarte?",
        "options": menu_options,
        "route": None,
    }

