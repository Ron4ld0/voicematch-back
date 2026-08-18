from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime, Numeric, Text, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import StatusEntrevista

if TYPE_CHECKING:
    from app.models.candidatura import Candidatura
    from app.models.pergunta_entrevista import PerguntaEntrevista


class Entrevista(Base):
    __tablename__ = "entrevista"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidatura_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidatura.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[StatusEntrevista] = mapped_column(
        SQLEnum(StatusEntrevista, name="status_entrevista_enum"), nullable=False
    )
    data_inicio: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    data_fim: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    score_geral: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    feedback_candidato: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_recrutador: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamentos
    candidatura: Mapped["Candidatura"] = relationship(
        "Candidatura", back_populates="entrevistas"
    )
    perguntas: Mapped[List["PerguntaEntrevista"]] = relationship(
        "PerguntaEntrevista",
        back_populates="entrevista",
        order_by="PerguntaEntrevista.ordem",
        cascade="all, delete-orphan",
    )
