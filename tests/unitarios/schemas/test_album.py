from app.schemas.album import album_schema, albums_schema

def test_validar_album_schema():
    """Testa a validação do schema de álbum com dados válidos.
    """
    dados = {
        "titulo": "Iron Maiden",
        "ano_lancamento": 1980,
        "usuario_id": 1
    }

    erros = album_schema.validate(dados)
    assert not erros

def test_album_schema_campos_obrigatorios():
    """Testa de schemas barra sem campos obrigatorios"""
    dados_vazios = {}

    erros = album_schema.validate(dados_vazios)
    assert "titulo" in erros
    assert "ano_lancamento" in erros

def test_album_limite_titulo_caracteres():
    """Testa a validacao de tamanho minimo e maximo de titulo"""
    dados_titulo_vazio = {"titulo":"", "ano_lancamento":2000}
    erros_vazio = album_schema.validate(dados_titulo_vazio)
    assert "titulo" in erros_vazio

    dados_titulo_longo = {"titulo": "A" * 201, "ano_lancamento":2000}
    erros_gigante = album_schema.validate(dados_titulo_longo)
    assert "titulo" in erros_gigante

def test_album_ano_lancamento_valido():
    """Testa o limite de ano de lancamento do album"""
    dados_ano_antigo = {"titulo": "Musica Classica", "ano_lancamento": 1899}
    erros_antigo = album_schema.validate(dados_ano_antigo)
    assert "ano_lancamento" in erros_antigo

    dados_ano_futuro = {"titulo": "Musica Futuro", "ano_lancamento": 2101}
    erros_futuro = album_schema.validate(dados_ano_futuro)
    assert "ano_lancamento" in erros_futuro