import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.config import settings
from app.core.database import get_db
from app.core.audio import save_audio_file
from app.crud.entrevista import (
    get_pergunta,
    get_resposta_by_pergunta,
    create_resposta,
    create_pergunta,
)
from app.schemas.entrevista import RespostaCreate, RespostaResponse, PerguntaCreate

router = APIRouter(prefix="/audio", tags=["Áudio"])


@router.post(
    "/upload/{pergunta_id}",
    response_model=RespostaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_audio_resposta(
    pergunta_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """
    Recebe um arquivo de áudio para uma pergunta específica e o salva no servidor.
    Cria a entidade RespostaEntrevista com o URL do arquivo de áudio.
    """
    # 1. Validar se o arquivo é de áudio
    if not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado não é um formato de áudio válido.",
        )

    # 2. Validar se a pergunta existe
    db_pergunta = get_pergunta(db, pergunta_id=pergunta_id)
    if not db_pergunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pergunta não encontrada."
        )

    # 3. Validar se já existe resposta
    existing_resposta = get_resposta_by_pergunta(db, pergunta_id=pergunta_id)
    if existing_resposta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta pergunta já foi respondida.",
        )

    # 4. Salvar o arquivo no diretório (Volume Docker)
    audio_url = await save_audio_file(file, pergunta_id)

    # 5. Chamar o microserviço de IA (VoiceMatchServices :8001) para transcrição e avaliação
    transcricao = None
    metricas = None
    proxima_pergunta_texto = None

    try:
        # Pega o caminho físico no disco
        # audio_url é '/media/audio/nome.wav' -> caminho relativo no projeto
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
    except Exception as e:
        print(
            f"Aviso: Não foi possível chamar o microserviço de IA ({e}). Salving áudio sem transcrição inicial."
        )

    # 6. Criar o registro da resposta no banco com transcrição e métricas
    resposta_in = RespostaCreate(
        audio_url=audio_url, transcricao=transcricao, metricas=metricas
    )
    db_resposta = create_resposta(db, pergunta_id=pergunta_id, resposta_in=resposta_in)

    # 7. Se a IA gerou a próxima pergunta, cadastrar automaticamente na entrevista
    if proxima_pergunta_texto:
        try:
            nova_ordem = db_pergunta.ordem + 1
            create_pergunta(
                db,
                entrevista_id=db_pergunta.entrevista_id,
                pergunta_in=PerguntaCreate(
                    pergunta_texto=proxima_pergunta_texto, ordem=nova_ordem
                ),
            )
        except Exception as e:
            print(f"Aviso: Não foi possível criar próxima pergunta gerada ({e})")

    return db_resposta
