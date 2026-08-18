from __future__ import annotations
import uuid
from typing import Optional, List

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.vaga import Vaga

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.vaga import Vaga


class Recrutador(Base):
    __tablename__ = "recrutador"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        primary_key=True,
    )
    empresa: Mapped[str] = mapped_column(String(255), nullable=False)
    # Sem unique: vários recrutadores podem pertencer à mesma empresa.
    cnpj: Mapped[Optional[str]] = mapped_column(String(14), nullable=True)
    cargo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relacionamento 1:1 com Usuario
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="recrutador")
    # Relacionamento 1:N com Vaga
    vagas: Mapped[List["Vaga"]] = relationship(
        "Vaga", back_populates="recrutador", cascade="all, delete-orphan"
    )
