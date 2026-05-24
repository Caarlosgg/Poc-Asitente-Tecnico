"""Punto de entrada principal de la API FastAPI — POC Asistente Conversacional."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import engine, Base
from api.routes.session import router as session_router
from api.routes.feedback import router as feedback_router
from api.routes.metrics import router as metrics_router
from api.routes.analytics import router as analytics_router
from api.routes.knowledge import router as knowledge_router

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación: startup y shutdown."""
    logger.info("Iniciando POC Asistente Conversacional...")
    # Las tablas se crean via init.sql en Docker; aquí no hacemos create_all
    # para respetar las migraciones SQL con pgvector
    yield
    logger.info("Cerrando POC Asistente Conversacional...")
    await engine.dispose()


app = FastAPI(
    title="POC Asistente Conversacional de Diagnóstico",
    description=(
        "Sistema conversacional de diagnóstico técnico para motocicletas. "
        "Combina árboles de decisión, FAQs semánticas e historial de casos."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — permite peticiones del frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session_router, prefix="/session", tags=["session"])
app.include_router(feedback_router, prefix="/session", tags=["feedback"])
app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(knowledge_router, prefix="/knowledge", tags=["knowledge"])


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Endpoint de salud para healthchecks."""
    return {"status": "ok", "service": "poc-asistente-tecnico"}
