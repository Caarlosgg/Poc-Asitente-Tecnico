"""Tests del nodo de texto libre (Ruta C)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from orchestrator.state import ConversationState
from services.ranking import rank_candidates


def _make_free_text_state(user_message: str, model: str = "AK550") -> ConversationState:
    return ConversationState(
        session_id="test-session-id",
        vin="AK550-POC-0001",
        model=model,
        current_node="free_text_node",
        tree_node=None,
        tree_id=None,
        user_message=user_message,
        assistant_message="",
        message_type="text",
        options=None,
        state_json={},
        vin_attempts=0,
        route="other",
        diagnosis_result=None,
    )


SAMPLE_CANDIDATES = [
    {
        "case_id": "CASE-001",
        "model": "AK550",
        "symptom_category": "Paradas de motor",
        "case_text": "La moto se para al pasar por baches y vuelve tras quitar contacto.",
        "final_diagnosis": "Sensor de inclinación defectuoso",
        "base_confidence": 0.85,
    },
    {
        "case_id": "CASE-002",
        "model": "AK550",
        "symptom_category": "Paradas de motor",
        "case_text": "La moto se para y no se escucha la bomba de gasolina.",
        "final_diagnosis": "Bomba de gasolina defectuosa",
        "base_confidence": 0.90,
    },
    {
        "case_id": "CASE-003",
        "model": "AK550",
        "symptom_category": "Paradas de motor",
        "case_text": "La moto se para en caliente y arranca al enfriar.",
        "final_diagnosis": "Reglaje de válvulas pisado",
        "base_confidence": 0.88,
    },
]


def test_rank_candidates_returns_sorted_by_score():
    """El ranking debe devolver candidatos ordenados por score descendente."""
    ranked = rank_candidates(
        candidates=SAMPLE_CANDIDATES,
        query="moto para en caliente arranca en frío",
        query_embedding=None,
        user_model="AK550",
    )

    assert len(ranked) == 3
    scores = [c["score"] for c in ranked]
    assert scores == sorted(scores, reverse=True)


def test_rank_candidates_model_bonus():
    """El candidato del mismo modelo debe recibir bonus mayor."""
    candidates = [
        {**SAMPLE_CANDIDATES[0], "model": "AK550"},
        {**SAMPLE_CANDIDATES[1], "model": "Xciting 400"},
    ]
    ranked = rank_candidates(
        candidates=candidates,
        query="moto para",
        query_embedding=None,
        user_model="AK550",
    )
    # El candidato AK550 debe estar primero por el model_match_bonus
    assert ranked[0]["model"] == "AK550"


def test_rank_candidates_empty_list():
    """Lista vacía debe devolver lista vacía."""
    result = rank_candidates(
        candidates=[],
        query="cualquier cosa",
        query_embedding=None,
        user_model="AK550",
    )
    assert result == []


@pytest.mark.asyncio
async def test_free_text_node_returns_diagnosis_with_candidates():
    """Con candidatos históricos, debe devolver mensaje tipo diagnosis."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_cases = [MagicMock() for _ in SAMPLE_CANDIDATES]
    for mc, sc in zip(mock_cases, SAMPLE_CANDIDATES):
        mc.case_id = sc["case_id"]
        mc.model = sc["model"]
        mc.symptom_category = sc["symptom_category"]
        mc.case_text = sc["case_text"]
        mc.final_diagnosis = sc["final_diagnosis"]
        mc.base_confidence = sc["base_confidence"]

    mock_result.scalars.return_value.all.return_value = mock_cases
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch("orchestrator.nodes.free_text.AsyncSessionLocal") as mock_session_local, \
         patch("orchestrator.nodes.free_text.extract_tags", new_callable=AsyncMock, return_value={"symptom_category": "Paradas de motor", "tags": [], "severity": "high"}), \
         patch("orchestrator.nodes.free_text.get_embedding", new_callable=AsyncMock, side_effect=Exception("No API")), \
         patch("orchestrator.nodes.free_text.trace_decision", new_callable=AsyncMock):
        mock_session_local.return_value.__aenter__.return_value = mock_db

        from orchestrator.nodes.free_text import free_text_node
        state = _make_free_text_state("la moto se para en caliente y no arranca")
        result = await free_text_node(state)

    assert result["message_type"] == "diagnosis"
    assert result["diagnosis_result"] is not None
    assert result["diagnosis_result"]["primary_hypothesis"] != ""
    assert isinstance(result["diagnosis_result"]["alternatives"], list)
