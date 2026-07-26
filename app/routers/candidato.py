from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.core.database import get_db
from app.schemas.candidato import CandidatoCreate, CandidatoUpdate, CandidatoResponse
from app.crud.candidato import (
    get_candidato,
    get_candidato_by_email,
    get_candidatos,
    create_candidato,
    update_candidato,
    delete_candidato,
)

router = APIRouter(prefix="/candidatos", tags=["Candidatos"])


@router.post("", response_model=CandidatoResponse, status_code=status.HTTP_201_CREATED)
def register_candidato(candidato_in: CandidatoCreate, db: Session = Depends(get_db)):
    """
    Cria um novo candidato. Os candidatos não possuem senha e não acessam o sistema.
    """
    # Verificando se já existe um candidato com este email
    db_candidato = get_candidato_by_email(db, email=candidato_in.email)
    if db_candidato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este endereço de email já está cadastrado como candidato.",
        )

    # Criar o perfil do candidato
    db_candidato = create_candidato(db, candidato_in=candidato_in)
    return db_candidato


@router.get("", response_model=List[CandidatoResponse])
def list_candidatos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os candidatos."""
    return get_candidatos(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=CandidatoResponse)
def read_candidato(id: UUID, db: Session = Depends(get_db)):
    """Retorna os dados de um candidato pelo ID."""
    db_candidato = get_candidato(db, candidato_id=id)
    if not db_candidato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidato não encontrado."
        )
    return db_candidato


@router.put("/{id}", response_model=CandidatoResponse)
def modify_candidato(
    id: UUID, candidato_in: CandidatoUpdate, db: Session = Depends(get_db)
):
    """Atualiza os dados de um candidato."""
    db_candidato = get_candidato(db, candidato_id=id)
    if not db_candidato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidato não encontrado."
        )
    return update_candidato(db, db_candidato=db_candidato, candidato_in=candidato_in)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_candidato(id: UUID, db: Session = Depends(get_db)):
    """Remove um candidato."""
    success = delete_candidato(db, candidato_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidato não encontrado para deleção.",
        )
    return None
