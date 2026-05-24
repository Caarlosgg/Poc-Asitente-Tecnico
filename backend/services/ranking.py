"""Servicio: ranking híbrido de candidatos para la Ruta C (historial + semántica)."""

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)


def rank_candidates(
    candidates: list[dict[str, Any]],
    query: str,
    query_embedding: list[float] | None,
    user_model: str | None,
) -> list[dict[str, Any]]:
    """
    Ordena los candidatos históricos usando un score ponderado:

    score = 0.4 * semantic_similarity
          + 0.3 * model_match_bonus
          + 0.2 * base_confidence
          + 0.1 * frequency_score

    Args:
        candidates: Lista de casos históricos (dicts).
        query: Texto libre del usuario.
        query_embedding: Embedding del texto del usuario (puede ser None).
        user_model: Modelo del vehículo del usuario.

    Returns:
        Lista de candidatos ordenados por score descendente, con campo 'score' añadido.
    """
    if not candidates:
        return []

    scored: list[dict[str, Any]] = []

    for candidate in candidates:
        semantic_sim = _semantic_similarity(query, candidate, query_embedding)
        model_bonus = _model_match_bonus(candidate.get("model"), user_model)
        base_conf = float(candidate.get("base_confidence", 0.5))
        freq_score = _frequency_score(candidate)

        score = (
            0.4 * semantic_sim
            + 0.3 * model_bonus
            + 0.2 * base_conf
            + 0.1 * freq_score
        )

        scored.append({**candidate, "score": round(score, 4)})
        logger.debug(
            "Ranking case=%s: semantic=%.3f model=%.3f conf=%.3f freq=%.3f → score=%.3f",
            candidate.get("case_id"), semantic_sim, model_bonus, base_conf, freq_score, score,
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def _semantic_similarity(
    query: str,
    candidate: dict[str, Any],
    query_embedding: list[float] | None,
) -> float:
    """
    Calcula similitud semántica entre query y caso candidato.
    - Si hay embeddings disponibles, usa similitud coseno.
    - Fallback: similitud léxica por solapamiento de palabras.
    """
    candidate_embedding = candidate.get("embedding")

    if query_embedding and candidate_embedding:
        try:
            return _cosine_similarity(query_embedding, candidate_embedding)
        except Exception as exc:
            logger.warning("Error calculando similitud coseno: %s. Usando fallback léxico.", exc)

    # Fallback léxico
    return _lexical_similarity(query, candidate.get("case_text", ""))


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Calcula la similitud coseno entre dos vectores."""
    if len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def _lexical_similarity(query: str, candidate_text: str) -> float:
    """
    Similitud léxica simple: proporción de palabras significativas
    del query que aparecen en el texto del candidato.
    """
    query_words = {w.lower() for w in query.split() if len(w) > 3}
    candidate_lower = candidate_text.lower()

    if not query_words:
        return 0.0

    matches = sum(1 for w in query_words if w in candidate_lower)
    return matches / len(query_words)


def _model_match_bonus(candidate_model: str | None, user_model: str | None) -> float:
    """
    Bonus por coincidencia de modelo:
    - Mismo modelo: 1.0
    - Modelo general (None) o diferente: 0.3
    """
    if not user_model or not candidate_model:
        return 0.3
    if candidate_model.lower() == user_model.lower():
        return 1.0
    return 0.3


def _frequency_score(candidate: dict[str, Any]) -> float:
    """
    Score de frecuencia normalizado. Basado en base_confidence como proxy
    de frecuencia histórica (en una implementación real usaría un contador).
    DESIGN DECISION: En esta POC no hay contador de uso, se usa base_confidence
    como aproximación.
    """
    return float(candidate.get("base_confidence", 0.5))
