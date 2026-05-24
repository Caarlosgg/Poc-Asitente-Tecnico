"""Nodo LangGraph: clasifica la intención del usuario y decide la ruta."""

import logging

from orchestrator.state import ConversationState
from services.groq_client import classify_user_intent
from services.tracing import trace_decision

logger = logging.getLogger(__name__)

# ── Opciones de menú → árbol por modelo ──────────────────────────────────────
MENU_TO_TREE: dict[str, dict[str, str]] = {
    "symptom_motor": {
        "AK550": "AK550_MOTOR_V1",
        "Xciting S 400": "XCITING_MOTOR_V1",
        "__default__": "AK550_MOTOR_V1",
    },
    "symptom_arranque": {
        "AK550": "AK550_ARRANQUE_V1",
        "__default__": "AK550_ARRANQUE_V1",
    },
    "symptom_celp": {
        "AK550": "AK550_CELP_V1",
        "__default__": "AK550_CELP_V1",
    },
    "symptom_consumo": {
        "AK550": "AK550_CONSUMO_V1",
        "__default__": "AK550_CONSUMO_V1",
    },
}

MENU_SYMPTOM_LABELS: dict[str, str] = {
    "symptom_motor": "Paradas de motor",
    "symptom_arranque": "Problemas de arranque",
    "symptom_celp": "Testigo CELP encendido",
    "symptom_consumo": "Consumo excesivo",
}

# Opciones de menú que van a FAQ o texto libre (sin árbol)
MENU_NON_TREE = {"faq", "other"}

# ── Categorías de FAQ disponibles como quick replies ─────────────────────────
FAQ_CATEGORY_OPTIONS: list[dict] = [
    {"id": "Arranque",          "label": "🔋 Arranque"},
    {"id": "Combustible",       "label": "⛽ Combustible"},
    {"id": "Electrónica",       "label": "⚡ Electrónica"},
    {"id": "Frenos",            "label": "🛑 Frenos"},
    {"id": "General",           "label": "📖 General"},
    {"id": "Mantenimiento",     "label": "🔧 Mantenimiento"},
    {"id": "Neumáticos",        "label": "🔵 Neumáticos"},
    {"id": "Paradas de motor",  "label": "🔄 Paradas de motor"},
    {"id": "Testigo CELP",      "label": "⚠️ Testigo CELP"},
    {"id": "Transmisión",       "label": "⚙️ Transmisión"},
]

# ── LLM symptom_key → árbol por modelo ───────────────────────────────────────
SYMPTOM_KEY_TO_TREE: dict[str, dict[str, str]] = {
    "motor_para": {
        "AK550": "AK550_MOTOR_V1",
        "Xciting S 400": "XCITING_MOTOR_V1",
        "__default__": "AK550_MOTOR_V1",
    },
    "arranque": {
        "AK550": "AK550_ARRANQUE_V1",
        "__default__": "AK550_ARRANQUE_V1",
    },
    "celp": {
        "AK550": "AK550_CELP_V1",
        "__default__": "AK550_CELP_V1",
    },
    "consumo": {
        "AK550": "AK550_CONSUMO_V1",
        "__default__": "AK550_CONSUMO_V1",
    },
}

SYMPTOM_KEY_LABELS: dict[str, str] = {
    "motor_para": "paradas de motor",
    "arranque": "problemas de arranque",
    "celp": "testigo CELP / avería electrónica",
    "consumo": "consumo excesivo",
    "frenos": "problemas de frenos",
    "ruido": "ruidos y vibraciones",
    "otro": "síntoma mecánico",
}


def _resolve_tree(option_id: str, model: str | None) -> str:
    tree_map = MENU_TO_TREE.get(option_id, {})
    if model and model in tree_map:
        return tree_map[model]
    return tree_map.get("__default__", "AK550_MOTOR_V1")


def _resolve_tree_from_symptom(symptom_key: str, model: str | None) -> str | None:
    tree_map = SYMPTOM_KEY_TO_TREE.get(symptom_key, {})
    if not tree_map:
        return None
    if model and model in tree_map:
        return tree_map[model]
    return tree_map.get("__default__")


async def classifier_node(state: ConversationState) -> ConversationState:
    """
    Clasifica la intención del usuario en tres rutas:
      A) Árbol de diagnóstico guiado (tree)
      B) FAQ / conocimiento técnico (faq)
      C) Texto libre / diagnóstico libre (other → free_text_node)

    Prioridad de evaluación:
      1. awaiting_input en state_json → el usuario ya eligió ruta y ahora escribe su consulta.
      2. Opción de menú con árbol → ruta directa sin LLM.
      3. Opción de menú sin árbol (faq/other) → mostrar prompt intermedio y esperar entrada real.
      4. Texto libre → LLM classify_user_intent → árbol si detecta síntoma conocido.
      5. Fallback: free_text_node.
    """
    user_message = state["user_message"].strip()
    msg_lower = user_message.lower()
    session_id = state["session_id"]
    model = state.get("model") or ""
    state_json = state.get("state_json", {})

    # ── Caso 0: el usuario ya eligió ruta (faq/other) y ahora envía su consulta real ──
    awaiting = state_json.get("awaiting_input")
    if awaiting in ("faq", "other"):
        next_node = "faq_matcher" if awaiting == "faq" else "free_text_node"
        new_state_json = {k: v for k, v in state_json.items() if k != "awaiting_input"}
        logger.info(
            "awaiting_input=%s → enviando consulta real a %s [session=%s]",
            awaiting, next_node, session_id,
        )
        return {
            **state,
            "route": awaiting,
            "tree_id": None,
            "current_node": next_node,
            "message_type": "text",
            "assistant_message": "",
            "options": None,
            "state_json": new_state_json,
        }

    # ── Caso 1: opción del menú con árbol ─────────────────────────────────────
    if msg_lower in MENU_TO_TREE:
        tree_id = _resolve_tree(msg_lower, model)
        symptom = MENU_SYMPTOM_LABELS.get(msg_lower, "Síntoma seleccionado")
        logger.info(
            "Clasificación menú-árbol: '%s' → tree_id=%s modelo=%s [session=%s]",
            msg_lower, tree_id, model, session_id,
        )
        return {
            **state,
            "route": "tree",
            "tree_id": tree_id,
            "tree_node": None,
            "current_node": "tree_engine",
            "message_type": "text",
            "assistant_message": "",
            "options": None,
            "state_json": {**state_json, "current_symptom": symptom},
        }

    # ── Caso 2: opción de menú sin árbol → prompt intermedio + await_input_node ──
    if msg_lower in MENU_NON_TREE:
        if msg_lower == "faq":
            prompt = (
                "¿Sobre qué tema tienes la consulta? "
                "Puedes elegir una categoría o escribir directamente tu pregunta."
            )
            options = FAQ_CATEGORY_OPTIONS
        else:  # other
            prompt = (
                "Cuéntame qué le pasa a la moto con tus propias palabras. "
                "Describe el síntoma, cuándo ocurre y qué has observado."
            )
            options = None

        logger.info(
            "Selección de ruta '%s' → prompt intermedio, awaiting_input [session=%s]",
            msg_lower, session_id,
        )
        return {
            **state,
            "route": msg_lower,
            "tree_id": None,
            "current_node": "await_input_node",
            "message_type": "text",
            "assistant_message": prompt,
            "options": options,
            "state_json": {**state_json, "awaiting_input": msg_lower},
        }

    # ── Caso 3: texto libre → LLM classify_user_intent ────────────────────────
    logger.info(
        "Texto libre detectado, llamando LLM classify_user_intent [session=%s]",
        session_id,
    )
    intent = await classify_user_intent(user_message, model)
    llm_route = intent.get("route", "other")
    symptom_key = intent.get("symptom_key")
    confidence = float(intent.get("confidence", 0.5))

    logger.info(
        "Intención LLM: route=%s symptom=%s conf=%.2f [session=%s]",
        llm_route, symptom_key, confidence, session_id,
    )

    if llm_route == "tree" and symptom_key:
        tree_id = _resolve_tree_from_symptom(symptom_key, model)
        if tree_id:
            symptom_label = SYMPTOM_KEY_LABELS.get(symptom_key, "síntoma mecánico")
            return {
                **state,
                "route": "tree",
                "tree_id": tree_id,
                "tree_node": None,
                "current_node": "tree_engine",
                "message_type": "text",
                "assistant_message": (
                    f"He identificado que describes un problema de **{symptom_label}**. "
                    f"Voy a guiarte con preguntas específicas para diagnosticarlo con precisión."
                ),
                "options": None,
                "state_json": {
                    **state_json,
                    "current_symptom": SYMPTOM_KEY_LABELS.get(symptom_key, "síntoma"),
                },
            }
        logger.info(
            "Árbol no disponible para symptom_key='%s' modelo='%s' → free_text",
            symptom_key, model,
        )

    if llm_route == "faq":
        return {
            **state,
            "route": "faq",
            "tree_id": None,
            "current_node": "faq_matcher",
            "message_type": "text",
            "assistant_message": "",
            "options": None,
        }

    # Fallback: texto libre → free_text_node
    return {
        **state,
        "route": "other",
        "tree_id": None,
        "current_node": "free_text_node",
        "message_type": "text",
        "assistant_message": "",
        "options": None,
    }

