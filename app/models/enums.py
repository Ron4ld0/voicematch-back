from enum import Enum


class TipoUsuario(str, Enum):
    recrutador = "recrutador"


class StatusVaga(str, Enum):
    ativa = "ativa"
    pausada = "pausada"
    encerrada = "encerrada"


class StatusCandidatura(str, Enum):
    pendente_triagem = "pendente_triagem"
    aprovada_triagem = "aprovada_triagem"
    reprovada_triagem = "reprovada_triagem"
    em_entrevista = "em_entrevista"
    avaliada = "avaliada"
    aprovada = "aprovada"
    rejeitada = "rejeitada"


class StatusEntrevista(str, Enum):
    agendada = "agendada"
    em_andamento = "em_andamento"
    concluida = "concluida"
    cancelada = "cancelada"
