import logging

from sqlalchemy.orm import Session

from app.crud.usuario import create_usuario, get_usuario_by_email
from app.schemas.usuario import RecrutadorCreate, UsuarioCreate

logger = logging.getLogger(__name__)


def seed_admin_user(db: Session):
    admin_email = "admin@voicematch.ai"
    try:
        user = get_usuario_by_email(db, email=admin_email)
        if not user:
            admin_in = UsuarioCreate(
                nome_completo="Admin VoiceMatch",
                email=admin_email,
                senha="admin123",
            )
            from app.crud.usuario import create_admin_sistema
            create_admin_sistema(db, usuario_in=admin_in)
            logger.info("Usuário admin@voicematch.ai/admin123 populado com sucesso.")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Aviso ao verificar/popular admin inicial: {e}")
