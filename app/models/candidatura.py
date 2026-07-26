import uuid
from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, DateTime, Enum as SQLEnum, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
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
