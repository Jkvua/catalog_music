import pytest
from app.services.usuario import UsuarioService

@pytest.mark.parametrize(
    "email, esperado",
    [
        ("camila@gmail.com", True),
        ("camila.ferreira.almeida", False),
        ("camila@", False),
        ("email_sem_arroba.com", False),
    ]
)
def test_validar_email(email, esperado):
    """Testa a validação do formato de e-mail."""
    # Arrange
    email_informado = email
    # Act
    resultado = UsuarioService.validar_email(email_informado)
    # Assert
    assert bool(resultado) is esperado