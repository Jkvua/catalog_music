from app.schemas.musica import musica_schema, musicas_schema

def test_validar_musica_schema():
    """Testa se musica com titulo e duracao (MM:SS) validos passa corretamente"""
    dados = {
        "titulo": "Ditto",
        "duracao": "03:25",
        "album_id": 1,
        "usuario_id": 1
    }

    erros = musica_schema.validate(dados)
    assert not erros

def test_musica_schemas_campos_obrigatorios():
    """Testa de schemas barra requisicoes sem os campos obrigatorios"""
    erros = musica_schema.validate({})
    assert "titulo" in erros
    assert "duracao" in erros

def test_musica_limite_titulo_musica():
    """Testa os limeites de caracteres do titulo de musica"""
    erros_vazio = musica_schema.validate({"titulo": "", "duracao": "03:05"})
    assert "titulo" in erros_vazio

    erros_gigante = musica_schema.validate({"titulo": "A" * 201, "duracao" : "03:05"})
    assert "titulo" in erros_gigante

def test_musica_schema_validacao_customizada_duracao():
    """Testar regra de customizacao de tempo da musica (MM:SS)"""
    erros_segundos = musica_schema.validate({"titulo": "Hype Boy", "duracao": "03:60"})
    assert "duracao" in erros_segundos

    erros_formato = musica_schema.validate({"titulo": "Hype Boy", "duracao": "300"})
    assert "duracao" in erros_formato

    erros_letras = musica_schema.validate({"titulo": "Hype Boy", "duracao": "ab:cd"})
    assert "duracao" in erros_letras