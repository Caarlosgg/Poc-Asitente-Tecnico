"""Endpoints de analítica interna (solo lectura, sin modificar datos)."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.feedback import Feedback
from models.knowledge import HistoricalCase
from models.session import Session, SessionState

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/sessions")
async def list_sessions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Lista de sesiones recientes con información básica.
    Permite filtrar por status (active/closed).
    """
    try:
        query = select(Session).order_by(desc(Session.started_at))
        if status_filter:
            query = query.where(Session.status == status_filter)

        count_query = select(func.count()).select_from(Session)
        if status_filter:
            count_query = count_query.where(Session.status == status_filter)

        total_result = await db.execute(count_query)
        total: int = total_result.scalar() or 0

        result = await db.execute(query.offset(offset).limit(limit))
        sessions = result.scalars().all()

        items = []
        for s in sessions:
            duration = None
            if s.ended_at and s.started_at:
                duration = round((s.ended_at - s.started_at).total_seconds())
            items.append({
                "session_id": str(s.session_id),
                "vin": s.vin,
                "model": s.model,
                "status": s.status,
                "entry_point": s.entry_point,
                "total_steps": s.total_steps,
                "final_result": s.final_result,
                "success": s.success,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                "duration_seconds": duration,
            })

        return {"total": total, "offset": offset, "limit": limit, "items": items}

    except Exception as exc:
        logger.error("Error listando sesiones: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener sesiones.",
        ) from exc


@router.get("/diagnoses")
async def list_diagnoses(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Ranking de diagnósticos más frecuentes (por final_result de sesión).
    """
    try:
        result = await db.execute(
            select(Session.final_result, Session.model, func.count().label("count"))
            .where(Session.final_result.isnot(None))
            .where(Session.final_result != "")
            .group_by(Session.final_result, Session.model)
            .order_by(func.count().desc())
            .limit(limit)
        )
        items = [
            {"diagnosis": row.final_result, "model": row.model, "count": row.count}
            for row in result
        ]
        return {"total": len(items), "items": items}

    except Exception as exc:
        logger.error("Error listando diagnósticos: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener diagnósticos.",
        ) from exc


@router.get("/feedback")
async def list_feedback(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Lista de feedback recibido con totales agregados.
    """
    try:
        total_result = await db.execute(select(func.count()).select_from(Feedback))
        total: int = total_result.scalar() or 0

        positive_result = await db.execute(
            select(func.count()).select_from(Feedback).where(Feedback.useful == True)
        )
        positive: int = positive_result.scalar() or 0

        result = await db.execute(
            select(Feedback).order_by(desc(Feedback.created_at)).offset(offset).limit(limit)
        )
        feedbacks = result.scalars().all()

        items = [
            {
                "session_id": str(f.session_id),
                "useful": f.useful,
                "comment": f.comment,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in feedbacks
        ]

        return {
            "total": total,
            "positive": positive,
            "negative": total - positive,
            "positive_rate": round(positive / total, 4) if total > 0 else 0.0,
            "offset": offset,
            "limit": limit,
            "items": items,
        }

    except Exception as exc:
        logger.error("Error listando feedback: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener feedback.",
        ) from exc


# Mapeo de entry_point / symptom_category → etiqueta de síntoma visible
_SYMPTOM_LABELS: dict[str, str] = {
    "symptom_motor": "Paradas de motor",
    "symptom_arranque": "Problemas de arranque",
    "symptom_celp": "Testigo CELP",
    "symptom_consumo": "Consumo excesivo",
    "tree": "Árbol DDT (genérico)",
    "faq": "Consulta FAQ",
    "other": "Descripción libre",
    # historical_cases symptom_category values
    "parada": "Paradas de motor",
    "arranque": "Problemas de arranque",
    "celp": "Testigo CELP",
    "consumo": "Consumo excesivo",
    "electrico": "Fallo eléctrico",
    "frenos": "Problemas de frenos",
    "transmision": "Transmisión",
    "suspension": "Suspensión",
}


@router.get("/heatmap")
async def get_symptom_heatmap(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Mapa de calor: frecuencia de síntomas por modelo.
    Combina datos de sesiones reales y casos históricos.
    Devuelve matriz { model -> { symptom -> count } } con ejes ordenados.
    """
    try:
        matrix: dict[str, dict[str, int]] = {}

        # Fuente 1: sesiones reales con entry_point
        session_result = await db.execute(
            select(Session.model, Session.entry_point, func.count().label("cnt"))
            .where(Session.model.isnot(None))
            .where(Session.entry_point.isnot(None))
            .group_by(Session.model, Session.entry_point)
        )
        for row in session_result:
            model = row.model
            symptom = _SYMPTOM_LABELS.get(row.entry_point, row.entry_point)
            matrix.setdefault(model, {})
            matrix[model][symptom] = matrix[model].get(symptom, 0) + row.cnt

        # Fuente 2: casos históricos con symptom_category
        cases_result = await db.execute(
            select(HistoricalCase.model, HistoricalCase.symptom_category, func.count().label("cnt"))
            .where(HistoricalCase.model.isnot(None))
            .where(HistoricalCase.symptom_category.isnot(None))
            .group_by(HistoricalCase.model, HistoricalCase.symptom_category)
        )
        for row in cases_result:
            model = row.model
            symptom = _SYMPTOM_LABELS.get(row.symptom_category or "", row.symptom_category or "Otro")
            matrix.setdefault(model, {})
            matrix[model][symptom] = matrix[model].get(symptom, 0) + row.cnt

        # Construir ejes ordenados
        all_models = sorted(matrix.keys())
        all_symptoms: set[str] = set()
        for symptoms in matrix.values():
            all_symptoms.update(symptoms.keys())
        symptom_list = sorted(all_symptoms)

        # Serializar como lista de filas para el frontend
        rows = []
        for symptom in symptom_list:
            row_data: dict[str, Any] = {"symptom": symptom}
            for model in all_models:
                row_data[model] = matrix.get(model, {}).get(symptom, 0)
            rows.append(row_data)

        # Valor máximo global para normalizar colores
        max_val = max(
            (v for sym_map in matrix.values() for v in sym_map.values()),
            default=1,
        )

        return {
            "models": all_models,
            "symptoms": symptom_list,
            "rows": rows,
            "max_value": max_val,
        }

    except Exception as exc:
        logger.error("Error generando heatmap: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al generar el mapa de calor.",
        ) from exc
