"""Validação de CNPJ pelos dígitos verificadores.

A função normaliza a entrada (aceita com ou sem máscara) e devolve apenas os
dígitos, que é o formato gravado no banco. Guardar sem máscara evita que o
mesmo documento entre duas vezes escrito de formas diferentes.
"""

import re

SOMENTE_DIGITOS = re.compile(r"\D")


def _digitos(valor: str) -> str:
    return SOMENTE_DIGITOS.sub("", valor or "")


def _digito_verificador(digitos: str, pesos: list) -> int:
    soma = sum(int(d) * p for d, p in zip(digitos, pesos))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def validar_cnpj(valor: str) -> str:
    """Retorna o CNPJ normalizado (14 dígitos) ou levanta ValueError."""
    cnpj = _digitos(valor)

    if len(cnpj) != 14:
        raise ValueError("CNPJ deve conter 14 dígitos.")

    # Sequências como 00.000.000/0000-00 passam no cálculo dos dígitos, mas não
    # são CNPJs válidos — precisam ser barradas explicitamente.
    if cnpj == cnpj[0] * 14:
        raise ValueError("CNPJ inválido.")

    pesos_primeiro = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_segundo = [6] + pesos_primeiro

    primeiro = _digito_verificador(cnpj[:12], pesos_primeiro)
    segundo = _digito_verificador(cnpj[:13], pesos_segundo)

    if cnpj[12:] != f"{primeiro}{segundo}":
        raise ValueError("CNPJ inválido.")

    return cnpj
