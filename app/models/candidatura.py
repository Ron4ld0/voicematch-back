from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Dict, Any

if TYPE_CHECKING:
    from app.models.candidato import Candidato
    from app.models.entrevista import Entrevista
    from app.models.vaga import Vaga
from sqlalchemy import (
    ForeignKey,
    DateTime,
    Numeric,
    Enum as SQLEnum,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import StatusCandidatura


class Candidatura(Base):
    __tablename__ = "candidatura"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vaga_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vaga.id", ondelete="CASCADE"), nullable=False
    )
    candidato_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidato.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[StatusCandidatura] = mapped_column(
        SQLEnum(StatusCandidatura, name="status_candidatura_enum"), nullable=False
    )
    score_triagem: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    feedback_triagem: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    data_triagem: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    data_candidatura: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("vaga_id", "candidato_id", name="uq_vaga_candidato"),
    )

    # Relacionamentos
    vaga: Mapped["Vaga"] = relationship("Vaga", back_populates="candidaturas")
    candidato: Mapped["Candidato"] = relationship(
        "Candidato", back_populates="candidaturas"
    )
    entrevistas: Mapped[List["Entrevista"]] = relationship(
        "Entrevista", back_populates="candidatura", cascade="all, delete-orphan"
    )
