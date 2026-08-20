from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.habilidade import Habilidade
    from app.models.vaga import Vaga
    from app.models.empresa import Empresa


import enum
import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.vaga import Vaga


class TipoHabilidadeEnum(str, enum.Enum):
    HARD = "HARD"
    SOFT = "SOFT"


class ObrigatoriedadeEnum(str, enum.Enum):
    OBRIGATORIA = "OBRIGATORIA"
    DESEJAVEL = "DESEJAVEL"


class Habilidade(Base):
    __tablename__ = "habilidade"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    tipo: Mapped[TipoHabilidadeEnum] = mapped_column(
        SQLEnum(TipoHabilidadeEnum), nullable=False
    )
    categoria: Mapped[str] = mapped_column(String, nullable=False)

    empresa_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empresa.id", ondelete="CASCADE"), nullable=True
    )

    empresa: Mapped[Empresa | None] = relationship("Empresa", back_populates="habilidades")


class VagaHabilidade(Base):
    __tablename__ = "vaga_habilidade"
    __table_args__ = (
        CheckConstraint("peso >= 1 AND peso <= 10", name="check_peso_range"),
    )

    vaga_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vaga.id", ondelete="CASCADE"), primary_key=True
    )
    habilidade_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("habilidade.id", ondelete="CASCADE"), primary_key=True
    )

    peso: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    obrigatoriedade: Mapped[ObrigatoriedadeEnum] = mapped_column(
        SQLEnum(ObrigatoriedadeEnum), default=ObrigatoriedadeEnum.DESEJAVEL
    )

    habilidade: Mapped[Habilidade] = relationship()

    vaga: Mapped[Vaga] = relationship(back_populates="habilidades_vinculadas")
