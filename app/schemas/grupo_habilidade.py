from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.habilidade import ObrigatoriedadeEnum, TipoHabilidadeEnum
from app.schemas.habilidade import HabilidadeResponse


class GrupoHabilidadeItemCreate(BaseModel):
    habilidade_id: UUID
    peso: int = Field(1, ge=1, le=10, description="Peso de relevância (1 a 10)")
    obrigatoriedade: ObrigatoriedadeEnum = Field(
        default=ObrigatoriedadeEnum.DESEJAVEL,
        description="Indica se a habilidade é obrigatória ou desejável",
    )


class GrupoHabilidadeItemResponse(BaseModel):
    habilidade_id: UUID
    peso: int
    obrigatoriedade: ObrigatoriedadeEnum
    habilidade: HabilidadeResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class GrupoHabilidadeBase(BaseModel):
    nome: str = Field(..., max_length=255)
    tipo: TipoHabilidadeEnum
    descricao: str | None = None
    empresa_id: UUID | None = None


class GrupoHabilidadeCreate(GrupoHabilidadeBase):
    itens: list[GrupoHabilidadeItemCreate] = Field(default_factory=list)


class GrupoHabilidadeUpdate(BaseModel):
    nome: str | None = Field(None, max_length=255)
    tipo: TipoHabilidadeEnum | None = None
    descricao: str | None = None
    empresa_id: UUID | None = None
    itens: list[GrupoHabilidadeItemCreate] | None = None


class GrupoHabilidadeResponse(GrupoHabilidadeBase):
    id: UUID
    data_criacao: datetime
    itens: list[GrupoHabilidadeItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
