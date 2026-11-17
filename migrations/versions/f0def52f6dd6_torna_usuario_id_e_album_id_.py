"""torna usuario_id e album_id obrigatorios em musica

Revision ID: f0def52f6dd6
Revises: 37715ed80bfa
Create Date: 2026-11-14 12:12:54.891968

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0def52f6dd6'
down_revision = '37715ed80bfa'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'musica',
        'usuario_id',
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.alter_column(
        'musica',
        'album_id',
        existing_type=sa.INTEGER(),
        nullable=False
    )


def downgrade():
    op.alter_column(
        'musica',
        'album_id',
        existing_type=sa.INTEGER(),
        nullable=True
    )

    op.alter_column(
        'musica',
        'usuario_id',
        existing_type=sa.INTEGER(),
        nullable=True
    )