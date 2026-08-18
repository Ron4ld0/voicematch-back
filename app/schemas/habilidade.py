import uuid
from typing import Optional
from pydantic import BaseModel, Field
from app.models.habilidade import TipoHabilidadeEnum, ObrigatoriedadeEnum


class HabilidadeBase(BaseModel):
    nome: str = Field(..., example="Python")
    tipo: TipoHabilidadeEnum = Field(..., example="HARD")
    categoria: str = Field(..., example="Backend")
    empresa_id: Optional[uuid.UUID] = None


class HabilidadeCreate(HabilidadeBase):
    pass


class HabilidadeResponse(HabilidadeBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class HabilidadeUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[TipoHabilidadeEnum] = None
    categoria: Optional[str] = None
    empresa_id: Optional[uuid.UUID] = None


class VagaHabilidadeCreate(BaseModel):
    habilidade_id: uuid.UUID
    peso: int = Field(..., ge=1, le=10, description="Peso de relevância (1 a 10)")
    obrigatoriedade: ObrigatoriedadeEnum


class VagaHabilidadeResponse(BaseModel):
    habilidade_id: uuid.UUID
    peso: int
    obrigatoriedade: ObrigatoriedadeEnum

    habilidade: HabilidadeResponse

    class Config:
        from_attributes = True
