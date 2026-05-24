"""Estado conversacional compartido entre todos los nodos del grafo LangGraph."""

from typing import Any, Optional
from typing_extensions import TypedDict


class ConversationState(TypedDict):
    """Estado completo de una conversación. Fuente de verdad del orquestador."""

    session_id: str
    vin: Optional[str]
    model: Optional[str]
    current_node: str           # Nodo actual del grafo LangGraph
    tree_node: Optional[str]    # Nodo actual dentro del árbol de diagnóstico
    tree_id: Optional[str]      # ID del árbol activo
    user_message: str           # Último mensaje del usuario
    assistant_message: str      # Respuesta a devolver al usuario
    message_type: str           # 'text'|'menu'|'question'|'diagnosis'|'error'
    options: Optional[list[dict[str, str]]]  # Quick replies / botones
    state_json: dict[str, Any]  # Estado diagnóstico (facts, hypotheses, asked)
    vin_attempts: int           # Contador de reintentos VIN inválido
    route: Optional[str]        # 'tree'|'faq'|'other'
    diagnosis_result: Optional[dict[str, Any]]  # Resultado final si hay diagnóstico
    step_number: int            # Paso actual dentro del árbol de diagnóstico
    suggests_tree: Optional[str]  # tree_id a sugerir cuando Ruta C detecta síntoma conocido
