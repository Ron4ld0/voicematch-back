from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.core.database import get_db
from app.schemas.vaga import VagaCreate, VagaUpdate, VagaResponse
from app.crud.vaga import create_vaga, get_vaga, get_vagas, update_vaga, delete_vaga
from app.crud.usuario import get_usuario
from app.schemas.habilidade import VagaHabilidadeCreate, VagaHabilidadeResponse
from app.crud.habilidade import get_habilidades_por_vaga, sincronizar_habilidades_vaga

router = APIRouter(prefix="/vagas", tags=["Vagas"])


@router.post("", response_model=VagaResponse, status_code=status.HTTP_201_CREATED)
def register_vaga(vaga_in: VagaCreate, db: Session = Depends(get_db)):
    # Validar se o recrutador (usuario) existe
    db_recrutador = get_usuario(db, usuario_id=vaga_in.recrutador_id)
    if not db_recrutador:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O ID do recrutador especificado é inválido ou não pertence a um recrutador cadastrado.",
        )
    return create_vaga(db, vaga_in=vaga_in)


@router.get("", response_model=List[VagaResponse])
def list_vagas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_vagas(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=VagaResponse)
def read_vaga(id: UUID, db: Session = Depends(get_db)):
    db_vaga = get_vaga(db, vaga_id=id)
    if not db_vaga:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vaga não encontrada."
        )
    return db_vaga


@router.put("/{id}", response_model=VagaResponse)
def modify_vaga(id: UUID, vaga_in: VagaUpdate, db: Session = Depends(get_db)):
    db_vaga = get_vaga(db, vaga_id=id)
    if not db_vaga:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vaga não encontrada."
        )
    return update_vaga(db, db_vaga=db_vaga, vaga_in=vaga_in)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_vaga(id: UUID, db: Session = Depends(get_db)):
    success = delete_vaga(db, vaga_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaga não encontrada para deleção.",
        )
    return None


@router.get("/{vaga_id}/habilidades", response_model=list[VagaHabilidadeResponse])
def listar_habilidades_da_vaga(vaga_id: UUID, db: Session = Depends(get_db)):
    """
    Lista as habilidades e pesos vinculados a uma vaga específica.
    """
    return get_habilidades_por_vaga(db=db, vaga_id=vaga_id)


@router.put("/{vaga_id}/habilidades", response_model=list[VagaHabilidadeResponse])
def atualizar_habilidades_da_vaga(
    vaga_id: UUID,
    habilidades_in: list[VagaHabilidadeCreate],
    db: Session = Depends(get_db),
):
    """
    Sincroniza as habilidades de uma vaga.
    A lista enviada substituirá completamente as habilidades anteriores.
    """
    return sincronizar_habilidades_vaga(
        db=db, vaga_id=vaga_id, habilidades_in=habilidades_in
    )
