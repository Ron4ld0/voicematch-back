import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.config import settings
from app.core.database import get_db
from app.core.audio import save_audio_file
from app.crud.candidato import get_candidato
from app.crud.entrevista import (
    get_pergunta,
    get_resposta_by_pergunta,
    create_resposta,
    create_pergunta,
    get_entrevistas_by_candidatura,
    inicializar_entrevista_automatica,
)
from app.schemas.entrevista import RespostaCreate, RespostaResponse, PerguntaCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audio", tags=["Áudio"])


@router.post(
    "/upload/{pergunta_id}",
    response_model=RespostaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_audio_resposta(
    pergunta_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """
    Recebe um arquivo de áudio para uma pergunta específica e o salva no servidor.
    Cria a entidade RespostaEntrevista com o URL do arquivo de áudio.
    """
    # Resolvendo o UUID da pergunta caso seja enviado como UUID ou string sintética
    target_pergunta_id = None
    try:
        target_pergunta_id = UUID(pergunta_id)
    except ValueError:
        parts = pergunta_id.rsplit("-", 5)
        possible_cand_id = "-".join(parts[-5:]) if len(parts) >= 5 else None
        if possible_cand_id:
            try:
                cand_uuid = UUID(possible_cand_id)
                db_candidato = get_candidato(db, candidato_id=cand_uuid)
                if db_candidato and db_candidato.candidaturas:
                    cand = db_candidato.candidaturas[0]
                    entrevistas = get_entrevistas_by_candidatura(
                        db, candidatura_id=cand.id
                    )
                    if not entrevistas:
                        entrevistas = [
                            inicializar_entrevista_automatica(
                                db, candidatura_id=cand.id
                            )
                        ]
                    if entrevistas and entrevistas[0].perguntas:
                        sem_resposta = [
                            p for p in entrevistas[0].perguntas if not p.resposta
                        ]
                        if sem_resposta:
                            target_pergunta_id = sem_resposta[0].id
                        else:
                            target_pergunta_id = entrevistas[0].perguntas[0].id
            except Exception as ex:  # noqa: BLE001
                logger.warning(f"Não foi possível resolver UUID de '{pergunta_id}': {ex}")

    if not target_pergunta_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID da pergunta inválido ou não fornecido em formato UUID.",
        )

    # 1. Validar se o arquivo é de áudio
    if not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado não é um formato de áudio válido.",
        )

    # 2. Validar se a pergunta existe
    db_pergunta = get_pergunta(db, pergunta_id=target_pergunta_id)
    if not db_pergunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pergunta não encontrada."
        )

    pergunta_id = target_pergunta_id

    # 3. Salvar o arquivo no diretório (Volume Docker)
    audio_url = await save_audio_file(file, pergunta_id)

    # 4. Chamar o microserviço de IA (VoiceMatchServices :8001) para transcrição e avaliação
    transcricao = None
    metricas = None
    proxima_pergunta_texto = None

    try:
        # Pega o caminho físico no disco
        audio_path_disk = audio_url.lstrip("/")

        payload_ai = {
            "audio_path": audio_path_disk,
            "context": {
                "job_requirements": db_pergunta.entrevista.candidatura.vaga.descricao
                or "Vaga técnica",
                "behavioral_profile": {
                    "proatividade": 8,
                    "resolucao_de_problemas": 8,
                    "trabalho_em_equipe": 8,
                },
                "candidate_resume": db_pergunta.entrevista.candidatura.candidato.curriculo_url
                or "",
                "conversation_history": [
                    {
                        "pergunta": p.pergunta_texto,
                        "resposta": p.resposta.transcricao if p.resposta else "",
                    }
                    for p in db_pergunta.entrevista.perguntas
                ],
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            res_ai = await client.post(
                f"{settings.AI_SERVICE_URL}/ai/evaluate-audio", json=payload_ai
            )
            if res_ai.status_code == 200:
                data_ai = res_ai.json()
                transcricao = data_ai.get("transcricao")
                metricas = data_ai.get("metricas")
                proxima_pergunta_texto = data_ai.get("proxima_pergunta")
    except Exception as e:  # noqa: BLE001
        print(f"Aviso: Não foi possível chamar o microserviço de IA ({e}).")

    # 5. Criar ou atualizar o registro da resposta no banco
    existing_resposta = get_resposta_by_pergunta(db, pergunta_id=target_pergunta_id)
    if existing_resposta:
        existing_resposta.audio_url = audio_url
        if transcricao:
            existing_resposta.transcricao = transcricao
        if metricas:
            existing_resposta.metricas = metricas
        db.commit()
        db.refresh(existing_resposta)
        db_resposta = existing_resposta
    else:
        resposta_in = RespostaCreate(
            audio_url=audio_url, transcricao=transcricao, metricas=metricas
        )
        db_resposta = create_resposta(
            db, pergunta_id=pergunta_id, resposta_in=resposta_in
        )

    # 6. Regra de Negócio: Ciclo Fixo de 3 Perguntas
    # Ordem 1: Pessoal -> Próxima é Ordem 2 (Fit Cultural)
    # Ordem 2: Fit Cultural -> Próxima é Ordem 3 (Técnica)
    # Ordem 3: Técnica -> Finalização imediata da sessão de entrevista e disparo do Parecer Consolidado por IA
    if db_pergunta.ordem < 3 and proxima_pergunta_texto:
        nova_ordem = db_pergunta.ordem + 1
        ja_existe_prox = any(
            p.ordem == nova_ordem for p in db_pergunta.entrevista.perguntas
        )
        if not ja_existe_prox:
            try:
                create_pergunta(
                    db,
                    entrevista_id=db_pergunta.entrevista_id,
                    pergunta_in=PerguntaCreate(
                        pergunta_texto=proxima_pergunta_texto, ordem=nova_ordem
                    ),
                )
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Não foi possível criar próxima pergunta gerada ({e})")
    elif db_pergunta.ordem >= 3:
        # Finalização automática após a terceira resposta
        try:
            from app.crud.entrevista import processar_finalizacao_entrevista

            await processar_finalizacao_entrevista(db, db_pergunta.entrevista)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Erro ao disparar finalização automática da entrevista na 3ª resposta: {e}")

    return db_resposta
