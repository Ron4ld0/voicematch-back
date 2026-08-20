from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CandidatoBase(BaseModel):
    nome: str = Field(..., max_length=255)
    email: EmailStr
    telefone: str | None = Field(None, max_length=50)
    curriculo_url: str | None = None
    resumo_profissional: str | None = None
    experiencias: dict[str, Any] | None = None
    tecnologias: dict[str, Any] | None = None


class CandidatoCreate(CandidatoBase):
    vaga_id_referencia: UUID | None = None


class CandidatoUpdate(BaseModel):
    nome: str | None = Field(None, max_length=255)
    email: EmailStr | None = None
    telefone: str | None = Field(None, max_length=50)
    curriculo_url: str | None = None
    resumo_profissional: str | None = None
    experiencias: dict[str, Any] | None = None
    tecnologias: dict[str, Any] | None = None


class CandidatoResponse(CandidatoBase):
    id: UUID
    empresa_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)
