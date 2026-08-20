from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_admin_user
from app.crud.usuario import (
    get_admins_sistema, create_admin_sistema, get_usuario_by_email
)
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioResponse, UsuarioCreate
import uuid
from app.models.recrutador import Recrutador
from app.models.enums import TipoUsuario
from app.schemas.auth import TokenResponse
from app.core.security import create_access_token

router = APIRouter(prefix="/admin", tags=["Administradores"])


@router.get("/usuarios", response_model=list[UsuarioResponse])
def listar_admins_sistema(
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_admin_user),
):
    """
    Lista todos os administradores da plataforma. Acesso exclusivo para admin_sistema.
    """
    return get_admins_sistema(db)


@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_admin_sistema(
    usuario_in: UsuarioCreate,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_admin_user),
):
    """
    Cadastra um novo admin da plataforma. Acesso exclusivo para admin_sistema.
    """
    if get_usuario_by_email(db, usuario_in.email):
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
        
    return create_admin_sistema(db, usuario_in)


@router.post("/empresas/{empresa_id}/impersonar", response_model=TokenResponse)
def impersonar_empresa(
    empresa_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_admin_user),
):
    """
    Entra no sistema como o administrador da empresa cliente informada.
    Acesso exclusivo para admin_sistema.
    """
    admin_empresa = (
        db.query(Usuario)
        .join(Recrutador)
        .filter(
            Recrutador.empresa_id == empresa_id,
            Usuario.tipo_usuario == TipoUsuario.admin_empresa,
        )
        .first()
    )

    if not admin_empresa:
        raise HTTPException(
            status_code=400,
            detail="A empresa selecionada não possui administradores para personificar.",
        )

    access_token = create_access_token(data={"sub": admin_empresa.email})
    return {"access_token": access_token, "token_type": "bearer", "user": admin_empresa}
