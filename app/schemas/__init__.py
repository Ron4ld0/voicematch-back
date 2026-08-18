from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.candidato import CandidatoCreate, CandidatoResponse, CandidatoUpdate
from app.schemas.candidatura import (
    CandidaturaCreate,
    CandidaturaResponse,
    CandidaturaStatusUpdate,
)
from app.schemas.entrevista import (
    EntrevistaCreate,
    EntrevistaResponse,
    EntrevistaUpdate,
    PerguntaCreate,
    PerguntaResponse,
    RespostaCreate,
    RespostaResponse,
)
from app.schemas.grupo_habilidade import (
    GrupoHabilidadeCreate,
    GrupoHabilidadeItemCreate,
    GrupoHabilidadeItemResponse,
    GrupoHabilidadeResponse,
    GrupoHabilidadeUpdate,
)
from app.schemas.habilidade import (
    HabilidadeCreate,
    HabilidadeResponse,
    HabilidadeUpdate,
    VagaHabilidadeCreate,
    VagaHabilidadeResponse,
)
from app.schemas.usuario import (
    RecrutadorCreate,
    RecrutadorResponse,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)
from app.schemas.vaga import VagaCreate, VagaResponse, VagaUpdate

__all__ = [
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioResponse",
    "RecrutadorCreate",
    "RecrutadorResponse",
    "CandidatoCreate",
    "CandidatoUpdate",
    "CandidatoResponse",
    "VagaCreate",
    "VagaUpdate",
    "VagaResponse",
    "CandidaturaCreate",
    "CandidaturaStatusUpdate",
    "CandidaturaResponse",
    "EntrevistaCreate",
    "EntrevistaUpdate",
    "EntrevistaResponse",
    "PerguntaCreate",
    "PerguntaResponse",
    "RespostaCreate",
    "RespostaResponse",
    "LoginRequest",
    "TokenResponse",
    "HabilidadeCreate",
    "HabilidadeUpdate",
    "HabilidadeResponse",
    "VagaHabilidadeCreate",
    "VagaHabilidadeResponse",
    "GrupoHabilidadeItemCreate",
    "GrupoHabilidadeItemResponse",
    "GrupoHabilidadeCreate",
    "GrupoHabilidadeUpdate",
    "GrupoHabilidadeResponse",
]
