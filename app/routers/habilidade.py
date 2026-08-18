import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.habilidade import (
    create_habilidade,
    delete_habilidade,
    get_habilidade_by_id,
    get_habilidades,
    update_habilidade,
)
from app.models.habilidade import TipoHabilidadeEnum
from app.schemas.habilidade import (
    HabilidadeCreate,
    HabilidadeResponse,
    HabilidadeUpdate,
)

router = APIRouter(prefix="/habilidades", tags=["Habilidades"])

router = APIRouter(prefix="/habilidades", tags=["Habilidades"])


@router.post(
    "/", response_model=HabilidadeResponse, status_code=status.HTTP_201_CREATED
)
def cadastrar_habilidade(
    habilidade_in: HabilidadeCreate, db: Session = Depends(get_db)
):
    """
    Cadastra uma nova habilidade no catálogo.
    """
    return create_habilidade(db=db, habilidade_in=habilidade_in)


@router.get("/", response_model=list[HabilidadeResponse])
def listar_habilidades(
    skip: int = 0,
    limit: int = 100,
    nome: str | None = None,
    tipo: TipoHabilidadeEnum | None = None,
    db: Session = Depends(get_db),
):
    """
    Lista as habilidades cadastradas com paginação, busca textual e filtro por tipo.
    """
    return get_habilidades(db=db, skip=skip, limit=limit, nome=nome, tipo=tipo)


@router.put("/{habilidade_id}", response_model=HabilidadeResponse)
def atualizar_habilidade(
    habilidade_id: uuid.UUID,
    habilidade_in: HabilidadeUpdate,
    db: Session = Depends(get_db),
):
    """
    Atualiza os dados de uma habilidade existente.
    """
    db_habilidade = get_habilidade_by_id(db, habilidade_id)
    if not db_habilidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habilidade não encontrada"
        )

    return update_habilidade(
        db=db, db_habilidade=db_habilidade, habilidade_in=habilidade_in
    )


@router.delete("/{habilidade_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_habilidade(habilidade_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Remove uma habilidade do catálogo.
    """
    db_habilidade = get_habilidade_by_id(db, habilidade_id)
    if not db_habilidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habilidade não encontrada"
        )

    delete_habilidade(db=db, db_habilidade=db_habilidade)

    return None
