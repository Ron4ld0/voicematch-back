from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.validators import validar_cnpj


# Sub-esquema de Recrutador
class RecrutadorCreate(BaseModel):
    empresa: str = Field(..., max_length=255)
    cnpj: str | None = Field(None, max_length=18)
    cargo: str | None = Field(None, max_length=100)

    @field_validator("cnpj")
    @classmethod
    def _valida_cnpj(cls, v: str | None) -> str | None:
        # Campo opcional: None e string vazia passam sem validação; o que for
        # preenchido é validado e normalizado para 14 dígitos.
        if v is None or not v.strip():
            return None
        return validar_cnpj(v)


class RecrutadorResponse(BaseModel):
    empresa: str
    cnpj: str | None = None
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
    data_criacao: datetime
    recrutador: RecrutadorResponse | None = None

    model_config = ConfigDict(from_attributes=True)
