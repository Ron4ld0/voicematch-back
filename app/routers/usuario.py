from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.core.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.crud.usuario import (
    get_usuario,
    get_usuario_by_email,
    get_usuarios,
    create_usuario,
    update_usuario,
    delete_usuario,
)

router = APIRouter(prefix="/usuarios", tags=["Usuários (Recrutadores)"])


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register_usuario(usuario_in: UsuarioCreate, db: Session = Depends(get_db)):
    """Cria um novo usuário (sempre será do tipo recrutador)."""
    db_usuario = get_usuario_by_email(db, email=usuario_in.email)
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este endereço de email já está cadastrado na base principal.",
        )
    return create_usuario(db, usuario_in=usuario_in)


@router.get("", response_model=List[UsuarioResponse])
def list_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os usuários (recrutadores)."""
    return get_usuarios(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=UsuarioResponse)
def read_usuario(id: UUID, db: Session = Depends(get_db)):
    """Retorna os dados de um usuário pelo ID."""
    db_usuario = get_usuario(db, usuario_id=id)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )
    return db_usuario


@router.put("/{id}", response_model=UsuarioResponse)
def modify_usuario(id: UUID, usuario_in: UsuarioUpdate, db: Session = Depends(get_db)):
    """Atualiza os dados de um usuário."""
    db_usuario = get_usuario(db, usuario_id=id)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )

    if usuario_in.email and usuario_in.email != db_usuario.email:
        existing = get_usuario_by_email(db, email=usuario_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este endereço de email já está em uso.",
            )
    return update_usuario(db, db_usuario=db_usuario, usuario_in=usuario_in)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_usuario(id: UUID, db: Session = Depends(get_db)):
    """Remove um usuário e seu perfil de recrutador (cascade)."""
    success = delete_usuario(db, usuario_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado para deleção.",
        )
    return None
