from app.models.musica import Musica
from app.models.album import Album
from app.models.artista import Artista
from app.schemas.musica import musica_schema, musica_output_schema

def test_musica_input_schema_serializacao():
    """Testa a serialização dos campos de uma música."""

    # Arrange
    musica = Musica(
        titulo="Ditto",
        duracao="03:25",
        album_id=1,
        usuario_id=1
    )
    # Act
    resultado = musica_schema.dump(musica)
    # Assert
    assert resultado["titulo"] == "Ditto"
    assert resultado["duracao"] == "03:25"
    assert resultado["album_id"] == 1
    assert resultado["usuario_id"] == 1

def test_musica_output_schema_relacionamentos():
    """Testa a serialização dos relacionamentos de uma música."""

    # Arrange
    artista = Artista(nome="NewJeans", genero="K-POP", pais="Coreia do Sul")
    album = Album(titulo="OMG", ano=2023, usuario_id=1)
    album.artista = artista
    musica = Musica(
        titulo="Ditto",
        duracao="03:25",
        usuario_id=1
    )
    musica.album = album

    # Act
    resultado = musica_output_schema.dump(musica)
    # Assert
    assert resultado["titulo"] == "Ditto"
    assert resultado["album"]["titulo"] == "OMG"
    assert resultado["artista"]["nome"] == "NewJeans"
    assert resultado["usuario_id"] == 1