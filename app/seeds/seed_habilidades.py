import uuid
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.habilidade import Habilidade, TipoHabilidadeEnum

logger = logging.getLogger(__name__)

HABILIDADES_SEED = [
    # Frontend (HARD)
    {"nome": "React", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Frontend"},
    {"nome": "Next.js", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Frontend"},
    {"nome": "TypeScript", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Frontend"},
    {"nome": "JavaScript (ES6+)", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Frontend"},
    {"nome": "Vue.js", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Frontend"},
    {"nome": "Angular", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Frontend"},
    {"nome": "HTML5 / CSS3", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Frontend"},
    {"nome": "Tailwind CSS", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Frontend"},
    {"nome": "Redux / Zustand", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Frontend"},
    {"nome": "Consumo de APIs (REST / GraphQL)", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Frontend"},

    # Backend (HARD)
    {"nome": "Node.js (Express / NestJS)", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Backend"},
    {"nome": "Python (FastAPI / Django)", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Backend"},
    {"nome": "Java (Spring Boot)", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Backend"},
    {"nome": "C# (.NET Core)", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Backend"},
    {"nome": "Go (Golang)", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Backend"},
    {"nome": "PHP (Laravel)", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Backend"},
    {"nome": "Criação de APIs RESTful e WebSockets", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Backend"},

    # Bancos de Dados & ORMs (HARD)
    {"nome": "PostgreSQL", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Banco de Dados"},
    {"nome": "MySQL", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Banco de Dados"},
    {"nome": "MongoDB", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Banco de Dados"},
    {"nome": "Redis", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Banco de Dados"},
    {"nome": "SQLAlchemy / Prisma / TypeORM", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Banco de Dados"},
    {"nome": "Modelagem Relacional e NoSQL", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Banco de Dados"},

    # DevOps, Cloud & Ferramentas (HARD)
    {"nome": "Docker & Docker Compose", "tipo": TipoHabilidadeEnum.HARD, "categoria": "DevOps & Cloud"},
    {"nome": "Kubernetes", "tipo": TipoHabilidadeEnum.HARD, "categoria": "DevOps & Cloud"},
    {"nome": "AWS (S3, EC2, Lambda)", "tipo": TipoHabilidadeEnum.HARD, "categoria": "DevOps & Cloud"},
    {"nome": "CI/CD (GitHub Actions / GitLab)", "tipo": TipoHabilidadeEnum.HARD, "categoria": "DevOps & Cloud"},
    {"nome": "Git & Git Flow", "tipo": TipoHabilidadeEnum.HARD, "categoria": "DevOps & Cloud"},
    {"nome": "Linux & Nginx", "tipo": TipoHabilidadeEnum.HARD, "categoria": "DevOps & Cloud"},

    # Arquitetura & Testes (HARD)
    {"nome": "Clean Architecture & SOLID", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Arquitetura & Qualidade"},
    {"nome": "Arquitetura de Microsserviços", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Arquitetura & Qualidade"},
    {"nome": "Testes Automatizados (Jest, Pytest, Cypress)", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Arquitetura & Qualidade"},
    {"nome": "Segurança & Autenticação (JWT, OAuth2)", "tipo": TipoHabilidadeEnum.HARD, "categoria": "Arquitetura & Qualidade"},

    # Soft Skills (SOFT)
    {"nome": "Comunicação Clara e Articulada", "tipo": TipoHabilidadeEnum.SOFT, "categoria": "Comportamental"},
    {"nome": "Resolução de Problemas sob Pressão", "tipo": TipoHabilidadeEnum.SOFT, "categoria": "Comportamental"},
    {"nome": "Trabalho em Equipe e Colaboração", "tipo": TipoHabilidadeEnum.SOFT, "categoria": "Comportamental"},
    {"nome": "Adaptabilidade e Aprendizado Rápido", "tipo": TipoHabilidadeEnum.SOFT, "categoria": "Comportamental"},
    {"nome": "Organização e Gestão de Tempo", "tipo": TipoHabilidadeEnum.SOFT, "categoria": "Comportamental"},
    {"nome": "Pensamento Crítico e Análise", "tipo": TipoHabilidadeEnum.SOFT, "categoria": "Comportamental"},
    {"nome": "Liderança e Mentoria Técnica", "tipo": TipoHabilidadeEnum.SOFT, "categoria": "Comportamental"},
    {"nome": "Gestão de Conflitos e Inteligência Emocional", "tipo": TipoHabilidadeEnum.SOFT, "categoria": "Comportamental"},
]


def seed_habilidades(db: Session = None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        total_criadas = 0
        for item in HABILIDADES_SEED:
            existe = db.query(Habilidade).filter(Habilidade.nome == item["nome"]).first()
            if not existe:
                nova_hab = Habilidade(
                    id=uuid.uuid4(),
                    nome=item["nome"],
                    tipo=item["tipo"],
                    categoria=item["categoria"],
                    empresa_id=None
                )
                db.add(nova_hab)
                total_criadas += 1

        db.commit()
        print(f"[SEED] Seed de habilidades concluído com sucesso! {total_criadas} novas habilidades inseridas.")
    except Exception as e:
        db.rollback()
        print(f"[SEED] Erro ao executar seed de habilidades: {e}")
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    seed_habilidades()
