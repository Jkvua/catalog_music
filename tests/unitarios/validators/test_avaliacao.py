import pytest

from app.validators.avaliacao import AvaliacaoValidator

@pytest.mark.parametrize("nota, esperado", [
    (1, True),
    (2, True),
    (3, True),
    (4, True),
    (5, True),
    (0, False),
    (6, False),
    (-1, False),
    (3.5, False),
    (None, False),
    ("3", False),
    ("cinco", False),
    (True, False),
])
def test_validar_nota(nota, esperado):
    assert AvaliacaoValidator.validar_nota(nota) is esperado


@pytest.mark.parametrize("comentario, esperado", [
    ("Álbum excelente", True),
    ("Muito bom", True),
    ("A", True),
    ("A" * 500, True),
    ("", False),
    ("   ", False),
    ("A" * 501, False),
    (None, False),
    (123, False),
])
def test_validar_comentario(comentario, esperado):
    assert AvaliacaoValidator.validar_comentario(comentario) is esperado


@pytest.mark.parametrize("data, esperado", [
    ("2026-10-11", True),
    ("2026-01-01", True),
    ("2024-02-29", True),
    ("11/10/2026", False),
    ("2026-13-01", False),
    ("2026-02-30", False),
    ("", False),
    (None, False),
    (123, False),
])
def test_validar_data_escuta(data, esperado):
    assert AvaliacaoValidator.validar_data_escuta(data) is esperado

@pytest.mark.parametrize("album_id, esperado", [
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
def test_validar_album_id(album_id, esperado):
    assert AvaliacaoValidator.validar_album_id(album_id) is esperado