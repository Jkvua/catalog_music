"""corrige on delete cascade nas chaves estrangeiras

Revision ID: 0e8a2c0b3f46
Revises: f0def52f6dd6
Create Date: 2026-11-14 12:40:25.479719

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e8a2c0b3f46'
down_revision = 'f0def52f6dd6'
branch_labels = None
depends_on = None


def upgrade():
    # ALBUNS
    op.drop_constraint(
        'albuns_artista_id_fkey',
        'albuns',
        type_='foreignkey'
    )
    op.drop_constraint(
        'albuns_usuario_id_fkey',
        'albuns',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'albuns_artista_id_fkey',
        'albuns',
        'artistas',
        ['artista_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'albuns_usuario_id_fkey',
        'albuns',
        'usuarios',
        ['usuario_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # ARTISTAS
    op.drop_constraint(
        'artistas_usuario_id_fkey',
        'artistas',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'artistas_usuario_id_fkey',
        'artistas',
        'usuarios',
        ['usuario_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # AVALIACAO
    op.drop_constraint(
        'avaliacao_usuario_id_fkey',
        'avaliacao',
        type_='foreignkey'
    )
    op.drop_constraint(
        'avaliacao_album_id_fkey',
        'avaliacao',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'avaliacao_usuario_id_fkey',
        'avaliacao',
        'usuarios',
        ['usuario_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'avaliacao_album_id_fkey',
        'avaliacao',
        'albuns',
        ['album_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # MUSICA
    op.drop_constraint(
        'musica_usuario_id_fkey',
        'musica',
        type_='foreignkey'
    )
    op.drop_constraint(
        'musica_album_id_fkey',
        'musica',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'musica_usuario_id_fkey',
        'musica',
        'usuarios',
        ['usuario_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'musica_album_id_fkey',
        'musica',
        'albuns',
        ['album_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # MUSICA
    op.drop_constraint(
        'musica_usuario_id_fkey',
        'musica',
        type_='foreignkey'
    )
    op.drop_constraint(
        'musica_album_id_fkey',
        'musica',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'musica_usuario_id_fkey',
        'musica',
        'usuarios',
        ['usuario_id'],
        ['id']
    )
    op.create_foreign_key(
        'musica_album_id_fkey',
        'musica',
        'albuns',
        ['album_id'],
        ['id']
    )

    # AVALIACAO
    op.drop_constraint(
        'avaliacao_usuario_id_fkey',
        'avaliacao',
        type_='foreignkey'
    )
    op.drop_constraint(
        'avaliacao_album_id_fkey',
        'avaliacao',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'avaliacao_usuario_id_fkey',
        'avaliacao',
        'usuarios',
        ['usuario_id'],
        ['id']
    )
    op.create_foreign_key(
        'avaliacao_album_id_fkey',
        'avaliacao',
        'albuns',
        ['album_id'],
        ['id']
    )

    # ARTISTAS
    op.drop_constraint(
        'artistas_usuario_id_fkey',
        'artistas',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'artistas_usuario_id_fkey',
        'artistas',
        'usuarios',
        ['usuario_id'],
        ['id']
    )

    # ALBUNS
    op.drop_constraint(
        'albuns_artista_id_fkey',
        'albuns',
        type_='foreignkey'
    )
    op.drop_constraint(
        'albuns_usuario_id_fkey',
        'albuns',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'albuns_artista_id_fkey',
        'albuns',
        'artistas',
        ['artista_id'],
        ['id']
    )
    op.create_foreign_key(
        'albuns_usuario_id_fkey',
        'albuns',
        'usuarios',
        ['usuario_id'],
        ['id']
    )