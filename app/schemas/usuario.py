from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# Sub-esquema de Recrutador
class RecrutadorCreate(BaseModel):
    empresa: str = Field(..., max_length=255)
    cargo: Optional[str] = Field(None, max_length=100)


class RecrutadorResponse(BaseModel):
    empresa: str
    cargo: Optional[str]

    class Config:
        from_attributes = True


# Esquemas de Usuario (sempre recrutador)
class UsuarioBase(BaseModel):
    nome_completo: str = Field(..., max_length=255)
    email: EmailStr
    telefone: Optional[str] = Field(None, max_length=50)
    cpf: Optional[str] = Field(None, max_length=14)


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, max_length=100)
    recrutador: Optional[RecrutadorCreate] = None


class UsuarioUpdate(BaseModel):
    nome_completo: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=50)
    cpf: Optional[str] = Field(None, max_length=14)
    senha: Optional[str] = Field(None, min_length=6, max_length=100)
    recrutador: Optional[RecrutadorCreate] = None


class UsuarioResponse(UsuarioBase):
    id: UUID
    tipo_usuario: str
    data_criacao: datetime
    recrutador: Optional[RecrutadorResponse] = None

    class Config:
        from_attributes = True
