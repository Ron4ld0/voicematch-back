from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.core.database import get_db
from app.schemas.candidatura import (
    CandidaturaCreate,
    CandidaturaStatusUpdate,
    CandidaturaResponse,
)
from app.crud.candidatura import (
    create_candidatura,
    get_candidatura,
    get_candidatura_by_vaga_and_candidato,
    get_candidaturas_by_vaga,
    get_candidaturas_by_candidato,
    update_candidatura_status,
)
from app.crud.candidato import get_candidato
from app.crud.vaga import get_vaga

router = APIRouter(prefix="/candidaturas", tags=["Candidaturas"])


@router.post(
    "", response_model=CandidaturaResponse, status_code=status.HTTP_201_CREATED
)
def apply_to_vaga(candidatura_in: CandidaturaCreate, db: Session = Depends(get_db)):
    """Cria uma nova candidatura vinculando um candidato a uma vaga."""
    # 1. Validar se a vaga existe
    db_vaga = get_vaga(db, vaga_id=candidatura_in.vaga_id)
    if not db_vaga:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A vaga especificada não existe.",
        )

    # 2. Validar se o candidato existe
    db_candidato = get_candidato(db, candidato_id=candidatura_in.candidato_id)
    if not db_candidato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O candidato especificado não existe.",
        )

    # 3. Validar se o candidato já se candidatou para essa vaga
    existing_candidatura = get_candidatura_by_vaga_and_candidato(
        db, vaga_id=candidatura_in.vaga_id, candidato_id=candidatura_in.candidato_id
    )
    if existing_candidatura:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este candidato já se candidatou a esta vaga anteriormente.",
        )

    return create_candidatura(db, candidatura_in=candidatura_in)


@router.get("/{id}", response_model=CandidaturaResponse)
def read_candidatura(id: UUID, db: Session = Depends(get_db)):
    """Retorna os dados de uma candidatura pelo ID."""
    db_candidatura = get_candidatura(db, candidatura_id=id)
    if not db_candidatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidatura não encontrada."
        )
    return db_candidatura


@router.get("/vaga/{vaga_id}", response_model=List[CandidaturaResponse])
def read_candidaturas_by_vaga(vaga_id: UUID, db: Session = Depends(get_db)):
    """Lista todas as candidaturas de uma vaga específica."""
    db_vaga = get_vaga(db, vaga_id=vaga_id)
    if not db_vaga:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A vaga especificada não existe.",
        )
    return get_candidaturas_by_vaga(db, vaga_id=vaga_id)


@router.get("/candidato/{candidato_id}", response_model=List[CandidaturaResponse])
def read_candidaturas_by_candidato(candidato_id: UUID, db: Session = Depends(get_db)):
    """Lista todas as candidaturas de um candidato específico."""
    db_candidato = get_candidato(db, candidato_id=candidato_id)
    if not db_candidato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidato não encontrado."
        )
    return get_candidaturas_by_candidato(db, candidato_id=candidato_id)


@router.patch("/{id}/status", response_model=CandidaturaResponse)
def modify_candidatura_status(
    id: UUID, status_in: CandidaturaStatusUpdate, db: Session = Depends(get_db)
):
    """Atualiza o status de uma candidatura (ex: pendente → aprovado)."""
    db_candidatura = get_candidatura(db, candidatura_id=id)
    if not db_candidatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidatura não encontrada."
        )
    return update_candidatura_status(
        db, db_candidatura=db_candidatura, status_in=status_in
    )
