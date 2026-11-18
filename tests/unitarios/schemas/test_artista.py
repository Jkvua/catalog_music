from app.schemas.artista import artista_schema
from app.models.artista import Artista

def test_validar_artista_schema():
    """Testa a validacao do schemas de artista com dados validos"""
    dados = {"nome": "KM2", "genero": "RAP", "pais": "Brasil"}
    erros = artista_schema.validate(dados)
    assert not erros

def test_artista_schema_campos_obrigatorios():
    """Testa se o schema barra sem os campos obrigatorios"""
    dados_vazio = {}
    erros = artista_schema.validate(dados_vazio)
    assert "nome" in erros
    assert "genero" in erros
    assert "pais" in erros

def test_artista_schema_serializacao():
    """Testa a serialização dos campos de um artista."""

    # Arrange
    artista = Artista(
        nome="TWICE",
        genero="K-POP",
        pais="Coreia do Sul"
    )

    # Act
    resultado = artista_schema.dump(artista)

    # Assert
    assert resultado["nome"] == "TWICE"
    assert resultado["genero"] == "K-POP"
    assert resultado["pais"] == "Coreia do Sul"