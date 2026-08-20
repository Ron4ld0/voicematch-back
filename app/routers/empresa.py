import uuid

from argon2 import PasswordHasher
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_admin_user, get_current_tenant
from app.crud.empresa import (
    create_empresa, get_empresa, get_empresas, 
    update_empresa, get_empresa_by_cnpj
)
from app.crud.usuario import (
    get_usuarios_por_empresa, create_admin_empresa, get_usuario_by_email
)
from app.models.usuario import Usuario
from app.models.enums import StatusEmpresa
from app.schemas.empresa import EmpresaCreate, EmpresaResponse, EmpresaUpdate
from app.schemas.usuario import UsuarioResponse, UsuarioCreate

router = APIRouter(prefix="/empresas", tags=["Empresas (Multi-tenant)"])
ph = PasswordHasher()


@router.get("/", response_model=list[EmpresaResponse])
def listar_empresas(
    status_empresa: StatusEmpresa | None = Query(None, alias="status"),
    busca: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_admin_user),
):
    """
    Lista as empresas na plataforma. Acesso exclusivo para admin_sistema.
    """
    return get_empresas(db, skip=skip, limit=limit, status=status_empresa, busca=busca)


@router.post("/", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_empresa(
    empresa_in: EmpresaCreate,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_admin_user),
):
    """
    Cadastra uma nova empresa. Acesso exclusivo para admin_sistema.
    """
    if empresa_in.cnpj:
        if get_empresa_by_cnpj(db, empresa_in.cnpj):
            raise HTTPException(status_code=409, detail="Já existe empresa com esse CNPJ")
            
    return create_empresa(db, empresa_in)


@router.get("/me", response_model=EmpresaResponse)
def obter_minha_empresa(
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant),
):
    """
    Retorna os dados da empresa vinculada ao usuário logado.
    """
    empresa = get_empresa(db, tenant_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa


@router.get("/me/recrutadores", response_model=list[UsuarioResponse])
def listar_recrutadores_empresa(
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant),
):
    """
    Lista todos os recrutadores vinculados à empresa do usuário logado.
    """
    return get_usuarios_por_empresa(db, tenant_id)


@router.post("/me/convites", status_code=status.HTTP_201_CREATED)
def convidar_recrutador(
    email: str,
    nome_completo: str,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant),
):
    """
    Cria um usuário recrutador vinculado à empresa do tenant atual.
    """
    from app.crud.usuario import get_usuario_by_email
    from app.models.usuario import Usuario
    from app.models.recrutador import Recrutador
    from app.models.enums import TipoUsuario
    
    if get_usuario_by_email(db, email):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
        
    senha_temporaria = "Mudar@123"
    
    novo_usuario = Usuario(
        nome_completo=nome_completo,
        email=email,
        senha_hash=ph.hash(senha_temporaria),
        tipo_usuario=TipoUsuario.recrutador
    )
    db.add(novo_usuario)
    db.flush()
    
    novo_recrutador = Recrutador(
        id=novo_usuario.id,
        empresa_id=tenant_id
    )
    db.add(novo_recrutador)
    db.commit()
    
    return {"message": f"Usuário criado com sucesso. Senha temporária: {senha_temporaria}"}


@router.get("/{empresa_id}", response_model=EmpresaResponse)
def obter_empresa(
    empresa_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_admin_user),
):
    """
    Retorna os dados de uma empresa específica. Acesso exclusivo para admin_sistema.
    """
    empresa = get_empresa(db, empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa


@router.patch("/{empresa_id}", response_model=EmpresaResponse)
def alterar_empresa(
    empresa_id: uuid.UUID,
    empresa_in: EmpresaUpdate,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_admin_user),
):
    """
    Altera os dados de uma empresa específica. Acesso exclusivo para admin_sistema.
    """
    db_empresa = get_empresa(db, empresa_id)
    if not db_empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    # Validation if CNPJ is updated
    if empresa_in.cnpj and empresa_in.cnpj != db_empresa.cnpj:
        if get_empresa_by_cnpj(db, empresa_in.cnpj):
            raise HTTPException(status_code=409, detail="Já existe empresa com esse CNPJ")

    return update_empresa(db, db_empresa, empresa_in)


@router.get("/{empresa_id}/usuarios", response_model=list[UsuarioResponse])
def listar_usuarios_da_empresa(
    empresa_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_admin_user),
):
    """
    Lista todos os usuários vinculados a uma empresa específica.
    """
    empresa = get_empresa(db, empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    return get_usuarios_por_empresa(db, empresa_id)


@router.post("/{empresa_id}/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_admin_empresa(
    empresa_id: uuid.UUID,
    usuario_in: UsuarioCreate,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_admin_user),
):
    """
    Cria um admin_empresa para a empresa específica.
    """
    empresa = get_empresa(db, empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    if get_usuario_by_email(db, usuario_in.email):
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
        
    return create_admin_empresa(db, empresa_id, usuario_in)
