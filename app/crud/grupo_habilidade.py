import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.grupo_habilidade import GrupoHabilidade, GrupoHabilidadeItem
from app.models.habilidade import TipoHabilidadeEnum
from app.schemas.grupo_habilidade import (
    GrupoHabilidadeCreate,
    GrupoHabilidadeUpdate,
)


def get_grupo_habilidade_by_id(
    db: Session, grupo_id: uuid.UUID
) -> GrupoHabilidade | None:
    """
    Busca um grupo de habilidades pelo ID com seus itens associados.
    """
    return db.query(GrupoHabilidade).filter(GrupoHabilidade.id == grupo_id).first()


def get_grupos_habilidades(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    tipo: TipoHabilidadeEnum | None = None,
    empresa_id: uuid.UUID | None = None,
) -> list[GrupoHabilidade]:
    """
    Lista grupos de habilidades com suporte a filtros por tipo (HARD/SOFT),
    busca textual (em nome e descrição) e paginação.
    """
    query = db.query(GrupoHabilidade)

    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            or_(
                GrupoHabilidade.nome.ilike(termo),
                GrupoHabilidade.descricao.ilike(termo),
            )
        )

    if tipo:
        query = query.filter(GrupoHabilidade.tipo == tipo)

    if empresa_id is not None:
        query = query.filter(
            or_(
                GrupoHabilidade.empresa_id == empresa_id,
                GrupoHabilidade.empresa_id.is_(None),
            )
        )

    return (
        query.order_by(GrupoHabilidade.data_criacao.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_grupo_habilidade(
    db: Session, grupo_in: GrupoHabilidadeCreate
) -> GrupoHabilidade:
    """
    Cria um novo grupo de habilidades e insere os itens associados.
    """
    db_grupo = GrupoHabilidade(
        nome=grupo_in.nome,
        tipo=grupo_in.tipo,
        descricao=grupo_in.descricao,
        empresa_id=grupo_in.empresa_id,
    )

    if grupo_in.itens:
        for item_in in grupo_in.itens:
            db_item = GrupoHabilidadeItem(
                habilidade_id=item_in.habilidade_id,
                peso=item_in.peso,
                obrigatoriedade=item_in.obrigatoriedade,
            )
            db_grupo.itens.append(db_item)

    db.add(db_grupo)
    db.commit()
    db.refresh(db_grupo)
    return db_grupo


def update_grupo_habilidade(
    db: Session, db_grupo: GrupoHabilidade, grupo_in: GrupoHabilidadeUpdate
) -> GrupoHabilidade:
    """
    Atualiza dados de um grupo de habilidades e sincroniza a lista de itens.
    """
    update_data = grupo_in.model_dump(exclude_unset=True)

    # Trata campos básicos
    for field in ["nome", "tipo", "descricao", "empresa_id"]:
        if field in update_data:
            setattr(db_grupo, field, update_data[field])

    # Sincroniza itens se fornecidos
    if grupo_in.itens is not None:
        db_grupo.itens.clear()
        for item_in in grupo_in.itens:
            db_item = GrupoHabilidadeItem(
                grupo_id=db_grupo.id,
                habilidade_id=item_in.habilidade_id,
                peso=item_in.peso,
                obrigatoriedade=item_in.obrigatoriedade,
            )
            db_grupo.itens.append(db_item)

    db.add(db_grupo)
    db.commit()
    db.refresh(db_grupo)
    return db_grupo


def delete_grupo_habilidade(db: Session, db_grupo: GrupoHabilidade) -> None:
    """
    Exclui um grupo de habilidades (os itens são excluídos via cascade).
    """
    db.delete(db_grupo)
    db.commit()
