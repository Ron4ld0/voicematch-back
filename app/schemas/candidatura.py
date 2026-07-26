from pydantic import BaseModel
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
    data_candidatura: datetime

    class Config:
        from_attributes = True
