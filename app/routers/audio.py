from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.core.audio import save_audio_file
from app.crud.entrevista import get_pergunta, get_resposta_by_pergunta, create_resposta
from app.schemas.entrevista import RespostaCreate, RespostaResponse

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

    # 5. Criar o registro da resposta no banco
    # Neste momento a transcrição e métricas podem estar nulas.
    # O motor de IA (serviço) vai preencher isso assincronamente depois (Fase 2).
    resposta_in = RespostaCreate(audio_url=audio_url, transcricao=None, metricas=None)

    db_resposta = create_resposta(db, pergunta_id=pergunta_id, resposta_in=resposta_in)
    return db_resposta
