import logging
import uuid

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.grupo_habilidade import GrupoHabilidade, GrupoHabilidadeItem
from app.models.habilidade import Habilidade, ObrigatoriedadeEnum, TipoHabilidadeEnum

logger = logging.getLogger(__name__)

GRUPOS_PADRAO_SEED = [
    # --- HARD SKILLS ---
    {
        "nome": "Desenvolvedor Frontend Pleno/Sênior",
        "tipo": TipoHabilidadeEnum.HARD,
        "descricao": (
            "Perfil completo para desenvolvimento frontend com React, TypeScript, "
            "Next.js, Tailwind e consumo de APIs modernas."
        ),
        "itens": [
            {
                "habilidade_nome": "React",
                "peso": 9,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "TypeScript",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Next.js",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.DESEJAVEL,
            },
            {
                "habilidade_nome": "HTML5 / CSS3",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Tailwind CSS",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.DESEJAVEL,
            },
            {
                "habilidade_nome": "Consumo de APIs (REST / GraphQL)",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Redux / Zustand",
                "peso": 6,
                "obrigatoriedade": ObrigatoriedadeEnum.DESEJAVEL,
            },
            {
                "habilidade_nome": "Git & Git Flow",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
        ],
    },
    {
        "nome": "Desenvolvedor Backend Python",
        "tipo": TipoHabilidadeEnum.HARD,
        "descricao": (
            "Perfil especializado em desenvolvimento de APIs e microsserviços em Python "
            "com FastAPI/Django, PostgreSQL e Docker."
        ),
        "itens": [
            {
                "habilidade_nome": "Python (FastAPI / Django)",
                "peso": 9,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "PostgreSQL",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "SQLAlchemy / Prisma / TypeORM",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Criação de APIs RESTful e WebSockets",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Docker & Docker Compose",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.DESEJAVEL,
            },
            {
                "habilidade_nome": "Testes Automatizados (Jest, Pytest, Cypress)",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.DESEJAVEL,
            },
            {
                "habilidade_nome": "Clean Architecture & SOLID",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.DESEJAVEL,
            },
            {
                "habilidade_nome": "Git & Git Flow",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
        ],
    },
    {
        "nome": "Desenvolvedor Backend Node.js",
        "tipo": TipoHabilidadeEnum.HARD,
        "descricao": (
            "Perfil para engenharia de backend com ecossistema Node.js, NestJS/Express, "
            "TypeScript, bancos relacionais e Redis."
        ),
        "itens": [
            {
                "habilidade_nome": "Node.js (Express / NestJS)",
                "peso": 9,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "TypeScript",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "PostgreSQL",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Redis",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.DESEJAVEL,
            },
            {
                "habilidade_nome": "Criação de APIs RESTful e WebSockets",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Docker & Docker Compose",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.DESEJAVEL,
            },
            {
                "habilidade_nome": "Segurança & Autenticação (JWT, OAuth2)",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.DESEJAVEL,
            },
            {
                "habilidade_nome": "Git & Git Flow",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
        ],
    },
    {
        "nome": "Engenheiro DevOps & Cloud",
        "tipo": TipoHabilidadeEnum.HARD,
        "descricao": (
            "Perfil para infraestrutura em nuvem (AWS), conteinerização, "
            "automação de pipelines CI/CD e orquestração com Kubernetes."
        ),
        "itens": [
            {
                "habilidade_nome": "Docker & Docker Compose",
                "peso": 9,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Kubernetes",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "AWS (S3, EC2, Lambda)",
                "peso": 9,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "CI/CD (GitHub Actions / GitLab)",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Linux & Nginx",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Git & Git Flow",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
        ],
    },
    # --- SOFT SKILLS ---
    {
        "nome": "Perfil Colaborativo & Ágil",
        "tipo": TipoHabilidadeEnum.SOFT,
        "descricao": (
            "Perfil com forte inteligência interpessoal, ideal para times "
            "multidisciplinares e processos ágeis contínuos."
        ),
        "itens": [
            {
                "habilidade_nome": "Trabalho em Equipe e Colaboração",
                "peso": 9,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Comunicação Clara e Articulada",
                "peso": 9,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Adaptabilidade e Aprendizado Rápido",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Organização e Gestão de Tempo",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.DESEJAVEL,
            },
        ],
    },
    {
        "nome": "Liderança & Mentoria Técnica",
        "tipo": TipoHabilidadeEnum.SOFT,
        "descricao": (
            "Perfil voltado para posições de liderança técnica, desenvolvimento "
            "de pessoas, mentoria e mediação de conflitos."
        ),
        "itens": [
            {
                "habilidade_nome": "Liderança e Mentoria Técnica",
                "peso": 9,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Comunicação Clara e Articulada",
                "peso": 9,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Gestão de Conflitos e Inteligência Emocional",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Pensamento Crítico e Análise",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
        ],
    },
    {
        "nome": "Resolução de Problemas sob Pressão",
        "tipo": TipoHabilidadeEnum.SOFT,
        "descricao": (
            "Perfil analítico de alta resiliência para ambientes de ritmo acelerado, "
            "tomada de decisão crítica e resposta a incidentes."
        ),
        "itens": [
            {
                "habilidade_nome": "Resolução de Problemas sob Pressão",
                "peso": 9,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Pensamento Crítico e Análise",
                "peso": 9,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Adaptabilidade e Aprendizado Rápido",
                "peso": 8,
                "obrigatoriedade": ObrigatoriedadeEnum.OBRIGATORIA,
            },
            {
                "habilidade_nome": "Comunicação Clara e Articulada",
                "peso": 7,
                "obrigatoriedade": ObrigatoriedadeEnum.DESEJAVEL,
            },
        ],
    },
]


def seed_grupos_habilidades(db: Session = None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        # Cache de habilidades existentes por nome para lookup rápido
        habilidades_map = {h.nome: h.id for h in db.query(Habilidade).all()}

        total_criados = 0
        for grupo_data in GRUPOS_PADRAO_SEED:
            grupo_existente = (
                db.query(GrupoHabilidade)
                .filter(GrupoHabilidade.nome == grupo_data["nome"])
                .first()
            )

            if not grupo_existente:
                novo_grupo = GrupoHabilidade(
                    id=uuid.uuid4(),
                    nome=grupo_data["nome"],
                    tipo=grupo_data["tipo"],
                    descricao=grupo_data["descricao"],
                    empresa_id=None,
                )

                for item in grupo_data["itens"]:
                    hab_id = habilidades_map.get(item["habilidade_nome"])
                    if hab_id:
                        novo_item = GrupoHabilidadeItem(
                            grupo_id=novo_grupo.id,
                            habilidade_id=hab_id,
                            peso=item["peso"],
                            obrigatoriedade=item["obrigatoriedade"],
                        )
                        novo_grupo.itens.append(novo_item)

                db.add(novo_grupo)
                total_criados += 1

        db.commit()
        print(
            f"[SEED] Seed de grupos de habilidades concluído com sucesso! "
            f"{total_criados} novos grupos inseridos."
        )
    except Exception as e:  # noqa: BLE001
        db.rollback()
        print(f"[SEED] Erro ao executar seed de grupos de habilidades: {e}")
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    seed_grupos_habilidades()
