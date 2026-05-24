"""Tests del nodo VIN lookup del orquestador."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from orchestrator.state import ConversationState

# UUID válido para los tests
TEST_SESSION_ID = "12345678-1234-5678-1234-567812345678"


def _make_state(user_message: str, vin_attempts: int = 0) -> ConversationState:
    return ConversationState(
        session_id=TEST_SESSION_ID,
        vin=None,
        model=None,
        current_node="vin_lookup",
        tree_node=None,
        tree_id=None,
        user_message=user_message,
        assistant_message="",
        message_type="text",
        options=None,
        state_json={},
        vin_attempts=vin_attempts,
        route=None,
        diagnosis_result=None,
    )


@pytest.mark.asyncio
async def test_vin_lookup_valid_vin():
    """Un VIN válido debe avanzar a show_menu con modelo correcto."""
    mock_vehicle = MagicMock()
    mock_vehicle.vin = "AK550-POC-0001"
    mock_vehicle.model = "AK550"
    mock_vehicle.model_year = 2022

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_vehicle
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch("orchestrator.nodes.vin_lookup.AsyncSessionLocal") as mock_session_local, \
         patch("orchestrator.nodes.vin_lookup.trace_decision", new_callable=AsyncMock):
        mock_session_local.return_value.__aenter__.return_value = mock_db

        from orchestrator.nodes.vin_lookup import vin_lookup_node
        state = _make_state("AK550-POC-0001")
        result = await vin_lookup_node(state)

    assert result["vin"] == "AK550-POC-0001"
    assert result["model"] == "AK550"
    assert result["current_node"] == "show_menu"
    assert result["vin_attempts"] == 0


@pytest.mark.asyncio
async def test_vin_lookup_invalid_vin_first_attempt():
    """VIN inválido en primer intento debe solicitar de nuevo."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch("orchestrator.nodes.vin_lookup.AsyncSessionLocal") as mock_session_local, \
         patch("orchestrator.nodes.vin_lookup.trace_decision", new_callable=AsyncMock):
        mock_session_local.return_value.__aenter__.return_value = mock_db

        from orchestrator.nodes.vin_lookup import vin_lookup_node
        state = _make_state("INVALIDO-123", vin_attempts=0)
        result = await vin_lookup_node(state)

    assert result["current_node"] == "request_vin"
    assert result["vin_attempts"] == 1
    assert "no encontrado" in result["assistant_message"].lower()


@pytest.mark.asyncio
async def test_vin_lookup_max_attempts_exceeded():
    """Al superar el máximo de intentos, debe terminar la sesión con error."""
    from core.config import settings

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch("orchestrator.nodes.vin_lookup.AsyncSessionLocal") as mock_session_local, \
         patch("orchestrator.nodes.vin_lookup.trace_decision", new_callable=AsyncMock):
        mock_session_local.return_value.__aenter__.return_value = mock_db

        from orchestrator.nodes.vin_lookup import vin_lookup_node
        # Llegamos al último intento permitido
        state = _make_state("INVALIDO-123", vin_attempts=settings.max_vin_attempts - 1)
        result = await vin_lookup_node(state)

    assert result["current_node"] == "session_end_error"
    assert result["message_type"] == "error"
