from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.empresa import Empresa
    from app.models.usuario import Usuario
    from app.models.vaga import Vaga

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.empresa import Empresa
    from app.models.usuario import Usuario
    from app.models.vaga import Vaga


class Recrutador(Base):
    __tablename__ = "recrutador"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        primary_key=True,
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("empresa.id", ondelete="CASCADE"),
        nullable=False,
    )
    cargo: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relacionamento 1:1 com Usuario
    usuario: Mapped[Usuario] = relationship("Usuario", back_populates="recrutador")
    # Relacionamento N:1 com Empresa
    empresa: Mapped[Empresa] = relationship("Empresa", back_populates="recrutadores")
    # Relacionamento 1:N com Vaga
    vagas: Mapped[list[Vaga]] = relationship(
        "Vaga", back_populates="recrutador", cascade="all, delete-orphan"
    )
