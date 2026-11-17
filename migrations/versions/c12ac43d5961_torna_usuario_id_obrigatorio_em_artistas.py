"""torna usuario_id obrigatorio em artistas

Revision ID: c12ac43d5961
Revises: c8dec16b722d
Create Date: 2026-11-14 10:00:39.825405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c12ac43d5961'
down_revision = 'c8dec16b722d'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'artistas',
        'usuario_id',
        existing_type=sa.INTEGER(),
        existing_nullable=True,
        nullable=False
    )


def downgrade():
    op.alter_column(
        'artistas',
        'usuario_id',
        existing_type=sa.INTEGER(),
        existing_nullable=False,
        nullable=True
    )