"""add unique constraint usuario_id+nome

Revision ID: c0fda2d20234
Revises: 549acd42cbc8
Create Date: 2026-07-10 13:05:40.354523

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0fda2d20234'
down_revision = '549acd42cbc8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('artistas', schema=None) as batch_op:
        batch_op.create_index(
            'idx_usuario_artista_nome',
            ['usuario_id', 'nome'],
            unique=True
        )


def downgrade():
    with op.batch_alter_table('artistas', schema=None) as batch_op:
        batch_op.drop_index('idx_usuario_artista_nome')
    # ### end Alembic commands ###
