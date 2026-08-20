from uuid import UUID

from sqlalchemy.orm import Session

from app.models.vaga import Vaga
from app.schemas.vaga import VagaCreate, VagaUpdate


def get_vaga(db: Session, vaga_id: UUID, empresa_id: UUID) -> Vaga | None:
    return db.query(Vaga).filter(Vaga.id == vaga_id, Vaga.empresa_id == empresa_id).first()


def get_vagas(db: Session, empresa_id: UUID, skip: int = 0, limit: int = 100) -> list[Vaga]:
    return db.query(Vaga).filter(Vaga.empresa_id == empresa_id).offset(skip).limit(limit).all()


def create_vaga(db: Session, vaga_in: VagaCreate, empresa_id: UUID) -> Vaga:
    db_vaga = Vaga(
        recrutador_id=vaga_in.recrutador_id,
        empresa_id=empresa_id,
        titulo=vaga_in.titulo,
        descricao=vaga_in.descricao,
        descricao_candidato_ideal=vaga_in.descricao_candidato_ideal,
        requisitos_hard=vaga_in.requisitos_hard,
        requisitos_soft=vaga_in.requisitos_soft,
        score_minimo_triagem=vaga_in.score_minimo_triagem,
        status=vaga_in.status,
    )
    db.add(db_vaga)
    db.commit()
    db.refresh(db_vaga)
    return db_vaga


def update_vaga(db: Session, db_vaga: Vaga, vaga_in: VagaUpdate) -> Vaga:
    update_data = vaga_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vaga, field, value)
    db.commit()
    db.refresh(db_vaga)
    return db_vaga


def delete_vaga(db: Session, vaga_id: UUID, empresa_id: UUID) -> bool:
    db_vaga = db.query(Vaga).filter(Vaga.id == vaga_id, Vaga.empresa_id == empresa_id).first()
    if not db_vaga:
        return False
    db.delete(db_vaga)
    db.commit()
    return True
