from datetime import datetime, timezone
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from app.models.entrevista import Entrevista
from app.models.pergunta_entrevista import PerguntaEntrevista
from app.models.resposta_entrevista import RespostaEntrevista
from app.schemas.entrevista import (
    EntrevistaCreate,
    EntrevistaUpdate,
    PerguntaCreate,
    RespostaCreate,
)

PERGUNTA_INICIAL_PADRAO = (
    "Olá! Seja bem-vindo(a) à entrevista do VoiceMatch. "
    "Para começarmos, por favor se apresente e conte sobre sua trajetória profissional e principais experiências."
)


def get_entrevista(db: Session, entrevista_id: UUID) -> Optional[Entrevista]:
    return db.query(Entrevista).filter(Entrevista.id == entrevista_id).first()


def get_entrevistas_by_candidatura(
    db: Session, candidatura_id: UUID
) -> List[Entrevista]:
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


def inicializar_entrevista_automatica(
    db: Session, candidatura_id: UUID
) -> Entrevista:
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
        data_inicio=datetime.now(timezone.utc),
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
def get_pergunta(db: Session, pergunta_id: UUID) -> Optional[PerguntaEntrevista]:
    return (
        db.query(PerguntaEntrevista)
        .filter(PerguntaEntrevista.id == pergunta_id)
        .first()
    )


def get_pergunta_by_entrevista_and_ordem(
    db: Session, entrevista_id: UUID, ordem: int
) -> Optional[PerguntaEntrevista]:
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
) -> Optional[RespostaEntrevista]:
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
