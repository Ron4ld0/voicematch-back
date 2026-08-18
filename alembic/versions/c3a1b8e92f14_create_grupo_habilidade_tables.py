"""create_grupo_habilidade_tables

Revision ID: c3a1b8e92f14
Revises: d1859dde4cf9
Create Date: 2026-08-18 12:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3a1b8e92f14"
down_revision: str | Sequence[str] | None = "d1859dde4cf9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema: cria as tabelas grupo_habilidade e grupo_habilidade_item."""
    op.create_table(
        "grupo_habilidade",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column(
            "tipo",
            postgresql.ENUM(
                "HARD",
                "SOFT",
                name="tipohabilidadeenum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column(
            "empresa_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "data_criacao",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "grupo_habilidade_item",
        sa.Column(
            "grupo_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("grupo_habilidade.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "habilidade_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("habilidade.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("peso", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "obrigatoriedade",
            postgresql.ENUM(
                "OBRIGATORIA",
                "DESEJAVEL",
                name="obrigatoriedadeenum",
                create_type=False,
            ),
            nullable=False,
            server_default="DESEJAVEL",
        ),
        sa.CheckConstraint(
            "peso >= 1 AND peso <= 10", name="check_grupo_item_peso_range"
        ),
    )


def downgrade() -> None:
    """Downgrade schema: remove as tabelas grupo_habilidade_item e grupo_habilidade."""
    op.drop_table("grupo_habilidade_item")
    op.drop_table("grupo_habilidade")
