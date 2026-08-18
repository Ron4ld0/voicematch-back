from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.candidatura import Candidatura
from app.models.entrevista import Entrevista
from app.models.enums import StatusCandidatura
from app.models.vaga import Vaga


def test_status_candidatura_enum_values():
    assert StatusCandidatura.pendente_triagem == "pendente_triagem"
    assert StatusCandidatura.aprovada_triagem == "aprovada_triagem"
    assert StatusCandidatura.reprovada_triagem == "reprovada_triagem"
    assert StatusCandidatura.em_entrevista == "em_entrevista"
    assert StatusCandidatura.avaliada == "avaliada"
    assert StatusCandidatura.aprovada == "aprovada"
    assert StatusCandidatura.rejeitada == "rejeitada"


def test_vaga_and_candidatura_model_attributes():
    assert hasattr(Vaga, "score_minimo_triagem")
    assert hasattr(Candidatura, "score_triagem")
    assert hasattr(Candidatura, "feedback_triagem")
    assert hasattr(Candidatura, "data_triagem")


def test_register_entrevista_blocked_when_not_aprovada_triagem():
    mock_candidatura = MagicMock()
    mock_candidatura.id = uuid4()
    mock_candidatura.status = StatusCandidatura.pendente_triagem

    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = mock_candidatura

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.post(
            "/entrevistas",
            json={
                "candidatura_id": str(mock_candidatura.id),
                "status": "agendada",
            },
        )
        assert response.status_code == 400
        assert "aprovada_triagem" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_register_entrevista_allowed_when_aprovada_triagem():
    candidatura_id = uuid4()
    mock_candidatura = MagicMock()
    mock_candidatura.id = candidatura_id
    mock_candidatura.status = StatusCandidatura.aprovada_triagem

    def fake_refresh(obj):
        if isinstance(obj, Entrevista):
            if not getattr(obj, "id", None):
                obj.id = uuid4()
            if not getattr(obj, "data_criacao", None):
                obj.data_criacao = datetime.now(UTC)
            if not getattr(obj, "perguntas", None):
                obj.perguntas = []

    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = mock_candidatura
    mock_db.refresh.side_effect = fake_refresh

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.post(
            "/entrevistas",
            json={
                "candidatura_id": str(candidatura_id),
                "status": "agendada",
            },
        )
        assert response.status_code == 201
        assert response.json()["candidatura_id"] == str(candidatura_id)
        assert response.json()["status"] == "agendada"
    finally:
        app.dependency_overrides.clear()
