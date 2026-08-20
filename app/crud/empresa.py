import uuid
from typing import Sequence

from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.recrutador import Recrutador
from app.models.vaga import Vaga
from app.models.candidatura import Candidatura
from app.models.enums import StatusEmpresa
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate


def _map_aggregates(row) -> Empresa:
    emp = row[0]
    emp.total_usuarios = row[1]
    emp.total_vagas = row[2]
    emp.total_candidaturas = row[3]
    return emp


def get_empresa(db: Session, empresa_id: uuid.UUID) -> Empresa | None:
    stmt = (
        select(
            Empresa,
            func.count(Recrutador.id.distinct()).label("total_usuarios"),
            func.count(Vaga.id.distinct()).label("total_vagas"),
            func.count(Candidatura.id.distinct()).label("total_candidaturas"),
        )
        .outerjoin(Recrutador, Recrutador.empresa_id == Empresa.id)
        .outerjoin(Vaga, Vaga.empresa_id == Empresa.id)
        .outerjoin(Candidatura, Candidatura.empresa_id == Empresa.id)
        .where(Empresa.id == empresa_id)
        .group_by(Empresa.id)
    )
    row = db.execute(stmt).first()
    if not row:
        return None
    return _map_aggregates(row)


def get_empresa_by_cnpj(db: Session, cnpj: str) -> Empresa | None:
    return db.execute(select(Empresa).where(Empresa.cnpj == cnpj)).scalar_one_or_none()


def get_empresas(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: StatusEmpresa | None = None,
    busca: str | None = None
) -> Sequence[Empresa]:
    stmt = (
        select(
            Empresa,
            func.count(Recrutador.id.distinct()).label("total_usuarios"),
            func.count(Vaga.id.distinct()).label("total_vagas"),
            func.count(Candidatura.id.distinct()).label("total_candidaturas"),
        )
        .outerjoin(Recrutador, Recrutador.empresa_id == Empresa.id)
        .outerjoin(Vaga, Vaga.empresa_id == Empresa.id)
        .outerjoin(Candidatura, Candidatura.empresa_id == Empresa.id)
        .group_by(Empresa.id)
    )

    if status:
        stmt = stmt.where(Empresa.status == status)
    
    if busca:
        stmt = stmt.where(
            or_(
                Empresa.nome.ilike(f"%{busca}%"),
                Empresa.cnpj.ilike(f"%{busca}%")
            )
        )

    results = db.execute(stmt.offset(skip).limit(limit)).all()
    return [_map_aggregates(row) for row in results]


def create_empresa(db: Session, empresa_in: EmpresaCreate) -> Empresa:
    db_empresa = Empresa(**empresa_in.model_dump())
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    # Ensure properties exist
    db_empresa.total_usuarios = 0
    db_empresa.total_vagas = 0
    db_empresa.total_candidaturas = 0
    return db_empresa


def update_empresa(
    db: Session, db_empresa: Empresa, empresa_in: EmpresaUpdate
) -> Empresa:
    update_data = empresa_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_empresa, field, value)
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    return db_empresa
