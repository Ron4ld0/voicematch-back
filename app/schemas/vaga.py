from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import StatusVaga


class VagaBase(BaseModel):
    titulo: str = Field(..., max_length=255)
    descricao: str
    descricao_candidato_ideal: str | None = None
    requisitos_hard: dict[str, Any] | None = None
    requisitos_soft: dict[str, Any] | None = None
    score_minimo_triagem: float | None = None
    status: StatusVaga


class VagaCreate(VagaBase):
    recrutador_id: UUID


class VagaUpdate(BaseModel):
    titulo: str | None = Field(None, max_length=255)
    descricao: str | None = None
    descricao_candidato_ideal: str | None = None
    requisitos_hard: dict[str, Any] | None = None
    requisitos_soft: dict[str, Any] | None = None
    score_minimo_triagem: float | None = None
    status: StatusVaga | None = None


class VagaResponse(VagaBase):
    id: UUID
    recrutador_id: UUID
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)
