from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.entrevista import Entrevista
    from app.models.resposta_entrevista import RespostaEntrevista

from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.entrevista import Entrevista
    from app.models.resposta_entrevista import RespostaEntrevista


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
    entrevista: Mapped[Entrevista] = relationship(
        "Entrevista", back_populates="perguntas"
    )
    resposta: Mapped[RespostaEntrevista | None] = relationship(
        "RespostaEntrevista",
        back_populates="pergunta",
        cascade="all, delete-orphan",
        uselist=False,
    )
