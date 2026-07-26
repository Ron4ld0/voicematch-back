from pydantic import ConfigDict, BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from uuid import UUID


class CandidatoBase(BaseModel):
    nome: str = Field(..., max_length=255)
    email: EmailStr
    telefone: Optional[str] = Field(None, max_length=50)
    curriculo_url: Optional[str] = None
    resumo_profissional: Optional[str] = None
    experiencias: Optional[Dict[str, Any]] = None
    tecnologias: Optional[Dict[str, Any]] = None


class CandidatoCreate(CandidatoBase):
    pass


class CandidatoUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=50)
    curriculo_url: Optional[str] = None
    resumo_profissional: Optional[str] = None
    experiencias: Optional[Dict[str, Any]] = None
    tecnologias: Optional[Dict[str, Any]] = None


class CandidatoResponse(CandidatoBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
