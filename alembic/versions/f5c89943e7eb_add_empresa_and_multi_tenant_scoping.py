"""Add Empresa and multi-tenant scoping

Revision ID: f5c89943e7eb
Revises: c3a1b8e92f14
Create Date: 2026-08-19 16:35:02.318806

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f5c89943e7eb"
down_revision: str | Sequence[str] | None = "c3a1b8e92f14"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    # Update enum
    op.execute("ALTER TYPE tipo_usuario_enum ADD VALUE IF NOT EXISTS 'admin'")

    # 1. Create Empresa table
    empresa_table = op.create_table(
        "empresa",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("cnpj", sa.String(length=14), nullable=True),
        sa.Column("logo_url", sa.String(length=255), nullable=True),
        sa.Column("plano", sa.String(length=50), nullable=True),
        sa.Column(
            "configuracoes_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("missao_visao_valores", sa.Text(), nullable=True),
        sa.Column(
            "data_criacao",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. Insert default Empresa
    default_empresa_id = str(uuid.uuid4())
    op.bulk_insert(
        empresa_table,
        [
            {
                "id": default_empresa_id,
                "nome": "Empresa Padrão",
            }
        ],
    )

    # 3. Add columns as nullable
    op.add_column("candidatura", sa.Column("empresa_id", sa.UUID(), nullable=True))
    op.add_column("recrutador", sa.Column("empresa_id", sa.UUID(), nullable=True))
    op.add_column("vaga", sa.Column("empresa_id", sa.UUID(), nullable=True))

    # 4. Update existing records
    op.execute(f"UPDATE candidatura SET empresa_id = '{default_empresa_id}'")
    op.execute(f"UPDATE recrutador SET empresa_id = '{default_empresa_id}'")
    op.execute(f"UPDATE vaga SET empresa_id = '{default_empresa_id}'")

    # 5. Alter columns to be NOT NULL
    op.alter_column("candidatura", "empresa_id", nullable=False)
    op.alter_column("recrutador", "empresa_id", nullable=False)
    op.alter_column("vaga", "empresa_id", nullable=False)

    # 6. Create Foreign Keys
    op.create_foreign_key(
        None, "candidatura", "empresa", ["empresa_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        None, "habilidade", "empresa", ["empresa_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        None, "recrutador", "empresa", ["empresa_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        None, "vaga", "empresa", ["empresa_id"], ["id"], ondelete="CASCADE"
    )

    # 7. Drop old columns
    op.drop_column("recrutador", "cnpj")
    op.drop_column("recrutador", "empresa")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "vaga", type_="foreignkey")
    op.drop_column("vaga", "empresa_id")

    op.add_column(
        "recrutador",
        sa.Column(
            "empresa", sa.VARCHAR(length=255), autoincrement=False, nullable=True
        ),
    )
    op.execute("UPDATE recrutador SET empresa = 'Empresa Padrão'")
    op.alter_column("recrutador", "empresa", nullable=False)

    op.add_column(
        "recrutador",
        sa.Column("cnpj", sa.VARCHAR(length=14), autoincrement=False, nullable=True),
    )
    op.drop_constraint(None, "recrutador", type_="foreignkey")
    op.drop_column("recrutador", "empresa_id")
    op.drop_constraint(None, "habilidade", type_="foreignkey")
    op.drop_constraint(None, "candidatura", type_="foreignkey")
    op.drop_column("candidatura", "empresa_id")
    op.drop_table("empresa")
