import pytest
from app.validators.usuario import UsuarioValidator

@pytest.mark.parametrize("user, esperado", [
    ("camila", True),
    ("usuario_teste", True),
    ("A", True),
    ("A" * 100, True),
    ("  camila  ", True),
    ("", False),
    ("   ", False),
    ("A" * 101, False),
    (None, False),
    (123, False),
    (True, False),
])
def test_validar_user(user, esperado):
    assert UsuarioValidator.validar_user(user) is esperado


@pytest.mark.parametrize("email, esperado", [
    ("camila@email.com", True),
    ("usuario.teste@email.com", True),
    ("usuario+teste@email.com", True),
    ("usuario_teste@email.com", True),
    ("CAMiLA@EMAIL.COM", True),
    ("  camila@email.com  ", True),
    ("", False),
    ("   ", False),
    ("camila", False),
    ("camila@", False),
    ("@email.com", False),
    ("camila@email", False),
    ("camila@email.c", False),
    ("camila email@email.com", False),
    ("A" * 90 + "@email.com", True),
    ("A" * 91 + "@email.com", False),
    (None, False),
    (123, False),
    (True, False),
])
def test_validar_email(email, esperado):
    assert UsuarioValidator.validar_email(email) is esperado


@pytest.mark.parametrize("password, esperado", [
    ("12345678", True),
    ("senha123", True),
    ("Senha@123", True),
    ("A" * 100, True),
    ("1234567", False),
    ("", False),
    ("   ", False),
    (None, False),
    (12345678, False),
    (True, False),
])
def test_validar_password(password, esperado):
    assert UsuarioValidator.validar_password(password) is esperado


@pytest.mark.parametrize("is_admin, esperado", [
    (True, True),
    (False, True),
    (1, False),
    (0, False),
    ("True", False),
    ("False", False),
    (None, False),
])
def test_validar_is_admin(is_admin, esperado):
    assert UsuarioValidator.validar_is_admin(is_admin) is esperado