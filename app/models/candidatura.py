from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.models.candidato import Candidato
    from app.models.entrevista import Entrevista
    from app.models.vaga import Vaga
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
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
    score_triagem: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    feedback_triagem: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True
    )
    data_triagem: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    data_candidatura: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("vaga_id", "candidato_id", name="uq_vaga_candidato"),
    )

    # Relacionamentos
    vaga: Mapped[Vaga] = relationship("Vaga", back_populates="candidaturas")
    candidato: Mapped[Candidato] = relationship(
        "Candidato", back_populates="candidaturas"
    )
    entrevistas: Mapped[list[Entrevista]] = relationship(
        "Entrevista", back_populates="candidatura", cascade="all, delete-orphan"
    )
