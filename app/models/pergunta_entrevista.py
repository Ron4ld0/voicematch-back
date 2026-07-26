from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, Text, Integer, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PerguntaEntrevista(Base):
    __tablename__ = "pergunta_entrevista"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entrevista_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entrevista.id", ondelete="CASCADE"),
        nullable=False,
    )
    pergunta_texto: Mapped[str] = mapped_column(Text, nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("entrevista_id", "ordem", name="uq_entrevista_ordem"),
    )

    # Relacionamentos
    entrevista: Mapped["Entrevista"] = relationship(
        "Entrevista", back_populates="perguntas"
    )
    resposta: Mapped[Optional["RespostaEntrevista"]] = relationship(
        "RespostaEntrevista",
        back_populates="pergunta",
        cascade="all, delete-orphan",
        uselist=False,
    )
