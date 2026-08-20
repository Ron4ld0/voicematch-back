from uuid import UUID

from sqlalchemy.orm import Session

from app.models.candidato import Candidato
from app.schemas.candidato import CandidatoCreate, CandidatoUpdate


def get_candidato(db: Session, candidato_id: UUID, empresa_id: UUID | None = None) -> Candidato | None:
    query = db.query(Candidato).filter(Candidato.id == candidato_id)
    if empresa_id:
        query = query.filter(Candidato.empresa_id == empresa_id)
    return query.first()


def get_candidato_by_email(db: Session, email: str, empresa_id: UUID) -> Candidato | None:
    return db.query(Candidato).filter(
        Candidato.email == email,
        Candidato.empresa_id == empresa_id
    ).first()


def get_candidatos(db: Session, empresa_id: UUID, skip: int = 0, limit: int = 100) -> list[Candidato]:
    return db.query(Candidato).filter(Candidato.empresa_id == empresa_id).offset(skip).limit(limit).all()


def create_candidato(db: Session, candidato_in: CandidatoCreate, empresa_id: UUID) -> Candidato:
    db_candidato = Candidato(
        nome=candidato_in.nome,
        email=candidato_in.email,
        telefone=candidato_in.telefone,
        curriculo_url=candidato_in.curriculo_url,
        resumo_profissional=candidato_in.resumo_profissional,
        experiencias=candidato_in.experiencias,
        tecnologias=candidato_in.tecnologias,
        empresa_id=empresa_id,
    )
    db.add(db_candidato)
    db.commit()
    db.refresh(db_candidato)
    return db_candidato


def update_candidato(
    db: Session, db_candidato: Candidato, candidato_in: CandidatoUpdate
) -> Candidato:
    update_data = candidato_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_candidato, field, value)
    db.commit()
    db.refresh(db_candidato)
    return db_candidato


def delete_candidato(db: Session, candidato_id: UUID) -> bool:
    db_candidato = db.query(Candidato).filter(Candidato.id == candidato_id).first()
    if not db_candidato:
        return False
    db.delete(db_candidato)
    db.commit()
    return True
