import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.crud.candidato import get_candidato
from app.crud.candidatura import (
    create_candidatura,
    get_candidatura,
    get_candidatura_by_vaga_and_candidato,
    get_candidaturas_by_candidato,
    get_candidaturas_by_empresa,
    get_candidaturas_by_vaga,
    update_candidatura_status,
    update_candidatura_triagem,
)
from app.crud.entrevista import inicializar_entrevista_automatica
from app.crud.vaga import get_vaga
from app.models.enums import StatusCandidatura
from app.schemas.candidatura import (
    CandidaturaCreate,
    CandidaturaResponse,
    CandidaturaStatusUpdate,
)
from app.services.triagem_service import analisar_curriculo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/candidaturas", tags=["Candidaturas"])


@router.get("", response_model=list[CandidaturaResponse])
def list_candidaturas(
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """Lista todas as candidaturas registradas no tenant atual."""
    return get_candidaturas_by_empresa(db, empresa_id=tenant_id)


@router.post(
    "", response_model=CandidaturaResponse, status_code=status.HTTP_201_CREATED
)
def apply_to_vaga(candidatura_in: CandidaturaCreate, db: Session = Depends(get_db)):
    """Cria uma nova candidatura vinculando um candidato a uma vaga e executa a triagem automática por IA.
    Este endpoint não exige autenticação de recrutador, usa a empresa da vaga."""
    # Como não temos auth de candidato, precisamos bypassar tenant check pegando a empresa da vaga globalmente.
    from app.models.vaga import Vaga

    db_vaga = db.query(Vaga).filter(Vaga.id == candidatura_in.vaga_id).first()

    if not db_vaga:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A vaga especificada não existe.",
        )

    db_candidato = get_candidato(db, candidato_id=candidatura_in.candidato_id)
    if not db_candidato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O candidato especificado não existe.",
        )

    existing_candidatura = get_candidatura_by_vaga_and_candidato(
        db, vaga_id=candidatura_in.vaga_id, candidato_id=candidatura_in.candidato_id
    )
    if existing_candidatura:
        db_candidatura = existing_candidatura
    else:
        db_candidatura = create_candidatura(
            db, candidatura_in=candidatura_in, empresa_id=db_vaga.empresa_id
        )

    try:
        resultado_triagem = analisar_curriculo(candidato=db_candidato, vaga=db_vaga)
        score = resultado_triagem.get("score")
        feedback = {
            "pontos_fortes": resultado_triagem.get("pontos_fortes", []),
            "gaps": resultado_triagem.get("gaps", []),
            "feedback_texto": resultado_triagem.get("feedback_texto", ""),
        }

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
            data_triagem=datetime.now(UTC),
        )

        if db_candidatura.status == StatusCandidatura.aprovada_triagem:
            inicializar_entrevista_automatica(db, candidatura_id=db_candidatura.id)
    except Exception as e:
        logger.warning(
            f"Falha ao executar triagem por IA na candidatura '{db_candidatura.id}': {e}"
        )
        feedback_erro = {
            "erro": f"falha na triagem automática, revisar manualmente: {e!s}"
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
def read_candidatura(
    id: UUID,
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """Retorna os dados de uma candidatura pelo ID."""
    db_candidatura = get_candidatura(db, candidatura_id=id, empresa_id=tenant_id)
    if not db_candidatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidatura não encontrada."
        )
    return db_candidatura


@router.get("/vaga/{vaga_id}", response_model=list[CandidaturaResponse])
def read_candidaturas_by_vaga(
    vaga_id: UUID,
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """Lista todas as candidaturas de uma vaga específica."""
    db_vaga = get_vaga(db, vaga_id=vaga_id, empresa_id=tenant_id)
    if not db_vaga:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A vaga especificada não existe.",
        )
    return get_candidaturas_by_vaga(db, vaga_id=vaga_id, empresa_id=tenant_id)


@router.get("/candidato/{candidato_id}", response_model=list[CandidaturaResponse])
def read_candidaturas_by_candidato(
    candidato_id: UUID,
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """Lista todas as candidaturas de um candidato específico no contexto da empresa logada."""
    db_candidato = get_candidato(db, candidato_id=candidato_id)
    if not db_candidato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidato não encontrado."
        )
    return get_candidaturas_by_candidato(
        db, candidato_id=candidato_id, empresa_id=tenant_id
    )


@router.patch("/{id}/status", response_model=CandidaturaResponse)
def modify_candidatura_status(
    id: UUID,
    status_in: CandidaturaStatusUpdate,
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """Atualiza o status de uma candidatura (ex: pendente → aprovado)."""
    db_candidatura = get_candidatura(db, candidatura_id=id, empresa_id=tenant_id)
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
