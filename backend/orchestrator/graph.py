"""Definición y compilación del grafo LangGraph conversacional."""

import logging
from typing import Literal

from langgraph.graph import StateGraph, START, END

from orchestrator.state import ConversationState
from orchestrator.nodes.vin_lookup import vin_lookup_node
from orchestrator.nodes.menu import show_menu_node
from orchestrator.nodes.classifier import classifier_node
from orchestrator.nodes.faq_matcher import faq_matcher_node
from orchestrator.nodes.tree_engine import tree_engine_node
from orchestrator.nodes.free_text import free_text_node

logger = logging.getLogger(__name__)


# ─── Nodo de despacho ─────────────────────────────────────────────────────────

async def dispatch_node(state: ConversationState) -> ConversationState:
    """
    Nodo inicial del grafo.
    Pasa el estado sin modificarlo; la ruta la decide route_from_dispatch
    basándose en current_node que fijó el API router.
    """
    return state


def route_from_dispatch(
    state: ConversationState,
) -> Literal["vin_lookup", "classifier_node", "tree_engine", "show_menu"]:
    """
    Enruta desde el nodo de despacho al punto correcto de la conversación.

    - vin_lookup:      No hay VIN validado todavía.
    - tree_engine:     Estamos en mitad de un árbol de diagnóstico.
    - show_menu:       Comandos especiales (menu/volver/nueva consulta).
    - classifier_node: VIN validado y fuera de árbol; procesar selección del usuario.
    """
    node = state.get("current_node", "vin_lookup")
    if node == "tree_engine":
        return "tree_engine"
    if node == "classifier_node":
        return "classifier_node"
    if node == "show_menu":
        return "show_menu"
    return "vin_lookup"


# ─── Funciones de enrutamiento condicional ────────────────────────────────────

def route_after_vin(
    state: ConversationState,
) -> Literal["request_vin", "session_end_error", "show_menu"]:
    """Decide el siguiente paso tras intentar validar el VIN."""
    node = state["current_node"]
    if node == "session_end_error":
        return "session_end_error"
    if node == "show_menu":
        return "show_menu"
    return "request_vin"


def route_after_classifier(
    state: ConversationState,
) -> Literal["tree_engine", "faq_matcher", "free_text_node", "await_input_node"]:
    """Decide la ruta según la clasificación."""
    node = state.get("current_node", "free_text_node")
    if node == "tree_engine":
        return "tree_engine"
    if node == "faq_matcher":
        return "faq_matcher"
    if node == "await_input_node":
        return "await_input_node"
    return "free_text_node"


def route_after_faq(
    state: ConversationState,
) -> Literal["free_text_node", "end_with_answer"]:
    """Decide si el FAQ resolvió la consulta o deriva a texto libre."""
    if state.get("current_node") == "free_text_node":
        return "free_text_node"
    return "end_with_answer"


def route_after_tree(
    state: ConversationState,
) -> Literal["wait_for_answer", "end_with_diagnosis"]:
    """Decide si el árbol continúa (pregunta) o ha llegado a diagnóstico."""
    if state.get("current_node") == "tree_engine":
        return "wait_for_answer"
    return "end_with_diagnosis"


# ─── Nodos auxiliares de terminación ──────────────────────────────────────────

async def await_input_node(state: ConversationState) -> ConversationState:
    """
    Nodo terminal intermedio: muestra un prompt al usuario (faq / other)
    y espera su respuesta sin procesar nada más.
    El estado ya contiene assistant_message y options fijados por classifier_node.
    """
    return state


async def session_end_error_node(state: ConversationState) -> ConversationState:
    """Nodo terminal: sesión finalizada por exceso de intentos de VIN."""
    logger.warning("Sesión finalizada por error VIN [session=%s]", state["session_id"])
    return {
        **state,
        "current_node": "__end__",
        "message_type": "error",
        "assistant_message": (
            "Sesión finalizada: no fue posible identificar el vehículo "
            "tras varios intentos. Por favor, inicia una nueva sesión."
        ),
        "options": None,
    }


async def request_vin_node(state: ConversationState) -> ConversationState:
    """Nodo intermedio: solicita el VIN de nuevo al usuario."""
    return {
        **state,
        "current_node": "vin_lookup",
        "message_type": "text",
        "assistant_message": state.get(
            "assistant_message",
            "Por favor, introduce el número de bastidor (VIN) del vehículo.",
        ),
        "options": None,
    }


# ─── Construcción y compilación del grafo ─────────────────────────────────────

def build_graph():
    """Construye y compila el StateGraph de LangGraph."""
    builder = StateGraph(ConversationState)

    # Registrar todos los nodos
    builder.add_node("dispatch", dispatch_node)
    builder.add_node("vin_lookup", vin_lookup_node)
    builder.add_node("request_vin", request_vin_node)
    builder.add_node("session_end_error", session_end_error_node)
    builder.add_node("show_menu", show_menu_node)
    builder.add_node("classifier_node", classifier_node)
    builder.add_node("tree_engine", tree_engine_node)
    builder.add_node("faq_matcher", faq_matcher_node)
    builder.add_node("free_text_node", free_text_node)
    builder.add_node("await_input_node", await_input_node)

    # START → dispatch (nodo de entrada único)
    builder.add_edge(START, "dispatch")

    # dispatch → enruta al punto correcto según el estado de la sesión
    builder.add_conditional_edges(
        "dispatch",
        route_from_dispatch,
        {
            "vin_lookup": "vin_lookup",
            "classifier_node": "classifier_node",
            "tree_engine": "tree_engine",
            "show_menu": "show_menu",
        },
    )

    # vin_lookup → valida VIN y decide siguiente paso
    builder.add_conditional_edges(
        "vin_lookup",
        route_after_vin,
        {
            "request_vin": "request_vin",
            "session_end_error": "session_end_error",
            "show_menu": "show_menu",
        },
    )

    # Terminaciones tras VIN
    builder.add_edge("request_vin", END)        # Espera respuesta del usuario
    builder.add_edge("session_end_error", END)  # Error irrecuperable
    builder.add_edge("show_menu", END)          # Muestra menú; espera selección

    # classifier_node → enruta la selección del usuario
    builder.add_conditional_edges(
        "classifier_node",
        route_after_classifier,
        {
            "tree_engine": "tree_engine",
            "faq_matcher": "faq_matcher",
            "free_text_node": "free_text_node",
            "await_input_node": "await_input_node",
        },
    )

    # await_input_node → muestra prompt intermedio y termina; espera siguiente turno
    builder.add_edge("await_input_node", END)

    # faq_matcher → responde FAQ o deriva a texto libre
    builder.add_conditional_edges(
        "faq_matcher",
        route_after_faq,
        {
            "free_text_node": "free_text_node",
            "end_with_answer": END,  # FAQ resolvió; espera siguiente acción del usuario
        },
    )

    # tree_engine → pregunta siguiente o diagnóstico final
    builder.add_conditional_edges(
        "tree_engine",
        route_after_tree,
        {
            "wait_for_answer": END,       # Pregunta Sí/No; espera respuesta
            "end_with_diagnosis": END,    # Diagnóstico encontrado
        },
    )

    # free_text_node → siempre termina con un resultado
    builder.add_edge("free_text_node", END)

    return builder.compile()


# Instancia global del grafo (se compila una vez al importar)
conversation_graph = build_graph()
logger.info("Grafo LangGraph compilado correctamente.")
