"""torna usuario_id obrigatorio em albuns

Revision ID: 37715ed80bfa
Revises: c12ac43d5961
Create Date: 2026-11-14 11:45:25.312924

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37715ed80bfa'
down_revision = 'c12ac43d5961'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'albuns',
        'usuario_id',
        existing_type=sa.INTEGER(),
        nullable=False
    )


def downgrade():
    op.alter_column(
        'albuns',
        'usuario_id',
        existing_type=sa.INTEGER(),
        nullable=True
    )