"""Modelo ORM para la tabla vehicles."""

from datetime import datetime

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    vin: Mapped[str] = mapped_column(String(50), primary_key=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    family: Mapped[str | None] = mapped_column(String(100))
    displacement_cc: Mapped[int | None] = mapped_column(Integer)
    market: Mapped[str | None] = mapped_column(String(20))
    model_year: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="vehicle")
    session_states: Mapped[list["SessionState"]] = relationship("SessionState", back_populates="vehicle")

    def __repr__(self) -> str:
        return f"<Vehicle vin={self.vin} model={self.model}>"
