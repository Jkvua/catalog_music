from app.schemas.artista import artista_schema, artistas_schema

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

def test_artista_limite_nome_caracteres():
    """Testa a validacao de tamanho dos caracteres do nome do artista"""
    dados_nome_vazio = {"nome": "", "genero": "RAP", "pais": "Brasil"}
    erros_vazio = artista_schema.validate(dados_nome_vazio)
    assert "nome" in erros_vazio

    dados_nome_gigante = {"nome": "A" * 201, "genero": "RAP", "pais": "Brasil"}
    erros_gigante = artista_schema.validate(dados_nome_gigante)
    assert "nome" in erros_gigante

def test_artista_limite_pais_caracteres():
    """Testa a validacao de tamanho dos caracteres do pais do artista"""
    dados_pais_vazio = {"nome": "TWICE", "genero": "K-POP", "pais": ""}
    erros_vazio = artista_schema.validate(dados_pais_vazio)
    assert "pais" in erros_vazio

    dados_pais_gigante = {"nome": "TWICE", "genero": "K-POP", "pais": "A" * 201}
    erros_gigante = artista_schema.validate(dados_pais_gigante)
    assert "pais" in erros_gigante