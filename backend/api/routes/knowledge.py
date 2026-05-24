"""Endpoints de consulta de conocimiento (solo lectura)."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.knowledge import FAQ, DiagnosticTree, HistoricalCase

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/faqs")
async def list_faqs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    model: str | None = Query(default=None),
    category: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Lista de FAQs con filtros opcionales por modelo y categoría.
    Ordenadas por usage_count descendente.
    """
    try:
        query = select(FAQ).where(FAQ.active == True).order_by(desc(FAQ.usage_count))
        if model:
            query = query.where(FAQ.model == model)
        if category:
            query = query.where(FAQ.category == category)

        result = await db.execute(query.offset(offset).limit(limit))
        faqs = result.scalars().all()

        items = [
            {
                "faq_id": f.faq_id,
                "model": f.model,
                "category": f.category,
                "question": f.question,
                "answer": f.answer,
                "usage_count": f.usage_count,
            }
            for f in faqs
        ]

        return {"total": len(items), "offset": offset, "limit": limit, "items": items}

    except Exception as exc:
        logger.error("Error listando FAQs: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener FAQs.",
        ) from exc


@router.get("/cases")
async def list_cases(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    model: str | None = Query(default=None),
    category: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Lista de casos históricos con filtros opcionales por modelo y categoría.
    Ordenados por base_confidence descendente.
    """
    try:
        query = select(HistoricalCase).order_by(desc(HistoricalCase.base_confidence))
        if model:
            query = query.where(HistoricalCase.model == model)
        if category:
            query = query.where(HistoricalCase.symptom_category == category)

        result = await db.execute(query.offset(offset).limit(limit))
        cases = result.scalars().all()

        items = [
            {
                "case_id": c.case_id,
                "model": c.model,
                "symptom_category": c.symptom_category,
                "case_text": c.case_text,
                "final_diagnosis": c.final_diagnosis,
                "base_confidence": float(c.base_confidence),
            }
            for c in cases
        ]

        return {"total": len(items), "offset": offset, "limit": limit, "items": items}

    except Exception as exc:
        logger.error("Error listando casos históricos: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener casos históricos.",
        ) from exc


@router.get("/trees")
async def list_trees(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Lista de árboles de diagnóstico disponibles (activos)."""
    try:
        result = await db.execute(
            select(DiagnosticTree).where(DiagnosticTree.active == True)
        )
        trees = result.scalars().all()

        items = [
            {
                "tree_id": t.tree_id,
                "model": t.model,
                "symptom": t.symptom,
                "version": t.version,
                "node_count": len(t.tree_json.get("nodes", {})),
            }
            for t in trees
        ]

        return {"total": len(items), "items": items}

    except Exception as exc:
        logger.error("Error listando árboles: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener árboles.",
        ) from exc
