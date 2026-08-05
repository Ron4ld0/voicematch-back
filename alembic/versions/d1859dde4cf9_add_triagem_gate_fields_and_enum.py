"""add_triagem_gate_fields_and_enum

Revision ID: d1859dde4cf9
Revises: 869ef0b06279
Create Date: 2026-08-05 17:21:02.843162

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "d1859dde4cf9"
down_revision: Union[str, Sequence[str], None] = "6b81e2f33812"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Update status_candidatura_enum safely with new values in autocommit block
    with op.get_context().autocommit_block():
        op.execute(
            "ALTER TYPE status_candidatura_enum ADD VALUE IF NOT EXISTS 'pendente_triagem'"
        )
        op.execute(
            "ALTER TYPE status_candidatura_enum ADD VALUE IF NOT EXISTS 'aprovada_triagem'"
        )
        op.execute(
            "ALTER TYPE status_candidatura_enum ADD VALUE IF NOT EXISTS 'reprovada_triagem'"
        )

    # Migrate existing candidaturas from 'pendente' to 'pendente_triagem'
    op.execute(
        "UPDATE candidatura SET status = 'pendente_triagem' WHERE status::text = 'pendente'"
    )

    # 2. Add score_minimo_triagem to vaga
    op.add_column(
        "vaga",
        sa.Column(
            "score_minimo_triagem", sa.Numeric(precision=4, scale=2), nullable=True
        ),
    )

    # 3. Add triagem fields to candidatura
    op.add_column(
        "candidatura",
        sa.Column("score_triagem", sa.Numeric(precision=4, scale=2), nullable=True),
    )
    op.add_column(
        "candidatura",
        sa.Column(
            "feedback_triagem", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
    )
    op.add_column(
        "candidatura",
        sa.Column("data_triagem", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("candidatura", "data_triagem")
    op.drop_column("candidatura", "feedback_triagem")
    op.drop_column("candidatura", "score_triagem")
    op.drop_column("vaga", "score_minimo_triagem")
