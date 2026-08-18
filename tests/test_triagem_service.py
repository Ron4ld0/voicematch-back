from uuid import uuid4
from unittest.mock import MagicMock, patch
import pytest
from app.models.enums import StatusCandidatura
from app.services.curriculo_parser import extrair_texto_curriculo
from app.services.triagem_service import (
    analisar_curriculo,
    _parse_and_validate_response,
)
from app.core.database import get_db
from app.main import app
from fastapi.testclient import TestClient


def test_curriculo_parser_invalid_extension():
    with pytest.raises(ValueError, match="não suportado"):
        extrair_texto_curriculo("http://example.com/curriculo.txt")


def test_curriculo_parser_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        extrair_texto_curriculo("iniquo_arquivo_que_nao_existe.pdf")


def test_parse_and_validate_response_success():
    raw_json = '{"score": 8.5, "pontos_fortes": ["Python"], "gaps": ["Docker"], "feedback_texto": "Bom candidato"}'
    result = _parse_and_validate_response(raw_json)
    assert result["score"] == 8.5
    assert result["pontos_fortes"] == ["Python"]
    assert result["gaps"] == ["Docker"]
    assert result["feedback_texto"] == "Bom candidato"


def test_parse_and_validate_response_invalid():
    with pytest.raises(ValueError):
        _parse_and_validate_response('{"invalido": true}')


@patch("app.services.triagem_service._get_groq_client")
def test_analisar_curriculo_success(mock_get_client):
    mock_response = MagicMock()
    mock_response.choices[
        0
    ].message.content = '{"score": 9.0, "pontos_fortes": ["FastAPI"], "gaps": [], "feedback_texto": "Excelente"}'
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client

    mock_candidato = MagicMock()
    mock_candidato.id = uuid4()
    mock_candidato.nome = "João Silva"
    mock_candidato.curriculo_url = None
    mock_candidato.resumo_profissional = "Dev Backend"
    mock_candidato.experiencias = ["Dev Python 3 anos"]
    mock_candidato.tecnologias = ["Python", "FastAPI"]

    mock_vaga = MagicMock()
    mock_vaga.titulo = "Desenvolvedor Backend Python"
    mock_vaga.descricao = "Vaga Python FastAPI"
    mock_vaga.descricao_candidato_ideal = None
    mock_vaga.requisitos_hard = ["Python", "FastAPI"]
    mock_vaga.requisitos_soft = ["Trabalho em equipe"]

    res = analisar_curriculo(mock_candidato, mock_vaga)
    assert res["score"] == 9.0
    assert res["pontos_fortes"] == ["FastAPI"]
    assert res["feedback_texto"] == "Excelente"


@patch("app.services.triagem_service._get_groq_client")
@patch("app.services.triagem_service.extrair_texto_curriculo")
def test_analisar_curriculo_with_local_pdf_file(mock_extrair, mock_get_client):
    mock_extrair.return_value = (
        "Engenheiro de Software com 5 anos de experiencia em Python e PostgreSQL."
    )

    mock_response = MagicMock()
    mock_response.choices[
        0
    ].message.content = '{"score": 8.8, "pontos_fortes": ["Experiencia Python"], "gaps": [], "feedback_texto": "Aprovado na triagem"}'
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client

    mock_candidato = MagicMock()
    mock_candidato.id = uuid4()
    mock_candidato.nome = "Maria Santos"
    mock_candidato.curriculo_url = "/media/curriculos/maria_curriculo.pdf"
    mock_candidato.resumo_profissional = None
    mock_candidato.experiencias = None
    mock_candidato.tecnologias = None

    mock_vaga = MagicMock()
    mock_vaga.titulo = "Engenheiro de Software Python"
    mock_vaga.descricao = "Vaga Python"
    mock_vaga.descricao_candidato_ideal = None
    mock_vaga.requisitos_hard = ["Python"]
    mock_vaga.requisitos_soft = []

    res = analisar_curriculo(mock_candidato, mock_vaga)
    assert res["score"] == 8.8
    assert res["pontos_fortes"] == ["Experiencia Python"]
    mock_extrair.assert_called_once_with("/media/curriculos/maria_curriculo.pdf")


def test_apply_to_vaga_fallback_on_groq_error():
    vaga_id = uuid4()
    candidato_id = uuid4()

    mock_vaga = MagicMock()
    mock_vaga.id = vaga_id
    mock_vaga.score_minimo_triagem = 7.0

    mock_candidato = MagicMock()
    mock_candidato.id = candidato_id

    mock_db = MagicMock()
    # Return mock_vaga, mock_candidato, None for existing_candidatura
    mock_db.query().filter().first.side_effect = [mock_vaga, mock_candidato, None]

    created_candidatura = MagicMock()
    created_candidatura.id = uuid4()
    created_candidatura.vaga_id = vaga_id
    created_candidatura.candidato_id = candidato_id
    created_candidatura.status = StatusCandidatura.pendente_triagem
    created_candidatura.score_triagem = None
    created_candidatura.feedback_triagem = None

    mock_db.query().filter().first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db

    with patch(
        "app.routers.candidatura.create_candidatura", return_value=created_candidatura
    ), patch(
        "app.routers.candidatura.analisar_curriculo",
        side_effect=Exception("API Groq Fora do Ar"),
    ):
        client = TestClient(app)
        response = client.post(
            "/candidaturas",
            json={
                "vaga_id": str(vaga_id),
                "candidato_id": str(candidato_id),
            },
        )
        assert response.status_code == 201
        assert created_candidatura.status == StatusCandidatura.pendente_triagem
        assert "falha na triagem" in created_candidatura.feedback_triagem["erro"]

    app.dependency_overrides.clear()
