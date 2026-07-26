from __future__ import annotations
import uuid
from typing import Optional, List
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Recrutador(Base):
    __tablename__ = "recrutador"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        primary_key=True,
    )
    empresa: Mapped[str] = mapped_column(String(255), nullable=False)
    cargo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relacionamento 1:1 com Usuario
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="recrutador")
    # Relacionamento 1:N com Vaga
    vagas: Mapped[List["Vaga"]] = relationship(
        "Vaga", back_populates="recrutador", cascade="all, delete-orphan"
    )
