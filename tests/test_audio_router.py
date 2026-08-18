from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.enums import StatusCandidatura


def test_read_candidatura_returns_triage_metadata():
    candidatura_id = uuid4()
    vaga_id = uuid4()
    candidato_id = uuid4()
    now = datetime.now(UTC)

    mock_candidatura = MagicMock()
    mock_candidatura.id = candidatura_id
    mock_candidatura.vaga_id = vaga_id
    mock_candidatura.candidato_id = candidato_id
    mock_candidatura.status = StatusCandidatura.aprovada_triagem
    mock_candidatura.score_triagem = 8.5
    mock_candidatura.feedback_triagem = {
        "score": 8.5,
        "pontos_fortes": ["Python"],
        "gaps": [],
        "feedback_texto": "Aprovado",
    }
    mock_candidatura.data_triagem = now
    mock_candidatura.data_candidatura = now

    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = mock_candidatura

    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)
    response = client.get(f"/candidaturas/{candidatura_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["score_triagem"] == 8.5
    assert data["feedback_triagem"]["score"] == 8.5

    app.dependency_overrides.clear()


@patch("app.routers.audio.save_audio_file")
@patch("app.routers.audio.httpx.AsyncClient")
def test_upload_audio_resposta_saves_acoustics_and_next_question(
    mock_async_client_cls, mock_save_audio
):
    pergunta_id = uuid4()
    entrevista_id = uuid4()
    now = datetime.now(UTC)

    mock_save_audio.return_value = "/media/audio/test_response.wav"

    mock_response_ai = MagicMock()
    mock_response_ai.status_code = 200
    mock_response_ai.json.return_value = {
        "transcricao": "Olá, tenho vasta experiência em desenvolvimento de software.",
        "proxima_pergunta": "Poderia nos contar sobre um desafio técnico superado?",
        "metricas": {
            "proatividade": 9,
            "acustica": {
                "soft_skills_acusticas": {
                    "oratoria_e_clareza": 8.5,
                    "firmeza_e_confianca": 8.0,
                    "controle_de_estresse": 9.0,
                    "entusiasmo_e_engajamento": 8.2,
                },
                "parecer_acustico": "Excelente oratória",
            },
        },
    }

    mock_client_instance = MagicMock()
    mock_client_instance.post = AsyncMock(return_value=mock_response_ai)
    mock_async_client_cls.return_value.__aenter__.return_value = mock_client_instance

    mock_pergunta = MagicMock()
    mock_pergunta.id = pergunta_id
    mock_pergunta.entrevista_id = entrevista_id
    mock_pergunta.ordem = 1
    mock_pergunta.pergunta_texto = "Apresente-se"
    mock_pergunta.entrevista.candidatura.vaga.descricao = "Desenvolvedor Backend"
    mock_pergunta.entrevista.candidatura.candidato.curriculo_url = None
    mock_pergunta.entrevista.perguntas = [mock_pergunta]

    mock_db = MagicMock()
    mock_db.query().filter().first.side_effect = [
        mock_pergunta,  # get_pergunta
        None,  # existing_resposta
    ]

    mock_created_resposta = MagicMock()
    mock_created_resposta.id = uuid4()
    mock_created_resposta.pergunta_id = pergunta_id
    mock_created_resposta.audio_url = "/media/audio/test_response.wav"
    mock_created_resposta.transcricao = "Olá, tenho vasta experiência..."
    mock_created_resposta.metricas = mock_response_ai.json()["metricas"]
    mock_created_resposta.data_resposta = now

    app.dependency_overrides[get_db] = lambda: mock_db

    with (
        patch("app.routers.audio.create_resposta", return_value=mock_created_resposta),
        patch("app.routers.audio.create_pergunta") as mock_create_pergunta,
    ):
        client = TestClient(app)
        response = client.post(
            f"/audio/upload/{pergunta_id}",
            files={"file": ("test.wav", b"dummy audio content", "audio/wav")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["audio_url"] == "/media/audio/test_response.wav"
        assert "acustica" in data["metricas"]
        assert (
            data["metricas"]["acustica"]["soft_skills_acusticas"]["oratoria_e_clareza"]
            == 8.5
        )
        mock_create_pergunta.assert_called_once()

    app.dependency_overrides.clear()
