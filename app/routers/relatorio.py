import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.crud.relatorio import obter_metricas_vaga, obter_totais_gerais
from app.schemas.relatorio import RelatorioGeralResponse, RelatorioVagaResponse

router = APIRouter(prefix="/relatorios", tags=["Relatorios e Metricas"])


@router.get("/geral", response_model=RelatorioGeralResponse)
def obter_relatorio_geral(
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """
    Retorna totais consolidados, nota média global,
    distribuição por faixa de nota e volume por status para a empresa do usuário.
    """
    return obter_totais_gerais(db=db, empresa_id=tenant_id)


@router.get("/vagas/{vaga_id}", response_model=RelatorioVagaResponse)
def obter_relatorio_vaga(
    vaga_id: uuid.UUID, 
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """
    Retorna métricas específicas da vaga selecionada, como notas médias
    nas etapas e o funil de conversão de candidatos da empresa logada.
    """
    return obter_metricas_vaga(db=db, vaga_id=vaga_id, empresa_id=tenant_id)
