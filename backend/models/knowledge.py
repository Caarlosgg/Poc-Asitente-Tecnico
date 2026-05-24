"""Modelos ORM para faqs, diagnostic_trees y historical_cases."""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class FAQ(Base):
    __tablename__ = "faqs"

    faq_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model: Mapped[str | None] = mapped_column(String(100))
    category: Mapped[str | None] = mapped_column(String(100))
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<FAQ id={self.faq_id} category={self.category}>"


class DiagnosticTree(Base):
    __tablename__ = "diagnostic_trees"

    tree_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    model: Mapped[str | None] = mapped_column(String(100))
    symptom: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    tree_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<DiagnosticTree id={self.tree_id} symptom={self.symptom}>"


class HistoricalCase(Base):
    __tablename__ = "historical_cases"

    case_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    symptom_category: Mapped[str | None] = mapped_column(String(100))
    case_text: Mapped[str] = mapped_column(Text, nullable=False)
    final_diagnosis: Mapped[str] = mapped_column(String(255), nullable=False)
    base_confidence: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<HistoricalCase id={self.case_id} model={self.model}>"
