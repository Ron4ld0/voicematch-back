from pydantic import ConfigDict, BaseModel, EmailStr, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.core.validators import validar_cnpj


# Sub-esquema de Recrutador
class RecrutadorCreate(BaseModel):
    empresa: str = Field(..., max_length=255)
    cnpj: Optional[str] = Field(None, max_length=18)
    cargo: Optional[str] = Field(None, max_length=100)

    @field_validator("cnpj")
    @classmethod
    def _valida_cnpj(cls, v: Optional[str]) -> Optional[str]:
        # Campo opcional: None e string vazia passam sem validação; o que for
        # preenchido é validado e normalizado para 14 dígitos.
        if v is None or not v.strip():
            return None
        return validar_cnpj(v)


class RecrutadorResponse(BaseModel):
    empresa: str
    cnpj: Optional[str] = None
    cargo: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# Esquemas de Usuario (sempre recrutador)
class UsuarioBase(BaseModel):
    nome_completo: str = Field(..., max_length=255)
    email: EmailStr
    telefone: Optional[str] = Field(None, max_length=50)


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, max_length=100)
    recrutador: Optional[RecrutadorCreate] = None


class UsuarioUpdate(BaseModel):
    nome_completo: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=50)
    senha: Optional[str] = Field(None, min_length=6, max_length=100)
    recrutador: Optional[RecrutadorCreate] = None


class UsuarioResponse(UsuarioBase):
    id: UUID
    tipo_usuario: str
    data_criacao: datetime
    recrutador: Optional[RecrutadorResponse] = None

    model_config = ConfigDict(from_attributes=True)
