from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.models.pergunta_entrevista import PerguntaEntrevista

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RespostaEntrevista(Base):
    __tablename__ = "resposta_entrevista"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pergunta_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pergunta_entrevista.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    audio_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    metricas: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    data_resposta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamentos
    pergunta: Mapped[PerguntaEntrevista] = relationship(
        "PerguntaEntrevista", back_populates="resposta"
    )
