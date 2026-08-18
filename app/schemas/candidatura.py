from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatusCandidatura


class CandidaturaBase(BaseModel):
    vaga_id: UUID
    candidato_id: UUID


class CandidaturaCreate(CandidaturaBase):
    pass


class CandidaturaStatusUpdate(BaseModel):
    status: StatusCandidatura


class CandidaturaResponse(BaseModel):
    id: UUID
    vaga_id: UUID
    candidato_id: UUID
    status: StatusCandidatura
    score_triagem: float | None = None
    feedback_triagem: dict[str, Any] | None = None
    data_triagem: datetime | None = None
    data_candidatura: datetime

    model_config = ConfigDict(from_attributes=True)
