from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.crud.usuario import get_usuario_by_email
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.usuario import UsuarioResponse
from app.models.usuario import Usuario
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

router = APIRouter(prefix="/auth", tags=["Autenticação"])
ph = PasswordHasher()


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Autentica um usuário usando email (username) e senha, e retorna o token JWT
    e os dados do usuário. Suporta o padrão OAuth2 (Swagger) via formulário.
    """
    user = get_usuario_by_email(db, email=login_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        ph.verify(user.senha_hash, login_data.password)
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.post("/login/json", response_model=TokenResponse)
def login_json(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica um usuário usando payload JSON.
    """
    user = get_usuario_by_email(db, email=login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    try:
        ph.verify(user.senha_hash, login_data.senha)
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=UsuarioResponse)
def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna os dados do usuário atualmente autenticado.
    """
    return current_user
