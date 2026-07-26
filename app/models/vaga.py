import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, ForeignKey, DateTime, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import StatusVaga


class Vaga(Base):
    __tablename__ = "vaga"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    recrutador_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recrutador.id", ondelete="CASCADE"),
        nullable=False,
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    descricao_candidato_ideal: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    requisitos_hard: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    requisitos_soft: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    status: Mapped[StatusVaga] = mapped_column(
        SQLEnum(StatusVaga, name="status_vaga_enum"), nullable=False
    )
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamentos
    recrutador: Mapped["Recrutador"] = relationship(
        "Recrutador", back_populates="vagas"
    )
    candidaturas: Mapped[List["Candidatura"]] = relationship(
        "Candidatura", back_populates="vaga", cascade="all, delete-orphan"
    )
