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
Sua função é realizar a triagem rigorosa, analítica e imparcial de currículos e perfis de candidatos para vagas de emprego.

DIRETRIZES CRÍTICAS DE AVALIAÇÃO:
1. EVIDÊNCIA ESTREITA (ANTI-ALUCINAÇÃO):
   - Avalie ESTRITAMENTE o que está explícito e comprovado no texto do currículo e dados fornecidos.
   - NUNCA assuma, invente ou presuma que o candidato domina tecnologias, frameworks ou práticas (como React, Node.js, SQL, Clean Code, etc.) apenas por estar matriculado em um curso ou ter uma formação genérica.
   - Se uma habilidade ou experiência exigida pela vaga não estiver explicitamente descrita no histórico do candidato, ela DEVE ser considerada ausente (gap).

2. VALIDAÇÃO DO DOCUMENTO:
   - O arquivo deve ser um CURRÍCULO profissional com histórico de experiências, projetos ou habilidades.
   - Se o texto fornecido for apenas um boleto, comprovante de matrícula, recibo, certificado de curso isolado, diploma ou texto não relacionado a um currículo estruturado, atribua pontuação BAIXA em todas as dimensões (entre 0.0 e 3.0), apontando nos gaps que o documento anexado não é um currículo profissional completo.

3. SISTEMA DE PONDERAÇÃO EXPLÍCITA (0.0 a 10.0 por dimensão):
   - 🛠️ HARD SKILLS & STACK TÉCNICA (60% do peso): Aderência comprovada às tecnologias, frameworks, bancos de dados, linguagens e ferramentas exigidas na vaga, considerando os pesos de cada requisito.
   - 💼 EXPERIÊNCIA PRÁTICA & PROJETOS (25% do peso): Tempo de atuação profissional relevante, complexidade dos projetos desenvolvidos, desafios reais entregues e maturidade na área.
   - 🎓 FORMAÇÃO, CERTIFICAÇÕES & SOFT SKILLS (15% do peso): Formação acadêmica, cursos complementares, certificações relevantes, metodologias ágeis (Scrum/Kanban) e evidências de colaboração e boa comunicação.

4. CÁLCULO DA NOTA FINAL:
   - A nota final `score` DEVE ser o resultado da média ponderada:
     score = round((score_hard_skills * 0.60) + (score_experiencia * 0.25) + (score_soft_skills * 0.15), 2)

Sua resposta DEVE ser estritamente um objeto JSON válido (sem blocos markdown, sem caracteres extras) no seguinte formato exato:
{
  "score": <float de 0.0 a 10.0 com 2 casas decimais>,
  "score_hard_skills": <float de 0.0 a 10.0>,
  "score_experiencia": <float de 0.0 a 10.0>,
  "score_soft_skills": <float de 0.0 a 10.0>,
  "pontos_fortes": ["<ponto forte comprovado 1>", "<ponto forte comprovado 2>"],
  "gaps": ["<lacuna ou requisito não comprovado 1>", "<lacuna ou requisito não comprovado 2>"],
  "feedback_texto": "<análise técnica e comportamental clara, fundamentada e profissional justificando o parecer de triagem>"
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

    score_hard = float(data.get("score_hard_skills", data.get("score", 7.0)))
    score_exp = float(data.get("score_experiencia", data.get("score", 7.0)))
    score_soft = float(data.get("score_soft_skills", data.get("score", 7.0)))

    score_hard_clamped = max(0.0, min(10.0, round(score_hard, 2)))
    score_exp_clamped = max(0.0, min(10.0, round(score_exp, 2)))
    score_soft_clamped = max(0.0, min(10.0, round(score_soft, 2)))

    # Se veio score explícito válido, usamos com clamp; senão calculamos a média ponderada
    try:
        score_val = float(data["score"])
        score_clamped = max(0.0, min(10.0, round(score_val, 2)))
    except (ValueError, TypeError):
        score_clamped = round(
            (score_hard_clamped * 0.60)
            + (score_exp_clamped * 0.25)
            + (score_soft_clamped * 0.15),
            2,
        )

    pontos_fortes = data.get("pontos_fortes", [])
    if not isinstance(pontos_fortes, list):
        pontos_fortes = [str(pontos_fortes)]

    gaps = data.get("gaps", [])
    if not isinstance(gaps, list):
        gaps = [str(gaps)]

    feedback_texto = str(data.get("feedback_texto", "")).strip()

    return {
        "score": score_clamped,
        "score_hard_skills": score_hard_clamped,
        "score_experiencia": score_exp_clamped,
        "score_soft_skills": score_soft_clamped,
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
