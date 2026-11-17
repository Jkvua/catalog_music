"""altera nota de avaliacao para inteiro

Revision ID: c8dec16b722d
Revises: 85536cc3d79d
Create Date: 2026-11-14 09:08:04.347009
"""

from alembic import op
import sqlalchemy as sa


revision = 'c8dec16b722d'
down_revision = '85536cc3d79d'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'avaliacao',
        'nota',
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using='nota::integer'
    )


def downgrade():
    op.alter_column(
        'avaliacao',
        'nota',
        existing_type=sa.Integer(),
        type_=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=False,
        postgresql_using='nota::double precision'
    )