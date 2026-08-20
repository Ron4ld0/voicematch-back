from enum import Enum


class TipoUsuario(str, Enum):
    admin_sistema = "admin_sistema"
    admin_empresa = "admin_empresa"
    recrutador = "recrutador"


class StatusEmpresa(str, Enum):
    ativa = "ativa"
    suspensa = "suspensa"


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
