import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.relatorio import RelatorioGeralResponse, RelatorioVagaResponse
from app.crud.relatorio import obter_totais_gerais, obter_metricas_vaga

router = APIRouter(
    prefix="/relatorios",
    tags=["Relatorios e Metricas"]
)

@router.get("/geral", response_model=RelatorioGeralResponse)
def obter_relatorio_geral(db: Session = Depends(get_db)):
    """
    Retorna totais consolidados, nota média global, 
    distribuição por faixa de nota e volume por status.
    """
    return obter_totais_gerais(db=db)


@router.get("/vagas/{vaga_id}", response_model=RelatorioVagaResponse)
def obter_relatorio_vaga(vaga_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retorna métricas específicas da vaga selecionada, como notas médias
    nas etapas e o funil de conversão de candidatos.
    """
    return obter_metricas_vaga(db=db, vaga_id=vaga_id)
