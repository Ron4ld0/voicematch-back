from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.core.database import get_db
from app.schemas.entrevista import (
    EntrevistaCreate,
    EntrevistaUpdate,
    EntrevistaResponse,
    PerguntaCreate,
    PerguntaResponse,
    RespostaCreate,
    RespostaResponse,
)
from app.crud.entrevista import (
    create_entrevista,
    get_entrevista,
    get_entrevistas_by_candidatura,
    inicializar_entrevista_automatica,
    update_entrevista,
    delete_entrevista,
    create_pergunta,
    get_pergunta,
    get_pergunta_by_entrevista_and_ordem,
    delete_pergunta,
    create_resposta,
    get_resposta_by_pergunta,
)
from app.models.enums import StatusCandidatura, StatusEntrevista
from app.crud.candidatura import get_candidatura

router = APIRouter(tags=["Entrevistas"])

# ── Rotas de Entrevista ──────────────────────────────────────────────────────


@router.post(
    "/entrevistas",
    response_model=EntrevistaResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_entrevista(entrevista_in: EntrevistaCreate, db: Session = Depends(get_db)):
    """Cria uma nova entrevista vinculada a uma candidatura."""
    db_candidatura = get_candidatura(db, candidatura_id=entrevista_in.candidatura_id)
    if not db_candidatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A candidatura especificada não existe.",
        )
    if db_candidatura.status != StatusCandidatura.aprovada_triagem:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A entrevista só pode ser criada se a candidatura estiver com status 'aprovada_triagem'.",
        )
    return create_entrevista(db, entrevista_in=entrevista_in)


@router.get(
    "/candidaturas/{candidatura_id}/entrevistas",
    response_model=List[EntrevistaResponse],
)
def list_entrevistas_by_candidatura(
    candidatura_id: UUID, db: Session = Depends(get_db)
):
    entrevistas = get_entrevistas_by_candidatura(db, candidatura_id=candidatura_id)
    if not entrevistas:
        entrevista_nova = inicializar_entrevista_automatica(db, candidatura_id=candidatura_id)
        entrevistas = [entrevista_nova]
    return entrevistas


import json
import httpx
from app.core.config import settings


@router.post("/entrevistas/{id}/finalizar", response_model=EntrevistaResponse)
async def finalizar_entrevista_endpoint(id: UUID, db: Session = Depends(get_db)):
    """
    Finaliza a entrevista, consolida o score geral (triagem + entrevista de voz) e gera o parecer final da IA.
    """
    db_entrevista = get_entrevista(db, entrevista_id=id)
    if not db_entrevista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entrevista não encontrada."
        )

    db_entrevista.status = StatusEntrevista.concluida
    db_entrevista.data_fim = datetime.now()

    # Chamar IA para gerar parecer final consolidado
    try:
        conversation_history = [
            {
                "pergunta": p.pergunta_texto,
                "resposta": p.resposta.transcricao if p.resposta else "",
            }
            for p in db_entrevista.perguntas
        ]
        payload = {
            "question": db_entrevista.candidatura.vaga.titulo,
            "candidate_answer": json.dumps(conversation_history, ensure_ascii=False),
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res_eval = await client.post(
                f"{settings.AI_SERVICE_URL}/ai/final-evaluation", json=payload
            )
            if res_eval.status_code == 200:
                parecer_data = res_eval.json()
                db_entrevista.feedback_recrutador = json.dumps(
                    parecer_data, ensure_ascii=False
                )
    except Exception as e:
        logger.warning(f"Não foi possível gerar parecer final via IA: {e}")

    # Cálculo da nota geral (40% triagem + 60% respostas de áudio da entrevista)
    score_triagem = float(db_entrevista.candidatura.score_triagem or 7.0)
    scores_respostas = []
    for p in db_entrevista.perguntas:
        if p.resposta and p.resposta.metricas:
            m = p.resposta.metricas
            if isinstance(m, dict):
                p_val = float(m.get("proatividade", 7))
                res_val = float(m.get("resolucao_de_problemas", 7))
                trab_val = float(m.get("trabalho_em_equipe", 7))
                scores_respostas.append((p_val + res_val + trab_val) / 3.0)

    score_entrevista = (
        sum(scores_respostas) / len(scores_respostas) if scores_respostas else 7.5
    )
    score_geral = round((score_triagem * 0.4) + (score_entrevista * 0.6), 2)
    db_entrevista.score_geral = score_geral

    # Atualizar candidatura para avaliada
    db_entrevista.candidatura.status = StatusCandidatura.avaliada
    db.commit()
    db.refresh(db_entrevista)
    return db_entrevista


@router.get("/entrevistas/{id}", response_model=EntrevistaResponse)
def read_entrevista(id: UUID, db: Session = Depends(get_db)):
    """Retorna os dados completos de uma entrevista, incluindo perguntas e respostas."""
    db_entrevista = get_entrevista(db, entrevista_id=id)
    if not db_entrevista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entrevista não encontrada."
        )
    return db_entrevista


@router.put("/entrevistas/{id}", response_model=EntrevistaResponse)
def modify_entrevista(
    id: UUID, entrevista_in: EntrevistaUpdate, db: Session = Depends(get_db)
):
    """Atualiza os dados de uma entrevista (status, score, feedbacks, datas)."""
    db_entrevista = get_entrevista(db, entrevista_id=id)
    if not db_entrevista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entrevista não encontrada."
        )
    return update_entrevista(
        db, db_entrevista=db_entrevista, entrevista_in=entrevista_in
    )


@router.delete("/entrevistas/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_entrevista(id: UUID, db: Session = Depends(get_db)):
    """Remove uma entrevista e todas as suas perguntas e respostas (cascade)."""
    success = delete_entrevista(db, entrevista_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrevista não encontrada para deleção.",
        )
    return None


# ── Rotas de Perguntas ───────────────────────────────────────────────────────


@router.post(
    "/entrevistas/{id}/perguntas",
    response_model=PerguntaResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_pergunta_to_entrevista(
    id: UUID, pergunta_in: PerguntaCreate, db: Session = Depends(get_db)
):
    """Adiciona uma pergunta a uma entrevista. A ordem deve ser única por entrevista."""
    db_entrevista = get_entrevista(db, entrevista_id=id)
    if not db_entrevista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entrevista não encontrada."
        )

    # Validar se já existe pergunta nessa mesma ordem para esta entrevista
    existing_pergunta = get_pergunta_by_entrevista_and_ordem(
        db, entrevista_id=id, ordem=pergunta_in.ordem
    )
    if existing_pergunta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma pergunta cadastrada na posição (ordem) {pergunta_in.ordem} para esta entrevista.",
        )

    return create_pergunta(db, entrevista_id=id, pergunta_in=pergunta_in)


@router.get("/entrevistas/{id}/perguntas", response_model=List[PerguntaResponse])
def list_perguntas_by_entrevista(id: UUID, db: Session = Depends(get_db)):
    """Lista todas as perguntas de uma entrevista ordenadas por posição."""
    db_entrevista = get_entrevista(db, entrevista_id=id)
    if not db_entrevista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entrevista não encontrada."
        )
    return sorted(db_entrevista.perguntas, key=lambda p: p.ordem)


@router.delete("/perguntas/{pergunta_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_pergunta(pergunta_id: UUID, db: Session = Depends(get_db)):
    """Remove uma pergunta e sua resposta associada (cascade)."""
    success = delete_pergunta(db, pergunta_id=pergunta_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pergunta não encontrada para deleção.",
        )
    return None


# ── Rotas de Respostas ───────────────────────────────────────────────────────


@router.post(
    "/perguntas/{pergunta_id}/resposta",
    response_model=RespostaResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_resposta(
    pergunta_id: UUID, resposta_in: RespostaCreate, db: Session = Depends(get_db)
):
    """Submete uma resposta (áudio/transcrição/métricas) para uma pergunta. Cada pergunta aceita apenas uma resposta."""
    # Validar se a pergunta existe
    db_pergunta = get_pergunta(db, pergunta_id=pergunta_id)
    if not db_pergunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A pergunta especificada não existe.",
        )

    # Validar se a pergunta já possui uma resposta (relacionamento 1:1)
    existing_resposta = get_resposta_by_pergunta(db, pergunta_id=pergunta_id)
    if existing_resposta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta pergunta já foi respondida anteriormente.",
        )

    return create_resposta(db, pergunta_id=pergunta_id, resposta_in=resposta_in)
