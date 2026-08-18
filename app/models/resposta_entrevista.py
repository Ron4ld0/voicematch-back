from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.pergunta_entrevista import PerguntaEntrevista

from sqlalchemy import ForeignKey, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
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
    audio_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metricas: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    data_resposta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamentos
    pergunta: Mapped["PerguntaEntrevista"] = relationship(
        "PerguntaEntrevista", back_populates="resposta"
    )
