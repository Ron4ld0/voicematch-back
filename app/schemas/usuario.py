from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Sub-esquema de Recrutador
class RecrutadorCreate(BaseModel):
    cargo: str | None = Field(None, max_length=100)


class RecrutadorResponse(BaseModel):
    empresa_id: UUID | None = None
    cargo: str | None

    model_config = ConfigDict(from_attributes=True)


# Esquemas de Usuario (sempre recrutador)
class UsuarioBase(BaseModel):
    nome_completo: str = Field(..., max_length=255)
    email: EmailStr
    telefone: str | None = Field(None, max_length=50)


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, max_length=100)
    recrutador: RecrutadorCreate | None = None


class UsuarioUpdate(BaseModel):
    nome_completo: str | None = Field(None, max_length=255)
    email: EmailStr | None = None
    telefone: str | None = Field(None, max_length=50)
    senha: str | None = Field(None, min_length=6, max_length=100)
    recrutador: RecrutadorCreate | None = None


class UsuarioResponse(UsuarioBase):
    id: UUID
    tipo_usuario: str
    empresa_id: UUID | None = None
    data_criacao: datetime
    recrutador: RecrutadorResponse | None = None

    model_config = ConfigDict(from_attributes=True)
