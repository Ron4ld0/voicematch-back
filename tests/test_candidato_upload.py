import io
from uuid import uuid4
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.core.database import get_db
from app.main import app


def test_upload_curriculo_pdf_success(tmp_path, monkeypatch):
    candidato_id = uuid4()
    mock_candidato = MagicMock()
    mock_candidato.id = candidato_id
    mock_candidato.nome = "Candidato Teste"
    mock_candidato.email = "candidato@teste.com"
    mock_candidato.telefone = "11999999999"
    mock_candidato.curriculo_url = None
    mock_candidato.resumo_profissional = None
    mock_candidato.experiencias = None
    mock_candidato.tecnologias = None
    mock_candidato.data_cadastro = None

    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = mock_candidato

    def fake_update_candidato(db, db_candidato, candidato_in):
        db_candidato.curriculo_url = candidato_in.curriculo_url
        return db_candidato

    monkeypatch.setattr("app.routers.candidato.update_candidato", fake_update_candidato)

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        dummy_pdf = io.BytesIO(b"%PDF-1.4 Fake PDF Content for Testing")

        response = client.post(
            f"/candidatos/{candidato_id}/upload-curriculo",
            files={"file": ("meu_curriculo.pdf", dummy_pdf, "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["curriculo_url"] is not None
        assert data["curriculo_url"].startswith("/media/curriculos/")
        assert data["curriculo_url"].endswith(".pdf")
    finally:
        app.dependency_overrides.clear()


def test_upload_curriculo_invalid_extension():
    candidato_id = uuid4()
    mock_candidato = MagicMock()
    mock_candidato.id = candidato_id

    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = mock_candidato

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        dummy_txt = io.BytesIO(b"Este e um arquivo texto invalido")

        response = client.post(
            f"/candidatos/{candidato_id}/upload-curriculo",
            files={"file": ("arquivo.txt", dummy_txt, "text/plain")},
        )
        assert response.status_code == 400
        assert "não suportado" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_upload_curriculo_candidate_not_found():
    candidato_id = uuid4()
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        dummy_pdf = io.BytesIO(b"%PDF-1.4 Fake PDF Content")

        response = client.post(
            f"/candidatos/{candidato_id}/upload-curriculo",
            files={"file": ("curriculo.pdf", dummy_pdf, "application/pdf")},
        )
        assert response.status_code == 404
        assert "Candidato não encontrado" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
