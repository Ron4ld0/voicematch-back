from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from app.models.enums import StatusEntrevista


# Resposta de Pergunta
class RespostaCreate(BaseModel):
    audio_url: Optional[str] = None
    transcricao: Optional[str] = None
    metricas: Optional[Dict[str, Any]] = None


class RespostaResponse(BaseModel):
    id: UUID
    pergunta_id: UUID
    audio_url: Optional[str]
    transcricao: Optional[str]
    metricas: Optional[Dict[str, Any]]
    data_resposta: datetime

    class Config:
        from_attributes = True


# Pergunta de Entrevista
class PerguntaCreate(BaseModel):
    pergunta_texto: str
    ordem: int


class PerguntaResponse(BaseModel):
    id: UUID
    entrevista_id: UUID
    pergunta_texto: str
    ordem: int
    data_criacao: datetime
    resposta: Optional[RespostaResponse] = None

    class Config:
        from_attributes = True


# Entrevista
class EntrevistaBase(BaseModel):
    candidatura_id: UUID
    status: StatusEntrevista
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    score_geral: Optional[float] = Field(None, ge=0.0, le=10.0)
    feedback_candidato: Optional[str] = None
    feedback_recrutador: Optional[str] = None


class EntrevistaCreate(EntrevistaBase):
    pass


class EntrevistaUpdate(BaseModel):
    status: Optional[StatusEntrevista] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    score_geral: Optional[float] = Field(None, ge=0.0, le=10.0)
    feedback_candidato: Optional[str] = None
    feedback_recrutador: Optional[str] = None


class EntrevistaResponse(EntrevistaBase):
    id: UUID
    data_criacao: datetime
    perguntas: List[PerguntaResponse] = []

    class Config:
        from_attributes = True
