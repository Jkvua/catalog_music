import pytest
from app.validators.album import AlbumValidator

@pytest.mark.parametrize("titulo, esperado", [
    ("Chromakopia", True),
    ("IGOR", True),
    ("A", True),
    ("A" * 150, True),
    ("  Chromakopia  ", True),
    ("", False),
    ("   ", False),
    ("A" * 151, False),
    (None, False),
    (123, False),
    (True, False),
])
def test_validar_titulo(titulo, esperado):
    assert AlbumValidator.validar_titulo(titulo) is esperado


@pytest.mark.parametrize("ano, esperado", [
    (1900, True),
    (2024, True),
    (2100, True),
    ("1900", True),
    ("2024", True),
    ("2100", True),
    (" 2024 ", True),
    (1899, False),
    (2101, False),
    ("1899", False),
    ("2101", False),
    ("", False),
    ("   ", False),
    ("2024.5", False),
    (2024.5, False),
    (None, False),
    (True, False),
])
def test_validar_ano(ano, esperado):
    assert AlbumValidator.validar_ano(ano) is esperado


@pytest.mark.parametrize("artista_id, esperado", [
    (1, True),
    (10, True),
    (999, True),
    (0, False),
    (-1, False),
    (None, False),
    ("1", False),
    (1.5, False),
    (True, False),
    (False, False),
])
def test_validar_artista_id(artista_id, esperado):
    assert AlbumValidator.validar_artista_id(artista_id) is esperado