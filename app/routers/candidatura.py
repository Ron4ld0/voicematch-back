import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.core.database import get_db
from app.models.enums import StatusCandidatura
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
    update_candidatura_triagem,
)
from app.crud.entrevista import inicializar_entrevista_automatica
from app.crud.candidato import get_candidato
from app.crud.vaga import get_vaga
from app.services.triagem_service import analisar_curriculo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/candidaturas", tags=["Candidaturas"])


@router.get("", response_model=List[CandidaturaResponse])
def list_candidaturas(db: Session = Depends(get_db)):
    """Lista todas as candidaturas registradas no sistema."""
    from app.models.candidatura import Candidatura
    return db.query(Candidatura).all()


@router.post(
    "", response_model=CandidaturaResponse, status_code=status.HTTP_201_CREATED
)
def apply_to_vaga(candidatura_in: CandidaturaCreate, db: Session = Depends(get_db)):
    """Cria uma nova candidatura vinculando um candidato a uma vaga e executa a triagem automática por IA."""
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

    db_candidatura = create_candidatura(db, candidatura_in=candidatura_in)

    # 4. Executar a triagem síncrona de currículo por IA
    try:
        resultado_triagem = analisar_curriculo(candidato=db_candidato, vaga=db_vaga)
        score = resultado_triagem.get("score")
        feedback = {
            "pontos_fortes": resultado_triagem.get("pontos_fortes", []),
            "gaps": resultado_triagem.get("gaps", []),
            "feedback_texto": resultado_triagem.get("feedback_texto", ""),
        }

        # Verificar gate de aprovação contra o threshold da vaga
        if db_vaga.score_minimo_triagem is None:
            novo_status = StatusCandidatura.aprovada_triagem
        elif score is not None and score >= float(db_vaga.score_minimo_triagem):
            novo_status = StatusCandidatura.aprovada_triagem
        else:
            novo_status = StatusCandidatura.reprovada_triagem

        db_candidatura = update_candidatura_triagem(
            db,
            db_candidatura=db_candidatura,
            score_triagem=score,
            feedback_triagem=feedback,
            status=novo_status,
            data_triagem=datetime.now(timezone.utc),
        )

        if db_candidatura.status == StatusCandidatura.aprovada_triagem:
            inicializar_entrevista_automatica(db, candidatura_id=db_candidatura.id)
    except Exception as e:
        logger.warning(
            f"Falha ao executar triagem por IA na candidatura '{db_candidatura.id}': {e}"
        )
        feedback_erro = {
            "erro": f"falha na triagem automática, revisar manualmente: {str(e)}"
        }
        db_candidatura = update_candidatura_triagem(
            db,
            db_candidatura=db_candidatura,
            score_triagem=None,
            feedback_triagem=feedback_erro,
            status=StatusCandidatura.pendente_triagem,
            data_triagem=None,
        )

    return db_candidatura


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
    updated = update_candidatura_status(
        db, db_candidatura=db_candidatura, status_in=status_in
    )
    if updated.status == StatusCandidatura.aprovada_triagem:
        inicializar_entrevista_automatica(db, candidatura_id=updated.id)
    return updated
