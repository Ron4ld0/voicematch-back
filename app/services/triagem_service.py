import json
import logging
from typing import Dict, Any, TYPE_CHECKING
from openai import OpenAI

from app.core.config import settings
from app.services.curriculo_parser import extrair_texto_curriculo

if TYPE_CHECKING:
    from app.models.candidato import Candidato
    from app.models.vaga import Vaga

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um especialista sênior em recrutamento e seleção técnica de RH.
Sua função é realizar a triagem de currículos e perfis de candidatos para vagas de emprego.

Analise cuidadosamente as experiências, conhecimentos técnicos, resumo e texto do currículo do candidato em relação aos requisitos exigidos pela vaga (descrição, perfil ideal, requisitos hard e soft).

Sua resposta DEVE ser estritamente um objeto JSON válido (sem blocos de código markdown, sem caracteres extras) no seguinte formato exato:
{
  "score": <número float de 0.0 a 10.0 representando a nota final de aderência com até 2 casas decimais>,
  "pontos_fortes": ["<ponto forte 1>", "<ponto forte 2>", ...],
  "gaps": ["<lacuna ou requisito não atendido 1>", ...],
  "feedback_texto": "<texto direto, construtivo e profissional explicando o resultado da avaliação ao candidato>"
}
"""


def _get_groq_client() -> OpenAI:
    if not settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY não configurada. Defina a variável GROQ_API_KEY no arquivo .env."
        )
    return OpenAI(
        api_key=settings.GROQ_API_KEY, base_url="https://api.groq.com/openai/v1"
    )


def _parse_and_validate_response(raw_text: str) -> Dict[str, Any]:
    data = json.loads(raw_text)
    if not isinstance(data, dict):
        raise ValueError("A resposta da IA não é um objeto JSON.")

    if "score" not in data or "feedback_texto" not in data:
        raise ValueError(
            "Chaves obrigatórias 'score' ou 'feedback_texto' ausentes no JSON."
        )

    score = float(data["score"])
    score_clamped = max(0.0, min(10.0, round(score, 2)))

    pontos_fortes = data.get("pontos_fortes", [])
    if not isinstance(pontos_fortes, list):
        pontos_fortes = [str(pontos_fortes)]

    gaps = data.get("gaps", [])
    if not isinstance(gaps, list):
        gaps = [str(gaps)]

    feedback_texto = str(data.get("feedback_texto", "")).strip()

    return {
        "score": score_clamped,
        "pontos_fortes": [str(p) for p in pontos_fortes],
        "gaps": [str(g) for g in gaps],
        "feedback_texto": feedback_texto,
    }


def analisar_curriculo(candidato: "Candidato", vaga: "Vaga") -> Dict[str, Any]:
    """
    Analisa o perfil e currículo do candidato contra os requisitos da vaga usando a API da Groq (LLM).
    Retorna um dicionário contendo score, pontos_fortes, gaps e feedback_texto.
    """
    # 1. Tentar extrair o texto do arquivo de currículo se curriculo_url estiver presente
    texto_curriculo = None
    if candidato.curriculo_url:
        try:
            texto_curriculo = extrair_texto_curriculo(candidato.curriculo_url)
        except Exception as e:
            logger.warning(
                f"Não foi possível extrair texto do arquivo de currículo do candidato '{candidato.id}': {e}"
            )

    # 2. Montar contexto do candidato
    experiencias_str = (
        json.dumps(candidato.experiencias, ensure_ascii=False)
        if candidato.experiencias
        else "Não informadas"
    )
    tecnologias_str = (
        json.dumps(candidato.tecnologias, ensure_ascii=False)
        if candidato.tecnologias
        else "Não informadas"
    )
    resumo_str = candidato.resumo_profissional or "Não informado"
    texto_curriculo_str = texto_curriculo or "Conteúdo do arquivo não disponível"

    # 3. Montar contexto da vaga
    req_hard_str = (
        json.dumps(vaga.requisitos_hard, ensure_ascii=False)
        if vaga.requisitos_hard
        else "Não informados"
    )
    req_soft_str = (
        json.dumps(vaga.requisitos_soft, ensure_ascii=False)
        if vaga.requisitos_soft
        else "Não informados"
    )
    perfil_ideal_str = vaga.descricao_candidato_ideal or "Não informado"

    user_prompt = f"""--- DADOS DA VAGA ---
Título: {vaga.titulo}
Descrição da Vaga: {vaga.descricao}
Perfil do Candidato Ideal: {perfil_ideal_str}
Requisitos Técnicos (Hard Skills): {req_hard_str}
Requisitos Comportamentais (Soft Skills): {req_soft_str}

--- DADOS DO CANDIDATO ---
Nome: {candidato.nome}
Resumo Profissional: {resumo_str}
Experiências Profissionais: {experiencias_str}
Tecnologias / Habilidades: {tecnologias_str}
Texto Extraído do Currículo:
{texto_curriculo_str}

--- INSTRUÇÃO ---
Avalie a compatibilidade do candidato com a vaga e responda EXCLUSIVAMENTE com o objeto JSON estruturado.
"""

    client = _get_groq_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    # Primeira chamada ao Groq
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL_TRIAGEM,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    raw_content = response.choices[0].message.content or ""

    try:
        return _parse_and_validate_response(raw_content)
    except Exception as parse_error:
        logger.warning(
            f"Erro ao processar JSON da primeira resposta da IA: {parse_error}. Tentando segunda chamada com instrução reforçada..."
        )
        # Segunda tentativa (Retry)
        messages.append({"role": "assistant", "content": raw_content})
        messages.append(
            {
                "role": "user",
                "content": (
                    "ATENÇÃO: Sua resposta anterior não atendeu ao formato JSON exigido. "
                    "Por favor, retorne APENAS um JSON válido contendo exatamente as chaves "
                    "'score' (float de 0 a 10), 'pontos_fortes' (lista de strings), "
                    "'gaps' (lista de strings) e 'feedback_texto' (string)."
                ),
            }
        )
        retry_response = client.chat.completions.create(
            model=settings.GROQ_MODEL_TRIAGEM,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        retry_content = retry_response.choices[0].message.content or ""
        return _parse_and_validate_response(retry_content)
