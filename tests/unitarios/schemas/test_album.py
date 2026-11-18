from app.schemas.album import album_schema, albums_schema
from app.models.album import Album


def test_album_schema_serializacao():
    """Testa a serialização dos campos de um álbum."""

    # Arrange
    album = Album(
        titulo="Iron Maiden",
        ano=1980,
        usuario_id=1
    )

    # Act
    resultado = album_schema.dump(album)

    # Assert
    assert resultado["titulo"] == "Iron Maiden"
    assert resultado["ano"] == 1980
    assert resultado["usuario_id"] == 1


def test_albums_schema_serializacao_lista():
    """Testa a serialização de uma lista de álbuns."""

    # Arrange
    albuns = [
        Album(titulo="Iron Maiden", ano=1980, usuario_id=1),
        Album(titulo="Killers", ano=1981, usuario_id=1)
    ]

    # Act
    resultado = albums_schema.dump(albuns)

    # Assert
    assert len(resultado) == 2
    assert resultado[0]["titulo"] == "Iron Maiden"
    assert resultado[1]["titulo"] == "Killers"
    assert resultado[0]["ano"] == 1980
    assert resultado[1]["ano"] == 1981