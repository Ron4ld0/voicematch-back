from pydantic import ConfigDict, BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
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
    score_triagem: Optional[float] = None
    feedback_triagem: Optional[Dict[str, Any]] = None
    data_triagem: Optional[datetime] = None
    data_candidatura: datetime

    model_config = ConfigDict(from_attributes=True)
