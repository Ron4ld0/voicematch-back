from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.habilidade import ObrigatoriedadeEnum, TipoHabilidadeEnum

if TYPE_CHECKING:
    from app.models.habilidade import Habilidade
    from app.models.empresa import Empresa


class GrupoHabilidade(Base):
    __tablename__ = "grupo_habilidade"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[TipoHabilidadeEnum] = mapped_column(
        SQLEnum(TipoHabilidadeEnum), nullable=False
    )
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    empresa_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empresa.id", ondelete="CASCADE"), nullable=True
    )
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    empresa: Mapped[Empresa | None] = relationship("Empresa", back_populates="grupos_habilidades")

    # Relacionamento com os itens/habilidades vinculadas ao grupo
    itens: Mapped[list[GrupoHabilidadeItem]] = relationship(
        "GrupoHabilidadeItem",
        back_populates="grupo",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class GrupoHabilidadeItem(Base):
    __tablename__ = "grupo_habilidade_item"
    __table_args__ = (
        CheckConstraint("peso >= 1 AND peso <= 10", name="check_grupo_item_peso_range"),
    )

    grupo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grupo_habilidade.id", ondelete="CASCADE"),
        primary_key=True,
    )
    habilidade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("habilidade.id", ondelete="CASCADE"),
        primary_key=True,
    )

    peso: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    obrigatoriedade: Mapped[ObrigatoriedadeEnum] = mapped_column(
        SQLEnum(ObrigatoriedadeEnum), default=ObrigatoriedadeEnum.DESEJAVEL
    )

    # Relacionamentos
    grupo: Mapped[GrupoHabilidade] = relationship(
        "GrupoHabilidade", back_populates="itens"
    )
    habilidade: Mapped[Habilidade] = relationship("Habilidade", lazy="selectin")
