import os
import uuid

import aiofiles
from fastapi import UploadFile

from app.core.config import settings


def ensure_audio_dir_exists():
    """Garante que o diretório de áudios exista."""
    os.makedirs(settings.AUDIO_UPLOAD_DIR, exist_ok=True)


async def save_audio_file(file: UploadFile, pergunta_id: uuid.UUID) -> str:
    """
    Salva um arquivo de áudio localmente e retorna o caminho relativo
    que será armazenado no banco de dados.
    """
    ensure_audio_dir_exists()

    # Extrair extensão do arquivo original ou usar .wav como fallback
    ext = os.path.splitext(file.filename)[1]
    if not ext:
        ext = ".wav"

    # Gerar um nome único baseado na pergunta_id e uuid
    unique_filename = f"{pergunta_id}_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.AUDIO_UPLOAD_DIR, unique_filename)

    # Salvar o arquivo de forma assíncrona
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    # Retornar o caminho relativo que a API vai usar para servir o arquivo
    # Ex: /media/audio/nome_do_arquivo.wav
    relative_path = f"/media/audio/{unique_filename}"
    return relative_path
