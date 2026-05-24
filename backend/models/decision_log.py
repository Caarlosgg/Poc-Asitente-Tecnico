"""Modelo ORM para la tabla decision_logs."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class DecisionLog(Base):
    __tablename__ = "decision_logs"

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False
    )
    module_name: Mapped[str] = mapped_column(String(100), nullable=False)
    input_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    output_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    session: Mapped["Session"] = relationship("Session", back_populates="decision_logs")

    def __repr__(self) -> str:
        return f"<DecisionLog id={self.log_id} module={self.module_name}>"
