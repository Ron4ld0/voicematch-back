"""create_grupo_habilidade_tables

Revision ID: c3a1b8e92f14
Revises: d1859dde4cf9
Create Date: 2026-08-18 12:30:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3a1b8e92f14"
down_revision: str | Sequence[str] | None = "d1859dde4cf9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema: cria enums e tabelas de habilidades e grupos de habilidades."""
    # 1. Garante que os ENUMs existam de forma segura no PostgreSQL
    with op.get_context().autocommit_block():
        op.execute(
            "DO $$ BEGIN "
            "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipohabilidadeenum') THEN "
            "CREATE TYPE tipohabilidadeenum AS ENUM ('HARD', 'SOFT'); "
            "END IF; "
            "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'obrigatoriedadeenum') THEN "
            "CREATE TYPE obrigatoriedadeenum AS ENUM ('OBRIGATORIA', 'DESEJAVEL'); "
            "END IF; "
            "END $$;"
        )

    # 2. Cria tabela de habilidade se não existir (necessária para FKs)
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS habilidade (
            id UUID PRIMARY KEY,
            nome VARCHAR NOT NULL,
            tipo tipohabilidadeenum NOT NULL,
            categoria VARCHAR NOT NULL,
            empresa_id UUID
        );
        """
    )

    # 3. Cria tabela vaga_habilidade se não existir
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS vaga_habilidade (
            vaga_id UUID NOT NULL REFERENCES vaga(id) ON DELETE CASCADE,
            habilidade_id UUID NOT NULL REFERENCES habilidade(id) ON DELETE CASCADE,
            peso INTEGER NOT NULL DEFAULT 1,
            obrigatoriedade obrigatoriedadeenum NOT NULL DEFAULT 'DESEJAVEL',
            CONSTRAINT check_peso_range CHECK (peso >= 1 AND peso <= 10),
            PRIMARY KEY (vaga_id, habilidade_id)
        );
        """
    )

    # 4. Cria tabela grupo_habilidade
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS grupo_habilidade (
            id UUID PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            tipo tipohabilidadeenum NOT NULL,
            descricao TEXT,
            empresa_id UUID,
            data_criacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        );
        """
    )

    # 5. Cria tabela grupo_habilidade_item
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS grupo_habilidade_item (
            grupo_id UUID NOT NULL REFERENCES grupo_habilidade(id) ON DELETE CASCADE,
            habilidade_id UUID NOT NULL REFERENCES habilidade(id) ON DELETE CASCADE,
            peso INTEGER NOT NULL DEFAULT 1,
            obrigatoriedade obrigatoriedadeenum NOT NULL DEFAULT 'DESEJAVEL',
            CONSTRAINT check_grupo_item_peso_range CHECK (peso >= 1 AND peso <= 10),
            PRIMARY KEY (grupo_id, habilidade_id)
        );
        """
    )


def downgrade() -> None:
    """Downgrade schema: remove as tabelas criadas."""
    op.execute("DROP TABLE IF EXISTS grupo_habilidade_item CASCADE;")
    op.execute("DROP TABLE IF EXISTS grupo_habilidade CASCADE;")
    op.execute("DROP TABLE IF EXISTS vaga_habilidade CASCADE;")
    op.execute("DROP TABLE IF EXISTS habilidade CASCADE;")
