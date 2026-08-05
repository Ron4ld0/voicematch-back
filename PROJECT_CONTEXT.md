# Contexto do Projeto — VoiceMatch Backend

Este arquivo fornece o contexto arquitetural, regras de negócio e diretrizes de desenvolvimento para auxiliar assistentes de IA (e desenvolvedores) no trabalho com este repositório.

---

## 🏗️ Visão Geral da Arquitetura

O **VoiceMatch Backend** é uma API RESTful desenvolvida com **FastAPI**, **PostgreSQL** e **SQLAlchemy 2.0**, responsável pela gestão de recrutadores, vagas, candidatos, triagem automatizada por IA e condução de entrevistas de emprego por voz.

### Stack Tecnológica
- **Framework**: FastAPI (Python 3.12+)
- **ORM & Banco de Dados**: SQLAlchemy 2.0 (com Mapped/mapped_column) + PostgreSQL
- **Migrações**: Alembic
- **Validação & Schemas**: Pydantic v2
- **Containerização**: Docker & Docker Compose
- **Testes & Qualidade**: Pytest, Ruff (linter & formatter), Pre-commit

---

## 📁 Estrutura de Diretórios

```
voicematch-back/
├── alembic/              # Scripts e versões de migração de banco de dados
│   └── versions/
├── app/
│   ├── core/             # Configurações globais, conexão DB, validadores e segurança
│   ├── crud/             # Camada de acesso a dados (Operações CRUD)
│   ├── models/           # Modelos de dados SQLAlchemy (ORM)
│   ├── routers/          # Endpoints da API agrupados por domínio
│   └── schemas/          # Modelos de entrada/saída Pydantic v2
├── tests/                # Testes unitários e de integração (pytest)
├── Dockerfile            # Imagem de produção da API
├── docker-compose.yml    # Orquestração local (API + PostgreSQL)
└── requirements.txt      # Dependências Python do projeto
```

---

## 🔄 Fluxo de Negócio & Regras Principais

```
Recrutador ──> Vaga (score_minimo_triagem)
                 │
Candidato ──> Candidatura (pendente_triagem)
                 │
                 ▼
         [Triagem por IA] ─── Score >= score_minimo_triagem ───> aprovada_triagem ──> Permite Entrevista
                 │
                 └─── Score < score_minimo_triagem  ───> reprovada_triagem (Bloqueia Entrevista)
```

1. **Vagas & Gate de Triagem**:
   - Uma `Vaga` pode definir o campo `score_minimo_triagem` (ex: `7.50`). Se for `null`, a vaga não possui gate de triagem por IA ativo.
2. **Candidaturas**:
   - Status iniciais e transições do Enum `StatusCandidatura`:
     - `pendente_triagem`: estado padrão ao criar uma candidatura.
     - `aprovada_triagem`: o score calculado pela IA atingiu o threshold da vaga.
     - `reprovada_triagem`: o score ficou abaixo do threshold.
     - `em_entrevista`, `avaliada`, `aprovada`, `rejeitada`: estágios posteriores do processo.
3. **Regra de Criação de Entrevistas**:
   - A rota `POST /entrevistas` exige obrigatoriamente que a `candidatura` associada possua o status **`aprovada_triagem`**. Caso contrário, o servidor retorna erro HTTP `400 Bad Request`.

---

## ⚙️ Convenções de Código & Boas Práticas

1. **Modelos SQLAlchemy**:
   - Utilize a sintaxe moderna 2.0: `Mapped[Tipo]` e `mapped_column(...)`.
   - Para relacionamentos entre models, utilize `if TYPE_CHECKING:` nos imports para evitar importações circulares e avisos de lint do `ruff`.
2. **Migrações Alembic**:
   - Toda alteração nos modelos em `app/models/` DEVE ser acompanhada de uma migração gerada/atualizada em `alembic/versions/`.
   - Ao adicionar novos valores a tipos Enum do PostgreSQL, utilize `with op.get_context().autocommit_block():` com `ALTER TYPE ... ADD VALUE IF NOT EXISTS` para evitar erros de transação no Postgres.
3. **Qualidade & Pre-Commit**:
   - O repositório utiliza hooks do pre-commit com `ruff` e `ruff-format`. Certifique-se de formatar o código e resolver warnings de import/linter antes de comitar.
