import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.grupo_habilidade import (
    create_grupo_habilidade,
    delete_grupo_habilidade,
    get_grupo_habilidade_by_id,
    get_grupos_habilidades,
    update_grupo_habilidade,
)
from app.models.habilidade import TipoHabilidadeEnum
from app.schemas.grupo_habilidade import (
    GrupoHabilidadeCreate,
    GrupoHabilidadeResponse,
    GrupoHabilidadeUpdate,
)

router = APIRouter(prefix="/grupos-habilidades", tags=["Grupos de Habilidades"])


@router.post(
    "/",
    response_model=GrupoHabilidadeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar grupo de habilidades",
)
def cadastrar_grupo_habilidade(
    grupo_in: GrupoHabilidadeCreate,
    db: Session = Depends(get_db),
):
    """
    Cria um novo template de grupo de habilidades (Hard ou Soft) com suas competências e pesos.
    """
    return create_grupo_habilidade(db=db, grupo_in=grupo_in)


@router.get(
    "/",
    response_model=list[GrupoHabilidadeResponse],
    summary="Listar grupos de habilidades",
)
def listar_grupos_habilidades(
    skip: int = Query(0, ge=0, description="Offset de paginação"),
    limit: int = Query(100, ge=1, le=100, description="Limite por página"),
    busca: str | None = Query(
        None, description="Busca textual por nome ou descrição do grupo"
    ),
    tipo: TipoHabilidadeEnum | None = Query(
        None, description="Filtro por tipo (HARD ou SOFT)"
    ),
    empresa_id: uuid.UUID | None = Query(
        None, description="Filtro por ID da empresa vinculada"
    ),
    db: Session = Depends(get_db),
):
    """
    Lista grupos de habilidades com suporte a filtros por tipo e busca textual.
    """
    return get_grupos_habilidades(
        db=db,
        skip=skip,
        limit=limit,
        busca=busca,
        tipo=tipo,
        empresa_id=empresa_id,
    )


@router.get(
    "/{grupo_id}",
    response_model=GrupoHabilidadeResponse,
    summary="Obter detalhes de um grupo de habilidades",
)
def obter_grupo_habilidade(
    grupo_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Retorna os detalhes completos de um grupo de habilidades e suas competências vinculadas.
    """
    db_grupo = get_grupo_habilidade_by_id(db, grupo_id=grupo_id)
    if not db_grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo de habilidades não encontrado",
        )
    return db_grupo


@router.put(
    "/{grupo_id}",
    response_model=GrupoHabilidadeResponse,
    summary="Atualizar grupo de habilidades",
)
def atualizar_grupo_habilidade_endpoint(
    grupo_id: uuid.UUID,
    grupo_in: GrupoHabilidadeUpdate,
    db: Session = Depends(get_db),
):
    """
    Atualiza nome, descrição, tipo e sincroniza a lista de habilidades/pesos do grupo.
    """
    db_grupo = get_grupo_habilidade_by_id(db, grupo_id=grupo_id)
    if not db_grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo de habilidades não encontrado",
        )
    return update_grupo_habilidade(db=db, db_grupo=db_grupo, grupo_in=grupo_in)


@router.delete(
    "/{grupo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir grupo de habilidades",
)
def remover_grupo_habilidade(
    grupo_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Exclui um grupo de habilidades e seus itens associados.
    """
    db_grupo = get_grupo_habilidade_by_id(db, grupo_id=grupo_id)
    if not db_grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo de habilidades não encontrado",
        )
    delete_grupo_habilidade(db=db, db_grupo=db_grupo)
    return None
