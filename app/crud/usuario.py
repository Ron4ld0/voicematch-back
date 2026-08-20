from uuid import UUID

from argon2 import PasswordHasher
from sqlalchemy.orm import Session

from app.models.enums import TipoUsuario
from app.models.recrutador import Recrutador
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

ph = PasswordHasher()


def get_usuario(db: Session, usuario_id: UUID) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def get_usuario_by_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def get_usuarios(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()


def get_usuarios_por_empresa(db: Session, empresa_id: UUID) -> list[Usuario]:
    return db.query(Usuario).join(Recrutador).filter(Recrutador.empresa_id == empresa_id).all()


def get_admins_sistema(db: Session) -> list[Usuario]:
    return db.query(Usuario).filter(Usuario.tipo_usuario == TipoUsuario.admin_sistema).all()


def create_admin_sistema(db: Session, usuario_in: UsuarioCreate) -> Usuario:
    senha_hash = ph.hash(usuario_in.senha)
    db_usuario = Usuario(
        nome_completo=usuario_in.nome_completo,
        email=usuario_in.email,
        senha_hash=senha_hash,
        telefone=usuario_in.telefone,
        tipo_usuario=TipoUsuario.admin_sistema,
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def create_admin_empresa(db: Session, empresa_id: UUID, usuario_in: UsuarioCreate) -> Usuario:
    senha_hash = ph.hash(usuario_in.senha)
    db_usuario = Usuario(
        nome_completo=usuario_in.nome_completo,
        email=usuario_in.email,
        senha_hash=senha_hash,
        telefone=usuario_in.telefone,
        tipo_usuario=TipoUsuario.admin_empresa,
    )
    db.add(db_usuario)
    db.flush()

    db_recrutador = Recrutador(
        id=db_usuario.id, empresa_id=empresa_id, cargo="Administrador"
    )
    db.add(db_recrutador)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def create_usuario(db: Session, usuario_in: UsuarioCreate) -> Usuario:
    senha_hash = ph.hash(usuario_in.senha)

    db_usuario = Usuario(
        nome_completo=usuario_in.nome_completo,
        email=usuario_in.email,
        senha_hash=senha_hash,
        telefone=usuario_in.telefone,
        tipo_usuario=TipoUsuario.recrutador,
    )
    db.add(db_usuario)
    db.flush()

    # Criar perfil de recrutador na mesma transação
    from app.models.empresa import Empresa
    empresa_padrao = db.query(Empresa).filter(Empresa.nome == "Empresa Padrão").first()
    
    cargo = None
    if usuario_in.recrutador:
        cargo = usuario_in.recrutador.cargo

    db_recrutador = Recrutador(
        id=db_usuario.id, empresa_id=empresa_padrao.id if empresa_padrao else None, cargo=cargo
    )
    db.add(db_recrutador)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def update_usuario(
    db: Session, db_usuario: Usuario, usuario_in: UsuarioUpdate
) -> Usuario:
    update_data = usuario_in.model_dump(
        exclude_unset=True, exclude={"senha", "recrutador"}
    )
    for field, value in update_data.items():
        setattr(db_usuario, field, value)

    if usuario_in.senha:
        db_usuario.senha_hash = ph.hash(usuario_in.senha)

    if usuario_in.recrutador and db_usuario.recrutador:
        perfil_data = usuario_in.recrutador.model_dump(exclude_unset=True)
        for field, value in perfil_data.items():
            setattr(db_usuario.recrutador, field, value)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def delete_usuario(db: Session, usuario_id: UUID) -> bool:
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        return False
    db.delete(db_usuario)
    db.commit()
    return True
