"""Modelos ORM para knowledge_chunks y embedding_jobs."""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    chunk_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # faq|historical_case|tree_node
    source_id: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str | None] = mapped_column(String(100))
    symptom_category: Mapped[str | None] = mapped_column(String(100))
    text_chunk: Mapped[str] = mapped_column(Text, nullable=False)
    # DESIGN DECISION: embedding almacenado como JSON list de floats para compatibilidad
    # sin la extensión pgvector en el ORM de SQLAlchemy. La búsqueda vectorial
    # se hace con SQL raw usando el operador <=> de pgvector.
    embedding: Mapped[list[float] | None] = mapped_column(JSONB)
    base_confidence: Mapped[float | None] = mapped_column(Numeric(5, 4))
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    embedding_provider: Mapped[str | None] = mapped_column(String(50))
    embedding_model: Mapped[str | None] = mapped_column(String(100))
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(JSONB, name="metadata")
    embedding_status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    embedding_jobs: Mapped[list["EmbeddingJob"]] = relationship(
        "EmbeddingJob", back_populates="chunk"
    )

    def __repr__(self) -> str:
        return f"<KnowledgeChunk id={self.chunk_id} source={self.source_type}:{self.source_id}>"


class EmbeddingJob(Base):
    __tablename__ = "embedding_jobs"

    job_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chunk_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("knowledge_chunks.chunk_id"), nullable=False
    )
    provider: Mapped[str | None] = mapped_column(String(50))
    model: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    chunk: Mapped["KnowledgeChunk"] = relationship("KnowledgeChunk", back_populates="embedding_jobs")

    def __repr__(self) -> str:
        return f"<EmbeddingJob id={self.job_id} status={self.status}>"
