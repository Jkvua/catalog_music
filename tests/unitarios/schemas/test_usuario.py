from app.schemas.usuario import usuario_schema, usuarios_schema

def test_validar_dados_usuarios():
    """Testa o dicionario de um usuario correto passa"""
    dados = {"user": "clara", "email":"clara@clara.com"}

    erros = usuario_schema.validate(dados)
    assert not erros

def test_usuario_schemas_dados_obrigatorios():
    """Testa de schema barra requisicoes sem campo obrigatorio"""
    erros = usuario_schema.validate({})
    assert "user" in erros
    assert "email" in erros

def test_limite_caractere_user():
    """Testa a validacao de limite de caractere para user (1-100)"""
    erros_vazio = usuario_schema.validate({"user": "", "email":"teste@teste.com"})
    assert "user" in erros_vazio

    erros_gigantes = usuario_schema.validate({"user": "A" * 101, "email": "teste@teste.com"})
    assert "user" in erros_gigantes

def test_usuario_schemas_invalido():
    """Testa o formato de email e limite de tamanho"""
    erros_formato = usuario_schema.validate({"user": "Teste", "email": "email_sem.com"})
    assert "email" in erros_formato

    email_gigante = "a" * 90 + "@exemple.com"
    erros_tamanho = usuario_schema.validate({"user": "Teste", "email": email_gigante})
    assert "email" in erros_tamanho