"""corrige cascade na exclusao de usuarios

Revision ID: 85536cc3d79d
Revises: 452568d7b07d
"""

from alembic import op


revision = '85536cc3d79d'
down_revision = '452568d7b07d'
branch_labels = None
depends_on = None


# (tabela, nome da restrição, tabela referenciada, coluna)
FOREIGN_KEYS = [
    ('albuns', 'albuns_artista_id_fkey', 'artistas', 'artista_id'),
    ('albuns', 'albuns_usuario_id_fkey', 'usuarios', 'usuario_id'),
    ('artistas', 'artistas_usuario_id_fkey', 'usuarios', 'usuario_id'),
    ('avaliacao', 'avaliacao_album_id_fkey', 'albuns', 'album_id'),
    ('avaliacao', 'avaliacao_usuario_id_fkey', 'usuarios', 'usuario_id'),
    ('musica', 'musica_album_id_fkey', 'albuns', 'album_id'),
    ('musica', 'musica_usuario_id_fkey', 'usuarios', 'usuario_id'),
]


def upgrade():
    for tabela, restricao, referencia, coluna in FOREIGN_KEYS:
        op.drop_constraint(
            restricao,
            tabela,
            type_='foreignkey'
        )

        op.create_foreign_key(
            restricao,
            tabela,
            referencia,
            [coluna],
            ['id'],
            ondelete='CASCADE'
        )


def downgrade():
    for tabela, restricao, referencia, coluna in reversed(FOREIGN_KEYS):
        op.drop_constraint(
            restricao,
            tabela,
            type_='foreignkey'
        )

        op.create_foreign_key(
            restricao,
            tabela,
            referencia,
            [coluna],
            ['id']
        )
