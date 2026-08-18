from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.candidatura import Candidatura
from app.models.enums import StatusCandidatura
from app.schemas.candidatura import CandidaturaCreate, CandidaturaStatusUpdate


def get_candidatura(db: Session, candidatura_id: UUID) -> Candidatura | None:
    return db.query(Candidatura).filter(Candidatura.id == candidatura_id).first()


def get_candidatura_by_vaga_and_candidato(
    db: Session, vaga_id: UUID, candidato_id: UUID
) -> Candidatura | None:
    return (
        db.query(Candidatura)
        .filter(
            Candidatura.vaga_id == vaga_id, Candidatura.candidato_id == candidato_id
        )
        .first()
    )


def get_candidaturas_by_vaga(db: Session, vaga_id: UUID) -> list[Candidatura]:
    return db.query(Candidatura).filter(Candidatura.vaga_id == vaga_id).all()


def get_candidaturas_by_candidato(db: Session, candidato_id: UUID) -> list[Candidatura]:
    return db.query(Candidatura).filter(Candidatura.candidato_id == candidato_id).all()


def create_candidatura(db: Session, candidatura_in: CandidaturaCreate) -> Candidatura:
    db_candidatura = Candidatura(
        vaga_id=candidatura_in.vaga_id,
        candidato_id=candidatura_in.candidato_id,
        status=StatusCandidatura.pendente_triagem,
    )
    db.add(db_candidatura)
    db.commit()
    db.refresh(db_candidatura)
    return db_candidatura


def update_candidatura_status(
    db: Session, db_candidatura: Candidatura, status_in: CandidaturaStatusUpdate
) -> Candidatura:
    db_candidatura.status = status_in.status
    db.commit()
    db.refresh(db_candidatura)
    return db_candidatura


def update_candidatura_triagem(
    db: Session,
    db_candidatura: Candidatura,
    score_triagem: float | None,
    feedback_triagem: dict[str, Any] | None,
    status: StatusCandidatura,
    data_triagem: datetime | None = None,
) -> Candidatura:
    db_candidatura.score_triagem = score_triagem
    db_candidatura.feedback_triagem = feedback_triagem
    db_candidatura.status = status
    db_candidatura.data_triagem = data_triagem
    db.commit()
    db.refresh(db_candidatura)
    return db_candidatura
