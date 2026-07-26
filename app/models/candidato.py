import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Candidato(Base):
    __tablename__ = "candidato"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    telefone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    curriculo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resumo_profissional: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experiencias: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    tecnologias: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relacionamento 1:N com Candidatura
    candidaturas: Mapped[List["Candidatura"]] = relationship(
        "Candidatura", back_populates="candidato", cascade="all, delete-orphan"
    )
