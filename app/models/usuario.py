from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.recrutador import Recrutador

from sqlalchemy import DateTime, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import TipoUsuario

if TYPE_CHECKING:
    from app.models.recrutador import Recrutador


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome_completo: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tipo_usuario: Mapped[TipoUsuario] = mapped_column(
        SQLEnum(TipoUsuario, name="tipo_usuario_enum"),
        nullable=False,
        default=TipoUsuario.recrutador,
    )
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamento 1:1 com Recrutador
    recrutador: Mapped[Recrutador | None] = relationship(
        "Recrutador",
        back_populates="usuario",
        cascade="all, delete-orphan",
        uselist=False,
    )
