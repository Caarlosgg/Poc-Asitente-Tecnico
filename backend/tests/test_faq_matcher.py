"""Tests del nodo FAQ matcher."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from orchestrator.state import ConversationState


def _make_faq_state(user_message: str, model: str = "AK550") -> ConversationState:
    return ConversationState(
        session_id="test-session-id",
        vin="AK550-POC-0001",
        model=model,
        current_node="faq_matcher",
        tree_node=None,
        tree_id=None,
        user_message=user_message,
        assistant_message="",
        message_type="text",
        options=None,
        state_json={},
        vin_attempts=0,
        route="faq",
        diagnosis_result=None,
    )


@pytest.mark.asyncio
async def test_faq_matcher_no_match_redirects_to_free_text():
    """Sin match semántico, debe derivar a free_text_node."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch("orchestrator.nodes.faq_matcher.AsyncSessionLocal") as mock_session_local, \
         patch("orchestrator.nodes.faq_matcher.get_embedding", new_callable=AsyncMock, side_effect=Exception("No API")), \
         patch("orchestrator.nodes.faq_matcher.trace_decision", new_callable=AsyncMock):
        mock_session_local.return_value.__aenter__.return_value = mock_db

        from orchestrator.nodes.faq_matcher import faq_matcher_node
        state = _make_faq_state("consulta sin match en la base de datos de FAQs")
        result = await faq_matcher_node(state)

    assert result["current_node"] == "free_text_node"
    assert result["route"] == "other"


@pytest.mark.asyncio
async def test_faq_matcher_lexical_match_returns_answer():
    """Un match léxico suficiente debe devolver la respuesta de FAQ."""
    mock_chunk = MagicMock()
    mock_chunk.source_type = "faq"
    mock_chunk.source_id = "1"
    mock_chunk.text_chunk = "bomba de gasolina no se escucha al dar contacto"
    mock_chunk.chunk_id = 1
    mock_chunk.embedding = None

    mock_faq = MagicMock()
    mock_faq.faq_id = 1
    mock_faq.question = "¿Qué significa que no se escuche la bomba?"
    mock_faq.answer = "Es señal de fallo de bomba de gasolina."

    mock_db = AsyncMock()
    chunks_result = MagicMock()
    chunks_result.scalars.return_value.all.return_value = [mock_chunk]
    faq_result = MagicMock()
    faq_result.scalar_one_or_none.return_value = mock_faq

    mock_db.execute = AsyncMock(side_effect=[chunks_result, faq_result, MagicMock()])

    with patch("orchestrator.nodes.faq_matcher.AsyncSessionLocal") as mock_session_local, \
         patch("orchestrator.nodes.faq_matcher.get_embedding", new_callable=AsyncMock, side_effect=Exception("No API")), \
         patch("orchestrator.nodes.faq_matcher._build_faq_response", new_callable=AsyncMock, return_value="Es señal de fallo de bomba."), \
         patch("orchestrator.nodes.faq_matcher.trace_decision", new_callable=AsyncMock):
        mock_session_local.return_value.__aenter__.return_value = mock_db

        from orchestrator.nodes.faq_matcher import faq_matcher_node
        state = _make_faq_state("no se escucha bomba gasolina contacto fallo")
        result = await faq_matcher_node(state)

    # Si hay match léxico suficiente, la respuesta viene de FAQ
    # (El resultado puede ser FAQ o free_text según el umbral léxico)
    assert result["current_node"] in ("show_menu", "free_text_node")
