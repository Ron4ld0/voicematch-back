import json
import logging
from datetime import UTC, datetime
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entrevista import Entrevista
from app.models.enums import StatusCandidatura, StatusEntrevista
from app.models.pergunta_entrevista import PerguntaEntrevista
from app.models.resposta_entrevista import RespostaEntrevista
from app.schemas.entrevista import (
    EntrevistaCreate,
    EntrevistaUpdate,
    PerguntaCreate,
    RespostaCreate,
)

PERGUNTA_INICIAL_PADRAO = (
    "Olá! Eu sou a Iris, a inteligência artificial do VoiceMatch AI, e vou conduzir a sua entrevista de voz. "
    "Para iniciarmos nossa primeira etapa (Apresentação Pessoal), por favor se apresente e compartilhe sobre sua trajetória profissional e motivações."
)


def get_entrevista(db: Session, entrevista_id: UUID) -> Entrevista | None:
    return db.query(Entrevista).filter(Entrevista.id == entrevista_id).first()


def get_entrevistas_by_candidatura(
    db: Session, candidatura_id: UUID
) -> list[Entrevista]:
    return (
        db.query(Entrevista).filter(Entrevista.candidatura_id == candidatura_id).all()
    )


def create_entrevista(db: Session, entrevista_in: EntrevistaCreate) -> Entrevista:
    db_entrevista = Entrevista(
        candidatura_id=entrevista_in.candidatura_id,
        status=entrevista_in.status,
        data_inicio=entrevista_in.data_inicio,
        data_fim=entrevista_in.data_fim,
        score_geral=entrevista_in.score_geral,
        feedback_candidato=entrevista_in.feedback_candidato,
        feedback_recrutador=entrevista_in.feedback_recrutador,
    )
    db.add(db_entrevista)
    db.commit()
    db.refresh(db_entrevista)
    return db_entrevista


def inicializar_entrevista_automatica(db: Session, candidatura_id: UUID) -> Entrevista:
    """
    Cria uma nova entrevista e adiciona automaticamente a pergunta inicial (Ordem 1)
    se ainda não existir entrevista para esta candidatura.
    """
    existentes = get_entrevistas_by_candidatura(db, candidatura_id=candidatura_id)
    if existentes:
        return existentes[0]

    entrevista_in = EntrevistaCreate(
        candidatura_id=candidatura_id,
        status="agendada",
        data_inicio=datetime.now(UTC),
    )
    db_entrevista = create_entrevista(db, entrevista_in=entrevista_in)

    pergunta_in = PerguntaCreate(
        pergunta_texto=PERGUNTA_INICIAL_PADRAO,
        ordem=1,
    )
    create_pergunta(db, entrevista_id=db_entrevista.id, pergunta_in=pergunta_in)

    return db_entrevista


def update_entrevista(
    db: Session, db_entrevista: Entrevista, entrevista_in: EntrevistaUpdate
) -> Entrevista:
    update_data = entrevista_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_entrevista, field, value)
    db.commit()
    db.refresh(db_entrevista)
    return db_entrevista


# Operações de Perguntas
def get_pergunta(db: Session, pergunta_id: UUID) -> PerguntaEntrevista | None:
    return (
        db.query(PerguntaEntrevista)
        .filter(PerguntaEntrevista.id == pergunta_id)
        .first()
    )


def get_pergunta_by_entrevista_and_ordem(
    db: Session, entrevista_id: UUID, ordem: int
) -> PerguntaEntrevista | None:
    return (
        db.query(PerguntaEntrevista)
        .filter(
            PerguntaEntrevista.entrevista_id == entrevista_id,
            PerguntaEntrevista.ordem == ordem,
        )
        .first()
    )


def create_pergunta(
    db: Session, entrevista_id: UUID, pergunta_in: PerguntaCreate
) -> PerguntaEntrevista:
    db_pergunta = PerguntaEntrevista(
        entrevista_id=entrevista_id,
        pergunta_texto=pergunta_in.pergunta_texto,
        ordem=pergunta_in.ordem,
    )
    db.add(db_pergunta)
    db.commit()
    db.refresh(db_pergunta)
    return db_pergunta


# Operações de Respostas
def get_resposta_by_pergunta(
    db: Session, pergunta_id: UUID
) -> RespostaEntrevista | None:
    return (
        db.query(RespostaEntrevista)
        .filter(RespostaEntrevista.pergunta_id == pergunta_id)
        .first()
    )


def create_resposta(
    db: Session, pergunta_id: UUID, resposta_in: RespostaCreate
) -> RespostaEntrevista:
    db_resposta = RespostaEntrevista(
        pergunta_id=pergunta_id,
        audio_url=resposta_in.audio_url,
        transcricao=resposta_in.transcricao,
        metricas=resposta_in.metricas,
    )
    db.add(db_resposta)
    db.commit()
    db.refresh(db_resposta)
    return db_resposta


def delete_entrevista(db: Session, entrevista_id: UUID) -> bool:
    db_entrevista = db.query(Entrevista).filter(Entrevista.id == entrevista_id).first()
    if not db_entrevista:
        return False
    db.delete(db_entrevista)
    db.commit()
    return True


def delete_pergunta(db: Session, pergunta_id: UUID) -> bool:
    db_pergunta = (
        db.query(PerguntaEntrevista)
        .filter(PerguntaEntrevista.id == pergunta_id)
        .first()
    )
    if not db_pergunta:
        return False
    db.delete(db_pergunta)
    db.commit()
    return True


logger = logging.getLogger(__name__)


async def processar_finalizacao_entrevista(
    db: Session, db_entrevista: Entrevista
) -> Entrevista:
    """
    Finaliza a entrevista de voz, consolida os scores e dispara a geração do Parecer Consolidado por IA.
    """
    db_entrevista.status = StatusEntrevista.concluida
    db_entrevista.data_fim = datetime.now()

    # Organizar histórico ordenado das perguntas e respostas transcritas com métricas
    perguntas_ordenadas = sorted(db_entrevista.perguntas, key=lambda p: p.ordem)
    conversation_history = [
        {
            "etapa": f"Etapa {p.ordem}",
            "pergunta": p.pergunta_texto,
            "resposta": p.resposta.transcricao if p.resposta else "",
            "metricas": p.resposta.metricas
            if p.resposta and p.resposta.metricas
            else {},
        }
        for p in perguntas_ordenadas
    ]

    # Obter dados complementares da vaga, candidato e triagem
    cand_nome = ""
    vaga_titulo = "Vaga"
    vaga_reqs = ""
    triagem_info = {}
    if db_entrevista.candidatura:
        if db_entrevista.candidatura.candidato:
            cand_nome = db_entrevista.candidatura.candidato.nome
        if db_entrevista.candidatura.vaga:
            v = db_entrevista.candidatura.vaga
            vaga_titulo = v.titulo
            vaga_reqs = f"Título: {v.titulo}\nDescrição: {v.descricao or ''}\nHard Skills: {v.requisitos_hard}\nSoft Skills: {v.requisitos_soft}"
        if db_entrevista.candidatura.feedback_triagem:
            triagem_info = (
                dict(db_entrevista.candidatura.feedback_triagem)
                if isinstance(db_entrevista.candidatura.feedback_triagem, dict)
                else {}
            )
        if db_entrevista.candidatura.score_triagem is not None:
            try:
                triagem_info["score_triagem"] = float(
                    db_entrevista.candidatura.score_triagem
                )
            except Exception:  # noqa: BLE001
                triagem_info["score_triagem"] = str(
                    db_entrevista.candidatura.score_triagem
                )

    # Chamar IA para gerar parecer final consolidado
    try:
        payload = {
            "question": vaga_reqs or vaga_titulo,
            "candidate_answer": json.dumps(
                {
                    "candidate_name": cand_nome,
                    "job_title": vaga_titulo,
                    "screening_evaluation": triagem_info,
                    "voice_interview_history": conversation_history,
                },
                ensure_ascii=False,
                default=str,
            ),
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
                if parecer_data.get("feedback_candidato"):
                    db_entrevista.feedback_candidato = parecer_data.get(
                        "feedback_candidato"
                    )
                if "score_geral" in parecer_data:
                    try:
                        db_entrevista.score_geral = round(
                            float(parecer_data["score_geral"]), 2
                        )
                    except (ValueError, TypeError):
                        pass
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Não foi possível gerar parecer final via IA: {e}")

    # Fallback/Cálculo da nota geral se não vier da IA (40% triagem + 60% respostas de áudio da entrevista)
    if db_entrevista.score_geral is None:
        score_triagem = float(
            (db_entrevista.candidatura and db_entrevista.candidatura.score_triagem)
            or 7.0
        )
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
    if db_entrevista.candidatura:
        db_entrevista.candidatura.status = StatusCandidatura.avaliada

    db.commit()
    db.refresh(db_entrevista)
    return db_entrevista
