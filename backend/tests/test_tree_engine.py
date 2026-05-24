"""Tests del motor de árbol de diagnóstico."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from orchestrator.state import ConversationState

SAMPLE_TREE_JSON = {
    "start_node": "n1",
    "nodes": {
        "n1": {"type": "question", "text": "¿Arranca sin quitar contacto?", "answers": {"si": "n2", "no": "n3"}},
        "n2": {"type": "diagnosis", "result": "Mal contacto en pipa de bujía"},
        "n3": {"type": "question", "text": "¿Se escucha la bomba?", "answers": {"si": "n4", "no": "n5"}},
        "n4": {"type": "diagnosis", "result": "Reglaje de válvulas pisado"},
        "n5": {"type": "diagnosis", "result": "Bomba de gasolina defectuosa"},
    },
}


def _make_tree_state(user_message: str, tree_node=None, tree_id="AK550_MOTOR_V1") -> ConversationState:
    return ConversationState(
        session_id="test-session-id",
        vin="AK550-POC-0001",
        model="AK550",
        current_node="tree_engine",
        tree_node=tree_node,
        tree_id=tree_id,
        user_message=user_message,
        assistant_message="",
        message_type="text",
        options=None,
        state_json={"asked_questions": []},
        vin_attempts=0,
        route="tree",
        diagnosis_result=None,
    )


@pytest.mark.asyncio
async def test_tree_engine_init_presents_first_question():
    """Sin nodo activo, debe presentar la primera pregunta del árbol."""
    mock_tree = MagicMock()
    mock_tree.tree_id = "AK550_MOTOR_V1"
    mock_tree.tree_json = SAMPLE_TREE_JSON
    mock_tree.active = True

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_tree
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch("orchestrator.nodes.tree_engine.AsyncSessionLocal") as mock_session_local, \
         patch("orchestrator.nodes.tree_engine.trace_decision", new_callable=AsyncMock), \
         patch("orchestrator.nodes.tree_engine._persist_tree_state", new_callable=AsyncMock):
        mock_session_local.return_value.__aenter__.return_value = mock_db

        from orchestrator.nodes.tree_engine import tree_engine_node
        state = _make_tree_state("symptom_motor", tree_node=None)
        result = await tree_engine_node(state)

    assert result["message_type"] == "question"
    assert result["tree_node"] == "n1"
    assert "¿Arranca sin quitar contacto?" in result["assistant_message"]
    assert result["options"] is not None
    assert len(result["options"]) == 2


@pytest.mark.asyncio
async def test_tree_engine_answer_si_reaches_diagnosis():
    """Responder 'si' al nodo n1 debe llevar al diagnóstico."""
    mock_tree = MagicMock()
    mock_tree.tree_id = "AK550_MOTOR_V1"
    mock_tree.tree_json = SAMPLE_TREE_JSON
    mock_tree.active = True

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_tree
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch("orchestrator.nodes.tree_engine.AsyncSessionLocal") as mock_session_local, \
         patch("orchestrator.nodes.tree_engine.trace_decision", new_callable=AsyncMock), \
         patch("orchestrator.nodes.tree_engine._persist_tree_state", new_callable=AsyncMock):
        mock_session_local.return_value.__aenter__.return_value = mock_db

        from orchestrator.nodes.tree_engine import tree_engine_node
        state = _make_tree_state("si", tree_node="n1")
        result = await tree_engine_node(state)

    assert result["message_type"] == "diagnosis"
    assert result["diagnosis_result"] is not None
    assert result["diagnosis_result"]["primary_hypothesis"] == "Mal contacto en pipa de bujía"
    assert result["diagnosis_result"]["confidence"] == 0.90


@pytest.mark.asyncio
async def test_tree_engine_unknown_answer_asks_again():
    """Una respuesta no reconocida debe pedir que se repita."""
    mock_tree = MagicMock()
    mock_tree.tree_id = "AK550_MOTOR_V1"
    mock_tree.tree_json = SAMPLE_TREE_JSON
    mock_tree.active = True

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_tree
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch("orchestrator.nodes.tree_engine.AsyncSessionLocal") as mock_session_local, \
         patch("orchestrator.nodes.tree_engine.trace_decision", new_callable=AsyncMock):
        mock_session_local.return_value.__aenter__.return_value = mock_db

        from orchestrator.nodes.tree_engine import tree_engine_node
        state = _make_tree_state("quizas", tree_node="n1")
        result = await tree_engine_node(state)

    assert result["message_type"] == "question"
    assert "Sí" in str(result["options"])
