from datetime import date
from app.models.avaliacao import Avaliacao
from app.schemas.avaliacao import avaliacao_schema, avaliacoes_schema

def test_avaliacao_schema_serializacao():
    """Testa a serialização dos campos de uma avaliação."""

    # Arrange
    avaliacao = Avaliacao(
        nota=5,
        comentario="Álbum lindo, extremamente emocionante",
        data_escuta=date(2026, 10, 8),
        album_id=1,
        usuario_id=1
    )

    # Act
    resultado = avaliacao_schema.dump(avaliacao)

    # Assert
    assert resultado["nota"] == 5
    assert resultado["comentario"] == "Álbum lindo, extremamente emocionante"
    assert resultado["data_escuta"] == "2026-10-08"
    assert resultado["album_id"] == 1
    assert resultado["usuario_id"] == 1


def test_avaliacao_schema_data_invalida():
    """Testa se o Schema rejeita uma data em formato inválido."""

    # Arrange
    dados = {
        "nota": 3,
        "data_escuta": "08/10/2026",
        "album_id": 1,
        "usuario_id": 1
    }

    # Act
    erros = avaliacao_schema.validate(dados)
    # Assert
    assert "data_escuta" in erros

def test_avaliacoes_schema_serializacao_lista():
    """Testa a serialização de uma lista de avaliações."""

    # Arrange
    avaliacoes = [
        Avaliacao(
            nota=5,
            comentario="Excelente",
            data_escuta=date(2026, 10, 8),
            album_id=1,
            usuario_id=1
        ),
        Avaliacao(
            nota=4,
            comentario="Muito bom",
            data_escuta=date(2026, 10, 9),
            album_id=2,
            usuario_id=1
        )
    ]

    # Act
    resultado = avaliacoes_schema.dump(avaliacoes)
    # Assert
    assert len(resultado) == 2
    assert resultado[0]["nota"] == 5
    assert resultado[1]["nota"] == 4
    assert resultado[0]["data_escuta"] == "2026-10-08"
    assert resultado[1]["data_escuta"] == "2026-10-09"