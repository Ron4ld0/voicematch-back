import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.enums import StatusEmpresa


class EmpresaBase(BaseModel):
    nome: str
    cnpj: str | None = None
    logo_url: str | None = None
    plano: str | None = None
    configuracoes_json: dict[str, Any] | None = None
    missao_visao_valores: str | None = None
    status: StatusEmpresa | None = None


class EmpresaCreate(EmpresaBase):
    pass


class EmpresaUpdate(BaseModel):
    nome: str | None = None
    cnpj: str | None = None
    logo_url: str | None = None
    plano: str | None = None
    configuracoes_json: dict[str, Any] | None = None
    missao_visao_valores: str | None = None
    status: StatusEmpresa | None = None


class EmpresaResponse(EmpresaBase):
    id: uuid.UUID
    data_criacao: datetime
    status: StatusEmpresa
    total_usuarios: int = 0
    total_vagas: int = 0
    total_candidaturas: int = 0

    model_config = {"from_attributes": True}
