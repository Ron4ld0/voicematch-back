from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.models.recrutador import Recrutador
    from app.models.vaga import Vaga
    from app.models.candidato import Candidato
    from app.models.habilidade import Habilidade
    from app.models.candidatura import Candidatura
    from app.models.grupo_habilidade import GrupoHabilidade

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import StatusEmpresa

class Empresa(Base):
    __tablename__ = "empresa"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[StatusEmpresa] = mapped_column(String(50), nullable=False, default=StatusEmpresa.ativa)
    cnpj: Mapped[str | None] = mapped_column(String(14), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    plano: Mapped[str | None] = mapped_column(String(50), nullable=True)
    configuracoes_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    missao_visao_valores: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    recrutadores: Mapped[list[Recrutador]] = relationship(
        "Recrutador", back_populates="empresa", cascade="all, delete-orphan"
    )
    vagas: Mapped[list[Vaga]] = relationship(
        "Vaga", back_populates="empresa", cascade="all, delete-orphan"
    )

    candidatos: Mapped[list["Candidato"]] = relationship(
        "Candidato", back_populates="empresa", cascade="all, delete-orphan"
    )
    candidaturas: Mapped[list[Candidatura]] = relationship(
        "Candidatura", back_populates="empresa", cascade="all, delete-orphan"
    )
    habilidades: Mapped[list[Habilidade]] = relationship(
        "Habilidade", back_populates="empresa", cascade="all, delete-orphan"
    )
    grupos_habilidades: Mapped[list[GrupoHabilidade]] = relationship(
        "GrupoHabilidade", back_populates="empresa", cascade="all, delete-orphan"
    )
