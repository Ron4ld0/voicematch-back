import uuid
from pydantic import BaseModel
from typing import List


class DistribuicaoFaixaNota(BaseModel):
    faixa: str
    quantidade: int


class MetricaStatus(BaseModel):
    status: str
    quantidade: int


class RelatorioGeralResponse(BaseModel):
    total_vagas: int
    total_candidaturas: int
    nota_media_global: float
    distribuicao_por_faixa: List[DistribuicaoFaixaNota]
    volume_por_status: List[MetricaStatus]


class RelatorioVagaResponse(BaseModel):
    vaga_id: uuid.UUID
    nota_media_triagem: float
    nota_media_entrevista_voz: float
    funil_conversao: List[MetricaStatus]
