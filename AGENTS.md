# Diretrizes para Assistentes de IA

Para entender a arquitetura completa, modelos de dados, fluxo de negócio e convenções do projeto, consulte o arquivo [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md).

## Regras Principais de Desenvolvimento:
1. ** SQLAlchemy 2.0**: Sempre utilizar `Mapped[...]` e `mapped_column(...)`.
2. **Imports Tipados**: Utilizar `if TYPE_CHECKING:` nos models para relacionamentos do ORM para evitar dependências circulares.
3. **Migrações Alembic**: Todas as mudanças no schema devem ter migração correspondente em `alembic/versions/`.
4. **Gate de Triagem**: Lembrar que `Entrevista` só pode ser criada se a `Candidatura` estiver com `status == StatusCandidatura.aprovada_triagem`.
5. **Formatação & Linter**: Código deve passar sem erros no `ruff` e `ruff-format`.
