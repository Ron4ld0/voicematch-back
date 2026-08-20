import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.habilidade import Habilidade, TipoHabilidadeEnum, VagaHabilidade
from app.schemas.habilidade import (
    HabilidadeCreate,
    HabilidadeUpdate,
    VagaHabilidadeCreate,
)


def get_habilidade_by_id(
    db: Session, habilidade_id: uuid.UUID, empresa_id: uuid.UUID | None = None
) -> Habilidade | None:
    query = db.query(Habilidade).filter(Habilidade.id == habilidade_id)
    if empresa_id:
        query = query.filter(
            or_(Habilidade.empresa_id.is_(None), Habilidade.empresa_id == empresa_id)
        )
    else:
        query = query.filter(Habilidade.empresa_id.is_(None))
    return query.first()


def update_habilidade(
    db: Session, db_habilidade: Habilidade, habilidade_in: HabilidadeUpdate
) -> Habilidade:

    update_data = habilidade_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_habilidade, key, value)

    db.add(db_habilidade)
    db.commit()
    db.refresh(db_habilidade)
    return db_habilidade


def delete_habilidade(db: Session, db_habilidade: Habilidade) -> None:
    db.delete(db_habilidade)
    db.commit()


def create_habilidade(db: Session, habilidade_in: HabilidadeCreate) -> Habilidade:
    db_habilidade = Habilidade(
        nome=habilidade_in.nome,
        tipo=habilidade_in.tipo,
        categoria=habilidade_in.categoria,
        empresa_id=habilidade_in.empresa_id,
    )

    db.add(db_habilidade)
    db.commit()
    db.refresh(db_habilidade)

    return db_habilidade


def get_habilidades(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    nome: str | None = None,
    tipo: TipoHabilidadeEnum | None = None,
    empresa_id: uuid.UUID | None = None,
):
    query = db.query(Habilidade)

    if empresa_id:
        query = query.filter(
            or_(Habilidade.empresa_id.is_(None), Habilidade.empresa_id == empresa_id)
        )
    else:
        query = query.filter(Habilidade.empresa_id.is_(None))

    if nome:
        query = query.filter(Habilidade.nome.ilike(f"%{nome}%"))

    if tipo:
        query = query.filter(Habilidade.tipo == tipo)

    return query.offset(skip).limit(limit).all()


def get_habilidades_por_vaga(db: Session, vaga_id: uuid.UUID):
    """
    Retorna todos os vínculos de habilidades de uma vaga específica.
    """
    return db.query(VagaHabilidade).filter(VagaHabilidade.vaga_id == vaga_id).all()


def sincronizar_habilidades_vaga(
    db: Session, vaga_id: uuid.UUID, habilidades_in: list[VagaHabilidadeCreate]
) -> list[VagaHabilidade]:
    """
    Sincroniza as habilidades de uma vaga. Remove as antigas e insere as novas,
    garantindo que o banco fique exatamente igual à lista enviada pelo frontend.
    """
    db.query(VagaHabilidade).filter(VagaHabilidade.vaga_id == vaga_id).delete()

    novos_vinculos = []
    for hab_in in habilidades_in:
        novo_vinculo = VagaHabilidade(
            vaga_id=vaga_id,
            habilidade_id=hab_in.habilidade_id,
            peso=hab_in.peso,
            obrigatoriedade=hab_in.obrigatoriedade,
        )
        db.add(novo_vinculo)
        novos_vinculos.append(novo_vinculo)

    db.commit()

    return get_habilidades_por_vaga(db, vaga_id)
