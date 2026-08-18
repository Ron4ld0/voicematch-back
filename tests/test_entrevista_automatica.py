from uuid import uuid4
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.models.enums import StatusCandidatura
from app.crud.entrevista import inicializar_entrevista_automatica
from app.core.database import get_db
from app.main import app


def test_inicializar_entrevista_automatica_unit():
    candidatura_id = uuid4()
    mock_db = MagicMock()

    # Nenhuma entrevista existente para esta candidatura
    mock_db.query().filter().all.return_value = []

    def fake_refresh(obj):
        if not getattr(obj, "id", None):
            obj.id = uuid4()

    mock_db.refresh.side_effect = fake_refresh

    entrevista = inicializar_entrevista_automatica(
        mock_db, candidatura_id=candidatura_id
    )

    assert entrevista is not None
    assert mock_db.add.call_count == 2  # Entrevista + Pergunta 1
    assert mock_db.commit.call_count == 2


@patch("app.routers.candidatura.analisar_curriculo")
def test_apply_to_vaga_auto_creates_entrevista_when_approved(mock_analisar):
    mock_analisar.return_value = {
        "score": 9.5,
        "pontos_fortes": ["Python", "FastAPI"],
        "gaps": [],
        "feedback_texto": "Excelente alinhamento",
    }

    vaga_id = uuid4()
    candidato_id = uuid4()

    mock_vaga = MagicMock()
    mock_vaga.id = vaga_id
    mock_vaga.score_minimo_triagem = 7.0

    mock_candidato = MagicMock()
    mock_candidato.id = candidato_id

    mock_db = MagicMock()
    mock_db.query().filter().first.side_effect = [mock_vaga, mock_candidato, None, None]

    created_candidatura = MagicMock()
    created_candidatura.id = uuid4()
    created_candidatura.vaga_id = vaga_id
    created_candidatura.candidato_id = candidato_id
    created_candidatura.status = StatusCandidatura.aprovada_triagem

    app.dependency_overrides[get_db] = lambda: mock_db

    with patch(
        "app.routers.candidatura.create_candidatura", return_value=created_candidatura
    ), patch(
        "app.routers.candidatura.inicializar_entrevista_automatica"
    ) as mock_init_entrevista:
        client = TestClient(app)
        response = client.post(
            "/candidaturas",
            json={
                "vaga_id": str(vaga_id),
                "candidato_id": str(candidato_id),
            },
        )
        assert response.status_code == 201
        mock_init_entrevista.assert_called_once_with(
            mock_db, candidatura_id=created_candidatura.id
        )

    app.dependency_overrides.clear()
