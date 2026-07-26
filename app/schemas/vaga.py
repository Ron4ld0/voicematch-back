from pydantic import ConfigDict, BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models.enums import StatusVaga


class VagaBase(BaseModel):
    titulo: str = Field(..., max_length=255)
    descricao: str
    descricao_candidato_ideal: Optional[str] = None
    requisitos_hard: Optional[Dict[str, Any]] = None
    requisitos_soft: Optional[Dict[str, Any]] = None
    status: StatusVaga


class VagaCreate(VagaBase):
    recrutador_id: UUID


class VagaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=255)
    descricao: Optional[str] = None
    descricao_candidato_ideal: Optional[str] = None
    requisitos_hard: Optional[Dict[str, Any]] = None
    requisitos_soft: Optional[Dict[str, Any]] = None
    status: Optional[StatusVaga] = None


class VagaResponse(VagaBase):
    id: UUID
    recrutador_id: UUID
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)
