"""Endpoint de métricas del sistema."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.decision_log import DecisionLog
from models.feedback import Feedback
from models.session import Session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary")
async def get_metrics_summary(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Devuelve métricas agregadas del sistema (DDT §22).
    - Total de sesiones / sesiones completadas
    - Tiempo medio de sesión
    - Pasos promedio por sesión
    - Uso de FAQ, árbol y Otros (por decision_logs.module_name)
    - Top diagnósticos (final_result)
    - Feedback positivo vs negativo
    """
    try:
        # Total sesiones
        total_result = await db.execute(select(func.count()).select_from(Session))
        total_sessions: int = total_result.scalar() or 0

        # Sesiones cerradas (completadas)
        completed_result = await db.execute(
            select(func.count()).select_from(Session).where(Session.status == "closed")
        )
        completed_sessions: int = completed_result.scalar() or 0

        # Tasa de éxito (sesiones con success=True)
        success_result = await db.execute(
            select(func.count()).select_from(Session).where(Session.success == True)
        )
        success_count: int = success_result.scalar() or 0
        success_rate = round(success_count / total_sessions, 4) if total_sessions > 0 else 0.0

        # Pasos promedio
        avg_steps_result = await db.execute(
            select(func.avg(Session.total_steps)).select_from(Session)
        )
        avg_steps = round(float(avg_steps_result.scalar() or 0), 2)

        # Tiempo medio de sesión (en segundos, para sesiones cerradas)
        avg_duration_result = await db.execute(
            text(
                "SELECT AVG(EXTRACT(EPOCH FROM (ended_at - started_at))) "
                "FROM sessions WHERE ended_at IS NOT NULL"
            )
        )
        avg_duration_seconds = round(float(avg_duration_result.scalar() or 0), 1)

        # Feedback positivo vs negativo
        total_feedback_result = await db.execute(
            select(func.count()).select_from(Feedback)
        )
        total_feedback: int = total_feedback_result.scalar() or 0

        positive_feedback_result = await db.execute(
            select(func.count()).select_from(Feedback).where(Feedback.useful == True)
        )
        positive_feedback: int = positive_feedback_result.scalar() or 0
        negative_feedback = total_feedback - positive_feedback
        positive_feedback_rate = (
            round(positive_feedback / total_feedback, 4) if total_feedback > 0 else 0.0
        )

        # Uso por módulo: faq_matcher, tree_engine, free_text_parser (DDT §22)
        module_usage_result = await db.execute(
            select(DecisionLog.module_name, func.count().label("count"))
            .where(DecisionLog.module_name.in_(["faq_matcher", "tree_engine", "free_text_parser"]))
            .group_by(DecisionLog.module_name)
        )
        module_usage: dict[str, int] = {}
        for row in module_usage_result:
            module_usage[row.module_name] = row.count

        # Top diagnósticos (por final_result de la sesión)
        top_diagnoses_result = await db.execute(
            select(Session.final_result, func.count().label("count"))
            .where(Session.final_result.isnot(None))
            .where(Session.final_result != "")
            .group_by(Session.final_result)
            .order_by(func.count().desc())
            .limit(5)
        )
        top_diagnoses = [
            {"diagnosis": row.final_result, "count": row.count}
            for row in top_diagnoses_result
        ]

        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "success_rate": success_rate,
            "avg_steps": avg_steps,
            "avg_duration_seconds": avg_duration_seconds,
            "total_feedback": total_feedback,
            "positive_feedback": positive_feedback,
            "negative_feedback": negative_feedback,
            "positive_feedback_rate": positive_feedback_rate,
            "module_usage": {
                "tree": module_usage.get("tree_engine", 0),
                "faq": module_usage.get("faq_matcher", 0),
                "free_text": module_usage.get("free_text_parser", 0),
            },
            "top_diagnoses": top_diagnoses,
        }

    except Exception as exc:
        logger.error("Error calculando métricas: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al calcular métricas.",
        ) from exc
