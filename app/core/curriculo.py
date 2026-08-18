import os
import uuid

import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

EXTENSOES_PERMITIDAS = {".pdf", ".docx"}


def ensure_curriculo_dir_exists():
    """Garante que o diretório de currículos exista."""
    os.makedirs(settings.CURRICULO_UPLOAD_DIR, exist_ok=True)


async def save_curriculo_file(file: UploadFile, candidato_id: uuid.UUID) -> str:
    """
    Salva um arquivo de currículo (.pdf ou .docx) localmente e retorna o caminho relativo
    armazenado no banco de dados.
    """
    ensure_curriculo_dir_exists()

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in EXTENSOES_PERMITIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de arquivo '{ext}' não suportado. Apenas arquivos .pdf e .docx são aceitos.",
        )

    unique_filename = f"{candidato_id}_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.CURRICULO_UPLOAD_DIR, unique_filename)

    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    relative_path = f"/media/curriculos/{unique_filename}"
    return relative_path
