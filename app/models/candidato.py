from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.models.candidatura import Candidatura

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
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
    telefone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    curriculo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    resumo_profissional: Mapped[str | None] = mapped_column(Text, nullable=True)
    experiencias: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    tecnologias: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Relacionamento 1:N com Candidatura
    candidaturas: Mapped[list[Candidatura]] = relationship(
        "Candidatura", back_populates="candidato", cascade="all, delete-orphan"
    )
