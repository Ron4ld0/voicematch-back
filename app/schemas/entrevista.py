from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import StatusEntrevista


# Resposta de Pergunta
class RespostaCreate(BaseModel):
    audio_url: str | None = None
    transcricao: str | None = None
    metricas: dict[str, Any] | None = None


class RespostaResponse(BaseModel):
    id: UUID
    pergunta_id: UUID
    audio_url: str | None
    transcricao: str | None
    metricas: dict[str, Any] | None
    data_resposta: datetime

    model_config = ConfigDict(from_attributes=True)


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
    resposta: RespostaResponse | None = None

    model_config = ConfigDict(from_attributes=True)


# Entrevista
class EntrevistaBase(BaseModel):
    candidatura_id: UUID
    status: StatusEntrevista
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
    score_geral: float | None = Field(None, ge=0.0, le=10.0)
    feedback_candidato: str | None = None
    feedback_recrutador: str | None = None


class EntrevistaCreate(EntrevistaBase):
    pass


class EntrevistaUpdate(BaseModel):
    status: StatusEntrevista | None = None
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
    score_geral: float | None = Field(None, ge=0.0, le=10.0)
    feedback_candidato: str | None = None
    feedback_recrutador: str | None = None


class EntrevistaResponse(EntrevistaBase):
    id: UUID
    data_criacao: datetime
    perguntas: list[PerguntaResponse] = []

    model_config = ConfigDict(from_attributes=True)
