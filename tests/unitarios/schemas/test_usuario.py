from app.models.usuario import Usuario
from app.schemas.usuario import usuario_schema


def test_usuario_schema_serializacao():
    """Testa a serialização dos campos de um usuário."""

    # Arrange
    usuario = Usuario(
        user="clara",
        email="clara@clara.com",
        password="senha12345"
    )
    # Act
    resultado = usuario_schema.dump(usuario)
    # Assert
    assert resultado["user"] == "clara"
    assert resultado["email"] == "clara@clara.com"

def test_usuario_schema_nao_expoe_senha():
    """Testa se a senha não aparece nos dados serializados."""

    # Arrange
    usuario = Usuario(
        user="clara",
        email="clara@clara.com",
        password="senha12345"
    )
    # Act
    resultado = usuario_schema.dump(usuario)
    # Assert
    assert "password" not in resultado

def test_usuario_schema_email_invalido():
    """Testa se o Schema rejeita um e-mail com formato inválido."""

    # Arrange
    dados = {
        "user": "clara",
        "email": "email_sem_arroba.com"
    }
    # Act
    erros = usuario_schema.validate(dados)
    # Assert
    assert "email" in erros