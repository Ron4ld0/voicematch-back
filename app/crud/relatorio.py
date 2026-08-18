import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.vaga import Vaga
from app.models.candidatura import Candidatura
from app.models.entrevista import Entrevista
from app.models.enums import StatusEntrevista


def obter_totais_gerais(db: Session):
    total_vagas = db.query(func.count(Vaga.id)).scalar() or 0
    total_candidaturas = db.query(func.count(Candidatura.id)).scalar() or 0

    nota_media_global = (
        db.query(func.avg(Entrevista.score_geral))
        .join(Candidatura, Candidatura.id == Entrevista.candidatura_id)
        .filter(Entrevista.status == StatusEntrevista.concluida)
        .filter(Entrevista.score_geral.isnot(None))
        .scalar()
        or 0.0
    )

    status_query = (
        db.query(Candidatura.status, func.count(Candidatura.id))
        .group_by(Candidatura.status)
        .all()
    )
    volume_por_status = [
        {
            "status": row[0].name if hasattr(row[0], "name") else str(row[0]),
            "quantidade": row[1],
        }
        for row in status_query
    ]

    faixas_query = (
        db.query(
            func.count(case((Candidatura.score_triagem <= 20, 1))).label("0-20"),
            func.count(case((Candidatura.score_triagem.between(21, 40), 1))).label(
                "21-40"
            ),
            func.count(case((Candidatura.score_triagem.between(41, 60), 1))).label(
                "41-60"
            ),
            func.count(case((Candidatura.score_triagem.between(61, 80), 1))).label(
                "61-80"
            ),
            func.count(case((Candidatura.score_triagem >= 81, 1))).label("81-100"),
        )
        .filter(Candidatura.score_triagem.isnot(None))
        .first()
    )

    if faixas_query:
        distribuicao_por_faixa = [
            {"faixa": "0-20", "quantidade": faixas_query[0] or 0},
            {"faixa": "21-40", "quantidade": faixas_query[1] or 0},
            {"faixa": "41-60", "quantidade": faixas_query[2] or 0},
            {"faixa": "61-80", "quantidade": faixas_query[3] or 0},
            {"faixa": "81-100", "quantidade": faixas_query[4] or 0},
        ]
    else:
        distribuicao_por_faixa = [
            {"faixa": "0-20", "quantidade": 0},
            {"faixa": "21-40", "quantidade": 0},
            {"faixa": "41-60", "quantidade": 0},
            {"faixa": "61-80", "quantidade": 0},
            {"faixa": "81-100", "quantidade": 0},
        ]

    return {
        "total_vagas": total_vagas,
        "total_candidaturas": total_candidaturas,
        "nota_media_global": round(nota_media_global, 2),
        "distribuicao_por_faixa": distribuicao_por_faixa,
        "volume_por_status": volume_por_status,
    }


def obter_metricas_vaga(db: Session, vaga_id: uuid.UUID):
    nota_media_triagem = (
        db.query(func.avg(Candidatura.score_triagem))
        .filter(Candidatura.vaga_id == vaga_id)
        .filter(Candidatura.score_triagem.isnot(None))
        .scalar()
        or 0.0
    )

    nota_media_entrevista_voz = (
        db.query(func.avg(Entrevista.score_geral))
        .join(Candidatura, Candidatura.id == Entrevista.candidatura_id)
        .filter(Candidatura.vaga_id == vaga_id)
        .filter(Entrevista.status == StatusEntrevista.concluida)
        .filter(Entrevista.score_geral.isnot(None))
        .scalar()
        or 0.0
    )

    funil_query = (
        db.query(Candidatura.status, func.count(Candidatura.id))
        .filter(Candidatura.vaga_id == vaga_id)
        .group_by(Candidatura.status)
        .all()
    )
    funil_conversao = [
        {
            "status": row[0].name if hasattr(row[0], "name") else str(row[0]),
            "quantidade": row[1],
        }
        for row in funil_query
    ]

    return {
        "vaga_id": vaga_id,
        "nota_media_triagem": round(nota_media_triagem, 2),
        "nota_media_entrevista_voz": round(nota_media_entrevista_voz, 2),
        "funil_conversao": funil_conversao,
    }
