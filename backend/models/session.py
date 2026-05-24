"""Modelos ORM para sessions y session_state."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vin: Mapped[str | None] = mapped_column(String(50), ForeignKey("vehicles.vin"))
    model: Mapped[str | None] = mapped_column(String(100))
    entry_point: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    total_steps: Mapped[int] = mapped_column(Integer, default=0)
    final_result: Mapped[str | None] = mapped_column(String(255))
    success: Mapped[bool | None] = mapped_column(Boolean)

    # Relaciones
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="sessions")
    state: Mapped["SessionState"] = relationship(
        "SessionState", back_populates="session", uselist=False
    )
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="session")
    decision_logs: Mapped[list["DecisionLog"]] = relationship(
        "DecisionLog", back_populates="session"
    )
    feedback: Mapped["Feedback"] = relationship(
        "Feedback", back_populates="session", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Session id={self.session_id} status={self.status}>"


class SessionState(Base):
    __tablename__ = "session_state"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        primary_key=True,
    )
    vin: Mapped[str | None] = mapped_column(String(50), ForeignKey("vehicles.vin"))
    model: Mapped[str | None] = mapped_column(String(100))
    current_symptom: Mapped[str | None] = mapped_column(String(100))
    current_node: Mapped[str | None] = mapped_column(String(100))
    state_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    session: Mapped["Session"] = relationship("Session", back_populates="state")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="session_states")

    def __repr__(self) -> str:
        return f"<SessionState session_id={self.session_id} node={self.current_node}>"
