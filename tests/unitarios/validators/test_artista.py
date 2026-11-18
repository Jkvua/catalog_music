import pytest
from app.validators.artista import ArtistaValidator

@pytest.mark.parametrize("nome, esperado", [
    ("TWICE", True),
    ("Legião Urbana", True),
    ("A", True),
    ("A" * 100, True),
    ("", False),
    ("   ", False),
    ("A" * 101, False),
    (None, False),
    (123, False),
    (True, False),
])
def test_validar_nome(nome, esperado):
    assert ArtistaValidator.validar_nome(nome) is esperado


@pytest.mark.parametrize("genero, esperado", [
    ("K-POP", True),
    ("Rock", True),
    ("A", True),
    ("A" * 50, True),
    ("", False),
    ("   ", False),
    ("A" * 51, False),
    (None, False),
    (123, False),
    (True, False),
])
def test_validar_genero(genero, esperado):
    assert ArtistaValidator.validar_genero(genero) is esperado


@pytest.mark.parametrize("pais, esperado", [
    ("Brasil", True),
    ("Coreia do Sul", True),
    ("A", True),
    ("A" * 50, True),
    ("", False),
    ("   ", False),
    ("A" * 51, False),
    (None, False),
    (123, False),
    (True, False),
])
def test_validar_pais(pais, esperado):
    assert ArtistaValidator.validar_pais(pais) is esperado